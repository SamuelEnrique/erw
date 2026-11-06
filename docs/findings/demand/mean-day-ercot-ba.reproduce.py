# Expected: 2019 1051.1418, 2025 1339.171978, change 288.030178 (GWh a day); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 164): reproduce candidate mean_day for ercot_ba from the ERW's public table.

    python {this file} <eia930_daily_demand.csv>

The year's mean day of demand, by calendar year, for EIA-930 respondent ERCO. A day under a third or over three times its year's median is
dropped as a fault of the report (the weekly hunt's rule).
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
d = d[(d["entity"] == "eia930:ERCO") & (d["variable"] == "demand_mwh")].copy()
d["value"] = pd.to_numeric(d["value"], errors="coerce")
d = d[d["value"] > 0].drop_duplicates(["entity", "ts_utc"])
d["year"], d["month"] = d["ts_utc"].str[:4].astype(int), d["ts_utc"].str[5:7].astype(int)
med = d.groupby("year")["value"].transform("median")
d = d[(d["value"] >= med / 3) & (d["value"] <= med * 3)]
for y, s in d.groupby("year"):
    print(y, round(float(s['value'].mean() / 1000), 6), len(s))
