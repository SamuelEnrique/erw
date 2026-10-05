#!/usr/bin/env python3
"""How hard the system works: the evening ramp, the lowest net load, what each fuel gives in the tightest hours, and
the dark, calm stretches, by grid and year (session 123).

Energy Research Warehouse (ERW). Method: docs/methods/grid_stress.md. Page: /mix/stress (in review). No request is made.

    python warehouse/derived/mix_stress.py                 # the table, under the data lock
    python warehouse/derived/mix_stress.py --out-dir DIR   # a trial run: the table under DIR, nothing in warehouse/output
    python warehouse/derived/mix_stress.py --snapshot      # also the site's own copy (site/data/stress/)
    python warehouse/derived/mix_stress.py --snapshot-only # the site's copy from the table as it is

The hours are the energy mix's (warehouse/derived/mix_profile.py hours_of): EIA-930's hourly demand and net generation
by source for the seven ISO grids from January 2019; California from the join is CAISO's own supply by fuel, with
EIA's demand; an impossible hour of demand is a blank (session 118's rule). Only held hours with a demand are used.
Every figure here is a record or rests on a few hours, so two more kinds of hour are not used. An hour of EIA's whose
own balance does not close: demand differs from net generation less total interchange by more than a fifth of demand
(the mix's own test for its records, mix_profile.BALANCE; CAISO's own hours are not put to it, for EIA's demand is not
CAISO's sum). Where EIA's interchange is blank the balance cannot be taken, and the hour is used only when its demand
stands to its net generation as in the grid's hours that do close (inside the middle 99 percent of their ratio). And an hour that repeats the hour before to the MW in net generation, wind and
solar: a stale report. The log counts both.
Installed capacity is EIA's monthly generator inventory (eia860m_operating_generators, and the units retired since
January 2025 from eia860m_retired_generators), nameplate MW by the balancing authority EIA gives each unit, month by
month from each unit's first month of operation. The battery fleet is storage_buildout_monthly's.

THE DEFINITIONS, AS COMPUTED. Local time is the grid's. A year is the local calendar year.

  net load                  demand less wind less solar, MW, hour by hour
  the evening ramp          for each day, the largest rise of net load from one hour to the next, between the hours
                            starting 14:00 and 22:00 local (eight steps), MW per hour; and the largest rise over three
                            hours in the same window. Only steps between hours that are both used and next to each other;
                            a one-hour rise that the next hour takes back by more than half is a spike in the data, not
                            a ramp, and is not counted
  the lowest net load       the hour of the year with the least net load
  the tightest hours        the 100 held hours of the year with the highest net load
  a fuel in those hours     its mean output over the 100 hours, over its installed capacity in each hour's month
  dark and calm             an hour in which wind and solar together put out less than a tenth of their installed
                            capacity of that month. A stretch is a run of such hours, each held and each next to the last;
                            an hour that is not held ends it. A stretch belongs to the year it begins in
  the energy missing        over a stretch, the year's average output of wind and solar (MW, over the year's held hours)
                            less what they put out, summed over its hours, MWh
  hours of the battery fleet   that energy over the fleet's power (MW) of the stretch's first month: the hours the whole
                            fleet would have to discharge at full power to supply it. Beside it, the same energy over the
                            fleet's energy (MWh): how many times the fleet would have to be emptied

WHAT THE INVENTORY CANNOT GIVE. It lists the units operating now and those retired since January 2025. A unit retired
before 2025 is in neither, so the capacity of a fuel that lost plants before then is understated for the earlier years,
and its output would look like a larger share of capacity than it was. So the share of installed capacity is written
for wind and solar for every year (few of them have retired), and for natural gas, coal, nuclear, and hydro and
storage, for 2025 and later only.

HYDRO AND STORAGE ARE SET AGAINST CAPACITY TOGETHER. The inventory counts pumped storage with storage; the grids do not
all report it that way. PJM's hydro output in its tightest hours of 2025 is 157 percent of its conventional hydro
capacity: its pumped storage is in its "hydro". MISO's is 106 percent. So each one's output is written, and the share
of installed capacity is of the two together: hydro and storage output over conventional hydro, pumped storage,
batteries and flywheels.

grid_stress_yearly (series, freq P1Y, ts_utc the local year's first day at 00:00:00Z, entity iso:<grid>; x_at: the hour
(UTC, its start) a record or a stretch begins at, blank otherwise):
    hours_held, hours_in_year, months_held        what the year rests on (a year is written when it holds at least nine tenths of its hours to date)
    wind_reported, solar_reported                 1 when the file reports that source in the year; a source it does not report is no part of the year's
                                                  net load or of its installed wind and solar capacity (New York's solar)
    peak_demand_mw (x_at), net_load_peak_mw (x_at)
    evening_ramp_max_mw_per_h (x_at: the hour the rise starts), evening_ramp_median_mw_per_h, evening_ramp_3h_max_mw (x_at)
    evening_ramp_max_share_of_peak_pct, evening_ramp_3h_max_share_of_peak_pct      of the year's peak demand
    net_load_min_mw (x_at), net_load_min_share_of_peak_pct, net_load_min_wind_solar_share_pct (wind and solar over demand in that hour)
    tight_net_load_mw                             the mean net load of the 100 tightest hours
    tight_<fuel>_mw                               fuel: natural_gas, coal, nuclear, wind, solar, hydro, storage, and hydro_storage (the two together)
    capacity_<fuel>_mw, tight_<fuel>_share_of_capacity_pct                         fuel: natural_gas, coal, nuclear, wind, solar, hydro_storage
    wind_solar_mean_mw, wind_solar_capacity_mw    the year's average output, and the capacity at the year's end (or its last month held)
    calm_hours, calm_stretches_ge24h              hours below the tenth, and stretches of a day or longer
    calm_longest_hours (x_at), calm_longest_missing_mwh, calm_longest_fleet_full_power_hours, calm_longest_fleet_energy_multiples,
    calm_longest_fleet_mw, calm_longest_fleet_mwh
"""

