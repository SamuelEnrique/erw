#!/usr/bin/env python3
"""The findings hunt over the whole warehouse (chain 164), family "prices": session 3001.

Energy Research Warehouse (ERW). Plan: docs/reviews/findings-hunt-plan-2026-11-06.md. Each candidate is a measure by
region and local year computed from the ERW's hourly price tables, tested by the weekly hunt's claim and five tests
(builder.py). The weekly hunt already asks the dearest interval, hours above USD 1,000, the hours gas sets the price,
negative hours, the peak hour's part of the day, the implied heat rate and the median hour's day-ahead to real-time
spread (hunt.py --list); none of those is asked again here.

Only ERCOT holds the years: its hubs and load zones from 2015 (ercot_all_hub_prices_history, ercot_zone_prices_history,
public). CAISO's hubs hold three full years (2023 to 2025) and the hunt's window test needs four; PJM's hub history is
not held; ISO-NE, MISO, NYISO and SPP need a license or are held. The hourly rows are the weekly hunt's own
(hunt_measures.ercot_prices: the mean of an hour's real-time intervals, the local year and clock hour in Central time).

    python warehouse/analysis/findings/deep/prices.py --dry-run     # test every candidate, build the drafts, load nothing
    python warehouse/analysis/findings/deep/prices.py --load        # the same, and add the drafts to the review list
"""

import argparse
import math
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..")))
sys.path.insert(0, HERE)
import builder  # noqa: E402
import hunt_measures as hm  # noqa: E402

FAMILY = "prices"
MIDDAY = (11, 15)                  # local clock hours 11 to 15: 11 AM to 4 PM, the hunt's midday
EVENING = hm.EVENING               # local clock hours 17 to 21: 5 PM to 10 PM
TOP_DAYS = 0.10                    # the top tenth of a year's days by their spread
TOP_HOURS = 0.01                   # the dearest hundredth of a year's hours
HEAT_RATE = 7.0                    # MMBtu per MWh, the gas_sets_price finding's standard heat rate
MIN_DAY_HOURS = 20                 # a day with at least 20 of its hours held, as the hunt's implied heat rate
ZONES = {"LZ_HOUSTON": "Houston load zone", "LZ_NORTH": "North load zone", "LZ_SOUTH": "South load zone", "LZ_WEST": "West load zone",
         "LZ_AEN": "Austin Energy load zone", "LZ_CPS": "CPS Energy load zone", "LZ_LCRA": "LCRA load zone", "LZ_RAYBN": "Rayburn load zone"}


def nodes(in_dir, hubs=True, zones=True):
    """[(region, words, node, hourly rows, table)] for ERCOT's hubs and load zones (not the bus average)."""
    e = hm.ercot_prices(in_dir)
    out = []
    for node, g in e.groupby("node"):
        if node in hm.ERCOT_HUBS and hubs:
            out.append((f"ercot_{node}", f"ERCOT's {hm.ERCOT_HUBS[node]} ({node})", node, g, "ercot_all_hub_prices_history"))
        elif node in ZONES and zones:
            out.append((f"ercot_{node}", f"ERCOT's {ZONES[node]} ({node})", node, g, "ercot_zone_prices_history"))
    return out


def _rt(g):
    return g.dropna(subset=["rt"])


def _days(g):
    d = _rt(g).groupby("day").agg(pmax=("rt", "max"), pmin=("rt", "min"), mean=("rt", "mean"), hours=("rt", "size"), year=("year", "first"))
    d = d[d["hours"] >= MIN_DAY_HOURS].copy()
    d["spread"] = d["pmax"] - d["pmin"]
    return d


def midday_discount(in_dir=None):
    rows, tables = [], {}
    for region, words, node, g, tbl in nodes(in_dir):
        for y, s in _rt(g).groupby("year"):
            m = s["rt"].mean()
            rows.append(hm._row(region, words, y, float(100 * s.loc[s["lhour"].between(*MIDDAY), "rt"].mean() / m) if m > 0 else None, len(s)))
        tables[region] = [tbl]
    return {"rows": rows, "tables": tables}


