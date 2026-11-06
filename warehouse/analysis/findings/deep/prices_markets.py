#!/usr/bin/env python3
"""The findings hunt over the whole warehouse (chain 164), family "prices", second part: session 3002.

Energy Research Warehouse (ERW). Plan: docs/reviews/findings-hunt-plan-2026-11-06.md. Six candidates beside
prices.py's eight, on ERCOT's hourly prices (2015 to 2025), ERCOT's day-ahead ancillary service prices (2018 to 2025)
and EIA's daily Henry Hub close (1997 to 2025). None is a pattern the weekly hunt already asks: its day-ahead to
real-time spread is the median hour's by part of the day; here it is the share of hours the day-ahead price was the
higher. ECRS starts in June 2023 (three full years at most: the window test needs four) and is computed, not drafted.

    python warehouse/analysis/findings/deep/prices_markets.py --dry-run
    python warehouse/analysis/findings/deep/prices_markets.py --load
"""

import argparse
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..")))
sys.path.insert(0, HERE)
import builder  # noqa: E402
import hunt_measures as hm  # noqa: E402
import prices  # noqa: E402

FAMILY = "prices"
SERVICES = {"REGUP": "regulation up", "REGDN": "regulation down", "RRS": "responsive reserve", "NSPIN": "non-spinning reserve", "ECRS": "ERCOT contingency reserve"}
WINTER = ("12", "01", "02")        # local months December, January and February
TZ = "America/Chicago"


def as_price_mean(in_dir=None):
    """The year's mean day-ahead market clearing price for capacity of each ancillary service (USD per MW-hour)."""
    d = hm.series("ercot_as_prices", in_dir, variables=["mcpc_dam"], entities=[f"ercot:{s}" for s in SERVICES])
    d["year"] = d["ts"].dt.tz_convert(TZ).dt.year
    rows, tables = [], {}
    for entity, g in d.groupby("entity"):
        svc = entity.split(":", 1)[1]
        region, words = f"ercot_as_{svc}", f"ERCOT's day-ahead {SERVICES[svc]} ({svc})"
        for y, s in g.groupby("year"):
            rows.append(hm._row(region, words, y, float(s["value"].mean()), len(s)))
        tables[region] = ["ercot_as_prices"]
    return {"rows": rows, "tables": tables}


def da_above_rt_share(in_dir=None):
    """The share of the year's hours in which the day-ahead price was above the hour's real-time price."""
    rows, tables = [], {}
    for region, words, node, g, tbl in prices.nodes(in_dir):
        b = g.dropna(subset=["rt", "da"])
        for y, s in b.groupby("year"):
            rows.append(hm._row(region, words, y, float(100 * (s["da"] > s["rt"]).mean()), len(s)))
        tables[region] = [tbl]
    return {"rows": rows, "tables": tables}


def _min_hours(g):
    r = prices._rt(g).sort_values("hour")
    r = r[r.groupby("day")["rt"].transform("size") >= prices.MIN_DAY_HOURS]
    i = r.groupby("day")["rt"].idxmin()
    return r.loc[i, ["day", "year", "lhour"]]


def cheapest_hour(in_dir=None):
    """The mean local clock hour (0 to 23) at which the day's lowest real-time price fell."""
    rows, tables = [], {}
    for region, words, node, g, tbl in prices.nodes(in_dir):
        m = _min_hours(g)
        for y, s in m.groupby("year"):
            rows.append(hm._row(region, words, y, float(s["lhour"].mean()), len(s)))
        tables[region] = [tbl]
    return {"rows": rows, "tables": tables}


def winter_top_share(in_dir=None):
    """The share of the year's dearest one percent of real-time hours that fell in December, January or February."""
    rows, tables = [], {}
    for region, words, node, g, tbl in prices.nodes(in_dir):
        for y, s in prices._rt(g).groupby("year"):
            k = int(np.ceil(prices.TOP_HOURS * len(s)))
            top = s.sort_values(["rt", "hour"], ascending=[False, True]).head(k)
            rows.append(hm._row(region, words, y, float(100 * top["day"].str[5:7].isin(WINTER).mean()), len(s)))
        tables[region] = [tbl]
    return {"rows": rows, "tables": tables}


