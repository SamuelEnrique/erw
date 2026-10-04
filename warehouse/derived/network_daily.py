#!/usr/bin/env python3
"""The network's replay: every day since 2019, one file per year (session 93, the network version 3).

Energy Research Warehouse (ERW). Writes, in the shape the network already draws (a frame per day where the live week has
a frame per hour):

    site/public/network/daily_<year>.json        the year's days: each pair's flow, the day's carbon intensity and hub price
    site/public/network/daily_index.json         the first and last day held, the years, and what was left out

from eia930_daily_interchange (EIA-930 daily interchange of every pair, EIA's Eastern day, MWh), carbon_intensity_daily
(the sphere color: the seven ISO balancing authorities) and the real-time price of each ISO's main hub where a public
price is held (the tables the cost of power reads; not PJM's, whose prices are internal).

What a frame holds:
- a pair's flow is the day's MWh over the hours of that Eastern day (24; 23 or 25 on the two days the clocks change):
  the day's average MW, so that a day draws on the scale an hour draws on. Each pair is counted once, by the network's
  own rule (grid_network.RULE): read from the balancing authority whose code sorts first, as it reported it; on a day it
  did not report, from the other's report with the sign flipped. A day neither reported is null, never filled.
- a pair-day that the monthly supply table screens out (ba_supply.screen: further than 10 median absolute deviations, at
  least 500 MWh, from the pair's own median over its history) is null here too, and counted: EIA's daily interchange
  holds days no tie can carry, and one such day would set the scale of a year.
- carbon intensity is that day's (intensity_generation, kg CO2/MWh); where it is not held the sphere is grey.
- a hub price is the mean of the real-time hourly prices of that Eastern day, only when every hour of the day is held.
- demand is not in the file: the warehouse holds no daily demand history, and the page says so.

Node positions and names are the committed snapshot's (site/data/grid_network.json): a balancing authority of the
history that is not in today's network is left out and counted. Nothing is written to warehouse/output: the files are
the site's, like the two stories (network_stories.py).

    python warehouse/derived/network_daily.py [--years 2021 2026]
"""

import argparse
import json
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, HERE)
import ba_supply  # noqa: E402  (screen)
import grid_network as gn  # noqa: E402  (RULE, REGIONS)
import iso_prices as ip  # noqa: E402
import network_stories as ns  # noqa: E402  (hub_prices, HUB_BA)

TABLE = "eia930_daily_interchange"
OUT_DIR = ns.OUT_DIR
TZ = "America/New_York"   # EIA's daily tables are its Eastern day
FIRST_YEAR = 2019


def day_hours(day):
    """The hours of an Eastern day: 24, or 23 or 25 on the days the clocks change."""
    a = pd.Timestamp(day).tz_localize(TZ)
    b = (pd.Timestamp(day) + pd.Timedelta(days=1)).tz_localize(TZ)
    return int(round((b - a) / pd.Timedelta(hours=1)))


def daily_prices(hourly):
    """{BA: {day: mean USD/MWh}} over the Eastern days whose every hour is held."""
    out = {}
    for ba, ser in hourly.items():
        if ser is None or not len(ser):
            continue
        s = pd.Series(ser.values, index=pd.DatetimeIndex(ser.index).tz_convert(TZ)).dropna()
        g = s.groupby(s.index.strftime("%Y-%m-%d"))
        mean, n = g.mean(), g.size()
        out[ba] = {d: round(float(mean[d]), 2) for d in mean.index if n[d] == day_hours(d)}
    return out


