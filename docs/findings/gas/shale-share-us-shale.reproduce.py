# Expected: 2007 8.069148, 2024 76.545041, change 68.475893 (percent of gross withdrawals); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 164): reproduce candidate shale_share for us_shale from the ERW's public table.

    python {this file} <eia_gas_production_state_monthly.csv>

Shale gas as a percent of US gross withdrawals. A year's figure: the numerator's rows summed times 100.0 over the denominator's rows summed, with the year's count of the numerator's months.
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
num = d[d["entity"].str.contains('^eia_gas_production:NUS:', regex=True) & d["variable"].isin(['shale_withdrawals'])]
den = d[d["entity"].str.contains('^eia_gas_production:NUS:', regex=True) & d["variable"].isin(['gross_withdrawals'])]
for y, s in num.groupby("year"):
    b = den.loc[den["year"] == y, "value"].sum()
    if b != 0:
        print(y, round(float(s["value"].sum() * 100.0 / b), 6), s["ts_utc"].nunique())
