#!/usr/bin/env python3
"""The price board, version 4: for every price held, its latest value, its moves and its place in its own year; and the
spreads an analyst reads (session 127).

Energy Research Warehouse (ERW). One derived table, price_board_stats, and the site's own copy of it for the review
page /board/v4. Method: docs/methods/price_board_v4.md.

    python warehouse/derived/price_board_v4.py                 # the table, under the data lock
    python warehouse/derived/price_board_v4.py --out-dir DIR   # a trial: the table under DIR
    python warehouse/derived/price_board_v4.py --snapshot      # also the site's copy (site/data/board_v4.json)

Inputs (no request is made): eia_fuel_spot_prices and eia_product_spot_prices (EIA's daily spot prices),
iso_hub_prices_history (the main hubs' day-ahead and real-time prices of CAISO, NYISO, SPP and ISO-NE) and
ercot_hub_prices_daily (ERCOT's hub prices by day). MISO's hub is in the history table and is not read: its prices are
paused (warehouse/metadata/paused_sources.csv) and no figure is made from them. PJM's are not held.

A PRICE is one daily series: a fuel's spot price by trading day, or a hub's day-ahead or real-time price as the mean
of a complete local operating day (a day short of an interval is not a day; nothing is filled). For each:

    last                 the newest day held, and its value
    change_1d            against the day held before it
    change_1w, _1m, _1y  against the newest day held at least 7, 30 and 365 days before the last, when that day is no
                         more than SLACK days older than that (else the move is not held, and no row is written)
    range_low_1y, range_high_1y, range_days_1y, range_position_1y
                         the lowest and highest value of the 365 days ending on the last day, how many days of them are
                         held, and where the last value sits between the two (0 the low, 1 the high); written when at
                         least RANGE_MIN days are held

THE SPREADS, each a daily series with the same figures:

    spark_spread_7   hub day-ahead daily mean - 7.0 MMBtu/MWh x Henry Hub (USD/MWh). The heat rate is a stated
                     assumption, about a combined-cycle gas plant. Henry Hub is in Louisiana and is not the gas a plant
                     in the grid burns: the spread is indicative. Gas of the operating day, else of the newest trading
                     day up to 4 days before it (the trader view's rule).
    da_minus_rt      hub day-ahead daily mean - real-time daily mean, on days both are held (USD/MWh)
    crack_321        (2 x U.S. Gulf Coast conventional regular gasoline + 1 x U.S. Gulf Coast ultra-low sulfur No. 2
                     diesel) x 42 / 3 - WTI at Cushing (USD/bbl), on days all three are held: what three barrels of
                     crude earn as two of gasoline and one of diesel, per barrel, before any cost

Variables are <measure>_<figure>: measure is spot, da, rt, spark_spread_7, da_minus_rt or crack_321.
"""

import argparse
import datetime as dt
import json
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, HERE)
import iso_prices as ip  # noqa: E402
import price_board as pb  # noqa: E402  (read_table, complete_days: the board's own reading of a complete day)

