# Expected: 2001 36.24913, 2022 19.156949, change -17.092181 (percent of US energy CO2); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 166): reproduce candidate coal_co2_share for us_coal_co2_share from the ERW's public tables.

    python {this file} <eia_co2_state_annual.csv>

Coal's share of US energy-related CO2, every sector.
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
a = d[(d['st'] == 'US') & (d['sec'] == 'TT') & (d['fuel'] == 'CO')].groupby('year')['value'].sum()
b = d[(d['st'] == 'US') & (d['sec'] == 'TT') & (d['fuel'] == 'TO')].groupby('year')['value'].sum()
for y in a.index:
    if b.get(y, 0) > 0:
        print(y, round(float(100 * a[y] / b[y]), 6), 1)
