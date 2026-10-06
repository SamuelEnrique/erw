#!/usr/bin/env python3
"""Supply and trade: is the market tighter or looser than last week, last year and normal for the season (session 134).

Energy Research Warehouse (ERW). The page /supply reads the site's own file; this builder writes it from tables
already in warehouse/output (no request is made). Method: docs/methods/supply_and_trade.md.

    python warehouse/derived/supply_page.py                      # site/data/supply.json
    python warehouse/derived/supply_page.py --hours-to DIR       # also save the grids' hours it read (for the next run)
    python warehouse/derived/supply_page.py --hours-from DIR     # read the grids' hours saved before, not EIA's workbooks
    python warehouse/derived/supply_page.py --no-burn            # leave the fuel burned for power out (no workbooks here)
    python warehouse/derived/supply_page.py --site-dir DIR       # a trial: the file under DIR

EVERY SERIES IS SET AGAINST THREE THINGS, each a value actually held:

    last week (or month)   the value one step before the latest
    last year              a weekly series: the value 364 days before the latest (the same weekday, 52 weeks back), or the
                           nearest within NEAR days; a monthly series: the same month a year before
    the five-year average  the mean of the values 52, 104, 156, 208 and 260 weeks before the latest (monthly: the same
                           month of the five years before), given only when all five are held; with their lowest and highest

THE SURPRISE is about the change, as a desk reads a weekly report: the latest change (latest less the step before)
less the mean of the same change in the five years before. It is marked when the change is outside the lowest and
highest of those five changes. With no analysts' consensus held (those polls are licensed), the five-year average
change is the open stand-in, and the page says "against the five-year average change", never "against expectations".

THE SEASONAL BAND of a series, for its chart: for each date of the current calendar year and on to its end, the value
this year (where held), the value 52 weeks before, and the mean, lowest and highest of the five years before.

FUEL BURNED FOR POWER is derived, not reported: each grid's hourly generation from natural gas, coal and oil
(EIA-930, the energy mix's held hours: warehouse/derived/mix_profile.py) added up by local day when every hour of the
day is held, times a stated heat rate, in the fuel's own unit by a stated heat content (HEAT_RATE, HEAT_CONTENT). A
week is the mean of its seven days, ending Friday as the gas storage week does, and is given only when all seven are
held. The seven grids together are the sum when all seven hold the week. It is an estimate of burn in the seven ISO
grids, not of the whole country's.

NEXT RELEASE of each weekly report: the standing weekday and time (Eastern), or the alternate date the publisher lists
for that week (warehouse/metadata/release_schedule.json, written by warehouse/connectors/release_schedule.py).
"""

import argparse
import datetime as dt
import json
import os
import re
import sys
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, HERE)
import iso_prices as ip  # noqa: E402

SITE = os.path.join(ROOT, "site")
SCHEDULE = os.path.join(ROOT, "warehouse", "metadata", "release_schedule.json")
NEAR = 3                 # days: how far from the date asked the weekly value compared with may be
YEARS = 5
SPARK = 52
STALE_BURN = 14          # days: a grid's fuel whose newest whole week is older than the newest of any by more than this is shown as not held
HEAT_RATE = {"natural_gas": 7.6, "coal": 10.6, "oil": 11.0}                 # MMBtu per MWh, stated: about the fleet averages EIA publishes (Electric Power Annual, Table 8.1)
HEAT_CONTENT = {"natural_gas": (1.037e6, "bcf/d"), "coal": (19.0e3, "thousand short tons/d"), "oil": (5.8e3, "kbbl/d")}   # MMBtu per unit shown, stated
FUEL_WORDS = {"natural_gas": "Natural gas", "coal": "Coal", "oil": "Oil"}
PAUSED = "paused while terms are reviewed"
LICENSED = "licensed source needed"

