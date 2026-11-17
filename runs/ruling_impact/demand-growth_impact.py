#!/usr/bin/env python3
"""ERW, ruling impact for /explore/demand-growth (session 7577, 17 November 2026).

The three lines marked "Changes a figure" under the demand growth explorer in docs/reviews/rulings-for-samuel-2026-11-17.md
(branch wip/7560-six-reads). The table is eia930_demand_growth (public, EIA Form EIA-930), as replication/demand_growth/
table_rows.csv holds the rows the page reads; California's charging is replication/demand_growth/california_charging.py's
rule on california_rows.csv (run, its lines printed).

    .venv/Scripts/python.exe runs/ruling_impact/demand-growth_impact.py
"""
import csv
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REP = os.path.join(ROOT, "replication", "demand_growth")
GRIDS = [("ERCO", "ERCOT"), ("CISO", "CAISO"), ("PJM", "PJM"), ("MISO", "MISO"), ("SWPP", "SPP"), ("NYIS", "NYISO"), ("ISNE", "ISO-NE"), ("US48", "Lower 48")]
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

T = {}
with open(os.path.join(REP, "table_rows.csv"), encoding="utf-8", newline="") as f:
    for r in csv.DictReader(l for l in f if not l.startswith("#")):
        T[(r["entity"].split(":")[1], r["variable"], r["ts_utc"][:4])] = float(r["value"])
years = sorted({k[2] for k in T})
last_whole = "2025"
newest = years[-1]
print(f"eia930_demand_growth rows as the page reads them (table_rows.csv, 16 November 2026): years {years[0]} to {newest}; last whole year {last_whole}")

# ---- line 1: California, demand less the batteries' charging
print("\n== line 1: California's growth with the batteries' charging (the table's row) and without (a second row)")
out = subprocess.run([sys.executable, os.path.join(REP, "california_charging.py")], capture_output=True, text=True)
print(out.stdout.strip())
g = T.get(("CISO", "avg_demand_growth_since_2019_pct", last_whole))
print(f"the page's headline for CAISO ({last_whole} on 2019, the whole year): {g:+.2f} percent. A second row for the whole year needs the charging of January to May 2025, "
      "which CAISO's own data on this machine does not hold (iso:caiso_own starts in June 2025): the whole-year figure without the charging is not computed")

# ---- line 2: a growth for the newest year's months
print(f"\n== line 2: a month's window: growth read at {last_whole} (default) or written for {newest}'s months")
for code, name in GRIDS:
    parts = []
    for m in range(1, 13):
        v = f"avg_demand_mw_m{m:02d}"
        b, a, n = T.get((code, v, "2019")), T.get((code, v, last_whole)), T.get((code, v, newest))
        if b is None or a is None or n is None:
            continue
        ga, gn = (a / b - 1) * 100, (n / b - 1) * 100
        parts.append(f"{MONTHS[m - 1][:3]} {ga:+.2f} -> {gn:+.2f} ({gn - ga:+.2f} points)")
    print(f"{name}: " + "; ".join(parts))

# ---- line 3: a site's own MW against a grid's growth
print(f"\n== line 3: a site's MW as a share of the grid's growth since 2019 (average demand, {last_whole} less 2019)")
for code, name in GRIDS:
    a, b = T.get((code, "avg_demand_mw", last_whole)), T.get((code, "avg_demand_mw", "2019"))
    grow = a - b
    print(f"{name}: average demand {b:,.0f} MW in 2019, {a:,.0f} in {last_whole}, growth {grow:+,.0f} MW; a 300 MW site is "
          + (f"{300 / grow * 100:.2f} percent of it" if grow > 0 else "not a share (the grid's demand fell)")
          + f"; 1,000 MW {1000 / grow * 100:.2f} percent" * (grow > 0))
