# Expected: 2005 65.804386, 2024 88.66781, change 22.863424 (percent of MW leaving the queue); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 164): reproduce candidate withdrawn_share for us_lbnl_wd from the ERW's public table.

    python {this file} <lbnl_interconnection_queue.csv>

The MW withdrawn in the year as a percent of the MW withdrawn or brought online in it.
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
for c in ('q_date', 'on_date', 'wd_date'):
    d[c] = pd.to_datetime(d[c], errors='coerce')
d['mw'], d['q_year'] = pd.to_numeric(d['mw_1'], errors='coerce'), pd.to_numeric(d['q_year'], errors='coerce')
d = d.dropna(subset=['mw'])
ob = d.dropna(subset=['on_date']).groupby(d['on_date'].dt.year)['mw'].sum()
wb = d.dropna(subset=['wd_date']).groupby(d['wd_date'].dt.year)['mw'].sum()
for y in range(2005, 2025):
    if ob.get(y, 0.0) > 0 and wb.get(y, 0.0) > 0:
        print(y, round(float(100 * wb[y] / (ob[y] + wb[y])), 6), 1)
