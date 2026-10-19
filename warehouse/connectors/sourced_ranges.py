#!/usr/bin/env python3
"""Published low and high cases for the battery's assumptions (session 306): the table battery_sourced_ranges.

The chain prompt names the table sourced_ranges; a series table's name has three parts (docs/datastandard.md), so it is
battery_sourced_ranges, and the page's file keeps the prompt's name, site/data/sourced_ranges.json.

Energy Research Warehouse (ERW). The battery page's Sensitivity (session 296) moves each assumption between published
cases, not between numbers a session chose. This table holds those cases, one row per source, case and assumption,
each with the document and the place in it where the number stands, and when it was read.

    python warehouse/connectors/sourced_ranges.py            # read the kept workbook, write the table and the page file
    python warehouse/connectors/sourced_ranges.py --pull     # first ask NLR's data host for the workbook (one request)

The source held: the 2025 Electricity Annual Technology Baseline (ATB) of the National Laboratory of the Rockies (NLR,
formerly NREL), its workbook 2025_v1_Workbook_08-27-2026.xlsx, sheets "Utility-Scale Battery - R&D" (the R&D cost
drivers without tax credits, the ATB's default) and nothing else. Its three cases are its own: Advanced, Moderate and
Conservative; on cost Advanced is the low case and Conservative the high one. Every value is the ATB's for the year 2025,
in the workbook's 2023 dollars. Where the workbook gives one value for all three cases (efficiency, the rates), each
case has its row with that value. Nothing is filled: an assumption the workbook does not state (cycles, degradation,
fade, augmentation, the debt share of a battery) has no row, and the run says so.

Lazard's LCOE+ (June 2025) is read only from a copy already held in warehouse/raw; none is held (session 306), so no row
of it is written and no request is made.

Terms (read 19 October 2026, kept in warehouse/raw/nlr_atb/terms/): the ATB's disclaimer agreement (data for reference,
as is, no warranty) and NLR's data terms (https://www.nlr.gov/disclaimer: use and copy without fee, with the notice kept
and DOE/NLR credited). License: public, with that credit.

Shape: series. entity nlr_atb_2025:utility_battery[_<d>h]:<case>; variable the assumption; ts_utc 2025-01-01, freq P1Y;
x_case low, mid or high on the cost scale; x_published_case the ATB's name; x_duration_h; x_document; x_page the sheet
and row; x_dollar_year. Also site/data/sourced_ranges.json, the same rows for the page.
"""

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "battery_sourced_ranges"
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
RAW = os.path.join(ROOT, "warehouse", "raw", "nlr_atb")
FILE = "2025_v1_Workbook_08-27-2026.xlsx"
URL = "https://data.openei.org/files/8759/2025_v1_Workbook_08-27-2026.xlsx"
PAGE = "https://atb.nlr.gov/electricity/2025/data"
SHEET = "Utility-Scale Battery - R&D"
SOURCE = "nlr:atb-2025-v1"
DOCUMENT = ("National Laboratory of the Rockies (NLR), 2025 Electricity Annual Technology Baseline (ATB), workbook "
            "2025_v1_Workbook_08-27-2026.xlsx, sheet Utility-Scale Battery - R&D (battery costs from Cole, Ramasamy and "
            "Olmez Turan, Cost Projections for Utility-Scale Battery Storage: 2025 Update, NREL/TP-6A40-93281)")
JSON_OUT = os.path.join(ROOT, "site", "data", "sourced_ranges.json")
YEAR = 2025
DOLLAR_YEAR = 2023
CASE = {"Advanced": "low", "Moderate": "mid", "Conservative": "high"}
# the workbook's label (column D of the block's first row) -> (variable, unit)
METRICS = {
    "CAPEX ($/kW)": ("capex", "USD/kW"),
    "Overnight Capital Cost ($/kW)": ("overnight_capital_cost", "USD/kW"),
    "Fixed Operation and Maintenance Expenses ($/kW-yr)": ("fixed_om", "USD/kW-year"),
    "Grid Connection Costs (GCC) ($/kW)": ("grid_connection_cost", "USD/kW"),
    "Round-Trip Efficiency": ("round_trip_efficiency", "ratio"),
}
RATES = {  # column E label of the rows of the financial assumptions -> (variable, unit)
    "Interest Rate Nominal": ("interest_rate_nominal", "ratio"),
    "Rate of Return on Equity Nominal": ("return_on_equity_nominal", "ratio"),
}
COMPONENTS = {"Battery Energy Capital Cost ($/kWh)": ("energy_capital_cost", "USD/kWh"),
              "Battery Power Capital Cost ($/kW)": ("power_capital_cost", "USD/kW")}
