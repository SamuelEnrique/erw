#!/usr/bin/env python3
"""The price board and its markets workbench: the files the one page /board reads (session 132).

Energy Research Warehouse (ERW). One page holds what /board, /board/v3, the version 4 work and /markets showed, and
the series session 132 added. This builder reads tables already in warehouse/output (no request is made) and writes
the site's own files:

    site/data/board.json              every row of the board: latest value and its date, the move over a day, a week,
                                      a month and a year, the last 30 points, the one-year range, and the week's table
                                      and spikes the markets page showed
    site/public/board/s/<id>.json     one file a row: its whole history held, for the workbench
    site/public/board/h/<id>.json     one file a power hub or ancillary service: its hourly prices, for the workbench

    python warehouse/derived/board_page.py                 # the site's files
    python warehouse/derived/board_page.py --site-dir DIR  # a trial: the files under DIR

Method, sources, terms and gaps: docs/methods/price_board.md. In short:

A POWER PRICE is a hub's or zone's day-ahead or real-time price. The hourly value of a real-time market is the mean of
the hour's intervals when all of them are held. A daily value is the mean of a complete local operating day (a day
short of an hour is not a day). MISO's prices are paused (warehouse/metadata/paused_sources.csv): its rows are listed
and no value of them is read. PJM's are not held. Nothing is filled, smoothed or estimated anywhere.

FIGURES of a row, from its own series: last (the newest date held); the move against the value held before it (daily
series), and against the newest value held at least 7, 30 and 365 days earlier and no more than SLACK days older than
that (a weekly series has no daily move, a monthly one no daily or weekly move); the lowest and highest value of the
365 days ending on the last, when enough of them are held; the mean of the last 7 and 30 days (daily series).

SPREADS, each a series of its own with the same figures (formulas and the stated heat rates and yields are in FORMULAS).
"""

import argparse
import datetime as dt
import json
import os
import re
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, HERE)
import iso_prices as ip  # noqa: E402
import price_board as pb  # noqa: E402  (read_table, is_peak, nerc_holidays)
import price_board_v4 as v4  # noqa: E402  (the fuels' names, spark, crack_321)

SITE = os.path.join(ROOT, "site")
START = "2019-01-01T00:00:00Z"   # hourly prices are read from here; daily fuels keep the whole history held
HEAT_RATE = 7.0                  # MMBtu/MWh: the spark spread's stated assumption, about a combined-cycle gas plant
COAL_HEAT_RATE = 10.5            # MMBtu/MWh: the dark spread's stated assumption, about the US coal fleet's average
GAS_BACK = 4                     # days: the newest gas trading day up to this many days before the operating day
SLACK = 6                        # days: how much older than asked the value compared with may be
RANGE_MIN = {"D": 180, "W": 26, "M": 9}     # values held of the 365 days for a range to be written
SPARK_POINTS = 30
ISO = {"ercot": ("ERCOT", "America/Chicago"), "caiso": ("CAISO", "America/Los_Angeles"), "nyiso": ("NYISO", "America/New_York"),
       "isone": ("ISO-NE", "America/New_York"), "spp": ("SPP", "America/Chicago")}
MAIN = {"ercot": "HB_HUBAVG", "caiso": "TH_SP15_GEN-APND", "nyiso": "N.Y.C.", "isone": ".H.INTERNAL_HUB", "spp": "SPPNORTH_HUB"}
# the price tables, oldest reading first: a later table's hour replaces an earlier one's for the same hub and market
PRICE_TABLES = ["ercot_all_hub_prices_history", "iso_hub_prices_history", "isone_rtm_zone_prices", "isone_rtm_zone_prices_hourly",
                "nyiso_dam_zone_prices", "nyiso_rtm_zone_prices", "isone_dam_zone_prices", "iso_dam_hub_prices", "iso_rtm_hub_prices"]
PRICE_VARIABLES = {"lmp_dam", "spp_dam", "lmp_rtm", "spp_rtm", "lmp_rtm_15m_mean"}
PER_HOUR = {"PT1H": 1, "PT15M": 4, "PT5M": 12}
HUB_WORDS = {
    "HB_HUBAVG": "Hub average", "HB_BUSAVG": "Bus average", "HB_NORTH": "North hub", "HB_SOUTH": "South hub", "HB_WEST": "West hub", "HB_HOUSTON": "Houston hub",
    "TH_NP15_GEN-APND": "Northern California (NP15)", "TH_SP15_GEN-APND": "Southern California (SP15)", "TH_ZP26_GEN-APND": "Central California (ZP26)",
    "CAPITL": "Capital", "CENTRL": "Central", "DUNWOD": "Dunwoodie", "GENESE": "Genesee", "HUD VL": "Hudson Valley", "LONGIL": "Long Island",
    "MHK VL": "Mohawk Valley", "MILLWD": "Millwood", "N.Y.C.": "New York City", "NORTH": "North", "WEST": "West",
    ".H.INTERNAL_HUB": "Internal hub", ".Z.MAINE": "Maine", ".Z.NEWHAMPSHIRE": "New Hampshire", ".Z.VERMONT": "Vermont", ".Z.CONNECTICUT": "Connecticut",
    ".Z.RHODEISLAND": "Rhode Island", ".Z.SEMASS": "Southeast Massachusetts", ".Z.WCMASS": "Western and Central Massachusetts", ".Z.NEMASSBOST": "Northeast Massachusetts and Boston",
    "SPPNORTH_HUB": "North hub", "SPPSOUTH_HUB": "South hub",
}
# listed, never read: MISO is paused, PJM needs a license the ERW does not hold
MISO_HUBS = [("INDIANA.HUB", "Indiana hub"), ("ARKANSAS.HUB", "Arkansas hub"), ("ILLINOIS.HUB", "Illinois hub"), ("LOUISIANA.HUB", "Louisiana hub"),
             ("MICHIGAN.HUB", "Michigan hub"), ("MINN.HUB", "Minnesota hub"), ("MS.HUB", "Mississippi hub"), ("TEXAS.HUB", "Texas hub")]