def evening_premium(in_dir=None):
    rows, tables = [], {}
    for region, words, node, g, tbl in nodes(in_dir):
        for y, s in _rt(g).groupby("year"):
            m = s["rt"].mean()
            rows.append(hm._row(region, words, y, float(100 * s.loc[s["lhour"].between(*EVENING), "rt"].mean() / m) if m > 0 else None, len(s)))
        tables[region] = [tbl]
    return {"rows": rows, "tables": tables}


def daily_spread(in_dir=None):
    rows, tables = [], {}
    for region, words, node, g, tbl in nodes(in_dir):
        for y, s in _days(g).groupby("year"):
            rows.append(hm._row(region, words, y, float(np.median(s["spread"])), len(s)))
        tables[region] = [tbl]
    return {"rows": rows, "tables": tables}


def top_days_share(in_dir=None):
    rows, tables = [], {}
    for region, words, node, g, tbl in nodes(in_dir):
        for y, s in _days(g).groupby("year"):
            k = int(math.ceil(TOP_DAYS * len(s)))
            tot = s["spread"].sum()
            rows.append(hm._row(region, words, y, float(100 * s["spread"].nlargest(k).sum() / tot) if tot > 0 else None, len(s)))
        tables[region] = [tbl]
    return {"rows": rows, "tables": tables}


def top_hours_share(in_dir=None):
    rows, tables = [], {}
    for region, words, node, g, tbl in nodes(in_dir):
        for y, s in _rt(g).groupby("year"):
            k = int(math.ceil(TOP_HOURS * len(s)))
            tot = s["rt"].sum()
            rows.append(hm._row(region, words, y, float(100 * s["rt"].nlargest(k).sum() / tot) if tot > 0 else None, len(s)))
        tables[region] = [tbl]
    return {"rows": rows, "tables": tables}


def hub_basis(in_dir=None):
    """The hour's real-time price at a hub minus the North hub's, the year's mean, for the West, Houston and South hubs."""
    e = hm.ercot_prices(in_dir)
    north = _rt(e[e["node"] == "HB_NORTH"]).set_index("hour")["rt"]
    rows, tables = [], {}
    for node in ("HB_WEST", "HB_HOUSTON", "HB_SOUTH"):
        g = _rt(e[e["node"] == node]).set_index("hour")
        g = g.join(north.rename("north"), how="inner")
        region, words = f"ercot_{node}_north", f"ERCOT's {hm.ERCOT_HUBS[node]} ({node}) against the North hub (HB_NORTH)"
        for y, s in g.groupby("year"):
            rows.append(hm._row(region, words, y, float((s["rt"] - s["north"]).mean()), len(s)))
        tables[region] = ["ercot_all_hub_prices_history"]
    return {"rows": rows, "tables": tables}


def _henry_hub(in_dir):
    gas = hm.series("eia_fuel_spot_prices", in_dir, variables=["spot_price"], entities=["eia:henry_hub"])
    return {t.strftime("%Y-%m-%d"): v for t, v in zip(gas["ts"], gas["value"]) if v > 0}


def spark_spread(in_dir=None):
    """The day's mean real-time price minus 7.0 MMBtu per MWh times that day's Henry Hub spot price, the year's mean."""
    hh = _henry_hub(in_dir)
    rows, tables = [], {}
    for region, words, node, g, tbl in nodes(in_dir, zones=False):
        d = _days(g)
        d["hh"] = d.index.map(hh)
        d = d.dropna(subset=["hh"])
        for y, s in d.groupby("year"):
            rows.append(hm._row(region, words, y, float((s["mean"] - HEAT_RATE * s["hh"]).mean()), len(s)))
        tables[region] = [tbl, "eia_fuel_spot_prices"]
    return {"rows": rows, "tables": tables}


