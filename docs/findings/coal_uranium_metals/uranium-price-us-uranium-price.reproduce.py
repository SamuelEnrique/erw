# Expected: 2003 10.81, 2025 58.46, change 47.65 (USD per pound U3O8e); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 164): reproduce candidate uranium_price for us_uranium_price from the ERW's public table.

    python {this file} <eia_uranium_marketing_annual.csv>

The weighted average price of the uranium the owners and operators of US reactors bought. Rule mean: the year's figure (an annual table: one row a year).
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
a = d[(d["entity"] == 'eia_uranium:us') & (d["variable"] == 'price_purchased_total')]
for y, s in a.groupby('year'):
    print(y, round(float(s['value'].mean() * 1.0), 6), 1)
