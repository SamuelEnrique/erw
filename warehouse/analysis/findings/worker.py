#!/usr/bin/env python3
"""The findings worker (session 170): the data machine takes queued requests from /analysis and runs them.

Energy Research Warehouse (ERW).

    python warehouse/analysis/findings/worker.py --once            # one turn: take every queued request, run each, stop
    python warehouse/analysis/findings/worker.py --loop 60         # a turn every 60 seconds, until stopped
    python warehouse/analysis/findings/worker.py --local-dir DIR   # the queue as JSON files in DIR (tests, a machine
                                                                   # without the migration): DIR/<id>.json is a row

How a request waits: a row of public.analysis_requests (migration 027) with status queued and the time it was asked.
This machine is the data machine, the one that holds the full histories (ERW_DATA_DIR, else warehouse/output). When it
is off the row stays queued and /analysis says so with the time; when it wakes, this worker takes the oldest queued row,
marks it running with the machine's name, runs the finding (run_finding.run) against the histories here, and writes the
card into the row (status done, card_id, card) or the plain reason (status failed). It never touches the data lock:
a finding reads tables and writes no warehouse table. Supabase is reached with the service role (SUPABASE_URL and
SUPABASE_SERVICE_KEY from .env, as warehouse/lock.py reads them), which bypasses row level security.

Starting it on this machine: a PowerShell window, `C:\\Users\\lossa\\Documents\\erw\\.venv\\Scripts\\python.exe
warehouse\\analysis\\findings\\worker.py --loop 60`, or the Task Scheduler entry the session report gives (at log on,
restart on failure). It stops cleanly on Ctrl-C.
"""

import argparse
import datetime as dt
import json
import os
import socket
import sys
import time
import traceback
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "warehouse"))
import common  # noqa: E402
import run_finding  # noqa: E402

TABLE = "analysis_requests"


def now():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def log(msg):
    print(f"{now()[11:19]} {msg}", flush=True)


class Supabase:
    """The queue as rows of the request table, read and written with the service role."""

    def __init__(self):
        import lock
        import requests
        self.requests = requests
        url, key = lock.env("SUPABASE_URL"), lock.env("SUPABASE_SERVICE_KEY")
        if not url or not key:
            raise SystemExit("the worker needs SUPABASE_URL and SUPABASE_SERVICE_KEY (.env or the environment)")
        u = urllib.parse.urlparse(url)
        self.base = f"{u.scheme}://{u.netloc}/rest/v1/{TABLE}"
        self.h = {"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json"}

    def queued(self):
        r = self.requests.get(self.base, params={"kind": "eq.run", "status": "eq.queued", "order": "asked_at.asc", "limit": "20"},
                              headers=self.h, timeout=30)
        r.raise_for_status()
        return r.json()

    def update(self, rid, fields):
        r = self.requests.patch(self.base, params={"id": f"eq.{rid}"}, json=fields, headers={**self.h, "Prefer": "return=minimal"}, timeout=60)
        r.raise_for_status()


class LocalDir:
    """The queue as JSON files (one row each) in a folder: the tests, and a machine without the migration."""

    def __init__(self, d):
        self.d = d
        os.makedirs(d, exist_ok=True)

    def rows(self):
        out = []
        for f in sorted(os.listdir(self.d)):
            if f.endswith(".json"):
                with open(os.path.join(self.d, f), encoding="utf-8") as fh:
                    out.append(json.load(fh))
        return out

    def queued(self):
        return sorted([r for r in self.rows() if r.get("kind", "run") == "run" and r.get("status") == "queued"], key=lambda r: r.get("asked_at", ""))

    def update(self, rid, fields):
        p = os.path.join(self.d, rid + ".json")
        with open(p, encoding="utf-8") as fh:
            row = json.load(fh)
        row.update(fields)
        with open(p, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(row, fh, indent=1, default=common.round6)


def run_one(q, row, machine, in_dir, card_dir, download_dir):
    rid = row["id"]
    params = row.get("params") or {}
    if isinstance(params, str):
        params = json.loads(params or "{}")
    log(f"request {rid}: {row['finding']} {params} (asked {row.get('asked_at', '?')})")
    q.update(rid, {"status": "running", "started_at": now(), "machine": machine})
    try:
        path, card = run_finding.run(row["finding"], params, in_dir, card_dir, download_dir, log=lambda m: log("  " + m))
        q.update(rid, {"status": "done", "done_at": now(), "card_id": card["card_id"], "card": json.loads(json.dumps(card, default=common.round6)), "note": ""})
        log(f"  done: {card['card_id']}")
        return "done"
    except common.NoData as exc:
        q.update(rid, {"status": "failed", "done_at": now(), "note": f"a table is not on the data machine: {str(exc)[:200]}"})
        log(f"  failed (no data): {exc}")
    except ValueError as exc:
        q.update(rid, {"status": "failed", "done_at": now(), "note": str(exc)[:200]})
        log(f"  failed (input): {exc}")
    except Exception as exc:
        q.update(rid, {"status": "failed", "done_at": now(), "note": f"{type(exc).__name__}: {str(exc)[:160]}"})
        log(f"  FAILED: {traceback.format_exc()}")
    return "failed"


def turn(q, machine, in_dir, card_dir, download_dir):
    rows = q.queued()
    if not rows:
        return 0
    for row in rows:
        run_one(q, row, machine, in_dir, card_dir, download_dir)
    return len(rows)


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW findings worker (session 170)")
    ap.add_argument("--once", action="store_true", help="one turn, then stop")
    ap.add_argument("--loop", type=int, default=0, metavar="SECONDS", help="a turn every SECONDS until stopped")
    ap.add_argument("--local-dir", help="the queue as JSON files in this folder instead of Supabase")
    ap.add_argument("--in-dir", default=common.DEFAULT_IN_DIR, help="the warehouse's output directory")
    ap.add_argument("--card-dir", help="where cards are written (default site/data/findings)")
    ap.add_argument("--download-dir", help="where downloads are written (default site/public/findings)")
    ap.add_argument("--machine", default=socket.gethostname())
    a = ap.parse_args(argv)
    if not a.once and not a.loop:
        ap.error("--once or --loop SECONDS")
    q = LocalDir(a.local_dir) if a.local_dir else Supabase()
    log(f"findings worker on {a.machine}, tables in {a.in_dir}, queue {'files in ' + a.local_dir if a.local_dir else 'Supabase ' + TABLE}")
    while True:
        try:
            n = turn(q, a.machine, a.in_dir, a.card_dir, a.download_dir)
            if n:
                log(f"turn: {n} request(s)")
        except KeyboardInterrupt:
            log("stopped")
            return 0
        except Exception as exc:
            log(f"turn failed: {type(exc).__name__}: {str(exc)[:200]}")
        if a.once:
            return 0
        try:
            time.sleep(a.loop)
        except KeyboardInterrupt:
            log("stopped")
            return 0


if __name__ == "__main__":
    sys.exit(main())
