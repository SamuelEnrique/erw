#!/usr/bin/env python3
"""The hours behind the co-optimized hybrid and the reader's own profile on /cost-of-power/seller (session 162).

Energy Research Warehouse (ERW). No warehouse table is written and no request is made. This reads the public
day-ahead price tables the capture price reads (warehouse/derived/capture_price.py, TABLES) and the generation shapes
the seller's model uses (warehouse/derived/merchant_revenue.py: EIA-930's hourly generation by fuel over the fuel's
installed nameplate, EIA-860M), and writes two things for the site:

    site/data/seller/hybrid.json                 for ERCOT and CAISO (the grids the battery page's model is open
                                                 for): the main hub's hourly day-ahead price and the solar and wind
                                                 output per MW of nameplate over the last twelve months, the local
                                                 days, and this builder's own optimum (scipy's HiGHS) for a battery
                                                 of the plant's size, which the tests compare with the page's
    site/public/seller/prices/<grid>_<year>.json for each public grid's main hub: one calendar year of hourly
                                                 day-ahead prices in the grid's local standard time, which the
                                                 box "Your plant's profile" fetches before a profile is pasted

    python warehouse/derived/seller_hybrid.py --in-dir C:/.../warehouse/output   # the tables of another copy, read only
    python warehouse/derived/seller_hybrid.py --out-dir DIR                      # a trial run: both under DIR

The pair. A plant and a battery behind one interconnection, each local day on its own, the day-ahead prices of the day
known when the schedule is made (an upper bound for a schedule made the day before). Per hour t, with the plant's
output g (MWh, never below zero), the price p, the battery's power P and energy E = P x hours, the limit L:

    maximize   sum p x (g + discharge - charge)
    charge     0 to min(P, L + g): what the plant does not supply is bought, and the purchase stays inside the limit
    discharge  0 to min(P, L - g): the pair's export stays inside the limit; none in an hour whose price is below zero
    energy     the state of charge, sum(eta x charge - discharge / eta) with eta = sqrt(0.86), between 0 and E,
               each day from empty; at most one full cycle a day (sum discharge / eta <= E): the battery page's rules
    L          the plant's capacity, or its highest hour of the span when that is higher

The plant sells every hour at its price, as the seller's model does: the pair's revenue is the plant's plus what the
battery adds, and the battery idle is always allowed, so the pair never earns less than the plant alone. In an hour
at a price of zero or more, charging and discharging together never pays; a tie that left both is netted. The page's
own function is site/lib/sellerhybrid.ts (a simplex of its own); this file solves the same program with scipy, and
tests/test_session162.py holds the two to the same figure. Never filled: a local day is solved only when every hour of
its price and of the fuel's output is held; a month counts when at least 90 percent of its days are (the battery
page's rule); the twelve months are the newest counted month and the eleven before it.

Method: docs/methods/cost_of_power.md, "Session 162".
"""

import argparse
import glob
import json
import math
import os
import sys

import numpy as np
import pandas as pd
from scipy.optimize import linprog

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, HERE)
import capture_price as cz  # noqa: E402  (the price tables, their order, the public test, the grids' main hubs)
import iso_prices as ip  # noqa: E402
import price_compare as pc  # noqa: E402  (the day-ahead variables, the licenses)

SITE_FILE = os.path.join(ROOT, "site", "data", "seller", "hybrid.json")
PRICE_DIR = os.path.join(ROOT, "site", "public", "seller", "prices")
METHOD = "docs/methods/cost_of_power.md"
RTE = 0.86            # round trip, as the battery page states it (site/lib/batterystack.ts, RTE)
NEAR_DAYS = 0.9       # a month counts when at least this share of its days is solved (the battery page's rule)
NEAR_YEAR = 0.95      # a calendar year of prices is offered when at least this share of its hours is held
DURATIONS = (2, 4, 8)
FUELS = ("solar", "wind")
HYBRID = ("ercot", "caiso")   # the grids the battery page's model is open for
BA = {"ercot": "ERCO", "caiso": "CISO"}
SRC = {"solar": "SUN", "wind": "WND"}
STANDARD = {"ercot": -6, "caiso": -8, "nyiso": -5, "isone": -5, "spp": -6}   # local standard time, hours from UTC
TOL = 1e-7


