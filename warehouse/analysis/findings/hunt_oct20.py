#!/usr/bin/env python3
"""The findings hunt of 20 October 2026: records and windows beside the weekly hunt's trends, with the first LinkedIn material.

Energy Research Warehouse (ERW). The weekly hunt (hunt.py, session 233) asks one question of every region: did a measure
move from the first full year to the last, and does the move pass five tests. This module keeps that engine and adds two
claim kinds the owner's prompt of 20 October 2026 asked for, each computed from the warehouse's own tables:

    record   the latest complete period against the table's full history: the highest (or lowest) value held
    window   this year to its cut date against the same window of every earlier year held (hours below zero this year)
    trend    the weekly hunt's claim, tested by hunt.test_claim (the five tests of sessions 233 and 316)

Candidate families, each on public-licensed regions only (hunt.blocked_grids: ISO-NE, MISO, NYISO need a license;
NYISO and SPP are held): ERCOT's hub prices since 2015 (hours below zero by year and by window, the yearly average,
the West hub's basis, the day-ahead premium, hours at USD 100 or more, the peak premium), Henry Hub and Brent against
WTI since the 1980s and 1990s, CAISO's curtailment, battery discharge and its timing (storage_daily_cycle,
eia930_all_storage), and the interconnection queues as LBNL records them (entries by year, each cohort's withdrawn
share, the median wait to operation). A finding built on an internal table is marked internal and never goes on a public
page or in a caption; no internal table is read by this hunt as it stands (large_load_statements is not on this machine).

What each kept finding gets, in docs/findings/<day>/<slug>/:

    finding.json      the claim, its series, its tests, its state (new, approved, rejected, stata_checked), its sources
    extract.csv       the exact rows the headline number comes from, at the table's own grain
    series.csv        one row a period: the measure, its observations, whether the period is complete
    chart_square.png  1200 by 1200, and chart_wide.png, 1600 by 900 (brand_chart.py: docs/brand.md in matplotlib)
    caption.md        a LinkedIn caption under 1,300 characters, ending with the source and the ERW table's name
    check.do          a Stata do-file to the owner's rules that reads extract.csv and reproduces the headline number

    python warehouse/analysis/findings/hunt_oct20.py hunt [--keep 10] [--out docs/findings/2026-10-20] [--dry-run]
    python warehouse/analysis/findings/hunt_oct20.py check [docs/findings/2026-10-20]     every check.do's logic, in Python
    python warehouse/analysis/findings/hunt_oct20.py state <slug> <new|approved|rejected|stata_checked> [--out ...]

Nothing here writes a warehouse table, reads Supabase or Redivis, or posts anywhere. No model is called: every sentence
is computed from the numbers. The ranking is by the size of the move in typical moves of the series, with a claim the
ERW has already shown (SHOWN) ranked after the new ones.
"""

import argparse
import datetime as dt
import io
import json
import math
import os
import re
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import findings_common as common  # noqa: E402
import hunt  # noqa: E402

VERSION = "1.0.0"
DAY = "2026-10-20"
OUT_DEFAULT = os.path.join(ROOT, "docs", "findings", DAY)
IN_DIR = common.DEFAULT_IN_DIR if hasattr(common, "DEFAULT_IN_DIR") else os.path.join(ROOT, "warehouse", "output")
METHOD = "docs/methods/automated_analysis_findings.md"
STATES = ("new", "approved", "rejected", "stata_checked")
STATE_WORDS = {"new": "New, not reviewed", "approved": "Approved", "rejected": "Rejected", "stata_checked": "Stata checked"}
FULL_SHARE = hunt.FULL_SHARE            # a period is complete at 90 percent of the fullest period's observations
RECORD_MARGIN = 0.05                     # a record beats the previous record by at least 5 percent of it
MIN_HISTORY = {"year": 5, "month": 12}   # periods before the record period
TZ = {"ercot": "America/Chicago", "caiso": "America/Los_Angeles", "pjm": "America/New_York"}
HUB_WORDS = {"HB_HUBAVG": "the hub average", "HB_NORTH": "the North hub", "HB_HOUSTON": "the Houston hub", "HB_SOUTH": "the South hub", "HB_WEST": "the West hub"}
LICENSE = {}                             # table -> license, read from coverage.csv

# What the ERW has shown already (docs/reviews/findings-verified-2026-10-13.md, blocks 1 to 40; the thesis page and the
# peak premium explorer): a claim of these topics is ranked after the new ones and says so on its card.
SHOWN = {
    "negative_share_year": "the weekly hunt's drafts of 13 and 14 October 2026 (ERCOT North, South, Houston and the load zones)",
    "curtailment_share_year": "the weekly hunt's draft of 13 October 2026 (block 19)",
    "peak_premium_year": "the thesis page and the ERCOT peak premium explorer (docs/methods/ercot_peak_premium.md)",
    "da_premium_year": "the weekly hunt's drafts of 13 and 14 October 2026 (the night part of the day at the West and South hubs)",
    "hours_above_100_year": "near the weekly hunt's draft of 13 October 2026 on hours at USD 1,000 or more (block 16)",
}
_CACHE = {}


def _cached(key, build):
    if key not in _CACHE:
        _CACHE[key] = build()
    return _CACHE[key]


def licenses():
    if not LICENSE:
        for r in _csv_rows(os.path.join(ROOT, "warehouse", "metadata", "coverage.csv")):
            LICENSE[r["table"]] = r.get("license", "")
    return LICENSE


def _csv_rows(path):
    with open(path, encoding="utf-8") as f:
        return list(__import__("csv").DictReader(ln for ln in f if not ln.startswith("#")))


def read(name, usecols, keep=None):
    """A warehouse table from this machine's output folder, read with pandas, filtered while it is read."""
    path = os.path.join(IN_DIR, name + ".csv")
    if not os.path.exists(path):
        raise common.NoData(f"{name} is not on this machine")
    parts = []
    for chunk in pd.read_csv(path, comment="#", usecols=usecols, chunksize=500_000, low_memory=False):
        parts.append(chunk[keep(chunk)] if keep else chunk)
    d = pd.concat(parts, ignore_index=True)
    d["value"] = pd.to_numeric(d["value"], errors="coerce")
    return d.dropna(subset=["value"]).reset_index(drop=True)


def local(ts, tz):
    return pd.to_datetime(ts, utc=True).dt.tz_convert(tz)


# ---------------------------------------------------------------------------------------------------------------------
# the inputs, read once
# ---------------------------------------------------------------------------------------------------------------------
def ercot_rtm():
    """ERCOT's five hubs, real-time 15-minute settlement point prices since 2015 (ercot_all_hub_prices_history, public),
    with the local year, the local date and the local clock hour."""
    def build():
        d = read("ercot_all_hub_prices_history", ["ts_utc", "value", "market", "node"],
                 keep=lambda c: (c["market"] == "ercot_rtm") & c["node"].isin(list(HUB_WORDS)))
        t = local(d["ts_utc"], TZ["ercot"])
        d["year"], d["date"], d["hour"] = t.dt.year, t.dt.strftime("%Y-%m-%d"), t.dt.hour
        return d.sort_values(["node", "ts_utc"]).reset_index(drop=True)
    return _cached("ercot_rtm", build)


def ercot_dam():
    def build():
        d = read("ercot_all_hub_prices_history", ["ts_utc", "value", "market", "node"],
                 keep=lambda c: (c["market"] == "ercot_dam") & c["node"].isin(list(HUB_WORDS)))
        t = local(d["ts_utc"], TZ["ercot"])
        d["year"] = t.dt.year
        d["hour_utc"] = pd.to_datetime(d["ts_utc"], utc=True).dt.floor("h")
        return d
    return _cached("ercot_dam", build)


def henry_hub():
    def build():
        d = read("eia_fuel_spot_prices", ["entity", "variable", "ts_utc", "value"], keep=lambda c: c["entity"].isin(["eia:henry_hub", "eia:brent", "eia:wti_cushing"]))
        d["date"] = d["ts_utc"].str[:10]
        d["year"] = d["date"].str[:4].astype(int)
        return d
    return _cached("fuel", build)


