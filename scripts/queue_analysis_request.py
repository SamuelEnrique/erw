#!/usr/bin/env python3
"""Queue one real request for the findings worker, as the page /analysis does (session 181).

Energy Research Warehouse (ERW).

    python scripts/queue_analysis_request.py --dry-run                 # print the call; send nothing
    python scripts/queue_analysis_request.py                           # queue queue_divorce from 2010 (the proof request)
    python scripts/queue_analysis_request.py --watch 300               # queue it, then wait up to 300 seconds for the worker
    python scripts/queue_analysis_request.py --finding gas_sets_price --param heat_rate=7 --watch 600

It calls the same database function the page's route calls (public.analysis_request, migration 027; the route is
site/app/api/analysis/route.ts): a POST to <SUPABASE_URL>rpc/analysis_request with the site's public key and the
internal token as p_token, both read from the .env of this checkout. The function checks the token, counts the day's
requests (24 a UTC day) and writes one queued row; the worker on the data machine takes it. With --watch the script
then reads the queue as the page does (analysis_requests_list) every 10 seconds until the row is done or failed, and
prints its state, its times and the card's id; the card's file is site/data/findings/<card id>.json on the data
machine. The default request is the cheapest finding, queue_divorce (one small table, seconds), asked from 2010 and not
from its default first year: the card is then queue_divorce__first_year-2010, a file of its own, and the committed
default card (queue_divorce.json, with its pinned downloads) is not rewritten by a proof.

Neither the token nor a key is ever printed. Exit 0 queued (and, with --watch, done), 1 not queued or failed, 2 bad
input, 3 still waiting when the watch ended (the worker is not running: python warehouse/analysis/findings/worker.py
--status).
"""

import argparse
import json
import os
import sys
import time
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
FINDINGS = os.path.join(ROOT, "warehouse", "analysis", "findings")
CARD_DIR = os.path.join(ROOT, "site", "data", "findings")
PROOF = {"queue_divorce": {"first_year": "2010"}}    # the request asked when no --param is given: never the default card


def env(name):
    v = os.environ.get(name)
    if not v:
        try:
            from dotenv import dotenv_values
            v = dotenv_values(os.path.join(ROOT, ".env")).get(name)
        except ImportError:
            v = None
    return (v or "").strip()


def rpc_url(fn):
    """<origin>/rest/v1/rpc/<fn>: SUPABASE_URL already ends in /rest/v1/, and only its origin is used, as the site does."""
    u = urllib.parse.urlparse(env("SUPABASE_URL"))
    if not u.scheme or not u.netloc:
        raise SystemExit("SUPABASE_URL is not set (.env or the environment)")
    return f"{u.scheme}://{u.netloc}/rest/v1/rpc/{fn}"


def catalogue_defaults(finding):
    """The finding's inputs with their defaults, from the engine's own catalogue (no table is read)."""
    sys.path.insert(0, FINDINGS)
    import run_finding
    for c in run_finding.catalogue():
        if c["id"] == finding:
            return {k: v for k, v in c["inputs"].items()}
    raise ValueError(f"no finding named {finding!r}; the findings are {', '.join(run_finding.FINDINGS)}")


def build_params(finding, given):
    inputs = catalogue_defaults(finding)
    params = {}
    for k, spec in inputs.items():
        v = str(given.get(k, spec["default"]))
        if spec["choices"] and v not in [str(c) for c in spec["choices"]]:
            raise ValueError(f"{spec['label']}: {v!r} is not one of {spec['choices']}")
        params[k] = v
    for k in given:
        if k not in inputs:
            raise ValueError(f"{finding} has no input named {k!r}; its inputs are {', '.join(inputs)}")
    return params


