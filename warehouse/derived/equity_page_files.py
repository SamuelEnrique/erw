#!/usr/bin/env python3
"""The page files of energy equities (session 10000, chain 701, part D4), by the contract docs/state/page_files_equities.md.

Energy Research Warehouse (ERW). Writes, from warehouse tables only (no request):

    site/data/equities/index.json          the segments, the companies and the indices (the lists)
    site/data/equities/board.json          the rows the price board's equities group shows, in the board's own row form
    site/data/equities/energy_prices.json  the energy prices set beside the equities, daily where the table is daily

Today the equity side holds nothing a page may show: SEC EDGAR, the one source of each company's industry code, share
count and statements, refuses the ERW's contact string, and no free source of daily share prices may be kept
(docs/reviews/equities-sources-2026-11-26.md). So the segments carry their names and the reason their rule cannot be
applied, the lists of companies and indices are empty, every board row is held with that reason, and no company or
index file is written. The energy prices are the warehouse's own:

    wti, brent, henry_hub   eia_fuel_spot_prices (EIA's daily spot prices), daily
    uranium                 imf_commodity_prices (IMF PCPS, PURAN), monthly, on its own dates
    cca_current             carb_auction_allowance_prices (CARB's quarterly auctions, current vintage), on its own dates
    ercot_hb_hubavg_da      ercot_hub_prices_daily (da_mean of ercot:HB_HUBAVG), daily
    caiso_sp15_da, caiso_np15_da   iso_hub_prices_history (caiso_dam), the mean of each complete Pacific day's 24 hours
                            (23 or 25 on the clock-change days); a day short of an hour is not written
    pjm, nyiso, isone, miso the grids docs/licenses.md holds or MISO's pause: a series with its status and no rows

Each daily series is written from 2016-01-01 (the contract's span is that of the longest shown equity series; none is
shown yet, so the last ten whole years and this one: a dated line of the contract says so).

    python warehouse/derived/equity_page_files.py [--out DIR]

Method: docs/methods/equities.md.
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
import iso_prices as ip  # noqa: E402

OUT = os.path.join(ROOT, "site", "data", "equities")
METHOD = "docs/methods/equities.md"
CONTRACT = "docs/state/page_files_equities.md"
SINCE = "2016-01-01"
SEC_WHY = ("source needed: the segment rule reads each company's SEC industry code (SIC), and SEC EDGAR refuses the ERW's "
           "contact string (docs/reviews/equities-sources-2026-11-26.md); no company is put in a segment by judgment")
PRICE_WHY = ("license needed: no source found whose terms allow the ERW to keep daily share prices or index levels "
             "(docs/reviews/equities-sources-2026-11-26.md)")
SEGMENTS = [("integrated_oil_gas", "Integrated oil and gas"), ("exploration_production", "Exploration and production"),
            ("midstream_pipelines", "Midstream and pipelines"), ("refining", "Refining"), ("oilfield_services", "Oilfield services"),
            ("lng", "LNG"), ("coal", "Coal"), ("regulated_utilities", "Regulated electric and gas utilities"),
            ("independent_power", "Independent power producers"), ("nuclear_uranium", "Nuclear and uranium"), ("solar", "Solar"),
            ("wind", "Wind"), ("storage", "Storage"), ("hydrogen_fuel_cells", "Hydrogen and fuel cells"),
            ("grid_equipment", "Grid and electrical equipment")]
HELD_GRIDS = [("pjm_western_hub_da", "PJM Western Hub, day-ahead", "license needed",
               "PJM's terms allow republication to members only (docs/licenses.md); held until a permission is recorded"),
              ("nyiso_zone_j_da", "NYISO New York City, day-ahead", "license needed",
               "NYISO's terms ask for written permission to republish (docs/licenses.md); none is recorded"),
              ("isone_mass_hub_da", "ISO-NE Mass Hub, day-ahead", "license needed",
               "ISO-NE's terms ask for written permission to republish (docs/licenses.md); none is recorded"),
              ("miso_indiana_hub_da", "MISO Indiana Hub, day-ahead", "paused",
               "MISO is paused since 4 October 2026: its terms forbid automated access (docs/methods/miso_pause.md)")]


def read(table, entity=None, variable=None):
    path = os.path.join(ip.OUT_DIR, table + ".csv")
    parts = []
    for ch in pd.read_csv(path, skiprows=ip.header_rows(path), dtype=str, keep_default_na=False, chunksize=500_000):
        if entity is not None:
            ch = ch[ch["entity"] == entity]
        if variable is not None:
            ch = ch[ch["variable"] == variable]
        if len(ch):
            parts.append(ch)
    if not parts:
        raise RuntimeError(f"{table}: no rows of {entity} {variable}")
    return pd.concat(parts, ignore_index=True)


def by_day(df):
    """[(YYYY-MM-DD, value)] from a table's rows dated at a day's 00:00Z, oldest first."""
    s = sorted((t[:10], float(v)) for t, v in zip(df["ts_utc"], df["value"]) if v != "")
    return s


def caiso_daily(node):
    """The mean of each complete Pacific day of CAISO's day-ahead price at a node (iso_hub_prices_history)."""
    df = read("iso_hub_prices_history", entity=f"caiso:{node}")
    df = df[df["market"] == "caiso_dam"]
    t = pd.to_datetime(df["ts_utc"], utc=True)
    loc = t.dt.tz_convert("America/Los_Angeles")
    d = pd.DataFrame({"day": loc.dt.strftime("%Y-%m-%d"), "v": df["value"].astype(float), "t": t}).drop_duplicates("t")
    out = []
    for day, g in d.groupby("day"):
        start = pd.Timestamp(day).tz_localize("America/Los_Angeles")
        end = (pd.Timestamp(day) + pd.Timedelta(days=1)).tz_localize("America/Los_Angeles")
        hours = round((end - start).total_seconds() / 3600)   # 24; 23 or 25 on the clock-change days
        if len(g) == hours:
            out.append((day, float(round(g["v"].mean(), 4))))
    return out


