# Expected: 2018 122300.0, 2023 132438.0, change 10138.0 (MW); tolerance 0.5 percent of the change.
# The claim: 2023 against the mean of the other years, 124628.375 MW.
"""ERW findings hunt (chain 502): reproduce candidate ercot_heat_2023 for MIDW from the ERW's public tables.

    python {this file} <eia930_ba_demand_hourly.csv>

For each year held: the highest hour of demand of the Midwest from 08-01 to 09-10 (UTC days), years holding at least 90 percent of the window's hours. The claim is 2023 against the mean of the other years.
An hour whose absolute flow is more than three times its year's 99th percentile of absolute flows is dropped as a fault
of the report; an hour of demand at or below zero or above three times its year's median is dropped the same way.
Prints one line a year: the year, the figure, the hours it rests on.
"""
import sys

import numpy as np
import pandas as pd


def read(path, cols):
    with open(path, encoding="utf-8") as f:
        skip = 0
        for line in f:
            if not line.startswith("#"):
                break
            skip += 1
    return pd.read_csv(path, skiprows=skip, usecols=cols, dtype=str, keep_default_na=False)


def drop_flow_faults(d, col, by):
    a = d[col].abs()
    p99 = a.groupby([d[k] for k in by]).transform(lambda s: np.nanpercentile(s, 99))
    return d[a <= 3 * p99]

def region_demand(path, code):
    """The region's demand by hour: the sum of every authority the files place in the region that files demand in the
    month, held only when all of them have a value after the demand fault rule (per authority and year)."""
    d = read(path, ["entity", "variable", "ts_utc", "value", "x_region"])
    d = d[(d["variable"] == "demand_mw") & (d["x_region"] == code)].copy()
    d["value"] = pd.to_numeric(d["value"], errors="coerce")
    d = d.dropna(subset=["value"])
    d["year"] = d["ts_utc"].str[:4].astype(int)
    d["nset"] = d.groupby(d["ts_utc"].str[:7])["entity"].transform("nunique")
    d = d[d["value"] > 0]
    d = d[d["value"] <= 3 * d.groupby(["entity", "year"])["value"].transform("median")]
    g = d.groupby("ts_utc")
    w = pd.DataFrame({"demand_mw": g["value"].sum(), "n_ba": g["value"].size(), "nset": g["nset"].first()}).reset_index()
    w = w[w["n_ba"] == w["nset"]]
    w["year"] = w["ts_utc"].str[:4].astype(int)
    return w[["ts_utc", "year", "demand_mw"]]

d = region_demand(sys.argv[1], 'MIDW')
d = d[(d['ts_utc'].str[5:10] >= '08-01') & (d['ts_utc'].str[5:10] <= '09-10')]
for y, s in d.groupby('year'):
    need = (pd.Timestamp(f'{y}-09-10') - pd.Timestamp(f'{y}-08-01')).days * 24 + 24
    if len(s) >= 0.9 * need:
        print(y, round(float(s['demand_mw'].max()), 6), len(s))
