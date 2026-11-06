# Expected: 1973 14.0, 2025 2422.841, change 2408.841 (Bcf); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 164): reproduce candidate mexico_exports for us_mexico from the ERW's public table.

    python {this file} <eia_gas_trade_country_monthly.csv>

US pipeline exports of gas to Mexico over the year. A year's figure: the numerator's rows summed, in Bcf (MMcf over 1,000), with the year's count of the numerator's months.
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
num = d[d["entity"].str.contains('^eia_gas_trade:N9132MX2$', regex=True) & d["variable"].isin(['volume'])]

for y, s in num.groupby("year"):
    print(y, round(float(s["value"].sum() * 1.0 / 1000.0), 6), s["ts_utc"].nunique())