GROUPS = [
    dict(id="gasstor", title="Natural gas in storage, weekly", band=True),
    dict(id="stocks", title="Crude and product stocks, weekly", band=True),
    dict(id="prod", title="Production"),
    dict(id="refining", title="Refining, weekly"),
    dict(id="trade", title="Crude and product trade, weekly"),
    dict(id="gastrade", title="Natural gas trade, monthly"),
    dict(id="burn", title="Fuel burned for power in the seven grids, weekly, derived"),
    dict(id="cleared", title="Day-ahead energy cleared, by grid"),
    dict(id="position", title="Managed money positioning, weekly"),
]
# entity: (group, label, at, sense) ; sense: +1 more of it is a looser market, -1 tighter, 0 no reading
WEEKLY = {
    "eia:NW2_EPG0_SWO_R48_BCF": ("gasstor", "Working gas in storage", "Lower 48", 1), "eia:NW2_EPG0_SWO_R31_BCF": ("gasstor", "Working gas in storage", "East", 1),
    "eia:NW2_EPG0_SWO_R32_BCF": ("gasstor", "Working gas in storage", "Midwest", 1), "eia:NW2_EPG0_SWO_R34_BCF": ("gasstor", "Working gas in storage", "Mountain", 1),
    "eia:NW2_EPG0_SWO_R35_BCF": ("gasstor", "Working gas in storage", "Pacific", 1), "eia:NW2_EPG0_SWO_R33_BCF": ("gasstor", "Working gas in storage", "South Central", 1),
    "eia:NW2_EPG0_SSO_R33_BCF": ("gasstor", "Working gas in storage", "South Central, salt", 1), "eia:NW2_EPG0_SNO_R33_BCF": ("gasstor", "Working gas in storage", "South Central, nonsalt", 1),
    "eia:WCESTUS1": ("stocks", "Commercial crude oil stocks", "United States", 1), "eia:W_EPC0_SAX_YCUOK_MBBL": ("stocks", "Crude oil stocks", "Cushing, Oklahoma", 1),
    "eia:WGTSTUS1": ("stocks", "Gasoline stocks", "United States", 1), "eia:WDISTUS1": ("stocks", "Distillate stocks", "United States", 1),
    "eia:WCSSTUS1": ("stocks", "Strategic Petroleum Reserve", "United States", 0),
    "eia:WCRFPUS2": ("prod", "Crude oil production", "United States, weekly", 1), "eia:W_EPC0_FPF_R48_MBBLD": ("prod", "Crude oil production", "Lower 48, weekly", 1),
    "eia:W_EPC0_FPF_SAK_MBBLD": ("prod", "Crude oil production", "Alaska, weekly", 1),
    "eia:WPULEUS3": ("refining", "Refinery utilization", "United States", 0), "eia:W_NA_YUP_R10_PER": ("refining", "Refinery utilization", "East Coast (PADD 1)", 0),
    "eia:W_NA_YUP_R20_PER": ("refining", "Refinery utilization", "Midwest (PADD 2)", 0), "eia:W_NA_YUP_R30_PER": ("refining", "Refinery utilization", "Gulf Coast (PADD 3)", 0),
    "eia:W_NA_YUP_R40_PER": ("refining", "Refinery utilization", "Rocky Mountain (PADD 4)", 0), "eia:W_NA_YUP_R50_PER": ("refining", "Refinery utilization", "West Coast (PADD 5)", 0),
    "eia:WCRRIUS2": ("refining", "Crude runs", "United States", 0), "eia:WCRRIP12": ("refining", "Crude runs", "East Coast (PADD 1)", 0), "eia:WCRRIP22": ("refining", "Crude runs", "Midwest (PADD 2)", 0),
    "eia:WCRRIP32": ("refining", "Crude runs", "Gulf Coast (PADD 3)", 0), "eia:WCRRIP42": ("refining", "Crude runs", "Rocky Mountain (PADD 4)", 0), "eia:WCRRIP52": ("refining", "Crude runs", "West Coast (PADD 5)", 0),
    "eia:WCRIMUS2": ("trade", "Crude oil imports", "United States", 1), "eia:WCREXUS2": ("trade", "Crude oil exports", "United States", -1), "eia:WCRNTUS2": ("trade", "Crude oil net imports", "United States", 1),
    "eia:WRPIMUS2": ("trade", "Product imports", "United States", 1), "eia:WRPEXUS2": ("trade", "Product exports", "United States", -1), "eia:WRPNTUS2": ("trade", "Product net imports", "United States", 1),
    "eia:WTTNTUS2": ("trade", "Crude and product net imports", "United States", 1), "eia:W_EPM0F_IM0_NUS-Z00_MBBLD": ("trade", "Gasoline imports", "United States", 1),
    "eia:WDIIMUS2": ("trade", "Distillate imports", "United States", 1), "eia:WDIEXUS2": ("trade", "Distillate exports", "United States", -1),
}
POSITIONS = {"cftc:067651": "WTI crude oil", "cftc:06765T": "Brent Last Day", "cftc:023651": "Henry Hub natural gas", "cftc:111659": "RBOB gasoline"}
BASINS = {"AP": "Appalachia", "BK": "Bakken", "EF": "Eagle Ford", "HA": "Haynesville", "PM": "Permian", "R48": "Rest of the Lower 48", "AN": "Anadarko", "NI": "Niobrara"}
MAJOR_LNG = 5000.0       # MMcf: a terminal is listed by name when it shipped at least this much in a month of the last twelve


