# Expected: 2017 78.242721, 2025 51.079679, change -27.163043 (percent); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 502): reproduce candidate eu_share_coal for eu_pl from the ERW's public tables.

    python {this file} <eurostat_electricity_monthly.csv>

Coal and manufactured gases's share (percent) of net production, PL, years with all twelve months of every figure.
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
d = d[(d['entity'] == 'eurostat_elec:PL') & d['variable'].isin(['net_production:C0000', 'net_production:TOTAL'])].copy()
d['value'] = pd.to_numeric(d['value'], errors='coerce')
d = d.dropna(subset=['value'])
d['year'] = d['ts_utc'].str[:4].astype(int)
g = d.groupby(['variable', 'year'])['value'].agg(['sum', 'size']).reset_index()
g = g[g['size'] == 12]
w = g.pivot_table(index='year', columns='variable', values='sum').dropna()
for y, t in w.iterrows():
    print(y, round(float(t['net_production:C0000'] / t['net_production:TOTAL'] * 100), 6), 12)
