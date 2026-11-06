# Expected: 2001 8308.188812, 2023 4150.0, change -4158.188812 (USD per kW DC); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 164): reproduce candidate res_pv_price for tts_res_CA from the ERW's public table.

    python {this file} <lbnl_tracking_the_sun.csv>

The median installed price of the year's residential systems over their DC size.
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
d = d[(d['entity'] == 'tts:ca_res') & d['variable'].isin(['price_median', 'systems_priced'])]
d['value'] = pd.to_numeric(d['value'], errors='coerce')
w = d.pivot_table(index='ts_utc', columns='variable', values='value').dropna()
w = w[w['systems_priced'] >= 500]
for ts, r in w.iterrows():
    print(int(ts[:4]), round(float(r['price_median']), 6), 1)
