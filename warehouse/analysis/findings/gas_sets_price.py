"""Finding: "Gas sets the price less often?" (session 170).

The share of hours each year, 2019 to 2026, in which the real-time hub price was below a gas plant's fuel cost (heat
rate times Henry Hub, 7.0 MMBtu per MWh, with 6.5 and 8.0 as a sensitivity), for ERCOT, CAISO, NYISO, ISO-NE and SPP.
MISO is paused and PJM licensed: their placeholders. A grid whose history the warehouse does not hold for a year
shows "not held" for that year, never a filled number.

Tables: ercot_all_hub_prices_history and iso_rtm_hub_prices (ERCOT 15-minute, the hub; CAISO and SPP 15-minute means
from 2026-08-26 only), nyiso_rtm_zone_prices (15-minute means from 2026-08-26 only), isone_zone_prices_history (hourly,
the eight load zones, 2019 to 2026-08; an internal table: the shares are aggregates and the hours are not published),
eia_fuel_spot_prices (Henry Hub daily spot, monthly mean).
"""

import os

import numpy as np
import pandas as pd

from findings_common import METHOD_URL, NoData, callout, do_destring, do_file, do_sentinels, fmt, now_iso, read_table, to_utc

NAME = "gas_sets_price"
TITLE = "GAS SETS THE PRICE LESS OFTEN?"
KIND = "visual"
HEAT_RATES = [6.5, 7.0, 8.0]
INPUTS = {
    "heat_rate": {"label": "Heat rate (MMBtu per MWh)", "default": 7.0, "choices": HEAT_RATES},
    "first_year": {"label": "First year", "default": 2019, "choices": [2019, 2020, 2021]},
}
TABLES = ["ercot_all_hub_prices_history", "iso_rtm_hub_prices", "nyiso_rtm_zone_prices", "isone_zone_prices_history", "eia_fuel_spot_prices"]
CSV_NAME = "erw_2026_gas_share_hours.csv"
GRIDS = [
    # grid, words, timezone, how the hourly price is made
    ("ercot", "ERCOT", "America/Chicago", "HB_HUBAVG, the mean of the four 15-minute settlement point prices in the local hour"),
    ("caiso", "CAISO", "America/Los_Angeles", "TH_SP15_GEN-APND, the mean of the four 15-minute interval means in the local hour"),
    ("nyiso", "NYISO", "America/New_York", "the simple mean of the eleven zones' 15-minute means in the local hour"),
    ("isone", "ISO-NE", "America/New_York", "the simple mean of the eight load zones' hourly real-time LMP"),
    ("spp", "SPP", "America/Chicago", "SPPSOUTH_HUB, the mean of the four 15-minute interval means in the local hour"),
]
PLACEHOLDERS = [{"grid": "miso", "words": "MISO", "text": "paused while terms are reviewed"},
                {"grid": "pjm", "words": "PJM", "text": "licensed source needed"}]


def henry_hub_monthly(in_dir):
    g = read_table("eia_fuel_spot_prices", in_dir, usecols=["entity", "variable", "ts_utc", "value"],
                   keep=lambda c: (c["entity"] == "eia:henry_hub") & (c["variable"] == "spot_price") & (c["ts_utc"] >= "2019-01-01"))
    if g.empty:
        raise NoData("eia_fuel_spot_prices has no Henry Hub rows from 2019")
    g["value"] = g["value"].astype(float)
    g["month"] = g["ts_utc"].str[:7]
    return g.groupby("month")["value"].mean().to_dict()


def hourly(d, tz):
    """15-minute (or hourly) rows -> one mean price per local hour, with the local year and month."""
    d = d.copy()
    d["value"] = d["value"].astype(float)
    d["hour_utc"] = to_utc(d["ts_utc"]).dt.floor("h")  # floored in UTC (every grid here is a whole-hour offset), then local
    h = d.groupby("hour_utc", as_index=False)["value"].mean()
    h["hour"] = h["hour_utc"].dt.tz_convert(tz)
    h["year"] = h["hour"].dt.year
    h["month"] = h["hour"].dt.strftime("%Y-%m")
    return h