def slug(key):
    return re.sub(r"[^a-z0-9]+", "-", key.lower()).strip("-")


def read(name):
    path = os.path.join(ip.OUT_DIR, name + ".csv")
    t = pd.read_csv(path, skiprows=ip.header_rows(path), usecols=["entity", "variable", "ts_utc", "value", "unit", "node"])
    t["day"] = pd.to_datetime(t["ts_utc"].str[:10]).dt.date
    return t


def series_of(t, entity, variable=None):
    g = t[(t["entity"] == entity) & ((t["variable"] == variable) if variable else True)]
    return {d: float(v) for d, v in zip(g["day"], g["value"]) if pd.notna(v)}


# ---------------------------------------------------------------------------
# a series against last week, last year and the five-year average
# ---------------------------------------------------------------------------

def at(series, days, target, freq):
    """The value held at a date: exactly (monthly), or the nearest within NEAR days (weekly). (date, value) or None."""
    if freq == "M":
        return (target, series[target]) if target in series else None
    cands = [d for d in days if abs((d - target).days) <= NEAR]
    if not cands:
        return None
    d = min(cands, key=lambda x: abs((x - target).days))
    return d, series[d]


def back(d, k, freq):
    """The date k years before d: 52 weeks at a time for a weekly series, the same month for a monthly one."""
    return dt.date(d.year - k, d.month, 1) if freq == "M" else d - dt.timedelta(days=364 * k)


def step(d, freq, n=1):
    """The date n steps before d."""
    if freq == "W":
        return d - dt.timedelta(days=7 * n)
    y, m = d.year, d.month - n
    while m < 1:
        y, m = y - 1, m + 12
    return dt.date(y, m, 1)


def compare(series, freq):
    """The figures of one series, {date: value}, freq W or M. None for an empty series."""
    if not series:
        return None
    days = sorted(series)
    d0, v0 = days[-1], series[days[-1]]
    r = lambda x: round(float(x), 4)      # noqa: E731
    out = dict(last=dict(t=d0.isoformat(), v=r(v0)))
    prev = at(series, days, step(d0, freq), freq)
    out["prev"] = None if prev is None else dict(t=prev[0].isoformat(), v=r(prev[1]), ch=r(v0 - prev[1]))
    year = at(series, days, back(d0, 1, freq), freq)
    out["year"] = None if year is None else dict(t=year[0].isoformat(), v=r(year[1]), ch=r(v0 - year[1]), pct=r(100 * (v0 - year[1]) / year[1]) if year[1] > 0 else None)
    five = [at(series, days, back(d0, k, freq), freq) for k in range(1, YEARS + 1)]
    out["avg5"] = None
    if all(x is not None for x in five):
        vals = [x[1] for x in five]
        avg = sum(vals) / YEARS
        out["avg5"] = dict(v=r(avg), lo=r(min(vals)), hi=r(max(vals)), ch=r(v0 - avg), pct=r(100 * (v0 - avg) / avg) if avg > 0 else None, outside=bool(v0 < min(vals) or v0 > max(vals)))
    out["change"] = None
    if prev is not None:
        changes = []
        for x in five:
            before = None if x is None else at(series, days, step(x[0], freq), freq)
            changes.append(None if before is None else x[1] - before[1])
        ch = v0 - prev[1]
        item = dict(v=r(ch), avg5=None, lo=None, hi=None, surprise=None, outside=False)
        if all(c is not None for c in changes):
            avg = sum(changes) / YEARS
            item.update(avg5=r(avg), lo=r(min(changes)), hi=r(max(changes)), surprise=r(ch - avg), outside=bool(ch < min(changes) or ch > max(changes)))
        out["change"] = item
    tail = days[-SPARK:]
    out["spark"] = dict(t=[d.isoformat() for d in tail], v=[r(series[d]) for d in tail])
    out["season"] = season(series, days, d0, freq)
    return out