import argparse
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, HERE)
import caiso_join as cj  # noqa: E402
import iso_prices as ip  # noqa: E402
import mix_profile as mp  # noqa: E402

NAME = "grid_stress_yearly"
SOURCE = "erw:grid_stress"
METHOD_URL = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/grid_stress.md"
SITE_DIR = os.path.join(ROOT, "site", "data", "stress")
OPERATING, RETIRED, FLEET = "eia860m_operating_generators", "eia860m_retired_generators", "storage_buildout_monthly"
FUELS = ["natural_gas", "coal", "nuclear", "wind", "solar", "hydro", "storage"]
ALL_YEARS = {"wind", "solar"}               # fuels whose installed capacity the inventory gives for every year (the docstring)
TOGETHER = ("hydro", "storage")              # set against installed capacity as one: grids do not report pumped storage under one name
FROM_YEAR = 2025                            # the first year the inventory's retirements reach back to
TIGHT = 100
CALM = 0.10
WINDOW = (14, 22)                           # the evening: steps between the local hours starting 14:00 and 22:00
NEAR = 0.9
COLS = ip.SERIES_COLS + ["x_at"]


def read(name, cols, in_dir=None):
    path = os.path.join(in_dir or ip.OUT_DIR, name + ".csv")
    return pd.read_csv(path, skiprows=ip.header_rows(path), usecols=cols, dtype=str, keep_default_na=False)