NAME = "price_board_stats"
SOURCE = "erw:price_board_v4"
METHOD_URL = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/price_board_v4.md"
SITE_FILE = os.path.join(ROOT, "site", "data", "board_v4.json")
HEAT_RATE = 7.0          # MMBtu/MWh, the stated assumption of the spark spread (the same as price_board.py's)
GAS_BACK = 4             # days: the newest gas trading day up to this many days before the operating day
SLACK = 6                # days: how much older than asked the day compared with may be
RANGE_MIN = 180          # days held of the 365 for a range to be written
HISTORY_DAYS = 800       # how far back the daily series are read (a year's move needs a little over two years of slack)
INPUTS = ["eia_fuel_spot_prices", "eia_product_spot_prices", "iso_hub_prices_history", "ercot_hub_prices_daily"]
# the grids whose hub prices are public and not paused: (grid, entity, the hub in words, time zone, geo, market stem)
GRIDS = [
    ("ERCOT", "ercot:HB_HUBAVG", "Hub average", "America/Chicago", "US-TX", "ercot"),
    ("CAISO", "caiso:TH_SP15_GEN-APND", "SP15", "America/Los_Angeles", "US-CA", "caiso"),
    ("NYISO", "nyiso:N.Y.C.", "New York City zone", "America/New_York", "US-NY", "nyiso"),
    ("SPP", "spp:SPPNORTH_HUB", "North hub", "America/Chicago", "", "spp"),
    ("ISO-NE", "isone:.H.INTERNAL_HUB", "Internal hub", "America/New_York", "", "isone"),
]
# EIA's daily spot series: entity: (group, label, where, unit, geo)
FUELS = {
    "eia:henry_hub": ("gas", "Natural gas", "Henry Hub, Louisiana", "USD/MMBtu", "US-LA"),
    "eia:wti_cushing": ("crude", "WTI crude oil", "Cushing, Oklahoma", "USD/bbl", "US-OK"),
    "eia:brent": ("crude", "Brent crude oil", "Europe, FOB", "USD/bbl", ""),
    "eia:EER_EPMRU_PF4_Y35NY_DPG": ("products", "Gasoline, conventional regular", "New York Harbor", "USD/gal", "US-NY"),
    "eia:EER_EPMRU_PF4_RGC_DPG": ("products", "Gasoline, conventional regular", "U.S. Gulf Coast", "USD/gal", ""),
    "eia:EER_EPMRR_PF4_Y05LA_DPG": ("products", "Gasoline, reformulated RBOB regular", "Los Angeles", "USD/gal", "US-CA"),
    "eia:EER_EPD2DXL0_PF4_Y35NY_DPG": ("products", "Diesel, ultra-low sulfur No. 2", "New York Harbor", "USD/gal", "US-NY"),
    "eia:EER_EPD2DXL0_PF4_RGC_DPG": ("products", "Diesel, ultra-low sulfur No. 2", "U.S. Gulf Coast", "USD/gal", ""),
    "eia:EER_EPD2DC_PF4_Y05LA_DPG": ("products", "Diesel, ultra-low sulfur CARB", "Los Angeles", "USD/gal", "US-CA"),
    "eia:EER_EPJK_PF4_RGC_DPG": ("products", "Jet fuel, kerosene-type", "U.S. Gulf Coast", "USD/gal", ""),
    "eia:EER_EPD2F_PF4_Y35NY_DPG": ("products", "Heating oil, No. 2", "New York Harbor", "USD/gal", "US-NY"),
    "eia:EER_EPLLPA_PF4_Y44MB_DPG": ("products", "Propane", "Mont Belvieu, Texas", "USD/gal", "US-TX"),
}
CRACK = ("eia:EER_EPMRU_PF4_RGC_DPG", "eia:EER_EPD2DXL0_PF4_RGC_DPG", "eia:wti_cushing")   # gasoline, diesel, crude
CRACK_ENTITY = "erw:crack_321_gulf_coast"
FORMULAS = {
    "spark_spread_7": f"day-ahead daily mean at the hub - {HEAT_RATE:g} MMBtu/MWh x Henry Hub",
    "da_minus_rt": "day-ahead daily mean - real-time daily mean, same day and hub",
    "crack_321": "(2 x Gulf Coast gasoline + 1 x Gulf Coast diesel) x 42 / 3 - WTI",
}


def day_of(ts_utc):
    return dt.date.fromisoformat(str(ts_utc)[:10])


def daily_from_series(df):
    """{date: value} of a table's daily rows of one entity and variable."""
    return {day_of(t): float(v) for t, v in zip(df["ts_utc"], df["value"])}


