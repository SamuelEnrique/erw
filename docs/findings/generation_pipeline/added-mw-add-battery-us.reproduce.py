# Expected: 2010 0.0, 2025 16372.5, change 16372.5 (MW); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 164): reproduce candidate added_mw for add_battery_US from the ERW's public table.

    python {this file} <eia860m_operating_generators.csv>

The nameplate MW of today's operating generators that entered service in the year.
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
d = d[d['technology'] == 'Batteries']
d['mw'], d['year'] = pd.to_numeric(d['nameplate_mw'], errors='coerce'), pd.to_numeric(d['operating_year'], errors='coerce')
by = d.dropna(subset=['mw', 'year']).groupby('year')['mw'].sum()
for y in range(2010, 2026):
    print(y, round(float(by.get(y, 0.0)), 6), 1)