def read_day_ahead(in_dir, tables, entities, log):
    """The day-ahead rows of the entities named, from the tables in their order: the first table that holds a row
    (price_compare's rule), read in pieces so that a history of several hundred MB never sits in memory."""
    parts = []
    for i, t in enumerate(tables):
        path = os.path.join(in_dir, f"{t}.csv")
        got = []
        for chunk in pd.read_csv(path, skiprows=ip.header_rows(path), usecols=["entity", "variable", "ts_utc", "value", "freq"], chunksize=500_000):
            chunk = chunk[chunk["entity"].isin(entities) & chunk["variable"].isin(pc.DAM_VARS) & (chunk["ts_utc"] >= cz.SINCE)]
            if len(chunk):
                got.append(chunk)
        n = sum(len(g) for g in got)
        log(f"  {t}: {n:,} day-ahead rows of the main hubs")
        if got:
            d = pd.concat(got)
            d["table"], d["rank"] = t, i
            parts.append(d)
    x = pd.concat(parts, ignore_index=True)
    x["ts"] = pd.to_datetime(x["ts_utc"], utc=True)
    x["side"] = "dam"
    return x.sort_values("rank").drop_duplicates(["entity", "freq", "ts"], keep="first")


def shapes(iso, raw_dir, in_dir, gens, mr, cj, log):
    """The fuel's output per MW of nameplate by hour (UTC), as the seller's model builds it."""
    found = sorted(glob.glob(os.path.join(raw_dir, "*", f"*_{BA[iso]}.xlsx")))
    if not found:
        raise RuntimeError(f"{iso}: no workbook of {BA[iso]} under {raw_dir}")
    wb = found[-1]
    fuel = mr.fuel_hours(wb)
    if iso == "caiso":
        fuel = cj.true_hours(fuel)  # session 82: EIA's California values of 2023-11 to 2025-12-02 sit one hour late
    tz = cz.GRIDS[iso]["tz"]
    month = fuel.index.tz_convert(tz).strftime("%Y-%m")
    out = pd.DataFrame(index=fuel.index)
    for f, col in (("solar", "sun"), ("wind", "wnd")):
        caps = {m: mr.capacity(gens, BA[iso], SRC[f], m) for m in sorted(set(month))}
        mw = pd.Series(month, index=fuel.index).map(caps)
        out[f] = np.where(mw > 0, fuel[col] / mw, np.nan)
        out[f] = out[f].clip(lower=0)  # an hour below zero (a plant's own use at night) is no output: the capture price's rule
    log(f"  {iso}: {len(out):,} hours of output per MW from {os.path.basename(wb)}")
    return out, os.path.basename(wb)


def day_bounds(p, g, power, energy, limit):
    """The bounds of one day's program: charge 0 to min(P, L + g), discharge 0 to min(P, L - g), none below a price of 0."""
    p, g = np.asarray(p, dtype=float), np.asarray(g, dtype=float)
    uc = np.minimum(power, limit + g)
    ud = np.where(p < 0, 0.0, np.minimum(power, np.maximum(0.0, limit - g)))
    return uc, ud


def solve_day(p, g, power, energy, limit, rte=RTE):
    """One day of the pair with scipy's HiGHS. Returns (the battery's net revenue, charge, discharge)."""
    T = len(p)
    p = np.asarray(p, dtype=float)
    if power <= 0 or energy <= 0:
        return 0.0, np.zeros(T), np.zeros(T)
    eta = math.sqrt(rte)
    uc, ud = day_bounds(p, g, power, energy, limit)
    rows, b = [], []
    for t in range(T):
        s = np.zeros(2 * T)
        s[:t + 1] = eta
        s[T:T + t + 1] = -1 / eta
        rows.append(s); b.append(energy)
        rows.append(-s); b.append(0.0)
    cyc = np.zeros(2 * T)
    cyc[T:] = 1 / eta
    rows.append(cyc); b.append(energy)
    res = linprog(np.concatenate([p, -p]), A_ub=np.array(rows), b_ub=np.array(b), bounds=list(zip(np.zeros(2 * T), np.concatenate([uc, ud]))), method="highs")
    if res.status != 0:
        raise RuntimeError(f"the linear program did not solve: {res.message}")
    c, d = res.x[:T].copy(), res.x[T:].copy()
    both = np.minimum(c, d / (eta * eta))
    both[p < 0] = 0
    c -= both
    d -= both * eta * eta
    return float(p @ (d - c)), c, d


