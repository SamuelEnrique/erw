#!/usr/bin/env python3
"""The hours behind "What a generator earns", as one CSV, for replication (session 183).

Energy Research Warehouse (ERW). The page /cost-of-power/seller shows months and spans; two builders decide hours: the
seller's model (warehouse/derived/merchant_revenue.py, whose months stand in site/data/merchant_snapshot.json) and the
capture price (warehouse/derived/capture_price.py, whose months stand in site/data/seller/capture.json). This script
writes the hours of the page's default case, one row an hour, so that a reader can rebuild every headline number of
the default page without either builder:

    site/public/seller/erw_2026_generator_hourly.csv

The default case is the page's own (site/lib/merchant.ts, inputsOf with no query): ERCOT, solar, 100 MW, priced at the
hub average HB_HUBAVG in real time. The file is per MW of installed nameplate, as the snapshot is; the page scales by
the reader's size. The window is the model's whole history for ERCOT: the local months of the snapshot from 2018-07,
ending with the snapshot's last hour. The column in_last_twelve marks the page's last twelve months.

Nothing is estimated and nothing is re-modelled. The hours are read by the two builders' own functions
(merchant_revenue.build_iso; capture_price.read_one, hourly_side and mix_hours), from the same tables and the same
EIA-930 workbook, and the script refuses to write unless, recomputed from the rows as they are written:

    (a) every month's revenue_per_mw, energy_per_mw and hours equal the snapshot's isos.ercot.months[m].solar, to the
        snapshot's four decimals (TOL_MODEL; the hours exactly), and the rule the do-file uses for the hours in a local
        month equals the snapshot's;
    (b) every month's record for HB_HUBAVG, real time, solar equals capture.json's, to its rounding (the hours
        exactly; TOL_CENT on the sums of prices and of price x generation; TOL_MWH on the generation);
    (c) every hour's price equals the snapshot's hourly price to its two decimals (TOL_PRICE), hour for hour;
    (d) the capture price's own price and generation equal the model's on every hour it uses, and the two last twelve
        months are the same months, so the file keeps one price column, one generation column and one flag.

If a month does not match because the tables moved since the two files were built, nothing is written and the months
and the differences are printed: neither file is rebuilt here, and no month is silently left out.

    python warehouse/derived/generator_hourly_export.py
    python warehouse/derived/generator_hourly_export.py --in-dir C:/.../warehouse/output --out C:/scratch/trial.csv
    python warehouse/derived/generator_hourly_export.py --cache-dir runs/session183/cache   # keep what is read

It writes nothing under warehouse/output, makes no request and needs no data lock: the inputs are read, the CSV is a
site file. The battery days and the gas peaker of the model are not computed (they play no part in solar): the model
is run with no battery duration and no gas price. Method: docs/methods/cost_of_power.md, "The seller's side" and
"The capture price".
"""

import argparse
import calendar
import datetime as dt
import hashlib
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, HERE)
import capture_price as cx  # noqa: E402  (the capture price's reader, its hourly rule and its hours of generation)
import eia930_emissions as em  # noqa: E402  (the workbook's address and retrieval time, from its extract)
import iso_prices as ip  # noqa: E402
import merchant_revenue as mr  # noqa: E402  (the seller's model)
import mix_profile as mp  # noqa: E402
import price_board as pb  # noqa: E402
import price_compare as pc  # noqa: E402

