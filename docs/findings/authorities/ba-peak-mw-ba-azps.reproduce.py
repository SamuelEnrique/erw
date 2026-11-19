# Expected: 2019 7026.0, 2025 8499.0, change 1473.0 (MW); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 502): reproduce candidate ba_peak_mw for ba_azps from the ERW's public tables.

    python {this file} <eia930_ba_demand_hourly.csv>

The year's highest hour of demand (MW) of AZPS, after dropping a lone spike (an hour more than 10 percent above both its neighbouring hours).
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

def clean(d, col):
    d = d[d[col] > 0]
    return d[d[col] <= 3 * d.groupby('year')[col].transform('median')]


def one(path, entity, variable, col):
    d = read(path, ['entity', 'variable', 'ts_utc', 'value'])
    d = d[(d['entity'] == entity) & (d['variable'] == variable)].copy()
    d[col] = pd.to_numeric(d['value'], errors='coerce')
    d = d.dropna(subset=[col])
    d['year'] = d['ts_utc'].str[:4].astype(int)
    return d[['ts_utc', 'year', col]]

d = clean(one(sys.argv[1], 'eia930:AZPS', 'demand_mw', 'demand'), 'demand')
d['t'] = pd.to_datetime(d['ts_utc'].str[:10]).values.astype('datetime64[D]').astype('int64') * 24 + d['ts_utc'].str[11:13].astype(int)
d = d.sort_values('t')
prev = d['demand'].shift(1).where(d['t'].shift(1) == d['t'] - 1)
nxt = d['demand'].shift(-1).where(d['t'].shift(-1) == d['t'] + 1)
near = pd.concat([prev, nxt], axis=1).max(axis=1)
d = d[~(d['demand'] > 1.1 * near)]
for y, s in d.groupby('year'):
    print(y, round(float(s['demand'].max()), 6), len(s))
