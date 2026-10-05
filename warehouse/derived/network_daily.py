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
- demand (session 109) is the day's MWh from eia930_daily_demand (EIA's daily demand of every balancing authority, its
  Eastern day) over the hours of that day: the day's average MW, on the scale of the flows, so that a tie's flow over it
  is that supplier's share of the grid's demand that day. A day's demand is used when it is above zero and between half
  and twice the median of the six days around it (three before, three after, those held); a day outside that is null
  and counted. EIA's daily demand is its own sum of the hours it holds, so a day with hours missing or faulty at the
  source can be far off; a day within the band can still hold one faulty hour (docs/methods/impossible_hours.md).

Node positions and names are the committed snapshot's (site/data/grid_network.json): a balancing authority of the
history that is not in today's network is left out and counted. Nothing is written to warehouse/output: the files are
the site's, like the two stories (network_stories.py).

    python warehouse/derived/network_daily.py [--years 2021 2026]
    python warehouse/derived/network_daily.py --daily        # the daily run (session 114)

Session 114, --daily: the replay holds every day to the newest day of eia930_daily_interchange, which the daily run now
extends each day (eia930_daily_interchange.py --days, eia930_daily_demand.py --days; warehouse/run_daily.sh). The daily
build writes the newest year's file (and the year before it during the first week of January, while that year's last
days are still arriving) and the index; the earlier years' files and their index entries stay as they are. Three rules
keep a machine that holds less than this one from writing a poorer file than the one it replaces:
- the files it replaces must be there: it adds days to a replay, it never starts one;
- a hub's price on a day this build cannot compute, and the file held, is kept from the file and counted
  (hub_price_days_kept). The GitHub runner does not hold the ERCOT price history, only the rolling table's recent weeks,
  so Texas's earlier days of the year come from the file the data machine built from the history, by the same rule;
- if, over the days the old file holds, the new one would hold fewer flows, intensities, demands or prices by more
  than one in a hundred, nothing is written and the step fails with the counts.
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
DEMAND = "eia930_daily_demand"   # session 109: EIA's daily demand by balancing authority, the denominator of a share
DEMAND_BAND = (0.5, 2.0)         # a day's demand is used within this band of the median of the six days around it
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


def screened_demand(d):
    """A balancing authority's daily demand (a Series by day, in order): the days used, the others NaN. A day is used when
    it is above zero and within DEMAND_BAND of the median of the six days around it (three before, three after)."""
    v = d.where(d > 0)
    around = pd.concat([v.shift(k) for k in (-3, -2, -1, 1, 2, 3)], axis=1).median(axis=1)
    ok = v.notna() & ~((v < DEMAND_BAND[0] * around) | (v > DEMAND_BAND[1] * around))
    return v.where(ok)


def demand_by_day(table, nodes):
    """{BA: {day: MWh}} of the screened daily demand of the network's nodes, and the count of days screened out."""
    out, screened = {}, 0
    for ba, g in table.groupby("ba"):
        if ba not in nodes:
            continue
        s = g.set_index("day")["v"].sort_index()
        used = screened_demand(s)
        screened += int((s.notna() & used.isna()).sum())
        out[ba] = {d: float(x) for d, x in used.dropna().items()}
    return out, screened


def build_year(year, flows, nodes, ci, prices, last_day, demand=None):
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
    dem, demand_days = {}, 0
    for ba, m in sorted((demand or {}).items()):
        arr = [round(m[d] / hours[d], 1) if d in m else None for d in days]   # the day's average MW, as the flows
        if any(v is not None for v in arr):
            dem[ba] = arr
            demand_days += sum(v is not None for v in arr)
    return dict(year=year, frame="day", tz=TZ, days=days, built=ip.utc_iso(pd.Timestamp.now(tz="UTC")), rule=gn.RULE, links=links,
                intensity=intensity, hub_prices=hub, demand=dem,
                missing=dict(pair_days=missing, pair_days_from_other_side=from_other, pair_days_screened=screened, demand_days_held=demand_days),
                source=[TABLE, DEMAND, "carbon_intensity_daily", "ercot_all_hub_prices_history", "iso_hub_prices_history", "iso_rtm_hub_prices"])


def hub_prices_held():
    """ns.hub_prices on a machine that may lack the ERCOT price history (the GitHub runner): there ERCOT's hub is read from
    the rolling table alone. The other hubs as ns.hub_prices reads them."""
    import cost_of_power as cp
    import price_board as pb
    if os.path.exists(os.path.join(ip.OUT_DIR, pb.HISTORY + ".csv")):
        return ns.hub_prices()
    out = {}
    for iso, ba in ns.HUB_BA.items():
        if iso == "ercot":
            table, market = pb.TABLES[(iso, "rtm")]
            out[ba] = cp.hourly(pb.read_table(table, market=market, node=pb.MAIN[iso]))
        else:
            df, _ = cp.prices_of(iso, "rtm", lambda m: None)
            out[ba] = cp.hourly(df)
    return out


