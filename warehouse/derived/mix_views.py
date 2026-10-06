#!/usr/bin/env python3
"""The energy mix, the views session 133 added: availability by source, the factors beside the mix, forecast against
actual for wind and solar, and the long history by state.

Energy Research Warehouse (ERW). The one page /mix reads the site's own files; this builder writes the new ones from
tables already in warehouse/output (no request is made). Method: docs/methods/generation_mix_hourly.md, "Session 133".

    python warehouse/derived/mix_views.py                       # every file
    python warehouse/derived/mix_views.py --only forecast history   # some of them (plus, forecast, history)
    python warehouse/derived/mix_views.py --hours-to DIR        # also save each grid's hours (hours_<grid>.parquet), for
                                                                # mix_clean.py and mix_stress.py --hours-from DIR
    python warehouse/derived/mix_views.py --site-dir DIR        # a trial: the files under DIR

    site/data/mixplus/<grid>.json   capacity      installed nameplate MW by fuel and month (EIA-860M: the operating inventory and
                                                  every retired unit, eia860m_retired_generators_all), from 2019
                                    availability  each fuel's output as a share of its installed capacity, by local hour, for
                                                  each year and each season of it
                                    factors       what can be drawn beside the mix, by local hour, for each month and year:
                                                  hub price (day-ahead and real time), carbon intensity, net imports, temperature
                                    nuclear       the NRC's reactor status by year and season: the note on nuclear's row
    site/data/mix_forecast.json     wind and solar, forecast a day ahead against actual (CAISO, ERCOT), by hour and month
    site/data/mix_history.json      net generation by state, year and fuel since 2001 (EIA-923, state_generation_mix_monthly)

DEFINITIONS, AS COMPUTED. Local time is the grid's. The hours are the energy mix's (mix_profile.hours_of): only held
hours are used, and nothing is filled.

  availability    for a fuel, a year and a season: by local hour, the mean over the held hours of
                  (the fuel's output, not below zero) / (the fuel's installed nameplate MW that month), percent.
                  Seasons are by month within the calendar year: winter is January, February and December; spring
                  March to May; summer June to August; autumn September to November. Hydro and storage are set against
                  their capacity together (grids do not report pumped storage under one name). A fuel the grid does not
                  report in a year, or with no installed capacity, has no figure. A season needs MIN_SEASON_HOURS held
                  hours in each local hour.
  a factor        by local hour, the mean of the hours held in the month (at least MIN_MONTH_DAYS of them in every local
                  hour) or the year (at least MIN_YEAR_DAYS). price: the grid's main hub, day-ahead and real time (a
                  real-time hour is the mean of its intervals when all are held); MISO's prices are paused and PJM's are
                  not held, and neither is read. carbon: carbon_intensity_hourly's intensity of generation, kg CO2 per
                  MWh (California's hydro-gap hours left out). net imports: EIA's total interchange with its sign turned
                  (positive when the grid imports), MW. temperature: the mean of the NOAA stations held for the grid
                  (noaa_isd_hourly), degrees Fahrenheit; a station-hour is the mean of its observations in the hour.
  forecast error  forecast less actual, on the hours that hold both. By local hour and by month: the mean actual, the
                  mean forecast, the mean error (bias) and the mean absolute error, MW, and the number of hours.
                  CAISO: its day-ahead forecast, the three trading hubs added up (an hour needs all three).
                  ERCOT: its short-term forecast as it stood at least 24 hours before the hour.
  nuclear note    from the NRC's daily status: for the reactors EIA's inventory places in the grid, the mean power as a
                  percent of licensed power, and the reactors with the most days below 50 percent, by year and season.
                  A reactor is placed in a grid when its NRC name matches exactly one nuclear plant of EIA's inventory;
                  one that matches none is in no grid's note.
"""

import argparse
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
import caiso_join as cj  # noqa: E402
import impossible_hours  # noqa: E402
import iso_prices as ip  # noqa: E402
import mix_profile as mp  # noqa: E402
import mix_stress as ms  # noqa: E402  (capacity: installed nameplate MW by balancing authority, fuel and month)
import price_board as pb  # noqa: E402  (read_table)

