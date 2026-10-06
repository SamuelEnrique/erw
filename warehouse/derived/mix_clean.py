#!/usr/bin/env python3
"""How clean, and when: the carbon-free share of each grid's generation by hour, month and year, what an annual clean
purchase covers hour by hour, and what moving load into the cleanest hours changes (session 122).

Energy Research Warehouse (ERW). Method: docs/methods/clean_energy.md. Page: /mix/clean (in review). No request is made.

    python warehouse/derived/mix_clean.py                 # the two tables, under the data lock
    python warehouse/derived/mix_clean.py --out-dir DIR   # a trial run: the tables under DIR, nothing in warehouse/output
    python warehouse/derived/mix_clean.py --snapshot      # also the site's own copy (site/data/clean/)
    python warehouse/derived/mix_clean.py --snapshot-only # the site's copy from the tables as they are

WHAT THIS IS, AND IS NOT. It is the generation inside each grid: what its own plants put out, hour by hour. It is not
what the grid's customers used: power the grid imported is not in it, and power it exported is. And every carbon figure
is the average of the hour's generation (kg CO2 per MWh generated), not the marginal plant's: it does not say what one
more MWh of load would have emitted. Both are said wherever a figure stands.

The hours are the energy mix's (warehouse/derived/mix_profile.py hours_of, docs/methods/generation_mix_hourly.md): EIA-930's
hourly net generation by source for the seven ISO grids from January 2019; California from the join (caiso_join.JOIN) is
CAISO's own supply by fuel, and EIA's California hours of the months in which its file holds no hydro are not held
(a main source blank), so the hydro gap is in no figure; an impossible hour of demand is a blank by session 118's rule
(impossible_hours.screen), and here the same rule is put to the hour's net generation too: an hour it leaves out is not
held. So is an hour in which EIA's file has the grid's nuclear output under "other" (misnamed_nuclear below: New York,
3,281 hours from 2021): its carbon-free share cannot be told. An hour that is not held is used for nothing. A day is complete when every hour of the local day is held; a month
is written when at least 90 percent of its days are complete, over those days; a year when at most one of its months
(to the last month written) is missing. California's month of the join is not written. Nothing is filled.

Carbon-free: nuclear, wind, solar and hydro. Generation: those and natural gas, coal and "other" (oil, geothermal,
biomass and what EIA does not name). Storage is not a source: what a battery puts out was generated before, and is
counted there. Geothermal and biomass sit in "other" because EIA's file does not always name them, so "other" is
counted as not carbon-free: where a grid has geothermal (California) its carbon-free share is understated by it.

clean_energy_hourly (series, PT1H, entity iso:<grid>, ts_utc the hour's start): carbon_free_share_pct, with
x_carbon_free_mwh, x_generation_mwh and x_side (eia930 or caiso). Held hours only.

clean_energy_summary (series, entity iso:<grid>). By local month (freq P1M, ts_utc the month's first day at 00:00:00Z):
    carbon_free_share_pct          carbon-free MWh over generation MWh, the month's complete days
    carbon_free_share_flat_pct     the mean of the hours' shares: what a load that draws the same power every hour meets
    cf_share_pct_hHH               the average day: the share in local hour HH (carbon-free MWh over generation MWh of that hour of the days)
    cleanest_hour_1 .. _4          the four local hours of the average day with the highest share, cleanest first
    days_held, days_in_month
    own_data                       1 when the month rests on CAISO's own data (California from the join), else 0
    flat_kgco2_per_mwh, shift10_kgco2_per_mwh, shift20_kgco2_per_mwh         a flat load's carbon per MWh, as it is and with 10 and 20
    shift10_carbon_change_pct, shift20_carbon_change_pct, shift_days         percent of each day's energy moved into the four cleanest hours
    flat_cost_usd_per_mwh, shift10_cost_usd_per_mwh, shift20_cost_usd_per_mwh   the same at the grid's day-ahead hub price, where the
    shift10_cost_change_pct, shift20_cost_change_pct, cost_days                 warehouse holds one for every hour of the day
By local year (freq P1Y, ts_utc the year's first day), the same names with the prefix year_ (no average day), and:
    year_months, year_months_due, year_days_held, year_own_data_months (the months of the year on CAISO's own data)
    year_hours_cf_ge50_pct, _ge75_pct, _ge90_pct    the share of the year's held hours at or above that carbon-free share
    year_match_<shape>_<p>_energy_pct     a flat load buys clean energy equal to p percent of its year's use (p: 50, 100, 150), delivered in
    year_match_<shape>_<p>_hours_pct      the shape of the grid's own <shape> (mix: all its carbon-free generation; solar; wind): the share of
                                          the load's energy that is met in the hour it is used, and the share of hours met in full

The shift, exactly. A flat load of 1 MW. Each day, s percent of the day's energy is taken evenly from every hour and
put, in equal parts, into the hours of that day that are among the month's four cleanest hours of its average day (a
schedule fixed for the month, known only afterwards: this is what a load that knew the month's pattern could do, not a
forecast). The day's energy is unchanged. Carbon: each hour's load times carbon_intensity_hourly's intensity_generation
(California's hours before the join set back as caiso_join.true_hours sets them). Cost: each hour's load times the
day-ahead hub price (ERCOT: from 2019; California, New England, New York and SPP: from September 2024; PJM: no price
is held; MISO: its prices are not used while MISO is paused and its terms are under review, docs/methods/miso_pause.md).
A day counts only when every one of its hours has the figure.
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
import impossible_hours as ih  # noqa: E402
import iso_prices as ip  # noqa: E402
import mix_profile as mp  # noqa: E402

HOURLY = "clean_energy_hourly"
SUMMARY = "clean_energy_summary"
SOURCE = "erw:clean_energy"
METHOD_URL = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/clean_energy.md"
SITE_DIR = os.path.join(ROOT, "site", "data", "clean")
CLEAN = ["nuclear", "wind", "solar", "hydro"]
DIRTY = ["natural_gas", "coal", "other"]
GENERATION = CLEAN + DIRTY          # storage is not a source of energy
K = 4                               # the cleanest hours of the average day a load is moved into
SHIFTS = (10, 20)                   # percent of a day's energy moved
PURCHASES = (50, 100, 150)          # an annual clean purchase, percent of the load's annual energy
SHAPES = {"mix": CLEAN, "solar": ["solar"], "wind": ["wind"]}
LEVELS = (50, 75, 90)
NO_PRICE = {"pjm": "no hub price of PJM is held", "miso": "MISO's prices are not used while MISO is paused and its terms are under review"}
HCOLS = ip.SERIES_COLS + ["x_carbon_free_mwh", "x_generation_mwh", "x_side"]


def misnamed_nuclear(x):
    """EIA's hours in which a grid's nuclear output is in the file under "other": nuclear at nothing (under a quarter of
    its usual output) while "other" stands above its usual level by at least half of nuclear's usual output. "Usual" is
    the median over the hours in which nuclear runs. New York: 3,281 hours in 19 runs from 2021 (13 March to 1 May 2023:
    nuclear 12 MW on average against 2,671 in the same weeks of 2022, "other" 3,080 against 899). A reactor fleet that
    is truly off (SPP's two plants in October and November 2022, California's in October 2020) leaves "other" where it
    was and is kept. A boolean Series; all False where nuclear is not one of the grid's main sources."""
    eia = x["side"] == "eia930"
    on = eia & (x["nuclear"] > 0)
    gen = x.loc[eia, GENERATION].clip(lower=0).sum()
    if not on.any() or gen.sum() <= 0 or gen["nuclear"] / gen.sum() < mp.MAIN:
        return pd.Series(False, index=x.index)
    usual_nuclear, usual_other = x.loc[on, "nuclear"].median(), x.loc[on, "other"].median()
    return eia & (x["nuclear"].fillna(0) < 0.25 * usual_nuclear) & (x["other"] > usual_other + 0.5 * usual_nuclear)