def caiso_curtailment():
    def build():
        d = read("caiso_curtailment_daily", ["entity", "variable", "ts_utc", "value"])
        d["date"] = d["ts_utc"].str[:10]
        d["year"], d["month"] = d["date"].str[:4].astype(int), d["date"].str[:7]
        return d
    return _cached("caiso_curt", build)


def storage_daily():
    def build():
        d = read("storage_daily_cycle", ["entity", "variable", "ts_utc", "value"])
        d["date"] = d["ts_utc"].str[:10]
        d["month"] = d["date"].str[:7]
        return d
    return _cached("storage_daily", build)


def storage_hourly():
    def build():
        d = read("eia930_all_storage", ["entity", "variable", "ts_utc", "value"], keep=lambda c: c["entity"] == "eia930:ERCO")
        t = local(d["ts_utc"], TZ["ercot"])
        d["month"], d["hour"], d["date"] = t.dt.strftime("%Y-%m"), t.dt.hour, t.dt.strftime("%Y-%m-%d")
        return d.drop_duplicates(["ts_utc"])
    return _cached("storage_hourly", build)


def lbnl():
    def build():
        path = os.path.join(IN_DIR, "lbnl_interconnection_queue.csv")
        if not os.path.exists(path):
            raise common.NoData("lbnl_interconnection_queue is not on this machine")
        d = pd.read_csv(path, comment="#", usecols=["entity_id", "capacity_mw", "q_status", "q_date", "on_date", "wd_date", "region", "q_year", "type_clean"], low_memory=False)
        d["capacity_mw"] = pd.to_numeric(d["capacity_mw"], errors="coerce")
        d["q_year"] = pd.to_numeric(d["q_year"], errors="coerce")
        return d[d["region"].isin(["ERCOT", "CAISO", "PJM"])].dropna(subset=["q_year"]).copy()
    return _cached("lbnl", build)


def peak_premium():
    def build():
        d = read("ercot_peak_premium_annual", ["entity", "variable", "ts_utc", "value"], keep=lambda c: c["entity"] == "ercot:HB_HUBAVG")
        d["year"] = d["ts_utc"].str[:4].astype(int)
        return d
    return _cached("peak_premium", build)


# ---------------------------------------------------------------------------------------------------------------------
# the claim kinds and their tests
# ---------------------------------------------------------------------------------------------------------------------
def spread(values):
    return hunt.spread(list(values))


def test_record(series, grain, high=True, recent=None):
    """series: ordered list of {period, value, n, complete}. The claim: the highest (or lowest) value of every complete
    period held was set in a recent period (recent: the periods that count as news; default the last complete one).
    Leading incomplete periods (a history that starts mid-year) are left out of the window. Four tests, all of which a
    record must pass."""
    full = [s for s in series if s["complete"]]
    if len(full) < 2:
        return None
    first_full = series.index(full[0])
    window = series[first_full:]
    vals = [s["value"] for s in full]
    best_i = int(np.argmax(vals)) if high else int(np.argmin(vals))
    last = full[best_i]
    recent = set(map(str, recent)) if recent is not None else {str(full[-1]["period"])}
    if str(last["period"]) not in recent:
        return None
    earlier = [s for s in full if s is not last]
    ev = [s["value"] for s in earlier]
    prev = earlier[int(np.argmax(ev)) if high else int(np.argmin(ev))]
    margin = abs(last["value"] - prev["value"])
    rel = margin / abs(prev["value"]) if prev["value"] else float("inf")
    before = [s for s in full if series.index(s) < series.index(last)]
    t1 = {"name": "history long enough", "passed": len(before) >= MIN_HISTORY[grain],
          "words": f"{len(before)} complete {grain}s before {last['period']}; the floor is {MIN_HISTORY[grain]}"}
    t2 = {"name": "the record period is complete", "passed": bool(last["complete"]),
          "words": f"{last['period']} holds {common.fmt(last['n'], 0)} observations, {common.fmt(last['share'] * 100, 0)} percent of a whole {grain}'s"}
    gaps = [str(s["period"]) for s in window if not s["complete"] and series.index(s) < series.index(last)]
    t3 = {"name": "no gap in the window", "passed": len(gaps) == 0,
          "words": f"every {grain} from {window[0]['period']} to {last['period']} is complete" if not gaps else f"incomplete {grain}s inside the window: {', '.join(gaps)}"}
    t4 = {"name": "a margin over the previous record", "passed": rel >= RECORD_MARGIN,
          "words": f"{last['period']} stands {common.fmt(rel * 100, 1)} percent {'above' if high else 'below'} {prev['period']}, the previous {'high' if high else 'low'}; the floor is {common.fmt(RECORD_MARGIN * 100, 0)} percent"}
    sp = spread([s["value"] for s in full])
    strength = round(margin / sp, 4) if sp > 0 else 0.0
    tests = [t1, t2, t3, t4]
    return {"kind": "record", "direction": "high" if high else "low", "period": last["period"], "value": last["value"], "n": last["n"],
            "previous_period": prev["period"], "previous": prev["value"], "margin": margin, "margin_pct": rel * 100,
            "tests": tests, "passed": all(t["passed"] for t in tests), "typical_move": sp, "strength": strength,
            "periods": [s["period"] for s in full], "values": [s["value"] for s in full]}


def recent_months(series, months=12):
    """The complete months within the last `months` of the data's end: a record set in one of them is news."""
    full = [s for s in series if s["complete"]]
    if not full:
        return []
    end = str(full[-1]["period"])
    y, m = int(end[:4]), int(end[5:7])
    keep = set()
    for k in range(months):
        keep.add(f"{y:04d}-{m:02d}")
        m -= 1
        if m == 0:
            y, m = y - 1, 12
    return [s["period"] for s in full if s["period"] in keep]


SERIES_LOG = []


def note_series(label, series):
    SERIES_LOG.append((label, [(s["period"], round(s["value"], 3), s["n"], s.get("complete")) for s in series]))


def test_trend(series, n_floor, decimals, unit, this_year, count_rule="share"):
    """The weekly hunt's claim and its five tests, on a yearly series of {period, value, n}. count_rule "floor": a
    period whose observations reach the floor counts as complete whatever the fullest period holds (a queue cohort's
    positions vary by year and are not a year's hours)."""
    P = {"n_floor": n_floor, "decimals": decimals, "unit": unit}
    s = {str(x["period"]): (x["value"], min(x["n"], n_floor) if count_rule == "floor" else x["n"]) for x in series}
    c = hunt.test_claim(s, P, this_year)
    if c is None:
        return None
    c["kind"] = "trend"
    if count_rule == "floor":
        real = {str(x["period"]): x["n"] for x in series}
        c["n_first"], c["n_last"] = real[c["first_year"]], real[c["last_year"]]
        c["tests"][2]["words"] = f"{c['first_year']} holds {common.fmt(c['n_first'], 0)} and {c['last_year']} holds {common.fmt(c['n_last'], 0)} observations; the floor is {common.fmt(n_floor, 0)}"
    return c


def test_trend_months(series, n_floor, decimals, unit, this_month):
    """The weekly hunt's five tests over complete months (period "YYYY-MM"): the last complete month against the first.
    The two ends may be different seasons; the caption says so, and the months between them are on the chart."""
    keyed = [{"period": int(x["period"].replace("-", "")), "value": x["value"], "n": x["n"]} for x in series]
    c = test_trend(keyed, n_floor, decimals, unit, int(this_month.replace("-", "")))
    if c is None:
        return None
    back = lambda k: f"{str(k)[:4]}-{str(k)[4:6]}"   # noqa: E731
    c["first_year"], c["last_year"] = back(c["first_year"]), back(c["last_year"])
    c["years"] = [back(y) for y in c["years"]]
    for t in c["tests"]:
        t["words"] = re.sub(r"\b(20\d{2})(\d{2})\b", r"\1-\2", t["words"]).replace("full years", "complete months").replace("yearly", "monthly").replace("years", "months").replace("year", "month")
    c["grain"] = "month"
    return c


def mark_complete(series, grain=None, expected=None):
    """Each period's completeness: its observations against the fullest period's (FULL_SHARE), or against an expected
    count per period when one is given (days in a month, intervals in a year)."""
    most = max(s["n"] for s in series) if series else 0
    for s in series:
        exp = expected(s["period"]) if expected else most
        s["share"] = s["n"] / exp if exp else 0.0
        s["complete"] = s["share"] >= FULL_SHARE
    return series


