#!/usr/bin/env python3
"""The Haiku shadow scorer: every story the daily run scores with Sonnet, scored again by a cheaper model, kept apart.

Energy Research Warehouse (ERW), session 30 (Part B4). The shadow model (SHADOW_MODEL, claude-haiku-4-5 in the
workflows; unset it to stop the shadow) scores the same stories with the same rubric, system prompt, schema and batching
as warehouse/news/score.py, into its own internal table, news_scores_shadow. It never writes news_stories, news_index or
any public table. From those scores the run builds a second Digest and a second Roundup, sent to one address only with
the subject prefixed "SHADOW HAIKU", until the expiry date in warehouse/config/shadow.yaml.

    python warehouse/news/shadow.py score                       # the daily run: stories Sonnet scored in the last 3 days
    python warehouse/news/shadow.py score --days 30 --eval      # the backtest: 30 days, and the 50 eval-sample stories
    python warehouse/news/shadow.py score --date 2026-09-26 --no-cache --no-write   # the caching measurement
    python warehouse/news/shadow.py digest [--date YYYY-MM-DD]  # the shadow Digest, to the shadow recipient
    python warehouse/news/shadow.py roundup [--week YYYY-Www]   # the shadow Roundup, to the shadow recipient

Stories are scored day by day (UTC publish day), oldest first, in batches of `batch` (shadow.yaml). Each day's reference
list for is_duplicate_of is the Sonnet-scored stories of the two days before it, as score.py offers the stories scored
before a run; it is cached (score.request_parts), so every call of a day after the first reads it from the cache.
The shadow's clusters are built from its own is_duplicate_of links, as score.py builds them.

Haiku 4.5 takes no effort setting; temperature 0 is sent. Every call goes through warehouse/llm.py (step
news_score_shadow, or the --step given), so its cost is in api_cost_ledger.
"""

import argparse
import datetime as dt
import json
import os
import sys
import traceback

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", "connectors"))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
import iso_prices as ip  # noqa: E402
import llm  # noqa: E402
import score  # noqa: E402
from ingest import NAME as NEWS, NEWS_COLS  # noqa: E402

NAME = "news_scores_shadow"
CONFIG = os.path.join(ROOT, "warehouse", "config", "shadow.yaml")
EVAL = os.path.join(HERE, "eval", "eval_sample.csv")
SHADOW_DIR = os.path.join(ROOT, "warehouse", "output", "shadow")  # the shadow issues and the stories view; not an ERW table
COLS = ["event_id", "event_date", "event_type", "parties", "mw", "source", "source_url",
        "story_id", "model_id", "significance", "ai_power_relevance", "sector", "region", "price_mentioned",
        "headline", "why", "is_duplicate_of", "cluster_id", "scored_at", "run_id"]
KEY = ["event_id"]
SCORED = ["significance", "ai_power_relevance", "sector", "region", "price_mentioned", "why", "cluster_id",
          "model_id", "scored_at", "headline", "parties", "mw"]


def config():
    import yaml
    with open(CONFIG, encoding="utf-8") as f:
        c = yaml.safe_load(f)
    c["expires"] = str(c["expires"])
    return c


def gate(log):
    """(model, reason): the shadow model, or None and why the shadow does not run today."""
    model = os.environ.get("SHADOW_MODEL", "").strip()
    if not model:
        return None, "SHADOW_MODEL is not set (the kill switch): no shadow call"
    today = dt.datetime.now(dt.timezone.utc).date().isoformat()
    if today >= config()["expires"]:
        return None, f"the shadow expired on {config()['expires']} (warehouse/config/shadow.yaml); no shadow call"
    return model, ""


def read_shadow():
    path = os.path.join(ip.OUT_DIR, NAME + ".csv")
    return ip.read_series(path, COLS) if os.path.exists(path) else pd.DataFrame(columns=COLS)


HEADER = [
    "Energy Research Warehouse (ERW): shadow news scores, the stories the daily run scored with its Sonnet-class "
    "model, scored again by a second model (the shadow, SHADOW_MODEL) with the same rubric (warehouse/news/rubric.md), "
    "system prompt, schema and batching, to measure whether it can replace the first (session 30, Part B4).",
    "Written by warehouse/news/shadow.py. One row per story and shadow model; story_id is the story's event_id in "
    "news_stories, whose own scores are the published ones. The scores and text fields here are the shadow model's "
    "(model_id), never shown on the site.",
    "License: internal. A comparison table: the stories' titles and summaries stay in news_stories (internal); the "
    "shadow's scores reach no public table, page or subscriber.",
    "Agreement with the published scores: warehouse/news/shadow_agreement.py.",
]


