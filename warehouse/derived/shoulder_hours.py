#!/usr/bin/env python3
"""The shoulder hours: midday surplus, the evening shoulder, and how much of it the battery fleet covers (session 75).

Energy Research Warehouse (ERW), derived table shoulder_hours_monthly. Method: docs/methods/shoulder_hours.md.
Page: /shoulder, "The shoulder hours" (in review).

    python warehouse/derived/shoulder_hours.py

For ERCOT and CAISO, by local month from January 2019, from hourly demand and generation by fuel. "Shoulder" is this
table's term, defined here, not an industry standard.

Inputs (no request is made):
- EIA-930 hourly demand, solar and wind (and battery for ERCOT) from the per-balancing-authority workbooks the emissions
  connector saved (warehouse/raw/eia930_emissions/<run>/<BA>.xlsx, sheet Published Hourly Data, EIA's Adjusted columns;
  solar is SUN plus SNB, wind WND plus WNB; an hour is dated by its start). California stops after November 2025: EIA's
  generation series for California changed on 16 December 2025 (docs/methods/eia930_caiso_break.md); its solar and wind
  did not break there, but this table does not mix a changed series in.
- CAISO's battery output: caiso_battery_storage (CAISO's own, 5-minute, from August 2025), averaged to the hour.
- CAISO's curtailment: caiso_curtailment_daily (curtailed_solar_mwh plus curtailed_wind_mwh). ERCOT's is not held.
- The fleet: storage_buildout_monthly, battery_operating_mw and battery_operating_mwh of the grid and month.

The average day of a month: for each local hour (0 to 23), the mean over the month's complete days (every hour of
demand, solar and wind held) of demand, solar, wind, net load (demand less solar and wind) and battery output (positive
discharging). A month is written only when at least 90 percent of its days are complete; never filled.

On the average day:
- midday surplus: the run of hours around net load's lowest hour in which net load is below its daily mean; its MWh are
  the sum of (mean less net load) over those hours;
- evening shoulder: from the first hour after solar's highest hour in which solar is below half of that highest value,
  to the first hour, after net load has risen above its daily mean, in which net load is back at or below that mean;
  if net load stays above it to midnight the shoulder ends at midnight and is flagged (shoulder_runs_to_midnight);
  if net load does not rise above its mean after the start, the shoulder is 0 hours. Its MWh are the sum of (net load less mean) over its hours;
- the fleet: fleet_hours = battery_operating_mwh / battery_operating_mw (its average duration);
  shoulder_hours_covered = min(shoulder_hours, fleet_hours): the hours the fleet can run at its rated power through the
  shoulder; shoulder_hours_needed = shoulder_mwh_above_mean / battery_operating_mw: the hours a fleet of that power would
  have to run at rated power to deliver all of the shoulder's MWh above the mean.

Session 80, two additions (Samuel's ruling on session 75's "For Samuel", 2 and 3):
- a second shoulder measure that ends inside the evening (shoulder2_*): the run of hours around the evening's highest
  net load (the highest from the shoulder's start to midnight) in which net load is above the midpoint between its
  daily mean and that peak. Its MWh are the sum of (net load less the midpoint) over the run. The fleet against it:
  shoulder2_hours_covered and shoulder2_hours_needed, as for the first measure.
- the worst days: for each grid and local year, the ten complete days with the largest evening shoulder energy above
  the day's own mean (the first measure, on that day's 24 hours). One row set per such day (freq P1D, ts_utc the local
  day at 00:00:00Z): worst_rank, the day's shoulder by both measures, the hours of storage the month's fleet would need
  at its rated power, and what the fleet's batteries did in that shoulder where every hour of the day holds a battery
  output (day_battery_discharge_mwh, day_battery_peak_mw, day_battery_hours = discharge over the fleet's MW). Yearly
  rows (year_worst10_*) put the ten days beside the average day. A day of 23 or 25 local hours is not ranked.

California's two sources are two entities, never mixed (session 80):
- iso:caiso      EIA-930, January 2019 to November 2025, as above;
- iso:caiso_own  CAISO's own supply by fuel (caiso_fuel_supply, hourly from June 2025): solar and wind are CAISO's;
                 demand is the sum of its thirteen sources (every source, imports and batteries net: the load the supply
                 serves); battery output is its batteries source.

A machine without the EIA workbooks (raw files stay on the machine that downloaded them) cannot rebuild an EIA grid. For
such a grid the earlier file's rows are kept as they stand, and the second measure of its average days is computed from
the average day the earlier file holds (avg_*_mw_hHH, four decimals); its worst days are not written, and the header and
the log say so. --out-dir writes a trial table elsewhere and leaves warehouse/output alone.
"""