CSV_NAME = "erw_2026_generator_hourly.csv"
OUT = os.path.join(ROOT, "site", "public", "seller", CSV_NAME)
SNAPSHOT = os.path.join(ROOT, "site", "data", "merchant_snapshot.json")
CAPTURE = os.path.join(ROOT, "site", "data", "seller", "capture.json")
GRID, ASSET, SIDE, MARKET = "ercot", "solar", "rtm", "rt"   # the page's defaults (lib/merchant.ts inputsOf; page.tsx mk)
HUB = pb.MAIN[GRID]
ENTITY = f"{GRID}:{HUB}"
TZ = pb.TZ[GRID]
FIRST_MONTH = "2018-07"      # the model's generation by fuel begins on 2018-07-01 (merchant_revenue.SHAPE_START)
CAPTURE_FIRST = "2019-01"    # the capture price's hours of generation begin in January 2019, local time (mix_profile.FIRST)
HEADER_LINES = 16            # the do-file reads the column names from line 17
SENTINEL = -99999            # solar_mwh: EIA's value for the hour is blank
COLUMNS = ["hour_utc", "local_day", "local_month", "price_usd_mwh", "solar_mwh", "nameplate_mw", "in_last_twelve"]
TOL_MODEL = 0.00005 + 1e-7   # half a unit of the snapshot's fourth decimal, and the order of a sum (USD per MW; MWh per MW)
TOL_CENT = 0.005 + 1e-6      # half a cent: capture.json's sums of prices and of price x generation hold two decimals
TOL_MWH = 0.05 + 1e-6        # capture.json's generation holds one decimal
TOL_PRICE = 0.005 + 1e-9     # the snapshot's hourly price holds two decimals


def prev_month(m, k):
    """The month k months before m (YYYY-MM)."""
    y, mo = int(m[:4]), int(m[5:7]) - 1 - k
    return f"{y + mo // 12:04d}-{mo % 12 + 1:02d}"


def rule_hours_in_month(m):
    """The hours of a US local month, as the do-file computes them: 24 a day, one fewer in March (the clock goes
    forward), one more in November (it goes back). The export checks it against the snapshot's and capture.json's."""
    y, mo = int(m[:4]), int(m[5:7])
    return 24 * calendar.monthrange(y, mo)[1] - (mo == 3) + (mo == 11)


def model_held(rec, near):
    """The page's rule for a month of the model that counts (lib/merchant.ts, months): hours over the month's hours."""
    a = rec.get(ASSET)
    return bool(a) and a["hours"] / rec["him"] >= near - 1e-9


def model_last_twelve(months, near):
    """The page's last twelve months of the model (lib/seller2.ts, lastTwelve): the newest held month whose eleven
    months before it are all held; the twelve, oldest first, or None."""
    for m in sorted(months, reverse=True):
        if not model_held(months[m], near):
            continue
        twelve = [prev_month(m, k) for k in range(11, -1, -1)]
        if all(t in months and model_held(months[t], near) for t in twelve):
            return twelve
    return None


def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def sha_of(path):
    """The sha256 of a file's bytes with LF line ends."""
    with open(path, "rb") as f:
        return hashlib.sha256(f.read().replace(b"\r\n", b"\n")).hexdigest()


def header_value(path, start):
    """The first header comment of a table that begins with `start`, without the prefix; "" when there is none."""
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.startswith("#"):
                break
            if line[2:].startswith(start):
                return line[2 + len(start):].strip()
    return ""


def fmt(v, places):
    """A number as the CSV writes it: fixed places, trailing zeros dropped, never an exponent, never minus zero."""
    s = f"{v:.{places}f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def file_stamp(path):
    return f"{os.path.basename(os.path.dirname(path))}/{os.path.basename(path)}:{os.path.getsize(path)}:{os.stat(path).st_mtime_ns}"


def kept_fuel_hours(cache_dir, log):
    """merchant_revenue.fuel_hours, with what it reads from a workbook kept under cache_dir while the workbook is the
    same file."""
    real = mr.fuel_hours

    def read(path):
        kept = os.path.join(cache_dir, "generator_fuel_hours.pkl")
        stamp = file_stamp(path)
        if os.path.exists(kept):
            had = pd.read_pickle(kept)
            if had[0] == stamp:
                log(f"  the model's fuel hours read back from {kept}")
                return had[1]
        df = real(path)
        os.makedirs(cache_dir, exist_ok=True)
        pd.to_pickle((stamp, df), kept)
        return df
    return read


