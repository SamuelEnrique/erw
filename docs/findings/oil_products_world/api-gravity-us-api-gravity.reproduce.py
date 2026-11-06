# Expected: 1985 32.463333, 2025 33.753333, change 1.29 (degrees API); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 164): reproduce candidate api_gravity for us_api_gravity from the ERW's public table.

    python {this file} <eia_crude_quality_monthly.csv>

The weighted average API gravity of the crude oil US refineries ran, the year's mean of its months. Rule mean: the year's mean of the series' months.
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
d["value"] = pd.to_numeric(d["value"], errors="coerce")
d = d.dropna(subset=["value"]).drop_duplicates(["entity", "variable", "ts_utc"])
d["year"] = d["ts_utc"].str[:4].astype(int)
a = d[(d["entity"] == 'eia_crude_quality:MCRAPUS2') & (d["variable"] == 'api_gravity')]
for y, s in a.groupby('year'):
    print(y, round(float(s['value'].mean() * 1.0), 6), len(s))