def grid_hours(grid, first_year, in_dir):
    """The grid's hourly real-time price rows the warehouse holds from first_year, and the span they cover."""
    if grid == "ercot":
        h = read_table("ercot_all_hub_prices_history", in_dir, usecols=["ts_utc", "value", "market", "node", "year"],
                       keep=lambda c: (c["market"] == "ercot_rtm") & (c["node"] == "HB_HUBAVG") & (c["year"].astype(int) >= first_year - 1))
        live = read_table("iso_rtm_hub_prices", in_dir, usecols=["ts_utc", "value", "market", "node"],
                          keep=lambda c: (c["market"] == "ercot_rtm") & (c["node"] == "HB_HUBAVG"))
        d = pd.concat([h[["ts_utc", "value"]], live[["ts_utc", "value"]]]).drop_duplicates("ts_utc")
    elif grid == "caiso":
        d = read_table("iso_rtm_hub_prices", in_dir, usecols=["ts_utc", "value", "market", "node"],
                       keep=lambda c: (c["market"] == "caiso_rtm") & (c["node"] == "TH_SP15_GEN-APND"))
    elif grid == "spp":
        d = read_table("iso_rtm_hub_prices", in_dir, usecols=["ts_utc", "value", "market", "node"],
                       keep=lambda c: (c["market"] == "spp_rtm") & (c["node"] == "SPPSOUTH_HUB"))
    elif grid == "nyiso":
        d = read_table("nyiso_rtm_zone_prices", in_dir, usecols=["ts_utc", "value", "market"], keep=lambda c: c["market"] == "nyiso_rtm")
    elif grid == "isone":
        d = read_table("isone_zone_prices_history", in_dir, usecols=["ts_utc", "value", "market", "variable"],
                       keep=lambda c: (c["market"] == "isone_rtm") & (c["variable"] == "lmp_rtm") & (c["ts_utc"] >= f"{first_year}-01-01"))
    else:
        raise ValueError(grid)
    if d.empty:
        raise NoData(f"no real-time rows for {grid}")
    return d


def compute(params, in_dir=None):
    first_year = int(params.get("first_year", 2019))
    hh = henry_hub_monthly(in_dir)
    rows, meta = [], {"first_year": first_year, "spans": {}, "missing": []}
    this_year = pd.Timestamp.now(tz="UTC").year
    for grid, words, tz, how in GRIDS:
        try:
            d = grid_hours(grid, first_year, in_dir)
        except NoData as exc:
            meta["missing"].append({"grid": grid, "reason": str(exc)})
            for y in range(first_year, this_year + 1):
                rows.append({"grid": grid, "year": y, "n_hours": None, "first_hour": None, "last_hour": None,
                             **{f"share_below_hr{hr:g}".replace(".", "p"): None for hr in HEAT_RATES}})
            continue
        h = hourly(d, tz)
        h = h[h["year"] >= first_year]
        h["hh"] = h["month"].map(hh)
        h = h[h["hh"].notna()]
        meta["spans"][grid] = {"first_hour": h["hour"].min().strftime("%Y-%m-%d %H:00"), "last_hour": h["hour"].max().strftime("%Y-%m-%d %H:00"),
                               "n_hours": int(len(h)), "how": how, "tz": tz}
        by_year = {y: g for y, g in h.groupby("year")}
        for y in range(first_year, this_year + 1):
            g = by_year.get(y)
            r = {"grid": grid, "year": y, "n_hours": int(len(g)) if g is not None else None,
                 "first_hour": g["hour"].min().strftime("%Y-%m-%d") if g is not None else None,
                 "last_hour": g["hour"].max().strftime("%Y-%m-%d") if g is not None else None}
            for hr in HEAT_RATES:
                k = f"share_below_hr{hr:g}".replace(".", "p")
                r[k] = float((g["value"] < hr * g["hh"]).mean() * 100) if g is not None and len(g) else None
            rows.append(r)
    return rows, meta