import argparse
import glob
import os
import shutil
import sys
from datetime import timedelta

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, HERE)
import caiso_join as cj  # noqa: E402  (session 82: California's hours that EIA holds one hour late)
import impossible_hours  # noqa: E402  (session 103: EIA's impossible demand hours are not used)
import iso_prices as ip  # noqa: E402
import price_board as pb  # noqa: E402

NAME = "shoulder_hours_monthly"
SOURCE = "erw:shoulder_hours"
METHOD_URL = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/shoulder_hours.md"  # a URL in every row, not a path (session 77)
RAW = os.path.join(ROOT, "warehouse", "raw", "eia930_emissions")
GRIDS = {
    "ercot": dict(ba="ERCO", tz="America/Chicago", geo="US-TX", last=None),
    "caiso": dict(ba="CISO", tz="America/Los_Angeles", geo="US-CA", last="2025-11"),  # the last month before EIA's break
    # session 80: California on CAISO's own supply by fuel, its own entity; the fleet and the curtailment are CAISO's
    "caiso_own": dict(ba=None, supply="caiso_fuel_supply", tz="America/Los_Angeles", geo="US-CA", last=None, first="2025-06",
                      fleet="caiso"),
}
FIRST = "2019-01"
WORST = 10   # the days ranked per grid and local year
SUPPLY_ALL = ["batteries_mw", "biogas_mw", "biomass_mw", "coal_mw", "geothermal_mw", "imports_mw", "large_hydro_mw",
              "natural_gas_mw", "nuclear_mw", "other_mw", "small_hydro_mw", "solar_mw", "wind_mw"]
NEAR = 0.9
COLS = {"Adjusted demand": "demand", "Adjusted SUN Gen": "sun", "Adjusted SNB Gen": "snb", "Adjusted WND Gen": "wnd",
        "Adjusted WNB Gen": "wnb", "Adjusted BAT Gen": "bat"}


def workbook(ba):
    files = [f for f in glob.glob(os.path.join(RAW, "*", f"*_{ba}.xlsx")) if os.path.getsize(f) > 0]
    if not files:
        raise FileNotFoundError(f"no {ba} workbook under {RAW}")
    return max(files, key=lambda f: (os.path.basename(os.path.dirname(f)), os.path.basename(f)))


def hourly(ba):
    """EIA-930 hourly MW (MWh in the hour) by hour start, UTC: demand, solar, wind, battery."""
    import openpyxl
    path = workbook(ba)
    ws = openpyxl.load_workbook(path, read_only=True, data_only=True)["Published Hourly Data"]
    rows = ws.iter_rows(values_only=True)
    head = list(next(rows))
    t = head.index("UTC time")
    idx = {v: head.index(k) for k, v in COLS.items() if k in head}
    out = []
    for r in rows:
        ts = r[t]
        if ts is None or ts.year < 2018:
            continue
        rec = {"ts": ts - timedelta(hours=1)}
        for k, i in idx.items():
            v = r[i]
            rec[k] = float(v) if isinstance(v, (int, float)) else np.nan
        out.append(rec)
    d = pd.DataFrame(out)
    d["ts"] = pd.to_datetime(d["ts"]).dt.tz_localize("UTC")
    if ba == "CISO":  # session 82: EIA's California values of 2023-11 to 2025-12-02 sit one hour late
        d = cj.true_hours(d.set_index("ts")).rename_axis("ts").reset_index()
    # session 103: an impossible hour of demand is a blank (docs/methods/impossible_hours.md); its day is then not a
    # complete day, by this table's own rule. Solar, wind and battery output are not screened: they move further in an hour
    d = d.drop_duplicates("ts").sort_values("ts").reset_index(drop=True)
    d["demand"] = impossible_hours.screen(d.set_index("ts")["demand"]).values
    for k in ("sun", "snb", "wnd", "wnb", "bat"):
        if k not in d:
            d[k] = np.nan
    d["solar"] = d[["sun", "snb"]].sum(axis=1, min_count=1)
    d["wind"] = d[["wnd", "wnb"]].sum(axis=1, min_count=1)
    return d[["ts", "demand", "solar", "wind", "bat"]], path


