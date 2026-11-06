# Expected: 2019 19.33, 2025 34.355, change 15.025 (percent of solar capacity); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 166): reproduce candidate tight_solar for pjm_tight_solar from the ERW's public table.

    python {this file} <grid_stress_yearly.csv>

Solar's output in the year's tightest hours as a percent of its capacity, PJM.
"""
import sys

import pandas as pd

with open(sys.argv[1], encoding="utf-8") as f:
    skip = 0
    for line in f:
        if not line.startswith("#"):
            break
        skip += 1
d = pd.read_csv(sys.argv[1], skiprows=skip, usecols=["entity", "variable", "ts_utc", "value"], dtype=str)
d = d[d["entity"] == 'iso:pjm'].copy()
d["value"] = pd.to_numeric(d["value"], errors="coerce")
d = d.dropna(subset=["value"]).drop_duplicates(["entity", "variable", "ts_utc"])
d["year"] = d["ts_utc"].str[:4].astype(int)
w = d.pivot_table(index="year", columns="variable", values="value")
for y, r in w.iterrows():
    if r.get('tight_solar_share_of_capacity_pct') == r.get('tight_solar_share_of_capacity_pct'):
        print(y, round(float(r['tight_solar_share_of_capacity_pct'] * 1.0), 6), 1)
