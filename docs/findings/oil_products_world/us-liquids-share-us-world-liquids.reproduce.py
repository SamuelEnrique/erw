# Expected: 1993 14.47344, 2025 22.322314, change 7.848874 (percent of world production); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 164): reproduce candidate us_liquids_share for us_world_liquids from the ERW's public table.

    python {this file} <eia_world_oil_monthly.csv>

US total petroleum and other liquids production as a percent of the world's, the months that hold both. Rule share: the series' months summed over the other's, the months that hold both.
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
a = d[(d["entity"] == 'eia_intl:USA:53') & (d["variable"] == 'production')]
b = d[(d['entity'] == 'eia_intl:WORL:53') & (d['variable'] == 'production')]
m = a.merge(b[['ts_utc', 'value']], on='ts_utc', suffixes=('', '_den'))
for y, s in m.groupby('year'):
    if s['value_den'].sum() != 0:
        print(y, round(float(s['value'].sum() * 100.0 / s['value_den'].sum()), 6), len(s))