def held_days(days, price, gen):
    """The local days whose every hour holds a price and the fuel's output: [(date, i0, T)]."""
    out = []
    for date, i0, T in days:
        if not (np.isnan(price[i0:i0 + T]).any() or np.isnan(gen[i0:i0 + T]).any()):
            out.append((date, i0, T))
    return out


def last_twelve(days, held):
    """The newest month with at least NEAR_DAYS of its days solved whose eleven months before it also count."""
    n_all, n_held = {}, {}
    for date, _, _ in days:
        n_all[date[:7]] = n_all.get(date[:7], 0) + 1
    for date, _, _ in held:
        n_held[date[:7]] = n_held.get(date[:7], 0) + 1
    def whole(m):
        y, k = int(m[:4]), int(m[5:7])
        return n_all.get(m, 0) == pd.Period(f"{y}-{k:02d}").days_in_month
    counted = {m for m in n_all if whole(m) and n_held.get(m, 0) >= NEAR_DAYS * n_all[m] - 1e-9}
    for m in sorted(counted, reverse=True):
        twelve = [(pd.Period(m) - k).strftime("%Y-%m") for k in range(11, -1, -1)]
        if all(t in counted for t in twelve):
            return twelve
    return None


def totals(days, price, gen, plant_mw, batt_mw, hours):
    """The sums of a span for a plant of plant_mw and a battery of batt_mw and `hours`: the plant alone, the pair, the
    battery alone (its own interconnection, no plant), and where the charging energy came from."""
    g_all = np.concatenate([gen[i0:i0 + T] for _, i0, T in days]) * plant_mw
    limit = max(plant_mw, float(g_all.max()))
    plant = pair_add = alone = from_plant = charged = discharged = energy = 0.0
    for _, i0, T in days:
        p, g = price[i0:i0 + T], gen[i0:i0 + T] * plant_mw
        plant += float(p @ g)
        energy += float(g.sum())
        v, c, d = solve_day(p, g, batt_mw, batt_mw * hours, limit)
        pair_add += v
        from_plant += float(np.minimum(c, g).sum())
        charged += float(c.sum())
        discharged += float(d.sum())
        alone += solve_day(p, np.zeros(T), batt_mw, batt_mw * hours, float("inf"))[0]
    return dict(plant=plant, pair=plant + pair_add, battery=alone, energy=energy, charged=charged, from_plant=from_plant, discharged=discharged, limit=limit)


