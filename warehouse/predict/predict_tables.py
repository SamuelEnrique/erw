#!/usr/bin/env python3
"""The ERW forecast's two ledgers as warehouse tables: predict_demand_forecasts and predict_price_forecasts.

Energy Research Warehouse (ERW), session 10000 (chain 701), data requests 2 and 5 of docs/state/data_requests_predict.md.
warehouse/predict/run.py appends each day's forecast to site/data/predict/ledger_demand.csv and ledger_price.csv once,
and never overwrites a forecast already written. This script writes each ledger as a table in the series shape, one row
a place and UTC hour of a target day, as the forecast was made on its day:

- entity `eia930:<code>` of the place (region-tex is eia930:TEX, ba-erco is eia930:ERCO), as data request 2 asks;
- variable `demand_forecast_mw` (MW) or `lmp_dam_forecast` (USD/MWh, the day-ahead price of the place's hub, named in
  `market` and `node`, as warehouse/predict/predict_data.HUBS reads it);
- `vintage` the hour the forecast was made (the ledger's made_utc). Revisions are kept: a newer forecast for an hour
  already held is a second row with its own vintage, never a replacement, so the key is entity, variable, ts_utc and
  vintage (the data standard's rule 77);
- x_place, x_method, x_horizon_days, x_inputs_through_utc, x_target_day, x_local_hour, x_lo and x_hi as the ledger
  holds them.

The table is the whole ledger, rewritten from it each run (iso_prices.write_snapshot): the ledger is the append-only
record, so a row once in the table stays in it. Tier derived: a model's output, never a published or official figure.
No request is made and no model is called.

    python warehouse/predict/predict_tables.py                  # the two tables, under the data lock
    python warehouse/predict/predict_tables.py --out-dir DIR    # a trial: the tables under DIR
    python warehouse/predict/predict_tables.py --ledger-dir DIR # read the ledgers from DIR (a worktree reads main's)
"""
import argparse
import datetime as dt
import os
import sys
import traceback

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import iso_prices as ip  # noqa: E402

CONNECTOR = "predict_tables"
SOURCE = "erw:predict"
LEDGER_DIR = os.path.join(ROOT, "site", "data", "predict")
METHODS = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/"
# the place each price forecast is made for, and its grid (warehouse/predict/run.py PRICE_GRID), and the grid's hub
# (warehouse/predict/predict_data.py HUBS); a ledger place outside these is an error, never guessed
PRICE_GRID = {"region-tex": "ercot", "ba-erco": "ercot", "region-cent": "spp", "ba-swpp": "spp", "region-cal": "caiso",
              "ba-ciso": "caiso"}
HUBS = {"ercot": "ercot:HB_NORTH", "spp": "spp:SPPNORTH_HUB", "caiso": "caiso:TH_SP15_GEN-APND"}
COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "market", "node", "source", "source_url", "retrieved_at",
        "vintage", "x_place", "x_method", "x_horizon_days", "x_inputs_through_utc", "x_target_day", "x_local_hour",
        "x_lo", "x_hi"]
LEDGER_COLS = ["series", "place", "target_day", "ts_utc", "local_hour", "made_utc", "inputs_through_utc", "horizon_days",
               "method", "erw", "lo", "hi"]
TABLES = {
    "demand": dict(name="predict_demand_forecasts", variable="demand_forecast_mw", unit="MW", method="predict.md",
                   what="hourly demand of each EIA-930 region and large balancing authority",
                   inputs="eia930_ba_demand_hourly (U.S. Energy Information Administration, Form EIA-930, public)"),
    "price": dict(name="predict_price_forecasts", variable="lmp_dam_forecast", unit="USD/MWh", method="predict_price.md",
                  what="day-ahead price of the hub of each place's grid (ERCOT HB_NORTH, SPP SPPNORTH_HUB, CAISO TH_SP15)",
                  inputs="the hubs' day-ahead prices (ERCOT, SPP, CAISO, public), eia930_ba_demand_hourly and "
                         "eia_fuel_spot_prices (public)"),
}


def entity(place):
    kind, code = place.split("-", 1)
    if kind not in ("region", "ba") or not code:
        raise ValueError(f"a ledger place that is neither a region nor a balancing authority: {place!r}")
    return "eia930:" + code.upper()


