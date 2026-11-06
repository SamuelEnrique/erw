# Expected: 2013 38.633375, 2019 60.542903, change 21.909529 (percent of meters); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 164): reproduce candidate ami_share for ami_US from the ERW's public table.

    python {this file} <eia_meters_state_annual.csv>

Advanced metering infrastructure as a percent of all meters, the United States.
"""
import sys

import pandas as pd

with open(sys.argv[1], encoding="utf-8") as f:
    skip = 0
    for line in f:
        if not line.startswith("#"):
            break
        skip += 1
d = pd.read_csv(sys.argv[1], skiprows=skip, dtype=str)
d["value"] = pd.to_numeric(d["value"], errors="coerce")
d = d.dropna(subset=["value"])
d["year"] = d["ts_utc"].str[:4].astype(int)
d = d[d['entity'].isin(['eia_meters:US:advanced_meter_infrastructure:TOT', 'eia_meters:US:all_meters:TOT']) & (d['variable'] == 'meters')]
d['kind'] = d['entity'].str.split(':').str[2]
w = d.pivot_table(index='year', columns='kind', values='value').dropna()
w = w[w['all_meters'] > 0]
for y, r in w.iterrows():
    print(y, round(float(100 * r['advanced_meter_infrastructure'] / r['all_meters']), 6), 1)