SITE = os.path.join(ROOT, "site")
MIN_MONTH_DAYS, MIN_YEAR_DAYS, MIN_SEASON_HOURS = 20, 300, 60
SEASONS = {"winter": (1, 2, 12), "spring": (3, 4, 5), "summer": (6, 7, 8), "autumn": (9, 10, 11)}
AV_FUELS = ["natural_gas", "coal", "nuclear", "wind", "solar", "hydro_storage"]
TOGETHER = ("hydro", "storage")
CAP_FUELS = ["natural_gas", "coal", "nuclear", "wind", "solar", "hydro", "storage"]
HUB = {"ercot": "HB_HUBAVG", "caiso": "TH_SP15_GEN-APND", "nyiso": "N.Y.C.", "isone": ".H.INTERNAL_HUB", "spp": "SPPNORTH_HUB"}
NO_PRICE = {"miso": ("paused", "MISO's prices are paused while its terms are reviewed; none is read."),
            "pjm": ("licensed", "PJM publishes its prices under a license the ERW does not hold.")}
PER_HOUR = {"PT1H": 1, "PT15M": 4, "PT5M": 12}
NRC_ALIAS = {"d c cook": "donald c cook", "saint lucie": "st lucie", "fitzpatrick": "james a fitzpatrick", "ginna": "r e ginna", "summer": "v c summer",
             "river bend station": "river bend", "harris": "harris", "robinson": "h b robinson", "farley": "joseph m farley", "hatch": "edwin i hatch", "lasalle": "lasalle"}


# ---------------------------------------------------------------------------
# small helpers
# ---------------------------------------------------------------------------

def by_hour(s, tz, min_month=MIN_MONTH_DAYS, min_year=MIN_YEAR_DAYS, digits=2):
    """A UTC hourly Series as its average day: {"months": {"YYYY-MM": [24]}, "years": {"YYYY": [24]}}. A period is
    written only when every local hour of it holds at least the minimum number of values."""
    s = s.dropna()
    if s.empty:
        return {"months": {}, "years": {}}
    local = s.index.tz_convert(tz)
    d = pd.DataFrame({"v": s.values, "hour": local.hour, "month": local.strftime("%Y-%m"), "year": local.strftime("%Y")})
    out = {"months": {}, "years": {}}
    for key, col, need in (("months", "month", min_month), ("years", "year", min_year)):
        g = d.groupby([col, "hour"])["v"].agg(["mean", "size"])
        for period, part in g.groupby(level=0):
            part = part.droplevel(0)
            if len(part) == 24 and part["size"].min() >= need:
                out[key][period] = [round(float(v), digits) for v in part["mean"].reindex(range(24)).values]
    return out


def hub_hourly(grid, log):
    """{"da": Series, "rt": Series} of the grid's main hub by UTC hour, from the price tables held."""
    node, out = HUB[grid], {}
    tables = ["ercot_all_hub_prices_history", "iso_dam_hub_prices", "iso_rtm_hub_prices"] if grid == "ercot" else ["iso_hub_prices_history"]
    parts = {"da": [], "rt": []}
    for name in tables:
        if not os.path.exists(os.path.join(ip.OUT_DIR, name + ".csv")):
            continue
        for market, kind in ((f"{grid}_dam", "da"), (f"{grid}_rtm", "rt")):
            t = pb.read_table(name, market=market, node=node, since="2019-01-01T00:00:00Z")
            t = t[t["value"].notna()]
            if t.empty:
                continue
            g = t.assign(hour=t["ts"].dt.floor("h"), per=t["freq"].map(PER_HOUR)).groupby("hour").agg(v=("value", "mean"), n=("value", "size"), per=("per", "first"))
            parts[kind].append(g.loc[g["n"] == g["per"], "v"])
    for kind, ps in parts.items():
        if ps:
            s = pd.concat(ps)
            out[kind] = s[~s.index.duplicated(keep="last")].sort_index()
            log(f"  {grid} {kind} price: {len(out[kind]):,} hours, {out[kind].index.min():%Y-%m-%d} to {out[kind].index.max():%Y-%m-%d}")
    return out


def temperature(grid, log):
    """The grid's temperature by UTC hour: the mean of its NOAA stations, a station-hour the mean of its observations."""
    path = os.path.join(ip.OUT_DIR, "noaa_isd_hourly.csv")
    if not os.path.exists(path):
        return pd.Series(dtype=float)
    t = pd.read_csv(path, skiprows=ip.header_rows(path), usecols=["entity", "variable", "ts_utc", "value", "ba"], dtype={"ba": str})
    t = t[(t["ba"].str.lower() == mp.GRIDS[grid]["ba"].lower()) & (t["variable"] == "temperature_f") & t["value"].notna()]
    if t.empty:
        return pd.Series(dtype=float)
    hour = pd.to_datetime(t["ts_utc"], utc=True).dt.floor("h")
    by_station = t.assign(hour=hour).groupby(["entity", "hour"])["value"].mean()
    s = by_station.groupby(level=1).mean()
    log(f"  {grid} temperature: {t['entity'].nunique()} stations, {len(s):,} hours")
    return s


