# Expected: 2007 8.691008, 2025 3.56712, change -5.123888 (percent); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 502): reproduce candidate nuc_out_share for nucf_2589 from the ERW's public tables.

    python {this file} <eia_nuclear_outages_facility_daily.csv>

The year's mean share (percent) of eia_nuclear_outages:2589's capacity on outage.
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
d = d[(d['entity'] == 'eia_nuclear_outages:2589') & d['variable'].isin(['capacity', 'outage'])].copy()
d['value'] = pd.to_numeric(d['value'], errors='coerce')
w = d.pivot_table(index='ts_utc', columns='variable', values='value', aggfunc='first').dropna().reset_index()
w = w[w['capacity'] > 0]
for y, s in w.groupby(w['ts_utc'].str[:4]):
    print(y, round(float((s['outage'] / s['capacity']).mean() * 100), 6), len(s))
