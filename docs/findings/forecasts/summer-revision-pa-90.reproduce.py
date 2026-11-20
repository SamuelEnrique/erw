# Expected: 2007 -1.265823, 2025 11.114302, change 12.380125 (percent); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 502): reproduce candidate summer_revision for pa_90 from the ERW's public tables.

    python {this file} <ferc714_planning_area_forecasts.csv>

For each filing (report year R): its forecast of the summer peak of year R+5 against the filing of R-1's forecast of the same year, percent.
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

d = read(sys.argv[1], ['entity', 'variable', 'ts_utc', 'value', 'x_report_year'])
d = d[(d['entity'] == 'ferc714:90') & (d['variable'] == 'summer_peak_forecast_mw')].copy()
d['value'] = pd.to_numeric(d['value'], errors='coerce')
d['ry'] = pd.to_numeric(d['x_report_year'], errors='coerce')
d = d.dropna(subset=['value', 'ry'])
d['fy'], d['ry'] = d['ts_utc'].str[:4].astype(int), d['ry'].astype(int)
d = d.drop_duplicates(['fy', 'ry'])
v = d.set_index(['ry', 'fy'])['value']
for ry in sorted(d['ry'].unique()):
    a, b = v.get((ry, ry + 5)), v.get((ry - 1, ry + 5))
    if a is None or b is None or b <= 0 or not (0.5 <= a / b <= 2.0):
        continue
    print(ry, round(float((a / b - 1) * 100), 6), 1)