def key(hr):
    return f"share_below_hr{hr:g}".replace(".", "p")


def numbers_from_rows(rows, params=None):
    hr = float((params or {}).get("heat_rate", 7.0))
    k = key(hr)
    years = sorted({r["year"] for r in rows})
    held = [r for r in rows if r[k] is not None]
    last_full = max(y for y in years if y < years[-1])
    first = years[0]
    def at(grid, y):
        for r in rows:
            if r["grid"] == grid and r["year"] == y:
                return r[k]
        return None
    n = {"heat_rate": hr, "first_year": first, "last_full_year": last_full,
         "ercot_first": at("ercot", first), "ercot_last": at("ercot", last_full),
         "isone_first": at("isone", first), "isone_last": at("isone", last_full),
         "ercot_last_hr6p5": next(r[key(6.5)] for r in rows if r["grid"] == "ercot" and r["year"] == last_full),
         "ercot_last_hr8": next(r[key(8.0)] for r in rows if r["grid"] == "ercot" and r["year"] == last_full),
         "ercot_hours_last": next(r["n_hours"] for r in rows if r["grid"] == "ercot" and r["year"] == last_full),
         "isone_hours_last": next(r["n_hours"] for r in rows if r["grid"] == "isone" and r["year"] == last_full),
         "n_cells_held": len(held), "n_cells": len(rows), "this_year": years[-1],
         "caiso_this": at("caiso", years[-1]), "nyiso_this": at("nyiso", years[-1]), "spp_this": at("spp", years[-1]),
         "ercot_this": at("ercot", years[-1])}
    return n


def chart(rows, hr):
    years = sorted({r["year"] for r in rows})
    series = []
    for grid, words, _, _ in GRIDS:
        series.append({"name": words, "type": "bar", "unit": "percent of hours",
                       "values": [next((r[key(hr)] for r in rows if r["grid"] == grid and r["year"] == y), None) for y in years],
                       "sensitivity": {f"{h:g}": [next((r[key(h)] for r in rows if r["grid"] == grid and r["year"] == y), None) for y in years] for h in HEAT_RATES},
                       "hours": [next((r["n_hours"] for r in rows if r["grid"] == grid and r["year"] == y), None) for y in years]})
    return {"kind": "grouped_bar", "x": [str(y) for y in years], "x_label": "Year (local)", "series": series,
            "y_left_label": f"percent of hours below {hr:g} x Henry Hub", "placeholders": PLACEHOLDERS}


