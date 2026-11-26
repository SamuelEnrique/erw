"""Session 10214 (demand audit): stream EIA-930's per-area workbooks of 3 October 2026 (the main copy's raw folder, read
only) and write, for each area, the hour's start (UTC), EIA's "Demand" and EIA's "Adjusted demand" to a small CSV under
runs/c10214/hours/. No table is read whole: openpyxl's read-only mode yields one row at a time. Nothing else is done
here; restate.py reads these files one local year at a time.

Usage: python runs/c10214/extract.py <raw run folder> <out folder>
"""
import csv
import glob
import os
import sys
from datetime import timedelta

import openpyxl

AREAS = ["ERCO", "CISO", "PJM", "MISO", "SWPP", "NYIS", "ISNE", "US48"]


def main(raw, out):
    os.makedirs(out, exist_ok=True)
    for ba in AREAS:
        pat = "*_Region_US48.xlsx" if ba == "US48" else f"*_{ba}.xlsx"
        files = [f for f in glob.glob(os.path.join(raw, pat)) if os.path.getsize(f) > 0]
        path = max(files)
        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
        ws = wb["Published Hourly Data"]
        rows = ws.iter_rows(values_only=True)
        head = list(next(rows))
        t = head.index("UTC time")
        dcol = head.index("Demand")
        acol = head.index("Adjusted demand") if "Adjusted demand" in head else None
        n = 0
        with open(os.path.join(out, f"{ba}.csv"), "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["ts_start_utc", "demand", "adjusted_demand"])
            for r in rows:
                ts = r[t]
                if ts is None or ts.year < 2018:
                    continue
                d = r[dcol] if isinstance(r[dcol], (int, float)) else ""
                a = (r[acol] if isinstance(r[acol], (int, float)) else "") if acol is not None else ""
                w.writerow([(ts - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ"), d, a])
                n += 1
        wb.close()
        print(f"{ba}: {n} rows from {os.path.basename(path)}; columns {head}", flush=True)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
