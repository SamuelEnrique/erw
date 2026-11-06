# Expected: 2014 1.797, 2025 49.737, change 47.94 (USD billion); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 164): reproduce candidate dc_construction for us_dc_build from the ERW's public table.

    python {this file} <census_c30_construction_monthly.csv>

The value of private data center construction put in place over the year.
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
d = d.dropna(subset=["value"])
d["year"] = d["ts_utc"].str[:4].astype(int)
d = d[(d['entity'] == 'census_c30:private:data_center') & (d['variable'] == 'value_put_in_place')]
for y, s in d.groupby('year'):
    print(y, round(float(s['value'].sum() / 1e9), 6), len(s))