def call(client, model, ref_list, seen, stories, cache, log):
    parts = score.request_parts(ref_list, seen, stories, cache=cache)
    kwargs = dict(model=model, max_tokens=16000, extra_body={"temperature": 0},
                  output_config={"format": {"type": "json_schema", "schema": score.SCHEMA}}, **parts)
    if "haiku" not in model:  # effort is not accepted by Haiku 4.5; the Sonnet-class models take it
        kwargs["output_config"]["effort"] = "low"
    resp = client.messages.create(**kwargs)
    if resp.stop_reason != "end_turn":
        raise RuntimeError(f"stop_reason {resp.stop_reason}")
    text = next(b.text for b in resp.content if b.type == "text")
    return json.loads(text)["results"], resp


def cmd_score(args, log, run_id):
    model, why = gate(log)
    if model is None:
        log(why)
        print(f"news_score_shadow SKIPPED: {why}")
        return dict(table=NAME, market="shadow", status="skipped", detail=why)
    cfg = config()
    news = ip.read_series(os.path.join(ip.OUT_DIR, NEWS + ".csv"), NEWS_COLS)
    when = pd.to_datetime(news["event_date"], utc=True, format="ISO8601")
    news = news.assign(_when=when, _day=when.dt.strftime("%Y-%m-%d"))
    scored = news[news["scored_at"] != ""]
    old = read_shadow()
    done = set(old.loc[old["model_id"] == model, "story_id"]) if args.write else set()
    if args.date:
        pick = scored[scored["_day"].isin(args.date)]
    else:
        pick = scored[scored["_when"] >= pd.Timestamp.now(tz="UTC") - pd.Timedelta(days=args.days)]
    if args.eval and os.path.exists(EVAL):
        ev = set(pd.read_csv(EVAL, dtype=str, keep_default_na=False)["id"])
        pick = pd.concat([pick, scored[scored["event_id"].isin(ev)]]).drop_duplicates("event_id")
    todo = pick[~pick["event_id"].isin(done)].sort_values("_when")
    log(f"shadow model {model}; {len(pick)} Sonnet-scored stories in scope, {len(todo)} without a shadow score; "
        f"cache {'on' if args.cache else 'off'}; write {'yes' if args.write else 'no (measurement)'}")
    if todo.empty:
        return dict(table=NAME, market="shadow", status="ok", detail=f"{model}: nothing to score")
    client = llm.client(args.step, log)
    cluster = {r["story_id"]: r["cluster_id"] for r in old[old["model_id"] == model].to_dict("records")}
    known = set(news["event_id"])
    rows, failed, n_calls = [], 0, 0
    now = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
    for day, g in todo.groupby("_day", sort=True):
        d0 = pd.Timestamp(day, tz="UTC")
        ref = scored[(scored["_when"] >= d0 - pd.Timedelta(days=2)) & (scored["_when"] < d0)].sort_values("_when")
        ref_list = [f"{r.event_id} | {r.title[:120]}" for r in ref.itertuples()]
        seen = []
        batches = [g.iloc[i:i + cfg["batch"]] for i in range(0, len(g), cfg["batch"])]
        for bi, b in enumerate(batches, 1):
            stories = [{"id": r.event_id, "published": r.event_date, "outlet": r.source, "feed_beat": r.feed_sector,
                        "title": r.title, "summary": r.summary} for r in b.itertuples()]
            try:
                n_calls += 1
                out, resp = call(client, model, ref_list, seen, stories, args.cache, log)
            except llm.SpendCapReached:
                raise
            except Exception as exc:
                failed += 1
                log(f"  {day} call {bi}: FAILED ({len(b)} stories left unscored): {ip.redact(repr(exc))[:300]}")
                continue
            u = llm.usage_numbers(resp.usage)
            ids = set(b["event_id"])
            got = {r["id"]: r for r in out if r["id"] in ids}
            log(f"  {day} call {bi}/{len(batches)}: {len(b)} stories, {len(got)} scored; tokens in {u['input']} "
                f"cache read {u['cache_read']} cache write {u['cache_write']} out {u['output']}; "
                f"USD {llm.usd(model, u) or 0:.4f}; request {resp._request_id}")
            titles = b.set_index("event_id")["title"]
            for eid in b["event_id"]:
                if eid not in got:
                    continue
                r = got[eid]
                sig, ai = int(r["significance"]), int(r["ai_power_relevance"])
                if not (0 <= sig <= 10 and 0 <= ai <= 10):
                    log(f"  {eid}: score out of range ({sig}, {ai}); left out")
                    continue
                dup = r["is_duplicate_of"]
                if dup and (dup == eid or dup not in known):
                    dup = None
                cluster[eid] = cluster.get(dup, dup) if dup else eid
                s = b.set_index("event_id").loc[eid]
                rows.append({
                    "event_id": f"shadow:{eid}:{model}", "event_date": s["event_date"], "event_type": "shadow_score",
                    "parties": score.nodash("; ".join(p.replace(";", ",") for p in r["parties"])),
                    "mw": "" if r["mw_mentioned"] is None else f"{float(r['mw_mentioned']):g}",
                    "source": s["source"], "source_url": s["source_url"], "story_id": eid, "model_id": model,
                    "significance": str(sig), "ai_power_relevance": str(ai), "sector": r["sector"],
                    "region": score.nodash(r["region"]), "price_mentioned": score.nodash(r["price_mentioned"] or ""),
                    "headline": score.nodash(r["headline"]), "why": score.nodash(" ".join(r["one_line_why"].split())),
                    "is_duplicate_of": dup or "", "cluster_id": cluster[eid], "scored_at": now, "run_id": run_id})
                seen.append(f"{eid} | {titles[eid][:120]}")
    spent = sum(float(x["usd"] or 0) for x in client.calls)
    detail = (f"{model}: {len(rows)} of {len(todo)} stories scored in {n_calls} calls ({failed} failed); "
              f"USD {spent:.4f} (api_cost_ledger, step {args.step}); cache {'on' if args.cache else 'off'}")
    log("RUN " + detail)
    if args.write and rows:
        ip.write_csv(pd.DataFrame(rows, columns=COLS), NAME, HEADER + [f"Retrieved: {run_id} (shadow scoring run).",
                                                               f"Run log: warehouse/output/logs/news_shadow_score_{run_id}.log"],
                     log, cols=COLS, key=KEY, time_col="event_date")
    print(f"news_score_shadow: {detail}")
    return dict(table=NAME, market="shadow", status="failed" if failed and not rows else "ok", detail=detail[:300])