def day_words(d):
    """'25 August' for '2026-08-25'."""
    x = dt.date(int(d[:4]), int(d[5:7]), int(d[8:10]))
    return f"{x.day} {x.strftime('%B')}"


def days_in_month(period):
    y, m = int(period[:4]), int(period[5:7])
    return (dt.date(y + (m == 12), m % 12 + 1, 1) - dt.date(y, m, 1)).days


def intervals_in_year(year, per_day):
    y = int(year)
    return (366 if (y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)) else 365) * per_day


# ---------------------------------------------------------------------------------------------------------------------
# the families: each yields candidate claims
# ---------------------------------------------------------------------------------------------------------------------
def _claim(family, slug, grid, region_words, title, label, unit, decimals, series, claim, tables, extract, headline, shown=None, grain="year", note=""):
    return dict(family=family, slug=slug, grid=grid, region_words=region_words, title=title, label=label, unit=unit, decimals=decimals,
                series=series, claim=claim, tables=tables, extract=extract, headline=headline, shown=shown or SHOWN.get(family), grain=grain, note=note,
                license=max((licenses().get(t, "") for t in tables), key=lambda s: s != "public"))


def fam_ercot_negative(this_year):
    """Hours below zero at ERCOT's hubs: by year (trend, the hunt's own pattern) and this year's window against the same
    window of every earlier year (record over windows)."""
    d = ercot_rtm()
    cut = d.loc[d["year"] == this_year, "date"].max()           # the last local date held this year
    cut_md = cut[5:]
    out = []
    for node, g in d.groupby("node"):
        words = f"ERCOT, {HUB_WORDS[node]}"
        yearly = []
        for y, s in g.groupby("year"):
            yearly.append({"period": int(y), "value": float((s["value"] < 0).mean() * 100), "n": int(len(s))})
        mark_complete(yearly, expected=lambda p: intervals_in_year(p, 96))
        note_series(f"negative by year {node}", yearly)
        full = [x for x in yearly if x["period"] < this_year]
        c = test_trend(full, 30000, 2, "percent of hours", this_year)
        if c:
            y0, y1 = int(c["first_year"]), int(c["last_year"])
            ex = g[g["year"].isin([y0, y1])][["year", "ts_utc", "value"]].rename(columns={"year": "period"})
            out.append(_claim("negative_share_year", f"ercot-{node.lower()}-negative-hours-by-year", "ercot", words,
                              "HOURS BELOW ZERO", f"share of the year's 15-minute intervals with a real-time price below zero at {HUB_WORDS[node]}",
                              "percent of intervals", 2, yearly, c, ["ercot_all_hub_prices_history"], ex,
                              {"op": "share_below", "threshold": 0, "period": y1, "compare_period": y0}))
        # the window: 1 January to the cut date, each year
        w = g[g["date"].str[5:] <= cut_md]
        windows = []
        for y, s in w.groupby("year"):
            windows.append({"period": int(y), "value": float((s["value"] < 0).mean() * 100), "n": int(len(s))})
        exp_days = (dt.date(this_year, int(cut[5:7]), int(cut[8:10])) - dt.date(this_year, 1, 1)).days + 1
        mark_complete(windows, expected=lambda p: exp_days * 96)
        note_series(f"negative window {node}", windows)
        r = test_record(windows, "year", high=True, recent=[this_year])
        if r:
            ex = w[w["year"].isin([int(r["period"]), int(r["previous_period"])])][["year", "ts_utc", "value"]].rename(columns={"year": "period"})
            out.append(_claim("negative_share_window", f"ercot-{node.lower()}-negative-hours-this-year", "ercot", words,
                              "HOURS BELOW ZERO, THIS YEAR SO FAR", f"share of the 15-minute intervals from 1 January to {day_words(cut)} with a real-time price below zero at {HUB_WORDS[node]}",
                              "percent of intervals", 2, windows, r, ["ercot_all_hub_prices_history"], ex,
                              {"op": "share_below", "threshold": 0, "period": r["period"], "compare_period": r["previous_period"]},
                              note=f"the window is 1 January to {cut} of each year, the last local date the table holds for {this_year}"))
    return out


def fam_ercot_levels(this_year):
    """ERCOT's hub average: the year's average real-time price (record low or high), the share of intervals at USD 100
    or more (trend), and the West hub's basis to the hub average (trend)."""
    d = ercot_rtm()
    out = []
    g = d[d["node"] == "HB_HUBAVG"]
    yearly = [{"period": int(y), "value": float(s["value"].mean()), "n": int(len(s))} for y, s in g.groupby("year")]
    mark_complete(yearly, expected=lambda p: intervals_in_year(p, 96))
    note_series("ercot hubavg yearly mean", yearly)
    full = [x for x in yearly if x["period"] < this_year]
    for high in (True, False):
        r = test_record(full, "year", high=high)
        if r:
            ex = g[g["year"].isin([int(r["period"]), int(r["previous_period"])])][["year", "ts_utc", "value"]].rename(columns={"year": "period"})
            out.append(_claim("average_price_year", f"ercot-hubavg-average-price-record-{'high' if high else 'low'}", "ercot", "ERCOT, the hub average",
                              "THE YEAR'S AVERAGE PRICE", "the year's mean real-time price at the hub average, over its 15-minute intervals", "USD per MWh", 2,
                              yearly, r, ["ercot_all_hub_prices_history"], ex, {"op": "mean", "period": r["period"], "compare_period": r["previous_period"]}))
    hi = [{"period": int(y), "value": float((s["value"] >= 100).mean() * 100), "n": int(len(s))} for y, s in g.groupby("year")]
    mark_complete(hi, expected=lambda p: intervals_in_year(p, 96))
    note_series("ercot hubavg share >= 100", hi)
    c = test_trend([x for x in hi if x["period"] < this_year], 30000, 2, "percent of intervals", this_year)
    if c:
        y0, y1 = int(c["first_year"]), int(c["last_year"])
        ex = g[g["year"].isin([y0, y1])][["year", "ts_utc", "value"]].rename(columns={"year": "period"})
        out.append(_claim("hours_above_100_year", "ercot-hubavg-intervals-at-100-or-more", "ercot", "ERCOT, the hub average",
                          "INTERVALS AT USD 100 OR MORE", "share of the year's 15-minute intervals with a real-time price of USD 100 per MWh or more at the hub average",
                          "percent of intervals", 2, hi, c, ["ercot_all_hub_prices_history"], ex, {"op": "share_at_least", "threshold": 100, "period": y1, "compare_period": y0}))
    # the West hub's basis: the median 15-minute difference West minus hub average
    w = d[d["node"] == "HB_WEST"][["ts_utc", "value", "year"]].merge(g[["ts_utc", "value"]].rename(columns={"value": "hubavg"}), on="ts_utc")
    w["basis"] = w["value"] - w["hubavg"]
    basis = [{"period": int(y), "value": float(s["basis"].median()), "n": int(len(s))} for y, s in w.groupby("year")]
    mark_complete(basis, expected=lambda p: intervals_in_year(p, 96))
    note_series("ercot west basis", basis)
    c = test_trend([x for x in basis if x["period"] < this_year], 30000, 2, "USD per MWh", this_year)
    if c:
        y0, y1 = int(c["first_year"]), int(c["last_year"])
        ex = w[w["year"].isin([y0, y1])][["year", "ts_utc", "value", "hubavg", "basis"]].rename(columns={"year": "period"})
        out.append(_claim("west_basis_year", "ercot-west-hub-basis-by-year", "ercot", "ERCOT, the West hub against the hub average",
                          "THE WEST HUB'S DISCOUNT", "the year's median 15-minute difference between the West hub's real-time price and the hub average's",
                          "USD per MWh", 2, basis, c, ["ercot_all_hub_prices_history"], ex, {"op": "median", "column": "basis", "period": y1, "compare_period": y0}))
    return out


