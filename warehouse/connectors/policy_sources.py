#!/usr/bin/env python3
"""Policy sources (platform tool 12): the Federal Register and agency news, as one events table, policy_actions.

Energy Research Warehouse (ERW) connector, session 24. All sources are free and public; every response is stored
raw under warehouse/raw/policy_sources/<run_id>/ (manifest.csv names each URL and time).

    python warehouse/connectors/policy_sources.py                       # from 2025-10-01 to today
    python warehouse/connectors/policy_sources.py --since 2026-09-01

Sources:
  federalregister   The Federal Register API (federalregister.gov/api/v1, no key): rules, proposed rules and notices of
                    DOE (with FERC, which the Register files under it), FERC, EPA, NRC, BLM and Interior, published
                    since --since. DOE, FERC and NRC documents are all energy; EPA, BLM and Interior documents are kept
                    only when their title, abstract or Federal Register topics name an energy subject (ENERGY below).
                    Routine paperwork (information collections, meeting and Sunshine Act notices, Privacy Act systems,
                    FERC's combined notices of filings) is left out (ROUTINE below).
  nrc               NRC news releases (www.nrc.gov RSS, the feed's window only).
  doe               DOE newsroom (www.energy.gov RSS, the feed's window only).
  puct              Public Utility Commission of Texas news page (puc.texas.gov, every dated item on the page).
  cpuc              California Public Utilities Commission news (cpuc.ca.gov/news-and-updates/all-news, pages until
                    --since), the items whose title names an energy subject (the CPUC also regulates rail, water and
                    telecommunications).
  FERC's own news and eLibrary pages answer a Cloudflare JavaScript challenge (checked 2026-09-28), so FERC's actions
  come from the Federal Register and FERC news items reach the ERW through news_stories (the Google News feed).

The table (events shape, docs/datastandard.md; public: every source is a US or state government publication):
  event_id     federalregister:<document number>, or <source>:<sha1 of the link, 12 hex>
  event_date   the publication date (Register) or the release date (news), YYYY-MM-DD
  event_type   filing (a Register document) or announcement (a news release)
  parties      the agencies, as named
  status       the Register's action line ("Final rule.", "Notice of availability.") or "news release"
  source, source_url
  then: agency (the short name: DOE, FERC, EPA, NRC, BLM, Interior, PUCT, CPUC), action_type (rule, proposed_rule,
  notice, press_release), title, abstract (the Register's own summary; blank for news), docket (docket ids and RINs,
  ";"-separated), rin, fr_document_number, sector_tags (keyword rules, SECTOR_TAGS), states (US states named in the
  title or abstract, or the commission's state), related_urls (a news release that reports a Register document is
  folded into it: its link is here and it gets no row of its own), news_story_ids and news_story_urls (the scored news
  stories that report the same action: a docket, RIN or document number in the story, or a title of the same content
  words within 21 days), and the scores warehouse/policy/score.py writes (significance, sector, why, model_id,
  scored_at; blank until scored).
"""

import argparse
import datetime as dt
import hashlib
import html as H
import json
import os
import re
import sys
import traceback
import xml.etree.ElementTree as ET

import pandas as pd
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "policy_actions"
ROOT = ip.ROOT
SCORES = os.path.join(ROOT, "warehouse", "policy", "scores.csv")
FR = "https://www.federalregister.gov/api/v1/documents.json"
UA = {"User-Agent": "Mozilla/5.0 (ERW energy research warehouse; https://github.com/SamuelEnrique/erw)"}
AGENCIES = {"energy-department": "DOE", "federal-energy-regulatory-commission": "FERC",
            "environmental-protection-agency": "EPA", "nuclear-regulatory-commission": "NRC",
            "land-management-bureau": "BLM", "interior-department": "Interior"}
ALWAYS_ENERGY = {"DOE", "FERC", "NRC"}
TYPES = {"Rule": "rule", "Proposed Rule": "proposed_rule", "Notice": "notice"}
ENERGY = re.compile(r"\b(energy|electric\w*|power plant|power sector|utilit(y|ies)|oil|natural gas|gas|coal|pipeline|"
                    r"methane|petroleum|crude|refiner\w*|nuclear|uranium|renewable|solar|wind|geothermal|hydro\w*|"
                    r"transmission|offshore|lease sale|leasing|fuel|emission guidelines|greenhouse gas|carbon capture|"
                    r"battery|batteries|lithium|critical mineral\w*|LNG|biofuel|ethanol|hydrogen|mining claim)\b", re.I)