def read_model(in_dir, cache_dir, log):
    """The model's hours of ERCOT (merchant_revenue.build_iso's frame: p the hourly price, sun the fleet's MWh, sun_mw
    the installed nameplate of the month, month and day local), and what the header states. The battery days and the
    peaker are not computed: no duration, no gas price."""
    had = mr.DURATIONS, mr.fuel_hours
    mr.DURATIONS = []
    if cache_dir:
        mr.fuel_hours = kept_fuel_hours(cache_dir, log)
    try:
        gens, vintage = mr.read_gens()
        no_gas = pd.Series(dtype=float, index=pd.DatetimeIndex([]))
        h, _monthly, _bat, table, workbook, extract, over, neg = mr.build_iso(GRID, gens, no_gas, log, [])
    finally:
        mr.DURATIONS, mr.fuel_hours = had
    return h, dict(table=table, workbook=workbook.replace("\\", "/"), extract=os.path.join(mr.ROOT, extract), vintage=vintage, over=over, negative=neg)


def read_capture(in_dir, cache_dir, log):
    """The capture price's two series for the hub, as capture_price.main reads them: the hourly real-time price
    (read_one over every public price table held, then hourly_side) and the grid's hours of solar (mix_hours)."""
    lic, _ = pc.licenses()
    tables = cx.readable(in_dir, lic, log)
    stamp = ";".join(f"{t}:{os.path.getsize(os.path.join(in_dir, t + '.csv'))}:{os.stat(os.path.join(in_dir, t + '.csv')).st_mtime_ns}" for t in tables)
    kept = os.path.join(cache_dir, "generator_capture_price.pkl") if cache_dir else None
    got = None
    if kept and os.path.exists(kept):
        had = pd.read_pickle(kept)
        if had[0] == stamp:
            log(f"  the capture price's hourly price read back from {kept}")
            got = had[1:]
    if got is None:
        parts = []
        for i, t in enumerate(tables):
            x = cx.read_one(in_dir, t, log)
            if x is None:
                continue
            x = x[x["entity"].astype(str) == ENTITY].copy()
            x["rank"] = np.int8(i)   # a row held in two tables: the first of capture_price.TABLES
            if len(x):
                parts.append(x)
        if not parts:
            raise RuntimeError(f"no price row of {ENTITY} in the tables the capture price reads")
        price, basis, used = cx.hourly_side(pd.concat(parts, ignore_index=True), SIDE)
        got = (price, basis, used)
        if kept:
            os.makedirs(cache_dir, exist_ok=True)
            pd.to_pickle((stamp,) + got, kept)
    price, basis, used = got
    gen, workbook = cx.mix_hours(GRID, cache_dir, log)
    return price, gen[ASSET], dict(basis=basis, tables=used, workbook=workbook)


def page_facts():
    """What the page's two committed files hold for the default case: the snapshot's ERCOT months and hours, the capture
    file's months of the hub in real time, and each one's last twelve months by the page's rule. No table is read."""
    snap, capj = read_json(SNAPSHOT), read_json(CAPTURE)
    s = snap["isos"][GRID]
    near = snap["defaults"]["near"]
    hub = next(x for x in capj["grids"][GRID]["hubs"] if x["id"] == HUB)
    cap_months = hub[MARKET][ASSET]
    l12 = model_last_twelve(s["months"], near)
    c12 = cx.last_twelve(cap_months, capj["near"])
    if l12 is None or c12 is None:
        raise RuntimeError("the snapshot or capture.json holds no twelve consecutive months for the default case: nothing written")
    return dict(snap=snap, s=s, near=near, capj=capj, cap_months=cap_months, l12=l12, c12=c12)


