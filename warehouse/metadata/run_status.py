#!/usr/bin/env python3
"""Run history of the Energy Research Warehouse (ERW) connectors.

Session 5 rulings: append each run's per-ISO status to the tracked
warehouse/metadata/run_status.csv, and open a GitHub issue when a market has
failed three daily runs in a row.

    python warehouse/metadata/run_status.py record            # after the connectors
    python warehouse/metadata/run_status.py streaks --n 3     # markets failing N runs running

`record` reads the runs/status/<connector>.json files the connectors write
(one per connector, the latest run) and appends one row per table:
run_id, runner, connector, table, market, status, detail. It is idempotent:
a (run_id, connector, table, market) already recorded is not appended again.
Session 13: a connector that checks completeness per day records each day it
could not write as its own row, status "gap", market "<market> <day>"; gap rows
never count toward a failure streak (the table itself was written).

`streaks` prints one line per (connector, table) whose last N recorded runs
all failed, and writes them to runs/failure_streaks.txt for the workflow.
Session 48: a table in warehouse/metadata/known_gaps.csv (a failure a human has
accepted, with its reason) is printed as known but not written to the file, so
the workflow opens no issue for it.
"""

import argparse
import glob
import json
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
CSV = os.path.join(HERE, "run_status.csv")
STATUS_DIR = os.path.join(ROOT, "runs", "status")
COLS = ["run_id", "runner", "connector", "table", "market", "status", "detail"]


def load(path=CSV):
    if os.path.exists(path):
        return pd.read_csv(path, dtype=str, keep_default_na=False)
    return pd.DataFrame(columns=COLS)


def record(status_dir=STATUS_DIR, path=CSV):
    hist = load(path)
    seen = set(zip(hist["run_id"], hist["connector"], hist["table"], hist["market"]))
    new = []
    for f in sorted(glob.glob(os.path.join(status_dir, "*.json"))):
        with open(f, encoding="utf-8") as fh:
            s = json.load(fh)
        for r in s["results"]:
            key = (s["run_id"], s["connector"], r["table"], r.get("market", ""))
            if key in seen:
                continue
            new.append({"run_id": s["run_id"], "runner": s.get("runner", ""),
                        "connector": s["connector"], "table": r["table"],
                        "market": r.get("market", ""), "status": r["status"],
                        "detail": str(r.get("detail", "")).replace("\n", " ")[:300]})
            seen.add(key)
    if new:
        out = pd.concat([hist, pd.DataFrame(new, columns=COLS)], ignore_index=True)
        out = out.sort_values(["run_id", "connector", "table"], kind="stable")
        tmp = path + ".tmp"
        out.to_csv(tmp, index=False, lineterminator="\n")
        os.replace(tmp, path)
    print(f"run_status: {len(new)} new rows, {len(hist) + len(new)} total")
    return len(new)


KNOWN_GAPS = os.path.join(ROOT, "warehouse", "metadata", "known_gaps.csv")


def known_gaps(path=KNOWN_GAPS):
    """{table: reason} of the failures a human has accepted (session 48)."""
    if not os.path.exists(path):
        return {}
    k = pd.read_csv(path, dtype=str, keep_default_na=False)
    return dict(zip(k["table"], k["reason"]))


def streaks(n=3, path=CSV, runner=None):
    """(connector, table) pairs whose last n recorded runs all failed."""
    hist = load(path)
    if runner:
        hist = hist[hist["runner"] == runner]
    out = []
    hist = hist[hist["status"] != "gap"]  # a gap day is not a failed run of the table
    for (conn, table), g in hist.groupby(["connector", "table"]):
        last = g.sort_values("run_id").tail(n)
        if len(last) == n and (last["status"] == "failed").all():
            out.append({"connector": conn, "table": table, "runs": ", ".join(last["run_id"]),
                        "detail": last["detail"].iloc[-1]})
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW run history")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("record")
    s = sub.add_parser("streaks")
    s.add_argument("--n", type=int, default=3)
    s.add_argument("--runner", help="only runs by this runner (github or local)")
    s.add_argument("--out", default=os.path.join(ROOT, "runs", "failure_streaks.txt"))
    args = ap.parse_args(argv)
    if args.cmd == "record":
        record()
        return 0
    all_found = streaks(args.n, runner=args.runner)
    gaps = known_gaps()  # session 48: accepted failures open no issue
    found = [f for f in all_found if f["table"] not in gaps]
    known = [f for f in all_found if f["table"] in gaps]
    lines = [f"{f['connector']} {f['table']}: failed the last {args.n} runs ({f['runs']}); "
             f"latest: {f['detail']}" for f in found]
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + ("\n" if lines else ""))
    print(f"markets failing {args.n} runs in a row: {len(found)}")
    for line in lines:
        print("  " + line)
    for f in known:
        print(f"  known gap, no issue: {f['connector']} {f['table']} (warehouse/metadata/known_gaps.csv)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
