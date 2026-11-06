# Expected: 1988 -1.043425, 2025 3.581926, change 4.625351 (USD per barrel); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 164): reproduce candidate brent_wti_spread for us_brent_wti from the ERW's public table.

    python {this file} <eia_fuel_spot_prices.csv>

The year's mean of the daily Brent spot close less the WTI Cushing close, days with both, by calendar year.
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
d = d[d['variable'] == 'spot_price']
w = d.pivot_table(index='ts', columns='entity', values='value').dropna(subset=['eia:brent', 'eia:wti_cushing'])
gap = w['eia:brent'] - w['eia:wti_cushing']
for y, s in gap.groupby(gap.index.year):
    print(y, round(float(s.mean()), 6), len(s))