ROUTINE = re.compile(r"(Combined Notice of Filings|Information Collection|Paperwork Reduction|Sunshine Act|"
                     r"Privacy Act of 1974|Meeting\b|Advisory (Committee|Board)|Environmental Impact Statements; Notice of "
                     r"Availability|Notice of Filing\b|Notice of Institution of Section 206|Records Governing Off-the-Record|"
                     r"Self-Certification|Change in Status|Market-Based Rate|Filing of Revised Rate|Supplemental Notice)",
                     re.I)
SECTOR_TAGS = [  # (tag, pattern) on title + abstract + Register topics
    ("power", r"\b(electric\w*|power plant|power sector|generat\w+|grid|reliability|capacity market|RTO|ISO)\b"),
    ("transmission", r"\b(transmission|interconnection|transmission line)\b"),
    ("gas", r"\b(natural gas|gas pipeline|interstate pipeline|LNG|liquefied natural gas|methane)\b"),
    ("oil", r"\b(oil|petroleum|crude|refiner\w*|gasoline|diesel)\b"),
    ("nuclear", r"\b(nuclear|reactor|uranium|spent fuel|radioactive)\b"),
    ("renewables", r"\b(renewable|solar|wind|geothermal|hydroelectric|hydropower|biofuel)\b"),
    ("storage", r"\b(storage|batter(y|ies))\b"),
    ("coal", r"\b(coal)\b"),
    ("efficiency", r"\b(energy conservation|efficiency standard\w*|appliance)\b"),
    ("emissions", r"\b(emission\w*|greenhouse gas|carbon|air quality)\b"),
    ("datacenters", r"\b(data ?cent(er|re)s?|large load\w*)\b"),
    ("leasing", r"\b(lease\w*|leasing|right-of-way|public lands)\b"),
    ("hydrogen", r"\b(hydrogen)\b"),
    ("minerals", r"\b(critical mineral\w*|lithium|mining)\b"),
]
STATES = {"Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA", "Colorado": "CO",
          "Connecticut": "CT", "Delaware": "DE", "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID",
          "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA",
          "Maine": "ME", "Maryland": "MD", "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN",
          "Mississippi": "MS", "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV",
          "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY", "North Carolina": "NC",
          "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA",
          "Rhode Island": "RI", "South Carolina": "SC", "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX",
          "Utah": "UT", "Vermont": "VT", "Virginia": "VA", "Washington": "WA", "West Virginia": "WV",
          "Wisconsin": "WI", "Wyoming": "WY"}
SCORE_COLS = ["significance", "sector", "why", "model_id", "scored_at"]
COLS = ["event_id", "event_date", "event_type", "parties", "entity_ids", "mw", "price", "currency", "status", "source",
        "source_url", "agency", "action_type", "title", "abstract", "docket", "rin", "fr_document_number",
        "sector_tags", "states", "related_urls", "news_story_ids", "news_story_urls"] + SCORE_COLS + ["retrieved_at"]
STOP = set("the and for of to in on a an by with from at as is are be or its that this under final notice rule "
           "proposed commission department agency federal u.s. us announces approves".split())


# Session 154 (the audit of 50 rows against their source documents, runs/session154/agent_report_audit.md): five
# rules below were wrong for a class of documents. Each is tested on the real documents in tests/fixtures/session154/.
INLINE = re.compile(r"</?(?:INF|SUB|SUP|E|I|B|EM|STRONG|SMALL)\b[^>]*>", re.I)  # the Register's inline markup
NOT_A_STATE = re.compile(r"\bWashington,? D\.? ?C\b\.?|\bDistrict of Columbia\b")
GAS_DOCKET = re.compile(r"\b(?:CP|PF)\d{2}-\d+")  # FERC: a natural gas certificate docket, or its pre-filing
HYDRO_DOCKET = re.compile(r"\bProject Nos?\. ?\d|\bDI\d{2}-\d+")  # FERC: a hydropower project, or a declaration of intention
NRC_STORAGE = re.compile(r"\b(batter(y|ies)|energy storage)\b", re.I)
EASTERN = "America/New_York"  # NRC and DOE date a release by the day in Washington, not by the UTC day of the feed


def clean(s):
    # NO<INF>X</INF> is "NOX": inline markup goes without a space (it left "NO X " in 2026-13027's abstract)
    s = H.unescape(re.sub(r"<[^>]+>", " ", INLINE.sub("", s or "")))
    s = s.replace(chr(0x2014), ", ").replace(chr(0x2013), "-")
    return re.sub(r"\s+", " ", s).strip()


