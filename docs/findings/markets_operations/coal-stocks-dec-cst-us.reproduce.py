# Expected: 2008 161.588607, 2025 109.733181, change -51.855426 (million short tons); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 502): reproduce candidate coal_stocks_dec for cst_us from the ERW's public tables.

    python {this file} <eia_power_fuel_stocks_monthly.csv>

The coal stocks (million short tons) of US's electric power sector at the end of each December.
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
d = d[(d['entity'] == 'eia_power_stocks:US:98:COL') & (d['ts_utc'].str[5:7] == '12')].copy()
d['value'] = pd.to_numeric(d['value'], errors='coerce')
for _, r in d.dropna(subset=['value']).sort_values('ts_utc').iterrows():
    print(int(r['ts_utc'][:4]), round(float(r['value'] / 1e6), 6), 1)