def carbon(grid):
    ci = mp.intensity_of(mp.GRIDS[grid]["ba"])
    if grid == "caiso":
        ci = ci[~impossible_hours.in_hydro_gap(pd.Series(ci.index))]
    return ci


# ---------------------------------------------------------------------------
# the per-grid file
# ---------------------------------------------------------------------------

def capacity_of(ba, caps):
    return {fuel: {m: round(float(v), 1) for m, v in caps[(ba, fuel)].items()} for fuel in CAP_FUELS if (ba, fuel) in caps}


def availability(grid, x, caps):
    """{year: {season|"all": {fuel: [24 percents]}}}: output as a share of installed capacity by local hour."""
    g = mp.GRIDS[grid]
    ba = g["ba"]
    d = x[x["held"]].copy()
    local = d.index.tz_convert(g["tz"])
    d["year"], d["mon"] = local.strftime("%Y"), local.month
    out = {}
    for fuel in AV_FUELS:
        parts = TOGETHER if fuel == "hydro_storage" else (fuel,)
        if not all((ba, k) in caps for k in parts):
            continue
        cap = sum(caps[(ba, k)].reindex(d["month"]).values for k in parts)
        mw = sum(d[k].clip(lower=0).fillna(0.0) for k in parts)
        share = pd.Series(np.where(cap > 0, 100.0 * mw.values / np.where(cap > 0, cap, np.nan), np.nan), index=d.index)
        for year, idx in d.groupby("year").groups.items():
            y = d.loc[idx]
            if not (sum(y[k].fillna(0.0).clip(lower=0) for k in parts) > 0).any():
                continue        # a source the grid's file does not report that year (New York's solar) has no figure
            for season, months in list(SEASONS.items()) + [("all", tuple(range(1, 13)))]:
                part = y[y["mon"].isin(months)]
                s = share.loc[part.index].dropna()
                if s.empty:
                    continue
                by = s.groupby(part.loc[s.index, "hour"]).agg(["mean", "size"])
                if len(by) == 24 and by["size"].min() >= (MIN_SEASON_HOURS if season != "all" else 4 * MIN_SEASON_HOURS):
                    out.setdefault(year, {}).setdefault(season, {})[fuel] = [round(float(v), 1) for v in by["mean"].reindex(range(24)).values]
    return out


def factors(grid, x, log):
    g = mp.GRIDS[grid]
    tz = g["tz"]
    held = x[x["held"]]
    out = {"net_imports": dict(unit="MW", **by_hour(-held["interchange"], tz, digits=0)),
           "carbon": dict(unit="kg CO2/MWh", **by_hour(carbon(grid), tz, digits=1)),
           "temperature": dict(unit="degrees F", **by_hour(temperature(grid, log), tz, digits=1))}
    if grid in NO_PRICE:
        status, note = NO_PRICE[grid]
        out["price_da"] = out["price_rt"] = dict(unit="USD/MWh", status=status, note=note, months={}, years={})
    else:
        hub = hub_hourly(grid, log)
        for kind in ("da", "rt"):
            out[f"price_{kind}"] = dict(unit="USD/MWh", hub=HUB[grid], **by_hour(hub.get(kind, pd.Series(dtype=float)), tz))
    return out


