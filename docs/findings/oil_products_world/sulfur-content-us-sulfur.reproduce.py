# Expected: 1985 0.911667, 2025 1.299167, change 0.3875 (percent sulfur by weight); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 164): reproduce candidate sulfur_content for us_sulfur from the ERW's public table.

    python {this file} <eia_crude_quality_monthly.csv>

The weighted average sulfur content of the crude oil US refineries ran, the year's mean of its months. Rule mean: the year's mean of the series' months.
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
a = d[(d["entity"] == 'eia_crude_quality:MCRS1US2') & (d["variable"] == 'sulfur_content')]
for y, s in a.groupby('year'):
    print(y, round(float(s['value'].mean() * 1.0), 6), len(s))
