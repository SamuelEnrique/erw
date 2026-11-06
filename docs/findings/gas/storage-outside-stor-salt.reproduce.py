# Expected: 2015 67.307692, 2025 13.461538, change -53.846154 (percent of weeks); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 164): reproduce candidate storage_outside for stor_salt from the ERW's public table.

    python {this file} <gas_balance_weekly.csv>

The percent of the year's weeks on which a region's working gas lay outside its five-year minimum to maximum, the South Central salt storage region.
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
d = d[(d["entity"] == 'gas_storage:salt') & d["variable"].isin(["working_gas_bcf", "five_year_min_bcf", "five_year_max_bcf"])].copy()
d["value"] = pd.to_numeric(d["value"], errors="coerce")
w = d.pivot_table(index="ts_utc", columns="variable", values="value").dropna()
w["out"] = (w["working_gas_bcf"] < w["five_year_min_bcf"]) | (w["working_gas_bcf"] > w["five_year_max_bcf"])
for y, s in w.groupby(w.index.str[:4].astype(int)):
    print(y, round(float(100 * s["out"].mean()), 6), len(s))