def tags(text, agency="", docket=""):
    """The sector tags: the keyword rules on the text, and (session 154) what the agency and the docket say where the
    text cannot. A FERC notice has no abstract in the Register's API, so its tags rested on a title that is often only
    the applicant's name: a CP docket is a natural gas certificate (and "Transmission" in a pipeline company's name is
    not the electric transmission sector), a Project No. or DI docket is a hydropower project. Every NRC document is
    nuclear; "storage" in one is spent fuel or waste storage unless it speaks of batteries or energy storage."""
    got = {t for t, p in SECTOR_TAGS if re.search(p, text, re.I)}
    if agency == "FERC" and GAS_DOCKET.search(docket or ""):
        got = (got | {"gas"}) - {"transmission"}
    if agency == "FERC" and HYDRO_DOCKET.search(docket or ""):
        got |= {"power", "renewables"}
    if agency == "NRC":
        got.add("nuclear")
        if not NRC_STORAGE.search(text):
            got.discard("storage")
    return ";".join(t for t, _ in SECTOR_TAGS if t in got)


def states(text):
    """US states named in the text. Session 154: the longest name is read first and taken out, so "West Virginia" is
    not also Virginia (2026-02830 held VA;WV), and "Washington, DC" is not the state of Washington."""
    t = NOT_A_STATE.sub(" ", text or "")
    out = set()
    for n, c in sorted(STATES.items(), key=lambda kv: -len(kv[0])):
        t, k = re.subn(rf"\b{n}\b", " ", t)
        if k:
            out.add(c)
    return ";".join(sorted(out))


def get(url, log, **kw):
    def call():
        r = requests.get(url, headers=UA, timeout=90, **kw)
        if r.status_code != 200:
            raise RuntimeError(f"HTTP {r.status_code} for {r.url}")
        return r
    return ip.with_retries(url, call, log)


def federal_register(since, log):
    fields = ["document_number", "type", "title", "abstract", "action", "publication_date", "agencies", "docket_ids",
              "regulation_id_numbers", "html_url", "topics", "significant"]
    rows, got = [], ip.utc_iso(pd.Timestamp.now(tz="UTC"))
    for slug, short in AGENCIES.items():
        for t in TYPES:
            page = 1
            while True:
                r = get(FR, log, params={"conditions[agencies][]": slug, "conditions[type][]": {"Rule": "RULE",
                        "Proposed Rule": "PRORULE", "Notice": "NOTICE"}[t], "conditions[publication_date][gte]": since,
                        "per_page": 1000, "page": page, "order": "oldest", "fields[]": fields})
                d = r.json()
                for x in d.get("results", []):
                    x["_short"], x["_url"], x["_got"] = short, r.url, got
                    rows.append(x)
                log(f"  Federal Register {short} {t} page {page}: {len(d.get('results', []))} (of {d.get('count')})")
                if page >= (d.get("total_pages") or 1):
                    break
                page += 1
    out, seen = [], set()
    for x in rows:
        if x["document_number"] in seen:
            continue
        seen.add(x["document_number"])
        names = [a.get("name") or a.get("raw_name", "") for a in x.get("agencies") or []]
        shorts = [AGENCIES.get((a.get("url") or "").rstrip("/").split("/")[-1], "") for a in x.get("agencies") or []]
        agency = "FERC" if "FERC" in shorts else next((s for s in ["NRC", "BLM", "EPA", "DOE", "Interior"] if s in shorts),
                                                       x["_short"])
        title, abstract = clean(x.get("title")), clean(x.get("abstract"))
        text = f"{title} {abstract} {' '.join(x.get('topics') or [])}"
        if agency not in ALWAYS_ENERGY and not ENERGY.search(text):
            continue
        if ROUTINE.search(title):
            continue
        rins = [r_ for r_ in x.get("regulation_id_numbers") or [] if r_]
        docket = ";".join([d_ for d_ in x.get("docket_ids") or [] if d_] + rins)
        out.append({"event_id": f"federalregister:{x['document_number']}", "event_date": x["publication_date"],
                    "event_type": "filing", "parties": ";".join(n for n in names if n), "status": clean(x.get("action")),
                    "source": "federalregister:api", "source_url": x["html_url"], "agency": agency,
                    "action_type": TYPES.get(x["type"], "notice"), "title": title, "abstract": abstract[:1500],
                    "docket": docket, "rin": ";".join(rins),
                    "fr_document_number": x["document_number"], "sector_tags": tags(text, agency, docket),
                    "states": states(text), "retrieved_at": x["_got"]})
    log(f"  Federal Register: {len(seen)} documents, {len(out)} kept (energy, not routine)")
    return out


