# Expected: 2010 5.0, 2025 83.0, change 78.0 (earthquakes); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 502): reproduce candidate quakes_m3 for eq_new_mexico from the ERW's public tables.

    python {this file} <usgs_comcat_earthquakes_south_central.csv>

The earthquakes of magnitude 3.0 and above whose place USGS names in New Mexico, by year.
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

d = read(sys.argv[1], ['event_id', 'event_date', 'x_magnitude', 'x_place_state'])
d['m'] = pd.to_numeric(d['x_magnitude'], errors='coerce')
d = d[(d['m'] >= 3.0) & (d['x_place_state'] == 'New Mexico')].drop_duplicates('event_id')
by = d.groupby(d['event_date'].str[:4].astype(int)).size()
for y in range(2010, 2027):
    print(y, int(by.get(y, 0)), 1)
