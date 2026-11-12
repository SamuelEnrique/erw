#!/usr/bin/env python3
"""How each planning area's forecast of a year moved from one FERC-714 filing to the next (session 3758, chain 211).

Energy Research Warehouse (ERW). One derived table, ferc714_forecast_growth, from ferc714_planning_area_forecasts
(FERC Form 714, Part 3, Schedule 2, every filing kept; warehouse/connectors/ferc714_forecasts.py). Method:
docs/methods/ferc714_forecast_growth.md. No request is made.

    python warehouse/derived/ferc714_forecast_growth.py                 # the table, under the data lock
    python warehouse/derived/ferc714_forecast_growth.py --out-dir DIR   # a trial: the table under DIR

For each planning area (entity ferc714:<id>), filing (vintage, with x_report_year) and forecast year (ts_utc): the
change of the area's forecast of that same year against the filing one year and two years before, for the summer peak,
the winter peak and net energy, in the unit filed and in percent of the earlier filing's figure:

    summer_peak_revision_1y_mw, summer_peak_revision_1y_pct, summer_peak_revision_2y_mw, summer_peak_revision_2y_pct
    winter_peak_revision_...    (the same four)
    net_energy_revision_1y_mwh, net_energy_revision_1y_pct, net_energy_revision_2y_mwh, net_energy_revision_2y_pct

A row is written only where both filings hold the figure; a percent only where the earlier figure is above zero.
Nothing is filled, smoothed or adjusted for weather; a respondent that changed what its planning area covers between
filings moves its forecast with it, and the method note says so. The table keeps every filing (decision 77).
"""

import argparse
import datetime as dt
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "connectors"))
import iso_prices as ip  # noqa: E402

NAME = "ferc714_forecast_growth"
INPUT = "ferc714_planning_area_forecasts"
SOURCE = "erw:ferc714_forecast_growth"
METHOD_URL = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/ferc714_forecast_growth.md"
BASES = {"summer_peak_forecast_mw": ("summer_peak", "mw", "MW"), "winter_peak_forecast_mw": ("winter_peak", "mw", "MW"),
         "net_energy_forecast_mwh": ("net_energy", "mwh", "MWh")}
COLS = ip.SERIES_COLS + ["x_report_year"]


def revisions(f):
    """The revision rows from the forecasts table's rows (entity, variable, ts_utc, value, x_report_year)."""
    f = f[f["variable"].isin(BASES)].copy()
    f["value"] = pd.to_numeric(f["value"], errors="coerce")
    f = f.dropna(subset=["value"])
    f["ry"] = f["x_report_year"].astype(int)
    if f.duplicated(["entity", "variable", "ts_utc", "ry"]).any():
        raise RuntimeError(f"{INPUT}: a (planning area, variable, forecast year, filing) given twice")
    out = []
    for lag in (1, 2):
        before = f[["entity", "variable", "ts_utc", "ry", "value"]].copy()
        before["ry"] = before["ry"] + lag
        j = f.merge(before, on=["entity", "variable", "ts_utc", "ry"], suffixes=("", "_before"))
        for var, (stem, u, unit) in BASES.items():
            part = j[j["variable"] == var]
            if part.empty:
                continue
            diff = part["value"] - part["value_before"]
            out.append(pd.DataFrame({"entity": part["entity"], "variable": f"{stem}_revision_{lag}y_{u}", "ts_utc": part["ts_utc"],
                                     "value": diff.round(3), "unit": unit, "ry": part["ry"]}))
            pos = part[part["value_before"] > 0]
            pct = 100 * (pos["value"] - pos["value_before"]) / pos["value_before"]
            out.append(pd.DataFrame({"entity": pos["entity"], "variable": f"{stem}_revision_{lag}y_pct", "ts_utc": pos["ts_utc"],
                                     "value": pct.round(3), "unit": "pct", "ry": pos["ry"]}))
    r = pd.concat(out, ignore_index=True)
    return r


