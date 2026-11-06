# Expected: 2001 14628.590779, 2024 11632.780844, change -2995.809935 (short tons per employee); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 164): reproduce candidate tons_per_employee for us_tons_employee from the ERW's public table.

    python {this file} <eia_coal_production_annual.csv>

US coal production over EIA's average employees at the mines. Rule share: one series over another, the years that hold both.
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
d = d.dropna(subset=["value"]).drop_duplicates(["entity", "variable", "ts_utc"])
d["year"] = d["ts_utc"].str[:4].astype(int)
a = d[(d["entity"] == 'eia_coal_production:US:TOT:ALL') & (d["variable"] == 'production')]
b = d[(d['entity'] == 'eia_coal_production:US:TOT:ALL') & (d['variable'] == 'employees')]
m = a.merge(b[['ts_utc', 'value']], on='ts_utc', suffixes=('', '_den'))
for y, s in m.groupby('year'):
    if s['value_den'].sum() != 0:
        print(y, round(float(s['value'].sum() * 1.0 / s['value_den'].sum()), 6), 1)