def weekend_discount(in_dir=None):
    """The mean real-time price of Saturdays and Sundays as a percent of the mean of Mondays to Fridays (local days)."""
    rows, tables = [], {}
    for region, words, node, g, tbl in prices.nodes(in_dir):
        r = prices._rt(g)
        wkend = pd.to_datetime(r["day"]).dt.dayofweek >= 5
        r = r.assign(wkend=wkend.values)
        for y, s in r.groupby("year"):
            a, b = s.loc[s["wkend"], "rt"].mean(), s.loc[~s["wkend"], "rt"].mean()
            rows.append(hm._row(region, words, y, float(100 * a / b) if b > 0 else None, len(s)))
        tables[region] = [tbl]
    return {"rows": rows, "tables": tables}


MORNING = (6, 9)                   # local clock hours 6 to 9: 6 AM to 10 AM, the morning shoulder
NIGHT = (0, 5)                     # local clock hours 0 to 5: midnight to 6 AM


def morning_shoulder(in_dir=None):
    """The mean real-time price from 6 AM to 10 AM local as a percent of the year's all-hours mean."""
    rows, tables = [], {}
    for region, words, node, g, tbl in prices.nodes(in_dir):
        for y, s in prices._rt(g).groupby("year"):
            m = s["rt"].mean()
            rows.append(hm._row(region, words, y, float(100 * s.loc[s["lhour"].between(*MORNING), "rt"].mean() / m) if m > 0 else None, len(s)))
        tables[region] = [tbl]
    return {"rows": rows, "tables": tables}


def midday_minus_night(in_dir=None):
    """The year's mean real-time price from 11 AM to 4 PM local minus its mean from midnight to 6 AM."""
    rows, tables = [], {}
    for region, words, node, g, tbl in prices.nodes(in_dir):
        for y, s in prices._rt(g).groupby("year"):
            a = s.loc[s["lhour"].between(*prices.MIDDAY), "rt"].mean()
            b = s.loc[s["lhour"].between(*NIGHT), "rt"].mean()
            rows.append(hm._row(region, words, y, float(a - b), len(s)))
        tables[region] = [tbl]
    return {"rows": rows, "tables": tables}


SPREAD_LINE = 50.0                 # USD per MWh: a day whose highest hour is this far above its lowest


def _days4(g):
    """Each whole day's spread of its four dearest hours' mean over its four cheapest hours' mean, and its 1-hour spread."""
    r = prices._rt(g)
    r = r[r.groupby("day")["rt"].transform("size") >= prices.MIN_DAY_HOURS]
    def one(s):
        v = np.sort(s["rt"].to_numpy())
        return pd.Series({"year": s["year"].iloc[0], "spread4": v[-4:].mean() - v[:4].mean(), "spread1": v[-1] - v[0]})
    return r.groupby("day").apply(one, include_groups=False)


def spread_4h(in_dir=None):
    """The median day's mean of its four dearest real-time hours less the mean of its four cheapest."""
    rows, tables = [], {}
    for region, words, node, g, tbl in prices.nodes(in_dir):
        for y, s in _days4(g).groupby("year"):
            rows.append(hm._row(region, words, y, float(np.median(s["spread4"])), len(s)))
        tables[region] = [tbl]
    return {"rows": rows, "tables": tables}


def wide_spread_days(in_dir=None):
    """The share of the year's days whose highest hourly real-time price was at least USD 50 per MWh above its lowest."""
    rows, tables = [], {}
    for region, words, node, g, tbl in prices.nodes(in_dir):
        for y, s in _days4(g).groupby("year"):
            rows.append(hm._row(region, words, y, float(100 * (s["spread1"] >= SPREAD_LINE).mean()), len(s)))
        tables[region] = [tbl]
    return {"rows": rows, "tables": tables}


