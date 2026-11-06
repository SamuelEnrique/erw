# Expected: 1973 30.906473, 2025 63.413382, change 32.506908 (percent of US crude imports); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 164): reproduce candidate import_share for imp_CA from the ERW's public tables.

    python {this file} <eia_crude_imports_by_country.csv>

A country's share of US crude oil imports over the year, Canada.
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
d = d[d['entity'].isin(['eia:MCRIMUS2', 'eia:MCRIMUSCA2']) & (d['variable'] == 'imports')].drop_duplicates(['entity', 'ts_utc'])
d['year'] = d['ts_utc'].str[:4].astype(int)
tot = d[d['entity'] == 'eia:MCRIMUS2'].groupby('year')['value'].sum()
for y, s in d[d['entity'] == 'eia:MCRIMUSCA2'].groupby('year'):
    if tot.get(y, 0) > 0:
        print(y, round(float(100 * s['value'].sum() / tot[y]), 6), len(s))
