# Expected: 1996 14196.494899, 2025 2078.979877, change -12117.515022 (million cubic feet a day); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 502): reproduce candidate gulf_gas for gulf from the ERW's public tables.

    python {this file} <boem_ogor_lease_production_monthly.csv>

The Gulf's gas (million cubic feet a day): the year's volume over its days; the third figure is the months held.
An hour whose absolute flow is more than three times its year's 99th percentile of absolute flows is dropped as a fault
of the report; an hour of demand at or below zero or above three times its year's median is dropped the same way.
Prints one line a year: the year, the figure, the hours it rests on.
"""
import sys

import numpy as np
import pandas as pd


def read(path, cols):
    with open(path, encoding="utf-8") as f:
        skip = 0
        for line in f:
            if not line.startswith("#"):
                break
            skip += 1
    return pd.read_csv(path, skiprows=skip, usecols=cols, dtype=str, keep_default_na=False)


def drop_flow_faults(d, col, by):
    a = d[col].abs()
    p99 = a.groupby([d[k] for k in by]).transform(lambda s: np.nanpercentile(s, 99))
    return d[a <= 3 * p99]

d = read(sys.argv[1], ['entity', 'variable', 'ts_utc', 'value'])
d = d[d['variable'] == 'gas_production'].copy()
d['value'] = pd.to_numeric(d['value'], errors='coerce')
d = d.dropna(subset=['value'])
d['year'] = d['ts_utc'].str[:4].astype(int)
for y, s in d.groupby('year'):
    print(y, round(float(s['value'].sum() / (366 if y % 4 == 0 else 365)), 6), s['ts_utc'].str[:7].nunique())