def henry_hub_volatility(in_dir=None):
    """The median absolute change of Henry Hub's spot close from one trading day to the next, in percent."""
    gas = hm.series("eia_fuel_spot_prices", in_dir, variables=["spot_price"], entities=["eia:henry_hub"]).sort_values("ts")
    gas = gas[gas["value"] > 0]
    ch = (gas["value"] / gas["value"].shift(1) - 1).abs() * 100
    gas = gas.assign(change=ch.values, year=gas["ts"].dt.year).dropna(subset=["change"])
    rows = [hm._row("us_henry_hub", "Henry Hub, Louisiana", y, float(np.median(s["change"])), len(s)) for y, s in gas.groupby("year")]
    return {"rows": rows, "tables": {"us_henry_hub": ["eia_fuel_spot_prices"]}}


# ---------------------------------------------------------------------------------------------------------------------
# the reproduction scripts
# ---------------------------------------------------------------------------------------------------------------------
PY_MEASURE = {
    "da_above_rt_share": None,
    "cheapest_hour": ("h = h.sort_values('hour')\nh = h[h.groupby('day')['rt'].transform('size') >= 20]\n"
                      "m = h.loc[h.groupby('day')['rt'].idxmin()]\n"
                      "for y, s in m.groupby('year'):\n    out[y] = (float(s['lhour'].mean()), len(s))\n"),
    "winter_top_share": ("for y, s in h.groupby('year'):\n    k = int(np.ceil(0.01 * len(s)))\n"
                         "    top = s.sort_values(['rt', 'hour'], ascending=[False, True]).head(k)\n"
                         "    out[y] = (100 * top['day'].str[5:7].isin(['12', '01', '02']).mean(), len(s))\n"),
    "morning_shoulder": "for y, s in h.groupby('year'):\n    out[y] = (100 * s.loc[s['lhour'].between(6, 9), 'rt'].mean() / s['rt'].mean(), len(s))\n",
    "midday_minus_night": ("for y, s in h.groupby('year'):\n"
                           "    out[y] = (float(s.loc[s['lhour'].between(11, 15), 'rt'].mean() - s.loc[s['lhour'].between(0, 5), 'rt'].mean()), len(s))\n"),
    "spread_4h": ("h = h[h.groupby('day')['rt'].transform('size') >= 20]\n"
                  "d = h.groupby('day').agg(year=('year', 'first'), top=('rt', lambda v: np.sort(v.to_numpy())[-4:].mean()), low=('rt', lambda v: np.sort(v.to_numpy())[:4].mean()))\n"
                  "for y, s in d.groupby('year'):\n    out[y] = (float(np.median(s['top'] - s['low'])), len(s))\n"),
    "wide_spread_days": ("h = h[h.groupby('day')['rt'].transform('size') >= 20]\n"
                         "d = h.groupby('day').agg(year=('year', 'first'), pmax=('rt', 'max'), pmin=('rt', 'min'))\n"
                         "for y, s in d.groupby('year'):\n    out[y] = (100 * ((s['pmax'] - s['pmin']) >= 50.0).mean(), len(s))\n"),
    "weekend_discount": ("h['wkend'] = pd.to_datetime(h['day']).dt.dayofweek >= 5\n"
                         "for y, s in h.groupby('year'):\n    out[y] = (100 * s.loc[s['wkend'], 'rt'].mean() / s.loc[~s['wkend'], 'rt'].mean(), len(s))\n"),
}

