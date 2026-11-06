# Expected: 2015 67.888128, 2025 60.856164, change -7.031963 (percent of hours); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 164): reproduce candidate da_above_rt_share for ercot_LZ_SOUTH from the ERW's public table.

    python {this file} <ercot_zone_prices_history.csv>

The share of the year's hours (local year, Central time) in which the day-ahead price was above the hour's real-time
price (the mean of its real-time intervals). The table's CSV as the public download holds it, or the ERW's own file.
"""
import sys

import pandas as pd


def read(path, cols):
    with open(path, encoding="utf-8") as f:
        skip = 0
        for line in f:
            if not line.startswith("#"):
                break
            skip += 1
    return pd.read_csv(path, skiprows=skip, usecols=cols, dtype=str)


d = read(sys.argv[1], ["ts_utc", "value", "market", "node"])
d = d[d["market"].isin(["ercot_rtm", "ercot_dam"]) & (d["node"] == 'LZ_SOUTH')].copy()
d["value"] = pd.to_numeric(d["value"], errors="coerce")
d = d.dropna(subset=["value"])
d["hour"] = pd.to_datetime(d["ts_utc"], format="%Y-%m-%dT%H:%M:%SZ", utc=True).dt.floor("h")
d["kind"] = d["market"].str[-3:]
w = d.groupby(["kind", "hour"])["value"].mean().unstack("kind").dropna()
w["year"] = w.index.tz_convert("America/Chicago").year
out = {}
for y, s in w.groupby("year"):
    out[y] = (100 * (s["dam"] > s["rtm"]).mean(), len(s))
for y in sorted(out):
    print(y, round(out[y][0], 6), out[y][1])