def main(argv=None):
    ap = argparse.ArgumentParser(description="The hours behind the co-optimized hybrid and the reader's own profile")
    ap.add_argument("--in-dir", help="read the tables from this folder (another copy's warehouse/output); nothing is written there")
    ap.add_argument("--raw-dir", help="the folder of the EIA-930 workbooks (default: warehouse/raw/eia930_emissions beside the tables read)")
    ap.add_argument("--out-dir", help="a trial run: the files under this directory; nothing in site/")
    ap.add_argument("--log-dir", help="where the run's log goes (default: beside the output)")
    a = ap.parse_args(argv)
    in_dir = os.path.abspath(a.in_dir) if a.in_dir else ip.OUT_DIR
    raw_dir = os.path.abspath(a.raw_dir) if a.raw_dir else os.path.join(os.path.dirname(in_dir), "raw", "eia930_emissions")
    site_file = os.path.join(a.out_dir, "hybrid.json") if a.out_dir else SITE_FILE
    price_dir = os.path.join(a.out_dir, "prices") if a.out_dir else PRICE_DIR
    log_dir = a.log_dir or (os.path.join(a.out_dir, "logs") if a.out_dir else os.path.join(ROOT, "warehouse", "output", "logs"))
    for d in (os.path.dirname(site_file), price_dir, log_dir):
        os.makedirs(d, exist_ok=True)
    run_id = pd.Timestamp.now(tz="UTC").strftime("%Y%m%dT%H%M%SZ")
    built = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
    log = ip.Log(os.path.join(log_dir, f"seller_hybrid_{run_id}.log"))
    log(f"ERW seller hybrid run {run_id}: tables from {in_dir}, workbooks from {raw_dir}")
    ip.OUT_DIR = in_dir   # merchant_revenue's reader of EIA-860M takes the tables of ip.OUT_DIR
    import caiso_join as cj  # noqa: E402
    import merchant_revenue as mr  # noqa: E402

    lic, _ = pc.licenses()
    tables = cz.readable(in_dir, lic, log)
    grids = [g for g in cz.GRIDS if not ip.paused(g)]
    entities = {f"{g}:{cz.GRIDS[g]['main']}": g for g in grids}
    x = read_day_ahead(in_dir, tables, list(entities), log)
    hourly = {}
    for entity, g in entities.items():
        h, basis, tabs = cz.hourly_side(x[x["entity"] == entity], "dam")
        if h is None or h.empty:
            log(f"  {g}: no day-ahead price of {entity}")
            continue
        hourly[g] = (h.sort_index(), basis, tabs)
        log(f"  {g}: {len(h):,} hours of day-ahead price at {entity} ({basis}; {tabs}), {h.index.min()} to {h.index.max()}")

    out = {"built": built, "method": METHOD, "rte": RTE, "near_days": NEAR_DAYS, "near_year": NEAR_YEAR, "grids": {}, "years": {}}

    # the reader's profile: one calendar year of the main hub's day-ahead price, in local standard time
    for g, (h, basis, tabs) in hourly.items():
        off = STANDARD[g]
        out["years"][g] = []
        for year in range(h.index.min().year, h.index.max().year + 1):
            a0 = pd.Timestamp(f"{year}-01-01T00:00:00Z") - pd.Timedelta(hours=off)
            a1 = pd.Timestamp(f"{year + 1}-01-01T00:00:00Z") - pd.Timedelta(hours=off)
            grid = pd.date_range(a0, a1, freq="h", inclusive="left")
            v = h.reindex(grid)
            held = int(v.notna().sum())
            if held < NEAR_YEAR * len(grid):
                log(f"  {g} {year}: {held:,} of {len(grid):,} hours priced; under {NEAR_YEAR:.0%}, not offered")
                continue
            name = f"{g}_{year}.json"
            rec = dict(grid=g, name=cz.GRIDS[g]["name"], hub=cz.GRIDS[g]["main"], market="day-ahead", year=year, utc_offset_hours=off, first_utc=ip.utc_iso(a0),
                       hours=len(grid), held=held, tables=tabs, built=built, price=[None if pd.isna(p) else round(float(p), 2) for p in v.values])
            with open(os.path.join(price_dir, name), "w", encoding="utf-8", newline="\n") as f:
                json.dump(rec, f, separators=(",", ":"), allow_nan=False)
            out["years"][g].append(dict(year=year, hours=len(grid), held=held, file=name))
            log(f"  {g} {year}: {held:,} of {len(grid):,} hours priced; {name}")

    # the page's own plants: ERCOT and CAISO, the last twelve months
    gens, vint = mr.read_gens()
    for g in HYBRID:
        if g not in hourly:
            continue
        h, basis, tabs = hourly[g]
        shape, wb = shapes(g, raw_dir, in_dir, gens, mr, cj, log)
        tz = cz.GRIDS[g]["tz"]
        end = min(h.index.max(), shape.index.max())
        start = (end - pd.DateOffset(months=15)).floor("D")
        grid = pd.date_range(start, end, freq="h")
        price = np.array([np.nan if pd.isna(v) else round(float(v), 2) for v in h.reindex(grid).values])
        gen = {f: np.array([np.nan if pd.isna(v) else round(float(v), 5) for v in shape[f].reindex(grid).values]) for f in FUELS}
        local = grid.tz_convert(tz)
        date = np.array(local.strftime("%Y-%m-%d"))
        days = []
        for d in sorted(set(date)):
            ix = np.flatnonzero(date == d)
            need = len(cz_day_hours(d, tz))
            if len(ix) == need and ix[-1] - ix[0] + 1 == need:
                days.append((d, int(ix[0]), int(need)))
        rec = dict(name=cz.GRIDS[g]["name"], tz=tz, hub=cz.GRIDS[g]["main"], market="day-ahead", basis=basis, tables=tabs, workbook=wb, capacity="eia860m_operating_generators and eia860m_retired_generators (" + ", ".join(vint) + ")",
                   t0=ip.utc_iso(grid[0]), fuels={}, check=[])
        keep_from = None
        for f in FUELS:
            held = held_days(days, price, gen[f])
            twelve = last_twelve(days, held)
            if not twelve:
                log(f"  {g} {f}: no twelve months in a row with {NEAR_DAYS:.0%} of their days solved")
                continue
            span_all = [d for d in days if twelve[0] <= d[0][:7] <= twelve[-1]]
            span = [d for d in held if twelve[0] <= d[0][:7] <= twelve[-1]]
            peak = float(np.concatenate([gen[f][i0:i0 + T] for _, i0, T in span]).max())
            rec["fuels"][f] = dict(months=twelve, days=len(span), left_out=len(span_all) - len(span), peak=round(peak, 5))
            keep_from = span_all[0][1] if keep_from is None else min(keep_from, span_all[0][1])
            for hours in DURATIONS:
                for ratio in (1.0, 0.5):
                    t = totals(span, price, gen[f], 1.0, ratio, hours)
                    rec["check"].append(dict(fuel=f, hours=hours, battery_mw_per_plant_mw=ratio, **{k: round(v, 6) for k, v in t.items()}))
                    log(f"  {g} {f} {hours}h battery {ratio} MW per plant MW, {twelve[0]} to {twelve[-1]}, {len(span)} days ({len(span_all) - len(span)} left out): "
                        f"plant {t['plant']:,.0f}, battery alone {t['battery']:,.0f}, pair {t['pair']:,.0f}, added {t['plant'] + t['battery']:,.0f} USD per MW of plant; "
                        f"{100 * t['from_plant'] / t['charged'] if t['charged'] else 0:.1f} percent of the charging from the plant")
        if keep_from is None:
            continue
        # keep the hours from the first day of the earliest span, the index of each day moved with them
        rec["t0"] = ip.utc_iso(grid[keep_from])
        rec["days"] = [[d, i0 - keep_from, T] for d, i0, T in days if i0 >= keep_from]
        rec["price"] = [None if np.isnan(v) else float(v) for v in price[keep_from:]]
        for f in FUELS:
            rec[f] = [None if np.isnan(v) else float(v) for v in gen[f][keep_from:]]
        out["grids"][g] = rec
    with open(site_file, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, separators=(",", ":"), allow_nan=False)
    log(f"  written: {site_file} ({os.path.getsize(site_file):,} bytes)")
    log.close()
    print(f"seller hybrid: {len(out['grids'])} grids with a hybrid; price years: " + "; ".join(f"{g} {[y['year'] for y in ys]}" for g, ys in out["years"].items()) + f"; {site_file}")
    return 0


def cz_day_hours(day, tz):
    """The UTC hour starts of a local day (23, 24 or 25 of them), as warehouse/derived/battery_stack.py counts them."""
    a = pd.Timestamp(day).tz_localize(tz)
    b = (pd.Timestamp(day) + pd.Timedelta(days=1)).tz_localize(tz)
    return pd.date_range(a.tz_convert("UTC"), b.tz_convert("UTC"), freq="h", inclusive="left")


if __name__ == "__main__":
    sys.exit(main())
