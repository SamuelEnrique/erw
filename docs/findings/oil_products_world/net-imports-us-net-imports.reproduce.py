# Expected: 2010 9439.916667, 2025 -2850.333333, change -12290.25 (thousand barrels a day); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 164): reproduce candidate net_imports for us_net_imports from the ERW's public tables.

    python {this file} <eia_net_imports_monthly.csv>

US net imports of crude oil and petroleum products, the year's mean of its months.
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
d = d[(d['entity'] == 'eia_net_imports:MTTNTUS2') & (d['variable'] == 'net_imports_crude_and_products')].drop_duplicates('ts_utc')
for y, s in d.groupby(d['ts_utc'].str[:4].astype(int)):
    print(y, round(float(s['value'].mean()), 6), len(s))
