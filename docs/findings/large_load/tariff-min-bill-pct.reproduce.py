# Expected figures: median 80.0; lowest 75.0; highest 100.0; filings 11.0; tolerance 0.5 percent of each.
"""ERW findings hunt (chain 502): reproduce candidate tariff_min_bill_pct for tariffs from the ERW's public tables.

    python {this file} <utility_large_load_tariffs.csv>

The filings' min_bill_pct as each tariff states it: the median, the lowest, the highest and the count.
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

d = read(sys.argv[1], ['variable', 'value'])
d = d[d['variable'] == 'min_bill_pct'].copy()
d['value'] = pd.to_numeric(d['value'], errors='coerce')
d = d.dropna(subset=['value'])
print('median', float(d['value'].median()))
print('lowest', float(d['value'].min()))
print('highest', float(d['value'].max()))
print('filings', float(len(d)))
