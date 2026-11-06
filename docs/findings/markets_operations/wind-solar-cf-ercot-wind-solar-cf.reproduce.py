# Expected: 2019 32.588279, 2025 29.711655, change -2.876625 (percent of capacity); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 166): reproduce candidate wind_solar_cf for ercot_wind_solar_cf from the ERW's public table.

    python {this file} <grid_stress_yearly.csv>

Wind and solar's mean output over the year as a percent of their capacity, ERCOT.
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
d = d[d["entity"] == 'iso:ercot'].copy()
d["value"] = pd.to_numeric(d["value"], errors="coerce")
d = d.dropna(subset=["value"]).drop_duplicates(["entity", "variable", "ts_utc"])
d["year"] = d["ts_utc"].str[:4].astype(int)
w = d.pivot_table(index="year", columns="variable", values="value")
for y, r in w.iterrows():
    if r.get('wind_solar_capacity_mw', 0) and r.get('wind_solar_mean_mw') == r.get('wind_solar_mean_mw'):
        print(y, round(float(r['wind_solar_mean_mw'] * 100.0 / r['wind_solar_capacity_mw']), 6), 1)