def supply_hourly(name):
    """CAISO's own hours (session 80): demand as the sum of every source of its supply (imports and batteries net), solar,
    wind and battery output, by hour start, UTC. Only hours that hold all thirteen sources."""
    path = os.path.join(ip.OUT_DIR, name + ".csv")
    f = pd.read_csv(path, skiprows=ip.header_rows(path), usecols=["entity", "variable", "ts_utc", "value"])
    w = f[f["entity"] == "caiso:ISO"].pivot(index="ts_utc", columns="variable", values="value")
    missing = [c for c in SUPPLY_ALL if c not in w]
    if missing:
        raise RuntimeError(f"{name}: no {missing}")
    w = w.dropna(subset=SUPPLY_ALL)
    d = pd.DataFrame({"ts": pd.to_datetime(w.index, utc=True), "demand": w[SUPPLY_ALL].sum(axis=1).values,
                      "solar": w["solar_mw"].values, "wind": w["wind_mw"].values, "bat": w["batteries_mw"].values})
    return d, path


def second_measure(nl, mean, start):
    """The second shoulder measure (session 80), which ends inside the evening: the run of hours around the evening's
    highest net load (the highest from hour start to midnight) in which net load is above the midpoint between the
    daily mean and that peak. nl: 24 local hours. Returns a dict; 0 hours when the evening never passes its mean."""
    peak_h = start + int(np.argmax(nl[start:]))
    peak = float(nl[peak_h])
    out = dict(evening_peak_hour=peak_h, evening_peak_mw=peak)
    if not peak > mean:
        out.update(shoulder2_level_mw=np.nan, shoulder2_start_hour=peak_h, shoulder2_end_hour=peak_h, shoulder2_hours=0,
                   shoulder2_mwh_above_midpoint=0.0, shoulder2_runs_to_midnight=0)
        return out
    level = (mean + peak) / 2
    a = b = peak_h
    while a - 1 >= start and nl[a - 1] > level:
        a -= 1
    while b + 1 <= 23 and nl[b + 1] > level:
        b += 1
    out.update(shoulder2_level_mw=level, shoulder2_start_hour=a, shoulder2_end_hour=b + 1, shoulder2_hours=b + 1 - a,
               shoulder2_mwh_above_midpoint=float(sum(nl[h] - level for h in range(a, b + 1))),
               shoulder2_runs_to_midnight=int(b == 23 and nl[23] > level))
    return out


def day_metrics(avg):
    """The midday surplus and the evening shoulder of one average day. avg: 24 rows (local hours 0 to 23) with demand,
    solar, wind and net_load. Returns a dict of the day's figures (hours as local hours of the day)."""
    nl = avg["net_load"].to_numpy(dtype=float)
    sol = avg["solar"].to_numpy(dtype=float)
    mean = float(nl.mean())
    low = int(nl.argmin())
    a = low
    while a - 1 >= 0 and nl[a - 1] < mean:
        a -= 1
    b = low
    while b + 1 <= 23 and nl[b + 1] < mean:
        b += 1
    trough = range(a, b + 1) if nl[low] < mean else range(0)
    out = dict(net_load_mean_mw=mean, midday_low_hour=low, midday_surplus_hours=len(trough),
               midday_surplus_mwh=float(sum(mean - nl[h] for h in trough)))
    peak = int(sol.argmax())
    start = next((h for h in range(peak + 1, 24) if sol[h] < 0.5 * sol[peak]), None)
    if start is None or sol[peak] <= 0:
        out.update(shoulder_start_hour=np.nan, shoulder_end_hour=np.nan, shoulder_hours=np.nan,
                   shoulder_mwh_above_mean=np.nan, shoulder_runs_to_midnight=np.nan)
        return out
    rise = next((h for h in range(start, 24) if nl[h] > mean), None)  # net load must be above its mean to fall back
    out.update(second_measure(nl, mean, start))  # session 80
    if rise is None:
        out.update(shoulder_start_hour=start, shoulder_end_hour=start, shoulder_hours=0, shoulder_mwh_above_mean=0.0,
                   shoulder_runs_to_midnight=0)
        return out
    end = next((h for h in range(rise + 1, 24) if nl[h] <= mean), None)
    to_midnight = end is None
    end = 24 if to_midnight else end
    out.update(shoulder_start_hour=start, shoulder_end_hour=end, shoulder_hours=end - start,
               shoulder_mwh_above_mean=float(sum(max(0.0, nl[h] - mean) for h in range(start, end))),
               shoulder_runs_to_midnight=int(to_midnight))
    return out