def clean_hours(x, log=None, grid=""):
    """The hours with what this table needs: generation (the seven sources that are sources, each at zero when below it
    or blank within a held hour), carbon_free, share (percent). Not held: an hour whose net generation fails session
    118's rule, and an hour in which EIA's file has the grid's nuclear output under "other" (the share cannot be told).
    Returns a copy."""
    x = x.copy()
    ok = ih.screen(x["net_generation"]).notna() | (x["side"] == "caiso")   # CAISO's own hours hold all of its sources: the rule is for EIA's totals
    wrong = misnamed_nuclear(x)
    if log:
        log(f"  {grid}: {int((x['held'] & ~ok).sum()):,} held hours left out by the rule for impossible hours on net generation; "
            f"{int((x['held'] & wrong).sum()):,} left out because the file has nuclear's output under \"other\"")
    x["held"] = x["held"] & ok & ~wrong
    parts = x[GENERATION].clip(lower=0).fillna(0.0)
    x["generation"] = parts.sum(axis=1)
    x["carbon_free"] = parts[CLEAN].sum(axis=1)
    for name, cols in SHAPES.items():
        x[f"shape_{name}"] = parts[cols].sum(axis=1)
    x.loc[x["generation"] <= 0, "held"] = False
    x["share"] = 100.0 * x["carbon_free"] / x["generation"].where(x["generation"] > 0)
    return x


