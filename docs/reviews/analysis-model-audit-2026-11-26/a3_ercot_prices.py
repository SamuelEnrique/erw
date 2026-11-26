"""Audit of Automated Analysis (session 10204): drafts 4, 5, 6 and 20 of the sheet re-done by hand from ERCOT's prices,
then each measure's choice changed one at a time.

Reads (never writes) the main checkout's tables, in chunks, one node at a time:
  ercot_zone_prices_history.csv  LZ_WEST, market ercot_rtm   (drafts 4 midday, 20 wide-spread days)
  ercot_all_hub_prices_history.csv  HB_SOUTH (draft 5 evening), HB_NORTH (draft 6 cheapest hour)
An hour's price is the mean of its real-time intervals (UTC hour floor), labelled in Central time, as the drafts say.

Run: python runs/a3_ercot_prices.py <folder of the tables> > runs/a3.out
"""
import math
import os
import sys

import numpy as np
import pandas as pd

D = sys.argv[1]


def skip_of(path):
    n = 0
    with open(path, encoding="utf-8") as f:
        for ln in f:
            if not ln.startswith("#"):
                return n
            n += 1


def node_hours(table, node):
    path = os.path.join(D, table + ".csv")
    parts = []
    for ch in pd.read_csv(path, skiprows=skip_of(path), usecols=["ts_utc", "value", "market", "node"], dtype=str, chunksize=1_000_000):
        ch = ch[(ch["market"] == "ercot_rtm") & (ch["node"] == node)]
        if len(ch):
            parts.append(ch[["ts_utc", "value"]])
    d = pd.concat(parts, ignore_index=True)
    d["value"] = pd.to_numeric(d["value"], errors="coerce")
    d = d.dropna(subset=["value"])
    d["hour"] = pd.to_datetime(d["ts_utc"], format="%Y-%m-%dT%H:%M:%SZ", utc=True).dt.floor("h")
    h = d.groupby("hour", as_index=False)["value"].mean().rename(columns={"value": "rt"})
    loc = h["hour"].dt.tz_convert("America/Chicago")
    h["year"], h["lhour"], h["day"] = loc.dt.year, loc.dt.hour, loc.dt.strftime("%Y-%m-%d")
    return h[h["year"] <= 2025]


def ratio(h, lo, hi, trim=0.0, how="mean"):
    out = {}
    for y, s in h.groupby("year"):
        if trim:
            k = int(math.ceil(trim * len(s)))
            s = s.drop(s["rt"].nlargest(k).index)
        f = (lambda v: v.median()) if how == "median" else (lambda v: v.mean())
        out[y] = 100 * f(s.loc[s["lhour"].between(lo, hi), "rt"]) / f(s["rt"])
    return out


def show(name, d):
    print(name + ": " + ", ".join(f"{y} {v:.4f}" for y, v in sorted(d.items())))


def days(h):
    h = h[h.groupby("day")["rt"].transform("size") >= 20]
    return h


def main():
    w = node_hours("ercot_zone_prices_history", "LZ_WEST")
    print("LZ_WEST hours by year: " + ", ".join(f"{y} {n}" for y, n in w.groupby("year").size().items()))
    show("draft 4 midday (11 to 15) mean / all-hours mean, percent", ratio(w, 11, 15))
    show("  the same with medians", ratio(w, 11, 15, how="median"))
    show("  the same, means, the year's dearest 1 percent of hours left out", ratio(w, 11, 15, trim=0.01))
    # who carries the all-hours mean: the share of the year's price sum in its dearest 1 percent of hours
    print("  LZ_WEST share of the year's summed price in its dearest 1 percent of hours: " + ", ".join(
        f"{y} {100 * s['rt'].nlargest(int(math.ceil(0.01 * len(s)))).sum() / s['rt'].sum():.2f}" for y, s in w.groupby("year")))
    wd = days(w).groupby("day").agg(year=("year", "first"), pmax=("rt", "max"), pmin=("rt", "min"))
    wd["spread"] = wd["pmax"] - wd["pmin"]
    show("draft 20 wide-spread days (spread >= USD 50 nominal), percent of days", {y: 100 * (s["spread"] >= 50).mean() for y, s in wd.groupby("year")})
    show("  the line held at USD 50 of 2025, assumed 2.5 percent a year inflation (USD 39.06 in 2015)",
         {y: 100 * (s["spread"] >= 50 / 1.025 ** (2025 - y)).mean() for y, s in wd.groupby("year")})
    print("  days by year: " + ", ".join(f"{y} {len(s)}" for y, s in wd.groupby("year")))
    del w, wd

    s_ = node_hours("ercot_all_hub_prices_history", "HB_SOUTH")
    show("draft 5 evening (17 to 21) mean / all-hours mean, percent", ratio(s_, 17, 21))
    show("  the same with medians", ratio(s_, 17, 21, how="median"))
    show("  the same, means, the year's dearest 1 percent of hours left out", ratio(s_, 17, 21, trim=0.01))
    del s_

    n_ = node_hours("ercot_all_hub_prices_history", "HB_NORTH")
    n_ = days(n_.sort_values("hour"))
    m = n_.loc[n_.groupby("day")["rt"].idxmin()]
    show("draft 6 cheapest hour: the mean local clock hour of the day's lowest price", {y: s["lhour"].mean() for y, s in m.groupby("year")})
    show("  the median hour", {y: float(s["lhour"].median()) for y, s in m.groupby("year")})

    def circ(v):
        a = np.angle(np.exp(2j * np.pi * v.to_numpy() / 24).mean()) * 24 / (2 * np.pi)
        return a % 24
    show("  the circular mean hour (23:00 and 01:00 average to midnight, not noon)", {y: circ(s["lhour"]) for y, s in m.groupby("year")})
    show("  share of days whose cheapest hour is 21:00 to 02:59 (where a plain mean of the clock misleads)",
         {y: 100 * s["lhour"].isin([21, 22, 23, 0, 1, 2]).mean() for y, s in m.groupby("year")})
    print("  days by year: " + ", ".join(f"{y} {len(s)}" for y, s in m.groupby("year")))


if __name__ == "__main__":
    main()