def extra_records(grid, x):
    """More records of the held hours, for the whole history ("all") and each local year: the hour with the lowest
    share of natural gas (among hours in which gas is above zero: a zero in the file is a missing value), the highest hour and the highest day of wind and of solar, the peak hour of demand, and the
    longest run of hours without coal. A day is ranked only when every hour of it is held; a run is of held hours next
    to each other in which coal's output is not above zero (a gap in the held hours ends it), and is given only for a
    grid whose file reports coal at all. {period: [{key, label, unit, value, at, kind}]}."""
    g = mp.GRIDS[grid]
    tz = g["tz"]
    d = x[x["held"]].copy()
    d["year"] = d.index.tz_convert(tz).strftime("%Y")
    v = d[mp.SOURCES].fillna(0.0)
    gross = v.clip(lower=0).sum(axis=1)
    d["gas_share"] = (100.0 * v["natural_gas"].clip(lower=0) / gross).where(gross > 0)
    per_day = d.groupby("day").agg(n=("held", "size"), wind=("wind", lambda c: c.fillna(0.0).clip(lower=0).sum()), solar=("solar", lambda c: c.fillna(0.0).clip(lower=0).sum()))
    per_day = per_day[[n == mp.expected_hours(day, tz) for day, n in per_day["n"].items()]]
    coal_reported = bool((v["coal"] > 0).any())
    out = {}

    def one(period, part, days):
        rows = []

        def add(key, label, unit, value, at, kind):
            rows.append(dict(key=key, label=label, unit=unit, value=round(float(value), 1), at=at, kind=kind))
        stamp = lambda t: t.strftime("%Y-%m-%dT%H:%M:%SZ")   # noqa: E731
        # an hour in which a gas-burning grid's file gives natural gas as exactly zero is a missing value, not a record
        s = part["gas_share"][v.loc[part.index, "natural_gas"] > 0].dropna()
        if len(s):
            add("gas_share_min", "Lowest share of natural gas in an hour", "pct", s.min(), stamp(s.idxmin()), "hour")
        for k, name in (("wind", "wind"), ("solar", "solar")):
            h = part[k].dropna()
            if len(h) and h.max() > 0:
                add(f"{k}_hour_max", f"Highest hour of {name}", "MW", h.max(), stamp(h.idxmax()), "hour")
            if len(days) and days[k].max() > 0:
                add(f"{k}_day_max", f"Highest day of {name}", "MWh", days[k].max(), str(days[k].idxmax()), "day")
        dem = part["demand"].dropna()
        if len(dem):
            add("demand_hour_max", "Peak hour of demand", "MW", dem.max(), stamp(dem.idxmax()), "hour")
        if coal_reported:
            runs = ms.stretches((~(part["coal"].fillna(0.0) > 0)).values, part.index)
            if runs:
                first, n = max(runs, key=lambda r: r[1])
                add("no_coal_run", "Longest run of hours without coal", "hours", n, stamp(part.index[first]), "run")
        out[period] = rows
    one("all", d, per_day)
    for year, part in d.groupby("year"):
        one(year, part, per_day[per_day.index.str[:4] == year])
    return out


def norm(name):
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]+", " ", name.lower())).strip()


def reactor_grids(log):
    """{NRC unit name: grid} for the reactors EIA's inventory places in one of the seven grids."""
    path = os.path.join(ip.OUT_DIR, "eia860m_operating_generators.csv")
    op = pd.read_csv(path, skiprows=ip.header_rows(path), usecols=["name", "balancing_authority", "technology_group"], dtype=str, keep_default_na=False)
    plants = op[op["technology_group"] == "nuclear"].drop_duplicates("name")
    plants = [(norm(n), ba) for n, ba in zip(plants["name"], plants["balancing_authority"])]
    by_ba = {g["ba"]: grid for grid, g in mp.GRIDS.items()}
    path = os.path.join(ip.OUT_DIR, "nrc_reactor_status.csv")
    units = pd.read_csv(path, skiprows=ip.header_rows(path), usecols=["node"], dtype=str)["node"].drop_duplicates()
    out, unmatched = {}, []
    for unit in units:
        base = norm(re.sub(r"\s*\d+$", "", unit))
        base = NRC_ALIAS.get(base, base)
        hits = {ba for n, ba in plants if re.search(rf"(^| ){re.escape(base)}( |$)", n)}
        if len(hits) == 1:
            ba = hits.pop()
            if ba in by_ba:
                out[unit] = by_ba[ba]
        else:
            unmatched.append(unit)
    log(f"  NRC reactors: {len(units)} units, {len(out)} placed in the seven grids, {len(unmatched)} matched to no single plant of EIA's inventory ({', '.join(sorted(unmatched)[:12])})")
    return out


