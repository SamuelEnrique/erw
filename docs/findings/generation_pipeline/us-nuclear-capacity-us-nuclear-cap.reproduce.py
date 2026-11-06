# Expected: 2007 101013.246301, 2025 98275.907945, change -2737.338356 (MW); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 164): reproduce candidate us_nuclear_capacity for us_nuclear_cap from the ERW's public table.

    python {this file} <eia_nuclear_outages_daily.csv>

The year's mean of EIA's daily US nuclear capacity, by calendar year.
"""
import sys

import pandas as pd

with open(sys.argv[1], encoding="utf-8") as f:
    skip = 0
    for line in f:
        if not line.startswith("#"):
            break
        skip += 1
d = pd.read_csv(sys.argv[1], skiprows=skip, usecols=['entity', 'variable', 'ts_utc', 'value'], dtype=str)
d["value"] = pd.to_numeric(d["value"], errors="coerce")
d = d.dropna(subset=["value"])
d["year"] = d["ts_utc"].str[:4].astype(int)
d = d[(d['entity'] == 'eia_nuclear_outages:US') & (d['variable'] == 'capacity')]
for y, s in d.groupby('year'):
    print(y, round(float(s['value'].mean()), 6), len(s))
