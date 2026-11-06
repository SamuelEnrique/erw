# Expected: 2001 163.358333, 2025 404.75, change 241.391667 (USD per MWh); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 164): reproduce candidate res_price for res_price_HI from the ERW's public table.

    python {this file} <eia_retail_electricity_prices.csv>

The mean of the year's monthly average residential retail price, Hawaii.
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
d["year"] = d["ts_utc"].str[:4].astype(int)
d = d[(d['entity'] == 'eia:retail_price:HI:RES') & (d['variable'] == 'retail_price')]
for y, s in d.groupby('year'):
    print(y, round(float(s['value'].mean()), 6), len(s))
