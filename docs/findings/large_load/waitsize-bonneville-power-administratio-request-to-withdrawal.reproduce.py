# Expected figures: large_at_least 17.051335; large_at_most 27.433265; small_at_least 42.809035; small_at_most 56.213552; tolerance 0.5 percent of each.
"""ERW findings hunt (chain 502): reproduce candidate waitsize_bonneville_power_administratio_request_to_withdrawal for Bonneville Power Administration from the ERW's public tables.

    python {this file} <large_load_waits.csv>

The bounds of the median wait, request to withdrawal, at Bonneville Power Administration, for requests of 300 MW and over and under 20 MW (months of 30.4375 days).
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

import statistics

d = read(sys.argv[1], ['entity', 'interval', 'size_class', 'label', 'days_at_least', 'days_at_most', 'request_id'])
d = d[(d['entity'] == 'Bonneville Power Administration') & (d['interval'] == 'request to withdrawal') & (d['label'] == 'measured')].copy()
for c in ('days_at_least', 'days_at_most'):
    d[c] = pd.to_numeric(d[c], errors='coerce')
for key, size in (('large', '300 MW and over'), ('small', 'under 20 MW')):
    x = d[d['size_class'] == size].drop_duplicates('request_id')
    print(key + '_at_least', round(statistics.median(x['days_at_least'].dropna()) / 30.4375, 6))
    print(key + '_at_most', round(statistics.median(x['days_at_most'].dropna()) / 30.4375, 6))
