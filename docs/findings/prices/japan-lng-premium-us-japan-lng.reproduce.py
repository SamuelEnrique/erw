# Expected: 2000 0.404167, 2025 8.510833, change 8.106667 (USD per MMBtu); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 164): reproduce candidate japan_lng_premium for us_japan_lng from the ERW's public table.

    python {this file} <wb_commodity_prices_monthly.csv>

The year's mean of the World Bank's Japan LNG import price less its US gas price, from 2000, by calendar year.
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
w = d[d['variable'] == 'price'].pivot_table(index='ts', columns='entity', values='value').dropna(subset=['wb_pink:liquefied_natural_gas_japan', 'wb_pink:natural_gas_us'])
w = w[w.index.year >= 2000]
gap = w['wb_pink:liquefied_natural_gas_japan'] - w['wb_pink:natural_gas_us']
for y, s in gap.groupby(gap.index.year):
    print(y, round(float(s.mean()), 6), len(s))
