#!/usr/bin/env python3
"""The energy mix by hour: the average day of each month, and the records (session 94, the energy mix version 2).

Energy Research Warehouse (ERW). Two derived tables for the seven ISO grids, from January 2019. Method:
docs/methods/generation_mix_hourly.md. Page: /mix/v2, "The energy mix" (in review).

    python warehouse/derived/mix_profile.py                 # the two tables, under the data lock
    python warehouse/derived/mix_profile.py --out-dir DIR   # a trial run: the tables under DIR, nothing in warehouse/output
    python warehouse/derived/mix_profile.py --snapshot      # also the site's own copy (site/data/mix/)

Inputs (no request is made):
- EIA-930 hourly demand, net generation and net generation by energy source, from the per-balancing-authority workbooks
  the emissions connector saved (warehouse/raw/eia930_emissions/<run>/<BA>.xlsx, sheet Published Hourly Data, EIA's
  Adjusted columns; an hour is dated by its start).
- California from the join: CAISO's own supply by fuel (caiso_fuel_supply), by the one join of the warehouse
  (caiso_join.JOIN, docs/methods/eia930_caiso_break.md). EIA's generation series for California changed on that day.
  Before it, EIA's hours, with the late ones of 2023-11 to 2025-12-02 set back (caiso_join.true_hours). The local month
  that holds the join (December 2025) is not written: a month is never built on both sources. Demand is EIA's throughout.
- carbon_intensity_hourly (intensity_generation, kg CO2/MWh), for the cleanest and the dirtiest hour.

The sources are grouped as the site groups them: natural_gas (NG), coal (COL), nuclear (NUC), wind (WND, WNB), solar
(SUN, SNB), hydro (WAT), storage (BAT, PS, OES, UES; negative when charging) and other (OIL, GEO, OTH, UNK). From
CAISO's own data: hydro is large and small hydro; storage is batteries; other is biogas, biomass, geothermal and other;
imports are not generation and are left out.

An hour is held when three things are true. Its net generation is held and positive. The sum of its sources is within
5 percent of it (PJM: 15 percent). And no main source is blank: a source that supplies at least 5 percent of the grid's
generation over its history is never taken as zero. An hour that is not held is used for nothing. Within a held hour a
smaller source EIA left blank counts as zero (storage before EIA itemized it; New England's coal when its last plant
is off), and a share is of the sum of the sources, not of EIA's total.

Why each test, from what the workbooks hold:
- the 5 percent: in Texas from 6 to 14 December 2025 EIA's "other" repeats the batteries' output (other 3,281 MW with
  storage at 3,172), and the sources stand 5 to 8 percent above the total. Those hours are not held.
- PJM's 15 percent: PJM itemizes no storage, and in 2,689 hours, most of them at 5 and 6 in the morning from 2020 to
  2024, its sources differ from its total by 5 to 15 percent, above as often as below, with no source blank. At 5
  percent 36 of PJM's 93 months could be written, at 10 percent 74, at 15 percent 91. The hours are kept; the shares
  are of the sources.
- the main sources: EIA's workbook holds no hydro for California from October 2019 to mid August 2020 (blank in 97 to
  100 percent of the hours of those months), its total leaves it out too, so the sources still add up to it, and its
  balance (demand against net generation less interchange) is off by 9 to 15 percent of demand in those months against
  2 to 4 around them. A month built on those hours would show California without hydro. They are not held.

A day is complete when every hour of the local day is held; a month is written
when at least 90 percent of its days are complete, as the average over those days; never filled.

generation_mix_hourly_profile (series, freq P1M, ts_utc the first day of the local month at 00:00:00Z, entity
iso:<grid>):
    avg_<source>_mw_hHH, avg_demand_mw_hHH, avg_net_generation_mw_hHH     the average day, by local hour 00 to 23
    <source>_mwh, net_generation_mwh                                      over the complete days
    <source>_share_pct                                                    of the sum of the sources over those days
    days_held, days_in_month

generation_mix_records (series, freq PT1H, ts_utc the hour of the record, entity iso:<grid>; x_period "all" or a local
year; x_side eia930 or caiso, the source of that hour):
    solar_share_max_pct, wind_share_max_pct, wind_solar_share_max_pct     the highest share of an hour's generation
    cleanest_hour_kgco2_per_mwh, dirtiest_hour_kgco2_per_mwh              the lowest and highest carbon intensity of generation
Each for the whole history and for each local year (variable prefixed year_).

What a record counts, so that a faulty hour is not a record:
- a share is of the hour's generation, the sum of what its sources put out: a source below zero (batteries charging,
  a solar farm's own use at night) adds nothing to it. Against net generation, a grid whose batteries charge at midday
  would show solar above 100 percent.
- an hour of EIA's is not ranked when EIA's own balance does not close: its demand differs from its net generation
  less its total interchange by more than 20 percent of demand, or its total interchange is blank. Such an hour is a
  partial report: California has hours in which only its wind was reported ("wind, 100 percent of generation, at one
  in the afternoon"). The hour stays in the monthly averages, where one hour moves little; a record is one hour.
  CAISO's own hours (from the join) are not put to this test: each holds all thirteen of CAISO's sources, and EIA's
  demand is not CAISO's sum.
- an hour is not ranked for carbon intensity when its intensity is less than half of what its own natural gas
  generation alone implies at EIA's factor for gas (caiso_join.F_GAS): its CO2 and its generation do not agree.
The log counts the hours each rule leaves out. Nothing is corrected or filled.
"""