def build(in_dir, cache_dir=None, log=print):
    """(rows, facts): the hourly rows of the window, and what the header and the checks state."""
    in_dir = os.path.abspath(in_dir)
    # the builders read ip.OUT_DIR, and the workbook beside the tables read; nothing is written there
    ip.OUT_DIR = in_dir
    ip.RAW_DIR = os.path.join(os.path.dirname(in_dir), "raw")
    mr.ROOT = os.path.dirname(os.path.dirname(in_dir))
    mp.RAW = os.path.join(ip.RAW_DIR, "eia930_emissions")
    facts = page_facts()
    s, l12 = facts["s"], facts["l12"]

    h, model = read_model(in_dir, cache_dir, log)
    cap_price, cap_gen, capture = read_capture(in_dir, cache_dir, log)
    last = pd.Timestamp(s["start"]) + pd.Timedelta(hours=len(s["price"]) - 1)
    inside = h.loc[:last]
    early = inside[inside["month"] < FIRST_MONTH]
    win = inside[inside["month"] >= FIRST_MONTH]
    rows = []
    for u, p, sun, mw, day, month in zip(win.index, win["p"].values, win["sun"].values, win["sun_mw"].values, win["day"].values, win["month"].values):
        rows.append(dict(hour_utc=u.strftime("%Y-%m-%dT%H:%M:%SZ"), local_day=day, local_month=month, price_usd_mwh=float(p),
                         solar_mwh=None if pd.isna(sun) else float(sun), nameplate_mw=float(mw), in_last_twelve=int(month in l12)))
    facts.update(model=model, capture=capture, last=last, early=len(early), early_solar=int(early["sun"].fillna(0).ne(0).sum()),
                 after=len(h) - len(inside), blank=sum(1 for r in rows if r["solar_mwh"] is None), win=win, cap_price=cap_price,
                 cap_gen=cap_gen, in_dir=in_dir, first_hour=rows[0]["hour_utc"] if rows else "")
    return rows, facts


def same_series(facts):
    """(d): the capture price's own price and generation beside the model's, hour for hour, and the two windows. The
    list of differences, and the number of hours the capture price uses in the window."""
    win, bad = facts["win"], []
    lo = pd.Timestamp(f"{CAPTURE_FIRST}-01", tz=TZ).tz_convert("UTC")
    d = pd.DataFrame({"p": facts["cap_price"]}).join(pd.DataFrame({"g": facts["cap_gen"]}), how="inner").dropna()   # month_sums' hours
    d = d[(d.index >= lo) & (d.index <= facts["last"])]
    mine = win[(win["month"] >= CAPTURE_FIRST) & win["sun"].notna()]
    for t in d.index.difference(mine.index)[:20]:
        bad.append(f"{ip.utc_iso(t)}: the capture price uses the hour, the model holds no generation or no price for it")
    for t in mine.index.difference(d.index)[:20]:
        bad.append(f"{ip.utc_iso(t)}: the model uses the hour, the capture price does not")
    both = d.join(mine[["p", "sun"]], how="inner", rsuffix="_model")
    for col, other, what in (("p", "p_model", "price"), ("g", "sun", "generation")):
        off = both[(both[col] - both[other]).abs() > 1e-9]
        for t, r in list(off.iterrows())[:20]:
            bad.append(f"{ip.utc_iso(t)}: the capture price's {what} is {r[col]}, the model's {r[other]}")
    if facts["l12"] != facts["c12"]:
        bad.append(f"the model's last twelve months are {facts['l12'][0]} to {facts['l12'][-1]}, the capture price's {facts['c12'][0]} to {facts['c12'][-1]}: "
                   "the file keeps one flag")
    return bad, len(d), int((d["g"] < 0).sum())


def render(rows):
    """The data lines of the CSV, as text."""
    out = []
    for r in rows:
        out.append(",".join([r["hour_utc"], r["local_day"], r["local_month"], fmt(r["price_usd_mwh"], 6),
                             str(SENTINEL) if r["solar_mwh"] is None else fmt(r["solar_mwh"], 4), fmt(r["nameplate_mw"], 4), str(r["in_last_twelve"])]))
    return out


def months_of_lines(lines):
    """Each local month recomputed from the CSV's own text: the model's sums (per MW), the capture price's sums, and
    the hours' prices by UTC hour. This is what a reader of the file has."""
    months, prices = {}, {}
    for line in lines:
        hour, _day, month, p, sun, mw, flag = line.split(",")
        p, sun, mw = float(p), float(sun), float(mw)
        prices[hour] = p
        m = months.setdefault(month, dict(rows=0, hours=0, revenue=0.0, energy=0.0, cap_n=0, cap_sp=0.0, cap_g=0.0, cap_pg=0.0, flags=set()))
        m["rows"] += 1
        m["flags"].add(flag)
        if sun == SENTINEL:
            continue
        if mw > 0:                                   # merchant_revenue: output per MW, where nameplate is installed
            m["hours"] += 1
            m["energy"] += sun / mw
            m["revenue"] += p * (sun / mw)
        if month >= CAPTURE_FIRST:                   # capture_price.month_sums: generation below zero weighs nothing
            w = max(0.0, sun)
            m["cap_n"] += 1
            m["cap_sp"] += p
            m["cap_g"] += w
            m["cap_pg"] += p * w
    return months, prices


