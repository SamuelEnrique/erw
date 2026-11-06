# Expected: 2015 250.2, 2025 43678.3, change 43428.1 (MW); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 164): reproduce candidate battery_fleet_mw for us_fleet_battery_operating_mw from the ERW's public table.

    python {this file} <storage_buildout_monthly.csv>

The battery fleet in operation at the year's end.
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
d = d[(d['entity'] == 'us:total') & (d['variable'] == 'battery_operating_mw') & (d['ts_utc'].str[5:7] == '12')]
d['value'] = pd.to_numeric(d['value'], errors='coerce')
for _, r in d.dropna(subset=['value']).iterrows():
    print(int(r['ts_utc'][:4]), round(float(r['value']), 6), 1)
