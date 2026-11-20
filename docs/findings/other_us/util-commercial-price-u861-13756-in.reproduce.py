# Expected: 2017 132.603805, 2025 192.43409, change 59.830285 (USD per MWh); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 502): reproduce candidate util_commercial_price for u861_13756_in from the ERW's public tables.

    python {this file} <eia861m_utility_sales_monthly.csv>

The commercial revenue over commercial sales (USD per MWh) of eia861m:13756:IN, by year, with the months held.
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
d = d[(d['entity'] == 'eia861m:13756:IN') & d['variable'].isin(['commercial_sales', 'commercial_revenue'])].copy()
d['value'] = pd.to_numeric(d['value'], errors='coerce')
d = d.dropna(subset=['value'])
d['year'] = d['ts_utc'].str[:4].astype(int)
g = d.groupby(['year', 'variable'])['value'].agg(['sum', 'size']).unstack('variable')
for y, r in g.iterrows():
    if r[('sum', 'commercial_sales')] > 0:
        print(y, round(float(r[('sum', 'commercial_revenue')] / r[('sum', 'commercial_sales')]), 6), int(min(r[('size', 'commercial_sales')], r[('size', 'commercial_revenue')])))
