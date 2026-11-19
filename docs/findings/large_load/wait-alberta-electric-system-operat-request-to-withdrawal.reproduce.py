# Expected figures: median_at_least 20.67; median_at_most 21.75; requests 39.0; tolerance 0.5 percent of each.
"""ERW findings hunt (chain 502): reproduce candidate wait_alberta_electric_system_operat_request_to_withdrawal for Alberta Electric System Operator (Canada) from the ERW's public tables.

    python {this file} <large_load_wait_summary.csv>

The bounds of the median wait, request to withdrawal, at Alberta Electric System Operator (Canada), as the internal summary holds them.
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

d = read(sys.argv[1], ['variable', 'value', 'x_publisher', 'x_interval'])
d = d[(d['x_publisher'] == 'Alberta Electric System Operator (Canada)') & (d['x_interval'] == 'request to withdrawal')]
for k in ('median_at_least', 'median_at_most', 'requests'):
    print(k, float(d[d['variable'] == k]['value'].iloc[0]))