def move(series, last_day, last_v, back):
    """The board's move: the value on the last day held on or before `back`, and the change to the last value."""
    prior = [(d, v) for d, v in series if d <= back]
    if not prior:
        return None
    d, v = prior[-1]
    ch = last_v - v
    return {"t": d, "v": v, "ch": round(ch, 4), "pct": round(ch / v * 100, 2) if v else None}


def moves(series):
    if not series:
        return {"d": None, "w": None, "m": None, "ytd": None, "y": None}
    last_d, last_v = series[-1]
    day = dt.date.fromisoformat(last_d)
    prev = series[-2][0] if len(series) > 1 else None

    def back_months(n):
        y, m = day.year, day.month - n
        while m < 1:
            y, m = y - 1, m + 12
        import calendar
        return dt.date(y, m, min(day.day, calendar.monthrange(y, m)[1])).isoformat()
    return {"d": move(series, last_d, last_v, prev) if prev else None,
            "w": move(series, last_d, last_v, (day - dt.timedelta(days=7)).isoformat()),
            "m": move(series, last_d, last_v, back_months(1)),
            "ytd": move(series, last_d, last_v, dt.date(day.year - 1, 12, 31).isoformat()),
            "y": move(series, last_d, last_v, back_months(12))}


def energy_series():
    spot = "EIA's daily spot prices (eia_fuel_spot_prices; EIA names Refinitiv, an LSEG business, as their source), https://www.eia.gov/dnav/pet/pet_pri_spt_s1_d.htm"
    specs = [
        ("wti", "WTI crude oil, Cushing, spot", "USD/bbl", "D", "eia_fuel_spot_prices", "eia:wti_cushing", "spot_price", spot,
         lambda: by_day(read("eia_fuel_spot_prices", "eia:wti_cushing", "spot_price"))),
        ("brent", "Brent crude oil, Europe, spot", "USD/bbl", "D", "eia_fuel_spot_prices", "eia:brent", "spot_price", spot,
         lambda: by_day(read("eia_fuel_spot_prices", "eia:brent", "spot_price"))),
        ("henry_hub", "Henry Hub natural gas, spot", "USD/MMBtu", "D", "eia_fuel_spot_prices", "eia:henry_hub", "spot_price", spot,
         lambda: by_day(read("eia_fuel_spot_prices", "eia:henry_hub", "spot_price"))),
        ("ercot_hb_hubavg_da", "ERCOT Hub average, day-ahead, daily mean", "USD/MWh", "D", "ercot_hub_prices_daily", "ercot:HB_HUBAVG", "da_mean",
         "ERCOT, from the ERW's daily table of its hub prices (ercot_hub_prices_daily)",
         lambda: by_day(read("ercot_hub_prices_daily", "ercot:HB_HUBAVG", "da_mean"))),
        ("caiso_sp15_da", "CAISO SP15, day-ahead, daily mean", "USD/MWh", "D", "iso_hub_prices_history", "caiso:TH_SP15_GEN-APND", "caiso_dam",
         "CAISO OASIS day-ahead LMP (iso_hub_prices_history), the mean of each complete Pacific day", lambda: caiso_daily("TH_SP15_GEN-APND")),
        ("caiso_np15_da", "CAISO NP15, day-ahead, daily mean", "USD/MWh", "D", "iso_hub_prices_history", "caiso:TH_NP15_GEN-APND", "caiso_dam",
         "CAISO OASIS day-ahead LMP (iso_hub_prices_history), the mean of each complete Pacific day", lambda: caiso_daily("TH_NP15_GEN-APND")),
        ("uranium", "Uranium, monthly average", "USD/lb", "M", "imf_commodity_prices", "imf:PCPS:PURAN", "price",
         "International Monetary Fund, Primary Commodity Price System (imf_commodity_prices)",
         lambda: by_day(read("imf_commodity_prices", "imf:PCPS:PURAN", "price"))),
        ("cca_current", "California carbon allowance, quarterly auction settlement (current vintage)", "USD/t CO2e", "Q",
         "carb_auction_allowance_prices", "carb:current_auction", "settlement_price",
         "California Air Resources Board, auction settlement prices (carb_auction_allowance_prices)",
         lambda: by_day(read("carb_auction_allowance_prices", "carb:current_auction", "settlement_price"))),
    ]
    series, daily = [], {}
    for sid, label, unit, freq, table, entity, variable, source, get in specs:
        s = get()
        s = [(d, v) for d, v in s if d >= SINCE] if freq == "D" else s
        series.append({"id": sid, "label": label, "unit": unit, "freq": freq, "table": table, "entity": entity, "variable": variable,
                       "source": source, "license": "public", "status": "shown", "why": None,
                       "first": s[0][0] if s else None, "last": s[-1][0] if s else None,
                       "last_value": {"t": s[-1][0], "v": s[-1][1]} if s else None, "moves": moves(s)})
        daily[sid] = [[d, v] for d, v in s]
    for sid, label, status, why in HELD_GRIDS:
        series.append({"id": sid, "label": label, "unit": "USD/MWh", "freq": "D", "table": None, "entity": None, "variable": None,
                       "source": None, "license": "internal" if status == "license needed" else None, "status": status, "why": why,
                       "first": None, "last": None, "last_value": None, "moves": {"d": None, "w": None, "m": None, "ytd": None, "y": None}})
    return series, daily