def fleet_metrics(shoulder_hours, shoulder_mwh, mw, mwh, shoulder2_hours=None, shoulder2_mwh=None):
    """The fleet's hours against the shoulder. Hours covered never exceed the fleet's MWh over its MW. Session 80: the
    same against the second measure, when it is given."""
    if mw is None or mwh is None or not mw > 0 or shoulder_hours is None or np.isnan(shoulder_hours):
        return {}
    fh = mwh / mw
    out = dict(fleet_mw=mw, fleet_mwh=mwh, fleet_hours=fh, shoulder_hours_covered=min(shoulder_hours, fh),
               shoulder_hours_needed=shoulder_mwh / mw)
    if shoulder2_hours is not None and shoulder2_mwh is not None and not np.isnan(shoulder2_hours):
        out.update(shoulder2_hours_covered=min(shoulder2_hours, fh), shoulder2_hours_needed=shoulder2_mwh / mw)
    return out


def unit_of(k):
    """A variable's unit, from its name (session 80: one rule for every row; session 75's two rules left
    shoulder_mwh_above_mean of a month as a count)."""
    if "_mwh" in k:
        return "MWh"
    if k.endswith("_mw") or "_mw_h" in k:
        return "MW"
    if k.startswith("year_") and k.endswith("runs_to_midnight"):
        return "ratio"
    if k.endswith(("_hours", "_covered", "_needed", "_hour")):
        return "hour"
    return "count"


def entity_of(grid):
    return f"iso:{grid}"


def worst_days(h, fl, grid, log):
    """The ten days of each local year with the largest evening shoulder energy above the day's own mean, among the days
    that hold all 24 local hours of demand, solar and wind. h: the grid's hours (day, hour, m, demand, solar, wind,
    net_load, bat). Returns ({day: figures}, {year: yearly figures})."""
    per = {}
    for day, x in h.groupby("day"):
        x = x.sort_values("hour")
        if len(x) != 24 or list(x["hour"]) != list(range(24)) or x[["demand", "solar", "wind"]].isna().any().any():
            continue  # a clock-change day (23 or 25 hours) or a day short of an hour is not ranked
        dm = day_metrics(x.set_index("hour")[["demand", "solar", "wind", "net_load"]])
        if not dm.get("shoulder_hours", 0) or np.isnan(dm["shoulder_hours"]):
            continue
        v = dict(day_shoulder_mwh_above_mean=dm["shoulder_mwh_above_mean"], day_shoulder_hours=dm["shoulder_hours"],
                 day_shoulder_start_hour=dm["shoulder_start_hour"], day_shoulder_runs_to_midnight=dm["shoulder_runs_to_midnight"],
                 day_shoulder2_hours=dm["shoulder2_hours"], day_shoulder2_start_hour=dm["shoulder2_start_hour"],
                 day_shoulder2_end_hour=dm["shoulder2_end_hour"], day_shoulder2_mwh_above_midpoint=dm["shoulder2_mwh_above_midpoint"],
                 day_evening_peak_mw=dm["evening_peak_mw"], day_net_load_mean_mw=dm["net_load_mean_mw"])
        m = day[:7]
        mw = float(fl.loc[m, "battery_operating_mw"]) if m in fl.index and "battery_operating_mw" in fl.columns \
            and not pd.isna(fl.loc[m, "battery_operating_mw"]) else None
        if mw and mw > 0:
            v.update(day_fleet_mw=mw, day_shoulder_hours_needed=dm["shoulder_mwh_above_mean"] / mw,
                     day_shoulder2_hours_needed=dm["shoulder2_mwh_above_midpoint"] / mw)
        if x["bat"].notna().all():  # what the batteries did, only where every hour of the day holds their output
            b = x.set_index("hour")["bat"].loc[int(dm["shoulder_start_hour"]):int(dm["shoulder_end_hour"]) - 1]
            v.update(day_battery_discharge_mwh=float(b.clip(lower=0).sum()), day_battery_peak_mw=float(b.max()))
            if mw and mw > 0:
                v["day_battery_hours"] = float(b.clip(lower=0).sum()) / mw
        per[day] = v
    days, years = {}, {}
    by_year = {}
    for day, v in per.items():
        by_year.setdefault(day[:4], []).append((day, v))
    for y, dv in sorted(by_year.items()):
        top = sorted(dv, key=lambda t: (-t[1]["day_shoulder_mwh_above_mean"], t[0]))[:WORST]
        for rank, (day, v) in enumerate(top, 1):
            days[day] = dict(v, worst_rank=rank)
        yv = dict(year_days_ranked=len(dv), year_worst10_days=len(top),
                  year_worst10_mean_shoulder_mwh_above_mean=float(np.mean([v["day_shoulder_mwh_above_mean"] for _, v in top])),
                  year_worst10_mean_shoulder_hours=float(np.mean([v["day_shoulder_hours"] for _, v in top])),
                  year_worst10_mean_shoulder2_hours=float(np.mean([v["day_shoulder2_hours"] for _, v in top])))
        withfleet = [v for _, v in top if "day_shoulder_hours_needed" in v]
        if len(withfleet) == len(top):  # a mean over the ten, or none: never over the days that happen to have a fleet
            yv.update(year_worst10_mean_shoulder_hours_needed=float(np.mean([v["day_shoulder_hours_needed"] for v in withfleet])),
                      year_worst10_max_shoulder_hours_needed=float(max(v["day_shoulder_hours_needed"] for v in withfleet)),
                      year_worst10_mean_shoulder2_hours_needed=float(np.mean([v["day_shoulder2_hours_needed"] for v in withfleet])))
        withbat = [v for _, v in top if "day_battery_hours" in v]
        yv["year_worst10_days_with_battery"] = len(withbat)
        if len(withbat) == len(top):
            yv["year_worst10_mean_battery_hours"] = float(np.mean([v["day_battery_hours"] for v in withbat]))
        years[y] = yv
        log(f"  {grid} {y}: {len(dv)} days ranked; the worst, {top[0][0]}, {top[0][1]['day_shoulder_mwh_above_mean']:.0f} MWh above its mean")
    return days, years


