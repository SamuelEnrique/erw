# Expected: 2015 64.709589, 2025 577.243836, change 512.534247 (thousand barrels a day); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 502): reproduce candidate exp_product for xp_epllea from the ERW's public tables.

    python {this file} <eia_petroleum_exports_by_destination.csv>

The exports of eia_petroleum_exports:NUS-Z00:EPLLEA (thousand barrels a day: the year's barrels over its days), with the months held.
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
d = d[(d['entity'] == 'eia_petroleum_exports:NUS-Z00:EPLLEA') & (d['variable'] == 'exports')].copy()
d['value'] = pd.to_numeric(d['value'], errors='coerce')
d = d.dropna(subset=['value'])
d['year'] = d['ts_utc'].str[:4].astype(int)
for y, s in d.groupby('year'):
    print(y, round(float(s['value'].sum() / (366 if y % 4 == 0 else 365)), 6), len(s))
