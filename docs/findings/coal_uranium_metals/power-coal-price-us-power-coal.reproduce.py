# Expected: 2001 24.68, 2025 45.85, change 21.17 (USD per short ton); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 164): reproduce candidate power_coal_price for us_power_coal from the ERW's public table.

    python {this file} <eia_coal_delivered_price_annual.csv>

The average delivered price of coal to the electric power sector. Rule mean: the year's figure (an annual table: one row a year).
"""
import sys

import pandas as pd

with open(sys.argv[1], encoding="utf-8") as f:
    skip = 0
    for line in f:
        if not line.startswith("#"):
            break
        skip += 1
d = pd.read_csv(sys.argv[1], skiprows=skip, usecols=["entity", "variable", "ts_utc", "value"], dtype=str)
d["value"] = pd.to_numeric(d["value"], errors="coerce")
d = d.dropna(subset=["value"]).drop_duplicates(["entity", "variable", "ts_utc"])
d["year"] = d["ts_utc"].str[:4].astype(int)
a = d[(d["entity"] == 'eia_coal_delivered:US:98') & (d["variable"] == 'price')]
for y, s in a.groupby('year'):
    print(y, round(float(s['value'].mean() * 1.0), 6), 1)