def agree(lines, facts):
    """(a), (b), (c) and the flag, from the CSV's own text (its data lines) and page_facts(). The list of differences,
    empty when the file is the page's own data, hour by hour; and the months recomputed."""
    months, prices = months_of_lines(lines)
    s, bad = facts["s"], []
    first_hour = facts.get("first_hour") or (min(prices) if prices else "")
    # (a) the model's months
    for m in sorted(set(months) | {k for k, v in s["months"].items() if v.get(ASSET)}):
        want, got = s["months"].get(m, {}).get(ASSET), months.get(m)
        if want is None or got is None:
            if want is not None or (got and got["energy"] > 0):
                bad.append(f"model {m}: {'in the rows only' if want is None else 'in the snapshot only'}")
            continue
        if rule_hours_in_month(m) != s["months"][m]["him"]:
            bad.append(f"model {m}: the rule gives {rule_hours_in_month(m)} hours in the month, the snapshot holds {s['months'][m]['him']}")
        for k, v, tol in (("revenue_per_mw", got["revenue"], TOL_MODEL), ("energy_per_mw", got["energy"], TOL_MODEL), ("hours", got["hours"], 0)):
            if abs(v - want[k]) > tol:
                bad.append(f"model {m} {k}: the rows give {v:.6f}, the snapshot holds {want[k]} (difference {v - want[k]:+.6f})")
    # (b) the capture price's months
    cap = facts["cap_months"]
    for m in sorted({k for k, v in months.items() if v["cap_n"]} | set(cap)):
        want, got = cap.get(m), months.get(m)
        if want is None or got is None or not got["cap_n"]:
            bad.append(f"capture {m}: {'in the rows only' if want is None else 'in capture.json only'}")
            continue
        if rule_hours_in_month(m) != want[1]:
            bad.append(f"capture {m}: the rule gives {rule_hours_in_month(m)} hours in the month, capture.json holds {want[1]}")
        for k, v, w, tol in (("hours", got["cap_n"], want[0], 0), ("sum of prices", got["cap_sp"], want[2], TOL_CENT),
                             ("generation", got["cap_g"], want[3], TOL_MWH), ("sum of price x generation", got["cap_pg"], want[4], TOL_CENT)):
            if abs(v - w) > tol:
                bad.append(f"capture {m} {k}: the rows give {v:.6f}, capture.json holds {w} (difference {v - w:+.6f})")
    # (c) the hours and their prices
    start, n_bad = pd.Timestamp(s["start"]), 0
    seen = 0
    for i, v in enumerate(s["price"]):
        hour = (start + pd.Timedelta(hours=i)).strftime("%Y-%m-%dT%H:%M:%SZ")
        if hour < first_hour:
            continue
        got = prices.get(hour)
        if v is None and got is None:
            continue
        seen += got is not None
        if v is None or got is None or abs(got - v) > TOL_PRICE:
            n_bad += 1
            if n_bad <= 20:
                bad.append(f"hour {hour}: the row's price is {got}, the snapshot's {v}")
    if seen != len(prices):
        bad.append(f"{len(prices) - seen} rows lie outside the snapshot's hours")
    if n_bad > 20:
        bad.append(f"and {n_bad - 20} more hours whose price is not the snapshot's")
    # the flag marks the twelve months, whole
    flagged = sorted(m for m, v in months.items() if v["flags"] == {"1"})
    if flagged != facts["l12"] or any(len(v["flags"]) != 1 for v in months.values()):
        bad.append(f"in_last_twelve marks {flagged[:1]} to {flagged[-1:]}, the page's last twelve months are {facts['l12'][0]} to {facts['l12'][-1]}")
    return bad, months


