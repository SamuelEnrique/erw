# Expected: 1973 4.019065, 2025 8.618382, change 4.599317 (percent of primary energy production); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 166): reproduce candidate renewable_share for us_renewable_share from the ERW's public table.

    python {this file} <eia_primary_energy_monthly.csv>

Renewables' share of US primary energy production.
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
d = d[d['entity'].isin(['eia:REPRBUS', 'eia:TEPRBUS'])].drop_duplicates(['entity', 'ts_utc'])
w = d.pivot_table(index='ts_utc', columns='entity', values='value').dropna()
for y, s in w.groupby(w.index.str[:4].astype(int)):
    print(y, round(float(100 * s['eia:REPRBUS'].sum() / s['eia:TEPRBUS'].sum()), 6), len(s))