def row(grid, g, variable, ts, value, freq, retrieved):
    return dict(entity=entity_of(grid), variable=variable, ts_utc=ts, value=round(float(value), 4), unit=unit_of(variable), freq=freq,
                geo=g["geo"], market="", node="", source=SOURCE, source_url=METHOD_URL, retrieved_at=retrieved, vintage="")


YEAR_MEANS = ("shoulder_hours", "shoulder_mwh_above_mean", "shoulder_start_hour", "shoulder_runs_to_midnight", "midday_surplus_hours",
              "midday_surplus_mwh", "curtailed_mwh_per_day", "shoulder_hours_covered", "shoulder_hours_needed",
              # session 80: the second measure
              "shoulder2_hours", "shoulder2_mwh_above_midpoint", "shoulder2_runs_to_midnight", "shoulder2_hours_covered",
              "shoulder2_hours_needed")


def caiso_battery():
    s = pb.read_table("caiso_battery_storage")
    s = s[s["variable"] == "batteries_mw"]
    x = pd.Series(s["value"].values, index=pd.DatetimeIndex(s["ts"]))
    n = x.groupby(x.index.floor("h")).size()
    h = x.groupby(x.index.floor("h")).mean()
    return h[n == 12]


def curtailment_by_month():
    c = pb.read_table("caiso_curtailment_daily")
    c = c[c["variable"].isin(["curtailed_solar_mwh", "curtailed_wind_mwh"])]
    c["m"] = pd.DatetimeIndex(c["ts"]).strftime("%Y-%m")
    days = c.groupby("m")["ts"].nunique()
    return c.groupby("m")["value"].sum(), days


def fleet_by_month(grid):
    f = pb.read_table("storage_buildout_monthly")
    f = f[f["entity"] == f"iso:{grid}"]
    f["m"] = pd.DatetimeIndex(f["ts"]).strftime("%Y-%m")
    return f.pivot_table(index="m", columns="variable", values="value", aggfunc="first")