def call(fn, args, post=None):
    import requests
    key, token = env("SUPABASE_ANON_KEY"), env("INTERNAL_COSTS_TOKEN")
    if not key or len(token) < 24:
        raise SystemExit("SUPABASE_ANON_KEY and INTERNAL_COSTS_TOKEN are needed (.env or the environment)")
    r = (post or requests.post)(rpc_url(fn), json={"p_token": token, **args},
                                headers={"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json"}, timeout=30)
    if r.status_code >= 400:
        raise RuntimeError(f"{fn}: HTTP {r.status_code} {r.text[:200]}")
    return r.json()


def watch(rid, seconds, out=print, sleep=time.sleep, post=None):
    """Read the queue as the page does until the row is done or failed. Returns the row (or None when it never showed)."""
    end = time.time() + seconds
    row, last = None, None
    while True:
        rows = call("analysis_requests_list", {}, post) or []
        row = next((r for r in rows if r.get("id") == rid), None)
        state = row.get("status") if row else "not in the list"
        if state != last:
            out(f"  {time.strftime('%H:%M:%S', time.gmtime())} UTC: {state}")
            last = state
        if row and state in ("done", "failed"):
            return row
        if time.time() >= end:
            return row
        sleep(10)


def main(argv=None, out=print, post=None):
    ap = argparse.ArgumentParser(description="ERW: queue one request for the findings worker, as /analysis does (session 181)")
    ap.add_argument("--finding", default="queue_divorce", help="the finding's id (default queue_divorce: one small table, seconds)")
    ap.add_argument("--param", action="append", default=[], help="k=v, one per input; an input left out takes its default (with none given, queue_divorce is asked from 2010)")
    ap.add_argument("--dry-run", action="store_true", help="print the call and send nothing")
    ap.add_argument("--watch", type=int, default=0, metavar="SECONDS", help="after queueing, wait this long for the worker and print the row's state")
    a = ap.parse_args(argv)
    given = dict(PROOF.get(a.finding, {})) if not a.param else {}
    for kv in a.param:
        k, _, v = kv.partition("=")
        given[k] = v
    try:
        params = build_params(a.finding, given)
    except ValueError as exc:
        out(f"not queued: {exc}")
        return 2
    args = {"p_kind": "run", "p_finding": a.finding, "p_params": json.dumps(params)}
    if a.dry_run:
        out("DRY RUN: nothing is sent. The call would be:")
        out(f"  POST {rpc_url('analysis_request')}")
        out("  headers: apikey and Authorization (SUPABASE_ANON_KEY, not printed), Content-Type application/json")
        out(f"  body: {json.dumps({'p_token': '(INTERNAL_COSTS_TOKEN, not printed)', **args})}")
        return 0
    try:
        r = call("analysis_request", args, post)
    except RuntimeError as exc:
        out(f"not queued: {exc}")
        return 1
    if not (isinstance(r, dict) and r.get("ok")):
        reason = r.get("reason") if isinstance(r, dict) else r
        out(f"not queued: {'the 24 requests of this UTC day are used' if reason == 'day' else reason}")
        return 1
    rid = r["id"]
    out(f"queued: request {rid} ({a.finding} {params}) at {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())} UTC")
    if not a.watch:
        out("to see it complete: run this again with --watch 300, or open /analysis (the list under 'Ask for a finding')")
        return 0
    row = watch(rid, a.watch, out, post=post)
    if not row or row.get("status") not in ("done", "failed"):
        out(f"still {row.get('status') if row else 'not listed'} after {a.watch} seconds: the worker is not taking requests "
            "(python warehouse/analysis/findings/worker.py --status)")
        return 3
    out(f"{row['status']}: asked {row.get('asked_at')}, started {row.get('started_at')}, ended {row.get('done_at')}, by {row.get('machine') or '?'}")
    if row["status"] == "failed":
        out(f"reason: {row.get('note')}")
        return 1
    card = os.path.join(CARD_DIR, f"{row.get('card_id')}.json")
    out(f"card: {row.get('card_id')} ({card}: {'there' if os.path.exists(card) else 'not on this machine'})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
