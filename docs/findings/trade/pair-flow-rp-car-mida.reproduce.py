# Expected: 2019 362.543721, 2025 767.140698, change 404.596977 (MW); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 502): reproduce candidate pair_flow for rp_car_mida from the ERW's public tables.

    python {this file} <eia930_region_pair_hourly.csv>

The year's mean hourly flow from the Carolinas to the Mid-Atlantic (MW).
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

d = read(sys.argv[1], ['entity', 'ts_utc', 'value'])
d = d[d['entity'] == 'eia930:CAR-MIDA'].copy()
d['v'] = pd.to_numeric(d['value'], errors='coerce') * 1
d = d.dropna(subset=['v'])
d['year'] = d['ts_utc'].str[:4].astype(int)
d = drop_flow_faults(d, 'v', ['year'])
for y, s in d.groupby('year'):
    print(y, round(float(s['v'].mean()), 6), len(s))
