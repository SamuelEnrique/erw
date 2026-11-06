# Expected: 2001 0.609549, 2025 17.75607, change 17.146521 (percent of US marketed production); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 164): reproduce candidate state_production_share for prod_PA from the ERW's public table.

    python {this file} <eia_gas_production_state_monthly.csv>

A state's marketed gas production as a percent of the US total. A year's figure: the numerator's rows summed times 100.0 over the denominator's rows summed, with the year's count of the numerator's months.
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
num = d[d["entity"].str.contains('^eia_gas_production:SPA:', regex=True) & d["variable"].isin(['marketed_production'])]
den = d[d["entity"].str.contains('^eia_gas_production:NUS:', regex=True) & d["variable"].isin(['marketed_production'])]
for y, s in num.groupby("year"):
    b = den.loc[den["year"] == y, "value"].sum()
    if b != 0:
        print(y, round(float(s["value"].sum() * 100.0 / b), 6), s["ts_utc"].nunique())