PJM_HUBS = [("WESTERN HUB", "Western hub"), ("AEP-DAYTON HUB", "AEP-Dayton hub"), ("N ILLINOIS HUB", "Northern Illinois hub"), ("DOMINION HUB", "Dominion hub"), ("EASTERN HUB", "Eastern hub")]
PAUSED = "paused while terms are reviewed"
LICENSED = "licensed source needed"
MISO_NOTE = "MISO's terms forbid automated access to its site, so the ERW stopped asking for its prices on 4 October 2026 until a person has reviewed the terms. No MISO value is shown."
PJM_NOTE = "PJM publishes its prices under a license and an account the ERW does not hold. Source that would supply them: PJM Data Miner, under PJM's data license."
AS_WORDS = {
    "ercot": {"REGUP": "Regulation up", "REGDN": "Regulation down", "RRS": "Responsive reserve", "NSPIN": "Non-spinning reserve", "ECRS": "Contingency reserve (ECRS)"},
    "caiso": {"as_price_dam_ru": "Regulation up", "as_price_dam_rd": "Regulation down", "as_price_dam_sr": "Spinning reserve", "as_price_dam_nr": "Non-spinning reserve"},
    "nyiso": {"as_price_dam_spin10": "10-minute spinning reserve", "as_price_dam_nsync10": "10-minute non-synchronized reserve", "as_price_dam_op30": "30-minute operating reserve", "as_price_dam_reg": "Regulation"},
    "spp": {"as_price_dam_regup": "Regulation up", "as_price_dam_regdn": "Regulation down", "as_price_dam_spin": "Spinning reserve", "as_price_dam_supp": "Supplemental reserve",
            "as_price_dam_rampup": "Ramp up", "as_price_dam_rampdn": "Ramp down", "as_price_dam_uncup": "Uncertainty up"},
}
AS_REGION = {"AS_CAISO": "CAISO system", "AS_CAISO_EXP": "CAISO expanded system", "NYCA": "New York statewide", "SPP": "SPP system", "SWPW": "SPP West"}
PADD_WORDS = {"U.S.": "United States", "PADD 1": "East Coast (PADD 1)", "PADD 1A": "New England (PADD 1A)", "PADD 1B": "Central Atlantic (PADD 1B)", "PADD 1C": "Lower Atlantic (PADD 1C)",
              "PADD 2": "Midwest (PADD 2)", "PADD 3": "Gulf Coast (PADD 3)", "PADD 4": "Rocky Mountain (PADD 4)", "PADD 5": "West Coast (PADD 5)",
              "PADD 5 EXCEPT CALIFORNIA": "West Coast less California"}
SECTORS = {"ALL": "All sectors", "RES": "Residential", "COM": "Commercial", "IND": "Industrial"}
FORMULAS = {
    "spark": f"day-ahead daily mean at the hub - {HEAT_RATE:g} MMBtu/MWh x Henry Hub (the day's gas price, else the newest trading day's up to {GAS_BACK} days before). Indicative: Henry Hub is in Louisiana, not the gas a plant in this grid burns, and {HEAT_RATE:g} is an assumed heat rate",
    "heat": f"day-ahead daily mean at the hub / Henry Hub (the day's gas price, else the newest trading day's up to {GAS_BACK} days before)",
    "dark": f"the month's mean of the hub's day-ahead daily means (every day of the month held) - {COAL_HEAT_RATE:g} MMBtu/MWh x EIA's US average cost of coal delivered to power plants that month. Indicative: {COAL_HEAT_RATE:g} is an assumed heat rate and the coal cost is a national average",
    "crack_gc": "(2 x Gulf Coast conventional gasoline + 1 x Gulf Coast ultra-low sulfur diesel) x 42 / 3 - WTI at Cushing: three barrels of crude as two of gasoline and one of diesel, per barrel, before any cost",
    "crack_ny": "(2 x New York Harbor conventional gasoline + 1 x New York Harbor ultra-low sulfur diesel) x 42 / 3 - Brent: three barrels of crude as two of gasoline and one of diesel, per barrel, before any cost",
    "brent_wti": "Brent spot - WTI spot at Cushing, on trading days EIA publishes both",
    "da_rt": "day-ahead daily mean - real-time daily mean, same day and hub",
    "battery": "the day's highest hourly price - its lowest hourly price at the hub, on complete operating days",
    "peak_less_off": "the day's on-peak mean - its off-peak mean (on-peak: hours ending 7 to 22 local, Monday to Friday, in CAISO Monday to Saturday; NERC holidays are off-peak)",
}


def slug(key):
    return re.sub(r"[^a-z0-9]+", "-", key.lower()).strip("-")


def day_of(ts_utc):
    return dt.date.fromisoformat(str(ts_utc)[:10])


# ---------------------------------------------------------------------------
# figures of one series
# ---------------------------------------------------------------------------

def stats(series, freq="D"):
    """The figures of one series, {date: value}, freq D, W or M. None for an empty series."""
    if not series:
        return None
    days = sorted(series)
    d0, v0 = days[-1], series[days[-1]]

    def back(n):
        """The newest date held at least n days before the last, no more than SLACK days older than that."""
        cands = [d for d in days if d0 - dt.timedelta(days=n + SLACK) <= d <= d0 - dt.timedelta(days=n)]
        return max(cands) if cands else None

    def move(d):
        if d is None:
            return None
        v = series[d]
        return dict(t=d.isoformat(), v=round(v, 4), ch=round(v0 - v, 4), pct=round(100 * (v0 - v) / v, 2) if v > 0 and v0 >= 0 else None)
    prev = days[-2] if freq == "D" and len(days) > 1 and (d0 - days[-2]).days <= 1 + SLACK else None
    moves = {"d": move(prev), "w": move(back(7)) if freq in ("D", "W") else None,
             "m": move(back(30) if freq != "M" else back(28)), "y": move(back(365))}
    window = [series[d] for d in days if d0 - dt.timedelta(days=365) < d <= d0]
    rng = None
    if len(window) >= RANGE_MIN[freq]:
        lo, hi = min(window), max(window)
        rng = dict(lo=round(lo, 4), hi=round(hi, 4), n=len(window), pos=round((v0 - lo) / (hi - lo), 4) if hi > lo else None)
    out = dict(last=dict(t=d0.isoformat(), v=round(v0, 4)), moves=moves, range=rng)
    if freq == "D":
        for n in (7, 30):
            vals = [series[d] for d in days[-n:] if d0 - dt.timedelta(days=n) < d <= d0]
            out[f"avg{n}"] = dict(v=round(sum(vals) / len(vals), 4), n=len(vals))
        last30 = [series[d] for d in days[-30:] if d0 - dt.timedelta(days=30) < d <= d0]
        out["lo30"], out["hi30"] = round(min(last30), 4), round(max(last30), 4)
    tail = days[-SPARK_POINTS:]
    out["spark"] = dict(t0=tail[0].isoformat(), d=[(d - tail[0]).days for d in tail], v=[round(series[d], 4) for d in tail])
    return out


def series_file(row, series):
    """The whole history of a row, compact: day offsets from the first date, and the values."""
    days = sorted(series)
    return dict(id=row["id"], label=row["label"], at=row.get("at", ""), unit=row["unit"], freq=row["freq"], t0=days[0].isoformat(),
                d=[(d - days[0]).days for d in days], v=[round(series[d], 4) for d in days])


