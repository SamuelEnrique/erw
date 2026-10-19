#!/usr/bin/env python3
"""A table's stores after a step of the data machine's run rewrote it (session 204).

Energy Research Warehouse (ERW). warehouse/run_data_machine.sh gives the load zone table its stores in the script
itself (session 149). Session 204 added two more tables to that run (ercot_rtm_node_prices, merchant_revenue_monthly);
this is the same sequence for any table named, once, so the script does not hold it three times:

    python warehouse/table_stores.py ercot_rtm_node_prices
    python warehouse/table_stores.py merchant_revenue_monthly --dry-run     # print the four commands; run nothing

For each table, in this order, each command started by itself and its own exit code read (never piped):

    1. the validator        warehouse/validate/erw_validate.py warehouse/output/<table>.csv      a gate
    2. the coverage row     warehouse/metadata/build_coverage.py --only ^<table>$                a gate
    3. the archive          warehouse/archive/archive.py write --tables ^<table>$
    4. the Redivis draft    warehouse/redivis/upload.py --tables <table>                         a draft; nothing is released

A gate that fails stops that table there: a table the validator blocks reaches no store, and one whose coverage row
could not be built is not archived or uploaded (the loader and the sync read coverage). The archive and the draft are
both tried; either failing is this script's failure. Each command's output is kept in runs/stores_<table>_<step>.out.
Exit 0 when every table reached all four; 1 when any did not; 2 when a table named is not in warehouse/output.

It writes metadata (coverage.csv, docs/coverage.md, the archive manifest, the Redivis record) and the two stores, so
it runs under the data lock, as the run that calls it does. It loads nothing into the live set and asks no publisher
for anything.
"""

import argparse
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
OUT_DIR = os.path.join(ROOT, "warehouse", "output")
RUNS = os.path.join(ROOT, "runs")
NAME = re.compile(r"^[a-z0-9_]+$")


def commands(table):
    """(step, gate, command) for one table, in order."""
    only = f"^{table}$"
    return [
        ("validate", True, ["warehouse/validate/erw_validate.py", f"warehouse/output/{table}.csv"]),
        ("coverage", True, ["warehouse/metadata/build_coverage.py", "--only", only]),
        ("archive", False, ["warehouse/archive/archive.py", "write", "--tables", only]),
        ("redivis", False, ["warehouse/redivis/upload.py", "--tables", table]),
    ]


SKIP = int(os.environ.get("ERW_SKIP_EXIT") or 75)
CAP_SKIPPED = set()  # session 305: the tables whose Redivis step was skipped for Redivis's export cap


def stores(table, dry=False, run=subprocess.run, log=print, runs=None):
    """True when the table reached all four (session 305: or the archive, with Redivis skipped for its export cap)."""
    ok = True
    for step, gate, cmd in commands(table):
        if dry:
            log(f"{table} {step}: {' '.join(cmd)}")
            continue
        out = os.path.join(runs or RUNS, f"stores_{table}_{step}.out")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            rc = run([sys.executable, os.path.join(ROOT, cmd[0])] + cmd[1:], cwd=ROOT, stdout=f, stderr=subprocess.STDOUT).returncode
        log(f"{table} {step} exit={rc} ({os.path.relpath(out, ROOT).replace(os.sep, '/')})")
        if step == "redivis" and rc == SKIP:
            # session 305: upload.py exits with the skip exit when Redivis's export cap stopped the upload; the table
            # is in the archive (the step before) and waits there, so this is a skip, not a failure
            CAP_SKIPPED.add(table)
            log(f"{table} redivis skipped: Redivis export cap; the table waits in the archive")
            continue
        if rc != 0:
            ok = False
            if gate:
                log(f"{table} FAILED: {step} exited {rc}, a gate; the steps after it were not run for this table")
                break
            log(f"{table} FAILED: {step} exited {rc}")
    return ok


def main(argv=None):
    ap = argparse.ArgumentParser(description="A table's stores: the validator, its coverage row, the archive and the Redivis draft (session 204)")
    ap.add_argument("tables", nargs="+")
    ap.add_argument("--dry-run", action="store_true", help="print the commands; run nothing")
    a = ap.parse_args(argv)
    for t in a.tables:
        if not NAME.match(t):
            ap.error(f"not a table name: {t}")
        if not a.dry_run and not os.path.exists(os.path.join(OUT_DIR, t + ".csv")):
            print(f"{t} FAILED: warehouse/output/{t}.csv is not on this machine; nothing was run")
            return 2
    done = [stores(t, a.dry_run) for t in a.tables]
    if not all(done):
        return 1
    if CAP_SKIPPED:  # the skip's reason is the last line (warehouse/health.py)
        print(f"stores SKIPPED: Redivis export cap: {', '.join(sorted(CAP_SKIPPED))} archived, not uploaded; they wait in the archive")
        return SKIP
    return 0


if __name__ == "__main__":
    sys.exit(main())
