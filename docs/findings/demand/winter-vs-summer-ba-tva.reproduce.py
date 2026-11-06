# Expected: 2019 101.176554, 2025 113.876102, change 12.699548 (percent of the summer top days); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 164): reproduce candidate winter_vs_summer for ba_tva from the ERW's public table.

    python {this file} <eia930_daily_demand.csv>

The mean of the year's five highest winter days (January, February, December) as a percent of its five highest summer days (June to August), by calendar year, for EIA-930 respondent TVA. A day under a third or over three times its year's median is
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
d = d[(d["entity"] == "eia930:TVA") & (d["variable"] == "demand_mwh")].copy()
d["value"] = pd.to_numeric(d["value"], errors="coerce")
d = d[d["value"] > 0].drop_duplicates(["entity", "ts_utc"])
d["year"], d["month"] = d["ts_utc"].str[:4].astype(int), d["ts_utc"].str[5:7].astype(int)
med = d.groupby("year")["value"].transform("median")
d = d[(d["value"] >= med / 3) & (d["value"] <= med * 3)]
for y, s in d.groupby("year"):
    w = s.loc[s['month'].isin([1, 2, 12]), 'value'].nlargest(5)
    m = s.loc[s['month'].isin([6, 7, 8]), 'value'].nlargest(5)
    if len(w) == 5 and len(m) == 5:
        print(y, round(float(100 * w.mean() / m.mean()), 6), len(s))