def build(f, retrieved):
    r = revisions(f)
    t = pd.DataFrame({
        "entity": r["entity"], "variable": r["variable"], "ts_utc": r["ts_utc"], "value": r["value"], "unit": r["unit"],
        "freq": "P1Y", "geo": "US", "market": "", "node": "", "source": SOURCE, "source_url": METHOD_URL,
        "retrieved_at": retrieved, "vintage": r["ry"].map(lambda y: f"{int(y) + 1}-06-01T00:00:00Z"),
        "x_report_year": r["ry"].astype(int).astype(str)})
    return t.sort_values(["entity", "variable", "ts_utc", "vintage"]).reset_index(drop=True)[COLS]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    ap.add_argument("--in-dir", help="where the forecasts table is read (default warehouse/output)")
    a = ap.parse_args(argv)
    src = os.path.join(a.in_dir or ip.OUT_DIR, INPUT + ".csv")
    if a.out_dir:
        ip.set_out_dir(a.out_dir)
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{NAME}_{run_id}.log"))
    if not os.path.exists(src):
        print(f"{NAME} FAILED: {INPUT} is not on this machine ({src}); nothing written", file=sys.stderr)
        return 1
    f = pd.read_csv(src, comment="#", dtype=str, keep_default_na=False)
    retrieved = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
    t = build(f, retrieved)
    years = sorted(set(t["x_report_year"]))
    target = os.path.join(ip.OUT_DIR, NAME + ".csv")
    if os.path.exists(target):
        ip._require_lock(target, f"rebuilding {NAME}")
        os.remove(target)  # rebuilt whole each run from the whole input
    ip.write_csv(t, NAME, [
        "Energy Research Warehouse (ERW): how each planning area's FERC-714 forecast of a year moved from one filing to the next, "
        "summer peak, winter peak and net energy (session 3758)",
        "Shape: series (docs/datastandard.md v0). entity ferc714:<PUDL's respondent id>; ts_utc the forecast year's first instant (freq P1Y); "
        "<summer_peak|winter_peak>_revision_<1y|2y>_mw and net_energy_revision_<1y|2y>_mwh: this filing's figure less the figure for the "
        "same year in the filing one or two years before; _pct: that change in percent of the earlier figure (written only where it is above zero).",
        "Revisions: kept, one row per vintage. Key: entity, variable, ts_utc, vintage. vintage is the later filing's due date (1 June of "
        "the year after its report year); x_report_year is its report year.",
        f"Filings compared: report years {years[0]} to {years[-1]} against the one and two before; {t['entity'].nunique()} planning areas; "
        "a row only where both filings hold the figure; nothing filled.",
        f"Derived from: {INPUT}",
        f"Retrieved: {run_id} (UTC) by warehouse/derived/ferc714_forecast_growth.py", f"Run log: warehouse/output/logs/{NAME}_{run_id}.log",
        f"Source: {SOURCE} Energy Research Warehouse (ERW), derived from {INPUT} (Catalyst Cooperative's PUDL, from FERC Form 714, "
        "Part 3, Schedule 2)",
        "License: public (its one input is public: the owner's ruling 1 of 6 November 2026)",
        "Method: docs/methods/ferc714_forecast_growth.md",
    ], log, cols=COLS, key=["entity", "variable", "ts_utc", "vintage"])
    if not a.out_dir:
        ip.update_sources([dict(source=SOURCE, publisher="Energy Research Warehouse (ERW), derived",
                                report="FERC-714 forecast revisions by planning area, filing and forecast year (docs/methods/ferc714_forecast_growth.md)",
                                report_url=METHOD_URL, document_list="docs/methods/ferc714_forecast_growth.md", license="public", tables=[NAME])])
    log.close()
    print(f"{NAME}: {len(t):,} rows, {t['entity'].nunique()} planning areas, filings {years[0]} to {years[-1]}"
          + (f" (trial, under {a.out_dir})" if a.out_dir else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
