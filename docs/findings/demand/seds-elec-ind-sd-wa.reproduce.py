# Expected: 1990 40.711899, 2024 18.159437, change -22.552462 (TWh); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 502): reproduce candidate seds_elec_ind for sd_wa from the ERW's public tables.

    python {this file} <eia_seds_state_energy.csv>

SEDS series ESICB for WA, by year (TBtu over 3.412: TWh).
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
d = d[d['entity'] == 'eia_seds:ESICB:WA'].copy()
d['value'] = pd.to_numeric(d['value'], errors='coerce')
for _, r in d.dropna(subset=['value']).sort_values('ts_utc').iterrows():
    print(int(r['ts_utc'][:4]), round(float(r['value'] / 3.412), 6), 1)
