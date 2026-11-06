# Expected: 2012 101.093778, 2023 247.172313, change 146.078535 (USD thousand a year); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 164): reproduce candidate hosting_pay for pay518_NY from the ERW's public table.

    python {this file} <census_cbp_hosting_annual.csv>

Annual payroll per mid-March employee in NAICS 518210.
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
d = d[d['entity'] == 'census_cbp_518210:ny']
p = d[d['variable'].isin(['annual_payroll', 'employment'])].pivot_table(index=['year', 'entity'], columns='variable', values='value').dropna()
for y, s in p.groupby('year'):
    print(y, round(float(s['annual_payroll'].sum() / s['employment'].sum() / 1000), 6), 1)