PY_DA = '''"""ERW findings hunt (chain 164): reproduce candidate da_above_rt_share for {region} from the ERW's public table.

    python {{this file}} <{table}.csv>

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
d = d[d["market"].isin(["ercot_rtm", "ercot_dam"]) & (d["node"] == {node!r})].copy()
d["value"] = pd.to_numeric(d["value"], errors="coerce")
d = d.dropna(subset=["value"])
d["hour"] = pd.to_datetime(d["ts_utc"], format="%Y-%m-%dT%H:%M:%SZ", utc=True).dt.floor("h")
d["kind"] = d["market"].str[-3:]
w = d.groupby(["kind", "hour"])["value"].mean().unstack("kind").dropna()
w["year"] = w.index.tz_convert("America/Chicago").year
out = {{}}
for y, s in w.groupby("year"):
    out[y] = (100 * (s["dam"] > s["rtm"]).mean(), len(s))
for y in sorted(out):
    print(y, round(out[y][0], 6), out[y][1])
'''

PY_AS = '''"""ERW findings hunt (chain 164): reproduce candidate as_price_mean for {region} from the ERW's public table.

    python {{this file}} <ercot_as_prices.csv>

The year's mean day-ahead clearing price for {svc} capacity (USD per MW-hour), by local year (Central time).
"""
import sys

import pandas as pd

with open(sys.argv[1], encoding="utf-8") as f:
    skip = 0
    for line in f:
        if not line.startswith("#"):
            break
        skip += 1
d = pd.read_csv(sys.argv[1], skiprows=skip, usecols=["entity", "variable", "ts_utc", "value"], dtype=str)
d = d[(d["entity"] == "ercot:{svc}") & (d["variable"] == "mcpc_dam")].copy()
d["value"] = pd.to_numeric(d["value"], errors="coerce")
d = d.dropna(subset=["value"])
d["year"] = pd.to_datetime(d["ts_utc"], format="%Y-%m-%dT%H:%M:%SZ", utc=True).dt.tz_convert("America/Chicago").dt.year
for y, s in d.groupby("year"):
    print(y, round(float(s["value"].mean()), 6), len(s))
'''

PY_HH = '''"""ERW findings hunt (chain 164): reproduce candidate henry_hub_volatility from the ERW's public table.

    python {this file} <eia_fuel_spot_prices.csv>

The median absolute change of Henry Hub's spot close from one trading day to the next, in percent, by calendar year.
"""
import sys

import numpy as np
import pandas as pd

with open(sys.argv[1], encoding="utf-8") as f:
    skip = 0
    for line in f:
        if not line.startswith("#"):
            break
        skip += 1
g = pd.read_csv(sys.argv[1], skiprows=skip, usecols=["entity", "variable", "ts_utc", "value"], dtype=str)
g = g[(g["entity"] == "eia:henry_hub") & (g["variable"] == "spot_price")].copy()
g["value"] = pd.to_numeric(g["value"], errors="coerce")
g = g[g["value"] > 0].sort_values("ts_utc")
g["change"] = (g["value"] / g["value"].shift(1) - 1).abs() * 100
g = g.dropna(subset=["change"])
g["year"] = g["ts_utc"].str[:4].astype(int)
for y, s in g.groupby("year"):
    print(y, round(float(np.median(s["change"])), 6), len(s))
'''


def _dst(var):
    """The Stata lines that turn a UTC clock variable into Central time (t_local), by the US daylight-time rule."""
    return [f"generate int y_utc = year(dofc({var}))", "generate int mar1 = mdy(3, 1, y_utc)", "generate int dst_start = mar1 + mod(7 - dow(mar1), 7) + 7",
            "generate int nov1 = mdy(11, 1, y_utc)", "generate int dst_end = nov1 + mod(7 - dow(nov1), 7)",
            f"generate byte dst = {var} >= cofd(dst_start) + msofhours(8) & {var} < cofd(dst_end) + msofhours(7)",
            f"generate double t_local = {var} - msofhours(6) + dst * msofhours(1)"]


