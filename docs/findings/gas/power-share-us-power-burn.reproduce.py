# Expected: 2001 24.022625, 2025 38.949701, change 14.927076 (percent of consumption); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 164): reproduce candidate power_share for us_power_burn from the ERW's public table.

    python {this file} <gas_balance_weekly.csv>

Gas burned for power as a percent of US gas consumption over the year. A year's figure: the numerator's rows summed times 100.0 over the denominator's rows summed, with the year's count of the numerator's months.
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
num = d[d["entity"].str.contains('^gas_balance:US$', regex=True) & d["variable"].isin(['power_burn'])]
den = d[d["entity"].str.contains('^gas_balance:US$', regex=True) & d["variable"].isin(['consumption'])]
for y, s in num.groupby("year"):
    b = den.loc[den["year"] == y, "value"].sum()
    if b != 0:
        print(y, round(float(s["value"].sum() * 100.0 / b), 6), s["ts_utc"].nunique())
