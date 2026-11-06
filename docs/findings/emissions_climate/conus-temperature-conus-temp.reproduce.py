# Expected: 2000 1.240833, 2025 2.6075, change 1.366667 (degrees F above the 1901 to 2000 mean); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 166): reproduce candidate conus_temperature for conus_temp from the ERW's public tables.

    python {this file} <noaa_climdiv_state_monthly.csv>

The contiguous US's mean monthly temperature over the year less its months' 1901 to 2000 means.
"""
import sys

import pandas as pd


def read(path, cols):
    with open(path, encoding="utf-8") as f:
        skip = 0
        for line in f:
            if not line.startswith("#"):
                break
            skip += 1
    d = pd.read_csv(path, skiprows=skip, usecols=cols, dtype=str)
    d["value"] = pd.to_numeric(d["value"], errors="coerce")
    return d.dropna(subset=["value"])


d = read(sys.argv[1], ['entity', 'variable', 'ts_utc', 'value', 'x_mean_1901_2000'])
d = d[(d['entity'] == 'noaa_climdiv:110') & (d['variable'] == 'temp_avg')].copy()
d['norm'] = pd.to_numeric(d['x_mean_1901_2000'], errors='coerce')
d = d.dropna(subset=['norm'])
d['year'] = d['ts_utc'].str[:4].astype(int)
d = d[d['year'] >= 2000]
for y, s in d.groupby('year'):
    print(y, round(float((s['value'] - s['norm']).mean()), 6), len(s))