def hour_to_hour_move(in_dir=None):
    """The median of the absolute change of the real-time price from one hour to the next (consecutive hours only)."""
    rows, tables = [], {}
    one = pd.Timedelta(hours=1)
    for region, words, node, g, tbl in nodes(in_dir):
        s = _rt(g).sort_values("hour")
        ok = s["hour"].diff() == one
        m = s.assign(move=s["rt"].diff().abs())[ok]
        for y, t in m.groupby("year"):
            rows.append(hm._row(region, words, y, float(np.median(t["move"])), len(t)))
        tables[region] = [tbl]
    return {"rows": rows, "tables": tables}


# ---------------------------------------------------------------------------------------------------------------------
# the reproduction scripts: Python and Stata, from the tables as the public downloads hold them
# ---------------------------------------------------------------------------------------------------------------------
PY_HEAD = '''"""ERW findings hunt (chain 164): reproduce candidate {name} for {region} from the ERW's public tables.

    python {{this file}} <{table}.csv>{extra_arg}

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
    h = d.groupby(["node", "hour"], as_index=False)["value"].mean().rename(columns={{"value": "rt"}})
    local = h["hour"].dt.tz_convert("America/Chicago")
    h["year"], h["lhour"], h["day"] = local.dt.year, local.dt.hour, local.dt.strftime("%Y-%m-%d")
    return h


def days(h):
    d = h.groupby("day").agg(pmax=("rt", "max"), pmin=("rt", "min"), mean=("rt", "mean"), hours=("rt", "size"), year=("year", "first"))
    d = d[d["hours"] >= 20].copy()
    d["spread"] = d["pmax"] - d["pmin"]
    return d


h = hourly(sys.argv[1], {nodes!r})
out = {{}}
'''

PY_TAIL = '''
for y in sorted(out):
    print(y, round(out[y][0], 6), out[y][1])
'''

PY_MEASURE = {
    "midday_discount": "for y, s in h.groupby('year'):\n    out[y] = (100 * s.loc[s['lhour'].between(11, 15), 'rt'].mean() / s['rt'].mean(), len(s))\n",
    "evening_premium": "for y, s in h.groupby('year'):\n    out[y] = (100 * s.loc[s['lhour'].between(17, 21), 'rt'].mean() / s['rt'].mean(), len(s))\n",
    "daily_spread": "for y, s in days(h).groupby('year'):\n    out[y] = (float(np.median(s['spread'])), len(s))\n",
    "top_days_share": "for y, s in days(h).groupby('year'):\n    k = int(math.ceil(0.10 * len(s)))\n    out[y] = (100 * s['spread'].nlargest(k).sum() / s['spread'].sum(), len(s))\n",
    "top_hours_share": "for y, s in h.groupby('year'):\n    k = int(math.ceil(0.01 * len(s)))\n    out[y] = (100 * s['rt'].nlargest(k).sum() / s['rt'].sum(), len(s))\n",
    "hour_to_hour_move": ("h = h.sort_values('hour')\nh['move'] = h['rt'].diff().abs()\nh = h[h['hour'].diff() == pd.Timedelta(hours=1)]\n"
                          "for y, s in h.groupby('year'):\n    out[y] = (float(np.median(s['move'])), len(s))\n"),
    "hub_basis": ("w = h.pivot_table(index='hour', columns='node', values='rt').dropna()\n"
                  "w = w.join(h.drop_duplicates('hour').set_index('hour')[['year']])\n"
                  "for y, s in w.groupby('year'):\n    out[y] = (float((s[NODE] - s['HB_NORTH']).mean()), len(s))\n"),
    "spark_spread": ("g = read(sys.argv[2], ['entity', 'variable', 'ts_utc', 'value'])\n"
                     "g = g[(g['entity'] == 'eia:henry_hub') & (g['variable'] == 'spot_price')].copy()\n"
                     "g['value'] = pd.to_numeric(g['value'], errors='coerce')\ng = g[g['value'] > 0]\n"
                     "hh = dict(zip(g['ts_utc'].str[:10], g['value']))\n"
                     "d = days(h)\nd['hh'] = d.index.map(hh)\nd = d.dropna(subset=['hh'])\n"
                     "for y, s in d.groupby('year'):\n    out[y] = (float((s['mean'] - 7.0 * s['hh']).mean()), len(s))\n"),
}


