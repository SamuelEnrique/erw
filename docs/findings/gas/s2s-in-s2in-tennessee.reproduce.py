# Expected: 1990 13.255, 2025 24.728, change 11.473 (bcf a day); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 502): reproduce candidate s2s_in for s2in_tennessee from the ERW's public tables.

    python {this file} <eia_state_to_state_capacity.csv>

The summed capacity (bcf a day) of the pipeline crossings into Tennessee, by year.
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

d = read(sys.argv[1], ['ts_utc', 'value', 'x_state_to'])
d = d[d['x_state_to'] == 'Tennessee'].copy()
d['value'] = pd.to_numeric(d['value'], errors='coerce')
for y, s in d.dropna(subset=['value']).groupby(d['ts_utc'].str[:4]):
    print(y, round(float(s['value'].sum()), 6), 1)