import argparse
import glob
import json
import os
import sys
from datetime import timedelta

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, HERE)
import caiso_join as cj  # noqa: E402
import iso_prices as ip  # noqa: E402

PROFILE = "generation_mix_hourly_profile"
RECORDS = "generation_mix_records"
SOURCE = "erw:generation_mix_hourly"
SOURCE_JOIN = "erw:generation_mix_hourly_caiso"
METHOD_URL = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/generation_mix_hourly.md"
RAW = os.path.join(ROOT, "warehouse", "raw", "eia930_emissions")
SITE_DIR = os.path.join(ROOT, "site", "data", "mix")
FIRST = "2019-01"
NEAR = 0.9          # the share of a month's days that must be complete
TOLERANCE = 0.05    # the sources of a held hour add up to its net generation within this share
LOOSE = {"pjm": 0.15}  # PJM itemizes no storage and its sources and total part by 5 to 15 percent in its ramp hours (the docstring)
MAIN = 0.05         # a source with at least this share of a grid's generation over its history is never taken as zero
BALANCE = 0.20      # an hour of EIA's is ranked only when demand is within this share of net generation less total interchange
GRIDS = {
    "caiso": dict(ba="CISO", tz="America/Los_Angeles", geo="US-CA", name="CAISO"),
    "ercot": dict(ba="ERCO", tz="America/Chicago", geo="US-TX", name="ERCOT"),
    "isone": dict(ba="ISNE", tz="America/New_York", geo="US", name="ISO-NE"),
    "miso": dict(ba="MISO", tz="America/Chicago", geo="US", name="MISO"),
    "nyiso": dict(ba="NYIS", tz="America/New_York", geo="US-NY", name="NYISO"),
    "pjm": dict(ba="PJM", tz="America/New_York", geo="US", name="PJM"),
    "spp": dict(ba="SWPP", tz="America/Chicago", geo="US", name="SPP"),
}
GROUPS = {"natural_gas": ["NG"], "coal": ["COL"], "nuclear": ["NUC"], "wind": ["WND", "WNB"], "solar": ["SUN", "SNB"], "hydro": ["WAT"],
          "storage": ["BAT", "PS", "OES", "UES"], "other": ["OIL", "GEO", "OTH", "UNK"]}
OWN = {"natural_gas": ["natural_gas_mw"], "coal": ["coal_mw"], "nuclear": ["nuclear_mw"], "wind": ["wind_mw"], "solar": ["solar_mw"],
       "hydro": ["large_hydro_mw", "small_hydro_mw"], "storage": ["batteries_mw"], "other": ["biogas_mw", "biomass_mw", "geothermal_mw", "other_mw"]}
