# Expected: 2019 -9.259141, 2025 -7.262145, change 1.996996 (percent); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 502): reproduce candidate util_vs_3y for xu3_12293 from the ERW's public tables.

    python {this file} <eia861m_utility_sales_monthly.csv> <ferc714_planning_area_forecasts.csv>

For each year 2019 to 2025: utility 12293's retail sales (EIA-861M, TN summed, years with all twelve months in every state) against the net energy planning area 90's filing of 3 years before forecast for it, percent.
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

s = read(sys.argv[1], ['ts_utc', 'value', 'x_utility_number', 'x_state', 'variable'])
s = s[(s['variable'] == 'total_sales') & (s['x_utility_number'] == '12293')].copy()
s['value'] = pd.to_numeric(s['value'], errors='coerce')
s = s.dropna(subset=['value'])
s['year'] = s['ts_utc'].str[:4].astype(int)
states = ['TN']
g = s.groupby(['x_state', 'year'])['value'].agg(['sum', 'size']).reset_index()
act = {}
for y, z in g.groupby('year'):
    if len(z) == len(states) and (z['size'] == 12).all():
        act[y] = z['sum'].sum()
f = read(sys.argv[2], ['entity', 'variable', 'ts_utc', 'value', 'x_report_year'])
f = f[(f['entity'] == 'ferc714:90') & (f['variable'] == 'net_energy_forecast_mwh')].copy()
f['value'] = pd.to_numeric(f['value'], errors='coerce')
f['ry'] = pd.to_numeric(f['x_report_year'], errors='coerce')
f = f.dropna(subset=['value', 'ry'])
f['fy'] = f['ts_utc'].str[:4].astype(int)
f = f.drop_duplicates(['fy', 'ry'])
fc = f[f['fy'] - f['ry'] == 3].groupby('fy')['value'].first()
for y in range(2019, 2026):
    if y in act and y in fc.index and fc[y] > 0 and 0.5 <= act[y] / fc[y] <= 2.0:
        print(y, round(float((act[y] / fc[y] - 1) * 100), 6), 1)