def capacity(in_dir=None):
    """Installed nameplate MW by balancing authority, fuel and month: {(ba, fuel): Series indexed by month "YYYY-MM"}.
    A unit counts from its first month of operation; a unit retired since January 2025 counts until the month before its
    retirement. A unit with no operating month is counted from the start."""
    cols = ["balancing_authority", "technology_group", "nameplate_mw", "operating_year", "operating_month"]
    op = read(OPERATING, cols, in_dir).assign(end="")
    rt = read(RETIRED, cols + ["status_date"], in_dir)
    rt = rt.assign(end=rt["status_date"].str[:7]).drop(columns="status_date")
    u = pd.concat([op, rt], ignore_index=True)
    u = u[u["balancing_authority"].isin({g["ba"] for g in mp.GRIDS.values()}) & u["technology_group"].isin(FUELS)]
    u["mw"] = pd.to_numeric(u["nameplate_mw"], errors="coerce")
    u = u[u["mw"] > 0]
    y, m = pd.to_numeric(u["operating_year"], errors="coerce"), pd.to_numeric(u["operating_month"], errors="coerce").fillna(1)
    u["start"] = [f"{int(a):04d}-{int(b):02d}" if a == a else "0000-00" for a, b in zip(y, m)]
    months = pd.period_range(mp.FIRST, pd.Timestamp.now(tz="UTC").strftime("%Y-%m"), freq="M").strftime("%Y-%m")
    out = {}
    for (ba, fuel), g in u.groupby(["balancing_authority", "technology_group"]):
        out[(ba, fuel)] = pd.Series([float(g.loc[(g["start"] <= mo) & ((g["end"] == "") | (g["end"] > mo)), "mw"].sum()) for mo in months], index=months)
    return out


def fleet(grid, in_dir=None):
    """The grid's operating batteries by month: (MW, MWh), each a Series by "YYYY-MM"."""
    d = read(FLEET, ["entity", "variable", "ts_utc", "value"], in_dir)
    d = d[d["entity"] == f"iso:{grid}"]
    pick = lambda v: pd.Series(pd.to_numeric(d[d["variable"] == v]["value"], errors="coerce").values, index=d[d["variable"] == v]["ts_utc"].str[:7].values)  # noqa: E731
    return pick("battery_operating_mw"), pick("battery_operating_mwh")


def stretches(below, index):
    """The runs of True in `below` (a boolean array over `index`, hourly timestamps): [(first position, length)]. A run
    is hours next to each other; a gap in the index ends it."""
    out, start = [], None
    for i, b in enumerate(below):
        joined = i > 0 and (index[i] - index[i - 1]) == pd.Timedelta(hours=1)
        if b and start is not None and not joined:
            out.append((start, i - start))
            start = i
        elif b and start is None:
            start = i
        elif not b and start is not None:
            out.append((start, i - start))
            start = None
    if start is not None:
        out.append((start, len(below) - start))
    return out


def evening_ramps(d, tz):
    """One row a local day: the largest one-hour rise of net load in the evening window and the hour it starts, and
    the largest three-hour rise and its start. d: held hours with `net`, indexed by UTC hour."""
    local = d.index.tz_convert(tz)
    s = pd.DataFrame({"net": d["net"].values, "day": local.strftime("%Y-%m-%d"), "hour": local.hour}, index=d.index)
    rows = []
    for k, col in ((1, "ramp1"), (3, "ramp3")):
        later = s["net"].reindex(s.index + pd.Timedelta(hours=k))
        rise = pd.Series(later.values - s["net"].values, index=s.index)
        if k == 3:  # every hour between must be held too
            for j in (1, 2):
                rise[s["net"].reindex(s.index + pd.Timedelta(hours=j)).isna().values] = np.nan
        if k == 1:
            # a rise the next hour takes back by more than half is a spike in the data, not a ramp (PJM, 1 December 2019:
            # demand 86,378, then 103,428, then 89,476)
            after = pd.Series(s["net"].reindex(s.index + pd.Timedelta(hours=2)).values - later.values, index=s.index)
            rise[(rise > 0) & (after < -0.5 * rise)] = np.nan
        ok = (s["hour"] >= WINDOW[0]) & (s["hour"] + k <= WINDOW[1]) & rise.notna()
        r = pd.DataFrame({"day": s["day"][ok], col: rise[ok]})
        best = r.loc[r.groupby("day")[col].idxmax()]
        rows.append(best.assign(**{col + "_at": best.index}).set_index("day"))
    return rows[0].join(rows[1], how="outer")


