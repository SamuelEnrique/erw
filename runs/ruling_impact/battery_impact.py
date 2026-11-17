#!/usr/bin/env python3
"""ERW, ruling impact for /cost-of-power/battery (session 7599, 17 November 2026).

The two lines marked "Changes a figure" under the battery tool in docs/reviews/rulings-for-samuel-2026-11-17.md (branch
wip/7560-six-reads). Line 1: the page's twelve months stay October 2025 to September 2026 (test 178 holds the note to
fixed months), or follow the data. The year's revenue per kW is the sum of the twelve months' revenue per MW over 1,000,
from battery_stack_monthly (warehouse/output, retrieved 21 October 2026), for each hub, duration and strategy the page
offers. Line 2 counts the fold's cells.

    .venv/Scripts/python.exe runs/ruling_impact/battery_impact.py
"""
import csv
import os
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
V = defaultdict(dict)
with open(os.path.join(ROOT, "warehouse", "output", "battery_stack_monthly.csv"), encoding="utf-8", newline="") as f:
    for r in csv.DictReader(l for l in f if not l.startswith("#")):
        if r["value"]:
            V[(r["entity"], r["variable"])][r["ts_utc"][:7]] = float(r["value"])


def months(a, b):
    y, m = int(a[:4]), int(a[5:])
    out = []
    while f"{y}-{m:02d}" <= b:
        out.append(f"{y}-{m:02d}")
        y, m = (y, m + 1) if m < 12 else (y + 1, 1)
    return out


A, B = months("2025-10", "2026-09"), months("2025-11", "2026-10")
print("== line 1: the battery page's year, October 2025 to September 2026 (default) or the twelve months to the newest (November 2025 to October 2026)")
for e in ("ercot:HB_HUBAVG", "caiso:TH_SP15_GEN-APND"):
    for strat in ("foresight", "dayahead"):
        for h in (2, 4, 8):
            v = V[(e, f"{strat}_{h}h_revenue_total_usd_per_mw")]
            dh = V[(e, f"{strat}_{h}h_days_held")]
            if all(m in v for m in A) and all(m in v for m in B):
                a, b = sum(v[m] for m in A) / 1000, sum(v[m] for m in B) / 1000
                print(f"{e} {strat} {h}h: {a:,.2f} -> {b:,.2f} USD per kW a year ({(b / a - 1) * 100:+.1f} percent); October 2026 holds {dh.get('2026-10', 0):.0f} days on this copy, "
                      f"October 2025 {v['2025-10'] / 1000:,.2f} against October 2026 {v['2026-10'] / 1000:,.2f} per kW")
print("October 2026 is partial on this copy (19 of 31 days), so the other choice's year is understated here; on the data machine's whole October the figure differs")

print("\n== line 2: the fold under the income table (each month: days held; the four-hour spread at the 10th percentile, median and 90th)")
print(f"the fold holds 4 figures for each of the 12 months: 48 cells; left out, they stay in the CSV; no other figure moves")
