# Expected: 2002 -0.229167, 2025 2.341818, change 2.570985 (USD per Mcf); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 164): reproduce candidate power_vs_citygate for state_pow_NE from the ERW's public table.

    python {this file} <eia_gas_prices_state_monthly.csv>

The year's mean of the gas price power plants paid less the citygate price, months with both, by calendar year.
"""
import sys

import pandas as pd

with open(sys.argv[1], encoding="utf-8") as f:
    skip = 0
    for line in f:
        if not line.startswith("#"):
            break
        skip += 1
d = pd.read_csv(sys.argv[1], skiprows=skip, dtype=str)
d["value"] = pd.to_numeric(d["value"], errors="coerce")
d = d.dropna(subset=["value"])
d["ts"] = pd.to_datetime(d["ts_utc"], format="%Y-%m-%dT%H:%M:%SZ", utc=True)
d = d[(d['geo'] == 'US-NE') & d['variable'].isin(['price_electric_power', 'price_citygate'])]
w = d.pivot_table(index='ts', columns='variable', values='value').dropna()
gap = w['price_electric_power'] - w['price_citygate']
for y, s in gap.groupby(gap.index.year):
    print(y, round(float(s.mean()), 6), len(s))
