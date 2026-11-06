# Expected: 2005 1512.371506, 2025 3804.358172, change 2291.986666 (kW); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 164): reproduce candidate turbine_kw for us_turbine_kw from the ERW's public table.

    python {this file} <uswtdb_wind_turbines.csv>

The mean rated capacity of the onshore turbines of the year's projects.
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
d = d[d['offshore'].isin(['0', '0.0', 'False', 'false'])]
d['year'], d['v'] = pd.to_numeric(d['project_year'], errors='coerce'), pd.to_numeric(d['turbine_capacity_kw'], errors='coerce')
d = d.dropna(subset=['year', 'v'])
for y, s in d.groupby('year'):
    if 2005 <= y <= 2025:
        print(int(y), round(float(s['v'].mean()), 6), 1)
