# Expected: 2001 20.041946, 2025 42.166911, change 22.124965 (percent of US crude production); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 164): reproduce candidate state_crude_share for crude_TX from the ERW's public tables.

    python {this file} <eia_crude_production_state_monthly.csv>

A state's share of US crude field production over the year, Texas.
"""
import sys

import pandas as pd


def read(path):
    with open(path, encoding="utf-8") as f:
        skip = 0
        for line in f:
            if not line.startswith("#"):
                break
            skip += 1
    d = pd.read_csv(path, skiprows=skip, usecols=["entity", "variable", "ts_utc", "value"], dtype=str)
    d["value"] = pd.to_numeric(d["value"], errors="coerce")
    return d.dropna(subset=["value"])


d = read(sys.argv[1])
d = d[d['variable'] == 'field_production_per_day'].drop_duplicates(['entity', 'ts_utc'])
d['code'], d['year'] = d['entity'].str.split(':').str[1], d['ts_utc'].str[:4].astype(int)
tot = d[d['code'] == 'NUS'].groupby('year')['value'].sum()
for y, s in d[d['code'] == 'STX'].groupby('year'):
    if tot.get(y, 0) > 0:
        print(y, round(float(100 * s['value'].sum() / tot[y]), 6), len(s))
