# Expected: 2015 20.3475, 2025 58.4675, change 38.12 (USD per MWh); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 164): reproduce candidate daily_spread for ercot_HB_WEST from the ERW's public tables.

    python {this file} <ercot_all_hub_prices_history.csv>

The table's CSV as the public download holds it (Redivis), or the ERW's own file with its # comment lines. Prints the
measure by local year (Central time) and the hours or days each year rests on. A full year holds at least 90 percent
of the fullest year's observations and is not the year under way.
"""
import math
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
    return pd.read_csv(path, skiprows=skip, usecols=cols, dtype=str)


def hourly(path, nodes):
    d = read(path, ["ts_utc", "value", "market", "node"])
    d = d[(d["market"] == "ercot_rtm") & d["node"].isin(nodes)].copy()
    d["value"] = pd.to_numeric(d["value"], errors="coerce")
    d = d.dropna(subset=["value"])
    d["hour"] = pd.to_datetime(d["ts_utc"], format="%Y-%m-%dT%H:%M:%SZ", utc=True).dt.floor("h")
    h = d.groupby(["node", "hour"], as_index=False)["value"].mean().rename(columns={"value": "rt"})
    local = h["hour"].dt.tz_convert("America/Chicago")
    h["year"], h["lhour"], h["day"] = local.dt.year, local.dt.hour, local.dt.strftime("%Y-%m-%d")
    return h


def days(h):
    d = h.groupby("day").agg(pmax=("rt", "max"), pmin=("rt", "min"), mean=("rt", "mean"), hours=("rt", "size"), year=("year", "first"))
    d = d[d["hours"] >= 20].copy()
    d["spread"] = d["pmax"] - d["pmin"]
    return d


h = hourly(sys.argv[1], ['HB_WEST'])
out = {}
for y, s in days(h).groupby('year'):
    out[y] = (float(np.median(s['spread'])), len(s))

for y in sorted(out):
    print(y, round(out[y][0], 6), out[y][1])
