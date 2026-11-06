# Expected: 2014 381.0, 2025 17344.0, change 16963.0 (ports); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 166): reproduce candidate dcfast_ports for dcfast_CA from the ERW's public table.

    python {this file} <afdc_ev_charging_state_annual.csv>

Public DC fast charging ports at the year's end.
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
d = d[d['variable'] == 'ev_dcfast_ports']
d = d[d['entity'].str.split(':').str[1].str.upper() == 'CA']
d = d[d['entity'].str.split(':').str[1].str.upper().isin(['AK', 'AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL', 'GA', 'HI', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD', 'ME', 'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM', 'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'US', 'UT', 'VA', 'VT', 'WA', 'WI', 'WV', 'WY'])]
for y, s in d.groupby('year'):
    print(y, round(float(s['value'].sum()), 6), 1)