def stats(series):
    """The figures of one daily series, {date: value}. Returns None for an empty series, else a dict:
    last (date, value); moves {1d, 1w, 1m, 1y: (from date, from value, change) or None}; range (low, high, days,
    position) or None."""
    if not series:
        return None
    days = sorted(series)
    d0 = days[-1]
    v0 = series[d0]

    def back(n):
        """The newest day held at least n days before the last, no more than SLACK days older than that."""
        cands = [d for d in days if d0 - dt.timedelta(days=n + SLACK) <= d <= d0 - dt.timedelta(days=n)]
        return max(cands) if cands else None
    moves = {}
    prev = days[-2] if len(days) > 1 and (d0 - days[-2]).days <= 1 + SLACK else None
    for key, d in (("1d", prev), ("1w", back(7)), ("1m", back(30)), ("1y", back(365))):
        moves[key] = (d, series[d], v0 - series[d]) if d is not None else None
    window = [series[d] for d in days if d0 - dt.timedelta(days=365) < d <= d0]
    rng = None
    if len(window) >= RANGE_MIN:
        lo, hi = min(window), max(window)
        rng = (lo, hi, len(window), (v0 - lo) / (hi - lo) if hi > lo else None)
    return dict(last=(d0, v0), moves=moves, range=rng)


def spark(da, gas, heat_rate=HEAT_RATE):
    """{day: da - heat_rate x gas of the day, else of the newest gas day up to GAS_BACK days before it}."""
    gas_days = sorted(gas)
    out = {}
    for d, v in da.items():
        cands = [g for g in gas_days if d - dt.timedelta(days=GAS_BACK) <= g <= d]
        if cands:
            out[d] = v - heat_rate * gas[max(cands)]
    return out


def da_minus_rt(da, rt):
    return {d: da[d] - rt[d] for d in da if d in rt}


def crack_321(gasoline, diesel, crude):
    """USD/bbl on the days all three are held: (2 x gasoline + 1 x diesel) x 42 / 3 - crude, the products in USD/gal."""
    return {d: (2 * gasoline[d] + diesel[d]) * 42 / 3 - crude[d] for d in gasoline if d in diesel and d in crude}


def read_inputs(log):
    """Every daily series the board holds: {(entity, measure): {date: value}}."""
    since = (pd.Timestamp.now(tz="UTC").normalize() - pd.Timedelta(days=HISTORY_DAYS)).strftime("%Y-%m-%dT%H:%M:%SZ")
    out = {}
    for table in ("eia_fuel_spot_prices", "eia_product_spot_prices"):
        t = pb.read_table(table, since=since)
        for entity, g in t.groupby("entity"):
            if entity in FUELS:
                out[(entity, "spot")] = daily_from_series(g)
    e = pb.read_table("ercot_hub_prices_daily", node="HB_HUBAVG", since=since)
    for var, measure in (("da_mean", "da"), ("rt_mean", "rt")):
        out[("ercot:HB_HUBAVG", measure)] = daily_from_series(e[e["variable"] == var])
    for grid, entity, at, tz, geo, stem in GRIDS[1:]:
        for market, measure in ((f"{stem}_dam", "da"), (f"{stem}_rtm", "rt")):
            h = pb.read_table("iso_hub_prices_history", market=market, node=entity.split(":", 1)[1], since=since)
            days, _ = pb.complete_days(h, tz)
            out[(entity, measure)] = {d: float(v) for d, v in zip(days["day"], days["mean"])}
    for k, v in out.items():
        log(f"  {k[0]} {k[1]}: {len(v)} days, {min(v) if v else 'none'} to {max(v) if v else 'none'}")
    return out