def build(built):
    tables = ["equity_universe", "equity_prices_daily", "equity_fundamentals_quarterly", "equity_index_daily"]
    index = {"built": built, "example": False, "method": METHOD, "contract": CONTRACT, "license": "public", "tables": tables,
             "last_day": None,
             "segments": [{"id": i, "label": l, "rule": None, "rule_why": SEC_WHY, "n_companies": None} for i, l in SEGMENTS],
             "companies": [], "indices": [], "segment_series": [],
             "held": {"companies": SEC_WHY, "indices": PRICE_WHY, "prices": PRICE_WHY}}
    rows = []
    for i, l in SEGMENTS:
        for w, wl in (("equal", "equal weight"), ("value", "weighted by market value")):
            rows.append({"id": f"equities-segment-{i}-{w}", "group": "equities", "label": f"{l} ({wl})", "unit": "index, first day = 100",
                         "tags": {"kind": "segment", "weighting": w}, "status": "not_held", "note": f"{SEC_WHY}; and {PRICE_WHY}",
                         "file": None})
    board = {"built": built, "example": False, "method": METHOD, "contract": CONTRACT,
             "group": {"id": "equities", "title": "Energy equities",
                       "filters": [{"key": "kind", "label": "Show", "options": [["all", "Segments and indices"], ["segment", "Segments"],
                                                                               ["index", "Indices"]], "default": "all"}]},
             "sources": [], "rows": rows}
    series, daily = energy_series()
    prices = {"built": built, "example": False, "method": METHOD, "contract": CONTRACT, "since": SINCE, "series": series, "daily": daily}
    return {"index.json": index, "board.json": board, "energy_prices.json": prices}


def main(argv=None):
    ap = argparse.ArgumentParser(description="The equities page files (docs/state/page_files_equities.md)")
    ap.add_argument("--out", default=OUT)
    a = ap.parse_args(argv)
    built = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    files = build(built)
    os.makedirs(a.out, exist_ok=True)
    for name, obj in files.items():
        path = os.path.join(a.out, name)
        with open(path + ".tmp", "w", encoding="utf-8", newline="\n") as f:
            json.dump(obj, f, ensure_ascii=False, separators=(",", ":"))
        os.replace(path + ".tmp", path)
    p = files["energy_prices.json"]
    shown = [s for s in p["series"] if s["status"] == "shown"]
    print(f"equity pages: {len(files['index.json']['segments'])} segments, 0 companies, 0 indices (held), "
          f"{len(files['board.json']['rows'])} board rows held; energy prices {len(shown)} shown, "
          f"{len(p['series']) - len(shown)} held; built {built}")
    for s in shown:
        print(f"  {s['id']}: {s['first']} to {s['last']}, {len(p['daily'][s['id']])} points, last {s['last_value']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