NOT_STATED = ["cycles a year or a day", "degradation", "capacity fade", "augmentation cost",
              "the debt share of a utility-scale battery (the WACC sheet gives none for it)"]


def pull(log):
    """One request: the workbook, kept as it came."""
    import requests
    os.makedirs(RAW, exist_ok=True)
    r = requests.get(URL, headers={"User-Agent": "ERW research (Energy Research Warehouse)"}, timeout=300)
    r.raise_for_status()
    with open(os.path.join(RAW, FILE), "wb") as f:
        f.write(r.content)
    log(f"pulled {URL}: {len(r.content):,} bytes")


def read(path):
    """[(variable, unit, duration_h or None, published case, value, row number)] for the year YEAR."""
    import openpyxl
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    rows = list(wb[SHEET].iter_rows(values_only=True))
    out, years, metric, component, life = [], {}, None, None, None
    for i, r in enumerate(rows, 1):
        r = list(r) + [None] * 30
        ints = {j: v for j, v in enumerate(r) if isinstance(v, int) and 2020 <= v <= 2060}
        if len(ints) >= 10:  # a row of years: the columns of the block that follows
            years = {v: j for j, v in ints.items()}
            continue
        d, e, g = r[3], r[4], r[6]
        if isinstance(d, str) and "technical life" in d:
            m = re.search(r"(\d+)-year technical life", d)
            life = (int(m.group(1)), i) if m else life
        if isinstance(d, str) and d.strip():
            metric = METRICS.get(d.strip())
        if isinstance(e, str) and e.strip() in COMPONENTS:
            component = COMPONENTS[e.strip()]
            continue
        if component and isinstance(e, str) and e in CASE and YEAR in years:
            out.append((component[0], component[1], None, e, float(r[years[YEAR]]), i))
            if e == "Conservative":
                component = None
            continue
        if isinstance(e, str) and e.strip() in RATES and g in CASE and YEAR in years:
            v, u = RATES[e.strip()]
            out.append((v, u, None, g, float(r[years[YEAR]]), i))
            continue
        if metric and isinstance(e, str) and e.startswith("Utility-Scale Battery Storage - ") and g in CASE and YEAR in years:
            dur = int(re.search(r"(\d+)Hr", e).group(1))
            out.append((metric[0], metric[1], dur, g, float(r[years[YEAR]]), i))
    if life:
        for c in CASE:
            out.append(("technical_life", "year", None, c, float(life[0]), life[1]))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="Published low and high cases of the battery's assumptions (session 306)")
    ap.add_argument("--pull", action="store_true", help="ask for the workbook first (one request)")
    a = ap.parse_args(argv)
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{NAME}_{run_id}.log"))
    results = []
    try:
        if a.pull:
            pull(log)
        path = os.path.join(RAW, FILE)
        if not os.path.exists(path):
            raise RuntimeError(f"warehouse/raw/nlr_atb/{FILE} is not on this machine; run with --pull")
        sha = hashlib.sha256(open(path, "rb").read()).hexdigest()
        kept = dt.datetime.fromtimestamp(os.path.getmtime(path), dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        got = read(path)
        if not got:
            raise RuntimeError(f"no value for {YEAR} was found on the sheet {SHEET!r}")
        recs = []
        for var, unit, dur, case, val, row in got:
            ent = f"nlr_atb_2025:utility_battery{'_%dh' % dur if dur else ''}:{case.lower()}"
            recs.append(dict(entity=ent, variable=var, ts_utc=f"{YEAR}-01-01T00:00:00Z", value=round(val, 6), unit=unit,
                             freq="P1Y", geo="US", market="", node="", source=SOURCE, source_url=URL, retrieved_at=kept,
                             vintage="2026-08-27T00:00:00Z", x_case=CASE[case], x_published_case=case,
                             x_duration_h="" if dur is None else str(dur), x_document=DOCUMENT,
                             x_page=f"sheet {SHEET}, row {row}, column {YEAR}" if var != "technical_life"
                             else f"sheet {SHEET}, row {row} (\"For 15-year technical life\")",
                             x_dollar_year=str(DOLLAR_YEAR) if unit.startswith("USD") else ""))
        df = pd.DataFrame(recs)
        if df.duplicated(ip.SERIES_KEY).any():
            raise RuntimeError("an (entity, variable, ts_utc) is given twice")
        cols = ip.SERIES_COLS + ["x_case", "x_published_case", "x_duration_h", "x_document", "x_page", "x_dollar_year"]
        header = [
            "Energy Research Warehouse (ERW): published low and high cases of the battery's assumptions, one row per source, case and assumption (session 306)",
            "Shape: series (docs/datastandard.md v0). entity <source>:<technology>:<case>; ts_utc the year the value is for; x_case low, mid or high on the cost scale; "
            "x_page where the number stands in the document. Nothing is filled: an assumption a source does not state has no row.",
            f"Source: {DOCUMENT}; {URL} (listed on {PAGE}); SHA-256 {sha}; kept in warehouse/raw/nlr_atb/{FILE}",
            f"Values: the ATB's for {YEAR}, in {DOLLAR_YEAR} dollars where a value is in dollars; cases Advanced (low cost), Moderate, Conservative (high cost)",
            "Vintage: the workbook's date, 27 August 2026 (2025 v1). Not stated by this source, so not written: " + "; ".join(NOT_STATED),
            "Lazard LCOE+ (June 2025): no copy is held in warehouse/raw, so none of its cases is written (no request was made)",
            "License: public. NLR's data terms (https://www.nlr.gov/disclaimer, read 2026-10-07) and the ATB's disclaimer agreement "
            "(https://atb.nlr.gov/electricity/2025/disclaimer, read 2026-10-19): use and copy without fee, the notice kept, DOE/NLR credited, as is",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/{NAME}.py (the workbook kept at {kept})",
            f"Run log: warehouse/output/logs/{NAME}_{run_id}.log",
        ]
        ip.write_snapshot(df[cols], NAME, header, log, cols)
        ip.update_sources([dict(source=SOURCE, publisher="National Laboratory of the Rockies (NLR, formerly NREL)",
                                report="2025 Electricity Annual Technology Baseline (ATB), workbook 2025_v1_Workbook_08-27-2026.xlsx",
                                report_url=PAGE, document_list=URL, license="public", tables=[NAME])])
        os.makedirs(os.path.dirname(JSON_OUT), exist_ok=True)
        with open(JSON_OUT, "w", encoding="utf-8", newline="\n") as f:
            json.dump({"about": "Published low and high cases of the battery's assumptions, from warehouse/output/battery_sourced_ranges.csv "
                                "(warehouse/connectors/sourced_ranges.py, session 306). One row per source, case and assumption; "
                                "an assumption a source does not state has no row.",
                       "built": run_id, "not_stated": {SOURCE: NOT_STATED},
                       "sources": [{"source": SOURCE, "document": DOCUMENT, "url": URL, "sha256": sha, "retrieved_at": kept,
                                    "dollar_year": DOLLAR_YEAR, "year": YEAR, "license": "public, DOE/NLR credited"}],
                       "rows": [{"assumption": r["variable"], "unit": r["unit"], "duration_h": int(r["x_duration_h"]) if r["x_duration_h"] else None,
                                 "case": r["x_case"], "published_case": r["x_published_case"], "value": r["value"],
                                 "source": SOURCE, "page": r["x_page"]} for r in recs]}, f, indent=1)
            f.write("\n")
        log(f"wrote {len(df)} rows and {os.path.relpath(JSON_OUT, ROOT)}")
        print(f"{NAME}: {len(df)} rows, {df['variable'].nunique()} assumptions, {df['entity'].nunique()} entities; "
              f"not stated: {len(NOT_STATED)}")
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(df)} rows"))
    except Exception as exc:
        log(f"FAILED, no output file written: {type(exc).__name__}: {exc}")
        print(f"{NAME} FAILED, no output file written: {type(exc).__name__}: {exc}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=str(exc)[:300]))
    ip.write_status(NAME, run_id, results)
    log.close()
    return 1 if any(r["status"] == "failed" for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