def complete_days(x, tz):
    """The local days every hour of which is held."""
    per = x.groupby("day").agg(n=("held", "size"), ok=("held", "sum"))
    return {d for d, r in per.iterrows() if r.n == r.ok and r.n == mp.expected_hours(d, tz)}


def intensity_of(grid):
    """kg CO2 per MWh generated, by the hour's start (UTC). California's hours before the join are EIA's, set back where
    EIA stamps them an hour late (caiso_join.true_hours, as session 118's rule reads them); from the join they are the
    table's own (CAISO's supply at EIA's factor for gas)."""
    ba = mp.GRIDS[grid]["ba"]
    s = mp.intensity_of(ba)
    s = s[~s.index.duplicated()].sort_index()
    if grid == "caiso":
        j = pd.Timestamp(cj.JOIN)
        before = cj.true_hours(s[s.index < j].to_frame("v"))["v"]
        s = pd.concat([before[before.index < j], s[s.index >= j]]).sort_index()
        s = s[~s.index.duplicated()]
        # session 133: the generation of the hydro gap's months is CAISO's own now (mix_profile.caiso_gap), but EIA's
        # intensity of those hours still divides by a total without hydro: no carbon figure rests on them
        s = s[~ih.in_hydro_gap(pd.Series(s.index))]
    return s


def prices_of(grid, log):
    """The grid's day-ahead hub price by hour (UTC hour start), or None with the reason."""
    if grid in NO_PRICE:
        return None, NO_PRICE[grid]
    import cost_of_power as cp
    try:
        p = cp.hourly(cp.prices_of(grid, "dam", log)[0])
    except Exception as exc:  # a grid with no price table
        return None, f"no day-ahead hub price could be read ({type(exc).__name__})"
    p.index = pd.to_datetime(p.index, utc=True)
    return p[~p.index.duplicated()].sort_index(), None


def shifted(day_hours, cleanest, s):
    """A flat load of 1 with s (a share) of the day's energy moved into the hours of the day that are among `cleanest`
    (local hours). day_hours: the local hour of each hour of the day. The sum is the number of hours, unchanged. None when
    the day holds none of those hours."""
    hours = np.asarray(day_hours)
    into = np.isin(hours, list(cleanest))
    if not into.any():
        return None
    load = np.full(len(hours), 1.0 - s)
    load[into] += s * len(hours) / into.sum()
    return load


def shift_figures(m, cleanest, value):
    """Over the days of m whose every hour has `value` (a column): the sum of value times load for the flat load and for
    each shift, the MWh of the flat load (one for each hour) and the days. {flat, shift10, shift20, energy, days}, or {}
    when no day qualifies."""
    tot = {"flat": 0.0, **{f"shift{p}": 0.0 for p in SHIFTS}}
    energy, days = 0.0, 0
    for _, d in m.groupby("day"):
        v = d[value].to_numpy(dtype=float)
        if np.isnan(v).any():
            continue
        loads = {p: shifted(d["hour"].to_numpy(), cleanest, p / 100.0) for p in SHIFTS}
        if any(x is None for x in loads.values()):
            continue
        tot["flat"] += v.sum()
        for p, load in loads.items():
            tot[f"shift{p}"] += float((load * v).sum())
        energy += len(v)
        days += 1
    if not days:
        return {}
    return {**tot, "energy": energy, "days": days}