def rss(name, agency, url, since, log):
    r = get(url, log)
    got = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
    out = rss_rows(name, agency, r.content, since, got)
    log(f"  {name}: {len(out)} items since {since} (the feed's window)")
    return out


def release_day(pub_date):
    """The day a feed item was released, as the agency dates it (session 154). The NRC's feed gives GMT times, so a
    release of the evening in Washington carried the next day's date: 24 of the feed's 167 items on 8 October 2026,
    and each of the 7 releases opened states the Eastern day. None when the feed's date cannot be read."""
    when = pd.to_datetime(pub_date, utc=True, errors="coerce")
    return None if pd.isna(when) else when.tz_convert(EASTERN).strftime("%Y-%m-%d")


def rss_rows(name, agency, content, since, got):
    """The rows of one feed (its bytes), apart from the request so that a saved feed can be read again."""
    out = []
    for it in ET.fromstring(content).iter("item"):
        title, link = clean(it.findtext("title")), (it.findtext("link") or "").strip()
        day = release_day(it.findtext("pubDate"))
        if not link or day is None or day < since:
            continue
        desc = clean(it.findtext("description"))
        text = f"{title} {desc}"
        out.append(press(name, agency, link, day, title, text, got,
                         "TX" if agency == "PUCT" else "CA" if agency == "CPUC" else states(text)))
    return out


def press(name, agency, link, date, title, text, got, st):
    # session 154: the PUCT's news page also lists releases of the Governor's office (gov.texas.gov); the row stays
    # under the commission that lists it, and parties names who issued it
    parties = f"Office of the Texas Governor;{agency}" if "gov.texas.gov" in link.lower() else agency
    return {"event_id": f"{name}:{hashlib.sha1(link.encode()).hexdigest()[:12]}", "event_date": date,
            "event_type": "announcement", "parties": parties, "status": "news release", "source": f"{name}:news",
            "source_url": link, "agency": agency, "action_type": "press_release", "title": title, "abstract": "",
            "docket": "", "rin": "", "fr_document_number": "", "sector_tags": tags(text, agency), "states": st,
            "retrieved_at": got}


def puct(since, log):
    url = "https://www.puc.texas.gov/agency/resources/pubs/news/"
    t = get(url, log).text
    got = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
    out = []
    for link, title, date in re.findall(r'<a href="([^"]+)"[^>]*>([^<]{10,300})</a><br\s*/?>\s*<span[^>]*>([A-Z][a-z]+ \d{1,2}, \d{4})',
                                        t):
        d = pd.to_datetime(date, errors="coerce")
        if pd.isna(d) or d.strftime("%Y-%m-%d") < since:
            continue
        # the page also lists the Governor's releases about the PUCT's programs: kept, with their own link
        out.append(press("puct", "PUCT", link, d.strftime("%Y-%m-%d"), clean(title), clean(title), got, "TX"))
    log(f"  PUCT news page: {len(out)} dated items since {since}")
    return out


def cpuc(since, log):
    out, got = [], ip.utc_iso(pd.Timestamp.now(tz="UTC"))
    for page in range(0, 80):
        t = get("https://www.cpuc.ca.gov/news-and-updates/all-news" + (f"?page={page}" if page else ""), log).text
        items = re.findall(r'<a href="(https://www\.cpuc\.ca\.gov/news-and-updates/all-news/[^"]+)">.*?'
                           r'<span class="heading__main">(.*?)</span>.*?news__date[^>]*>([A-Z][a-z]+ \d{1,2}, \d{4})', t, re.S)
        if not items:
            break
        older = False
        for link, title, date in items:
            d = pd.to_datetime(date, errors="coerce")
            if pd.isna(d):
                continue
            if d.strftime("%Y-%m-%d") < since:
                older = True
                continue
            if not ENERGY.search(clean(title)):  # the CPUC also regulates rail, water and telecommunications
                continue
            out.append(press("cpuc", "CPUC", link, d.strftime("%Y-%m-%d"), clean(title), clean(title), got, "CA"))
        if older:
            break
    log(f"  CPUC news: {len(out)} items since {since} ({page + 1} pages read)")
    return out


def words(s):
    return {w for w in re.findall(r"[a-z0-9]+", (s or "").lower()) if w not in STOP and len(w) > 2}