def season(series, days, d0, freq):
    """For each date of the latest year, and on to its end: this year, a year before, and the five years' mean, low and high."""
    if freq == "M":
        dates = [dt.date(d0.year, m, 1) for m in range(1, 13)]
    else:
        first = d0
        while (first - dt.timedelta(days=7)).year == d0.year:
            first -= dt.timedelta(days=7)
        dates, d = [], first
        while d.year == d0.year:
            dates.append(d)
            d += dt.timedelta(days=7)
    cur, last, avg, lo, hi = [], [], [], [], []
    for d in dates:
        c = at(series, days, d, freq) if d <= d0 else None
        cur.append(None if c is None else round(c[1], 4))
        y = at(series, days, back(d, 1, freq), freq)
        last.append(None if y is None else round(y[1], 4))
        five = [at(series, days, back(d, k, freq), freq) for k in range(1, YEARS + 1)]
        if all(x is not None for x in five):
            vals = [x[1] for x in five]
            avg.append(round(sum(vals) / YEARS, 4)); lo.append(round(min(vals), 4)); hi.append(round(max(vals), 4))
        else:
            avg.append(None); lo.append(None); hi.append(None)
    return dict(t=[d.isoformat() for d in dates], cur=cur, last=last, avg=avg, lo=lo, hi=hi)


# ---------------------------------------------------------------------------
# the rows
# ---------------------------------------------------------------------------

class Page:
    def __init__(self):
        self.rows = []

    def add(self, group, key, label, at_, unit, freq, series, sense=0, source="", note=None, extra=None):
        row = dict(id=slug(key), group=group, label=label, at=at_, unit=unit, freq=freq, sense=sense, source=source, status="ok")
        c = compare(series, freq)
        if c is None:
            row.update(status="not_held", note=note or "The warehouse holds no value of this series yet.")
        else:
            row.update(c)
        if extra:
            row.update(extra)
        self.rows.append(row)

    def grey(self, group, key, label, at_, status, note, unit=""):
        self.rows.append(dict(id=slug(key), group=group, label=label, at=at_, unit=unit, freq="", sense=0, status=status, note=note))


def weekly_rows(p, log):
    gas, pet = read("eia_gas_storage_weekly"), read("eia_petroleum_supply_weekly")
    both = pd.concat([gas, pet])
    units = {"kbbl": ("million bbl", 0.001), "kbbl/d": ("thousand bbl/d", 1.0), "bcf": ("bcf", 1.0), "pct": ("percent", 1.0)}
    for entity, (group, label, where, sense) in WEEKLY.items():
        g = both[both["entity"] == entity]
        unit, scale = units[g["unit"].iloc[0]] if len(g) else ("", 1.0)
        src = "EIA, Weekly Natural Gas Storage Report (eia_gas_storage_weekly)" if group == "gasstor" else "EIA, Weekly Petroleum Status Report (eia_petroleum_supply_weekly)"
        p.add(group, entity, label, where, unit, "W", {d: v * scale for d, v in series_of(both, entity).items()}, sense, src)
    p.grey("prod", "gasprod|weekly", "Natural gas production", "Lower 48, weekly", "licensed",
           "EIA publishes no weekly gas production of its own: the weekly supply figures in its Natural Gas Weekly Update are S&P Global's. Source that would supply it: S&P Global Commodity Insights. Monthly production by region is below.", "bcf/d")
    log(f"  weekly: {len(WEEKLY)} series")


