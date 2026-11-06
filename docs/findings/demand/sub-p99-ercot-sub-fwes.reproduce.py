# Expected: 2020 4337.0, 2025 8763.0, change 4426.0 (MW); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 164): reproduce candidate sub_p99 for ercot_sub_FWES from the ERW's public tables.

    python {this file} <eia930_subba_demand_hourly_2019.csv> ... <eia930_subba_demand_hourly_2025.csv>

The year's 99th-percentile hour of the sub-region's demand, by local year (America/Chicago), for EIA-930 sub-region eia930_subba:ERCO:FWES. An hour at or below zero, or over three times its
year's median, is dropped as a fault of the report.
"""
import sys

import numpy as np
import pandas as pd


def read(path):
    with open(path, encoding="utf-8") as f:
        skip = 0
        for line in f:
            if not line.startswith("#"):
                break
            skip += 1
    d = pd.read_csv(path, skiprows=skip, usecols=["entity", "variable", "ts_utc", "value"], dtype=str)
    return d[(d["entity"] == "eia930_subba:ERCO:FWES") & (d["variable"] == "demand_mw")]


d = pd.concat([read(p) for p in sys.argv[1:]], ignore_index=True).drop_duplicates(["entity", "ts_utc"])
d["value"] = pd.to_numeric(d["value"], errors="coerce")
d = d[d["value"] > 0].copy()
local = pd.to_datetime(d["ts_utc"], format="%Y-%m-%dT%H:%M:%SZ", utc=True).dt.tz_convert("America/Chicago")
d["year"], d["lhour"] = local.dt.year, local.dt.hour
med = d.groupby("year")["value"].transform("median")
d = d[d["value"] <= med * 3]
for y, s in d.groupby("year"):
    if 2019 <= y <= 2025:
        print(y, round(float(np.percentile(s['value'], 99, method='averaged_inverted_cdf')), 6), len(s))
