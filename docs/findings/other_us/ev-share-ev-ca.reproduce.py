# Expected: 2016 0.460962, 2025 4.817932, change 4.356971 (percent of registered light-duty vehicles); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 166): reproduce candidate ev_share for ev_CA from the ERW's public table.

    python {this file} <afdc_vehicle_registrations_annual.csv>

Battery electric vehicles' share of the light-duty vehicles registered.
"""
import sys

import pandas as pd

with open(sys.argv[1], encoding="utf-8") as f:
    skip = 0
    for line in f:
        if not line.startswith("#"):
            break
        skip += 1
d = pd.read_csv(sys.argv[1], skiprows=skip, usecols=["entity", "variable", "ts_utc", "value"], dtype=str)
d["value"] = pd.to_numeric(d["value"], errors="coerce")
d = d.dropna(subset=["value"])
d["year"] = d["ts_utc"].str[:4].astype(int)
d = d[(d['entity'] == 'afdc_reg:CA') & d['variable'].str.startswith('registrations_')]
for y, s in d.groupby('year'):
    t = s['value'].sum()
    if t > 0:
        print(y, round(float(100 * s.loc[s['variable'] == 'registrations_ev', 'value'].sum() / t), 6), 1)
