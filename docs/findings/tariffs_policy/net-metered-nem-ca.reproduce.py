# Expected: 2013 2125.309, 2024 18822.433, change 16697.124 (MW); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 164): reproduce candidate net_metered for nem_CA from the ERW's public table.

    python {this file} <eia_net_metering_state_annual.csv>

Net-metered capacity, every technology and sector, California.
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
d["value"] = pd.to_numeric(d["value"], errors="coerce")
d = d.dropna(subset=["value"])
d["year"] = d["ts_utc"].str[:4].astype(int)
d = d[(d['entity'] == 'eia_net_metering:CA:all_technologies:TOT') & (d['variable'] == 'capacity')]
for y, s in d.groupby('year'):
    print(y, round(float(s['value'].sum()), 6), 1)
