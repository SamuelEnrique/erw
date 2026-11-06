# Expected: 2001 2258.660668, 2022 1532.041064, change -726.619604 (million tCO2); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 166): reproduce candidate power_co2 for us_power_co2 from the ERW's public tables.

    python {this file} <eia_co2_state_annual.csv>

The US electric power sector's energy-related CO2 over the year.
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


d = read(sys.argv[1], ['entity', 'variable', 'ts_utc', 'value'])
d = d[d['variable'] == 'co2']
p = d['entity'].str.split(':', expand=True)
d['st'], d['sec'], d['fuel'], d['year'] = p[1], p[2], p[3], d['ts_utc'].str[:4].astype(int)
d = d[d['year'] >= 2001]
s = d[(d['st'] == 'US') & (d['sec'] == 'EC') & (d['fuel'] == 'TO')].groupby('year')['value'].sum()
for y, v in s.items():
    print(y, round(float(v / 1e6), 6), 1)