def view(model, log):
    """The stories as news_stories has them, with the shadow's scores in place of the published ones; a story the
    shadow has not scored is left unscored. Written under warehouse/output/shadow/ (not an ERW table)."""
    news = ip.read_series(os.path.join(ip.OUT_DIR, NEWS + ".csv"), NEWS_COLS)
    sh = read_shadow()
    sh = sh[sh["model_id"] == model].set_index("story_id")
    news = news.set_index("event_id")
    news[SCORED] = ""
    both = news.index.intersection(sh.index)
    for c in SCORED:
        news.loc[both, c] = sh.loc[both, c]
    news = news.reset_index()[NEWS_COLS]
    os.makedirs(SHADOW_DIR, exist_ok=True)
    path = os.path.join(SHADOW_DIR, "news_stories_shadow_view.csv")
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(f"# The stories of news_stories with the {model} shadow scores (news_scores_shadow) in place of the "
                "published ones; written by warehouse/news/shadow.py for the shadow Digest and Roundup. Not an ERW table.\n")
        news.to_csv(f, index=False, lineterminator="\n")
    log(f"view: {len(both)} stories with {model} scores -> {os.path.relpath(path, ROOT)}")
    return path


def send(kind, path, model, log):
    """The shadow issue to the shadow recipient only, subject prefixed."""
    import requests
    import email_digest as em
    cfg = config()
    key = em.env("RESEND_API_KEY")
    to = [a.strip() for a in (em.env("SHADOW_RECIPIENT") or em.env("DIGEST_RECIPIENTS")).split(",") if a.strip()]
    if not key or not to:
        log("  not sent: RESEND_API_KEY or SHADOW_RECIPIENT/DIGEST_RECIPIENTS not set")
        return "not sent (no key or recipient)"
    if len(to) != 1:  # session 34: the shadow goes to one address (Samuel's), never to a list that has grown
        log(f"  not sent: {len(to)} addresses; the shadow goes to one only (set SHADOW_RECIPIENT to that address)")
        return f"not sent ({len(to)} addresses; the shadow goes to one)"
    note = (f"Shadow issue: the stories are selected and described by {model}'s scores (news_scores_shadow), for "
            "comparison with the published issue. Not published; sent to one address.")
    title, label, text, body = em.render(path, kind, note=note, unsubscribe=None)
    subject = f"{cfg['subject_prefix']}: {title}"
    for addr in to:
        r = requests.post(em.RESEND, headers={"Authorization": f"Bearer {key}"}, timeout=60,
                          json={"from": em.env("DIGEST_FROM") or "ERW Energy Digest <onboarding@resend.dev>",
                                "to": [addr], "subject": subject, "text": text, "html": body})
        if r.status_code >= 300:
            raise RuntimeError(f"Resend HTTP {r.status_code}: {ip.redact(r.text[:200])}")
        log(f"  sent '{subject}' (Resend id {r.json().get('id', '?')})")
    return f"sent '{subject}' to {len(to)} address"


