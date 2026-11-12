#!/usr/bin/env python3
"""FERC Form 714, Part 3, Schedule 2: each planning area's ten-year forecast, as filed each year (session 3758).

Energy Research Warehouse (ERW) connector, chain 211, under the owner's ruling 1 of 6 November 2026
(docs/state/rulings_2026-11-06.md: the pull is allowed, license public). One series table,
warehouse/output/ferc714_planning_area_forecasts.csv, from Catalyst Cooperative's Public Utility Data Liberation
project (PUDL), stable release, table core_ferc714__yearly_planning_area_demand_forecast (FERC's filings as filed;
FERC's own site refuses automated requests, session 484):

    https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/stable/core_ferc714__yearly_planning_area_demand_forecast.parquet

    entity    ferc714:<PUDL's respondent id>   (the entity of ferc714_area_demand and ferc714_respondents)
    variable  summer_peak_forecast_mw, winter_peak_forecast_mw (MW), net_energy_forecast_mwh (MWh)
    ts_utc    the forecast year's first instant, <forecast_year>-01-01T00:00:00Z; freq P1Y
    vintage   the filing: 1 June of the year after the report year, FERC-714's due date (PUDL gives no submission time)
    x_report_year  the report year of the filing the forecast is in

A planning area files a forecast for each of the next ten years every year, so the same forecast year appears once a
filing: the table keeps every filing (its key is entity, variable, ts_utc and vintage, as docs/datastandard.md allows
for a table that keeps its revisions, and its header says so). That is the point: warehouse/derived/
ferc714_forecast_growth.py reads how each area's forecast of one year moved from filing to filing.

Values as PUDL publishes them; a blank stays blank (no row); nothing is filled. A (respondent, report year, forecast
year) given twice stops the run.

    python warehouse/connectors/ferc714_forecasts.py
    python warehouse/connectors/ferc714_forecasts.py --out-dir C:/scratch      a trial: nothing in warehouse/output

Ceiling: one request a run (the file is about 250 KB); a raw file this connector saved before is reused.
License: public (the owner's ruling 1 of 6 November 2026; PUDL's data are CC-BY-4.0,
attribution in the header and the source registry).
"""

import argparse
import datetime as dt
import io
import os
import sys
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "ferc714_planning_area_forecasts"
CONNECTOR = "ferc714_forecasts"
SOURCE = "pudl:core_ferc714__yearly_planning_area_demand_forecast"
URL = "https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/stable/core_ferc714__yearly_planning_area_demand_forecast.parquet"
PAGE = "https://docs.catalyst.coop/pudl/en/stable/data_sources/ferc714.html"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
VARS = {"summer_peak_demand_forecast_mw": ("summer_peak_forecast_mw", "MW"),
        "winter_peak_demand_forecast_mw": ("winter_peak_forecast_mw", "MW"),
        "net_demand_forecast_mwh": ("net_energy_forecast_mwh", "MWh")}
COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "market", "node", "source", "source_url",
        "retrieved_at", "vintage", "x_report_year"]
KEY = ["entity", "variable", "ts_utc", "vintage"]
CEILING = 100_000


def filing_vintage(report_year):
    """FERC-714's due date for a report year: 1 June of the year after it."""
    return f"{int(report_year) + 1}-06-01T00:00:00Z"