def build(inputs):
    """The board's lines, in order: a list of dicts (group, key, entity, measure, label, at, unit, geo, market, stats,
    formula)."""
    lines = []
    gas = inputs.get(("eia:henry_hub", "spot"), {})
    for measure, group in (("da", "power_da"), ("rt", "power_rt")):
        for grid, entity, at, tz, geo, stem in GRIDS:
            lines.append(dict(group=group, entity=entity, measure=measure, label=grid, at=at, unit="USD/MWh", geo=geo,
                              market=f"{stem}_{'dam' if measure == 'da' else 'rtm'}", series=inputs.get((entity, measure), {})))
    for want in ("gas", "crude", "products"):
        for entity, (group, label, at, unit, geo) in FUELS.items():
            if group == want:
                lines.append(dict(group=group, entity=entity, measure="spot", label=label, at=at, unit=unit, geo=geo, market="", series=inputs.get((entity, "spot"), {})))
    for grid, entity, at, tz, geo, stem in GRIDS:
        lines.append(dict(group="spark", entity=entity, measure="spark_spread_7", label=grid, at=at, unit="USD/MWh", geo=geo, market=f"{stem}_dam",
                          series=spark(inputs.get((entity, "da"), {}), gas), formula=FORMULAS["spark_spread_7"]))
    for grid, entity, at, tz, geo, stem in GRIDS:
        lines.append(dict(group="da_rt", entity=entity, measure="da_minus_rt", label=grid, at=at, unit="USD/MWh", geo=geo, market=f"{stem}_dam",
                          series=da_minus_rt(inputs.get((entity, "da"), {}), inputs.get((entity, "rt"), {})), formula=FORMULAS["da_minus_rt"]))
    g, d, c = (inputs.get((e, "spot"), {}) for e in CRACK)
    lines.append(dict(group="crack", entity=CRACK_ENTITY, measure="crack_321", label="3-2-1 crack spread", at="U.S. Gulf Coast products, WTI at Cushing", unit="USD/bbl",
                      geo="", market="", series=crack_321(g, d, c), formula=FORMULAS["crack_321"]))
    for ln in lines:
        ln["stats"] = stats(ln["series"])
        ln["key"] = f"{ln['entity']}|{ln['measure']}"
    return lines


def rows_of(lines, retrieved):
    out = []
    ts = lambda d: d.isoformat() + "T00:00:00Z"   # noqa: E731
    for ln in lines:
        s = ln["stats"]
        if not s:
            continue
        d0, v0 = s["last"]
        base = dict(entity=ln["entity"], ts_utc=ts(d0), freq="P1D", geo=ln["geo"], market=ln["market"], node=ln["at"], source=SOURCE,
                    source_url=METHOD_URL, retrieved_at=retrieved, vintage="")
        m = ln["measure"]
        out.append(dict(base, variable=f"{m}_last", value=round(v0, 4), unit=ln["unit"], x_from=""))
        for key, mv in s["moves"].items():
            if mv:
                out.append(dict(base, variable=f"{m}_change_{key}", value=round(mv[2], 4), unit=ln["unit"], x_from=mv[0].isoformat()))
        if s["range"]:
            lo, hi, n, pos = s["range"]
            out.append(dict(base, variable=f"{m}_range_low_1y", value=round(lo, 4), unit=ln["unit"], x_from=""))
            out.append(dict(base, variable=f"{m}_range_high_1y", value=round(hi, 4), unit=ln["unit"], x_from=""))
            out.append(dict(base, variable=f"{m}_range_days_1y", value=n, unit="count", x_from=""))
            if pos is not None:
                out.append(dict(base, variable=f"{m}_range_position_1y", value=round(pos, 4), unit="ratio", x_from=""))
    return pd.DataFrame(out)


def site_copy(lines, built):
    def move(mv, v0):
        if not mv:
            return None
        d, v, ch = mv
        return dict(t=d.isoformat(), v=round(v, 4), change=round(ch, 4), pct=round(100 * ch / v, 2) if v > 0 else None)
    out = []
    for ln in lines:
        s = ln["stats"]
        row = dict(group=ln["group"], key=ln["key"], label=ln["label"], at=ln["at"], unit=ln["unit"], formula=ln.get("formula"), last=None, moves=None, range=None)
        if s:
            d0, v0 = s["last"]
            row["last"] = dict(t=d0.isoformat(), v=round(v0, 4))
            row["moves"] = {k: move(mv, v0) for k, mv in s["moves"].items()}
            if s["range"]:
                lo, hi, n, pos = s["range"]
                row["range"] = dict(low=round(lo, 4), high=round(hi, 4), days=n, position=None if pos is None else round(pos, 4))
        out.append(row)
    return dict(built=built, table=NAME, heat_rate=HEAT_RATE, slack_days=SLACK, range_min_days=RANGE_MIN, gas_back_days=GAS_BACK, lines=out)


