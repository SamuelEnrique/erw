# Expected: 2017 9324.666667, 2025 8933.416667, change -391.25 (thousand barrels a day); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 164): reproduce candidate supplied_gasoline for us_supplied_gasoline from the ERW's public table.

    python {this file} <eia_product_supplied_monthly.csv>

US product supplied of finished motor gasoline, the year's mean of its months. Rule mean: the year's mean of the series' months.
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
a = d[(d["entity"] == 'eia_product_supplied:MGFUPUS2') & (d["variable"] == 'product_supplied_per_day')]
for y, s in a.groupby('year'):
    print(y, round(float(s['value'].mean() * 1.0), 6), len(s))
