# Expected: 2019 1492.0, 2025 1976.0, change 484.0 (hours); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 166): reproduce candidate calm_hours for pjm_calm_hours from the ERW's public table.

    python {this file} <grid_stress_yearly.csv>

The year's calm hours (wind and solar together far below their usual output, as docs/methods/grid_stress.md defines them), PJM.
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
    if r.get('calm_hours') == r.get('calm_hours'):
        print(y, round(float(r['calm_hours'] * 1.0), 6), 1)
