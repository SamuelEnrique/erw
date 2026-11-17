#!/usr/bin/env python3
"""ERW, ruling impact for /storage (session 7590, 17 November 2026).

The one line marked "Changes a figure" under /storage in docs/reviews/rulings-for-samuel-2026-11-17.md (branch
wip/7560-six-reads): give the daily cycle a month's total discharge by grid beside the newest day and the 30-day spark.
Table: storage_daily_cycle (warehouse/output, this machine's copy of 9 October 2026), public grids only (CAISO's own
data, EIA-930 for ERCOT and SPP); the rows of ISO-NE and MISO are not printed.

    .venv/Scripts/python.exe runs/ruling_impact/storage_impact.py
"""
import calendar
import csv
import os
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
KEEP = {"caiso:ISO": "CAISO (its own data)", "eia930:ERCO": "ERCOT (EIA-930)", "eia930:SWPP": "SPP (EIA-930)"}
d = defaultdict(dict)
with open(os.path.join(ROOT, "warehouse", "output", "storage_daily_cycle.csv"), encoding="utf-8", newline="") as f:
    for r in csv.DictReader(l for l in f if not l.startswith("#")):
        if r["entity"] in KEEP and r["variable"] in ("mwh_discharged", "mwh_charged") and r["value"]:
            d[(r["entity"], r["variable"])][r["ts_utc"][:10]] = float(r["value"])
for e, name in KEEP.items():
    dis = d[(e, "mwh_discharged")]
    newest = max(dis)
    last30 = sorted(dis)[-30:]
    print(f"{name}: newest day {newest}, discharged {dis[newest]:,.0f} MWh; the 30 days to it {sum(dis[x] for x in last30):,.0f} MWh")
    for m in ("2026-08", "2026-09", "2026-10"):
        days = [x for x in dis if x.startswith(m)]
        n = calendar.monthrange(int(m[:4]), int(m[5:]))[1]
        if days:
            tot = sum(dis[x] for x in days)
            print(f"   {m}: {tot:,.0f} MWh discharged over {len(days)} of {n} days ({tot / len(days):,.0f} a day){'' if len(days) == n else ', a partial month'}")
print("the site's table runs past this machine's copy (9 October), so October 2026 whole, the line's example, is not computed here")