def _nodes_of(name, region):
    node = region[len("ercot_"):]
    if name == "hub_basis":
        node = node[: -len("_north")]
        return [node, "HB_NORTH"], node
    return [node], node


def reproduce_py(name, region):
    nodes_, node = _nodes_of(name, region)
    table = "ercot_zone_prices_history" if node.startswith("LZ_") else "ercot_all_hub_prices_history"
    extra = " <eia_fuel_spot_prices.csv>" if name == "spark_spread" else ""
    text = PY_HEAD.format(name=name, region=region, table=table, extra_arg=extra, nodes=nodes_)
    if name == "hub_basis":
        text += f"NODE = {node!r}\n"
    return text + PY_MEASURE[name] + PY_TAIL


def _do_hourly(table, nodes_):
    keep = " | ".join(f'node == "{n}"' for n in nodes_)
    return [
        "* Input: the table's CSV as the public download holds it (Redivis: the variable names on its first line). From the ERW's own file, delete its lines that begin with # first.",
        "clear all",
        f'import delimited "{table}.csv", varnames(1) stringcols(_all) clear',
        f'keep if market == "ercot_rtm" & ({keep})',
        "destring value, replace force",
        "drop if missing(value)",
        'generate double t_utc = clock(subinstr(subinstr(ts_utc, "T", " ", 1), "Z", "", 1), "YMDhms")',
        "generate double hour_utc = floor(t_utc / msofhours(1)) * msofhours(1)",
        "collapse (mean) rt = value, by(node hour_utc)",
        "* Central time: standard is UTC minus 6 hours; daylight time from the second Sunday of March 08:00 UTC to the first Sunday of November 07:00 UTC.",
        "generate int y_utc = year(dofc(hour_utc))",
        "generate int mar1 = mdy(3, 1, y_utc)",
        "generate int dst_start = mar1 + mod(7 - dow(mar1), 7) + 7",
        "generate int nov1 = mdy(11, 1, y_utc)",
        "generate int dst_end = nov1 + mod(7 - dow(nov1), 7)",
        "generate byte dst = hour_utc >= cofd(dst_start) + msofhours(8) & hour_utc < cofd(dst_end) + msofhours(7)",
        "generate double t_local = hour_utc - msofhours(6) + dst * msofhours(1)",
        "generate int year = year(dofc(t_local))",
        "generate int lhour = hh(t_local)",
        "generate long day = dofc(t_local)",
    ]


DO_DAYS = ["collapse (max) pmax = rt (min) pmin = rt (mean) pmean = rt (count) hours = rt (firstnm) year, by(day)",
           "keep if hours >= 20", "generate double spread = pmax - pmin"]
