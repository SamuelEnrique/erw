# Expected: 2019 15.775663, 2025 12.592394, change -3.18327 (percent); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 502): reproduce candidate region_net for rn_ny from the ERW's public tables.

    python {this file} <eia930_region_hourly.csv> <eia930_ba_demand_hourly.csv>

The year's net imports of New York as a percent of its demand: total interchange from the region table over the demand of the region's authorities summed by hour, hours both are held.
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

d = read(sys.argv[1], ['entity', 'variable', 'ts_utc', 'value'])
d = d[(d['entity'] == 'eia930:NY') & (d['variable'] == 'total_interchange_mw')].copy()
d['ti'] = pd.to_numeric(d['value'], errors='coerce')
w = d.dropna(subset=['ti'])[['ts_utc', 'ti']].copy()
w['year'] = w['ts_utc'].str[:4].astype(int)
w = drop_flow_faults(w, 'ti', ['year'])
w['v'] = w['ti'] * -1
w = w.merge(region_demand(sys.argv[2], 'NY')[['ts_utc', 'demand_mw']], on='ts_utc')
for y, s in w.groupby('year'):
    print(y, round(float(s['v'].sum() / s['demand_mw'].sum() * 100), 6), len(s))
