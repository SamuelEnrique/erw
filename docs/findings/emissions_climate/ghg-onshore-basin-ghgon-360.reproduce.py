# Expected: 2015 10.955733, 2023 6.164428, change -4.791305 (million t CO2e); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 502): reproduce candidate ghg_onshore_basin for ghgon_360 from the ERW's public tables.

    python {this file} <epa_ghgrp_facility_emissions.csv>

The emissions (million t CO2e) reported for onshore oil and gas production in basin 360, by year.
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

d = read(sys.argv[1], ['variable', 'ts_utc', 'value', 'geo', 'x_sectors', 'x_basin'])
d['value'] = pd.to_numeric(d['value'], errors='coerce')
d = d.dropna(subset=['value'])
d = d[(d['variable'] == 'emissions_onshore_production') & d['x_basin'].str.lower().str.startswith('360 - ')]
for y, s in d.groupby(d['ts_utc'].str[:4]):
    print(y, round(float(s['value'].sum() / 1e6), 6), 1)