DO_MEASURE = {
    "midday_discount": ["generate double mid = rt if inrange(lhour, 11, 15)",
                        "collapse (mean) all_mean = rt (mean) mid_mean = mid (count) n = rt, by(year)",
                        "generate double measure = 100 * mid_mean / all_mean"],
    "evening_premium": ["generate double eve = rt if inrange(lhour, 17, 21)",
                        "collapse (mean) all_mean = rt (mean) eve_mean = eve (count) n = rt, by(year)",
                        "generate double measure = 100 * eve_mean / all_mean"],
    "daily_spread": DO_DAYS + ["collapse (median) measure = spread (count) n = spread, by(year)"],
    "top_days_share": DO_DAYS + ["generate double neg_spread = -spread", "bysort year (neg_spread): generate long rank = _n", "by year: generate long n = _N",
                                 "by year: egen double total = total(spread)", "by year: egen double top = total(cond(rank <= ceil(0.10 * n), spread, .))",
                                 "by year: keep if _n == 1", "generate double measure = 100 * top / total"],
    "top_hours_share": ["generate double neg_rt = -rt", "bysort year (neg_rt): generate long rank = _n", "by year: generate long n = _N",
                        "by year: egen double total = total(rt)", "by year: egen double top = total(cond(rank <= ceil(0.01 * n), rt, .))",
                        "by year: keep if _n == 1", "generate double measure = 100 * top / total"],
    "hour_to_hour_move": ["sort hour_utc", "generate double move = abs(rt - rt[_n - 1]) if hour_utc - hour_utc[_n - 1] == msofhours(1)",
                          "drop if missing(move)", "collapse (median) measure = move (count) n = move, by(year)"],
}


def _do_basis(node):
    return ["keep node hour_utc rt year", "reshape wide rt, i(hour_utc) j(node) string", f"generate double diff = rt{node} - rtHB_NORTH",
            "drop if missing(diff)", "bysort hour_utc: keep if _n == 1",
            "collapse (mean) measure = diff (count) n = diff, by(year)"]


DO_SPARK = ["save hourly_prices, replace", "clear",
            'import delimited "eia_fuel_spot_prices.csv", varnames(1) stringcols(_all) clear',
            'keep if entity == "eia:henry_hub" & variable == "spot_price"', "destring value, replace force", "keep if value > 0 & !missing(value)",
            'generate long day = daily(substr(ts_utc, 1, 10), "YMD")', "keep day value", "rename value hh", "save henry_hub, replace",
            "use hourly_prices, clear"] + DO_DAYS + ["merge 1:1 day using henry_hub, keep(match) nogenerate",
                                                      "generate double spark = pmean - 7.0 * hh", "collapse (mean) measure = spark (count) n = spark, by(year)"]


def reproduce_do(name, region):
    import findings_common as common
    nodes_, node = _nodes_of(name, region)
    table = "ercot_zone_prices_history" if node.startswith("LZ_") else "ercot_all_hub_prices_history"
    lines = [f"* ERW findings hunt (chain 164): reproduce candidate {name} for {region} from the ERW's public tables."] + _do_hourly(table, nodes_)
    if name == "hub_basis":
        lines = lines[:-3] + ["generate int year = year(dofc(t_local))"] + _do_basis(node)
    elif name == "spark_spread":
        lines += DO_SPARK
    else:
        lines += DO_MEASURE[name]
    lines += ["sort year", "list year measure n, noobs"]
    return common.do_file(lines)


def reproduce(name):
    return lambda region: {"py": reproduce_py(name, region), "do": reproduce_do(name, region)}