def card(rows, params, meta):
    hr = float(params.get("heat_rate", 7.0))
    n = numbers_from_rows(rows, params)
    y0, y1 = n["first_year"], n["last_full_year"]
    e0, e1, i0, i1 = n["ercot_first"], n["ercot_last"], n["isone_first"], n["isone_last"]
    if e1 is not None and e0 is not None and e1 > e0 + 5:
        sub = "In ERCOT, yes: the hub cleared below a gas plant's fuel cost far more often"
    elif e1 is not None and e0 is not None and e1 < e0 - 5:
        sub = "In ERCOT, no: the hub cleared below a gas plant's fuel cost less often"
    else:
        sub = "In ERCOT the share barely moved; the sensitivity moves it more than the years do"
    held = [g for g in ("caiso", "nyiso", "spp") if n[f"{g}_this"] is not None]
    spans = meta.get("spans", {})
    why = (f"At {hr:g} MMBtu per MWh, ERCOT's hub average sat below a gas plant's fuel cost in {fmt(e0, 1)} percent of {y0}'s hours and "
           f"{fmt(e1, 1)} percent of {y1}'s ({fmt(n['ercot_hours_last'], 0)} hours). ISO-NE's zones went from {fmt(i0, 1)} to {fmt(i1, 1)} percent. "
           f"The heat rate matters: at 6.5 ERCOT's {y1} share is {fmt(n['ercot_last_hr6p5'], 1)} percent and at 8.0 it is {fmt(n['ercot_last_hr8'], 1)}. "
           + ("CAISO, NYISO and SPP are held from " + ", ".join(f"{g.upper()} {spans[g]['first_hour'][:10]}" for g in held if g in spans)
              + f" only, so their {n['this_year']} bars cover weeks, not a year, and their earlier years are not held: "
              + ", ".join(f"{g.upper()} {fmt(n[f'{g}_this'], 1)} percent" for g in held) + ". " if held else "")
           + "An hour below fuel cost is an hour when something cheaper than gas set the price, or gas sold below its cost; the share says how "
           "often, not which. Henry Hub is the national benchmark; New England's gas is dearer at Algonquin, so ISO-NE's share reads low.")
    foot = (f"Data: real-time prices by local hour, {y0} to {n['this_year']}: " +
            "; ".join(f"{w}: {spans[g]['how']}, {spans[g]['first_hour']} to {spans[g]['last_hour']} ({fmt(spans[g]['n_hours'], 0)} hours, {spans[g]['tz']})"
                      for g, w, _, _ in GRIDS if g in spans) +
            ". Gas: Henry Hub daily spot (EIA), the calendar month's mean applied to every hour of the month. An hour counts when its price is "
            f"below heat rate x Henry Hub; shares are percent of the year's held hours; {hr:g} MMBtu/MWh on the card, 6.5 and 8.0 in the hover. "
            "A year a grid's history does not cover is not held and not filled. ISO-NE's hourly history is an internal table: only these "
            "aggregates are published. MISO paused, PJM licensed: placeholders.")
    return {
        "id": NAME, "title": TITLE, "kind": KIND, "subtitle": sub, "params": {"heat_rate": hr, "first_year": meta["first_year"]},
        "inputs_words": {"heat_rate": f"{hr:g} MMBtu per MWh", "first_year": str(meta["first_year"])},
        "chart": chart(rows, hr),
        "callouts": [
            callout("ERCOT hours below gas fuel cost", str(y0), f"{fmt(e0, 1)}%", str(y1), f"{fmt(e1, 1)}%"),
            callout("ISO-NE hours below gas fuel cost", str(y0), f"{fmt(i0, 1)}%", str(y1), f"{fmt(i1, 1)}%"),
            callout(f"ERCOT {y1}, heat rate 6.5 to 8.0", "6.5", f"{fmt(n['ercot_last_hr6p5'], 1)}%", "8.0", f"{fmt(n['ercot_last_hr8'], 1)}%"),
        ],
        "why": why, "footnote": foot, "numbers": n, "placeholders": PLACEHOLDERS,
        "source_line": "Source: ERCOT, CAISO OASIS, NYISO, ISO-NE, SPP real-time prices; EIA Henry Hub spot; ERW tables " + ", ".join(TABLES) + ".",
        "tables": TABLES, "computed_at": now_iso(), "method": METHOD_URL,
        "csv_header": [f"Energy Research Warehouse (ERW): finding {NAME}, {TITLE}", f"Computed {now_iso()} by warehouse/analysis/findings/{NAME}.py; method {METHOD_URL}",
                       "Rows: one per grid and local year: held hours and the percent of them with the real-time price below heat rate x Henry Hub (6.5, 7.0, 8.0)",
                       "A blank is a year the warehouse does not hold for that grid. Sources: " + ", ".join(TABLES)],
    }


def stata(params):
    V = ["year", "n_hours", key(6.5), key(7.0), key(8.0)]
    return do_file([
        f"* ERW finding {NAME}: {TITLE}. Reproduces the card's shares from {CSV_NAME}.",
        "clear all",
        f'import delimited "{CSV_NAME}", varnames(1) stringcols(_all) clear',
        *do_destring(V),
        *do_sentinels(V),
        "sort grid year",
        ["foreach v in share_below_hr6p5 share_below_hr7 share_below_hr8 {",
         "    tabstat `v', by(grid) statistics(mean min max) format(%6.1f)",
         "}"],
        "list grid year n_hours share_below_hr7, sepby(grid) noobs",
    ])


SOURCE_PATH = os.path.abspath(__file__)