def forecasts(d, url, retrieved):
    need = ["respondent_id_ferc714", "report_year", "forecast_year"] + list(VARS)
    missing = [c for c in need if c not in d.columns]
    if missing:
        raise RuntimeError(f"the file lacks {missing}")
    if d[["respondent_id_ferc714", "report_year", "forecast_year"]].isna().any().any():
        raise RuntimeError("a row with no respondent, report year or forecast year")
    dup = d.duplicated(["respondent_id_ferc714", "report_year", "forecast_year"])
    if dup.any():
        raise RuntimeError(f"{int(dup.sum())} (respondent, report year, forecast year) given twice")
    long = d.melt(id_vars=["respondent_id_ferc714", "report_year", "forecast_year"], value_vars=list(VARS),
                  var_name="col", value_name="value").dropna(subset=["value"])
    out = pd.DataFrame({
        "entity": "ferc714:" + long["respondent_id_ferc714"].astype(int).astype(str),
        "variable": long["col"].map(lambda c: VARS[c][0]),
        "ts_utc": long["forecast_year"].astype(int).astype(str) + "-01-01T00:00:00Z",
        "value": long["value"].astype(float),
        "unit": long["col"].map(lambda c: VARS[c][1]),
        "freq": "P1Y", "geo": "US", "market": "", "node": "",
        "source": SOURCE, "source_url": url, "retrieved_at": retrieved,
        "vintage": long["report_year"].map(filing_vintage),
        "x_report_year": long["report_year"].astype(int).astype(str),
    })
    return out.sort_values(["entity", "variable", "ts_utc", "vintage"]).reset_index(drop=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description="FERC Form 714 planning areas' forecasts, from PUDL")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    args = ap.parse_args(argv)
    if args.out_dir:
        raw_dir = ip.RAW_DIR
        ip.set_out_dir(args.out_dir)
        ip.RAW_DIR = raw_dir
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{CONNECTOR}_{run_id}.log"))
    ip.RAW.open(CONNECTOR, run_id)
    results = []
    try:
        hit = ip.raw_cached(CONNECTOR, URL)
        content, rec = hit if hit else ip.fetch_raw(CONNECTOR, URL, log, headers=UA)
        log(("  raw file reused: " if hit else "  fetched: ") + URL)
        lm = rec.get("last_modified") or ""
        retrieved = rec.get("retrieved_at") or ip.utc_iso(pd.Timestamp.now(tz="UTC"))
        t = forecasts(pd.read_parquet(io.BytesIO(content)), URL, retrieved)
        if len(t) > CEILING:
            raise RuntimeError(f"{len(t)} rows would pass the ceiling of {CEILING}; nothing written")
        years = sorted(set(t["x_report_year"]))
        header = [
            "Energy Research Warehouse (ERW): FERC Form 714, Part 3, Schedule 2, each planning area's ten-year forecast of "
            "summer peak, winter peak and net energy, every filing kept (session 3758)",
            "Shape: series (docs/datastandard.md v0). entity ferc714:<PUDL's respondent id>; ts_utc the forecast year's "
            "first instant (freq P1Y); units MW (peaks) and MWh (net energy).",
            "Revisions: kept, one row per vintage. Key: entity, variable, ts_utc, vintage. vintage is FERC-714's due date "
            "for the filing (1 June of the year after its report year; PUDL gives no submission time); x_report_year is "
            "the filing's report year.",
            f"Filings: report years {years[0]} to {years[-1]}; {t['entity'].nunique()} planning areas; {len(t)} rows. "
            "Values as PUDL publishes them; a blank is no row; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/ferc714_forecasts.py; the file's Last-Modified {lm or 'not given'}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Catalyst Cooperative (PUDL), from FERC Form 714, Part 3, Schedule 2 (stable release), {URL}",
            "License: public (the owner's ruling 1 of 6 November 2026, docs/state/rulings_2026-11-06.md: a federal "
            "public-domain filing; PUDL's data are CC-BY-4.0, credited here).",
            "Method: docs/methods/ferc714_forecast_growth.md",
        ]
        ip.write_snapshot(t, NAME, header, log, cols=COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Catalyst Cooperative (PUDL), from FERC Form 714",
                                    report="FERC Form 714, Part 3, Schedule 2: planning area demand forecasts (PUDL core table, stable release)",
                                    report_url=PAGE, document_list=URL, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows, report years {years[0]} to {years[-1]}"))
        print(f"{NAME}: {len(t)} rows, {t['entity'].nunique()} planning areas, report years {years[0]} to {years[-1]}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED, no output file written:\n{tb}")
        print(f"{CONNECTOR} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
