# Expected: 1980 59557.68724, 2025 84462.560673, change 24904.873433 (thousand barrels a day); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 502): reproduce candidate wog_crude for wog_worl from the ERW's public tables.

    python {this file} <eia_world_oil_gas_annual.csv>

Crude oil production (EIA's code 57, thousand barrels a day) of WORL, by year from 1980.
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
d = d[(d['entity'] == 'eia_intl:WORL:57') & (d['variable'] == 'production')].copy()
d['value'] = pd.to_numeric(d['value'], errors='coerce')
for _, r in d.dropna(subset=['value']).sort_values('ts_utc').iterrows():
    if int(r['ts_utc'][:4]) >= 1980:
        print(int(r['ts_utc'][:4]), round(float(r['value']), 6), 1)