def build(grid, log):
    g = GRIDS[grid]
    h, path = supply_hourly(g["supply"]) if g.get("supply") else hourly(g["ba"])
    if grid == "caiso":
        cb = caiso_battery()
        h = h.set_index("ts")
        h["bat"] = cb.reindex(h.index)
        h = h.reset_index()
    h["local"] = h["ts"].dt.tz_convert(g["tz"])
    h["day"] = h["local"].dt.strftime("%Y-%m-%d")
    h["hour"] = h["local"].dt.hour
    h["m"] = h["local"].dt.strftime("%Y-%m")
    h = h[(h["m"] >= g.get("first", FIRST)) & ((g["last"] is None) | (h["m"] <= (g["last"] or "9999")))]
    h["net_load"] = h["demand"] - h["solar"] - h["wind"]
    need = h.groupby("day")["ts"].size()
    ok = h.dropna(subset=["demand", "solar", "wind"]).groupby("day").size()
    full = {d for d in need.index if ok.get(d, 0) == need[d] and need[d] in (23, 24, 25)}
    curt, curt_days = curtailment_by_month() if grid.startswith("caiso") else (None, None)
    fl = fleet_by_month(g.get("fleet", grid))
    rows, months = [], []
    for m, x in h.groupby("m"):
        dim = pd.Period(m).days_in_month
        days = sorted(set(x["day"]) & full)
        if len(days) < NEAR * dim:
            log(f"  {grid} {m}: {len(days)} of {dim} days complete, not written")
            continue
        x = x[x["day"].isin(days)]
        avg = x.groupby("hour")[["demand", "solar", "wind", "net_load", "bat"]].mean().reindex(range(24))
        if avg[["demand", "solar", "wind"]].isna().any().any():
            log(f"  {grid} {m}: a local hour of the average day not held, not written")
            continue
        v = dict(days_held=len(days), days_in_month=dim)
        for k in ("demand", "solar", "wind", "net_load"):
            for hr in range(24):
                v[f"avg_{k}_mw_h{hr:02d}"] = avg.loc[hr, k]
        if x.groupby("day")["bat"].apply(lambda b: b.notna().all()).all():  # battery output in every hour of every held day
            for hr in range(24):
                v[f"avg_battery_mw_h{hr:02d}"] = avg.loc[hr, "bat"]
        dm = day_metrics(avg)
        v.update({k: val for k, val in dm.items() if not (isinstance(val, float) and np.isnan(val))})
        if curt is not None and m in curt.index and curt_days.get(m, 0) == dim:
            v["curtailed_mwh_per_day"] = float(curt[m]) / dim
        if m in fl.index and "battery_operating_mw" in fl.columns:
            mw = fl.loc[m].get("battery_operating_mw")
            mwh = fl.loc[m].get("battery_operating_mwh")
            v.update(fleet_metrics(dm.get("shoulder_hours"), dm.get("shoulder_mwh_above_mean", 0.0),
                                   None if pd.isna(mw) else float(mw), None if pd.isna(mwh) else float(mwh),
                                   dm.get("shoulder2_hours"), dm.get("shoulder2_mwh_above_midpoint")))
        months.append((m, v))
        ts = f"{m}-01T00:00:00Z"
        for k, val in v.items():
            if val is None or (isinstance(val, float) and np.isnan(val)):
                continue
            rows.append(row(grid, g, k, ts, val, "P1M", ip.utc_iso(pd.Timestamp.now(tz="UTC"))))
    # session 75: each year's figures, so the page's table does no arithmetic: the mean over the year's months held, and
    # the fleet at the year's last month held that has one (freq P1Y, ts_utc the year's first day)
    by_year = {}
    for m, v in months:
        by_year.setdefault(m[:4], []).append((m, v))
    now = pd.Timestamp.now(tz="UTC").strftime("%Y-%m-%dT%H:%M:%SZ")
    for y, mv in sorted(by_year.items()):
        f = pd.DataFrame([v for _, v in mv])
        yv = {"year_months_held": len(mv)}
        for k in YEAR_MEANS:
            if k in f and f[k].notna().any():
                yv[f"year_mean_{k}"] = float(f[k].mean())
        withfleet = [v for _, v in mv if "fleet_mw" in v]  # the year's last month that has a fleet (EIA-860M lags)
        if withfleet:
            for k in ("fleet_mw", "fleet_mwh", "fleet_hours"):
                yv[f"year_end_{k}"] = withfleet[-1][k]
        for k, val in yv.items():
            rows.append(row(grid, g, k, f"{y}-01-01T00:00:00Z", val, "P1Y", now))
    # session 80: the worst days of each year, and each year's ten beside its average day
    wd, wy = worst_days(h[h["day"].isin(full)], fl, grid, log)
    for day, v in sorted(wd.items()):
        for k, val in v.items():
            rows.append(row(grid, g, k, f"{day}T00:00:00Z", val, "P1D", now))
    for y, yv in sorted(wy.items()):
        for k, val in yv.items():
            rows.append(row(grid, g, k, f"{y}-01-01T00:00:00Z", val, "P1Y", now))
    log(f"  {grid}: {len(months)} months, {len(by_year)} years from {os.path.relpath(path, ROOT)}")
    return rows, path