def matching(y, shape, p):
    """A flat load of 1 over the hours of y buys clean energy equal to p percent of its use, delivered in the shape of
    the grid's own generation of `shape`: (share of the load's energy met in its own hour, share of hours met in full),
    percent; None when the shape generated nothing."""
    g = y[f"shape_{shape}"].to_numpy(dtype=float)
    if g.sum() <= 0:
        return None
    bought = g * (p / 100.0) * len(g) / g.sum()
    return 100.0 * np.minimum(bought, 1.0).sum() / len(g), 100.0 * float((bought >= 1.0 - 1e-12).mean())


def grid_rows(grid, x, ci, price, retrieved, log, join_month=None):
    """(hourly rows, summary rows, {month: its figures}) of one grid."""
    g = mp.GRIDS[grid]
    x = clean_hours(x, log, grid)
    x["ci"] = ci.reindex(x.index)
    x["price"] = price.reindex(x.index) if price is not None else np.nan
    good = complete_days(x, g["tz"])
    held = x[x["held"]]
    base = dict(entity=f"iso:{grid}", geo=g["geo"], market="", node="", source=SOURCE, source_url=METHOD_URL, retrieved_at=retrieved, vintage="")
    hourly = pd.DataFrame({"entity": f"iso:{grid}", "variable": "carbon_free_share_pct", "ts_utc": held.index.strftime("%Y-%m-%dT%H:%M:%SZ"),
                           "value": held["share"].round(3).values, "unit": "pct", "freq": "PT1H", "geo": g["geo"], "market": "", "node": "", "source": SOURCE,
                           "source_url": METHOD_URL, "retrieved_at": retrieved, "vintage": "", "x_carbon_free_mwh": held["carbon_free"].round(1).values,
                           "x_generation_mwh": held["generation"].round(1).values, "x_side": held["side"].values})
    rows, months = [], {}

    def add(variable, ts, value, unit, freq):
        if value is None or (isinstance(value, float) and not np.isfinite(value)):
            return
        rows.append(dict(base, variable=variable, ts_utc=ts, value=round(float(value), 4), unit=unit, freq=freq))

    def shift_rows(prefix, ts, freq, m, cleanest_of):
        """The carbon and the cost of the flat load and of its shifts over the days of m; cleanest_of(month) -> hours."""
        out = {}
        for value, name, unit, n in (("ci", "kgco2_per_mwh", "kgCO2/MWh", "shift_days"), ("price", "cost_usd_per_mwh", "USD/MWh", "cost_days")):
            tot, energy, days = {"flat": 0.0, **{f"shift{p}": 0.0 for p in SHIFTS}}, 0.0, 0
            for month, mm in m.groupby("month"):
                f = shift_figures(mm, cleanest_of(month), value)
                if not f:
                    continue
                for k in tot:
                    tot[k] += f[k]
                energy += f["energy"]
                days += f["days"]
            if not days:
                continue
            for k, t in tot.items():
                add(f"{prefix}{k}_{name}", ts, t / energy, unit, freq)
                out[f"{k}_{name}"] = t / energy
            for p in SHIFTS:
                if tot["flat"]:
                    kind = "carbon" if value == "ci" else "cost"
                    add(f"{prefix}shift{p}_{kind}_change_pct", ts, 100.0 * (tot[f"shift{p}"] - tot["flat"]) / abs(tot["flat"]), "pct", freq)
            add(f"{prefix}{n}", ts, days, "count", freq)
        return out

    per_day = x.groupby("day")["month"].first()
    cleanest = {}
    for month in sorted(set(per_day.values)):
        if month == join_month:
            continue  # a month is never built on both sources
        in_month = pd.Period(month).days_in_month
        days = [d for d in per_day.index[per_day == month] if d in good]
        if len(days) < mp.NEAR * in_month:
            continue
        m = x[(x["month"] == month) & x["day"].isin(days)]
        ts = f"{month}-01T00:00:00Z"
        by_hour = m.groupby("hour").agg(cf=("carbon_free", "sum"), gen=("generation", "sum"))
        day_share = (100.0 * by_hour["cf"] / by_hour["gen"]).reindex(range(24))
        if day_share.isna().any():
            continue
        top = [int(h) for h in day_share.sort_values(ascending=False, kind="stable").index[:K]]
        cleanest[month] = top
        add("carbon_free_share_pct", ts, 100.0 * m["carbon_free"].sum() / m["generation"].sum(), "pct", "P1M")
        add("carbon_free_share_flat_pct", ts, m["share"].mean(), "pct", "P1M")
        for h in range(24):
            add(f"cf_share_pct_h{h:02d}", ts, day_share[h], "pct", "P1M")
        for i, h in enumerate(top, 1):
            add(f"cleanest_hour_{i}", ts, h, "hour", "P1M")
        add("days_held", ts, len(days), "count", "P1M")
        add("days_in_month", ts, in_month, "count", "P1M")
        add("own_data", ts, 1 if m["side"].iloc[0] == "caiso" else 0, "count", "P1M")
        shift_rows("", ts, "P1M", m, lambda _m, top=top: top)
        months[month] = dict(days=days, side=m["side"].iloc[0])
    if not months:
        return hourly, rows, months
    upto = max(months)
    for year in sorted({m[:4] for m in months}):
        due = [f"{year}-{k:02d}" for k in range(1, 13) if f"{year}-{k:02d}" <= upto]
        have = [m for m in due if m in months]
        if len(due) - len(have) > 1:
            continue
        days = [d for m in have for d in months[m]["days"]]
        y = x[x["day"].isin(days)]
        ts = f"{year}-01-01T00:00:00Z"
        add("year_carbon_free_share_pct", ts, 100.0 * y["carbon_free"].sum() / y["generation"].sum(), "pct", "P1Y")
        add("year_carbon_free_share_flat_pct", ts, y["share"].mean(), "pct", "P1Y")
        add("year_months", ts, len(have), "count", "P1Y")
        add("year_months_due", ts, len(due), "count", "P1Y")
        add("year_days_held", ts, len(days), "count", "P1Y")
        add("year_own_data_months", ts, sum(1 for m in have if months[m]["side"] == "caiso"), "count", "P1Y")
        for level in LEVELS:
            add(f"year_hours_cf_ge{level}_pct", ts, 100.0 * float((y["share"] >= level).mean()), "pct", "P1Y")
        for shape in SHAPES:
            for p in PURCHASES:
                r = matching(y, shape, p)
                if r:
                    add(f"year_match_{shape}_{p}_energy_pct", ts, r[0], "pct", "P1Y")
                    add(f"year_match_{shape}_{p}_hours_pct", ts, r[1], "pct", "P1Y")
        shift_rows("year_", ts, "P1Y", y, lambda m: cleanest[m])
    log(f"  {grid}: {len(hourly):,} held hours written; {len(months)} months ({min(months)} to {max(months)}); "
        f"{sum(1 for r in rows if r['variable'] == 'year_carbon_free_share_pct')} years; carbon intensity for {int(x['ci'].notna().sum()):,} hours, "
        f"a price for {int(x['price'].notna().sum()):,}")
    return hourly, rows, months


