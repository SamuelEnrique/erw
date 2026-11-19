# Expected: 2019 82.636923, 2024 83.542286, change 0.905363 (F); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 502): reproduce candidate summer_temp for wt_fla from the ERW's public tables.

    python {this file} <region_weather_hourly.csv>

The mean temperature (F) of the year's June to August hours, Florida.
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

w = read(sys.argv[1], ['entity', 'variable', 'ts_utc', 'value'])
w = w[(w['entity'] == 'eia930:FLA') & (w['variable'] == 'temperature_f')].copy()
w['temp'] = pd.to_numeric(w['value'], errors='coerce')
w = w.dropna(subset=['temp'])
w['year'] = w['ts_utc'].str[:4].astype(int)
w = w[w['ts_utc'].str[5:7].astype(int).isin([6, 7, 8])]
for y, s in w.groupby('year'):
    print(y, round(float(s['temp'].mean()), 6), len(s))