def monthly_rows(p, log):
    b = read("eia_basin_production_monthly")
    for kind, variable, unit, words in (("COPR", "crude_production", "thousand bbl/d", "Crude oil production"), ("NGMP", "gas_marketed_production", "bcf/d", "Natural gas marketed production")):
        for code, name in BASINS.items():
            s = series_of(b, f"eia:{kind}{code}", variable)
            if s:
                p.add("prod", f"eia:{kind}{code}", words, f"{name}, monthly", unit, "M", s, 1, "EIA, Short-Term Energy Outlook, history only (eia_basin_production_monthly)")
    t = read("eia_gas_trade_monthly")
    days_in = lambda d: (dt.date(d.year + (d.month == 12), d.month % 12 + 1, 1) - d).days      # noqa: E731
    per_day = lambda s: {d: v / 1000.0 / days_in(d) for d, v in s.items()}                     # noqa: E731  (MMcf in the month to bcf a day)
    src = "EIA, U.S. natural gas imports and exports by point of entry and exit (eia_gas_trade_monthly); the month's volume over its days"
    lng = series_of(t, "eia:N9133US2")
    p.add("gastrade", "eia:N9133US2", "LNG exports", "all terminals, monthly", "bcf/d", "M", per_day(lng), -1, src)
    terminals = {}
    for entity, g in t[t["entity"].str.contains("_ENG_Y") & t["entity"].str.endswith("-Z00_MMCF")].groupby("entity"):
        s = {d: float(v) for d, v in zip(g["day"], g["value"])}
        terminals[entity] = (re.sub(r"\s+Liquefied Natural Gas Exports.*$", "", g["node"].iloc[0]).strip(), s)
    newest = max(lng) if lng else None
    recent = lambda s: [v for d, v in s.items() if newest and (newest - d).days <= 366]         # noqa: E731
    major = {e: x for e, x in terminals.items() if recent(x[1]) and max(recent(x[1])) >= MAJOR_LNG}
    for entity, (name, s) in sorted(major.items(), key=lambda kv: -kv[1][1].get(newest, 0)):
        p.add("gastrade", entity, "LNG exports", f"{name}, monthly", "bcf/d", "M", per_day(s), -1, src)
    other = {d: v - sum(x[1].get(d, 0.0) for x in major.values()) for d, v in lng.items()}
    p.add("gastrade", "erw:lng_other_points", "LNG exports", "every other point of exit together, monthly", "bcf/d", "M", per_day(other), -1, src + "; the total less the terminals named")
    for entity, label, where, sense in (("eia:N9132MX2", "Pipeline exports", "to Mexico, monthly", -1), ("eia:N9132CN2", "Pipeline exports", "to Canada, monthly", -1),
                                        ("eia:N9102CN2", "Pipeline imports", "from Canada, monthly", 1), ("eia:N9103US2", "LNG imports", "all terminals, monthly", 1)):
        p.add("gastrade", entity, label, where, "bcf/d", "M", per_day(series_of(t, entity)), sense, src)
    log(f"  monthly: {len(major)} LNG terminals by name, {len(terminals) - len(major)} small points together")


def position_rows(p, log):
    t = read("cftc_cot_positions")
    for entity, name in POSITIONS.items():
        net, lng, sht, oi = (series_of(t, entity, v) for v in ("managed_money_net", "managed_money_long", "managed_money_short", "open_interest"))
        d0 = max(net) if net else None
        extra = dict(long=lng.get(d0), short=sht.get(d0), open_interest=oi.get(d0), net_share_pct=round(100 * net[d0] / oi[d0], 2) if d0 and oi.get(d0) else None) if d0 else None
        if net:
            w = sorted(net)[-156:]            # where the latest sits in the last three years of weeks
            vals = [net[d] for d in w]
            extra["three_year"] = dict(lo=min(vals), hi=max(vals), pos=round((net[d0] - min(vals)) / (max(vals) - min(vals)), 4) if max(vals) > min(vals) else None, n=len(w))
        p.add("position", entity, "Managed money net position", f"{name}, NYMEX futures", "contracts", "W", net, 0, "CFTC, Commitments of Traders, Disaggregated report, futures only (cftc_cot_positions)", extra=extra)
    p.grey("position", "ice|brent", "Managed money net position", "Brent, ICE Futures Europe", "licensed",
           "ICE publishes its own report for ICE Brent, and its terms of use forbid copying or republishing its site's content without written permission. Source that would supply it: ICE, under license. The Brent row above is the far smaller NYMEX contract the CFTC reports.", "contracts")


