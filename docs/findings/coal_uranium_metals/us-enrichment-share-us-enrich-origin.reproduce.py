# Expected: 2003 13.883098, 2025 22.834646, change 8.951547 (percent of enrichment services); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 164): reproduce candidate us_enrichment_share for us_enrich_origin from the ERW's public table.

    python {this file} <eia_uranium_marketing_annual.csv>

Enrichment of US origin as a percent of the enrichment services bought for US reactors. Rule share: one series over another, the years that hold both.
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
a = d[(d["entity"] == 'eia_uranium:us') & (d["variable"] == 'enrichment_us_origin')]
b = d[(d['entity'] == 'eia_uranium:us') & (d['variable'] == 'enrichment_total')]
m = a.merge(b[['ts_utc', 'value']], on='ts_utc', suffixes=('', '_den'))
for y, s in m.groupby('year'):
    if s['value_den'].sum() != 0:
        print(y, round(float(s['value'].sum() * 100.0 / s['value_den'].sum()), 6), 1)
