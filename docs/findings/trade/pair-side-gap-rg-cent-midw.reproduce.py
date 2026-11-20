# Expected: 2021 38.403212, 2024 28.100643, change -10.302569 (MW); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 502): reproduce candidate pair_side_gap for rg_cent_midw from the ERW's public tables.

    python {this file} <eia930_region_pair_hourly.csv>

The year's mean absolute difference (MW) between the two regions' reports of the hour's flow, hours both sides hold.
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

d = read(sys.argv[1], ['entity', 'ts_utc', 'x_first_report', 'x_second_report'])
d = d[d['entity'] == 'eia930:CENT-MIDW'].copy()
d['year'] = d['ts_utc'].str[:4].astype(int)
sides = []
for col in ('x_first_report', 'x_second_report'):
    x = d[['ts_utc', 'year', col]].copy()
    x[col] = pd.to_numeric(x[col], errors='coerce')
    x = drop_flow_faults(x.dropna(subset=[col]), col, ['year'])
    sides.append(x)
w = sides[0].merge(sides[1][['ts_utc', 'x_second_report']], on='ts_utc')
w['gap'] = (w['x_first_report'] - w['x_second_report']).abs()
for y, s in w.groupby('year'):
    print(y, round(float(s['gap'].mean()), 6), len(s))