def burn_rows(p, log, hours_from=None, hours_to=None):
    """Fuel burned for power by grid and by week, from the energy mix's held hours."""
    import mix_profile as mp
    mp.GROUPS = dict(mp.GROUPS, oil=["OIL"])       # oil on its own beside the mix's eight sources ("other" still holds it)
    weekly = {}
    for grid, g in mp.GRIDS.items():
        if hours_from:
            x = pd.read_parquet(os.path.join(hours_from, f"hours_{grid}.parquet"))
        else:
            x, _ = mp.hours_of(grid, log)
            if hours_to:
                os.makedirs(hours_to, exist_ok=True)
                x.to_parquet(os.path.join(hours_to, f"hours_{grid}.parquet"))
        per_day = x.groupby("day").agg(n=("held", "size"), ok=("held", "sum"))
        full = set(per_day.index[[(r.n == r.ok) and r.n == mp.expected_hours(d, g["tz"]) for d, r in per_day.iterrows()]])
        d = x[x["day"].isin(full)]
        for fuel in HEAT_RATE:
            if fuel not in d or not (d[fuel] > 0).any():
                continue
            by = d.groupby("day")[fuel]
            named = by.apply(lambda c: bool(c.notna().all()))         # a day counts only when every hour names the fuel: a blank hour is never read as zero
            mwh = by.apply(lambda c: c.clip(lower=0).sum())[named]
            per_unit, _ = HEAT_CONTENT[fuel]
            daily = {dt.date.fromisoformat(k): float(v) * HEAT_RATE[fuel] / per_unit for k, v in mwh.items()}
            wk = {}
            for day, v in daily.items():
                end = day + dt.timedelta(days=(4 - day.weekday()) % 7)        # the Friday that ends the day's week
                wk.setdefault(end, []).append(v)
            weekly[(grid, fuel)] = {end: sum(v) / 7 for end, v in wk.items() if len(v) == 7}
    src = "derived from EIA-930 hourly generation by source (the energy mix's held hours) at stated heat rates"
    newest = max(max(w) for w in weekly.values() if w)
    for fuel, words in FUEL_WORDS.items():
        unit = HEAT_CONTENT[fuel][1]
        grids = [g for g in mp.GRIDS if (g, fuel) in weekly]
        if not grids:
            p.grey("burn", f"burn|{fuel}", f"{words} burned for power", "the seven grids", "not_held", "The grids' files do not itemize this fuel in the hours read.", unit)
            continue
        if len(grids) == len(mp.GRIDS):
            common = set.intersection(*(set(weekly[(g, fuel)]) for g in grids))
            p.add("burn", f"burn|all|{fuel}", f"{words} burned for power", "the seven grids together", unit, "W", {d: sum(weekly[(g, fuel)][d] for g in grids) for d in common}, -1, src)
        for g in grids:
            w = weekly[(g, fuel)]
            if not w or max(w) < newest - dt.timedelta(days=STALE_BURN):
                since = f"the last whole week held ended {max(w).isoformat()}" if w else "no whole week is held"
                p.grey("burn", f"burn|{g}|{fuel}", f"{words} burned for power", mp.GRIDS[g]["name"], "not_held",
                       f"The hourly file leaves this fuel blank for this grid in hours of the latest weeks: {since}. A blank hour is not read as zero.", unit)
                continue
            p.add("burn", f"burn|{g}|{fuel}", f"{words} burned for power", mp.GRIDS[g]["name"], unit, "W", w, -1, src)
    log(f"  burn: {len(weekly)} grid and fuel series")


def cleared_rows(p):
    for grid in ("ERCOT", "CAISO", "NYISO", "ISO-NE", "SPP"):
        p.grey("cleared", f"cleared|{grid}", "Day-ahead energy cleared", grid, "not_held", "Not pulled yet: session 134 did not reach the operators' day-ahead cleared volumes. Each operator publishes them in its own report.", "MWh/d")
    p.grey("cleared", "cleared|MISO", "Day-ahead energy cleared", "MISO", "paused", "MISO's terms forbid automated access to its site; its pulls are paused.", "MWh/d")
    p.grey("cleared", "cleared|PJM", "Day-ahead energy cleared", "PJM", "licensed", "PJM publishes its data under a license and an account the ERW does not hold.", "MWh/d")