def head_lines(rows, facts, months, n_capture, run_at):
    in_dir, s, capj, model, capture = facts["in_dir"], facts["s"], facts["capj"], facts["model"], facts["capture"]

    def got(t):
        return header_value(os.path.join(in_dir, t + ".csv"), "Retrieved: ").split(" (UTC)")[0] or "not stated"
    url, modified, retrieved = em.extract_meta(model["extract"])
    held = [m for m in sorted(months) if model_held(s["months"].get(m, {}), facts["near"])]
    counted = [m for m in sorted(facts["cap_months"]) if cx.counted(facts["cap_months"][m], capj["near"])]
    l12 = facts["l12"]
    price_tables = "; ".join(dict.fromkeys([pb.HISTORY, model["table"]] + list(capture["tables"])))
    head = [
        "Energy Research Warehouse (ERW): the hours behind What a generator earns; the default case of /cost-of-power/seller (session 183)",
        f"Case: ERCOT; solar; priced at the hub average {HUB} in real time; per 1 MW of installed nameplate (the page's default size is 100 MW). "
        "A fleet average: not a site",
        f"Window: local (Central) months {rows[0]['local_month']} to {rows[-1]['local_month']}; every hour of the model's snapshot from "
        f"{rows[0]['hour_utc']} to its last hour {rows[-1]['hour_utc']}. in_last_twelve = 1 marks {l12[0]} to {l12[-1]}: the last twelve months of "
        "the model and of the capture price alike (the same months; so one flag is kept)",
        f"Rows: one per hour that holds a real-time price; every hour of the window holds one ({len(rows)} rows). hour_utc is the hour's start; "
        f"local_day and local_month are the hour's day and month in {TZ}",
        "price_usd_mwh: the hour's real-time settlement point price in USD per MWh; the mean of its four 15-minute prices; held only when all four are",
        "solar_mwh: the solar generation of ERCOT's whole fleet in the hour in MWh (EIA-930; balancing authority ERCO; column Adjusted SUN Gen). "
        "nameplate_mw: the solar nameplate installed in ERCO at the start of the local month in MW (EIA-860M operating and retired generators; "
        f"vintage {' '.join(model['vintage'])})",
        f"Sentinel: {SENTINEL} in solar_mwh means EIA's value for the hour is blank ({facts['blank']} hours); such an hour is in no sum. "
        "No other column holds a sentinel",
        "The model (What a generator earns): output per MW = solar_mwh / nameplate_mw; a month's revenue per MW = the sum of price x output over "
        f"its hours with a value; a month is held when those hours are at least {facts['near']:.2f} of the hours in the local month",
        "The capture price: generation-weighted price = sum(price x generation) / sum(generation); flat average = sum(price) / hours; over the "
        f"hours with a value in the local months from {CAPTURE_FIRST}; a month counts at {capj['near']:.2f} of its hours. Its price and its "
        f"generation are these two columns: equal on every hour it uses ({n_capture} hours compared at export); so one column of each is kept",
        f"Source tables (ERW; warehouse/output): {price_tables}; eia860m_operating_generators; eia860m_retired_generators. "
        f"Workbook: {model['workbook']} from {url} (last modified {modified.replace(',', '')}; retrieved {retrieved})",
        "Retrieved (UTC) as each table's own header states: " + "; ".join(
            f"{t} {got(t)}" for t in (model["table"], pb.HISTORY, "eia860m_operating_generators", "eia860m_retired_generators")),
        f"Builders: warehouse/derived/merchant_revenue.py sha256 {sha_of(os.path.join(HERE, 'merchant_revenue.py'))}; "
        f"warehouse/derived/capture_price.py sha256 {sha_of(os.path.join(HERE, 'capture_price.py'))}. Every hour here is read by their own functions",
        f"Check at export; from these rows as written: each of {len(months)} months equals site/data/merchant_snapshot.json (built {facts['snap']['built']}; "
        f"sha256 {sha_of(SNAPSHOT)[:16]}) to within 0.00005 USD per MW and MWh per MW with the same hours ({len(held)} months held); each of "
        f"{len(facts['cap_months'])} months equals site/data/seller/capture.json (built {capj['built']}; sha256 {sha_of(CAPTURE)[:16]}) to within "
        f"0.005 USD and 0.05 MWh with the same hours ({len(counted)} months counted); each hour's price equals the snapshot's to 0.005",
        f"Exported: {run_at} (UTC) by warehouse/derived/generator_hourly_export.py. Method: "
        "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/cost_of_power.md",
        "License: public. Derived by the ERW from ERCOT's public prices (https://www.ercot.com/help/terms) and EIA's public data (EIA-930 and "
        "EIA-860M; public domain). Not a forecast; not what any plant earned: merchant sales at the hub price with no contract",
        f"Stata: import delimited using {CSV_NAME}; varnames({HEADER_LINES + 1}) rowrange({HEADER_LINES + 2}) stringcols(_all). "
        "These comment lines hold no comma and no double quote",
    ]
    if len(head) != HEADER_LINES:
        raise RuntimeError(f"the header holds {len(head)} lines, the do-file expects {HEADER_LINES}")
    for line in head:
        if "," in line or '"' in line or "\n" in line:
            raise RuntimeError(f"a header line holds a comma, a quote or a line break: {line[:80]}")
    return head