SOURCES = list(GROUPS)
RECORD_VARS = {"solar_share_max_pct": ("solar_share", "max", "pct"), "wind_share_max_pct": ("wind_share", "max", "pct"),
               "wind_solar_share_max_pct": ("wind_solar_share", "max", "pct"),
               "cleanest_hour_kgco2_per_mwh": ("intensity", "min", "kgCO2/MWh"), "dirtiest_hour_kgco2_per_mwh": ("intensity", "max", "kgCO2/MWh")}


def workbook(ba):
    files = [f for f in glob.glob(os.path.join(RAW, "*", f"*_{ba}.xlsx")) if os.path.getsize(f) > 0]
    if not files:
        raise FileNotFoundError(f"no {ba} workbook under {RAW}")
    return max(files, key=lambda f: (os.path.basename(os.path.dirname(f)), os.path.basename(f)))


def eia_hourly(ba):
    """EIA-930's hours of one balancing authority, by hour start (UTC): demand, net_generation and the eight sources, MW
    (MWh in the hour), as EIA's Adjusted columns give them; a blank is NaN."""
    import openpyxl
    path = workbook(ba)
    ws = openpyxl.load_workbook(path, read_only=True, data_only=True)["Published Hourly Data"]
    rows = ws.iter_rows(values_only=True)
    head = list(next(rows))
    t = head.index("UTC time")
    cols = {"demand": head.index("Adjusted demand"), "net_generation": head.index("Adjusted net generation"),
            "interchange": head.index("Adjusted total interchange")}
    for codes in GROUPS.values():
        for c in codes:
            if f"Adjusted {c} Gen" in head:
                cols[c] = head.index(f"Adjusted {c} Gen")
    out = []
    for r in rows:
        ts = r[t]
        if ts is None or ts.year < 2018:
            continue
        rec = {"ts": ts - timedelta(hours=1)}
        for k, i in cols.items():
            v = r[i]
            rec[k] = float(v) if isinstance(v, (int, float)) else np.nan
        out.append(rec)
    d = pd.DataFrame(out)
    d["ts"] = pd.to_datetime(d["ts"]).dt.tz_localize("UTC")
    d = d.drop_duplicates("ts").set_index("ts").sort_index()
    if ba == "CISO":
        d = cj.true_hours(d)
    return grouped(d, GROUPS), path


def grouped(d, groups):
    """The eight sources from their columns: a source is NaN only when every one of its columns is blank."""
    out = pd.DataFrame(index=d.index)
    for k in ("demand", "net_generation", "interchange"):
        out[k] = d[k] if k in d else np.nan
    for g, codes in groups.items():
        have = [c for c in codes if c in d]
        out[g] = d[have].sum(axis=1, min_count=1) if have else np.nan
    return out


def caiso_own():
    """CAISO's own hours from the join, grouped; net generation is the sum of its own sources (imports left out)."""
    w = cj.caiso_hours(ip.OUT_DIR)
    w.index = pd.to_datetime(w.index, utc=True)
    w = w[w.index >= pd.Timestamp(cj.JOIN)]
    d = w.rename(columns={"net_generation_mwh": "net_generation"})
    d["demand"] = np.nan
    d["interchange"] = -d["imports_mw"]  # EIA's sign: total interchange is positive when the grid exports
    return grouped(d, OWN)


def flags(x, grid):
    """Mark each hour of x held or not (the three tests of the docstring), in place; returns the tolerance used and the
    grid's main sources."""
    total = x[SOURCES].sum(axis=1, min_count=1)
    tol = LOOSE.get(grid, TOLERANCE)
    share = x[SOURCES].clip(lower=0).sum() / x[SOURCES].clip(lower=0).sum().sum()
    main = [k for k in SOURCES if share[k] >= MAIN]
    x["unreported"] = x[main].isna().any(axis=1) & x["net_generation"].notna()
    x["held"] = x["net_generation"].notna() & (x["net_generation"] > 0) & total.notna() \
        & ((total - x["net_generation"]).abs() <= tol * x["net_generation"]) & ~x["unreported"]
    return tol, main


