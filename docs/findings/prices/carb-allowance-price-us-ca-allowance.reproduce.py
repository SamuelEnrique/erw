# Expected: 2013 12.83, 2025 28.055, change 15.225 (USD per tCO2); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 164): reproduce candidate carb_allowance_price for us_ca_allowance from the ERW's public table.

    python {this file} <carb_auction_allowance_prices.csv>

The year's mean settlement price of California's quarterly current-vintage allowance auctions, by calendar year.
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
d = d[(d['entity'] == 'carb:current_auction') & (d['variable'] == 'settlement_price')]
for y, s in d.groupby(d['ts'].dt.year):
    print(y, round(float(s['value'].mean()), 6), len(s))
