#!/usr/bin/env python3
"""Ingest energy news feeds into the ERW events shape: warehouse/output/news_stories.csv.

Energy Research Warehouse (ERW). Reads every feed in warehouse/news/feeds.yaml,
keeps titles, summaries (trimmed to 500 characters) and links only, never
article bodies, and stores each story as one row of the `events` shape
(docs/datastandard.md) through the same merge writer as the price tables.

    python warehouse/news/ingest.py            # stories published in the last 2 days
    python warehouse/news/ingest.py --days 2

Per story:
  event_id      news:<16 hex of sha1(canonical URL)>
  event_date    the feed's publish time, UTC (a story without one is skipped and counted)
  event_type    news
  source        the outlet: the feed's name, or for Google News feeds the outlet
                named in the item's <source> element
  source_url    the story link as the feed gives it (Google News items link
                through news.google.com; the outlet is in `source`)
  feed, feed_sector, feed_region   from feeds.yaml
  parties, mw, price, currency, status, entity_ids   empty at ingest
  significance ... scored_at       empty until warehouse/news/score.py fills them

Deduplication: by canonical URL (scheme, host case, tracking parameters and
fragments normalised), then by near-identical title (difflib ratio >= 0.92
after lowercasing and removing an appended " - Outlet"), against both this run
and stories already stored. The first copy seen is kept, direct feeds before
Google News. A story already stored is never rewritten here, so scores survive.
Raw feed responses are saved under warehouse/raw/news/<run_id>/.
"""

import argparse
import datetime as dt
import difflib
import hashlib
import html
import os
import re
import sys
import time
import traceback
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import feedparser
import pandas as pd
import requests
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "connectors"))
import iso_prices as ip  # noqa: E402  shared: raw capture, merge writer, logs, registry, status

NAME = "news_stories"
FEEDS = os.path.join(HERE, "feeds.yaml")
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-news-ingest/0.1; "
                    "+https://github.com/SamuelEnrique/erw)"}
SUMMARY_MAX = 500
TITLE_SIMILAR = 0.92
# events shape (docs/datastandard.md) first, then the news columns (Decision 15)
NEWS_COLS = ["event_id", "event_date", "event_type", "parties", "entity_ids", "mw", "price",
             "currency", "status", "source", "source_url",
             "title", "summary", "feed", "feed_sector", "feed_region", "retrieved_at",
             "significance", "ai_power_relevance", "sector", "region", "price_mentioned", "why",
             "cluster_id", "model_id", "scored_at"]
KEY = ["event_id"]
TRACKING = re.compile(r"^(utm_|fbclid$|gclid$|mc_cid$|mc_eid$|cmpid$|ref$|src$|_hsenc$|_hsmi$)", re.I)


def canonical(url):
    parts = urlsplit(url.strip())
    q = [(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True) if not TRACKING.match(k)]
    path = parts.path.rstrip("/") or "/"
    return urlunsplit((parts.scheme.lower() or "https", parts.netloc.lower(), path, urlencode(q), ""))


def clean(text, limit=None):
    text = html.unescape(re.sub(r"<[^>]+>", " ", text or ""))
    # the ERW writes no em dashes in any file (CLAUDE.md): an outlet's em dash becomes " - "
    text = text.replace("—", " - ")
    text = re.sub(r"\s+", " ", text).strip()
    if limit and len(text) > limit:
        text = text[:limit].rsplit(" ", 1)[0] + " ..."
    return text


def norm_title(title, outlet):
    t = title
    if outlet and t.endswith(" - " + outlet):
        t = t[: -len(" - " + outlet)]
    return re.sub(r"[^a-z0-9 ]+", "", t.lower()).strip()


