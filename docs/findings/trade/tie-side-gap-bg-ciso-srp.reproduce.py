# Expected: 2019 1.534491, 2025 229.367539, change 227.833048 (MW); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 502): reproduce candidate tie_side_gap for bg_ciso_srp from the ERW's public tables.

    python {this file} <eia930_ba_interchange_hourly_2018.csv> <eia930_ba_interchange_hourly_2019.csv> <eia930_ba_interchange_hourly_2020.csv> <eia930_ba_interchange_hourly_2021.csv> <eia930_ba_interchange_hourly_2022.csv> <eia930_ba_interchange_hourly_2023.csv> <eia930_ba_interchange_hourly_2024.csv> <eia930_ba_interchange_hourly_2025.csv> <eia930_ba_interchange_hourly_2026.csv>

The year's mean absolute difference (MW) between CISO's and SRP's reports on their tie, hours both hold, each read as power from CISO to SRP.
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

d = pd.concat([read(p, ['entity', 'ts_utc', 'value']) for p in sys.argv[1:]], ignore_index=True)
d = d[d['entity'].isin(['eia930:CISO-SRP', 'eia930:SRP-CISO'])].copy()
d['value'] = pd.to_numeric(d['value'], errors='coerce')
d['v'] = np.where(d['entity'] == 'eia930:CISO-SRP', d['value'], -d['value'])
d['side'] = d['entity']
d = d.dropna(subset=['v'])
d['year'] = d['ts_utc'].str[:4].astype(int)
d = drop_flow_faults(d, 'v', ['side', 'year'])
w = d.pivot_table(index=['ts_utc', 'year'], columns='side', values='v', aggfunc='first').dropna().reset_index()
w['gap'] = (w['eia930:CISO-SRP'] - w['eia930:SRP-CISO']).abs()
for y, s in w.groupby('year'):
    print(y, round(float(s['gap'].mean()), 6), len(s))