def from_held(grid, log):
    """An EIA grid on a machine without its workbook (session 80): nothing of it can be rebuilt. Its earlier rows stay
    (the writer merges into the earlier file), and the second measure of each month's average day is computed from the
    average day the earlier file holds. Returns the new rows only; the grid's worst days are not written."""
    g = GRIDS[grid]
    path = os.path.join(ip.OUT_DIR, NAME + ".csv")
    if not os.path.exists(path):
        raise FileNotFoundError(f"{grid}: no workbook and no earlier {NAME}.csv")
    t = pd.read_csv(path, skiprows=ip.header_rows(path), dtype=str, keep_default_na=False)
    t = t[(t["entity"] == entity_of(grid)) & (t["freq"] == "P1M")]
    w = t.assign(v=t["value"].astype(float)).pivot(index="ts_utc", columns="variable", values="v")
    now = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
    rows, by_year, differ = [], {}, 0
    for ts, r in w.iterrows():
        avg = pd.DataFrame({k: [r.get(f"avg_{k}_mw_h{hr:02d}") for hr in range(24)] for k in ("demand", "solar", "wind", "net_load")})
        if avg.isna().any().any():
            continue
        dm = day_metrics(avg)
        # the first measure recomputed from the held average day must be the held figure, or the average day is not enough
        for k in ("shoulder_hours", "shoulder_start_hour", "shoulder_end_hour"):
            if k in r and not pd.isna(r[k]) and abs(float(dm[k]) - float(r[k])) > 1e-9:
                differ += 1
        v = {k: val for k, val in dm.items() if k.startswith(("shoulder2_", "evening_peak_")) and not (isinstance(val, float) and np.isnan(val))}
        if not pd.isna(r.get("fleet_mw")) and not pd.isna(r.get("fleet_mwh")):
            f = fleet_metrics(dm.get("shoulder_hours"), dm.get("shoulder_mwh_above_mean", 0.0), float(r["fleet_mw"]), float(r["fleet_mwh"]),
                              dm.get("shoulder2_hours"), dm.get("shoulder2_mwh_above_midpoint"))
            v.update({k: val for k, val in f.items() if k.startswith("shoulder2_")})
        for k, val in v.items():
            rows.append(row(grid, g, k, ts, val, "P1M", now))
        by_year.setdefault(ts[:4], []).append(v)
    if differ:
        raise RuntimeError(f"{grid}: the first measure recomputed from the held average day differs from the held figure in "
                           f"{differ} cells; the second measure is not written from it")
    for y, vs in sorted(by_year.items()):
        f = pd.DataFrame(vs)
        for k in YEAR_MEANS:
            if k.startswith("shoulder2_") and k in f and f[k].notna().any():
                rows.append(row(grid, g, f"year_mean_{k}", f"{y}-01-01T00:00:00Z", float(f[k].mean()), "P1Y", now))
    log(f"  {grid}: no workbook on this machine; {len(w)} months kept from the earlier file, the second measure of {len(by_year)} "
        "years computed from its average days; no worst days")
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser(description="The shoulder hours (sessions 75 and 80)")
    ap.add_argument("--out-dir", help="a trial run: the table, its log and the registry under this directory, starting from a "
                                      "copy of the earlier table; nothing in warehouse/output")
    a = ap.parse_args(argv)
    if a.out_dir:
        inputs = ip.OUT_DIR
        os.makedirs(a.out_dir, exist_ok=True)
        for t in (NAME, "caiso_fuel_supply", "caiso_battery_storage", "caiso_curtailment_daily", "storage_buildout_monthly"):
            src, dst = os.path.join(inputs, t + ".csv"), os.path.join(a.out_dir, t + ".csv")
            if os.path.exists(src) and not os.path.exists(dst):
                shutil.copy(src, dst)  # the trial reads its inputs, and merges into the earlier table, beside its output
        ip.set_out_dir(a.out_dir)
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = pd.Timestamp.now(tz="UTC").strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"shoulder_hours_{run_id}.log"))
    rows, paths, kept = [], [], []
    for grid in GRIDS:
        try:
            r, p = build(grid, log)
            paths.append(os.path.relpath(p, ROOT).replace("\\", "/"))
        except FileNotFoundError as exc:
            if GRIDS[grid].get("supply"):
                raise
            log(f"  {grid}: {exc}")
            r = from_held(grid, log)
            kept.append(grid)
        rows += r
    s = pd.DataFrame(rows)[ip.SERIES_COLS]
    header = [
        "Energy Research Warehouse (ERW): the shoulder hours, ERCOT and CAISO, by local month (sessions 75 and 80)",
        "Shape: series (docs/datastandard.md v0). freq P1M; ts_utc is the first day of the local month at 00:00:00Z. The average "
        "day by local hour (avg_<demand|solar|wind|net_load|battery>_mw_hHH), the midday surplus, the evening shoulder and the "
        "battery fleet against it; definitions in docs/methods/shoulder_hours.md (\"shoulder\" is this table's term). Session 80: "
        "a second measure that ends inside the evening (shoulder2_*: net load above the midpoint between its daily mean and its "
        "evening peak); freq P1D, the ten days of each local year with the largest evening shoulder energy (worst_rank, day_*); "
        "freq P1Y, each year's means and its ten worst days (year_*).",
        "Window: from 2019-01; iso:caiso (EIA-930) to 2025-11 (EIA's generation series for California changed after it, "
        "docs/methods/eia930_caiso_break.md); iso:caiso_own is CAISO's own supply by fuel from 2025-06, a separate entity, never "
        "mixed with EIA-930; a month with fewer than 90 percent of its days complete is not written.",
        f"Retrieved: {run_id} (UTC) by warehouse/derived/shoulder_hours.py",
        f"Run log: warehouse/output/logs/shoulder_hours_{run_id}.log",
        "Derived from: storage_buildout_monthly; caiso_battery_storage; caiso_curtailment_daily; caiso_fuel_supply",
        f"Source: {SOURCE} EIA Form EIA-930 hourly demand and net generation by energy source, the per-BA workbooks "
        f"(https://www.eia.gov/electricity/gridmonitor/knownissues/xls/<BA>.xlsx), and CAISO's supply by fuel (caiso_fuel_supply); "
        f"read by this run from {'; '.join(paths)}",
    ]
    if kept:
        header.append("Not rebuilt by this run (no EIA workbook on the machine): " + ", ".join(entity_of(k) for k in kept) + ". Their rows are "
                      "the earlier file's; this run added only the second measure of their average days, computed from the earlier "
                      "file's avg_*_mw_hHH rows, and no worst day.")
    header.append("License: public")
    # Session 103: a grid rebuilt by this run is written whole. The table is merged into the earlier file (a grid whose
    # workbook is not on the machine keeps its rows), and until now a row this run no longer makes stayed too: a day that
    # left a year's ten worst kept its worst_rank, so a year could hold eleven ranked days (tests/test_session80.py found
    # it on the first rebuild with a newer day). The earlier rows of a rebuilt grid that this run does not make are dropped.
    target = os.path.join(ip.OUT_DIR, NAME + ".csv")
    rebuilt = set(s["entity"]) - {entity_of(k) for k in kept}
    if os.path.exists(target) and rebuilt:
        old = ip.read_series(target)
        made = set(zip(s["entity"], s["variable"], s["ts_utc"]))
        in_run = pd.Series([k in made for k in zip(old["entity"], old["variable"], old["ts_utc"])], index=old.index)
        stale = old["entity"].isin(rebuilt) & ~in_run
        if stale.any():
            log(f"  {int(stale.sum())} earlier rows of {', '.join(sorted(rebuilt))} are not made by this run and are dropped: "
                + ", ".join(f"{v} {n}" for v, n in old[stale].groupby("variable").size().head(12).items()))
            ip._require_lock(target, f"rebuilding {NAME}")
            carried = old[~stale & ~in_run]   # the rows of a grid this run could not rebuild
            os.remove(target)
            s = pd.concat([carried, s.astype({c: str for c in s.columns if c != "value"})], ignore_index=True) if len(carried) else s
    ip.write_csv(s, NAME, header, log)
    ip.update_sources([dict(source=SOURCE, publisher="Energy Research Warehouse (ERW), derived",
                            report="The shoulder hours by grid and month (docs/methods/shoulder_hours.md)",
                            report_url=METHOD_URL,
                            document_list="docs/methods/shoulder_hours.md", license="public", tables=[NAME])])
    log.close()
    print(f"{NAME}: {len(s):,} rows written by this run, {s['ts_utc'].nunique()} periods, {s['entity'].nunique()} entities"
          + (f"; kept from the earlier file: {', '.join(kept)}" if kept else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