def reproduce_py(name, region):
    if name == "as_price_mean":
        svc = region[len("ercot_as_"):]
        return PY_AS.format(region=region, svc=svc)
    if name == "henry_hub_volatility":
        return PY_HH
    node = region[len("ercot_"):]
    table = "ercot_zone_prices_history" if node.startswith("LZ_") else "ercot_all_hub_prices_history"
    if name == "da_above_rt_share":
        return PY_DA.format(region=region, table=table, node=node)
    head = prices.PY_HEAD.format(name=name, region=region, table=table, extra_arg="", nodes=[node])
    return head + PY_MEASURE[name] + prices.PY_TAIL


def reproduce_do(name, region):
    import findings_common as common
    head = [f"* ERW findings hunt (chain 164): reproduce candidate {name} for {region} from the ERW's public tables.",
            "* Input: the table's CSV as the public download holds it (Redivis: the variable names on its first line). From the ERW's own file, delete its lines that begin with # first.",
            "clear all"]
    if name == "as_price_mean":
        svc = region[len("ercot_as_"):]
        lines = head + ['import delimited "ercot_as_prices.csv", varnames(1) stringcols(_all) clear',
                        f'keep if entity == "ercot:{svc}" & variable == "mcpc_dam"', "destring value, replace force", "drop if missing(value)",
                        'generate double t_utc = clock(subinstr(subinstr(ts_utc, "T", " ", 1), "Z", "", 1), "YMDhms")'] + _dst("t_utc") + [
                        "generate int year = year(dofc(t_local))", "collapse (mean) measure = value (count) n = value, by(year)"]
    elif name == "henry_hub_volatility":
        lines = head + ['import delimited "eia_fuel_spot_prices.csv", varnames(1) stringcols(_all) clear',
                        'keep if entity == "eia:henry_hub" & variable == "spot_price"', "destring value, replace force", "keep if value > 0 & !missing(value)",
                        "sort ts_utc", "generate double change = abs(value / value[_n - 1] - 1) * 100", "drop if missing(change)",
                        "generate int year = real(substr(ts_utc, 1, 4))", "collapse (median) measure = change (count) n = change, by(year)"]
    else:
        node = region[len("ercot_"):]
        table = "ercot_zone_prices_history" if node.startswith("LZ_") else "ercot_all_hub_prices_history"
        if name == "da_above_rt_share":
            lines = head + [f'import delimited "{table}.csv", varnames(1) stringcols(_all) clear',
                            f'keep if (market == "ercot_rtm" | market == "ercot_dam") & node == "{node}"', "destring value, replace force",
                            "drop if missing(value)", 'generate double t_utc = clock(subinstr(subinstr(ts_utc, "T", " ", 1), "Z", "", 1), "YMDhms")',
                            "generate double hour_utc = floor(t_utc / msofhours(1)) * msofhours(1)", "generate str3 kind = substr(market, -3, 3)",
                            "collapse (mean) value, by(kind hour_utc)", "reshape wide value, i(hour_utc) j(kind) string", "drop if missing(valuedam) | missing(valuertm)"
                            ] + _dst("hour_utc") + ["generate int year = year(dofc(t_local))", "generate byte above = valuedam > valuertm",
                                                    "collapse (mean) measure = above (count) n = above, by(year)", "replace measure = 100 * measure"]
        else:
            lines = [f"* ERW findings hunt (chain 164): reproduce candidate {name} for {region} from the ERW's public tables."] + prices._do_hourly(table, [node])
            if name == "cheapest_hour":
                lines += ["bysort day: generate long hours = _N", "keep if hours >= 20", "bysort day (rt hour_utc): keep if _n == 1",
                          "collapse (mean) measure = lhour (count) n = lhour, by(year)"]
            elif name == "winter_top_share":
                lines += ["generate byte winter = inlist(month(day), 12, 1, 2)", "gsort year -rt hour_utc", "by year: generate long rank = _n",
                          "by year: generate long n = _N", "by year: egen double top_winter = mean(cond(rank <= ceil(0.01 * n), winter, .))",
                          "by year: keep if _n == 1", "generate double measure = 100 * top_winter"]
            elif name == "morning_shoulder":
                lines += ["generate double mor = rt if inrange(lhour, 6, 9)", "collapse (mean) all_mean = rt (mean) mor_mean = mor (count) n = rt, by(year)",
                          "generate double measure = 100 * mor_mean / all_mean"]
            elif name == "midday_minus_night":
                lines += ["generate double mid = rt if inrange(lhour, 11, 15)", "generate double nig = rt if inrange(lhour, 0, 5)",
                          "collapse (mean) mid_mean = mid (mean) nig_mean = nig (count) n = rt, by(year)", "generate double measure = mid_mean - nig_mean"]
            elif name == "spread_4h":
                lines += ["bysort day: generate long hours = _N", "keep if hours >= 20", "bysort day (rt): generate long up = _n",
                          "by day: generate long down = _N - _n + 1", "generate double low4 = rt if up <= 4", "generate double top4 = rt if down <= 4",
                          "collapse (mean) low4 (mean) top4 (firstnm) year, by(day)", "generate double spread4 = top4 - low4",
                          "collapse (median) measure = spread4 (count) n = spread4, by(year)"]
            elif name == "wide_spread_days":
                lines += ["collapse (max) pmax = rt (min) pmin = rt (count) hours = rt (firstnm) year, by(day)", "keep if hours >= 20",
                          "generate byte wide = pmax - pmin >= 50", "collapse (mean) measure = wide (count) n = wide, by(year)", "replace measure = 100 * measure"]
            elif name == "weekend_discount":
                lines += ["generate byte wkend = inlist(dow(day), 0, 6)", "generate double we = rt if wkend == 1", "generate double wd = rt if wkend == 0",
                          "collapse (mean) we_mean = we (mean) wd_mean = wd (count) n = rt, by(year)", "generate double measure = 100 * we_mean / wd_mean"]
    lines += ["sort year", "list year measure n, noobs"]
    return common.do_file(lines)


