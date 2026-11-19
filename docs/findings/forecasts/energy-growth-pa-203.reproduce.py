# Expected: 2009 -1.403549, 2025 2.696003, change 4.099552 (percent a year); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 502): reproduce candidate energy_growth for pa_203 from the ERW's public tables.

    python {this file} <ferc714_planning_area_forecasts.csv>

For each filing (report year): the yearly growth it forecasts for the net energy of ferc714:203, from its first forecast year to its tenth, in percent.
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
d = d[(d['entity'] == 'ferc714:203') & (d['variable'] == 'net_energy_forecast_mwh')].copy()
d['value'] = pd.to_numeric(d['value'], errors='coerce')
d['ry'] = pd.to_numeric(d['x_report_year'], errors='coerce')
d = d.dropna(subset=['value', 'ry'])
d['fy'], d['ry'] = d['ts_utc'].str[:4].astype(int), d['ry'].astype(int)
d = d.drop_duplicates(['fy', 'ry'])
for ry, g in d.groupby('ry'):
    v = dict(zip(g['fy'], g['value']))
    a, b = v.get(ry + 1), v.get(ry + 10)
    if a is None or b is None or a <= 0 or not (0.5 <= b / a <= 3.0):
        continue
    print(ry, round(((b / a) ** (1 / 9) - 1) * 100, 6), 1)