# ---------------------------------------------------------------------------
# power: hourly and daily prices by hub and market
# ---------------------------------------------------------------------------

def to_hourly(df):
    """One table's price rows as hourly values: a Series indexed by (entity, kind, hour), kind da or rt. An hour of a
    sub-hourly market is the mean of its intervals when every one of them is held; MISO's rows are dropped unread."""
    df = df[df["variable"].isin(PRICE_VARIABLES) & ~df["entity"].str.startswith("miso:") & df["value"].notna()]
    if df.empty:
        return pd.Series(dtype=float)
    kind = np.where(df["market"].str.endswith("_dam"), "da", "rt")
    g = (df.assign(kind=kind, hour=df["ts"].dt.floor("h"), per=df["freq"].map(PER_HOUR))
         .groupby(["entity", "kind", "hour"]).agg(v=("value", "mean"), n=("value", "size"), per=("per", "first")))
    return g.loc[g["n"] == g["per"], "v"]


def hourly_store(log, tables=PRICE_TABLES):
    """{(entity, kind): Series of hourly prices indexed by UTC hour}, from every price table held, from START."""
    parts = []
    for name in tables:
        path = os.path.join(ip.OUT_DIR, name + ".csv")
        if not os.path.exists(path):
            log(f"  {name}: not on this machine, skipped")
            continue
        h = to_hourly(pb.read_table(name, since=START))
        log(f"  {name}: {len(h):,} complete hours")
        parts.append(h)
    allh = pd.concat(parts)
    allh = allh[~allh.index.duplicated(keep="last")].sort_index()
    return {key: s.droplevel([0, 1]) for key, s in allh.groupby(level=[0, 1])}


def daily_of(hourly, tz, iso, holidays):
    """The complete local operating days of one hourly series: a frame indexed by date with mean, max, min, and the
    on-peak and off-peak means (NaN on a day with no on-peak hour)."""
    local = pd.Series(hourly.index.tz_convert(tz), index=hourly.index)
    df = pd.DataFrame({"v": hourly.values, "day": local.dt.date.values, "peak": pb.is_peak(local, iso, holidays).values})
    g = df.groupby("day")["v"].agg(["mean", "max", "min", "size"])
    days = pd.to_datetime(pd.Index(g.index))
    expected = ((days + pd.Timedelta(days=1)).tz_localize(tz) - days.tz_localize(tz)) / pd.Timedelta(hours=1)
    g = g[g["size"].values == expected.values.astype(int)]
    full = df[df["day"].isin(set(g.index))]
    g["peak"] = full[full["peak"]].groupby("day")["v"].mean()
    g["offpeak"] = full[~full["peak"]].groupby("day")["v"].mean()
    return g


def col(frame, name):
    return {d: float(v) for d, v in frame[name].items() if pd.notna(v)}


