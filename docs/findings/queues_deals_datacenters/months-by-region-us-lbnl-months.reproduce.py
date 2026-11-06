# Expected: 2005 17.626283, 2024 62.75154, change 45.125257 (months); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 164): reproduce candidate months_by_region for us_lbnl_months from the ERW's public table.

    python {this file} <lbnl_interconnection_queue.csv>

The median months from request to online of the projects that came online in the year.
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
d = d.dropna(subset=['q_date', 'on_date'])
d = d[d['on_date'] >= d['q_date']]
d['months'], d['year'] = (d['on_date'] - d['q_date']).dt.days / 30.4375, d['on_date'].dt.year
for y, s in d.groupby('year'):
    if 2005 <= y <= 2024 and len(s) >= 10:
        print(int(y), round(float(s['months'].median()), 6), 1)
