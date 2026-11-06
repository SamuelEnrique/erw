# Expected: 2012 2097.0, 2023 2698.0, change 601.0 (establishments); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 164): reproduce candidate hosting_sites for est518_CA from the ERW's public table.

    python {this file} <census_cbp_hosting_annual.csv>

The number of NAICS 518210 establishments.
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
d = d[d['entity'] == 'census_cbp_518210:ca']
d = d[d['variable'] == 'establishments']
for y, s in d.groupby('year'):
    print(y, round(float(s['value'].sum()), 6), 1)