def hourly_file(hid, tz, iso, da, rt, holidays):
    """The hourly prices of a hub (or of an ancillary service, rt None): arrays from the first hour held to the last."""
    held = [s for s in (da, rt) if s is not None and len(s)]
    start, end = min(s.index[0] for s in held), max(s.index[-1] for s in held)
    idx = pd.date_range(start, end, freq="h")
    local = pd.Series(idx.tz_convert(tz), index=idx)
    out = dict(id=hid, tz=tz, t0=int(start.timestamp() // 3600), n=len(idx), pk="".join("1" if p else "0" for p in pb.is_peak(local, iso, holidays).values))
    for name, s in (("da", da), ("rt", rt)):
        if s is not None and len(s):
            vals = s.reindex(idx).round(2)
            out[name] = [None if pd.isna(x) else float(x) for x in vals.values]
    return out


# ---------------------------------------------------------------------------
# spreads
# ---------------------------------------------------------------------------

def gas_on(d, gas, gas_days):
    cands = [g for g in gas_days if d - dt.timedelta(days=GAS_BACK) <= g <= d]
    return gas[max(cands)] if cands else None


def spark(da, gas, heat_rate=HEAT_RATE):
    gas_days = sorted(gas)
    return {d: v - heat_rate * g for d, v in da.items() if (g := gas_on(d, gas, gas_days)) is not None}


def implied_heat_rate(da, gas):
    gas_days = sorted(gas)
    return {d: v / g for d, v in da.items() if (g := gas_on(d, gas, gas_days)) is not None and g > 0}


def month_means(daily):
    """{first day of month: mean of the daily values} for the months whose every day is held."""
    by = {}
    for d, v in daily.items():
        by.setdefault((d.year, d.month), []).append(v)
    out = {}
    for (y, m), vals in by.items():
        n = (dt.date(y + (m == 12), m % 12 + 1, 1) - dt.date(y, m, 1)).days
        if len(vals) == n:
            out[dt.date(y, m, 1)] = sum(vals) / n
    return out


def dark(da, coal, heat_rate=COAL_HEAT_RATE):
    mm = month_means(da)
    return {m: v - heat_rate * coal[m] for m, v in mm.items() if m in coal}


def crack(gasoline, diesel, crude):
    return {d: (2 * gasoline[d] + diesel[d]) * 42 / 3 - crude[d] for d in gasoline if d in diesel and d in crude}


def minus(a, b):
    return {d: a[d] - b[d] for d in a if d in b}


# ---------------------------------------------------------------------------
# the rows
# ---------------------------------------------------------------------------

class Board:
    def __init__(self):
        self.rows, self.series, self.hourly = [], {}, {}

    def add(self, group, key, label, unit, freq, series, at="", code="", tags=None, formula=None, source="", also=None, curve=None, hourly=None, extra=None):
        rid = slug(key)
        if any(r["id"] == rid for r in self.rows):
            raise RuntimeError(f"two rows share the id {rid}")
        row = dict(id=rid, group=group, label=label, at=at, code=code, unit=unit, freq=freq, tags=tags or {}, source=source, status="ok")
        if formula:
            row["formula"] = formula
        if also:
            row["also"] = also
        if curve:
            row["curve"] = curve
        if hourly:
            row["hourly"] = hourly
        if extra:
            row.update(extra)
        s = stats(series, freq)
        if s is None:
            row.update(status="not_held", note="The warehouse holds no value of this series yet.")
        else:
            row.update(s)
            self.series[rid] = series_file(row, series)
        self.rows.append(row)
        return row

    def grey(self, group, key, label, status, note, at="", code="", tags=None, unit=""):
        self.rows.append(dict(id=slug(key), group=group, label=label, at=at, code=code, unit=unit, freq="", tags=tags or {}, status=status, note=note))


def table_daily(name, since=None):
    """{(entity, variable): {date: value}} of a daily, weekly or monthly table, with each pair's unit and node."""
    t = pb.read_table(name, since=since)
    out, meta = {}, {}
    for (entity, variable), g in t.groupby(["entity", "variable"]):
        out[(entity, variable)] = {day_of(ts): float(v) for ts, v in zip(g["ts_utc"], g["value"]) if pd.notna(v)}
        meta[(entity, variable)] = dict(unit=g["unit"].iloc[0], node=g["node"].iloc[0], geo=g["geo"].iloc[0])
    return out, meta


FUT_NOTE = "EIA's NYMEX contracts 1 to 4 end on 5 April 2024 (\"Futures prices after April 5, 2024, are not available\"). Source that would supply the curve: CME Group."
CURVE = dict(status="licensed", note=FUT_NOTE)


def build_power(b, store, holidays, log):
    """Hubs and zones: the day-ahead and real-time rows, on-peak and off-peak, the spreads between markets, the
    battery spread. Returns {(entity, kind): daily frame}."""
    daily = {}
    for (entity, kind), h in store.items():
        iso, node = entity.split(":", 1)
        if iso not in ISO:
            continue
        daily[(entity, kind)] = daily_of(h, ISO[iso][1], iso, holidays)
    for iso, (grid, tz) in ISO.items():
        nodes = sorted({e.split(":", 1)[1] for (e, k) in daily if e.startswith(iso + ":")}, key=lambda n: (n != MAIN[iso], HUB_WORDS.get(n, n)))
        for node in nodes:
            entity, words = f"{iso}:{node}", HUB_WORDS.get(node, node)
            scope = "main" if node == MAIN[iso] else "all"
            hid = slug(entity)
            da_h, rt_h = store.get((entity, "da")), store.get((entity, "rt"))
            b.hourly[hid] = hourly_file(hid, tz, iso, da_h, rt_h, holidays)
            for kind, name in (("da", "day-ahead"), ("rt", "real time")):
                d = daily.get((entity, kind))
                tags = dict(grid=grid, market=kind, scope=scope)
                src = "the grid operator's published prices (iso_hub_prices_history, ercot_all_hub_prices_history and the rolling hub and zone tables)"
                b.add("power", f"{entity}|{kind}", f"{grid} {words}", "USD/MWh", "D", col(d, "mean") if d is not None else {}, at=name, code=node, tags=tags, source=src, hourly=hid)
                if d is not None:
                    b.add("battery", f"{entity}|{kind}|battery", f"{grid} {words}", "USD/MWh", "D", {x: float(r["max"] - r["min"]) for x, r in d.iterrows()},
                          at=name, code=node, tags=tags, formula=FORMULAS["battery"], source=src, extra=dict(hub=hid))
                    if scope == "main":
                        for measure, title in (("peak", "on-peak"), ("offpeak", "off-peak")):
                            b.add("peak", f"{entity}|{kind}|{measure}", f"{grid} {words}", "USD/MWh", "D", col(d, measure), at=f"{name}, {title}", code=node, tags=dict(tags, measure=measure), source=src, extra=dict(hub=hid))
                        both = d.dropna(subset=["peak", "offpeak"])
                        b.add("peak", f"{entity}|{kind}|peak_less_off", f"{grid} {words}", "USD/MWh", "D", {x: float(r["peak"] - r["offpeak"]) for x, r in both.iterrows()},
                              at=f"{name}, on-peak less off-peak", code=node, tags=dict(tags, measure="spread"), formula=FORMULAS["peak_less_off"], source=src, extra=dict(hub=hid))
            da, rt = daily.get((entity, "da")), daily.get((entity, "rt"))
            if da is not None and rt is not None:
                b.add("da_rt", f"{entity}|da_minus_rt", f"{grid} {words}", "USD/MWh", "D", minus(col(da, "mean"), col(rt, "mean")), code=node,
                      tags=dict(grid=grid, scope=scope), formula=FORMULAS["da_rt"], source="the day-ahead and real-time rows above", extra=dict(hub=hid))
        log(f"  {grid}: {len(nodes)} hubs and zones")
    for code, words in MISO_HUBS:
        for kind, name in (("da", "day-ahead"), ("rt", "real time")):
            b.grey("power", f"miso:{code}|{kind}", f"MISO {words}", "paused", MISO_NOTE, at=name, code=code, unit="USD/MWh",
                   tags=dict(grid="MISO", market=kind, scope="main" if code == "INDIANA.HUB" else "all"))
    for code, words in PJM_HUBS:
        for kind, name in (("da", "day-ahead"), ("rt", "real time")):
            b.grey("power", f"pjm:{code}|{kind}", f"PJM {words}", "licensed", PJM_NOTE, at=name, code=code, unit="USD/MWh",
                   tags=dict(grid="PJM", market=kind, scope="main" if code == "WESTERN HUB" else "all"))
    return daily


def build_as(b, holidays, log):
    for iso, table in (("ercot", "ercot_as_prices"), ("caiso", "caiso_as_prices"), ("nyiso", "nyiso_as_prices"), ("spp", "spp_as_prices")):
        grid, tz = ISO[iso]
        if not os.path.exists(os.path.join(ip.OUT_DIR, table + ".csv")):
            # session 166: on the runner NYISO's and SPP's tables are held out of the restore, and ERCOT's is written
            # later in the run; the rows of a table not on the machine are left to page_keep.py, which keeps the
            # held ones (the builder failed here on 7 and 8 October 2026 and the board stayed on 6 October)
            log(f"  {grid} ancillary services: {table} not on this machine, skipped (page_keep.py keeps the held rows)")
            continue
        t = pb.read_table(table, since=START)
        t = t[t["value"].notna()]
        n = 0
        for (entity, variable), g in t.groupby(["entity", "variable"]):
            node = entity.split(":", 1)[1]
            product = AS_WORDS[iso].get(node if iso == "ercot" else variable, variable)
            region = "" if iso == "ercot" else AS_REGION.get(node, HUB_WORDS.get(node, node))
            h = g.set_index("ts")["value"].sort_index()
            h = h[~h.index.duplicated(keep="last")]
            d = daily_of(h, tz, iso, holidays)
            hid = slug(f"{entity}|{variable}")
            b.hourly[hid] = hourly_file(hid, tz, iso, h, None, holidays)
            b.add("as", f"{entity}|{variable}", f"{grid} {product}", "USD/MW-hour", "D", col(d, "mean"), at=region, code=f"{node} {variable}", tags=dict(grid=grid),
                  source=f"the grid operator's day-ahead ancillary service prices ({table})", hourly=hid)
            n += 1
        log(f"  {grid} ancillary services: {n} rows")
    b.grey("as", "isone|as", "ISO-NE reserves and regulation", "not_held", "Held internal while ISO-NE's terms are reviewed; not shown.", tags=dict(grid="ISO-NE"), unit="USD/MW-hour")
    b.grey("as", "miso|as", "MISO reserves and regulation", "paused", MISO_NOTE, tags=dict(grid="MISO"), unit="USD/MW-hour")
    b.grey("as", "pjm|as", "PJM reserves and regulation", "licensed", PJM_NOTE, tags=dict(grid="PJM"), unit="USD/MW-hour")


def build_fuels(b, log):
    """Gas, crude, products, retail fuel, retail electricity, plant fuel costs, metals, rates, credits. Returns the
    daily fuel series by EIA entity, and the US coal cost by month."""
    fuels = {}
    for table in ("eia_fuel_spot_prices", "eia_product_spot_prices"):
        s, _ = table_daily(table)
        for (entity, variable), series in s.items():
            if variable == "spot_price" and entity in v4.FUELS:
                fuels[entity] = series
    spot = "EIA's daily spot prices (EIA names Refinitiv, an LSEG business, as their source)"
    # gas
    b.add("gas", "eia:henry_hub|spot", "Henry Hub natural gas", "USD/MMBtu", "D", fuels.get("eia:henry_hub", {}), at="Louisiana, spot", code="RNGWHHD", source=spot, curve=CURVE)
    b.grey("gas", "nymex|ng", "Henry Hub futures, contracts 1 to 4", "licensed", FUT_NOTE, at="NYMEX", unit="USD/MMBtu")
    for name, where in (("Waha", "West Texas"), ("SoCal Citygate", "Southern California"), ("Algonquin Citygate", "New England"), ("Chicago Citygate", "Illinois")):
        b.grey("gas", f"gashub|{name}", name, "licensed", "Source that would supply it: S&P Global Commodity Insights (Platts) or Natural Gas Intelligence, daily indices.", at=where, unit="USD/MMBtu")
    b.grey("gas", "ttf", "TTF, the Dutch gas benchmark", "licensed", "Source that would supply the daily price: ICE Endex or LSEG.", at="Netherlands, daily", unit="EUR/MWh")
    b.grey("gas", "jkm", "JKM, the Japan-Korea LNG marker", "licensed", "Source that would supply the daily price: S&P Global Commodity Insights (Platts).", at="Northeast Asia, daily", unit="USD/MMBtu")
    # crude
    wti, brent = fuels.get("eia:wti_cushing", {}), fuels.get("eia:brent", {})
    b.add("crude", "eia:wti_cushing|spot", "WTI crude oil", "USD/bbl", "D", wti, at="Cushing, Oklahoma, spot", code="RWTC", tags=dict(kind="daily"), source=spot, curve=CURVE)
    b.add("crude", "eia:brent|spot", "Brent crude oil", "USD/bbl", "D", brent, at="Europe, FOB, spot", code="RBRTE", tags=dict(kind="daily"), source=spot)
    b.add("crude", "erw:brent_minus_wti", "Brent minus WTI", "USD/bbl", "D", minus(brent, wti), at="the gap", tags=dict(kind="daily"), formula=FORMULAS["brent_wti"], source="the two rows above", also=["oilspreads"])
    b.grey("crude", "nymex|cl", "WTI futures, contracts 1 to 4", "licensed", FUT_NOTE, at="NYMEX", unit="USD/bbl", tags=dict(kind="daily"))
    s, meta = table_daily("eia_crude_stream_prices")
    kinds = {"first_purchase_price": "first purchase price", "landed_cost": "landed cost of imports", "fob_cost": "F.O.B. cost of imports", "refiner_acquisition_cost": "refiner acquisition cost"}
    for (entity, variable), series in sorted(s.items(), key=lambda kv: (list(kinds).index(kv[0][1]), meta[kv[0]]["node"])):
        node = meta[(entity, variable)]["node"]
        m = re.match(r"(.*) Crude Oil (Composite|Domestic|Imported) Acquisition Cost by Refiners", node)
        label, at = (f"{m.group(1).replace('U.S.', 'United States')}, {m.group(2).lower()}", kinds[variable]) if m else (node, kinds[variable])
        b.add("crude", f"{entity}|{variable}", label, "USD/bbl", "M", series, at=f"{at}, monthly", code=entity.split(":", 1)[1], tags=dict(kind=variable), source="EIA, monthly crude oil prices (eia_crude_stream_prices)")
    # products
    for entity, (group, label, at, unit, geo) in v4.FUELS.items():
        if group == "products":
            is_curve = entity in ("eia:EER_EPMRU_PF4_Y35NY_DPG", "eia:EER_EPD2F_PF4_Y35NY_DPG")
            b.add("products", f"{entity}|spot", label, unit, "D", fuels.get(entity, {}), at=f"{at}, spot", code=entity.split(":", 1)[1], source=spot, curve=CURVE if is_curve else None)
    b.grey("products", "nymex|rb", "RBOB gasoline futures, contracts 1 to 4", "licensed", FUT_NOTE, at="NYMEX, New York Harbor", unit="USD/gal")
    b.grey("products", "nymex|ho", "Heating oil futures, contracts 1 to 4", "licensed", FUT_NOTE, at="NYMEX, New York Harbor", unit="USD/gal")
    # retail fuel, weekly
    s, meta = table_daily("eia_regional_retail_fuel_prices")

    def area_kind(entity, node):
        code = entity.split("_")[-2]
        return "region" if node in PADD_WORDS else "city" if code.startswith("Y") else "state"
    order = {"region": 0, "state": 1, "city": 2}
    for (entity, variable), series in sorted(s.items(), key=lambda kv: ("EPD2D" in kv[0][0], order[area_kind(kv[0][0], meta[kv[0]]["node"])], list(PADD_WORDS).index(meta[kv[0]]["node"]) if meta[kv[0]]["node"] in PADD_WORDS else 99, meta[kv[0]]["node"])):
        node = meta[(entity, variable)]["node"]
        product = "diesel" if "EPD2D" in entity else "gasoline"
        b.add("retailfuel", f"{entity}|retail", "Diesel, No. 2" if product == "diesel" else "Gasoline, regular", "USD/gal", "W", series, at=f"{PADD_WORDS.get(node, node.title())}, retail, weekly",
              code=entity.split(":", 1)[1], tags=dict(product=product, area=area_kind(entity, node)), source="EIA, Gasoline and Diesel Fuel Update (eia_regional_retail_fuel_prices)")
    # plant fuel costs, monthly; their names serve the retail electricity rows too
    s, meta = table_daily("eia_power_plant_fuel_costs")
    names = {e.split(":")[2]: meta[(e, v)]["node"] for (e, v) in s}
    us_coal = s.get(("eia:plant_fuel_cost:US:COW", "cost_per_mmbtu"), {})

    def loc_kind(loc):
        return "us" if loc == "US" else "state" if len(loc) == 2 else "division"
    korder = {"us": 0, "division": 1, "state": 2}
    measures = [("COW", "cost_per_mmbtu", "Coal delivered to power plants", "coal"), ("COW", "cost_per_short_ton", "Coal delivered to power plants", "coal_ton"), ("NG", "cost_per_mmbtu", "Natural gas delivered to power plants", "gas")]
    for fuel, variable, label, tag in measures:
        keys = sorted([k for k in s if k[1] == variable and k[0].endswith(":" + fuel)], key=lambda k: (korder[loc_kind(k[0].split(":")[2])], names[k[0].split(":")[2]]))
        for key in keys:
            loc = key[0].split(":")[2]
            b.add("plantfuel", f"{key[0]}|{variable}", label, meta[key]["unit"].replace("_", " "), "M", s[key], at=f"{names[loc].replace('U.S. Total', 'United States')}, monthly", code=f"{loc} {fuel}",
                  tags=dict(fuel=tag, area=loc_kind(loc)), source="EIA, Form EIA-923, cost of fossil fuels delivered to the electric power sector (eia_power_plant_fuel_costs)")
    for basin in ("Central Appalachia", "Northern Appalachia", "Illinois Basin", "Powder River Basin", "Uinta Basin"):
        b.grey("plantfuel", f"coalspot|{basin}", "Coal spot price", "licensed", "EIA shows the week's coal spot prices with S&P Global's permission and says the history is proprietary and cannot be released. Source that would supply it: S&P Global.",
               at=f"{basin}, weekly", unit="USD/short ton", tags=dict(fuel="coal_spot", area="us"))
    # retail electricity, monthly, by state and sector
    s, meta = table_daily("eia_retail_electricity_prices", since=START)
    keys = [k for k in s if k[0].split(":")[3] in SECTORS]
    for key in sorted(keys, key=lambda k: (list(SECTORS).index(k[0].split(":")[3]), korder[loc_kind(k[0].split(":")[2])], names.get(k[0].split(":")[2], k[0].split(":")[2]))):
        loc, sec = key[0].split(":")[2], key[0].split(":")[3]
        b.add("retailpower", f"{key[0]}", "Retail electricity", "USD/MWh", "M", s[key], at=f"{names.get(loc, loc).replace('U.S. Total', 'United States')}, {SECTORS[sec].lower()}, monthly", code=f"{loc} {sec}",
              tags=dict(sector=sec, area=loc_kind(loc)), source="EIA, Form EIA-861M, average retail price of electricity (eia_retail_electricity_prices)")
    # metals and uranium, monthly (IMF)
    s, meta = table_daily("imf_commodity_prices")
    for code in ("PURAN", "PLITH", "PCOBA", "PNICK", "PCOPP"):
        key = (f"imf:PCPS:{code}", "price")
        b.add("metals", f"{key[0]}", meta[key]["node"] if key in meta else code, meta[key]["unit"] if key in meta else "", "M", s.get(key, {}), at="IMF monthly average", code=code,
              source="International Monetary Fund, Primary Commodity Price System (imf_commodity_prices)")
    b.grey("metals", "uranium|daily", "Uranium, daily spot", "licensed", "Source that would supply it: UxC or TradeTech.", unit="USD/lb")
    b.grey("metals", "lithium|daily", "Lithium, daily", "licensed", "Source that would supply it: Fastmarkets or Benchmark Mineral Intelligence.", unit="USD/t")
    # rates
    s, meta = table_daily("fred_treasury_yields")
    for sid, words in (("DGS2", "2-year"), ("DGS10", "10-year"), ("DGS30", "30-year")):
        b.add("rates", f"fred:{sid}", f"US Treasury yield, {words}", "percent", "D", s.get((f"fred:{sid}", "yield"), {}), at="constant maturity", code=sid,
              source="Board of Governors of the Federal Reserve System, release H.15, through FRED (fred_treasury_yields)")
    # carbon and credits
    s, meta = table_daily("carb_lcfs_credit_prices")
    b.add("carbon", "carb:lcfs|avg", "California low-carbon fuel credit", "USD/t CO2e", "W", s.get(("carb:lcfs_credit", "credit_price_weekly_avg"), {}), at="all transfers, weekly average", code="LCFS",
          source="California Air Resources Board, Weekly LCFS Credit Transfer Activity Report (carb_lcfs_credit_prices)")
    b.add("carbon", "carb:lcfs|type1", "California low-carbon fuel credit", "USD/t CO2e", "W", s.get(("carb:lcfs_credit", "credit_price_type1_weekly_avg"), {}), at="Type 1 transfers, weekly average", code="LCFS Type 1",
          source="California Air Resources Board, Weekly LCFS Credit Transfer Activity Report (carb_lcfs_credit_prices)")
    b.grey("carbon", "cca|auction", "California carbon allowance, quarterly auction", "not_held", "The auction results are held internal while the publisher's terms are reviewed; not shown.", unit="USD/t CO2e")
    b.grey("carbon", "rggi|auction", "RGGI carbon allowance, quarterly auction", "not_held", "The auction results are held internal while the publisher's terms are reviewed; not shown.", unit="USD/short ton CO2")
    b.grey("carbon", "eua", "European carbon allowance (EUA)", "licensed", "Source that would supply it: ICE Endex.", unit="EUR/t CO2e")
    b.grey("carbon", "rec", "Renewable energy credits", "licensed", "Source that would supply them: S&P Global Commodity Insights or ICE.", unit="USD/MWh")
    # capacity and equities
    b.grey("other", "capacity", "Capacity prices (PJM, NYISO, ISO-NE, MISO)", "licensed", "Auction results are held internal while each operator's terms are reviewed. Source that would supply them openly: each operator, under its data license.", unit="USD/MW-day")
    b.grey("other", "equities", "Energy equities", "licensed", "Source that would supply them: an exchange data vendor (for example Nasdaq Data Link or LSEG).", unit="USD")
    return fuels, us_coal


def build_spreads(b, daily, fuels, us_coal):
    gas = fuels.get("eia:henry_hub", {})
    for iso, (grid, tz) in ISO.items():
        entity, words = f"{iso}:{MAIN[iso]}", HUB_WORDS[MAIN[iso]]
        d = daily.get((entity, "da"))
        da = col(d, "mean") if d is not None else {}
        b.add("spark", f"{entity}|spark", f"{grid} {words}", "USD/MWh", "D", spark(da, gas), at="spark spread, indicative", code=MAIN[iso], tags=dict(grid=grid), formula=FORMULAS["spark"], source="the hub's day-ahead row and Henry Hub")
        b.add("spark", f"{entity}|heat", f"{grid} {words}", "MMBtu/MWh", "D", implied_heat_rate(da, gas), at="implied heat rate", code=MAIN[iso], tags=dict(grid=grid), formula=FORMULAS["heat"], source="the hub's day-ahead row and Henry Hub")
        b.add("spark", f"{entity}|dark", f"{grid} {words}", "USD/MWh", "M", dark(da, us_coal), at="dark spread, indicative, monthly", code=MAIN[iso], tags=dict(grid=grid), formula=FORMULAS["dark"], source="the hub's day-ahead row and eia_power_plant_fuel_costs")
    for grid, status, note in (("MISO", "paused", MISO_NOTE), ("PJM", "licensed", PJM_NOTE)):
        b.grey("spark", f"{grid}|spark", f"{grid} spark and dark spreads", status, note, tags=dict(grid=grid), unit="USD/MWh")
    g, d = fuels.get("eia:EER_EPMRU_PF4_RGC_DPG", {}), fuels.get("eia:EER_EPD2DXL0_PF4_RGC_DPG", {})
    b.add("oilspreads", "erw:crack_321_gulf_coast", "3-2-1 crack spread", "USD/bbl", "D", crack(g, d, fuels.get("eia:wti_cushing", {})), at="Gulf Coast products, WTI", formula=FORMULAS["crack_gc"], source="EIA's daily spot prices")
    g, d = fuels.get("eia:EER_EPMRU_PF4_Y35NY_DPG", {}), fuels.get("eia:EER_EPD2DXL0_PF4_Y35NY_DPG", {})
    b.add("oilspreads", "erw:crack_321_new_york", "3-2-1 crack spread", "USD/bbl", "D", crack(g, d, fuels.get("eia:brent", {})), at="New York Harbor products, Brent", formula=FORMULAS["crack_ny"], source="EIA's daily spot prices")


def build_week(log):
    """The week's table and spikes the markets page showed, from iso_trader_daily and iso_rt_top_intervals (no MISO)."""
    t = pb.read_table("iso_trader_daily")
    t = t[t["market"].isin(ISO)]
    means = ["da_mean_usd", "da_onpeak_mean_usd", "da_offpeak_mean_usd", "da_rt_spread_mean_usd", "implied_heat_rate"]
    out = []
    for iso, (grid, tz) in ISO.items():
        rows = t[t["market"] == iso]
        days = sorted(set(rows["ts_utc"]))
        if len(days) < 7:
            log(f"  the week, {grid}: {len(days)} days held, a week needs 7")
            continue
        by = {(e, v, ts): float(x) for e, v, ts, x in zip(rows["entity"], rows["variable"], rows["ts_utc"], rows["value"])}
        days_of = {v: sorted(set(rows.loc[rows["variable"] == v, "ts_utc"])) for v in set(rows["variable"])}
        week_of = lambda v: days_of.get(v, [])[-7:]          # noqa: E731
        prev_of = lambda v: days_of.get(v, [])[-14:-7]       # noqa: E731

        def wmean(e, v, ds):
            vals = [by[(e, v, d)] for d in ds if (e, v, d) in by]
            need = 1 if v == "da_onpeak_mean_usd" else len(ds)
            return sum(vals) / len(vals) if len(ds) == 7 and len(vals) >= max(need, 1) else None
        last = days[-1]
        for entity in sorted(set(rows["entity"]), key=lambda e: (e.split(":", 1)[1] != MAIN[iso], HUB_WORDS.get(e.split(":", 1)[1], e))):
            node = entity.split(":", 1)[1]
            item = dict(hub=slug(entity), grid=grid, label=f"{grid} {HUB_WORDS.get(node, node)}", code=node, means={})
            if (entity, "da_mean_usd", last) in by:
                item["last_da"] = dict(t=last[:10], v=round(by[(entity, "da_mean_usd", last)], 4))
            for v in means:
                a, p = wmean(entity, v, week_of(v)), wmean(entity, v, prev_of(v))
                if a is not None:
                    item["means"][v] = dict(v=round(a, 4), ch=None if p is None else round(a - p, 4), end=week_of(v)[-1][:10])
            for v, fn, name in (("da_rt_spread_max_usd", max, "max_spread"), ("hours_rt_over_da_50", sum, "hours50")):
                vals = [by.get((entity, v, d)) for d in week_of(v)]
                if len(vals) == 7 and all(x is not None for x in vals):
                    item[name] = dict(v=round(fn(vals), 4), start=week_of(v)[0][:10], end=week_of(v)[-1][:10])
            vols = [(d, by[(entity, "da_volatility_30d_usd", d)]) for d in days if (entity, "da_volatility_30d_usd", d) in by]
            if vols:
                item["vol"] = dict(t=vols[-1][0][:10], v=round(vols[-1][1], 4))
            out.append(item)
    top = pb.read_table("iso_rt_top_intervals")
    top = top[top["market"].isin(ISO)]
    spikes = [dict(hub=slug(e), grid=ISO[m][0], label=f"{ISO[m][0]} {HUB_WORDS.get(e.split(':', 1)[1], e.split(':', 1)[1])}", code=e.split(":", 1)[1], t=ts, v=round(float(x), 4), tz=ISO[m][1], freq=f)
              for e, m, ts, x, f in zip(top["entity"], top["market"], top["ts_utc"], top["value"], top["freq"])]
    spikes.sort(key=lambda r: (-r["v"], r["t"]))
    return out, spikes


GROUPS = [
    dict(id="power", title="Power, by hub and zone", filters=[
        dict(key="grid", label="Grid", options=[["all", "All grids"], ["ERCOT", "ERCOT"], ["CAISO", "CAISO"], ["NYISO", "NYISO"], ["ISO-NE", "ISO-NE"], ["SPP", "SPP"], ["MISO", "MISO"], ["PJM", "PJM"]], default="all"),
        dict(key="market", label="Market", options=[["all", "Both"], ["da", "Day-ahead"], ["rt", "Real time"]], default="all"),
        dict(key="scope", label="Show", options=[["main", "Main hubs"], ["all", "Every hub and zone"]], default="main", inclusive=True)]),
    dict(id="peak", title="Power, on-peak and off-peak", filters=[
        dict(key="market", label="Market", options=[["all", "Both"], ["da", "Day-ahead"], ["rt", "Real time"]], default="da"),
        dict(key="measure", label="Measure", options=[["all", "All"], ["peak", "On-peak"], ["offpeak", "Off-peak"], ["spread", "On-peak less off-peak"]], default="all")]),
    dict(id="spark", title="Spark and dark spreads, by grid", filters=[
        dict(key="grid", label="Grid", options=[["all", "All grids"], ["ERCOT", "ERCOT"], ["CAISO", "CAISO"], ["NYISO", "NYISO"], ["ISO-NE", "ISO-NE"], ["SPP", "SPP"]], default="all")]),
    dict(id="da_rt", title="Day-ahead minus real time, by hub", filters=[
        dict(key="grid", label="Grid", options=[["all", "All grids"], ["ERCOT", "ERCOT"], ["CAISO", "CAISO"], ["NYISO", "NYISO"], ["ISO-NE", "ISO-NE"], ["SPP", "SPP"]], default="all"),
        dict(key="scope", label="Show", options=[["main", "Main hubs"], ["all", "Every hub and zone"]], default="main", inclusive=True)]),
    dict(id="battery", title="Battery spread, by hub", filters=[
        dict(key="grid", label="Grid", options=[["all", "All grids"], ["ERCOT", "ERCOT"], ["CAISO", "CAISO"], ["NYISO", "NYISO"], ["ISO-NE", "ISO-NE"], ["SPP", "SPP"]], default="all"),
        dict(key="market", label="Market", options=[["da", "Day-ahead"], ["rt", "Real time"]], default="da"),
        dict(key="scope", label="Show", options=[["main", "Main hubs"], ["all", "Every hub and zone"]], default="main", inclusive=True)]),
    dict(id="as", title="Ancillary services, day-ahead", filters=[
        dict(key="grid", label="Grid", options=[["all", "All grids"], ["ERCOT", "ERCOT"], ["CAISO", "CAISO"], ["NYISO", "NYISO"], ["SPP", "SPP"]], default="ERCOT")]),
    dict(id="gas", title="Natural gas", curve=True, filters=[]),
    dict(id="crude", title="Crude oil", curve=True, filters=[
        dict(key="kind", label="Show", options=[["daily", "Daily benchmarks"], ["first_purchase_price", "First purchase, monthly"], ["landed_cost", "Landed cost, monthly"], ["fob_cost", "F.O.B. cost, monthly"],
                                                 ["refiner_acquisition_cost", "Refiner acquisition cost, monthly"], ["all", "Everything"]], default="daily")]),
    dict(id="products", title="Refined products, spot", curve=True, filters=[]),
    dict(id="oilspreads", title="Oil spreads", filters=[]),
    dict(id="retailfuel", title="Retail gasoline and diesel, weekly", filters=[
        dict(key="product", label="Fuel", options=[["gasoline", "Gasoline"], ["diesel", "Diesel"], ["all", "Both"]], default="gasoline"),
        dict(key="area", label="Area", options=[["region", "Regions"], ["state", "States"], ["city", "Cities"], ["all", "All"]], default="region")]),
    dict(id="retailpower", title="Retail electricity by state, monthly", filters=[
        dict(key="sector", label="Sector", options=[["ALL", "All sectors"], ["RES", "Residential"], ["COM", "Commercial"], ["IND", "Industrial"]], default="ALL"),
        dict(key="area", label="Area", options=[["us", "United States"], ["division", "Census divisions"], ["state", "States"], ["all", "All"]], default="state")]),
    dict(id="plantfuel", title="Coal and gas delivered to power plants, monthly", filters=[
        dict(key="fuel", label="Fuel", options=[["coal", "Coal, USD/MMBtu"], ["coal_ton", "Coal, USD/short ton"], ["gas", "Natural gas, USD/MMBtu"], ["coal_spot", "Coal spot by basin"]], default="coal"),
        dict(key="area", label="Area", options=[["us", "United States"], ["division", "Census divisions"], ["state", "States"], ["all", "All"]], default="all")]),
    dict(id="metals", title="Uranium and battery metals, monthly", filters=[]),
    dict(id="rates", title="US Treasury yields", filters=[]),
    dict(id="carbon", title="Carbon and credits", filters=[]),
    dict(id="other", title="Capacity and equities", filters=[]),
]


def build(log):
    b = Board()
    holidays = pb.nerc_holidays(range(2018, dt.date.today().year + 2))
    log("hourly prices:")
    store = hourly_store(log)
    daily = build_power(b, store, holidays, log)
    build_as(b, holidays, log)
    fuels, us_coal = build_fuels(b, log)
    build_spreads(b, daily, fuels, us_coal)
    week, spikes = build_week(log)
    return b, week, spikes


def write_site(b, week, spikes, site_dir, built, log):
    data_dir, s_dir, h_dir = os.path.join(site_dir, "data"), os.path.join(site_dir, "public", "board", "s"), os.path.join(site_dir, "public", "board", "h")
    for d in (data_dir, s_dir, h_dir):
        os.makedirs(d, exist_ok=True)
    order = {g["id"]: i for i, g in enumerate(GROUPS)}
    rows = sorted(b.rows, key=lambda r: order[r["group"]])       # stable: a group's rows keep the order they were added in
    sources = sorted({r["source"] for r in rows if r.get("source")})
    rows = [dict(r, source=sources.index(r["source"])) if r.get("source") else r for r in rows]     # a source is written once, and a row points at it
    board = dict(built=built, sources=sources, heat_rate=HEAT_RATE, coal_heat_rate=COAL_HEAT_RATE, gas_back_days=GAS_BACK, slack_days=SLACK, groups=GROUPS, rows=rows, week=week, spikes=spikes)
    with open(os.path.join(data_dir, "board.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(board, f, separators=(",", ":"))
        f.write("\n")
    for kind, folder, files in (("series", s_dir, b.series), ("hourly", h_dir, b.hourly)):
        keep = set()
        for rid, body in files.items():
            keep.add(rid + ".json")
            with open(os.path.join(folder, rid + ".json"), "w", encoding="utf-8", newline="\n") as f:
                json.dump(body, f, separators=(",", ":"))
        for old in os.listdir(folder):
            if old.endswith(".json") and old not in keep:
                os.remove(os.path.join(folder, old))      # a row that left the board leaves its file: the folder is this builder's own output
        log(f"  {kind}: {len(files)} files in {os.path.relpath(folder, ROOT)}")
    held = [r for r in rows if r["status"] == "ok"]
    log(f"  board.json: {len(rows)} rows, {len(held)} with values, {len(rows) - len(held)} placeholders; the week: {len(week)} hubs, {len(spikes)} spikes")
    return board


def main(argv=None):
    ap = argparse.ArgumentParser(description="the price board's site files")
    ap.add_argument("--site-dir", default=SITE, help="write under this folder (default: site/)")
    args = ap.parse_args(argv)
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"board_page_{run_id}.log"))
    b, week, spikes = build(log)
    board = write_site(b, week, spikes, args.site_dir, ip.utc_iso(pd.Timestamp.now(tz="UTC")), log)
    held = sum(1 for r in board["rows"] if r["status"] == "ok")
    print(f"board: {len(board['rows'])} rows ({held} with values), {len(b.series)} series files, {len(b.hourly)} hourly files")
    log.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
