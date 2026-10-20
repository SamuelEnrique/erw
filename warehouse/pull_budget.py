#!/usr/bin/env python3
"""The budget of one publisher pull in the daily run (session 321, the owner's ruling of 19 October 2026).

Energy Research Warehouse (ERW). The daily job was cancelled at GitHub's 180-minute limit on 14, 15 and 19 October 2026:
CAISO's OASIS and SPP's file server did not answer the runner, and each request waited for the operating system's own
connect timeout (about 2.4 minutes) four times a day, three days a run (39 minutes a market). Now every publisher pull of
warehouse/run_daily.sh runs under this wrapper:

    python warehouse/pull_budget.py --step caiso [--minutes 15] -- python warehouse/connectors/iso_prices.py caiso --days 3

1. The command runs with ERW_PULL_STEP (the step's name) and ERW_PULL_DEADLINE (epoch seconds: the start plus the budget,
   less a minute to write its status). A connector that imports warehouse/connectors/iso_prices.py has every request to
   a publisher cut to the time left (connect and read timeouts, retries included) and refused after the deadline, with
   the reason below; its failed tables are written as gap rows (iso_prices.write_status) and it leaves a mark in
   runs/budget/<step>.txt.
2. At the budget (wall clock, 15 minutes by default) the command and its children are stopped, whatever they import.
3. Then the step is settled. When the budget ran out (the mark, or the stop): every table its status files of this run
   name as failed becomes a gap row with the reason "publisher did not answer within the budget"; a stopped connector
   that wrote no status gets one gap row a table (the tables of its last recorded run, warehouse/metadata/run_status.csv);
   a line "<step> SKIPPED: <reason>" is printed, and the exit is 75, the skip exit warehouse/health.py and run_other read.
   A skip is not a failure for the health gate (session 305's rule) and the next run asks for the same days again.
   When the budget did not run out, the command's own exit is passed on unchanged.

Only the standard library: the wrapper runs before any connector imports anything.
"""

import argparse
import datetime as dt
import glob
import json
import os
import signal
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
STATUS_DIR = os.path.join(ROOT, "runs", "status")
MARK_DIR = os.path.join(ROOT, "runs", "budget")
RUN_STATUS = os.path.join(ROOT, "warehouse", "metadata", "run_status.csv")
SKIP = 75
MINUTES = 15
MARGIN = 60  # seconds the connector keeps after its deadline to write its tables' status
REASON = "publisher did not answer within the budget"


def reason(minutes):
    return f"{REASON} ({minutes:g} minutes of wall clock); asked again by the next run"


def mark_path(step):
    return os.path.join(MARK_DIR, f"{step}.txt")


def stop(p):
    """Stop the command and every process it started."""
    if os.name == "nt":
        subprocess.run(["taskkill", "/T", "/F", "/PID", str(p.pid)], capture_output=True)
    else:
        for sig in (signal.SIGTERM, signal.SIGKILL):
            try:
                os.killpg(p.pid, sig)
            except ProcessLookupError:
                break
            try:
                p.wait(timeout=30)
                break
            except subprocess.TimeoutExpired:
                continue
    try:
        p.wait(timeout=30)
    except subprocess.TimeoutExpired:
        pass


def last_tables(step, path=None):
    """The tables of this connector's last recorded run, or [step] when none is recorded."""
    import csv
    path = path or RUN_STATUS
    if not os.path.exists(path):
        return [step]
    rows = []
    with open(path, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            if r.get("connector") == step and r.get("status") != "gap":
                rows.append(r)
    if not rows:
        return [step]
    last = max(r["run_id"] for r in rows)
    return sorted({r["table"] for r in rows if r["run_id"] == last}) or [step]


def settle(step, rc, since, minutes, stopped, status_dir=None, run_status=None):
    """(exit code, line) once the command has ended. See the module's docstring."""
    status_dir, run_status = status_dir or STATUS_DIR, run_status or RUN_STATUS
    mark = mark_path(step)
    exhausted = stopped or os.path.exists(mark)
    if not exhausted:
        return rc, None
    why = reason(minutes)
    day = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")
    files = [p for p in glob.glob(os.path.join(status_dir, "*.json")) if os.path.getmtime(p) >= since - 1]
    for path in files:
        try:
            with open(path, encoding="utf-8") as f:
                doc = json.load(f)
        except (OSError, ValueError):
            continue
        changed = False
        for r in doc.get("results", []):
            if r.get("status") == "failed":
                r["status"] = "gap"
                r["market"] = f"{r.get('market') or 'all'} {day}"
                r["detail"] = f"{why}: {r.get('detail') or ''}"[:300]
                changed = True
        if changed:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(doc, f, indent=1)
    if stopped and not files:
        os.makedirs(status_dir, exist_ok=True)
        run_id = dt.datetime.fromtimestamp(since, dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        runner = "github" if os.environ.get("GITHUB_ACTIONS") == "true" else "local"
        doc = {"connector": step, "run_id": run_id, "runner": runner,
               "results": [{"table": t, "market": f"all {day}", "status": "gap",
                            "detail": f"{why}: stopped after {minutes:g} minutes, nothing written"}
                           for t in last_tables(step, run_status)]}
        with open(os.path.join(status_dir, f"{step}.json"), "w", encoding="utf-8") as f:
            json.dump(doc, f, indent=1)
    return SKIP, f"{step} SKIPPED: {why}"


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--" not in argv:
        print("usage: pull_budget.py --step NAME [--minutes 15] -- command ...", file=sys.stderr)
        return 2
    cut = argv.index("--")
    ap = argparse.ArgumentParser(description="the budget of one publisher pull (session 321)")
    ap.add_argument("--step", required=True)
    ap.add_argument("--minutes", type=float, default=float(os.environ.get("PULL_BUDGET_MIN") or MINUTES))
    args = ap.parse_args(argv[:cut])
    cmd = argv[cut + 1:]
    if not cmd:
        ap.error("no command after --")
    budget = args.minutes * 60
    since = time.time()
    try:
        os.remove(mark_path(args.step))
    except OSError:
        pass
    env = {**os.environ, "ERW_PULL_STEP": args.step,
           "ERW_PULL_DEADLINE": f"{since + max(budget - MARGIN, budget / 2):.0f}"}
    sys.stdout.flush()
    p = subprocess.Popen(cmd, env=env, cwd=ROOT, **({} if os.name == "nt" else {"start_new_session": True}))
    stopped = False
    try:
        rc = p.wait(timeout=budget)
    except subprocess.TimeoutExpired:
        stopped = True
        print(f"{args.step}: stopped at the budget of {args.minutes:g} minutes", flush=True)
        stop(p)
        rc = p.returncode if p.returncode is not None else 124
    code, line = settle(args.step, rc, since, args.minutes, stopped)
    if line:
        print(line, flush=True)
    return code


if __name__ == "__main__":
    sys.exit(main())