def fetch_feed(feed, log):
    def call():
        r = requests.get(feed["url"], headers=UA, timeout=45)
        if r.status_code != 200:
            raise RuntimeError(f"HTTP {r.status_code}")
        return r
    r = ip.with_retries(f"feed {feed['name']}", call, log, attempts=3, wait=3)
    parsed = feedparser.parse(r.content)
    retrieved = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
    stories, undated = [], 0
    for e in parsed.entries:
        link = e.get("link")
        title = clean(e.get("title"))
        when = e.get("published_parsed") or e.get("updated_parsed")
        if not link or not title:
            continue
        if not when:
            undated += 1
            continue
        outlet = feed["name"]
        if feed["via"].startswith("google_news"):
            src = e.get("source") or {}
            outlet = (src.get("title") if hasattr(src, "get") else None) or feed["name"]
            if title.endswith(" - " + outlet):
                title = title[: -len(" - " + outlet)]
        stories.append({
            "event_date": dt.datetime(*when[:6], tzinfo=dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "source": outlet, "source_url": link, "canonical": canonical(link),
            "title": title, "summary": clean(e.get("summary"), SUMMARY_MAX),
            "feed": feed["name"], "feed_sector": feed["sector"], "feed_region": feed["region"],
            "via": feed["via"], "retrieved_at": retrieved,
        })
    return stories, undated, len(parsed.entries)


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW news ingest")
    ap.add_argument("--days", type=int, default=2, help="keep stories published in the last N days")
    ap.add_argument("--out-dir", help="write under this directory instead (trial runs)")
    args = ap.parse_args(argv)
    if args.out_dir:
        ip.set_out_dir(args.out_dir)
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"news_ingest_{run_id}.log"))
    ip.RAW.open("news", run_id)
    feeds = yaml.safe_load(open(FEEDS, encoding="utf-8"))["feeds"]
    cutoff = pd.Timestamp.now(tz="UTC") - pd.Timedelta(days=args.days)
    log(f"ERW news ingest {run_id}: {len(feeds)} feeds, stories since {ip.utc_iso(cutoff)}")

    results, got = [], []

    def one(feed):
        try:
            return feed, fetch_feed(feed, log), None
        except Exception as exc:
            return feed, None, exc
    with ThreadPoolExecutor(8) as pool:
        for feed, res, exc in pool.map(one, feeds):
            if exc is not None:
                log(f"  FEED FAILED {feed['name']}: {exc!r}")
                results.append(dict(table=NAME, market=f"feed:{feed['name']}", status="failed",
                                    detail=repr(exc)[:300]))
                continue
            stories, undated, n = res
            log(f"  {feed['name']}: {n} entries, {len(stories)} dated, {undated} without a publish "
                f"time (skipped)")
            got += stories
            results.append(dict(table=NAME, market=f"feed:{feed['name']}",
                                status="ok" if n else "failed",
                                detail="" if n else "feed returned no entries"))

    path = os.path.join(ip.OUT_DIR, NAME + ".csv")
    old = ip.read_series(path, NEWS_COLS) if os.path.exists(path) else pd.DataFrame(columns=NEWS_COLS)
    seen_ids = set(old["event_id"])
    seen_titles = [norm_title(t, s) for t, s in zip(old["title"], old["source"])]
    order = {"direct": 0, "google_news_site": 1, "google_news_catchall": 2}
    got.sort(key=lambda x: (order.get(x["via"], 3), x["event_date"]))
    new, dup_url, dup_title, too_old = [], 0, 0, 0
    for st in got:
        if pd.Timestamp(st["event_date"]) < cutoff:
            too_old += 1
            continue
        eid = "news:" + hashlib.sha1(st["canonical"].encode("utf-8")).hexdigest()[:16]
        if eid in seen_ids:
            dup_url += 1
            continue
        nt = norm_title(st["title"], st["source"])
        if nt and any(difflib.SequenceMatcher(None, nt, t).ratio() >= TITLE_SIMILAR
                      for t in seen_titles if abs(len(t) - len(nt)) < 20):
            dup_title += 1
            continue
        seen_ids.add(eid)
        seen_titles.append(nt)
        row = {c: "" for c in NEWS_COLS}
        row.update({"event_id": eid, "event_date": st["event_date"], "event_type": "news",
                    "source": st["source"], "source_url": st["source_url"], "title": st["title"],
                    "summary": st["summary"], "feed": st["feed"], "feed_sector": st["feed_sector"],
                    "feed_region": st["feed_region"], "retrieved_at": st["retrieved_at"]})
        new.append(row)
    log(f"  fetched {len(got)} dated stories: {len(new)} new, {dup_url} already stored or same URL, "
        f"{dup_title} near-identical title, {too_old} older than {args.days} days")
    header = [
        "Energy Research Warehouse (ERW): Energy news stories, titles, summaries and links",
        "Shape: events (docs/datastandard.md v0), event_type news; news columns per Decision 15. "
        "event_date is the publish time, UTC.",
        f"Retrieved: {run_id} (UTC) by warehouse/news/ingest.py from {len(feeds)} feeds in "
        "warehouse/news/feeds.yaml",
        f"Run log: warehouse/output/logs/news_ingest_{run_id}.log (every feed, counts, failures)",
        f"Raw files: warehouse/raw/news/{run_id}/ (not in git; manifest.csv lists each feed response)",
        "License: internal. Titles and summaries are the outlets' text, kept for scoring and "
        "linking, not for republication. Scores are written by warehouse/news/score.py.",
    ]
    df = pd.DataFrame(new, columns=NEWS_COLS)
    if len(df) or not os.path.exists(path):
        ip.write_csv(df, NAME, header, log, cols=NEWS_COLS, key=KEY, time_col="event_date")
    else:
        log("  no new stories; file unchanged")
        print(f"{NAME}.csv: no new stories")
    outlets = sorted(set(pd.concat([old["source"], df["source"]])) if len(old) else set(df["source"]))
    feed_of = {}
    for st in got:
        feed_of.setdefault(st["source"], st)
    ip.update_sources([dict(source=o, publisher=o,
                            report=f"news stories via feed '{feed_of[o]['feed']}'" if o in feed_of else "news stories",
                            report_url="", document_list="", license="internal", tables=[NAME])
                       for o in outlets])
    ip.write_status("news_ingest", run_id, results + [dict(table=NAME, market="stories", status="ok",
                                                           detail=f"{len(new)} new stories")])
    log(f"done: {len(new)} new stories, {sum(r['status'] == 'failed' for r in results)} feeds failed")
    log.close()
    print(f"news ingest: {len(new)} new stories from {len(feeds)} feeds; run log "
          f"{os.path.relpath(log.path, ip.ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