def hours_of(grid, log):
    """One grid's hours with what the tables need: the sources, the held flag, the local day and hour, and the side."""
    g = GRIDS[grid]
    x, path = eia_hourly(g["ba"])
    x["side"] = "eia930"
    if grid == "caiso":
        own = caiso_own()
        own["demand"] = x["demand"].reindex(own.index)  # demand stays EIA's
        own["side"] = "caiso"
        x = pd.concat([x[x.index < pd.Timestamp(cj.JOIN)], own]).sort_index()
        log(f"  caiso: EIA's hours to {cj.JOIN}, CAISO's own from it ({len(own):,} hours)")
    x = x[x.index >= pd.Timestamp(f"{FIRST}-01", tz=g["tz"]).tz_convert("UTC")].copy()
    tol, main = flags(x, grid)
    local = x.index.tz_convert(g["tz"])
    x["day"] = local.strftime("%Y-%m-%d")
    x["month"] = local.strftime("%Y-%m")
    x["hour"] = local.hour
    n = len(x)
    log(f"  {grid}: {n:,} hours from {x.index.min():%Y-%m-%d}, {int(x['held'].sum()):,} held, {n - int(x['held'].sum()):,} not "
        f"(net generation blank or not positive, the sources off it by more than {tol:.0%}, or, {int(x['unreported'].sum()):,} of them, a main source "
        f"blank: {', '.join(main)})")
    return x, path


def expected_hours(day, tz):
    a = pd.Timestamp(day).tz_localize(tz)
    b = (pd.Timestamp(day) + pd.Timedelta(days=1)).tz_localize(tz)
    return int(round((b - a) / pd.Timedelta(hours=1)))


def profile_rows(grid, x, retrieved, join_month=None):
    """The average day of each month over its complete days, and the month's totals and shares."""
    g = GRIDS[grid]
    rows = []
    per_day = x.groupby("day").agg(n=("held", "size"), ok=("held", "sum"), month=("month", "first"))
    per_day["complete"] = [(r.n == r.ok) and r.n == expected_hours(d, g["tz"]) for d, r in per_day.iterrows()]
    good = set(per_day.index[per_day["complete"]])
    for month, days in per_day.groupby("month"):
        if month == join_month:
            continue  # a month is never built on both sources
        in_month = pd.Period(month).days_in_month
        held = int(days["complete"].sum())
        if held < NEAR * in_month:
            continue
        m = x[(x["month"] == month) & x["day"].isin(good)]
        side = m["side"].iloc[0]
        src = SOURCE_JOIN if side == "caiso" else SOURCE
        ts = f"{month}-01T00:00:00Z"

        def add(variable, value, unit):
            rows.append(dict(entity=f"iso:{grid}", variable=variable, ts_utc=ts, value=value, unit=unit, freq="P1M", geo=g["geo"], market="", node="",
                             source=src, source_url=METHOD_URL, retrieved_at=retrieved, vintage=""))
        by = m.groupby("hour")
        for s in SOURCES + ["demand", "net_generation"]:
            means = by[s].mean() if s in ("demand", "net_generation") else by[s].apply(lambda v: v.fillna(0).mean())
            for h, v in means.items():
                if not np.isnan(v):
                    add(f"avg_{s}_mw_h{int(h):02d}", round(float(v), 1), "MW")
        totals = {s: float(m[s].fillna(0).sum()) for s in SOURCES}
        whole = sum(totals.values())
        for s in SOURCES:
            add(f"{s}_mwh", round(totals[s], 1), "MWh")
            add(f"{s}_share_pct", round(100 * totals[s] / whole, 2), "pct")
        add("net_generation_mwh", round(float(m["net_generation"].sum()), 1), "MWh")
        add("days_held", held, "count")
        add("days_in_month", in_month, "count")
    return rows


