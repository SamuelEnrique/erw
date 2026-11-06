# Expected: 2019 191.602692, 2025 59.258269, change -132.344423 (USD per tCO2); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 164): reproduce candidate lcfs_credit_price for us_ca_lcfs from the ERW's public table.

    python {this file} <carb_lcfs_credit_prices.csv>

The year's mean of the weekly average Low Carbon Fuel Standard credit price, by calendar year.
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
d = d[(d['entity'] == 'carb:lcfs_credit') & (d['variable'] == 'credit_price_weekly_avg')]
for y, s in d.groupby(d['ts'].dt.year):
    print(y, round(float(s['value'].mean()), 6), len(s))
