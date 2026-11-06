# Expected: 2001 31.425, 2025 115.191667, change 83.766667 (USD per MWh); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 164): reproduce candidate res_over_ind for res_ind_gap_MI from the ERW's public table.

    python {this file} <eia_retail_electricity_prices.csv>

The mean residential retail price less the mean industrial retail price over the year, Michigan.
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
d = d[d['entity'].isin(['eia:retail_price:MI:RES', 'eia:retail_price:MI:IND']) & (d['variable'] == 'retail_price')]
d['sec'] = d['entity'].str.split(':').str[3]
w = d.pivot_table(index=['year', 'ts_utc'], columns='sec', values='value').dropna().reset_index()
for y, s in w.groupby('year'):
    print(y, round(float((s['RES'] - s['IND']).mean()), 6), len(s))