def cmd_issue(args, log, run_id, kind):
    model, why = gate(log)
    if model is None:
        log(why)
        print(f"news_{kind}_shadow SKIPPED: {why}")
        return dict(table=kind, market="shadow", status="skipped", detail=why)
    stories = view(model, log)
    os.makedirs(SHADOW_DIR, exist_ok=True)
    if kind == "digest":
        import brief
        date = args.date or pd.Timestamp.now(tz="UTC").strftime("%Y-%m-%d")
        if pd.Timestamp(date).weekday() >= 5:
            msg = f"no weekend issue ({date}); the digest is a weekday email"
            print(f"news_digest_shadow SKIPPED: {msg}")
            return dict(table=kind, market="shadow", status="skipped", detail=msg)
        out = os.path.join(SHADOW_DIR, f"digest-{date}.md")
        rc = brief.main(["--date", date, "--stories", stories, "--out", out])
        em_kind = "daily"
    else:
        import roundup
        label = args.week or ""
        out = os.path.join(SHADOW_DIR, f"roundup-{label or 'latest'}.md")
        rc = roundup.main((["--week", args.week] if args.week else []) + ["--stories", stories, "--out", out])
        em_kind = "roundup"
    if rc != 0 or not os.path.exists(out):
        raise RuntimeError(f"the shadow {kind} was not written (exit {rc}); see the brief's log")
    detail = f"{os.path.relpath(out, ROOT)}; " + (send(em_kind, out, model, log) if args.send else "not sent (--no-send)")
    print(f"news_{kind}_shadow: {detail}")
    return dict(table=kind, market="shadow", status="ok", detail=detail[:300])


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW shadow scorer (session 30, B4)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("score")
    s.add_argument("--days", type=int, default=3, help="stories Sonnet scored, published in the last N days")
    s.add_argument("--date", nargs="+", help="only these publish days (UTC), YYYY-MM-DD")
    s.add_argument("--eval", action="store_true", help="also the 50 stories of warehouse/news/eval/eval_sample.csv")
    s.add_argument("--no-cache", dest="cache", action="store_false", help="no cache breakpoints (the measurement)")
    s.add_argument("--no-write", dest="write", action="store_false", help="score, record the cost, write no row")
    s.add_argument("--step", default="news_score_shadow", help="the ledger's step name")
    d = sub.add_parser("digest")
    d.add_argument("--date")
    d.add_argument("--no-send", dest="send", action="store_false")
    r = sub.add_parser("roundup")
    r.add_argument("--week")
    r.add_argument("--no-send", dest="send", action="store_false")
    args = ap.parse_args(argv)
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"news_shadow_{args.cmd}_{run_id}.log"))
    try:
        res = cmd_score(args, log, run_id) if args.cmd == "score" else cmd_issue(args, log, run_id, args.cmd)
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED:\n{tb}")
        print(f"news_shadow {args.cmd} FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        res = dict(table=NAME if args.cmd == "score" else args.cmd, market="shadow", status="failed",
                   detail=tb.strip().splitlines()[-1][:300])
    ip.write_status(f"news_shadow_{args.cmd}", run_id, [res])
    log.close()
    return 0 if res["status"] in ("ok", "skipped") else 1


if __name__ == "__main__":
    sys.exit(main())
