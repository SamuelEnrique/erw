# Expected: 2008 6.096928, 2025 1.609081, change -4.487846 (percent); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 502): reproduce candidate coal_basin_share for cb_appalachia_central from the ERW's public tables.

    python {this file} <eia_coal_receipts_annual.csv>

The share (percent, by tons) of the coal US power plants received with x_mine_basin Appalachia Central, by year.
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

d = read(sys.argv[1], ['entity', 'variable', 'ts_utc', 'value', 'x_mine_basin', 'x_transport_mode'])
d = d[d['variable'].isin(['quantity', 'sulfur_content'])].copy()
d['value'] = pd.to_numeric(d['value'], errors='coerce')
w = d.pivot_table(index=['entity', 'ts_utc', 'x_mine_basin', 'x_transport_mode'], columns='variable', values='value', aggfunc='first').reset_index()
w = w.dropna(subset=['quantity'])
w['year'] = w['ts_utc'].str[:4].astype(int)
tot = w.groupby('year')['quantity'].sum()
by = w[w['x_mine_basin'] == 'Appalachia Central'].groupby('year')['quantity'].sum()
for y, q in by.items():
    print(y, round(float(q / tot[y] * 100), 6), 1)
