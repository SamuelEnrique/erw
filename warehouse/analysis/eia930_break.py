#!/usr/bin/env python3
"""EIA-930 by fuel, by day, from the saved per-balancing-authority workbooks (session 73).

Energy Research Warehouse (ERW). docs/methods/eia930_caiso_break.md.

    python warehouse/analysis/eia930_break.py [--run 20260929T181949Z] [--out runs/session73]

Session 68 found that EIA-930's net generation for CAISO fell by about 80 GWh a day from December 2025 while demand and
interchange did not. This reads the workbooks the emissions connector saved (warehouse/raw/eia930_emissions/<run>/,
EIA's "Published Hourly Data" sheet of https://www.eia.gov/electricity/gridmonitor/knownissues/xls/<BA>.xlsx): no
request is made. For each of the seven ISO balancing authorities it writes one row per UTC day (an hour is dated by its
start: EIA's "UTC time" column is the hour's end): demand, net generation
and total interchange as EIA reports them and as EIA adjusts them, and net generation by fuel (EIA's NG: columns, as
reported, and the adjusted ones), each the day's sum of hourly MWh, with the number of hours that held a value. A day's
sum is over the hours EIA gave; nothing is filled. Output: <out>/<ba>_daily.csv, an analysis file, not a warehouse table.
"""

import argparse
import csv
import glob
import os
import sys
from datetime import timedelta
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
HOUR = timedelta(hours=1)
RAW = os.path.join(ROOT, "warehouse", "raw", "eia930_emissions")
BAS = ["CISO", "ERCO", "ISNE", "MISO", "NYIS", "PJM", "SWPP"]
FUELS = ["COL", "NG", "NUC", "OIL", "GEO", "WAT", "PS", "SUN", "SNB", "WND", "WNB", "BAT", "OES", "UES", "OTH", "UNK"]
TOTALS = ["Demand", "Net generation", "Total interchange", "Adjusted demand", "Adjusted net generation", "Adjusted total interchange"]
COLUMNS = TOTALS + [f"NG: {f}" for f in FUELS] + [f"Adjusted {f} Gen" for f in FUELS]


def name(col):
    """A workbook column as a CSV column name: demand, net_generation, adj_net_generation, ng_sun, adj_sun ..."""
    if col.startswith("NG: "):
        return "ng_" + col[4:].lower()
    if col.startswith("Adjusted ") and col.endswith(" Gen"):
        return "adj_" + col[9:-4].lower()
    return col.lower().replace("adjusted ", "adj_").replace(" ", "_")


def workbook(run, ba):
    """One BA's workbook: from the named run if it holds a non-empty one, else the newest non-empty one of any saved run
    (the connector saves each BA under the run that downloaded it; a run may hold an empty first attempt)."""
    files = [f for f in glob.glob(os.path.join(RAW, run, f"*_{ba}.xlsx")) if os.path.getsize(f) > 0]
    if not files:
        files = [f for f in glob.glob(os.path.join(RAW, "*", f"*_{ba}.xlsx")) if os.path.getsize(f) > 0]
    if not files:
        raise FileNotFoundError(f"no {ba} workbook under {RAW}")
    return max(files, key=lambda f: (os.path.basename(os.path.dirname(f)), os.path.basename(f)))


def daily(args):
    run, ba, out = args
    import openpyxl
    path = workbook(run, ba)
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    ws = wb["Published Hourly Data"]
    rows = ws.iter_rows(values_only=True)
    head = list(next(rows))
    idx = {c: head.index(c) for c in COLUMNS if c in head}
    t = head.index("UTC time")
    sums = defaultdict(lambda: defaultdict(float))
    hours = defaultdict(lambda: defaultdict(int))
    for r in rows:
        ts = r[t]
        if ts is None:
            continue
        d = (ts - HOUR).strftime("%Y-%m-%d")  # EIA's "UTC time" is the hour's end; the ERW dates an hour by its start
        hours[d]["_rows"] += 1
        for c, k in idx.items():
            v = r[k]
            if isinstance(v, (int, float)):
                sums[d][c] += v
                hours[d][c] += 1
    cols = [c for c in COLUMNS if c in idx]
    os.makedirs(out, exist_ok=True)
    dest = os.path.join(out, f"{ba.lower()}_daily.csv")
    with open(dest, "w", encoding="utf-8", newline="") as f:
        f.write(f"# EIA-930 daily sums (UTC days) of hourly MWh for {ba}, from {os.path.relpath(path, ROOT)}, sheet Published Hourly Data; "
                f"each value column has an hours_<column> count of the hours that held a value; nothing filled (warehouse/analysis/eia930_break.py)\n")
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["day", "hours"] + [name(c) for c in cols] + [f"hours_{name(c)}" for c in cols])
        for d in sorted(sums):
            w.writerow([d, hours[d]["_rows"]] + [round(sums[d][c], 1) if hours[d][c] else "" for c in cols] + [hours[d][c] for c in cols])
    return ba, dest, len(sums)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--run", default="20260929T181949Z", help="the saved workbook run under warehouse/raw/eia930_emissions/")
    ap.add_argument("--out", default=os.path.join(ROOT, "runs", "session73"))
    ap.add_argument("--bas", default=",".join(BAS))
    a = ap.parse_args(argv)
    jobs = [(a.run, ba, a.out) for ba in a.bas.split(",")]
    failed = 0
    with ProcessPoolExecutor(max_workers=min(7, len(jobs))) as ex:
        for fut, job in zip([ex.submit(daily, j) for j in jobs], jobs):
            try:
                ba, dest, n = fut.result()
                print(f"{ba}: {n} days -> {os.path.relpath(dest, ROOT)}")
            except Exception as exc:
                failed += 1
                print(f"FAILED {job[1]}: {type(exc).__name__}: {exc}", file=sys.stderr)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