def nuclear_notes(log):
    """{grid: {year: {season|"all": {units, mean_pct, days, low: [[unit, days below 50 percent]]}}}} from the NRC's daily status."""
    path = os.path.join(ip.OUT_DIR, "nrc_reactor_status.csv")
    if not os.path.exists(path):
        return {}
    grids = reactor_grids(log)
    t = pd.read_csv(path, skiprows=ip.header_rows(path), usecols=["node", "ts_utc", "value"])
    t = t[t["node"].isin(grids)].assign(grid=lambda d: d["node"].map(grids), year=lambda d: d["ts_utc"].str[:4], mon=lambda d: d["ts_utc"].str[5:7].astype(int))
    out = {}
    for (grid, year), y in t.groupby(["grid", "year"]):
        for season, months in list(SEASONS.items()) + [("all", tuple(range(1, 13)))]:
            part = y[y["mon"].isin(months)]
            if part.empty:
                continue
            low = part[part["value"] < 50].groupby("node").size().sort_values(ascending=False)
            out.setdefault(grid, {}).setdefault(year, {})[season] = dict(units=int(part["node"].nunique()), mean_pct=round(float(part["value"].mean()), 1),
                                                                         days=int(part["ts_utc"].nunique()), low=[[u, int(n)] for u, n in low.head(4).items()])
    return out


# ---------------------------------------------------------------------------
# forecast against actual
# ---------------------------------------------------------------------------

def error_tables(forecast, actual, tz):
    """The two UTC hourly Series on the hours both hold, as by-hour and by-month figures."""
    j = pd.DataFrame({"f": forecast, "a": actual}).dropna()
    if j.empty:
        return None
    local = j.index.tz_convert(tz)
    j["err"], j["hour"], j["month"] = j["f"] - j["a"], local.hour, local.strftime("%Y-%m")

    def figures(g):
        return dict(n=int(len(g)), actual=round(float(g["a"].mean()), 1), forecast=round(float(g["f"].mean()), 1), bias=round(float(g["err"].mean()), 1), mae=round(float(g["err"].abs().mean()), 1))
    months = {}
    for m, g in j.groupby("month"):
        row = figures(g)
        by = g.groupby("hour")["err"].agg(lambda e: float(e.abs().mean()))
        act = g.groupby("hour")["a"].mean()
        row["mae_by_hour"] = [None if h not in by.index else round(by[h], 1) for h in range(24)]
        row["actual_by_hour"] = [None if h not in act.index else round(float(act[h]), 1) for h in range(24)]
        months[m] = row
    return dict(first=j.index.min().strftime("%Y-%m-%dT%H:%M:%SZ"), last=j.index.max().strftime("%Y-%m-%dT%H:%M:%SZ"), all=figures(j),
                hours=[figures(j[j["hour"] == h]) if (j["hour"] == h).any() else None for h in range(24)], months=months)


def forecast_file(log):
    out = {}
    path = os.path.join(ip.OUT_DIR, "caiso_wind_solar_forecast.csv")
    if os.path.exists(path):
        t = pd.read_csv(path, skiprows=ip.header_rows(path), usecols=["entity", "variable", "ts_utc", "value"])
        t["ts"] = pd.to_datetime(t["ts_utc"], utc=True)
        w = t.pivot_table(index="ts", columns=["variable", "entity"], values="value")
        grid = dict(name="CAISO", tz="America/Los_Angeles", forecast="CAISO's day-ahead forecast", sources={})
        for src in ("wind", "solar"):
            f, a = w.get(f"{src}_forecast_dam_mw"), w.get(f"{src}_actual_mw")
            if f is None or a is None:
                continue
            # the system is the three trading hubs added up; an hour needs every hub that reports the source
            e = error_tables(f.dropna(how="any").sum(axis=1), a.dropna(how="any").sum(axis=1), grid["tz"])
            if e:
                grid["sources"][src] = e
                log(f"  forecast caiso {src}: {e['all']['n']:,} hours, {e['first'][:10]} to {e['last'][:10]}, bias {e['all']['bias']}, MAE {e['all']['mae']}")
        out["caiso"] = grid
    path = os.path.join(ip.OUT_DIR, "ercot_wind_solar_forecast.csv")
    if os.path.exists(path):
        t = pd.read_csv(path, skiprows=ip.header_rows(path), usecols=["variable", "ts_utc", "value"])
        w = t.assign(ts=pd.to_datetime(t["ts_utc"], utc=True)).pivot_table(index="ts", columns="variable", values="value")
        grid = dict(name="ERCOT", tz="America/Chicago", forecast="ERCOT's short-term forecast as it stood at least 24 hours before the hour", sources={})
        for src in ("wind", "solar"):
            if f"{src}_forecast_24h_mw" in w and f"{src}_actual_mw" in w:
                e = error_tables(w[f"{src}_forecast_24h_mw"], w[f"{src}_actual_mw"], grid["tz"])
                if e:
                    grid["sources"][src] = e
                    log(f"  forecast ercot {src}: {e['all']['n']:,} hours, {e['first'][:10]} to {e['last'][:10]}, bias {e['all']['bias']}, MAE {e['all']['mae']}")
        out["ercot"] = grid
    return out


