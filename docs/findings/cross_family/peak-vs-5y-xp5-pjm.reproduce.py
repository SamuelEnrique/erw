# Expected: 2019 -8.738766, 2025 5.681639, change 14.420404 (percent); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 502): reproduce candidate peak_vs_5y for xp5_pjm from the ERW's public tables.

    python {this file} <eia930_ba_demand_hourly.csv> <ferc714_planning_area_forecasts.csv>

For each year 2019 to 2025: PJM's actual peak hour (a lone spike dropped) against the higher of the summer and winter peak that planning area 119's filing of 5 years before forecast for it, percent.
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
d = d[(d['entity'] == 'eia930:PJM') & (d['variable'] == 'demand_mw')].copy()
d['demand'] = pd.to_numeric(d['value'], errors='coerce')
d = d.dropna(subset=['demand'])
d['year'] = d['ts_utc'].str[:4].astype(int)
d = d[d['demand'] > 0]
d = d[d['demand'] <= 3 * d.groupby('year')['demand'].transform('median')]
d['t'] = pd.to_datetime(d['ts_utc'].str[:10]).values.astype('datetime64[D]').astype('int64') * 24 + d['ts_utc'].str[11:13].astype(int)
d = d.sort_values('t')
prev = d['demand'].shift(1).where(d['t'].shift(1) == d['t'] - 1)
nxt = d['demand'].shift(-1).where(d['t'].shift(-1) == d['t'] + 1)
d = d[~(d['demand'] > 1.1 * pd.concat([prev, nxt], axis=1).max(axis=1))]
act = d.groupby('year')['demand'].max()
f = read(sys.argv[2], ['entity', 'variable', 'ts_utc', 'value', 'x_report_year'])
f = f[(f['entity'] == 'ferc714:119') & f['variable'].isin(['summer_peak_forecast_mw', 'winter_peak_forecast_mw'])].copy()
f['value'] = pd.to_numeric(f['value'], errors='coerce')
f['ry'] = pd.to_numeric(f['x_report_year'], errors='coerce')
f = f.dropna(subset=['value', 'ry'])
f['fy'] = f['ts_utc'].str[:4].astype(int)
f = f.drop_duplicates(['variable', 'fy', 'ry'])
fc = f[f['fy'] - f['ry'] == 5].groupby('fy')['value'].max()
for y in range(2019, 2026):
    if y in act.index and y in fc.index and fc[y] > 0 and 0.5 <= act[y] / fc[y] <= 2.0:
        print(y, round(float((act[y] / fc[y] - 1) * 100), 6), 1)
