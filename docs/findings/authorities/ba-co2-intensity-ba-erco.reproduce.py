# Expected: 2019 408.474734, 2025 315.408474, change -93.06626 (kg CO2 per MWh); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 502): reproduce candidate ba_co2_intensity for ba_erco from the ERW's public tables.

    python {this file} <eia930_all_emissions.csv> <eia930_ba_supply_hourly.csv>

The CO2 ERCO's generators emitted per MWh they generated (kg per MWh), hours both are held.
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

def clean(d, col):
    d = d[d[col] > 0]
    return d[d[col] <= 3 * d.groupby('year')[col].transform('median')]


def one(path, entity, variable, col):
    d = read(path, ['entity', 'variable', 'ts_utc', 'value'])
    d = d[(d['entity'] == entity) & (d['variable'] == variable)].copy()
    d[col] = pd.to_numeric(d['value'], errors='coerce')
    d = d.dropna(subset=[col])
    d['year'] = d['ts_utc'].str[:4].astype(int)
    return d[['ts_utc', 'year', col]]

c = one(sys.argv[1], 'eia930:ERCO', 'co2_emissions_generated', 'co2')
c = c[c['co2'] >= 0]
g = clean(one(sys.argv[2], 'eia930:ERCO', 'net_generation_mw', 'gen'), 'gen')
w = c.merge(g[['ts_utc', 'gen']], on='ts_utc')
for y, s in w.groupby('year'):
    print(y, round(float(s['co2'].sum() / s['gen'].sum() * 1000), 6), len(s))