def record_rows(grid, x, ci, retrieved, log=None):
    """The records of the held hours: for the whole history and for each local year."""
    g = GRIDS[grid]
    h = x[x["held"]].copy()
    v = h[SOURCES].fillna(0)
    gross = v.clip(lower=0).sum(axis=1)
    gap = (h["demand"] - (h["net_generation"] - h["interchange"])).abs() / h["demand"]
    odd = (h["side"] == "eia930") & ~(gap <= BALANCE)  # a blank interchange or demand fails the test too
    for k in ("solar", "wind"):
        h[f"{k}_share"] = (100 * v[k].clip(lower=0) / gross).where(~odd)
    h["wind_solar_share"] = h["solar_share"] + h["wind_share"]
    ci = ci.reindex(h.index)
    implied = 1000 * cj.F_GAS * v["natural_gas"].clip(lower=0) / h["net_generation"]
    low = ci.notna() & (ci < 0.5 * implied)
    h["intensity"] = ci.where(~low & ~odd)
    h["year"] = h["day"].str[:4]
    if log:
        log(f"  {grid} records: {len(h):,} held hours; {int(odd.sum()):,} of EIA's not ranked (its balance does not close within {BALANCE:.0%} of demand, or "
            f"no total interchange); {int(ci.isna().sum()):,} with no carbon intensity; {int(low.sum()):,} not ranked for intensity (less than half of what "
            "its own gas generation implies)")
    rows = []

    def add(variable, col, how, unit, part, period):
        s = part[col].dropna()
        if not len(s) or (how == "max" and col.endswith("_share") and s.max() <= 0):
            return  # a source the grid does not report to EIA-930 (New York's solar) has no record, not a record of zero
        at = s.idxmax() if how == "max" else s.idxmin()
        rows.append(dict(entity=f"iso:{grid}", variable=variable, ts_utc=at.strftime("%Y-%m-%dT%H:%M:%SZ"), value=round(float(s.loc[at]), 2), unit=unit, freq="PT1H",
                         geo=g["geo"], market="", node="", source=SOURCE_JOIN if part.loc[at, "side"] == "caiso" else SOURCE, source_url=METHOD_URL,
                         retrieved_at=retrieved, vintage="", x_period=period, x_side=part.loc[at, "side"]))
    for variable, (col, how, unit) in RECORD_VARS.items():
        add(variable, col, how, unit, h, "all")
        for year, part in h.groupby("year"):
            add(f"year_{variable}", col, how, unit, part, year)
    return rows


def intensity_of(ba):
    """The hourly carbon intensity of generation of one balancing authority (kg CO2/MWh), indexed by the hour (UTC)."""
    c = cj.read_entity("carbon_intensity_hourly", f"eia930:{ba}")
    c = c[c["variable"] == "intensity_generation"]
    return pd.Series(c["value"].values, index=pd.to_datetime(c["ts_utc"], utc=True))


def year_of(months, year, upto):
    """A year from its months, or None: the average day weighted by each month's complete days, the MWh summed, the shares
    of the summed MWh. Given only when at most one month of the year (to the last month of the table, upto) is missing."""
    due = [f"{year}-{m:02d}" for m in range(1, 13) if f"{year}-{m:02d}" <= upto]
    have = [m for m in due if m in months]
    if not due or len(due) - len(have) > 1:
        return None
    days = sum(months[m]["days_held"] for m in have)
    avg = {}
    for k in SOURCES + ["demand", "net_generation"]:
        cols = []
        for h in range(24):
            vals = [(months[m]["avg"].get(k) or [None] * 24)[h] for m in have]
            cols.append(None if any(v is None for v in vals) else round(sum(v * months[m]["days_held"] for v, m in zip(vals, have)) / days, 1))
        avg[k] = cols
    out = {"avg": avg, "side": "+".join(sorted({months[m]["side"] for m in have})), "months": len(have), "months_due": len(due),
           "missing": [m for m in due if m not in months], "days_held": days}
    whole = sum(sum(months[m][f"{k}_mwh"] for m in have) for k in SOURCES)
    for k in SOURCES:
        t = sum(months[m][f"{k}_mwh"] for m in have)
        out[f"{k}_mwh"] = round(t, 1)
        out[f"{k}_share_pct"] = round(100 * t / whole, 2)
    out["net_generation_mwh"] = round(sum(months[m]["net_generation_mwh"] for m in have), 1)
    return out


