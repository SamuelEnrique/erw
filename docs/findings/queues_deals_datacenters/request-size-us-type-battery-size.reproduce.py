# Expected: 2008 20.0, 2024 152.755203, change 132.755203 (MW); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 164): reproduce candidate request_size for us_type_battery_size from the ERW's public table.

    python {this file} <lbnl_interconnection_queue.csv>

The median MW of the requests of the type that entered a queue in the year.
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
d = d[d['type_clean'] == 'Battery']
for y, s in d.groupby('q_year'):
    if 2005 <= y <= 2024 and len(s) >= 10:
        print(int(y), round(float(s['mw'].median()), 6), 1)