# ---------------------------------------------------------------------------------------------------------------------
# the candidates
# ---------------------------------------------------------------------------------------------------------------------
C = builder.candidate
CANDIDATES = [
    C("midday_discount", FAMILY, midday_discount, "percent of the all-hours mean", 1, 8000, 5.0, "THE MIDDAY PRICE",
      "the mean real-time price from 11 AM to 4 PM local as a percent of the year's all-hours mean",
      lambda w: f"the midday real-time price at {w}",
      "A ratio of two means: a year whose all-hours mean is lifted by a few scarcity hours shows a lower midday percent without any change at midday.",
      reproduce("midday_discount"), consequence=3),
    C("evening_premium", FAMILY, evening_premium, "percent of the all-hours mean", 1, 8000, 5.0, "THE EVENING PRICE",
      "the mean real-time price from 5 PM to 10 PM local as a percent of the year's all-hours mean",
      lambda w: f"the evening real-time price at {w}",
      "A ratio of two means: a few evening scarcity hours can carry most of a year's premium, and the measure does not say how many.",
      reproduce("evening_premium"), consequence=3),
    C("daily_spread", FAMILY, daily_spread, "USD per MWh", 2, 330, 5.0, "THE DAILY PRICE SPREAD",
      "the median day's highest hourly real-time price minus its lowest",
      lambda w: f"the median day's spread between the highest and the lowest hourly real-time price at {w}",
      "Nominal dollars, not adjusted for inflation; a spread a battery could capture only in part (it charges and discharges over hours, not one hour each).",
      reproduce("daily_spread"), consequence=3),
    C("top_days_share", FAMILY, top_days_share, "percent", 1, 330, 5.0, "THE DAYS THAT CARRY THE SPREAD",
      "the share of the sum of the year's daily price spreads that falls on its top tenth of days",
      lambda w: f"the share of the year's summed daily price spread at {w} that fell on its top tenth of days",
      "A share of a sum of daily spreads in one hour each; it says how concentrated the spread is, not how much any asset earned.",
      reproduce("top_days_share"), consequence=2),
    C("top_hours_share", FAMILY, top_hours_share, "percent", 1, 8000, 5.0, "THE DEAREST HOURS",
      "the share of the sum of the year's hourly real-time prices that falls in its dearest one percent of hours",
      lambda w: f"the share of a flat one-MWh-an-hour revenue at {w} earned in the year's dearest one percent of hours",
      "Nominal prices; negative hours lower the year's sum and so raise the share, and the measure does not separate the two.",
      reproduce("top_hours_share"), consequence=3),
    C("hub_basis", FAMILY, hub_basis, "USD per MWh", 2, 8000, 1.0, "THE HUB BASIS",
      "the year's mean of the hourly real-time price at the hub minus the North hub's",
      lambda w: f"the mean hourly real-time price difference of {w}",
      "A mean over hours: a few congested hours can move it, and it is not a congestion rent or a transmission cost.",
      reproduce("hub_basis"), consequence=3),
    C("spark_spread", FAMILY, spark_spread, "USD per MWh", 2, 200, 3.0, "THE SPARK SPREAD",
      "the year's mean of the day's mean real-time price minus 7.0 MMBtu per MWh times that day's Henry Hub spot price",
      lambda w: f"the mean daily spark spread at {w} against Henry Hub at a 7.0 heat rate",
      "Henry Hub is a Louisiana price, not the gas a Texas plant buys; the heat rate is a standard, not a plant's; days without a Henry Hub close are left out.",
      reproduce("spark_spread"), consequence=3),
    C("hour_to_hour_move", FAMILY, hour_to_hour_move, "USD per MWh", 2, 8000, 0.5, "THE HOUR-TO-HOUR MOVE",
      "the median absolute change of the real-time price from one hour to the next",
      lambda w: f"the median absolute hour-to-hour move of the real-time price at {w}",
      "A median of hourly moves in nominal dollars; it says how the typical hour moves, not how the rare spike does.",
      reproduce("hour_to_hour_move"), consequence=2),
]



def area(region):
    """The place a region names: a hub and the load zone of one name are one area (ercot_HB_WEST, ercot_LZ_WEST and
    ercot_HB_WEST_north are WEST)."""
    r = region[len("ercot_"):].replace("_north", "")
    return r.split("_", 1)[1] if r[:3] in ("HB_", "LZ_") else r


for _P in CANDIDATES:
    _P["area"] = area


def main(argv=None):
    ap = argparse.ArgumentParser(description="The findings hunt, family prices (chain 164)")
    ap.add_argument("--in-dir", default=None)
    ap.add_argument("--only", default=None, help="a candidate's name")
    ap.add_argument("--replace", action="store_true", help="correct the open drafts of the same claims in place (session 3019)")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--load", action="store_true")
    a = ap.parse_args(argv)
    cands = [P for P in CANDIDATES if not a.only or P["name"] == a.only]
    builder.run(FAMILY, cands, a.in_dir, dry_run=not a.load, replace=a.replace)
    return 0


if __name__ == "__main__":
    sys.exit(main())
