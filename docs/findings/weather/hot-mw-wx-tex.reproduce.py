# Expected: 2019 72017.46, 2024 83437.06, change 11419.6 (MW); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 502): reproduce candidate hot_mw for wx_tex from the ERW's public tables.

    python {this file} <region_weather_hourly.csv> <eia930_ba_demand_hourly.csv>

The mean demand (MW) in the year's 50 hottest hours by the region's temperature, Texas; hours both tables hold; ties broken by the hour.
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

w = read(sys.argv[1], ['entity', 'variable', 'ts_utc', 'value'])
w = w[(w['entity'] == 'eia930:TEX') & (w['variable'] == 'temperature_f')].copy()
w['temp'] = pd.to_numeric(w['value'], errors='coerce')
w = w.dropna(subset=['temp'])
s_all = region_demand(sys.argv[2], 'TEX').merge(w[['ts_utc', 'temp']], on='ts_utc')
for y, s in s_all.groupby('year'):
    print(y, round(float(s.sort_values(['temp', 'ts_utc'], ascending=[False, True]).head(50)['demand_mw'].mean()), 6), len(s))
