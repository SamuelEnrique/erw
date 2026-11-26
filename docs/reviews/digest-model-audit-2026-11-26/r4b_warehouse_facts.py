"""Session 10235: the two warehouse-kind fun facts re-done from the main checkout's tables.

13 October: the lowest daily Henry Hub close in eia_fuel_spot_prices, the series' first day, the close of 2026-10-06 and
their ratio. 21 October: CAISO's largest month of curtailed wind and solar in iso_curtailment_monthly and the months held.

Run: python r4b_warehouse_facts.py <output dir> > r4b_warehouse_facts.out
"""
import csv
import os
import sys
from collections import defaultdict

OUT = sys.argv[1]


def rows(name):
    with open(os.path.join(OUT, name + ".csv"), encoding="utf-8", newline="") as f:
        yield from csv.DictReader(ln for ln in f if not ln.startswith("#"))


hh = sorted((r["ts_utc"][:10], float(r["value"])) for r in rows("eia_fuel_spot_prices") if r["entity"] == "eia:henry_hub")
lo = min(hh, key=lambda x: (x[1], x[0]))
latest = dict(hh).get("2026-10-06")
print(f"Henry Hub: {len(hh)} closes from {hh[0][0]} to {hh[-1][0]}; lowest {lo[1]:.2f} on {lo[0]}; "
      f"other days at that low: {[d for d, v in hh if v == lo[1]]}; close of 2026-10-06 {latest}; ratio {latest / lo[1]:.3f}")
print("five lowest:", sorted(hh, key=lambda x: x[1])[:5])
if os.path.exists(os.path.join(OUT, "iso_curtailment_monthly.csv")):
    by = defaultdict(float)
    vs = set()
    for r in rows("iso_curtailment_monthly"):
        if r["entity"].startswith("caiso:"):
            vs.add((r["entity"], r["variable"]))
            if r["entity"] == "caiso:ISO":
                by[(r["variable"], r["ts_utc"][:7])] += float(r["value"])
    print("caiso series:", sorted(vs)[:12])
    for var in sorted({k[0] for k in by}):
        months = sorted((m, v) for (vv, m), v in by.items() if vv == var)
        top = max(months, key=lambda x: x[1])
        print(f"  caiso:ISO {var}: {len(months)} months from {months[0][0]} to {months[-1][0]}; largest {top[1]:,.0f} in {top[0]}")
else:
    print("iso_curtailment_monthly.csv is not on this machine")