def snapshot(profile, records, retrieved):
    """The site's own copy: one file per grid (the average days as arrays of 24, the years from them) and the records."""
    upto = profile["ts_utc"].max()[:7]
    os.makedirs(SITE_DIR, exist_ok=True)
    for grid in GRIDS:
        p = profile[profile["entity"] == f"iso:{grid}"]
        months = {}
        for r in p.itertuples():
            m = months.setdefault(r.ts_utc[:7], {"avg": {}, "side": "caiso" if r.source == SOURCE_JOIN else "eia930"})
            if r.variable.startswith("avg_"):
                key, hh = r.variable[4:-7], int(r.variable[-2:])
                m["avg"].setdefault(key, [None] * 24)[hh] = r.value
            else:
                m[r.variable] = r.value
        rec = [dict(variable=r.variable, ts_utc=r.ts_utc, value=r.value, unit=r.unit, period=r.x_period, side=r.x_side)
               for r in records[records["entity"] == f"iso:{grid}"].itertuples()]
        years = {}
        for y in sorted({m[:4] for m in months}):
            v = year_of(months, y, upto)
            if v:
                years[y] = v
        with open(os.path.join(SITE_DIR, f"{grid}.json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump(dict(grid=grid, name=GRIDS[grid]["name"], tz=GRIDS[grid]["tz"], built=retrieved, join=cj.JOIN if grid == "caiso" else None,
                           first=FIRST, upto=upto, sources=SOURCES, months=dict(sorted(months.items())), years=years, records=rec), f, separators=(",", ":"))


