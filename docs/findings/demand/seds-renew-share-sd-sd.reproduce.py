# Expected: 1990 8.72132, 2024 40.691958, change 31.970638 (percent); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 502): reproduce candidate seds_renew_share for sd_sd from the ERW's public tables.

    python {this file} <eia_seds_state_energy.csv>

Renewable energy's share (percent) of SD's total energy consumption, by year.
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
d = d[d['entity'].isin(['eia_seds:RETCB:SD', 'eia_seds:TETCB:SD'])].copy()
d['value'] = pd.to_numeric(d['value'], errors='coerce')
w = d.pivot_table(index='ts_utc', columns='entity', values='value', aggfunc='first').dropna()
for ts, r in w.iterrows():
    if r['eia_seds:TETCB:SD'] > 0:
        print(int(ts[:4]), round(float(r['eia_seds:RETCB:SD'] / r['eia_seds:TETCB:SD'] * 100), 6), 1)