def reproduce(name):
    return lambda region: {"py": reproduce_py(name, region), "do": reproduce_do(name, region)}


def area(region):
    if region.startswith("ercot_as_") or region.startswith("us_"):
        return region
    return prices.area(region)


C = builder.candidate
CANDIDATES = [
    C("as_price_mean", FAMILY, as_price_mean, "USD per MW-hour", 2, 8000, 1.0, "THE PRICE OF RESERVES",
      "the year's mean day-ahead market clearing price for the service's capacity",
      lambda w: f"the mean day-ahead clearing price of {w} capacity",
      "Nominal dollars for capacity held, not energy; the quantities ERCOT buys of each service changed in these years, and the mean does not weigh by them.",
      reproduce("as_price_mean"), consequence=3),
    C("da_above_rt_share", FAMILY, da_above_rt_share, "percent of hours", 1, 8000, 3.0, "DAY-AHEAD ABOVE REAL TIME",
      "the share of the year's hours in which the day-ahead price was above the hour's real-time price",
      lambda w: f"the share of hours in which the day-ahead price at {w} was above the real-time price",
      "A count of hours, not of dollars: it says how often the day-ahead price was the higher, not by how much.",
      reproduce("da_above_rt_share"), consequence=2),
    C("cheapest_hour", FAMILY, cheapest_hour, "hours after local midnight", 1, 330, 0.5, "THE CHEAPEST HOUR OF THE DAY",
      "the mean local clock hour (0 to 23) at which the day's lowest real-time price fell",
      lambda w: f"the mean local hour of the day's cheapest real-time hour at {w}",
      "A mean of clock hours: a year with cheap hours split between night and midday averages to an hour in between that may itself be rarely the cheapest.",
      reproduce("cheapest_hour"), consequence=3),
    C("winter_top_share", FAMILY, winter_top_share, "percent of the dearest hours", 1, 8000, 5.0, "WINTER'S SHARE OF THE DEAREST HOURS",
      "the share of the year's dearest one percent of real-time hours that fell in December, January or February",
      lambda w: f"the share of the year's dearest one percent of real-time hours at {w} that fell in December, January or February",
      "About 88 hours a year: one cold spell can carry a year, and the year's December is not the same winter as its January.",
      reproduce("winter_top_share"), consequence=2),
    C("weekend_discount", FAMILY, weekend_discount, "percent of the weekday mean", 1, 8000, 3.0, "THE WEEKEND PRICE",
      "the mean real-time price of Saturdays and Sundays as a percent of the mean of Mondays to Fridays",
      lambda w: f"the mean weekend real-time price at {w}",
      "A ratio of two means; holidays that fall on weekdays are counted as weekdays.",
      reproduce("weekend_discount"), consequence=1),
    C("morning_shoulder", FAMILY, morning_shoulder, "percent of the all-hours mean", 1, 8000, 5.0, "THE MORNING SHOULDER",
      "the mean real-time price from 6 AM to 10 AM local as a percent of the year's all-hours mean",
      lambda w: f"the morning real-time price (6 AM to 10 AM) at {w}",
      "A ratio of two means; a few scarcity hours elsewhere in the day lower the morning's percent without any change in the morning.",
      reproduce("morning_shoulder"), consequence=2),
    C("midday_minus_night", FAMILY, midday_minus_night, "USD per MWh", 2, 8000, 2.0, "MIDDAY AGAINST NIGHT",
      "the year's mean real-time price from 11 AM to 4 PM local minus its mean from midnight to 6 AM",
      lambda w: f"the mean midday real-time price at {w} less its mean night price",
      "Nominal dollars; a difference of two means, each of which a few scarcity hours can move.",
      reproduce("midday_minus_night"), consequence=3),
    C("spread_4h", FAMILY, spread_4h, "USD per MWh", 2, 330, 3.0, "THE FOUR-HOUR SPREAD",
      "the median day's mean of its four dearest real-time hours less the mean of its four cheapest",
      lambda w: f"the median day's four-hour spread at {w} (its four dearest hours' mean less its four cheapest)",
      "Nominal dollars; the hours need not be consecutive, so a four-hour battery could capture the spread only in part, before losses.",
      reproduce("spread_4h"), consequence=3),
    C("wide_spread_days", FAMILY, wide_spread_days, "percent of days", 1, 330, 5.0, "DAYS WITH A WIDE SPREAD",
      "the share of the year's days whose highest hourly real-time price was at least USD 50 per MWh above its lowest",
      lambda w: f"the share of days at {w} whose highest hourly real-time price was at least USD 50 per MWh above its lowest",
      "A nominal line, not adjusted for inflation: the same real spread crosses it more easily in a later year.",
      reproduce("wide_spread_days"), consequence=2),
    C("henry_hub_volatility", FAMILY, henry_hub_volatility, "percent a day", 2, 200, 0.2, "HENRY HUB'S DAILY MOVE",
      "the median absolute change of Henry Hub's spot close from one trading day to the next",
      lambda w: f"the median absolute daily change of the spot gas price at {w}",
      "Trading days as EIA publishes them; a change across a weekend or a holiday counts as one day's.",
      reproduce("henry_hub_volatility"), consequence=2),
]
for _P in CANDIDATES:
    _P["area"] = area


def main(argv=None):
    ap = argparse.ArgumentParser(description="The findings hunt, family prices, second part (chain 164)")
    ap.add_argument("--in-dir", default=None)
    ap.add_argument("--only", default=None)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--load", action="store_true")
    a = ap.parse_args(argv)
    cands = [P for P in CANDIDATES if not a.only or P["name"] == a.only]
    builder.run(FAMILY + "_markets", cands, a.in_dir, dry_run=not a.load)
    return 0


if __name__ == "__main__":
    sys.exit(main())
