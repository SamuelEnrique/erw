# Expected: 2015 0.534192, 2025 2.855958, change 2.321766 (MWh per MW); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 164): reproduce candidate battery_hours for us_battery_hours from the ERW's public table.

    python {this file} <eia860m_operating_generators.csv>

The MWh per MW of the batteries that entered service in the year (their summed MWh over their summed MW).
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
for c in ('nameplate_mw', 'energy_capacity_mwh', 'operating_year'):
    d[c] = pd.to_numeric(d[c], errors='coerce')
d = d.dropna(subset=['nameplate_mw', 'energy_capacity_mwh', 'operating_year'])
d = d[d['operating_year'].between(2010, 2025)]
t = d.groupby('operating_year')[['energy_capacity_mwh', 'nameplate_mw']].sum()
for y, r in t.iterrows():
    if r['nameplate_mw'] >= 100:
        print(int(y), round(float(r['energy_capacity_mwh'] / r['nameplate_mw']), 6), 1)