def fam_ercot_da_premium(this_year):
    """The day-ahead premium at the hub average: the year's median hourly day-ahead price minus the hour's mean real-time price."""
    rt = ercot_rtm()
    g = rt[rt["node"] == "HB_HUBAVG"].copy()
    g["hour_utc"] = pd.to_datetime(g["ts_utc"], utc=True).dt.floor("h")
    h = g.groupby(["hour_utc", "year"], as_index=False)["value"].mean().rename(columns={"value": "rt"})
    da = ercot_dam()
    da = da[da["node"] == "HB_HUBAVG"][["hour_utc", "value"]].rename(columns={"value": "da"})
    j = h.merge(da, on="hour_utc")
    j["premium"] = j["da"] - j["rt"]
    j["ts_utc"] = j["hour_utc"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    yearly = [{"period": int(y), "value": float(s["premium"].median()), "n": int(len(s))} for y, s in j.groupby("year")]
    mark_complete(yearly, expected=lambda p: intervals_in_year(p, 24))
    note_series("ercot da premium", yearly)
    c = test_trend([x for x in yearly if x["period"] < this_year], 8000, 2, "USD per MWh", this_year)
    if not c:
        return []
    y0, y1 = int(c["first_year"]), int(c["last_year"])
    ex = j[j["year"].isin([y0, y1])][["year", "ts_utc", "da", "rt", "premium"]].rename(columns={"year": "period"})
    return [_claim("da_premium_year", "ercot-hubavg-day-ahead-premium-by-year", "ercot", "ERCOT, the hub average",
                   "THE DAY-AHEAD PREMIUM", "the year's median hour of the day-ahead price minus the hour's mean real-time price at the hub average",
                   "USD per MWh", 2, yearly, c, ["ercot_all_hub_prices_history"], ex, {"op": "median", "column": "premium", "period": y1, "compare_period": y0})]


def fam_peak_premium(this_year):
    d = peak_premium()
    m = d[d["variable"] == "peak_minus_midday_median"].set_index("year")["value"]
    n = d[d["variable"] == "n_intervals"].set_index("year")["value"]
    yearly = [{"period": int(y), "value": float(m[y]), "n": int(n.get(y, 0))} for y in sorted(m.index)]
    mark_complete(yearly, expected=lambda p: intervals_in_year(p, 96))
    note_series("ercot peak premium", yearly)
    c = test_trend([x for x in yearly if x["period"] < this_year], 30000, 2, "USD per MWh", this_year)
    if not c:
        return []
    y0, y1 = int(c["first_year"]), int(c["last_year"])
    ex = d[d["year"].isin([y0, y1]) & d["variable"].isin(["peak_minus_midday_median", "peak_median", "midday_median", "n_intervals"])][["year", "variable", "value"]].rename(columns={"year": "period"})
    return [_claim("peak_premium_year", "ercot-peak-premium-by-year", "ercot", "ERCOT, the hub average",
                   "THE PEAK PREMIUM", "the year's median evening-peak real-time price minus its median midday price at the hub average (ercot_peak_premium_annual)",
                   "USD per MWh", 2, yearly, c, ["ercot_peak_premium_annual"], ex, {"op": "value_of", "variable": "peak_minus_midday_median", "period": y1, "compare_period": y0})]


def fam_fuel(this_year):
    """Henry Hub's yearly average (record), the share of trading days under USD 2.00 (record), and Brent minus WTI
    (record), each over the table's full history and over this year's window."""
    d = henry_hub()
    out = []
    hh = d[d["entity"] == "eia:henry_hub"]
    yearly = [{"period": int(y), "value": float(s["value"].mean()), "n": int(len(s))} for y, s in hh.groupby("year")]
    mark_complete(yearly)
    note_series("henry hub yearly mean", yearly)
    full = [x for x in yearly if x["period"] < this_year]
    for high in (False, True):
        r = test_record(full, "year", high=high)
        if r:
            ex = hh[hh["year"].isin([int(r["period"]), int(r["previous_period"])])][["year", "date", "value"]].rename(columns={"year": "period"})
            out.append(_claim("henry_hub_year", f"henry-hub-yearly-average-record-{'high' if high else 'low'}", "us", "Henry Hub",
                              "HENRY HUB'S YEAR", "the year's mean daily Henry Hub spot price", "USD per MMBtu", 2, yearly, r, ["eia_fuel_spot_prices"], ex,
                              {"op": "mean", "period": r["period"], "compare_period": r["previous_period"]}))
    low = [{"period": int(y), "value": float((s["value"] < 2.0).mean() * 100), "n": int(len(s))} for y, s in hh.groupby("year")]
    mark_complete(low)
    note_series("henry hub days under 2", low)
    r = test_record([x for x in low if x["period"] < this_year], "year", high=True)
    if r:
        ex = hh[hh["year"].isin([int(r["period"]), int(r["previous_period"])])][["year", "date", "value"]].rename(columns={"year": "period"})
        out.append(_claim("henry_hub_under_2", "henry-hub-days-under-2-dollars", "us", "Henry Hub",
                          "DAYS UNDER TWO DOLLARS", "share of the year's trading days with a Henry Hub spot price below USD 2.00", "percent of trading days", 1, low, r,
                          ["eia_fuel_spot_prices"], ex, {"op": "share_below", "threshold": 2.0, "period": r["period"], "compare_period": r["previous_period"]}))
    # this year's window for Henry Hub: 1 January to the last date held
    cut = hh.loc[hh["year"] == this_year, "date"].max()
    w = hh[hh["date"].str[5:] <= cut[5:]]
    windows = [{"period": int(y), "value": float(s["value"].mean()), "n": int(len(s))} for y, s in w.groupby("year")]
    mark_complete(windows)
    note_series("henry hub window", windows)
    for high in (False, True):
        r = test_record(windows, "year", high=high, recent=[this_year])
        if r:
            ex = w[w["year"].isin([int(r["period"]), int(r["previous_period"])])][["year", "date", "value"]].rename(columns={"year": "period"})
            out.append(_claim("henry_hub_window", f"henry-hub-this-year-record-{'high' if high else 'low'}", "us", "Henry Hub",
                              "HENRY HUB, THIS YEAR SO FAR", f"the mean daily Henry Hub spot price from 1 January to {day_words(cut)}", "USD per MMBtu", 2, windows, r,
                              ["eia_fuel_spot_prices"], ex, {"op": "mean", "period": r["period"], "compare_period": r["previous_period"]},
                              note=f"the window is 1 January to {cut} of each year"))
    # Brent minus WTI, by year
    b = d[d["entity"] == "eia:brent"][["date", "year", "value"]].rename(columns={"value": "brent"})
    wti = d[d["entity"] == "eia:wti_cushing"][["date", "value"]].rename(columns={"value": "wti"})
    j = b.merge(wti, on="date")
    j["spread"] = j["brent"] - j["wti"]
    sp = [{"period": int(y), "value": float(s["spread"].mean()), "n": int(len(s))} for y, s in j.groupby("year")]
    mark_complete(sp)
    note_series("brent minus wti yearly", sp)
    for high in (True, False):
        r = test_record([x for x in sp if x["period"] < this_year], "year", high=high)
        if r:
            ex = j[j["year"].isin([int(r["period"]), int(r["previous_period"])])][["year", "date", "brent", "wti", "spread"]].rename(columns={"year": "period"})
            out.append(_claim("brent_wti_year", f"brent-minus-wti-yearly-record-{'high' if high else 'low'}", "world", "Brent against WTI",
                              "BRENT OVER WTI", "the year's mean of the daily Brent spot price minus the WTI Cushing spot price, on days both are held", "USD per barrel", 2, sp, r,
                              ["eia_fuel_spot_prices"], ex, {"op": "mean", "column": "spread", "period": r["period"], "compare_period": r["previous_period"]}))
    cutj = j.loc[j["year"] == this_year, "date"].max()
    wj = j[j["date"].str[5:] <= cutj[5:]]
    wsp = [{"period": int(y), "value": float(s["spread"].mean()), "n": int(len(s))} for y, s in wj.groupby("year")]
    mark_complete(wsp)
    note_series("brent minus wti window", wsp)
    for high in (True, False):
        r = test_record(wsp, "year", high=high, recent=[this_year])
        if r:
            ex = wj[wj["year"].isin([int(r["period"]), int(r["previous_period"])])][["year", "date", "brent", "wti", "spread"]].rename(columns={"year": "period"})
            out.append(_claim("brent_wti_window", f"brent-minus-wti-this-year-record-{'high' if high else 'low'}", "world", "Brent against WTI",
                              "BRENT OVER WTI, THIS YEAR SO FAR", f"the mean of the daily Brent spot price minus the WTI Cushing spot price from 1 January to {day_words(cutj)}, on days both are held",
                              "USD per barrel", 2, wsp, r, ["eia_fuel_spot_prices"], ex, {"op": "mean", "column": "spread", "period": r["period"], "compare_period": r["previous_period"]},
                              note=f"the window is 1 January to {cutj} of each year"))
    return out


def fam_caiso_curtailment(this_year):
    """CAISO's curtailed wind and solar: the record month, this year's window, and the yearly share of output (trend)."""
    d = caiso_curtailment()
    cut = d[d["variable"].isin(["curtailed_solar_mwh", "curtailed_wind_mwh"])]
    daily = cut.pivot_table(index="date", columns="variable", values="value", aggfunc="sum")
    daily = daily.dropna(subset=["curtailed_solar_mwh", "curtailed_wind_mwh"]).reset_index()
    daily["curtailed"] = daily["curtailed_solar_mwh"] + daily["curtailed_wind_mwh"]
    daily["month"], daily["year"] = daily["date"].str[:7], daily["date"].str[:4].astype(int)
    out = []
    monthly = [{"period": m, "value": float(s["curtailed"].sum()), "n": int(len(s))} for m, s in daily.groupby("month")]
    mark_complete(monthly, expected=days_in_month)
    note_series("caiso curtailment monthly", monthly)
    r = test_record(monthly, "month", high=True, recent=recent_months(monthly))
    if r:
        ex = daily[daily["month"].isin([r["period"], r["previous_period"]])][["month", "date", "curtailed_solar_mwh", "curtailed_wind_mwh", "curtailed"]].rename(columns={"month": "period"})
        out.append(_claim("curtailment_record_month", "caiso-curtailment-record-month", "caiso", "CAISO",
                          "THE MOST CURTAILED MONTH", "the month's curtailed wind and solar output, MWh (caiso_curtailment_daily, solar and wind, all causes)", "MWh", 0,
                          monthly, r, ["caiso_curtailment_daily"], ex, {"op": "sum", "column": "curtailed", "period": r["period"], "compare_period": r["previous_period"]}, grain="month"))
    cutd = daily.loc[daily["year"] == this_year, "date"].max()
    w = daily[daily["date"].str[5:] <= cutd[5:]]
    exp_days = (dt.date(this_year, int(cutd[5:7]), int(cutd[8:10])) - dt.date(this_year, 1, 1)).days + 1
    windows = [{"period": int(y), "value": float(s["curtailed"].sum()), "n": int(len(s))} for y, s in w.groupby("year")]
    mark_complete(windows, expected=lambda p: exp_days)
    note_series("caiso curtailment window", windows)
    r = test_record(windows, "year", high=True, recent=[this_year])
    if r:
        ex = w[w["year"].isin([int(r["period"]), int(r["previous_period"])])][["year", "date", "curtailed_solar_mwh", "curtailed_wind_mwh", "curtailed"]].rename(columns={"year": "period"})
        out.append(_claim("curtailment_window", "caiso-curtailment-this-year", "caiso", "CAISO",
                          "CURTAILMENT, THIS YEAR SO FAR", f"curtailed wind and solar output from 1 January to {day_words(cutd)}, MWh", "MWh", 0, windows, r,
                          ["caiso_curtailment_daily"], ex, {"op": "sum", "column": "curtailed", "period": r["period"], "compare_period": r["previous_period"]},
                          note=f"the window is 1 January to {cutd} of each year"))
    gen = d[d["variable"].isin(["solar_generation_mwh", "wind_generation_mwh"])].pivot_table(index="date", columns="variable", values="value", aggfunc="sum").dropna().reset_index()
    gen["generation"] = gen["solar_generation_mwh"] + gen["wind_generation_mwh"]
    j = daily.merge(gen[["date", "generation"]], on="date")
    yearly = [{"period": int(y), "value": float(s["curtailed"].sum() / (s["curtailed"].sum() + s["generation"].sum()) * 100), "n": int(len(s))} for y, s in j.groupby("year")]
    mark_complete(yearly, expected=lambda p: 366 if intervals_in_year(p, 1) == 366 else 365)
    note_series("caiso curtailment share yearly", yearly)
    c = test_trend([x for x in yearly if x["period"] < this_year], 330, 2, "percent of output", this_year)
    if c:
        y0, y1 = int(c["first_year"]), int(c["last_year"])
        ex = j[j["year"].isin([y0, y1])][["year", "date", "curtailed", "generation"]].rename(columns={"year": "period"})
        out.append(_claim("curtailment_share_year", "caiso-curtailment-share-by-year", "caiso", "CAISO",
                          "WIND AND SOLAR CURTAILED", "share of the year's wind and solar output that was curtailed: curtailed over curtailed plus generated", "percent of output", 2,
                          yearly, c, ["caiso_curtailment_daily"], ex, {"op": "share_of_sum", "numerator": "curtailed", "denominator_add": "generation", "period": y1, "compare_period": y0}))
    return out


def fam_storage(this_year):
    """Battery discharge: the record month of discharge (ERCOT, CAISO) and the share of ERCOT's discharge delivered in
    the evening, by month (record)."""
    d = storage_daily()
    out = []
    for entity, grid, words in (("eia930:ERCO", "ercot", "ERCOT"), ("caiso:ISO", "caiso", "CAISO")):
        g = d[(d["entity"] == entity) & (d["variable"] == "mwh_discharged")].drop_duplicates("date")
        monthly = [{"period": m, "value": float(s["value"].sum()), "n": int(len(s))} for m, s in g.groupby("month")]
        mark_complete(monthly, expected=days_in_month)
        note_series(f"storage discharge monthly {grid}", monthly)
        r = test_record(monthly, "month", high=True, recent=recent_months(monthly))
        if r:
            ex = g[g["month"].isin([r["period"], r["previous_period"]])][["month", "date", "value"]].rename(columns={"month": "period"})
            table = "storage_daily_cycle"
            out.append(_claim("storage_record_month", f"{grid}-battery-discharge-record-month", grid, words,
                              "THE MOST BATTERY DISCHARGE IN A MONTH", f"the month's battery discharge in {words}, MWh, summed from the daily cycle table", "MWh", 0,
                              monthly, r, [table], ex, {"op": "sum", "period": r["period"], "compare_period": r["previous_period"]}, grain="month"))
        this_month = max(s["period"] for s in monthly)
        c = test_trend_months([x for x in monthly if x["period"] < this_month or x["complete"]], 28, 0, "MWh", this_month if not monthly[-1]["complete"] else "2099-12")
        if c:
            m0, m1 = c["first_year"], c["last_year"]
            ex = g[g["month"].isin([m0, m1])][["month", "date", "value"]].rename(columns={"month": "period"})
            out.append(_claim("storage_discharge_months", f"{grid}-battery-discharge-by-month", grid, words,
                              "BATTERY DISCHARGE, MONTH BY MONTH", f"the month's battery discharge in {words}, MWh, summed from the daily cycle table", "MWh", 0,
                              monthly, c, ["storage_daily_cycle"], ex, {"op": "sum", "period": m1, "compare_period": m0}, grain="month",
                              note="the two ends of the series are different months of the year; every complete month between them is on the chart"))
    h = storage_hourly()
    h = h[h["value"] > 0]
    evening = []
    for m, s in h.groupby("month"):
        evening.append({"period": m, "value": float(s.loc[s["hour"].between(17, 21), "value"].sum() / s["value"].sum() * 100), "n": int(s["date"].nunique())})
    mark_complete(evening, expected=days_in_month)
    note_series("ercot storage evening share monthly", evening)
    this_month = max(s["period"] for s in evening)
    c = test_trend_months(evening, 28, 1, "percent of discharge", this_month if not evening[-1]["complete"] else "2099-12")
    if c:
        m0, m1 = c["first_year"], c["last_year"]
        ex = h[h["month"].isin([m0, m1])][["month", "ts_utc", "hour", "value"]].rename(columns={"month": "period"})
        ex["evening"] = ex["hour"].between(17, 21).astype(int)
        out.append(_claim("storage_evening_months", "ercot-battery-evening-share-by-month", "ercot", "ERCOT",
                          "BATTERY DISCHARGE IN THE EVENING, MONTH BY MONTH", "share of the month's battery discharge (hourly net battery output above zero) delivered from 5 PM to 10 PM local",
                          "percent of discharge", 1, evening, c, ["eia930_all_storage"], ex,
                          {"op": "share_of_sum", "numerator_flag": "evening", "period": m1, "compare_period": m0}, grain="month",
                          note="the two ends of the series are different months of the year; every complete month between them is on the chart"))
    for high in (True, False):
        r = test_record(evening, "month", high=high, recent=recent_months(evening))
        if r:
            ex = h[h["month"].isin([r["period"], r["previous_period"]])][["month", "ts_utc", "hour", "value"]].rename(columns={"month": "period"})
            ex["evening"] = ex["hour"].between(17, 21).astype(int)
            out.append(_claim("storage_evening_share", f"ercot-battery-evening-share-record-{'high' if high else 'low'}", "ercot", "ERCOT",
                              "BATTERY DISCHARGE IN THE EVENING", "share of the month's battery discharge (hourly net battery output above zero) delivered from 5 PM to 10 PM local",
                              "percent of discharge", 1, evening, r, ["eia930_all_storage"], ex,
                              {"op": "share_of_sum", "numerator_flag": "evening", "period": r["period"], "compare_period": r["previous_period"]}, grain="month"))
    return out


def fam_queues(this_year):
    """The interconnection queues as LBNL records them (through 2025): MW entered by year (record), the share of each
    cohort's MW withdrawn by the data's end (trend over cohorts 2010 to 2019), and the median wait from entry to
    operation for the projects that reached it (trend over cohorts 2010 to 2019)."""
    d = lbnl()
    out = []
    last_year = int(d["q_year"].max())
    for region, g in d.groupby("region"):
        grid = region.lower()
        entered = [{"period": int(y), "value": float(s["capacity_mw"].sum()), "n": int(len(s))} for y, s in g.groupby("q_year") if y >= 2005]
        mark_complete(entered, expected=lambda p: 1)
        note_series(f"queue entered {region}", entered)
        r = test_record(entered, "year", high=True, recent=[last_year, last_year - 1])
        if r:
            ex = g[g["q_year"].isin([int(r["period"]), int(r["previous_period"])])][["q_year", "entity_id", "type_clean", "q_status", "capacity_mw"]].rename(columns={"q_year": "period", "capacity_mw": "value"})
            out.append(_claim("queue_entries_year", f"{grid}-queue-entries-record-year", grid, region,
                              "THE QUEUE'S BIGGEST YEAR", f"MW of generation and storage that entered {region}'s interconnection queue in the year, every status, as LBNL's Queued Up data file records it", "MW", 0,
                              entered, r, ["lbnl_interconnection_queue"], ex, {"op": "sum", "period": r["period"], "compare_period": r["previous_period"]},
                              note=f"LBNL's 2026 edition holds entries through {last_year}"))
        cohorts = g[(g["q_year"] >= 2010) & (g["q_year"] <= last_year - 6)]
        wd = []
        for y, s in cohorts.groupby("q_year"):
            wd.append({"period": int(y), "value": float(s.loc[s["q_status"] == "withdrawn", "capacity_mw"].sum() / s["capacity_mw"].sum() * 100), "n": int(len(s))})
        mark_complete(wd, expected=lambda p: 1)
        note_series(f"queue withdrawn {region}", wd)
        c = test_trend(wd, 20, 1, "percent of the cohort's MW", last_year - 5, count_rule="floor")
        if c:
            y0, y1 = int(c["first_year"]), int(c["last_year"])
            ex = cohorts[cohorts["q_year"].isin([y0, y1])][["q_year", "entity_id", "type_clean", "q_status", "capacity_mw"]].rename(columns={"q_year": "period", "capacity_mw": "value"})
            ex["withdrawn"] = (ex["q_status"] == "withdrawn").astype(int)
            out.append(_claim("queue_withdrawn_cohort", f"{grid}-queue-withdrawn-share-by-cohort", grid, region,
                              "TILL QUEUE DO US PART, BY COHORT", f"share of the MW that entered {region}'s queue in the year and had withdrawn by the end of {last_year} (cohorts at least six years old)",
                              "percent of the cohort's MW", 1, wd, c, ["lbnl_interconnection_queue"], ex,
                              {"op": "share_of_sum", "numerator_flag": "withdrawn", "period": y1, "compare_period": y0}))
        op = cohorts[(cohorts["q_status"] == "operational") & cohorts["on_date"].notna() & cohorts["q_date"].notna()].copy()
        op["wait_years"] = (pd.to_datetime(op["on_date"], errors="coerce") - pd.to_datetime(op["q_date"], errors="coerce")).dt.days / 365.25
        op = op.dropna(subset=["wait_years"])
        waits = [{"period": int(y), "value": float(s["wait_years"].median()), "n": int(len(s))} for y, s in op.groupby("q_year")]
        mark_complete(waits, expected=lambda p: 1)
        note_series(f"queue wait {region}", waits)
        c = test_trend(waits, 15, 2, "years", last_year - 5, count_rule="floor")
        if c:
            y0, y1 = int(c["first_year"]), int(c["last_year"])
            ex = op[op["q_year"].isin([y0, y1])][["q_year", "entity_id", "type_clean", "q_date", "on_date", "wait_years"]].rename(columns={"q_year": "period"})
            out.append(_claim("queue_wait_years", f"{grid}-queue-wait-to-operation-by-cohort", grid, region,
                              "THE WAIT TO OPERATION", f"median years from queue entry to commercial operation for the projects of the year's cohort that reached it in {region}'s queue (cohorts at least six years old)",
                              "years", 2, waits, c, ["lbnl_interconnection_queue"], ex, {"op": "median", "column": "wait_years", "period": y1, "compare_period": y0}))
    return out


FAMILIES = [fam_ercot_negative, fam_ercot_levels, fam_ercot_da_premium, fam_peak_premium, fam_fuel, fam_caiso_curtailment, fam_storage, fam_queues]


# ---------------------------------------------------------------------------------------------------------------------
# the headline: one operation on the extract, mirrored in Python and in Stata
# ---------------------------------------------------------------------------------------------------------------------
def headline_python(df, spec):
    """The headline number recomputed from extract.csv's rows, the mirror of check.do."""
    p = df[df["period"].astype(str) == str(spec["period"])]
    col = spec.get("column", "value")
    op = spec["op"]
    if op == "share_below":
        return float((p[col] < spec["threshold"]).sum() / len(p) * 100)
    if op == "share_at_least":
        return float((p[col] >= spec["threshold"]).sum() / len(p) * 100)
    if op == "mean":
        return float(p[col].mean())
    if op == "median":
        return float(p[col].median())
    if op == "sum":
        return float(p[col].sum())
    if op == "value_of":
        return float(p.loc[p["variable"] == spec["variable"], "value"].iloc[0])
    if op == "share_of_sum":
        if "numerator_flag" in spec:
            return float(p.loc[p[spec["numerator_flag"]] == 1, col].sum() / p[col].sum() * 100)
        num = p[spec["numerator"]].sum()
        return float(num / (num + p[spec["denominator_add"]].sum()) * 100)
    raise ValueError(op)


def do_text(f, expected):
    """check.do: the owner's rules (findings_common.do_file): no line continuation, one empty line between commands
    outside a loop and none inside, every numeric variable destrung with force. Reads extract.csv and reproduces the
    headline; then reads series.csv and lists the series."""
    s = f["headline"]
    col = s.get("column", "value")
    per = s["period"]
    cmp_ = s["compare_period"]
    numeric = [c for c in f["extract_columns"] if c not in ("ts_utc", "date", "entity_id", "type_clean", "q_status", "variable", "q_date", "on_date")]
    pv = f"period == {per}"
    cv = f"period == {cmp_}"
    lines = [
        f"* ERW findings hunt of {DAY}: {f['slug']}. Reproduces the headline number from extract.csv.",
        f"* Expected headline value: {expected:.6f} {f['unit']} ({f['label']}, {f['region_words']}, period {per}).",
        f"* The comparison period {cmp_} is in the same file; its value is printed after the headline.",
        "* The CSV's first four lines are comments; its fifth line holds the variable names.",
        "clear all",
        'import delimited "extract.csv", varnames(5) rowrange(6) stringcols(_all) clear',
        *common.do_destring(numeric),
        *common.do_sentinels(numeric),
    ]
    if f["grain"] == "month":
        lines.append("* period is the month as YYYYMM.")
    op = s["op"]
    for label, cond in (("headline", pv), ("comparison", cv)):
        if op in ("share_below", "share_at_least"):
            sign = "<" if op == "share_below" else ">="
            lines += [f"count if {cond} & {col} {sign} {s['threshold']}", "scalar part = r(N)", f"count if {cond}", "scalar whole = r(N)",
                      f'display "{label} ({cond}), percent of rows: " part / whole * 100']
        elif op == "mean":
            lines += [f"summarize {col} if {cond}", f'display "{label} ({cond}), mean: " r(mean)']
        elif op == "median":
            lines += [f"summarize {col} if {cond}, detail", f'display "{label} ({cond}), median: " r(p50)']
        elif op == "sum":
            lines += [f"summarize {col} if {cond}", f'display "{label} ({cond}), sum: " r(sum)']
        elif op == "value_of":
            lines += [f'summarize value if {cond} & variable == "{s["variable"]}"', f'display "{label} ({cond}), the table\'s own value: " r(mean)']
        elif op == "share_of_sum" and "numerator_flag" in s:
            lines += [f"summarize {col} if {cond} & {s['numerator_flag']} == 1", "scalar part = r(sum)", f"summarize {col} if {cond}", "scalar whole = r(sum)",
                      f'display "{label} ({cond}), percent of the sum: " part / whole * 100']
        elif op == "share_of_sum":
            lines += [f"summarize {s['numerator']} if {cond}", "scalar part = r(sum)", f"summarize {s['denominator_add']} if {cond}", "scalar other = r(sum)",
                      f'display "{label} ({cond}), percent: " part / (part + other) * 100']
    lines += [
        "* The series the chart draws: one row a period (series.csv, the same four comment lines).",
        'import delimited "series.csv", varnames(5) rowrange(6) stringcols(_all) clear',
        *common.do_destring(["period", "value", "n_observations", "complete"]),
        *common.do_sentinels(["period", "value", "n_observations", "complete"]),
        "sort period",
        "list period value n_observations complete, noobs",
    ]
    return common.do_file(lines)


# ---------------------------------------------------------------------------------------------------------------------
# words: the fact line and the caption, computed from the numbers
# ---------------------------------------------------------------------------------------------------------------------
def fmtv(v, f):
    return f"{common.fmt(v, f['decimals'])} {f['unit']}"


def period_words(p, grain):
    if grain == "month":
        return dt.date(int(str(p)[:4]), int(str(p)[5:7]), 1).strftime("%B %Y")
    return str(p)


def fact_of(f):
    c, g = f["claim"], f["grain"]
    if c["kind"] == "record":
        return (f"{f['region_words']}: {f['label']} was {fmtv(c['value'], f)} in {period_words(c['period'], g)}, the {'highest' if c['direction'] == 'high' else 'lowest'} of the "
                f"{len(c['periods'])} complete {g}s held; the previous {c['direction']} was {fmtv(c['previous'], f)} in {period_words(c['previous_period'], g)}.")
    return (f"{f['region_words']}: {f['label']}, {fmtv(c['last'], f)} in {period_words(c['last_year'], g)}, {c['direction']} from {fmtv(c['first'], f)} in {period_words(c['first_year'], g)}. "
            f"The direction holds in {c['years_held']} of the {c['years_after']} complete {g}s after {period_words(c['first_year'], g)}.")


def source_line(f):
    return f"Source: the rows for {f['region_words']} of the ERW table{'s' if len(f['tables']) > 1 else ''} {', '.join(f['tables'])} (license: {f['license']}). Computed by warehouse/analysis/findings/hunt_oct20.py; method {METHOD}."


def caption_of(f):
    """A LinkedIn caption in the ERW's voice: the fact, how it was checked, the source and the table. Under 1,300
    characters, no em dash, no point of view, no recommendation."""
    c, g = f["claim"], f["grain"]
    t = {x["name"]: x["words"] for x in c["tests"]}
    if c["kind"] == "record":
        head = f"{f['title'].capitalize()}. {fact_of(f)}"
        checks = [f"Checked before it was drafted: {t['history long enough']}; {t['a margin over the previous record']}; {t['no gap in the window']}."]
    else:
        head = f"{f['title'].capitalize()}. {fact_of(f)}"
        checks = [f"Checked five ways before it was drafted: {t['holds in more than one year']}; {t['survives a change of window']}; {t['half the change remains without the first year']}; "
                  f"{t['at least one typical yearly move']}; {t['sample large enough']}."]
    body = [head, *checks, "The claim states a change; it does not say what caused it." + (f" {f['note']}." if f.get("note") else "")]
    tail = f"Source: {', '.join(f['tables'])}, as the ERW holds it. ERW table: {f['tables'][0]}."
    text = "\n\n".join(body + [tail])
    if len(text) > 1300:                                # trim the checks first, never the fact or the source
        short = [head, "Checked against the table's full history before it was drafted; the tests are in the finding's record.", body[2], tail]
        text = "\n\n".join(short)
    if len(text) > 1300:
        text = "\n\n".join([head, tail])
    assert len(text) <= 1300, len(text)
    assert chr(0x2014) not in text
    return text


# ---------------------------------------------------------------------------------------------------------------------
# the files
# ---------------------------------------------------------------------------------------------------------------------
def comment_header(f, what):
    return (f"# Energy Research Warehouse (ERW): findings hunt of {DAY}, finding {f['slug']} ({f['region_words']}): {what}\n"
            f"# Computed {common.now_iso()} by warehouse/analysis/findings/hunt_oct20.py {VERSION}; method {METHOD}\n"
            f"# Sources: ERW table{'s' if len(f['tables']) > 1 else ''} {', '.join(f['tables'])}; license {f['license']}; each table's own header names its publisher's report and retrieval time\n"
            f"# {f['label']} ({f['unit']})\n")


def period_key(p, grain):
    return int(str(p).replace("-", "")[:6]) if grain == "month" else int(p)


def write_finding(f, out_dir, rank):
    import brand_chart
    folder = os.path.join(out_dir, f["slug"])
    os.makedirs(folder, exist_ok=True)
    c = f["claim"]
    ex = f["extract"].copy()
    ex["period"] = ex["period"].map(lambda p: period_key(p, f["grain"]))
    ex = ex.sort_values(["period"] + [col for col in ("ts_utc", "date", "entity_id") if col in ex.columns]).reset_index(drop=True)
    f["extract_columns"] = list(ex.columns)
    spec = dict(f["headline"], period=period_key(f["headline"]["period"], f["grain"]), compare_period=period_key(f["headline"]["compare_period"], f["grain"]))
    f["headline"] = spec
    expected = c["value"] if c["kind"] == "record" else c["last"]
    got = headline_python(ex, spec)
    if not math.isclose(got, expected, rel_tol=1e-9, abs_tol=1e-9):
        raise AssertionError(f"{f['slug']}: the extract gives {got}, the claim says {expected}")
    with open(os.path.join(folder, "extract.csv"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(comment_header(f, "the exact rows the headline number comes from, at the table's own grain, for the headline period and the comparison period"))
        ex.to_csv(fh, index=False, lineterminator="\n")
    ser = pd.DataFrame([{"period": period_key(s["period"], f["grain"]), "value": s["value"], "n_observations": s["n"], "complete": int(s["complete"])} for s in f["series"]])
    with open(os.path.join(folder, "series.csv"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(comment_header(f, "one row a period: the measure, its observations, whether the period is complete"))
        ser.to_csv(fh, index=False, lineterminator="\n")
    with open(os.path.join(folder, "check.do"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(do_text(f, expected))
    caption = caption_of(f)
    with open(os.path.join(folder, "caption.md"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(caption + "\n")
    record = {
        "slug": f["slug"], "day": DAY, "rank": rank, "state": "new", "state_history": [], "internal": f["license"] != "public" or any(t in ("large_load_statements",) for t in f["tables"]),
        "family": f["family"], "kind": c["kind"], "grid": f["grid"], "region_words": f["region_words"], "title": f["title"], "label": f["label"],
        "unit": f["unit"], "decimals": f["decimals"], "grain": f["grain"], "fact": fact_of(f), "note": f.get("note", ""),
        "shown_before": f.get("shown") or "", "tables": f["tables"], "license": f["license"], "source_line": source_line(f),
        "headline": dict(spec, value=expected, compare_value=c["previous"] if c["kind"] == "record" else c["first"], expected_in_do_file=round(expected, 6)),
        "claim": {k: v for k, v in c.items() if k != "tests"}, "tests": c["tests"], "strength": c["strength"],
        "series": [{"period": s["period"], "value": s["value"], "n": s["n"], "complete": bool(s["complete"])} for s in f["series"]],
        "files": {"extract": "extract.csv", "series": "series.csv", "do": "check.do", "caption": "caption.md", "chart_square": "chart_square.png", "chart_wide": "chart_wide.png"},
        "extract_rows": int(len(ex)), "caption": caption, "computed_at": common.now_iso(), "hunt_version": VERSION, "method": METHOD,
    }
    brand_chart.render(record, os.path.join(folder, "chart_square.png"), "square")
    brand_chart.render(record, os.path.join(folder, "chart_wide.png"), "wide")
    with open(os.path.join(folder, "finding.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(record, fh, indent=1, ensure_ascii=False, default=common.round6)
        fh.write("\n")
    return record


def write_index(out_dir, records, summary):
    with open(os.path.join(out_dir, "index.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"day": DAY, "hunt_version": VERSION, "computed_at": common.now_iso(), "summary": summary,
                   "findings": [{k: r[k] for k in ("slug", "rank", "state", "title", "fact", "kind", "family", "grid", "internal", "tables", "license", "strength", "shown_before")} for r in records]},
                  fh, indent=1, ensure_ascii=False, default=common.round6)
        fh.write("\n")


# ---------------------------------------------------------------------------------------------------------------------
# the hunt
# ---------------------------------------------------------------------------------------------------------------------
def run(keep=10, out_dir=None, dry_run=False, log=print, now=None):
    now = now or dt.datetime.now(dt.timezone.utc)
    this_year = now.year
    out_dir = out_dir or OUT_DEFAULT
    blocked = hunt.blocked_grids()
    candidates, failed = [], []
    for fam in FAMILIES:
        try:
            got = fam(this_year)
        except common.NoData as exc:
            failed.append({"family": fam.__name__, "reason": f"a table is not on this machine: {exc}"})
            log(f"  {fam.__name__}: NOT RUN, {exc}")
            continue
        for f in got:
            if f["grid"] in blocked:
                f["reason"] = f"its grid ({f['grid']}) needs a license or is held; never drafted"
            elif not f["claim"]["passed"]:
                f["reason"] = "fails " + "; ".join(t["name"] for t in f["claim"]["tests"] if not t["passed"])
            else:
                f["reason"] = "passes"
            candidates.append(f)
    passing = [f for f in candidates if f["reason"] == "passes"]
    passing.sort(key=lambda f: (1 if f.get("shown") else 0, -f["claim"]["strength"], f["slug"]))
    kept, per_family, per_topic = [], {}, {}
    for f in passing:
        topic = (f["family"], f["grid"])
        if per_family.get(f["family"], 0) >= 2:
            f["reason"] = "passes; beyond the two strongest of its family"
            continue
        if per_topic.get(topic, 0) >= 1 and f["family"] in ("negative_share_year", "negative_share_window"):
            f["reason"] = "passes; one hub of this grid already tells the story"
            continue
        if len(kept) >= keep:
            f["reason"] = f"passes; beyond the {keep} kept"
            continue
        per_family[f["family"]] = per_family.get(f["family"], 0) + 1
        per_topic[topic] = per_topic.get(topic, 0) + 1
        kept.append(f)
    for f in candidates:
        c = f["claim"]
        head = f"{c['period']}: {common.fmt(c['value'], f['decimals'])} (prev {c['previous_period']}: {common.fmt(c['previous'], f['decimals'])})" if c["kind"] == "record" \
            else f"{c['first_year']}: {common.fmt(c['first'], f['decimals'])} to {c['last_year']}: {common.fmt(c['last'], f['decimals'])}"
        log(f"  {'KEEP ' if f in kept else '     '}{f['slug']:<55} {c['kind']:<6} strength {c['strength']:>6.2f}  {head}  [{f['reason']}]")
    records = []
    if not dry_run:
        os.makedirs(out_dir, exist_ok=True)
        for i, f in enumerate(kept, 1):
            records.append(write_finding(f, out_dir, i))
            log(f"  wrote {f['slug']} ({records[-1]['extract_rows']} extract rows)")
    summary = {"candidates": len(candidates), "passing": len(passing), "kept": len(kept), "failed": failed, "blocked_grids": sorted(blocked), "this_year": this_year,
               "candidates_list": [{"slug": f["slug"], "family": f["family"], "kind": f["claim"]["kind"], "strength": f["claim"]["strength"], "reason": f["reason"],
                                    "tests": [{"name": t["name"], "passed": t["passed"]} for t in f["claim"]["tests"]]} for f in candidates]}
    if not dry_run:
        write_index(out_dir, records, summary)
    if dry_run and os.environ.get("ERW_HUNT_DEBUG"):
        for label, rows in SERIES_LOG:
            log(f"  series {label}: {rows}")
    log(f"hunt_oct20 {VERSION}: {len(candidates)} candidate claims, {len(passing)} pass their tests, {len(kept)} kept{' (dry run: nothing written)' if dry_run else ''}; {len(failed)} family(ies) not run")
    return {"summary": summary, "kept": kept, "records": records}


def check(out_dir=None, log=print):
    """Every finding's check.do logic, run in Python on its own extract.csv; exit 1 when one does not reproduce."""
    out_dir = out_dir or OUT_DEFAULT
    bad = 0
    for slug in sorted(os.listdir(out_dir)):
        folder = os.path.join(out_dir, slug)
        if not os.path.isfile(os.path.join(folder, "finding.json")):
            continue
        with open(os.path.join(folder, "finding.json"), encoding="utf-8") as fh:
            r = json.load(fh)
        ex = pd.read_csv(os.path.join(folder, "extract.csv"), comment="#")
        got = headline_python(ex, r["headline"])
        cmp_ = headline_python(ex, dict(r["headline"], period=r["headline"]["compare_period"]))
        ok = math.isclose(got, r["headline"]["value"], rel_tol=1e-6, abs_tol=1e-6) and math.isclose(cmp_, r["headline"]["compare_value"], rel_tol=1e-6, abs_tol=1e-6)
        bad += 0 if ok else 1
        log(f"  {'ok  ' if ok else 'FAIL'} {slug}: headline {got:.6f} (expected {r['headline']['value']:.6f}); comparison {cmp_:.6f} (expected {r['headline']['compare_value']:.6f})")
    log(f"check: {bad} finding(s) failed")
    return bad


def set_state(slug, state, out_dir=None, log=print):
    out_dir = out_dir or OUT_DEFAULT
    if state not in STATES:
        raise SystemExit(f"state is one of {', '.join(STATES)}")
    path = os.path.join(out_dir, slug, "finding.json")
    with open(path, encoding="utf-8") as fh:
        r = json.load(fh)
    r["state_history"].append({"from": r["state"], "state": state, "at": common.now_iso()})
    r["state"] = state
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(r, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    idx_path = os.path.join(out_dir, "index.json")
    with open(idx_path, encoding="utf-8") as fh:
        idx = json.load(fh)
    for x in idx["findings"]:
        if x["slug"] == slug:
            x["state"] = state
    with open(idx_path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(idx, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    log(f"{slug}: {state}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    h = sub.add_parser("hunt")
    h.add_argument("--keep", type=int, default=10)
    h.add_argument("--out", default=None)
    h.add_argument("--dry-run", action="store_true")
    c = sub.add_parser("check")
    c.add_argument("out", nargs="?", default=None)
    s = sub.add_parser("state")
    s.add_argument("slug")
    s.add_argument("state", choices=STATES)
    s.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    if a.cmd == "hunt":
        run(keep=a.keep, out_dir=a.out, dry_run=a.dry_run)
        return 0
    if a.cmd == "check":
        return 1 if check(a.out) else 0
    set_state(a.slug, a.state, a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
