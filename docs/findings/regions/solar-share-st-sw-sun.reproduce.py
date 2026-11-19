# Expected: 2001 0.000396, 2025 13.962588, change 13.962192 (percent); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 502): reproduce candidate solar_share for st_sw_sun from the ERW's public tables.

    python {this file} <eia_state_generation_monthly.csv>

Utility-scale solar's share (percent) of the net generation of AZ, NM, years with all twelve months of every state.
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
sts = ['AZ', 'NM']
d = d[(d['variable'] == 'net_generation') & d['entity'].isin([f'eia:generation:{s}:{f}' for s in sts for f in ('ALL', 'SUN')])].copy()
d['value'] = pd.to_numeric(d['value'], errors='coerce')
d = d.dropna(subset=['value'])
d['state'], d['fuel'] = d['entity'].str.split(':').str[2], d['entity'].str.split(':').str[3]
d['year'] = d['ts_utc'].str[:4].astype(int)
for y, s in d.groupby('year'):
    a = s[s['fuel'] == 'ALL']
    months = a.groupby('state')['ts_utc'].nunique()
    if len(months) < len(sts) or months.min() < 12:
        continue
    print(y, round(float(s[s['fuel'] == 'SUN']['value'].sum() / a['value'].sum() * 100), 6), 12)
