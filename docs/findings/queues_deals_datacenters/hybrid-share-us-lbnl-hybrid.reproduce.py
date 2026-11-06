# Expected: 2005 0.0, 2024 37.039781, change 37.039781 (percent of solar MW requested); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 164): reproduce candidate hybrid_share for us_lbnl_hybrid from the ERW's public table.

    python {this file} <lbnl_interconnection_queue.csv>

The percent of the solar MW requested in the year whose request also lists a battery.
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
d = d.dropna(subset=['mw', 'q_year'])
d = d[d['type_1'] == 'Solar']
d['paired'] = (d['type_2'] == 'Battery') | (d['type_3'] == 'Battery')
tot, par = d.groupby('q_year')['mw'].sum(), d[d['paired']].groupby('q_year')['mw'].sum()
for y in range(2005, 2025):
    if tot.get(y, 0) > 0:
        print(y, round(float(100 * par.get(y, 0.0) / tot[y]), 6), 1)