def similar(a, b):
    wa, wb = words(a), words(b)
    return len(wa & wb) / max(1, len(wa | wb))


def fold_press(frame, log):
    """A news release that reports a Register document (the same docket in its text, or a title of the same content
    words, similarity 0.5 or more, within 30 days) is folded into it: its link goes to related_urls."""
    fr = frame[frame["action_type"] != "press_release"]
    pr = frame[frame["action_type"] == "press_release"]
    drop = []
    frd = pd.to_datetime(fr["event_date"])
    for i, p in pr.iterrows():
        near = fr[(abs(frd - pd.Timestamp(p["event_date"])) <= pd.Timedelta(days=30)) & (fr["agency"] == p["agency"])]
        best = max(((similar(p["title"], r["title"]), j) for j, r in near.iterrows()), default=(0, None))
        if best[0] >= 0.5:
            j = best[1]
            frame.at[j, "related_urls"] = ";".join(x for x in [frame.at[j, "related_urls"], p["source_url"]] if x)
            drop.append(i)
    log(f"  {len(drop)} news releases folded into the Register documents they report")
    return frame.drop(index=drop)


def link_news(frame, log):
    """The scored news stories that report the same action (deduplication against news_stories)."""
    path = os.path.join(ip.OUT_DIR, "news_stories.csv")
    if not os.path.exists(path):
        log("  news_stories.csv not on this machine: no links to news")
        return frame
    with open(path, encoding="utf-8") as fh:
        skip = sum(1 for line in fh if line.startswith("#"))
    n = pd.read_csv(path, skiprows=skip, dtype=str, keep_default_na=False)
    n = n[n.get("scored_at", "") != ""] if "scored_at" in n.columns else n
    n = n.assign(d=pd.to_datetime(n["event_date"], utc=True, errors="coerce").dt.tz_localize(None).dt.normalize(),
                 text=(n["title"].fillna("") + " " + n["summary"].fillna("")))
    n = n[n["d"] >= pd.Timestamp(frame["event_date"].min()) - pd.Timedelta(days=21)]
    nwords = [words(t) for t in n["title"]]
    linked = 0
    for i, r in frame.iterrows():
        d = pd.Timestamp(r["event_date"])
        ids = [x for x in (r["docket"].split(";") + [r["fr_document_number"]]) if len(x) >= 6]
        hit = set()
        if ids:
            m = n["text"].str.contains("|".join(re.escape(x) for x in ids), regex=True)
            hit |= set(n.index[m])
        rw = words(r["title"])
        win = n.index[(n["d"] >= d - pd.Timedelta(days=2)) & (n["d"] <= d + pd.Timedelta(days=21))]
        for j in win:
            k = n.index.get_loc(j)
            if rw and len(rw & nwords[k]) / max(1, len(rw | nwords[k])) >= 0.5:
                hit.add(j)
        if r["action_type"] == "press_release":  # the agency's own feed item, already in news_stories
            hit |= set(n.index[n["source_url"] == r["source_url"]])
        if hit:
            frame.at[i, "news_story_ids"] = ";".join(sorted(n.loc[list(hit), "event_id"]))
            frame.at[i, "news_story_urls"] = ";".join(sorted(n.loc[list(hit), "source_url"]))
            linked += 1
    log(f"  {linked} actions linked to the news stories that report them")
    return frame


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW policy sources")
    ap.add_argument("--since", default="2025-10-01")
    ap.add_argument("--out-dir", help="session 154: a trial run, every output (the table, logs, raw files, registry, "
                                      "status) under this directory and nothing under warehouse/output")
    args = ap.parse_args(argv)
    if args.out_dir:
        ip.set_out_dir(args.out_dir)
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"policy_sources_{run_id}.log"))
    ip.RAW.open("policy_sources", run_id)
    results, rows, absent = [], [], []
    try:
        for name, fn in (("federalregister", lambda: federal_register(args.since, log)),
                         ("nrc", lambda: rss("nrc", "NRC", "https://www.nrc.gov/public-involve/rss?feed=news", args.since, log)),
                         ("doe", lambda: rss("doe", "DOE", "https://www.energy.gov/rss/newsroom.xml", args.since, log)),
                         ("puct", lambda: puct(args.since, log)), ("cpuc", lambda: cpuc(args.since, log))):
            try:
                got = fn()
                rows += got
                results.append(dict(table=NAME, market=name, status="ok", detail=f"{len(got)} rows"))
            except Exception as exc:
                last = ip.redact(repr(exc))[:300]
                log(f"{name} FAILED: {last}")
                print(f"policy_sources {name} FAILED: {last}", file=sys.stderr)
                absent.append(name)
                results.append(dict(table=NAME, market=name, status="failed", detail=last))
        if not rows:
            raise RuntimeError("no source returned rows")
        f = pd.DataFrame(rows)
        for c in COLS:
            if c not in f.columns:
                f[c] = ""
        f = f.drop_duplicates("event_id").reset_index(drop=True).fillna("")
        f = fold_press(f, log)
        f = link_news(f, log)
        if os.path.exists(SCORES):  # the scores warehouse/policy/score.py wrote, kept across runs
            s = pd.read_csv(SCORES, dtype=str, keep_default_na=False).drop_duplicates("event_id", keep="last")
            f = f.drop(columns=SCORE_COLS).merge(s[["event_id"] + SCORE_COLS], on="event_id", how="left").fillna("")
        f = f[COLS].sort_values(["event_date", "event_id"])
        header = [
            "Energy Research Warehouse (ERW): policy actions: Federal Register rules, proposed rules and notices of DOE, "
            "FERC, EPA, NRC, BLM and Interior on energy, and news releases of NRC, DOE, the PUCT and the CPUC",
            "Shape: events (docs/datastandard.md v0). event_date is the publication or release date; the columns after "
            "source_url are described in warehouse/connectors/policy_sources.py.",
            f"Window: {args.since} to the run; every run reads the Register window again and merges news releases.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/policy_sources.py",
            f"Run log: warehouse/output/logs/policy_sources_{run_id}.log",
            f"Raw files: warehouse/raw/policy_sources/{run_id}/ (not in git)",
            "Sources: federalregister:api (https://www.federalregister.gov/developers/documentation/api/v1); nrc:news "
            "(https://www.nrc.gov/public-involve/rss?feed=news); doe:news (https://www.energy.gov/rss/newsroom.xml); "
            "puct:news (https://www.puc.texas.gov/agency/resources/pubs/news/); cpuc:news "
            "(https://www.cpuc.ca.gov/news-and-updates/all-news). FERC's own pages answer a Cloudflare challenge: not read.",
            "Scores (significance, sector, why) from warehouse/policy/score.py with the news rubric; blank = not scored.",
        ] + ([f"Absent inputs: {', '.join(absent)} (failed this run; their rows from earlier runs are kept)"] if absent else []) + [
            "License: public (US and state government publications)."]
        ip.write_csv(f, NAME, header, log, cols=COLS, key=["event_id"], time_col="event_date")
        ip.update_sources([
            dict(source="federalregister:api", publisher="Office of the Federal Register (NARA)",
                 report="Federal Register documents API", report_url="https://www.federalregister.gov/developers/documentation/api/v1",
                 document_list=FR, license="public", tables=[NAME]),
            dict(source="nrc:news", publisher="U.S. Nuclear Regulatory Commission (NRC)", report="NRC news releases (RSS)",
                 report_url="https://www.nrc.gov/reading-rm/doc-collections/news/", document_list="https://www.nrc.gov/public-involve/rss?feed=news",
                 license="public", tables=[NAME]),
            dict(source="doe:news", publisher="U.S. Department of Energy (DOE)", report="DOE newsroom (RSS)",
                 report_url="https://www.energy.gov/newsroom", document_list="https://www.energy.gov/rss/newsroom.xml",
                 license="public", tables=[NAME]),
            dict(source="puct:news", publisher="Public Utility Commission of Texas (PUCT)", report="PUCT news releases",
                 report_url="https://www.puc.texas.gov/agency/resources/pubs/news/", document_list="https://www.puc.texas.gov/agency/resources/pubs/news/",
                 license="public", tables=[NAME]),
            dict(source="cpuc:news", publisher="California Public Utilities Commission (CPUC)", report="CPUC news",
                 report_url="https://www.cpuc.ca.gov/news-and-updates/all-news", document_list="https://www.cpuc.ca.gov/news-and-updates/all-news",
                 license="public", tables=[NAME])])
        by = f.groupby(["agency", "action_type"]).size()
        log("rows by agency and type: " + "; ".join(f"{a} {t} {n}" for (a, t), n in by.items()))
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{NAME} FAILED, no output file written:\n{tb}")
        print(f"policy_sources {NAME} FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    ip.write_status("policy_sources", run_id, results)
    log.close()
    print(f"policy_sources run log: {os.path.relpath(log.path, ip.ROOT)}")
    return 1 if any(r["status"] == "failed" and r["market"] == "all" for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