def write(head, lines, out):
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out + ".tmp", "w", encoding="utf-8", newline="\n") as f:
        for line in head:
            f.write("# " + line + "\n")
        f.write(",".join(COLUMNS) + "\n")
        for line in lines:
            f.write(line + "\n")
    os.replace(out + ".tmp", out)
    return os.path.getsize(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW: the hours behind What a generator earns for the page's default case, as one CSV")
    ap.add_argument("--in-dir", default=os.path.join(ROOT, "warehouse", "output"), help="read the tables from this directory (another copy's "
                    "warehouse/output; the EIA-930 workbook from the raw folder beside it); nothing is written there")
    ap.add_argument("--out", default=OUT, help="the CSV to write")
    ap.add_argument("--cache-dir", help="keep what is read from the workbook and the price tables under this folder, and read it back while "
                    "the files are the same")
    a = ap.parse_args(argv)
    in_dir = os.path.abspath(a.in_dir)
    need = [pb.TABLES[(GRID, SIDE)][0], pb.HISTORY, "eia860m_operating_generators", "eia860m_retired_generators"]
    missing = [t for t in need if not os.path.exists(os.path.join(in_dir, t + ".csv"))]
    if missing:
        print(f"generator_hourly_export SKIPPED: input tables not on this machine: {', '.join(missing)}")
        return 0
    run_at = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    rows, facts = build(in_dir, os.path.abspath(a.cache_dir) if a.cache_dir else None)
    if not rows:
        print("generator_hourly_export FAILED: the model holds no hour of the window; nothing written", file=sys.stderr)
        return 1
    for r in rows:
        if r["solar_mwh"] == SENTINEL or r["price_usd_mwh"] == SENTINEL:
            print(f"generator_hourly_export FAILED: a real value equals the sentinel at {r['hour_utc']}; nothing written", file=sys.stderr)
            return 1
    lines = render(rows)
    same, n_capture, n_negative = same_series(facts)
    bad, months = agree(lines, facts)
    if same or bad:
        print(f"generator_hourly_export FAILED: {len(same) + len(bad)} differences from the page's two files; nothing written. Neither file is "
              "rebuilt here: if the tables moved since they were built, these are the months and hours that moved", file=sys.stderr)
        for line in (same + bad)[:80]:
            print("  " + line, file=sys.stderr)
        return 1
    size = write(head_lines(rows, facts, months, n_capture, run_at), lines, os.path.abspath(a.out))
    print(f"{os.path.basename(a.out)}: rows={len(rows)} months={len(months)} bytes={size} window={rows[0]['hour_utc']}..{rows[-1]['hour_utc']} "
          f"last_twelve={facts['l12'][0]}..{facts['l12'][-1]} blank_solar_hours={facts['blank']} capture_hours={n_capture} "
          f"capture_hours_below_zero={n_negative} left_out_before_{FIRST_MONTH}={facts['early']} (with solar: {facts['early_solar']}) "
          f"hours_after_the_snapshot_not_written={facts['after']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
