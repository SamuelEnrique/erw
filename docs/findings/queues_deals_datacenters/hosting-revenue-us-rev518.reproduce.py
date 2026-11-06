# Expected: 2004 55.394, 2024 374.936, change 319.542 (USD billion); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 164): reproduce candidate hosting_revenue for us_rev518 from the ERW's public table.

    python {this file} <census_qss_utilities_hosting_quarterly.csv>

The revenue of NAICS 518 over the year, the Quarterly Services Survey.
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
d = d[(d['entity'] == 'census_qss:518') & (d['variable'] == 'total_revenue')]
for y, s in d.groupby('year'):
    print(y, round(float(s['value'].sum() / 1e9), 6), len(s))
