# Expected: 2001 87.912113, 2025 174.683009, change 86.770896 (TWh); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 164): reproduce candidate commercial_sales for com_sales_TX from the ERW's public table.

    python {this file} <eia_retail_sales_monthly.csv>

The year's retail electricity sales to the commercial sector, Texas.
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
d = d[(d['entity'] == 'eia:retail_sales:TX:COM') & (d['variable'] == 'retail_sales')]
for y, s in d.groupby('year'):
    print(y, round(float(s['value'].sum() / 1e6), 6), len(s))