def calendar(now=None):
    """Each weekly report's next release (Eastern time): its standing day, or the date its publisher moved that week's to.
    The file also carries each report's rule and alternate dates, so the page works the next date out when it is read."""
    if not os.path.exists(SCHEDULE):
        return dict(retrieved_at=None, reports=[])
    with open(SCHEDULE, encoding="utf-8") as f:
        sched = json.load(f)
    tz = ZoneInfo(sched.get("timezone", "America/New_York"))
    now = now or dt.datetime.now(tz)
    out = []
    for r in sched["reports"]:
        d = now.date() - dt.timedelta(days=now.weekday()) + dt.timedelta(days=r["weekday"])      # this week's standing day, past or not
        for _ in range(60):
            monday = d - dt.timedelta(days=d.weekday())
            alt = [e for e in r["exceptions"] if monday <= dt.date.fromisoformat(e["date"]) <= monday + dt.timedelta(days=6)]
            day, clock = (dt.date.fromisoformat(alt[0]["date"]), alt[0]["time"]) if alt else (d, r["time"])
            h, m = map(int, clock.split(":"))
            if dt.datetime(day.year, day.month, day.day, h, m, tzinfo=tz) > now:
                break
            d += dt.timedelta(days=7)
        out.append(dict(id=r["id"], name=r["name"], publisher=r["publisher"], page=r["page"], covers=r["covers"],
                        rule=f"{['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'][r['weekday']]}s at {r['time']} Eastern", read=r["read"],
                        weekday=r["weekday"], time=r["time"], exceptions=[dict(date=e["date"], time=e["time"], holiday=e["holiday"]) for e in r["exceptions"]],
                        next=f"{day.isoformat()}T{clock}", moved=f"moved from the standing day for {alt[0]['holiday']}" if alt else None))
    return dict(retrieved_at=sched["retrieved_at"], timezone=str(tz), reports=out)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Supply and trade: the site's file")
    ap.add_argument("--site-dir", default=SITE)
    ap.add_argument("--hours-from")
    ap.add_argument("--hours-to")
    ap.add_argument("--no-burn", action="store_true")
    a = ap.parse_args(argv)
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = pd.Timestamp.now(tz="UTC").strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"supply_page_{run_id}.log"))
    p = Page()
    weekly_rows(p, log)
    monthly_rows(p, log)
    if a.no_burn:
        for fuel, words in FUEL_WORDS.items():
            p.grey("burn", f"burn|{fuel}", f"{words} burned for power", "the seven grids", "working", "Not built in this run: the hourly generation files are on a data machine.", HEAT_CONTENT[fuel][1])
    else:
        burn_rows(p, log, a.hours_from, a.hours_to)
    cleared_rows(p)
    position_rows(p, log)
    order = {g["id"]: i for i, g in enumerate(GROUPS)}
    rows = sorted(p.rows, key=lambda r: order[r["group"]])
    sources = sorted({r["source"] for r in rows if r.get("source")})
    rows = [dict(r, source=sources.index(r["source"])) if r.get("source") else r for r in rows]
    body = dict(built=ip.utc_iso(pd.Timestamp.now(tz="UTC")), years=YEARS, near_days=NEAR, heat_rate=HEAT_RATE, heat_content={k: dict(mmbtu_per_unit=v[0], unit=v[1]) for k, v in HEAT_CONTENT.items()},
                groups=GROUPS, sources=sources, rows=rows, calendar=calendar())
    out = os.path.join(a.site_dir, "data", "supply.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(body, f, separators=(",", ":"))
        f.write("\n")
    held = sum(1 for r in rows if r["status"] == "ok")
    print(f"supply: {len(rows)} rows ({held} with values), {os.path.getsize(out):,} bytes")
    log(f"  supply.json: {len(rows)} rows, {held} with values")
    log.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
