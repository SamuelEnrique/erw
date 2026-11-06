# Expected: 2015 67.933313, 2025 542.784914, change 474.851601 (minutes a customer); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 164): reproduce candidate saidi for saidi_NE from the ERW's public table.

    python {this file} <eia861_utility_reliability.csv>

The customer-weighted mean of the utilities' IEEE SAIDI with major event days, Nebraska.
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
d = d[d['geo'] == 'US-NE']
d = d[d['variable'].isin(['ieee_saidi_with_med', 'ieee_customers'])]
w = d.pivot_table(index=['entity', 'year'], columns='variable', values='value').dropna().reset_index()
w = w[w['ieee_customers'] > 0]
for y, s in w.groupby('year'):
    print(y, round(float((s['ieee_saidi_with_med'] * s['ieee_customers']).sum() / s['ieee_customers'].sum()), 6), 1)
