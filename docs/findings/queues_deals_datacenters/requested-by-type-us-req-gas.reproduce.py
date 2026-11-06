# Expected: 2005 28602.399985, 2024 77929.4, change 49327.000015 (MW); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 164): reproduce candidate requested_by_type for us_req_gas from the ERW's public table.

    python {this file} <lbnl_interconnection_queue.csv>

The US MW requested in the year, by type.
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
by = d[d['type_clean'] == 'Gas'].groupby('q_year')['mw'].sum()
for y in range(2005, 2025):
    print(y, round(float(by.get(y, 0.0)), 6), 1)
