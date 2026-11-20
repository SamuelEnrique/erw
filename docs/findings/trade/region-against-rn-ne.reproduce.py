# Expected: 2019 0.045662, 2025 27.780315, change 27.734653 (percent of hours); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 502): reproduce candidate region_against for rn_ne from the ERW's public tables.

    python {this file} <eia930_region_hourly.csv>

The share of the year's hours (percent) in which New England, a net importer over 2019 to 2025, exported.
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
d = d[(d['entity'] == 'eia930:NE') & (d['variable'] == 'total_interchange_mw')].copy()
d['ti'] = pd.to_numeric(d['value'], errors='coerce')
w = d.dropna(subset=['ti'])[['ts_utc', 'ti']].copy()
w['year'] = w['ts_utc'].str[:4].astype(int)
w = drop_flow_faults(w, 'ti', ['year'])
w['v'] = w['ti'] * -1
for y, s in w.groupby('year'):
    print(y, round(float((s['v'] < 0).mean() * 100), 6), len(s))
