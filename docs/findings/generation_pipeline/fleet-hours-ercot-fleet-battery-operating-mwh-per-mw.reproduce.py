# Expected: 2015 0.3778, 2025 1.5514, change 1.1736 (MWh per MW); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 164): reproduce candidate fleet_hours for ercot_fleet_battery_operating_mwh_per_mw from the ERW's public table.

    python {this file} <storage_buildout_monthly.csv>

The battery fleet's MWh per MW at the year's end.
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
d = d[(d['entity'] == 'iso:ercot') & (d['variable'] == 'battery_operating_mwh_per_mw') & (d['ts_utc'].str[5:7] == '12')]
d['value'] = pd.to_numeric(d['value'], errors='coerce')
for _, r in d.dropna(subset=['value']).iterrows():
    print(int(r['ts_utc'][:4]), round(float(r['value']), 6), 1)