def keep_prices(new, old):
    """A hub's price on a day the new file lacks and the old one holds is kept from the old one. Returns the count kept."""
    at = {d: i for i, d in enumerate(old["days"])}
    kept = 0
    for ba, was in old.get("hub_prices", {}).items():
        arr = new["hub_prices"].setdefault(ba, [None] * len(new["days"]))
        for j, d in enumerate(new["days"]):
            i = at.get(d)
            if arr[j] is None and i is not None and was[i] is not None:
                arr[j] = was[i]
                kept += 1
    return kept


def held(y, days):
    """How many values a year's file holds on these days: flows, intensities, demands and hub prices."""
    idx = [i for i, d in enumerate(y["days"]) if d in days]

    def n(arrs):
        return sum(a[i] is not None for a in arrs for i in idx)
    return dict(flows=n([k["mw"] for k in y["links"]]), intensity=n(list(y["intensity"].values())), demand=n(list(y.get("demand", {}).values())),
                hub_prices=n(list(y["hub_prices"].values())))


def poorer(new, old, share=0.01):
    """The kinds of value of which the new file holds fewer than the old one, over the old file's days, by more than `share`."""
    days = set(old["days"])
    a, b = held(old, days), held(new, days)
    return {k: (a[k], b[k]) for k in a if b[k] < (1 - share) * a[k]}


def main(argv=None):
    ap = argparse.ArgumentParser(description="The network's replay files, one per year since 2019")
    ap.add_argument("--years", nargs="*", type=int)
    ap.add_argument("--daily", action="store_true", help="the daily run: the newest year's file and the index; the earlier years stay (the docstring)")
    a = ap.parse_args(argv)
    if a.daily and a.years:
        ap.error("--daily chooses its own years")
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
    prices = daily_prices(hub_prices_held() if a.daily else ns.hub_prices())
    dm = ns.read(DEMAND, ["entity", "variable", "ts_utc", "value"])
    dm = dm[dm["variable"] == "demand_mwh"].assign(ba=lambda z: z["entity"].str[7:], day=lambda z: z["ts_utc"].str[:10], v=lambda z: z["value"].astype(float))
    demand, demand_screened = demand_by_day(dm, nodes)
    os.makedirs(OUT_DIR, exist_ok=True)
    index = dict(first=f"{FIRST_YEAR}-01-01", last=last_day, tz=TZ, frame="day", rule=gn.RULE, years={}, left_out_bas=left_out,
                 built=ip.utc_iso(pd.Timestamp.now(tz="UTC")), source=TABLE, demand_source=DEMAND, demand_band=list(DEMAND_BAND),
                 demand_days_screened=demand_screened, demand_bas=sorted(demand))
    index_path = os.path.join(OUT_DIR, "daily_index.json")
    if a.daily:
        # the newest year, and the year before it while its last days are still arriving
        a.years = sorted({int(last_day[:4]), (pd.Timestamp(last_day) - pd.Timedelta(days=7)).year})
        was = json.load(open(index_path, encoding="utf-8"))
        index["years"] = {k: v for k, v in was["years"].items() if int(k) not in a.years}
        if was["last"] > last_day:
            raise RuntimeError(f"the replay holds days to {was['last']} and the table only to {last_day}: nothing written")
    built = {}
    for year in range(FIRST_YEAR, int(last_day[:4]) + 1):
        if a.years and year not in a.years:
            continue
        y = build_year(year, flows, nodes, ci, prices, last_day, demand)
        path = os.path.join(OUT_DIR, f"daily_{year}.json")
        if a.daily and (str(year) in was["years"] or os.path.exists(path)):
            # the file it replaces must be there (a missing one the index names fails here); only a new year's first file is started
            old = json.load(open(path, encoding="utf-8"))
            y["missing"]["hub_price_days_kept"] = keep_prices(y, old)
            less = poorer(y, old)
            if less:
                raise RuntimeError(f"daily_{year}.json would hold fewer values than the file it replaces (held, would hold): {less}: nothing written")
        built[year] = (path, y)
    for year, (path, y) in built.items():
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(y, f, separators=(",", ":"))
        index["years"][str(year)] = dict(file=f"/network/daily_{year}.json", days=len(y["days"]), first=y["days"][0], last=y["days"][-1], links=len(y["links"]),
                                         priced=sorted(y["hub_prices"]), intensity=sorted(y["intensity"]), with_demand=len(y["demand"]), **y["missing"])
        print(f"{year}: {len(y['days'])} days, {len(y['links'])} pairs, {y['missing']['pair_days_screened']} pair-days screened, "
              f"{y['missing']['pair_days']} not reported, prices {sorted(y['hub_prices'])}, {os.path.getsize(path) / 1e3:.0f} kB")
    if a.daily:
        index["years"] = dict(sorted(index["years"].items()))
    if a.daily or not a.years:
        with open(index_path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(index, f, indent=1)
            f.write("\n")
        print(f"index: {index['first']} to {index['last']}, {len(index['years'])} years; left out (not in today's network): {', '.join(left_out) or 'none'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