# ---------------------------------------------------------------------------
# the long history by state
# ---------------------------------------------------------------------------

def history_file(log):
    """{state: {fuels: [...], years: {"YYYY": {fuel: MWh, months}}}} from state_generation_mix_monthly; a year is whole when it holds 12 months."""
    path = os.path.join(ip.OUT_DIR, "state_generation_mix_monthly.csv")
    t = pd.read_csv(path, skiprows=ip.header_rows(path), usecols=["entity", "variable", "ts_utc", "value"])
    t = t[t["variable"].str.startswith("net_generation_") & t["variable"].str.endswith("_mwh")]
    t["fuel"] = t["variable"].str[len("net_generation_"):-len("_mwh")]
    t["year"] = t["ts_utc"].str[:4]
    out = {}
    for state, s in t.groupby("entity"):
        months = s.groupby("year")["ts_utc"].nunique()
        tot = s.groupby(["year", "fuel"])["value"].sum().unstack()
        out[state.split(":", 1)[1]] = {y: dict(months=int(months[y]), **{f: round(float(v), 0) for f, v in row.items() if pd.notna(v)}) for y, row in tot.iterrows()}
    fuels = sorted(set(t["fuel"]))
    log(f"  history: {len(out)} states and areas, {t['year'].min()} to {t['year'].max()}, fuels {fuels}")
    return dict(fuels=fuels, first=t["year"].min(), last_month=t["ts_utc"].max()[:7], states=out)


def write(path, body):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(body, f, separators=(",", ":"))
        f.write("\n")


def main(argv=None):
    ap = argparse.ArgumentParser(description="the energy mix: the views session 133 added")
    ap.add_argument("--only", nargs="*", choices=["plus", "forecast", "history"])
    ap.add_argument("--grids", nargs="*", choices=sorted(mp.GRIDS))
    ap.add_argument("--hours-to", help="also save each grid's hours here (hours_<grid>.parquet and .source.txt)")
    ap.add_argument("--hours-from", help="read each grid's hours from this directory instead of the workbooks")
    ap.add_argument("--site-dir", default=SITE)
    a = ap.parse_args(argv)
    want = set(a.only or ["plus", "forecast", "history"])
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = pd.Timestamp.now(tz="UTC").strftime("%Y%m%dT%H%M%SZ")
    built = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
    log = ip.Log(os.path.join(ip.LOG_DIR, f"mix_views_{run_id}.log"))
    data = os.path.join(a.site_dir, "data")
    if "plus" in want:
        caps = ms.capacity()
        notes = nuclear_notes(log)
        for grid in (a.grids or mp.GRIDS):
            if a.hours_from:
                x = pd.read_parquet(os.path.join(a.hours_from, f"hours_{grid}.parquet"))
            else:
                x, path = mp.hours_of(grid, log)
                if a.hours_to:
                    os.makedirs(a.hours_to, exist_ok=True)
                    x.to_parquet(os.path.join(a.hours_to, f"hours_{grid}.parquet"))
                    with open(os.path.join(a.hours_to, f"hours_{grid}.source.txt"), "w", encoding="utf-8") as f:
                        f.write(path)
            g = mp.GRIDS[grid]
            body = dict(grid=grid, name=g["name"], tz=g["tz"], built=built, seasons={k: list(v) for k, v in SEASONS.items()}, av_fuels=AV_FUELS,
                        capacity=capacity_of(g["ba"], caps), availability=availability(grid, x, caps), factors=factors(grid, x, log), nuclear=notes.get(grid, {}), records=extra_records(grid, x))
            write(os.path.join(data, "mixplus", f"{grid}.json"), body)
            log(f"  {grid}: availability for {len(body['availability'])} years; factors: " + ", ".join(f"{k} {len(v['months'])} months" for k, v in body["factors"].items()))
    if "forecast" in want:
        write(os.path.join(data, "mix_forecast.json"), dict(built=built, grids=forecast_file(log)))
    if "history" in want:
        write(os.path.join(data, "mix_history.json"), dict(built=built, **history_file(log)))
    print(f"mix_views: wrote {', '.join(sorted(want))} under {os.path.relpath(data, ROOT)}")
    log.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
