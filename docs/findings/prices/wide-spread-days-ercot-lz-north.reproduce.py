# Expected: 2015 20.0, 2025 53.972603, change 33.972603 (percent of days); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 164): reproduce candidate wide_spread_days for ercot_LZ_NORTH from the ERW's public tables.

    python {this file} <ercot_zone_prices_history.csv>

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


h = hourly(sys.argv[1], ['LZ_NORTH'])
out = {}
h = h[h.groupby('day')['rt'].transform('size') >= 20]
d = h.groupby('day').agg(year=('year', 'first'), pmax=('rt', 'max'), pmin=('rt', 'min'))
for y, s in d.groupby('year'):
    out[y] = (100 * ((s['pmax'] - s['pmin']) >= 50.0).mean(), len(s))

for y in sorted(out):
    print(y, round(out[y][0], 6), out[y][1])