def snapshot(summary, retrieved, notes):
    """The site's own copy: one file per grid, the months and the years as objects of their variables."""
    os.makedirs(SITE_DIR, exist_ok=True)
    for grid, g in mp.GRIDS.items():
        s = summary[summary["entity"] == f"iso:{grid}"]
        months, years = {}, {}
        for r in s.itertuples():
            if r.variable.startswith("year_"):
                years.setdefault(r.ts_utc[:4], {})[r.variable[5:]] = r.value
            elif r.variable.startswith("cf_share_pct_h"):
                months.setdefault(r.ts_utc[:7], {}).setdefault("day", [None] * 24)[int(r.variable[-2:])] = r.value
            else:
                months.setdefault(r.ts_utc[:7], {})[r.variable] = r.value
        with open(os.path.join(SITE_DIR, f"{grid}.json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump(dict(grid=grid, name=g["name"], tz=g["tz"], built=retrieved, join=cj.JOIN if grid == "caiso" else None, first=mp.FIRST,
                           upto=max(months) if months else None, clean=CLEAN, not_clean=DIRTY, k=K, shifts=list(SHIFTS), purchases=list(PURCHASES),
                           shapes=list(SHAPES), levels=list(LEVELS), no_price=notes.get(grid), months=dict(sorted(months.items())), years=dict(sorted(years.items()))),
                      f, separators=(",", ":"))