def main(argv=None):
    ap = argparse.ArgumentParser(description="The energy mix by hour: the average day of each month, and the records")
    ap.add_argument("--out-dir", help="a trial run: the tables, their log and the registry under this directory; nothing in warehouse/output")
    ap.add_argument("--snapshot", action="store_true", help="also write the site's own copy (site/data/mix/)")
    ap.add_argument("--grids", nargs="*", choices=sorted(GRIDS))
    ap.add_argument("--snapshot-only", action="store_true", help="write the site's own copy from the tables as they are (no table is written; no lock)")
    a = ap.parse_args(argv)
    if a.snapshot_only:
        d = a.out_dir or ip.OUT_DIR
        p = pd.read_csv(os.path.join(d, f"{PROFILE}.csv"), comment="#")
        r = pd.read_csv(os.path.join(d, f"{RECORDS}.csv"), comment="#", dtype={"x_period": str})
        snapshot(p, r, p["retrieved_at"].max())
        print(f"the site's copy written from {d}: {p['entity'].nunique()} grids")
        return 0
    inputs = ip.OUT_DIR
    if a.out_dir:
        os.makedirs(a.out_dir, exist_ok=True)
    run_id = pd.Timestamp.now(tz="UTC").strftime("%Y%m%dT%H%M%SZ")
    retrieved = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
    log_dir = os.path.join(a.out_dir, "logs") if a.out_dir else ip.LOG_DIR
    os.makedirs(log_dir, exist_ok=True)
    log = ip.Log(os.path.join(log_dir, f"mix_profile_{run_id}.log"))
    join_month = pd.Timestamp(cj.JOIN).tz_convert(GRIDS["caiso"]["tz"]).strftime("%Y-%m")
    prof, rec, paths = [], [], []
    for grid in (a.grids or GRIDS):
        x, path = hours_of(grid, log)
        paths.append(os.path.relpath(path, ROOT).replace("\\", "/"))
        prof += profile_rows(grid, x, retrieved, join_month if grid == "caiso" else None)
        rec += record_rows(grid, x, intensity_of(GRIDS[grid]["ba"]), retrieved, log)
    p = pd.DataFrame(prof)[ip.SERIES_COLS]
    r = pd.DataFrame(rec)[ip.SERIES_COLS + ["x_period", "x_side"]]
    if a.out_dir:
        ip.set_out_dir(a.out_dir)
    common = [f"Retrieved: {run_id} (UTC) by warehouse/derived/mix_profile.py", f"Run log: warehouse/output/logs/mix_profile_{run_id}.log",
              "Derived from: caiso_fuel_supply; carbon_intensity_hourly",
              f"Source: {SOURCE} EIA Form EIA-930 hourly net generation by energy source, the per-BA workbooks "
              f"(https://www.eia.gov/electricity/gridmonitor/knownissues/xls/<BA>.xlsx); California from {cj.JOIN} is CAISO's own supply by fuel "
              f"(caiso_fuel_supply; source {SOURCE_JOIN}), the warehouse's one join (docs/methods/eia930_caiso_break.md); read by this run from {'; '.join(paths)}",
              "License: public"]
    if not a.grids:
        # rebuilt whole from its inputs each run: a month that no longer passes the tests must not stay from an earlier run
        for name in (PROFILE, RECORDS):
            path = os.path.join(ip.OUT_DIR, name + ".csv")
            if os.path.exists(path):
                ip._require_lock(path, f"rebuilding {name}")
                os.remove(path)
    ip.write_csv(p, PROFILE, [
        "Energy Research Warehouse (ERW): the energy mix by hour, the average day of each month, the seven ISO grids (session 94)",
        "Shape: series (docs/datastandard.md v0). freq P1M; ts_utc is the first day of the local month at 00:00:00Z. avg_<source>_mw_hHH is the mean, "
        "over the month's complete days, of that source's MW in local hour HH; <source>_mwh and <source>_share_pct are over the same days. Sources: "
        "natural_gas, coal, nuclear, wind, solar, hydro, storage (negative when charging), other. Definitions: docs/methods/generation_mix_hourly.md.",
        f"Window: from {FIRST}. An hour is held when its net generation is positive, its sources add up to it within {TOLERANCE:.0%} (PJM: {LOOSE['pjm']:.0%}) and "
        f"no source with at least {MAIN:.0%} of the grid's generation is blank; a month is written "
        f"when at least {NEAR:.0%} of its days are complete; California's {join_month} is not written (the month of the join: never both sources in one month).",
    ] + common, log)
    ip.write_csv(r, RECORDS, [
        "Energy Research Warehouse (ERW): the energy mix's records by grid: the highest solar and wind shares of an hour, the cleanest and the dirtiest hour (session 94)",
        "Shape: series (docs/datastandard.md v0). freq PT1H; ts_utc is the hour of the record (its start, UTC). Variables for the whole history, and with the "
        "prefix year_ for each local year (x_period: all, or the year). x_side: eia930 or caiso, the source of that hour. A share is of the hour's "
        "generation (the sum of what its sources put out; a source below zero adds nothing); the intensity is carbon_intensity_hourly's "
        "intensity_generation. Only held hours, and not an hour whose sources or whose CO2 do not describe it (docs/methods/generation_mix_hourly.md).",
        f"Window: from {FIRST}.",
    ] + common, log, cols=ip.SERIES_COLS + ["x_period", "x_side"], key=["entity", "variable", "x_period"])
    ip.update_sources([dict(source=s, publisher="Energy Research Warehouse (ERW), derived", report=rep, report_url=METHOD_URL,
                            document_list="docs/methods/generation_mix_hourly.md", license="public", tables=[PROFILE, RECORDS])
                       for s, rep in ((SOURCE, "The energy mix by hour: the average day of each month and the records, from EIA-930 (docs/methods/generation_mix_hourly.md)"),
                                      (SOURCE_JOIN, f"The same for California from {cj.JOIN[:10]}, from CAISO's own supply by fuel (docs/methods/eia930_caiso_break.md)"))])
    if a.snapshot:
        snapshot(p, r, retrieved)
    log.close()
    print(f"{PROFILE}: {len(p):,} rows, {p['ts_utc'].nunique()} months, {p['entity'].nunique()} grids; {RECORDS}: {len(r):,} rows"
          + ("; the site's copy written" if a.snapshot else "") + (f" (trial, under {a.out_dir}; inputs read from {inputs})" if a.out_dir else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