def build_year(year, flows, nodes, ci, prices, last_day):
    days = [d.strftime("%Y-%m-%d") for d in pd.date_range(f"{year}-01-01", min(pd.Timestamp(f"{year}-12-31"), pd.Timestamp(last_day)), freq="D")]
    hours = {d: day_hours(d) for d in days}
    f = flows[flows["day"].str[:4] == str(year)]
    by = {}
    for r in f.itertuples():
        by.setdefault((r.fr, r.to), {})[r.day] = (float(r.v), bool(r.bad))
    links, from_other, missing, screened = [], 0, 0, 0
    for p, q in sorted({tuple(sorted(k)) for k in by}):
        own, other = by.get((p, q), {}), by.get((q, p), {})
        mw = []
        for d in days:
            got = own.get(d)
            sign = 1
            if got is None and d in other:
                got, sign = other[d], -1
                from_other += 1
            if got is None:
                mw.append(None)
                missing += 1
            elif got[1]:
                mw.append(None)
                screened += 1
            else:
                mw.append(round(sign * got[0] / hours[d], 1))
        if any(v is not None for v in mw):
            links.append(dict(a=p, b=q, mw=mw))
    intensity = {}
    for ba, g in ci[ci["day"].str[:4] == str(year)].groupby("ba"):
        if ba in nodes:
            m = dict(zip(g["day"], g["value"].astype(float)))
            intensity[ba] = [round(m[d], 2) if d in m else None for d in days]
    hub = {}
    for ba, m in prices.items():
        arr = [m.get(d) for d in days]
        if any(v is not None for v in arr):
            hub[ba] = arr
    return dict(year=year, frame="day", tz=TZ, days=days, built=ip.utc_iso(pd.Timestamp.now(tz="UTC")), rule=gn.RULE, links=links,
                intensity=intensity, hub_prices=hub,
                missing=dict(pair_days=missing, pair_days_from_other_side=from_other, pair_days_screened=screened),
                source=[TABLE, "carbon_intensity_daily", "ercot_all_hub_prices_history", "iso_hub_prices_history", "iso_rtm_hub_prices"])


def main(argv=None):
    ap = argparse.ArgumentParser(description="The network's replay files, one per year since 2019")
    ap.add_argument("--years", nargs="*", type=int)
    a = ap.parse_args(argv)
    base = json.load(open(ns.COMMITTED, encoding="utf-8"))
    nodes = {n["id"] for n in base["nodes"]}
    it = ns.read(TABLE, ["entity", "variable", "ts_utc", "value"])
    it = it[it["variable"] == "interchange_mwh"].assign(v=lambda z: z["value"].astype(float), day=lambda z: z["ts_utc"].str[:10],
                                                        fr=lambda z: z["entity"].str[7:].str.split("-").str[0], to=lambda z: z["entity"].str[7:].str.split("-").str[1])
    it["bad"] = ba_supply.screen(it)
    seen = set(it["fr"]) | set(it["to"])
    left_out = sorted(c for c in seen if c not in nodes and c not in gn.REGIONS)
    flows = it[it["fr"].isin(nodes) & it["to"].isin(nodes)]
    last_day = flows["day"].max()
    ci = ns.read("carbon_intensity_daily", ["entity", "variable", "ts_utc", "value"])
    ci = ci[ci["variable"] == "intensity_generation"].assign(ba=lambda z: z["entity"].str[7:], day=lambda z: z["ts_utc"].str[:10])
    prices = daily_prices(ns.hub_prices())
    os.makedirs(OUT_DIR, exist_ok=True)
    index = dict(first=f"{FIRST_YEAR}-01-01", last=last_day, tz=TZ, frame="day", rule=gn.RULE, years={}, left_out_bas=left_out,
                 built=ip.utc_iso(pd.Timestamp.now(tz="UTC")), source=TABLE)
    for year in range(FIRST_YEAR, int(last_day[:4]) + 1):
        if a.years and year not in a.years:
            continue
        y = build_year(year, flows, nodes, ci, prices, last_day)
        path = os.path.join(OUT_DIR, f"daily_{year}.json")
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(y, f, separators=(",", ":"))
        index["years"][str(year)] = dict(file=f"/network/daily_{year}.json", days=len(y["days"]), first=y["days"][0], last=y["days"][-1], links=len(y["links"]),
                                         priced=sorted(y["hub_prices"]), intensity=sorted(y["intensity"]), **y["missing"])
        print(f"{year}: {len(y['days'])} days, {len(y['links'])} pairs, {y['missing']['pair_days_screened']} pair-days screened, "
              f"{y['missing']['pair_days']} not reported, prices {sorted(y['hub_prices'])}, {os.path.getsize(path) / 1e3:.0f} kB")
    if not a.years:
        with open(os.path.join(OUT_DIR, "daily_index.json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump(index, f, indent=1)
            f.write("\n")
        print(f"index: {index['first']} to {index['last']}, {len(index['years'])} years; left out (not in today's network): {', '.join(left_out) or 'none'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