def grid_rows(grid, x, caps, fleet_mw, fleet_mwh, retrieved, log):
    g = mp.GRIDS[grid]
    ba, tz = g["ba"], g["tz"]
    base = dict(entity=f"iso:{grid}", freq="P1Y", geo=g["geo"], market="", node="", source=SOURCE, source_url=METHOD_URL, retrieved_at=retrieved, vintage="")
    d = x[x["held"] & x["demand"].notna()].copy()
    d["year"] = d.index.tz_convert(tz).year
    # two kinds of hour that are in the file and do not describe the grid (the docstring): they would be records
    eia = d["side"] == "eia930"
    tested = eia & d["interchange"].notna()
    closes = (d["demand"] - (d["net_generation"] - d["interchange"])).abs() <= mp.BALANCE * d["demand"]
    # an hour whose interchange is blank cannot be put to the balance (California: 2,208 hours of 2024). It is used when its
    # demand stands to its net generation as it does in the grid's hours that do close: inside the middle 99 percent of
    # their ratio. (California, 8 March 2025, interchange blank: demand 13,710 MW against net generation 25,095.)
    ratio = d["demand"] / d["net_generation"]
    ok_ratio = ratio[tested & closes]
    lo, hi = (ok_ratio.quantile(0.005), ok_ratio.quantile(0.995)) if len(ok_ratio) else (0.0, np.inf)
    unbalanced = (tested & ~closes) | (eia & ~tested & ~ratio.between(lo, hi))
    prev = d[["net_generation", "wind", "solar"]].shift(1)
    stale = (d.index.to_series().diff() == pd.Timedelta(hours=1)).values & (d[["net_generation", "wind", "solar"]].fillna(-1.0) == prev.fillna(-1.0)).all(axis=1).values \
        & (d["net_generation"] > 0).values
    log(f"  {grid}: of {len(d):,} held hours with a demand, {int(unbalanced.sum()):,} not used because EIA's own balance does not close (demand against net generation less "
        f"interchange, more than {mp.BALANCE:.0%} of demand apart; or, {int((eia & ~tested).sum()):,} hours with interchange blank, demand over net generation outside "
        f"{lo:.2f} to {hi:.2f}) and {int((stale & ~unbalanced.values).sum()):,} because the hour repeats the hour before to the MW")
    d = d[~unbalanced.values & ~stale].copy()
    # wind and solar, hour by hour. A source the file does not report in a year (blank or zero in every hour: New York's
    # solar) is no part of that year's net load or of its installed capacity here, and the page says so. In a year that
    # does report it, an hour in which it is blank is not used: taken as zero, a blank would be a jump in net load
    d["cap_ws"] = 0.0
    d["ws"] = 0.0
    reported, dropped = {}, 0
    keep = pd.Series(True, index=d.index)
    for k in ("wind", "solar"):
        for year, y in d.groupby("year"):
            if not (y[k].fillna(0.0) > 0).any():
                continue
            reported.setdefault(year, []).append(k)
            blank = y.index[y[k].isna()]
            keep[blank] = False
            dropped += len(blank)
            d.loc[y.index, "ws"] += y[k].clip(lower=0).fillna(0.0)
            if (ba, k) in caps:
                d.loc[y.index, "cap_ws"] += caps[(ba, k)].reindex(y["month"]).values
    d = d[keep].copy()
    if dropped:
        log(f"  {grid}: {dropped:,} held hours not used: wind or solar blank in a year that reports it")
    d["storage"] = d["storage"].fillna(0.0)
    d["net"] = d["demand"] - d["ws"]
    ramps = evening_ramps(d, tz)
    ramps["year"] = ramps.index.str[:4].astype(int)
    last = x.index.max()
    rows = []
    at = lambda t: pd.Timestamp(t).strftime("%Y-%m-%dT%H:%M:%SZ")  # noqa: E731

    def add(year, variable, value, unit, when=None):
        if value is None or (isinstance(value, float) and not np.isfinite(value)):
            return
        rows.append(dict(base, variable=variable, ts_utc=f"{year}-01-01T00:00:00Z", value=round(float(value), 3), unit=unit, x_at=at(when) if when is not None else ""))

    below = (d["ws"] < CALM * d["cap_ws"]) & (d["cap_ws"] > 0)
    runs = [(d.index[i], n, i) for i, n in stretches(below.values, d.index)]
    for year, y in d.groupby("year"):
        a = pd.Timestamp(f"{year}-01-01", tz=tz)
        b = min(pd.Timestamp(f"{year + 1}-01-01", tz=tz), last.tz_convert(tz) + pd.Timedelta(hours=1))
        due = int(round((b - a) / pd.Timedelta(hours=1)))
        if len(y) < NEAR * due:
            log(f"  {grid} {year}: {len(y):,} of {due:,} hours held with a demand: not written")
            continue
        add(year, "hours_held", len(y), "count")
        add(year, "wind_reported", 1 if "wind" in reported.get(year, []) else 0, "count")
        add(year, "solar_reported", 1 if "solar" in reported.get(year, []) else 0, "count")
        add(year, "hours_in_year", due, "count")
        add(year, "months_held", y["month"].nunique(), "count")
        peak = y["demand"].max()
        add(year, "peak_demand_mw", peak, "MW", y["demand"].idxmax())
        add(year, "net_load_peak_mw", y["net"].max(), "MW", y["net"].idxmax())
        r = ramps[ramps["year"] == year]
        if len(r):
            i1, i3 = r["ramp1"].idxmax(), r["ramp3"].idxmax()
            add(year, "evening_ramp_max_mw_per_h", r.loc[i1, "ramp1"], "MW", r.loc[i1, "ramp1_at"])
            add(year, "evening_ramp_median_mw_per_h", r["ramp1"].median(), "MW")
            add(year, "evening_ramp_max_share_of_peak_pct", 100.0 * r.loc[i1, "ramp1"] / peak, "pct")
            if r["ramp3"].notna().any():
                add(year, "evening_ramp_3h_max_mw", r.loc[i3, "ramp3"], "MW", r.loc[i3, "ramp3_at"])
                add(year, "evening_ramp_3h_max_share_of_peak_pct", 100.0 * r.loc[i3, "ramp3"] / peak, "pct")
        low = y["net"].idxmin()
        add(year, "net_load_min_mw", y.loc[low, "net"], "MW", low)
        add(year, "net_load_min_share_of_peak_pct", 100.0 * y.loc[low, "net"] / peak, "pct")
        add(year, "net_load_min_wind_solar_share_pct", 100.0 * y.loc[low, "ws"] / y.loc[low, "demand"], "pct")
        tight = y.nlargest(TIGHT, "net")
        add(year, "tight_net_load_mw", tight["net"].mean(), "MW")
        for fuel in FUELS:
            if not (y[fuel].fillna(0.0) > 0).any():
                continue  # the file does not report this source in this year: no figure, never a zero
            out = tight[fuel].clip(lower=0).fillna(0.0).mean()
            add(year, f"tight_{fuel}_mw", out, "MW")
            if fuel in TOGETHER or (ba, fuel) not in caps or (fuel not in ALL_YEARS and year < FROM_YEAR):
                continue
            cap = caps[(ba, fuel)].reindex(tight["month"]).values
            if not np.isfinite(cap).all() or (cap <= 0).any():
                continue
            add(year, f"capacity_{fuel}_mw", float(cap.mean()), "MW")
            add(year, f"tight_{fuel}_share_of_capacity_pct", 100.0 * float((tight[fuel].clip(lower=0).fillna(0.0).values / cap).mean()), "pct")
        # hydro and storage together (the docstring): one output, one capacity, from the year the inventory reaches
        both = sum(tight[k].clip(lower=0).fillna(0.0) for k in TOGETHER)
        if (both > 0).any():
            add(year, "tight_hydro_storage_mw", both.mean(), "MW")
            if year >= FROM_YEAR and all((ba, k) in caps for k in TOGETHER):
                cap = sum(caps[(ba, k)].reindex(tight["month"]).values for k in TOGETHER)
                if np.isfinite(cap).all() and (cap > 0).all():
                    add(year, "capacity_hydro_storage_mw", float(cap.mean()), "MW")
                    add(year, "tight_hydro_storage_share_of_capacity_pct", 100.0 * float((both.values / cap).mean()), "pct")
        mean_ws = y["ws"].mean()
        add(year, "wind_solar_mean_mw", mean_ws, "MW")
        add(year, "wind_solar_capacity_mw", y["cap_ws"].iloc[-1], "MW")
        mine = [(t, n, i) for t, n, i in runs if t.tz_convert(tz).year == year]
        add(year, "calm_hours", int(below[y.index].sum()), "count")
        add(year, "calm_stretches_ge24h", sum(1 for _, n, _ in mine if n >= 24), "count")
        if mine:
            t, n, i = max(mine, key=lambda r_: r_[1])
            part = d.iloc[i:i + n]
            missing = float((mean_ws - part["ws"]).sum())
            mo = part["month"].iloc[0]
            add(year, "calm_longest_hours", n, "hour", t)
            add(year, "calm_longest_missing_mwh", missing, "MWh")
            mw, mwh = fleet_mw.get(mo), fleet_mwh.get(mo)
            if mw and mw > 0:
                add(year, "calm_longest_fleet_mw", mw, "MW")
                add(year, "calm_longest_fleet_full_power_hours", missing / mw, "hour")
            if mwh and mwh > 0:
                add(year, "calm_longest_fleet_mwh", mwh, "MWh")
                add(year, "calm_longest_fleet_energy_multiples", missing / mwh, "ratio")
    log(f"  {grid}: {len(d):,} held hours with a demand; {len({r['ts_utc'] for r in rows})} years written; {len(runs):,} dark, calm stretches, {int(below.sum()):,} hours")
    return rows