def main(argv=None):
    ap = argparse.ArgumentParser(description="How clean, and when: the carbon-free share by hour, month and year (session 122)")
    ap.add_argument("--out-dir", help="a trial run: the tables and their log under this directory; nothing in warehouse/output")
    ap.add_argument("--snapshot", action="store_true", help="also write the site's own copy (site/data/clean/)")
    ap.add_argument("--snapshot-only", action="store_true", help="write the site's own copy from the summary table as it is (no table is written; no lock)")
    ap.add_argument("--grids", nargs="*", choices=sorted(mp.GRIDS))
    ap.add_argument("--hours-from", help="a directory of hours_<grid>.parquet (mix_profile.hours_of, saved): read in place of the workbooks (a trial)")
    a = ap.parse_args(argv)
    notes = {}
    for grid in mp.GRIDS:
        if grid in NO_PRICE:
            notes[grid] = NO_PRICE[grid]
    if a.snapshot_only:
        d = a.out_dir or ip.OUT_DIR
        p = os.path.join(d, f"{SUMMARY}.csv")
        s = pd.read_csv(p, skiprows=ip.header_rows(p))
        snapshot(s, s["retrieved_at"].max(), notes)
        print(f"the site's copy written from {d}: {s['entity'].nunique()} grids")
        return 0
    if a.out_dir:
        os.makedirs(a.out_dir, exist_ok=True)
    run_id = pd.Timestamp.now(tz="UTC").strftime("%Y%m%dT%H%M%SZ")
    retrieved = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
    log_dir = os.path.join(a.out_dir, "logs") if a.out_dir else ip.LOG_DIR
    os.makedirs(log_dir, exist_ok=True)
    log = ip.Log(os.path.join(log_dir, f"mix_clean_{run_id}.log"))
    join_month = pd.Timestamp(cj.JOIN).tz_convert(mp.GRIDS["caiso"]["tz"]).strftime("%Y-%m")
    hourly, rows, paths = [], [], []
    for grid in (a.grids or mp.GRIDS):
        if a.hours_from:
            x = pd.read_parquet(os.path.join(a.hours_from, f"hours_{grid}.parquet"))
            path = open(os.path.join(a.hours_from, f"hours_{grid}.source.txt"), encoding="utf-8").read().strip()
        else:
            x, path = mp.hours_of(grid, log)
        paths.append(os.path.relpath(path, ROOT).replace("\\", "/"))
        price, why = prices_of(grid, log)
        if why:
            notes[grid] = why
            log(f"  {grid}: no cost figure: {why}")
        h, r, _ = grid_rows(grid, x, intensity_of(grid), price, retrieved, log, join_month if grid == "caiso" else None)
        hourly.append(h)
        rows += r
    h = pd.concat(hourly, ignore_index=True)[HCOLS]
    s = pd.DataFrame(rows)[ip.SERIES_COLS]
    if a.out_dir:
        ip.set_out_dir(a.out_dir)
    common = [f"Retrieved: {run_id} (UTC) by warehouse/derived/mix_clean.py", f"Run log: warehouse/output/logs/mix_clean_{run_id}.log",
              "Derived from: caiso_fuel_supply; carbon_intensity_hourly; ercot_all_hub_prices_history; iso_hub_prices_history; iso_dam_hub_prices",
              f"Source: {SOURCE} EIA Form EIA-930 hourly net generation by energy source, the per-BA workbooks "
              f"(https://www.eia.gov/electricity/gridmonitor/knownissues/xls/<BA>.xlsx); California from {cj.JOIN} is CAISO's own supply by fuel "
              f"(caiso_fuel_supply), the warehouse's one join (docs/methods/eia930_caiso_break.md); read by this run from {'; '.join(paths)}",
              "License: public"]
    what = ("WHAT IT IS: the generation inside each grid, not what its customers used (imports are not in it); every carbon figure is the average of the hour's "
            "generation, not the marginal plant's. Carbon-free: nuclear, wind, solar, hydro. Generation: those and natural gas, coal and other (oil, geothermal, "
            "biomass, unnamed: counted as not carbon-free). Storage is not a source.")
    if not a.grids:
        for name in (HOURLY, SUMMARY):  # rebuilt whole: a month that no longer passes the tests must not stay from an earlier run
            path = os.path.join(ip.OUT_DIR, name + ".csv")
            if os.path.exists(path):
                ip._require_lock(path, f"rebuilding {name}")
                os.remove(path)
    ip.write_csv(h, HOURLY, [
        "Energy Research Warehouse (ERW): the carbon-free share of each grid's generation by hour, the seven ISO grids (derived, session 122)",
        "Shape: series (docs/datastandard.md v0). freq PT1H; ts_utc the hour's start; entity iso:<grid>; variable carbon_free_share_pct (percent); "
        "x_carbon_free_mwh and x_generation_mwh the hour's two sums; x_side eia930 or caiso, the source of the hour. Held hours only "
        "(docs/methods/generation_mix_hourly.md, and session 118's rule on the hour's net generation, docs/methods/impossible_hours.md).",
        what, f"Window: from {mp.FIRST}. California's hours in which EIA's file holds no hydro (October 2019 to August 2020) are not held.",
    ] + common, log, cols=HCOLS)
    ip.write_csv(s, SUMMARY, [
        "Energy Research Warehouse (ERW): how clean each grid's generation is by month and year, what an annual clean purchase covers hour by hour, and what "
        "moving load into the cleanest hours changes (derived, session 122)",
        "Shape: series (docs/datastandard.md v0). entity iso:<grid>. Monthly rows (freq P1M, ts_utc the local month's first day): carbon_free_share_pct, "
        "carbon_free_share_flat_pct, cf_share_pct_hHH (the average day), cleanest_hour_1 to 4, days_held, days_in_month, flat_ and shift10_ and "
        "shift20_kgco2_per_mwh, shift10_ and shift20_carbon_change_pct, shift_days, the same for cost (_cost_usd_per_mwh, _cost_change_pct, cost_days). Yearly rows "
        "(freq P1Y, ts_utc the local year's first day): the same names with the prefix year_, and year_months, year_months_due, year_days_held, "
        "year_hours_cf_ge50_pct, _ge75_pct, _ge90_pct, year_match_<mix|solar|wind>_<50|100|150>_energy_pct and _hours_pct. Definitions: docs/methods/clean_energy.md.",
        what,
        f"Window: from {mp.FIRST}. A month is written when at least {mp.NEAR:.0%} of its days are complete, over those days; a year when at most one of its months is "
        f"missing; California's {join_month} is not written (the month of the join). The shift moves {SHIFTS[0]} and {SHIFTS[1]} percent of each day's energy into the "
        f"{K} cleanest hours of the month's average day. Cost at the day-ahead hub price: " + "; ".join(f"{g}: {w}" for g, w in sorted(notes.items())) + ".",
    ] + common, log)
    ip.update_sources([dict(source=SOURCE, publisher="Energy Research Warehouse (ERW), derived",
                            report="How clean each grid's generation is by hour, month and year; hourly against annual matching; load moved into the cleanest hours (docs/methods/clean_energy.md)",
                            report_url=METHOD_URL, document_list="docs/methods/clean_energy.md", license="public", tables=[HOURLY, SUMMARY])])
    if a.snapshot:
        snapshot(s, retrieved, notes)
    log.close()
    print(f"{HOURLY}: {len(h):,} rows; {SUMMARY}: {len(s):,} rows, {s['entity'].nunique()} grids"
          + ("; the site's copy written" if a.snapshot else "") + (f" (trial, under {a.out_dir})" if a.out_dir else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