def table(ledger, series, retrieved):
    """The ledger's rows of one series as the table's rows."""
    t = TABLES[series]
    if list(ledger.columns) != LEDGER_COLS:
        raise ValueError(f"the {series} ledger's columns are {list(ledger.columns)}, not {LEDGER_COLS}")
    x = ledger[ledger["series"] == series]
    if len(x) != len(ledger):
        raise ValueError(f"the {series} ledger holds {len(ledger) - len(x)} rows of another series")
    if x.empty:
        raise ValueError(f"the {series} ledger holds no forecast")
    if (x[["ts_utc", "made_utc"]] == "").any().any():
        raise ValueError(f"the {series} ledger has a row without its hour or its making time")
    # 27 November 2026: run.py wrote a day of rows with no figure for one new place (ba-spa, made 19:00 UTC), and the whole
    # table was refused. A row without a figure is no forecast: it is left out, and header() says how many and where
    x = x[x["erw"] != ""]
    if x.empty:
        raise ValueError(f"the {series} ledger holds no forecast with a figure")
    out = pd.DataFrame({
        "entity": x["place"].map(entity), "variable": t["variable"], "ts_utc": x["ts_utc"], "value": x["erw"],
        "unit": t["unit"], "freq": "PT1H", "market": "", "node": "", "source": SOURCE,
        "source_url": METHODS + t["method"], "retrieved_at": retrieved, "vintage": x["made_utc"],
        "x_place": x["place"], "x_method": x["method"], "x_horizon_days": x["horizon_days"],
        "x_inputs_through_utc": x["inputs_through_utc"], "x_target_day": x["target_day"], "x_local_hour": x["local_hour"],
        "x_lo": x["lo"], "x_hi": x["hi"],
    })
    if series == "price":
        grid = x["place"].map(PRICE_GRID)
        if grid.isna().any():
            raise ValueError(f"price ledger places with no grid: {sorted(set(x['place'][grid.isna()]))}")
        out["market"] = grid.values
        out["node"] = grid.map(HUBS).str.split(":", n=1).str[1].values
    dup = out.duplicated(["entity", "variable", "ts_utc", "vintage"])
    if dup.any():
        raise ValueError(f"the {series} ledger holds {int(dup.sum())} rows twice for one place, hour and making time")
    return out.sort_values(["entity", "ts_utc", "vintage"]).reset_index(drop=True)


def figureless(ledger, series):
    """The words for the ledger's rows of a series that hold no figure (left out of the table), or 'none'."""
    x = ledger[(ledger["series"] == series) & (ledger["erw"] == "")]
    if x.empty:
        return "none"
    groups = x.groupby(["place", "made_utc"]).size()
    return f"{len(x)} (" + "; ".join(f"{p} made {m}: {n}" for (p, m), n in groups.items()) + ")"


def header(series, t, run_id, left_out="none"):
    m = TABLES[series]
    return [
        f"Energy Research Warehouse (ERW): the ERW forecast of the {m['what']}, every forecast as made on its day "
        "(tier derived: a model's output, not a published or official figure). Session 10000 (chain 701).",
        f"Shape: series (docs/datastandard.md v0). entity eia930:<code> of the place; variable {m['variable']} "
        f"({m['unit']}); ts_utc the forecast hour's start (UTC); x_lo and x_hi the forecast's range; market and node the "
        "hub, for the price.",
        "Revisions: kept, one row per vintage. Key: entity, variable, ts_utc, vintage. vintage is the hour the forecast "
        "was made (the ledger's made_utc); a forecast once made is never replaced.",
        f"Forecasts: target days {t['x_target_day'].min()} to {t['x_target_day'].max()}; {t['entity'].nunique()} places; "
        f"{t['vintage'].nunique()} makings; {len(t)} rows. Ledger rows without a figure, left out: {left_out}.",
        f"Retrieved: {run_id} (UTC) by warehouse/predict/predict_tables.py, from site/data/predict/ledger_{series}.csv "
        "(written by warehouse/predict/run.py)",
        f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
        f"Source: {SOURCE} the ERW's own forecast, from {m['inputs']}, {METHODS}{m['method']}",
        "License: public (derived by the ERW from public data).",
        f"Method: docs/methods/{m['method']}",
    ]


def main(argv=None):
    ap = argparse.ArgumentParser(description="The ERW forecast's ledgers as warehouse tables (data requests 2 and 5)")
    ap.add_argument("--out-dir", help="a trial: the tables under this folder, not warehouse/output")
    ap.add_argument("--ledger-dir", default=LEDGER_DIR, help="the folder holding ledger_demand.csv and ledger_price.csv")
    args = ap.parse_args(argv)
    if args.out_dir:
        raw_dir = ip.RAW_DIR
        ip.set_out_dir(args.out_dir)
        ip.RAW_DIR = raw_dir
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    now = dt.datetime.now(dt.timezone.utc)
    run_id = now.strftime("%Y%m%dT%H%M%SZ")
    retrieved = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{CONNECTOR}_{run_id}.log"))
    results, written = [], []
    for series, m in TABLES.items():
        try:
            p = os.path.join(args.ledger_dir, f"ledger_{series}.csv")
            ledger = pd.read_csv(p, skiprows=ip.header_rows(p), dtype=str, keep_default_na=False)
            t = table(ledger, series, retrieved)
            ip.write_snapshot(t, m["name"], header(series, t, run_id, figureless(ledger, series)), log, cols=COLS)
            written.append(m["name"])
            results.append(dict(table=m["name"], market="all", status="ok",
                                detail=f"{len(t)} rows, target days {t['x_target_day'].min()} to {t['x_target_day'].max()}"))
            print(f"{m['name']}: {len(t)} rows, {t['entity'].nunique()} places, {t['vintage'].nunique()} makings, "
                  f"target days {t['x_target_day'].min()} to {t['x_target_day'].max()}")
        except Exception:
            tb = ip.redact(traceback.format_exc())
            log(f"{m['name']} FAILED, no output file written:\n{tb}")
            print(f"{m['name']} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
            results.append(dict(table=m["name"], market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if written and not args.out_dir:
        ip.update_sources([dict(source=SOURCE, publisher="Energy Research Warehouse (ERW), derived",
                                report="The ERW forecast of hourly demand and of day-ahead hub prices (warehouse/predict/)",
                                report_url=METHODS + "predict.md", document_list="", license="public", tables=written)])
    if not args.out_dir:
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