def main(argv=None):
    ap = argparse.ArgumentParser(description="the price board, version 4")
    ap.add_argument("--out-dir")
    ap.add_argument("--snapshot", action="store_true", help="also write the site's copy, site/data/board_v4.json")
    args = ap.parse_args(argv)
    in_dir = ip.OUT_DIR
    if args.out_dir:
        ip.set_out_dir(args.out_dir)
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    retrieved = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
    log = ip.Log(os.path.join(ip.LOG_DIR, f"price_board_v4_{run_id}.log"))
    out_dir, ip.OUT_DIR = ip.OUT_DIR, in_dir       # the inputs are read where the warehouse keeps them
    try:
        inputs = read_inputs(log)
    finally:
        ip.OUT_DIR = out_dir
    lines = build(inputs)
    t = rows_of(lines, retrieved)
    cols = ip.SERIES_COLS + ["x_from"]
    held = [ln for ln in lines if ln["stats"]]
    header = [
        "Energy Research Warehouse (ERW): the price board, version 4: for every price held, its latest value, its moves over a day, a week, a month and a year, and its place in its own one-year range; and the spreads (session 127)",
        "Shape: series (docs/datastandard.md v0). Variables are <measure>_<figure>. Measures: spot (EIA's daily spot price), da and rt (the mean of a complete local operating day at a grid's main hub, day-ahead and real time), "
        f"spark_spread_7 (da - {HEAT_RATE:g} MMBtu/MWh x Henry Hub, indicative: Henry Hub is not local gas), da_minus_rt, crack_321 ((2 x Gulf Coast gasoline + 1 x Gulf Coast diesel) x 42 / 3 - WTI). "
        "Figures: last (ts_utc is its day); change_1d, change_1w, change_1m, change_1y (the last value less the value of x_from, the newest day held at least 1, 7, 30 and 365 days before, "
        f"no more than {SLACK} days older than that); range_low_1y, range_high_1y, range_days_1y, range_position_1y (0 the low, 1 the high; written when at least {RANGE_MIN} of the 365 days are held). node is the hub or place in words.",
        "A move or a range that is not held has no row. Nothing is filled. MISO's hub prices are paused and not read; PJM's are not held.",
        f"Retrieved: {run_id} (UTC) by warehouse/derived/price_board_v4.py",
        f"Run log: warehouse/output/logs/price_board_v4_{run_id}.log",
        f"Source: {SOURCE} ERW derived table, the price board, version 4 (docs/methods/price_board_v4.md), {METHOD_URL}",
        "Derived from: " + "; ".join(INPUTS),
        "License: public. A derived table inherits the most restrictive license of its inputs (Decision 23).",
        "Method: docs/methods/price_board_v4.md",
    ]
    path = os.path.join(ip.OUT_DIR, NAME + ".csv")
    if os.path.exists(path):
        os.remove(path)     # the board is the newest day's figures: an older day's rows leave the table
    ip.write_csv(t[cols], NAME, header, log, cols=cols)
    summary = site_copy(lines, retrieved)
    if args.snapshot:
        with open(SITE_FILE, "w", encoding="utf-8", newline="\n") as f:
            json.dump(summary, f, indent=1)
            f.write("\n")
        log(f"  the site's copy: {os.path.relpath(SITE_FILE, ROOT)}")
    else:
        with open(os.path.join(ip.OUT_DIR if args.out_dir else os.path.join(ROOT, "runs"), "board_v4_summary.json"), "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=1)
    if not args.out_dir:
        ip.update_sources([dict(source=SOURCE, publisher="Energy Research Warehouse (ERW)", report="ERW derived table, the price board, version 4 (docs/methods/price_board_v4.md)",
                                report_url=METHOD_URL, document_list="", license="public", tables=[NAME])])
        ip.write_status("price_board_v4", run_id, [dict(table=NAME, market="derived", status="ok", detail=f"{len(t)} rows, {len(held)} of {len(lines)} lines held")])
    print(f"{NAME}: {len(t):,} rows; {len(held)} of {len(lines)} lines held")
    log.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