def snapshot(table, retrieved):
    os.makedirs(SITE_DIR, exist_ok=True)
    for grid, g in mp.GRIDS.items():
        t = table[table["entity"] == f"iso:{grid}"]
        years = {}
        for r in t.itertuples():
            y = years.setdefault(r.ts_utc[:4], {})
            y[r.variable] = r.value
            if isinstance(r.x_at, str) and r.x_at:
                y[r.variable + "_at"] = r.x_at
        with open(os.path.join(SITE_DIR, f"{grid}.json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump(dict(grid=grid, name=g["name"], tz=g["tz"], built=retrieved, join=cj.JOIN if grid == "caiso" else None, fuels=FUELS + ["hydro_storage"], all_years=sorted(ALL_YEARS),
                           together=list(TOGETHER),
                           from_year=FROM_YEAR, tight=TIGHT, calm_pct=int(CALM * 100), window=list(WINDOW), years=dict(sorted(years.items()))), f, separators=(",", ":"))


def main(argv=None):
    ap = argparse.ArgumentParser(description="How hard the system works, by grid and year (session 123)")
    ap.add_argument("--out-dir", help="a trial run: the table and its log under this directory; nothing in warehouse/output")
    ap.add_argument("--snapshot", action="store_true", help="also write the site's own copy (site/data/stress/)")
    ap.add_argument("--snapshot-only", action="store_true", help="write the site's own copy from the table as it is (no table is written; no lock)")
    ap.add_argument("--grids", nargs="*", choices=sorted(mp.GRIDS))
    ap.add_argument("--hours-from", help="a directory of hours_<grid>.parquet (mix_profile.hours_of, saved): read in place of the workbooks (a trial)")
    a = ap.parse_args(argv)
    if a.snapshot_only:
        d = a.out_dir or ip.OUT_DIR
        p = os.path.join(d, f"{NAME}.csv")
        t = pd.read_csv(p, skiprows=ip.header_rows(p), dtype={"x_at": str}, keep_default_na=False, na_values=[])
        t["value"] = pd.to_numeric(t["value"])
        snapshot(t, t["retrieved_at"].max())
        print(f"the site's copy written from {d}: {t['entity'].nunique()} grids")
        return 0
    if a.out_dir:
        os.makedirs(a.out_dir, exist_ok=True)
    run_id = pd.Timestamp.now(tz="UTC").strftime("%Y%m%dT%H%M%SZ")
    retrieved = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
    log_dir = os.path.join(a.out_dir, "logs") if a.out_dir else ip.LOG_DIR
    os.makedirs(log_dir, exist_ok=True)
    log = ip.Log(os.path.join(log_dir, f"mix_stress_{run_id}.log"))
    caps = capacity()
    rows, paths = [], []
    for grid in (a.grids or mp.GRIDS):
        if a.hours_from:
            x = pd.read_parquet(os.path.join(a.hours_from, f"hours_{grid}.parquet"))
            path = open(os.path.join(a.hours_from, f"hours_{grid}.source.txt"), encoding="utf-8").read().strip()
        else:
            x, path = mp.hours_of(grid, log)
        paths.append(os.path.relpath(path, ROOT).replace("\\", "/"))
        mw, mwh = fleet(grid)
        rows += grid_rows(grid, x, caps, mw, mwh, retrieved, log)
    t = pd.DataFrame(rows)[COLS]
    if a.out_dir:
        ip.set_out_dir(a.out_dir)
    if not a.grids:
        path = os.path.join(ip.OUT_DIR, NAME + ".csv")
        if os.path.exists(path):  # rebuilt whole: a year that no longer passes must not stay from an earlier run
            ip._require_lock(path, f"rebuilding {NAME}")
            os.remove(path)
    ip.write_csv(t, NAME, [
        "Energy Research Warehouse (ERW): how hard each grid works, by year: the evening ramp of net load, the lowest net load, what each fuel gives in the 100 "
        "tightest hours as a share of its installed capacity, and the longest dark, calm stretch (derived, session 123)",
        "Shape: series (docs/datastandard.md v0). freq P1Y; ts_utc the local year's first day; entity iso:<grid>; x_at the hour (UTC, its start) a record or a "
        "stretch begins at. Variables and definitions: the header of warehouse/derived/mix_stress.py and docs/methods/grid_stress.md. Net load is demand less wind "
        f"less solar. The evening is the local hours starting {WINDOW[0]}:00 to {WINDOW[1]}:00. The tightest hours are the {TIGHT} of the year with the highest net load. "
        f"Dark and calm: wind and solar together under {CALM:.0%} of their installed capacity of that month.",
        f"Window: from {mp.FIRST}. A year is written when it holds at least {NEAR:.0%} of its hours to date; the newest year is not a whole one. Installed capacity: "
        f"EIA's generator inventory; for natural gas, coal, nuclear, and hydro and storage together, from {FROM_YEAR} only (units retired before then are not in the "
        "inventory read; hydro and storage are one line because grids do not report pumped storage under one name). "
        f"California from {cj.JOIN} is CAISO's own supply by fuel, with EIA's demand. Nothing is filled.",
        f"Retrieved: {run_id} (UTC) by warehouse/derived/mix_stress.py", f"Run log: warehouse/output/logs/mix_stress_{run_id}.log",
        f"Derived from: {OPERATING}; {RETIRED}; {FLEET}; caiso_fuel_supply",
        f"Source: {SOURCE} EIA Form EIA-930 hourly demand and net generation by energy source, the per-BA workbooks "
        f"(https://www.eia.gov/electricity/gridmonitor/knownissues/xls/<BA>.xlsx), read by this run from {'; '.join(paths)}; EIA-860M for installed capacity",
        "License: public",
    ], log, cols=COLS)
    ip.update_sources([dict(source=SOURCE, publisher="Energy Research Warehouse (ERW), derived",
                            report="How hard each grid works by year: evening ramp, lowest net load, fuels in the tightest hours, dark and calm stretches (docs/methods/grid_stress.md)",
                            report_url=METHOD_URL, document_list="docs/methods/grid_stress.md", license="public", tables=[NAME])])
    if a.snapshot:
        snapshot(t, retrieved)
    log.close()
    print(f"{NAME}: {len(t):,} rows, {t['entity'].nunique()} grids, {t['ts_utc'].nunique()} years"
          + ("; the site's copy written" if a.snapshot else "") + (f" (trial, under {a.out_dir})" if a.out_dir else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
