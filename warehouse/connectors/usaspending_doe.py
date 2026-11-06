#!/usr/bin/env python3
"""The Department of Energy's budget as USAspending.gov reports it: each fiscal year's budgetary resources, obligations
and outlays, the obligations to date at each reporting period, and the year's award obligations by category (contracts,
grants, loans, direct payments and others) (session 2188, chain 097: the federal money behind the energy programmes,
year by year).

Energy Research Warehouse (ERW) connector. One series table from USAspending's public API (the Department of the
Treasury, Bureau of the Fiscal Service), DOE's toptier code 089:

    https://api.usaspending.gov/api/v2/agency/089/budgetary_resources/
    https://api.usaspending.gov/api/v2/agency/089/obligations_by_award_category/?fiscal_year=<year>

    usaspending_doe_obligations   entity usaspending:doe (the agency) or usaspending:doe:<category> (contracts,
               direct_payments, grants, idvs, loans, other); variable budgetary_resources, obligated and outlayed (the
               fiscal year's totals, freq P1Y), obligated_to_date (the year's obligations through a reporting period, P1M
               where the agency reports monthly, from fiscal 2022, P3M where quarterly), award_obligations (the year's
               obligations by award category, P1Y); value in USD as USAspending gives it; ts_utc the fiscal year's first
               day (1 October of the year before) or the period's month's first day; geo US; x_fiscal_year; x_period the
               fiscal period (1 October to 12 September); x_partial yes for a fiscal year not yet closed

A fiscal year with no figures (the next one, listed empty) has no row. A year's award categories need not sum to its
obligated total: obligations outside awards (salaries, for one) are in the total only. A year or period given twice, a
category not in the map or a figure that does not read stops the run. Nothing is filled.

    python warehouse/connectors/usaspending_doe.py [--offline] [--out-dir DIR]

Ceiling: 11 requests (the budgetary resources and fiscal years 2017 to 2026's award categories, each asked again unless
--offline, since USAspending revises them at the same address). api.usaspending.gov has no robots file (HTTP 404);
www.usaspending.gov's disallows only addresses with a query or .php. License: internal until a ruling (the Treasury's
terms are a standing question; see license_verdicts.csv).
"""

import argparse
import datetime as dt
import json
import os
import sys
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

CONNECTOR = "usaspending_doe"
SOURCE = "usaspending:doe_089"
HOST = "api.usaspending.gov"
PAGE = "https://www.usaspending.gov/agency/department-of-energy"
BUDGET = "https://api.usaspending.gov/api/v2/agency/089/budgetary_resources/"
AWARDS = "https://api.usaspending.gov/api/v2/agency/089/obligations_by_award_category/?fiscal_year={}"
YEARS = range(2017, 2027)
TABLE = "usaspending_doe_obligations"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
CATEGORIES = {"contracts", "direct_payments", "grants", "idvs", "loans", "other"}
X_COLS = ["x_fiscal_year", "x_period", "x_partial"]


def fy_start(fy):
    return f"{fy - 1}-10-01T00:00:00Z"


def period_month(fy, p):
    m = (p + 8) % 12 + 1  # period 1 is October
    return f"{fy - 1 if m >= 10 else fy}-{m:02d}-01T00:00:00Z"


def usd(x, where):
    try:
        return float(x)
    except (TypeError, ValueError):
        raise RuntimeError(f"{where}: a figure that does not read: {x!r}")


def parse_budget(d, base, today_fy):
    out, seen = [], set()
    if d.get("toptier_code") != "089":
        raise RuntimeError(f"not DOE's record: {d.get('toptier_code')!r}")
    for y in d["agency_data_by_year"]:
        fy = int(y["fiscal_year"])
        if fy in seen:
            raise RuntimeError(f"fiscal year {fy} given twice")
        seen.add(fy)
        if y["agency_budgetary_resources"] is None and y["agency_total_obligated"] is None:
            continue
        partial = "yes" if fy >= today_fy else ""
        row = dict(base, entity="usaspending:doe", unit="USD", geo="US", market="", node="Department of Energy", x_fiscal_year=str(fy), x_partial=partial)
        for var, key in [("budgetary_resources", "agency_budgetary_resources"), ("obligated", "agency_total_obligated"), ("outlayed", "agency_total_outlayed")]:
            out.append(dict(row, variable=var, ts_utc=fy_start(fy), value=usd(y[key], f"{fy} {key}"), freq="P1Y", x_period=""))
        periods = [int(p["period"]) for p in y["agency_obligation_by_period"]]
        if len(set(periods)) != len(periods):
            raise RuntimeError(f"fiscal year {fy}: a period given twice")
        quarterly = all(p % 3 == 0 for p in periods)
        for p in y["agency_obligation_by_period"]:
            out.append(dict(row, variable="obligated_to_date", ts_utc=period_month(fy, int(p["period"])), value=usd(p["obligated"], f"{fy} period {p['period']}"),
                            freq="P3M" if quarterly else "P1M", x_period=str(int(p["period"]))))
    return out


def parse_awards(d, fy, base, today_fy):
    out = []
    cats = [r["category"] for r in d["results"]]
    if len(set(cats)) != len(cats) or set(cats) - CATEGORIES:
        raise RuntimeError(f"fiscal year {fy}: categories not as read: {cats}")
    for r in d["results"]:
        out.append(dict(base, entity=f"usaspending:doe:{r['category']}", variable="award_obligations", ts_utc=fy_start(fy),
                        value=usd(r["aggregated_amount"], f"{fy} {r['category']}"), unit="USD", freq="P1Y", geo="US", market="",
                        node=f"Department of Energy: {r['category']}", x_fiscal_year=str(fy), x_period="", x_partial="yes" if fy >= today_fy else ""))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="USAspending.gov: the Department of Energy's budget and obligations, a fiscal year")
    ap.add_argument("--offline", action="store_true", help="the saved files only, no request")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    args = ap.parse_args(argv)
    if args.out_dir:
        raw_dir = ip.RAW_DIR
        ip.set_out_dir(args.out_dir)
        ip.RAW_DIR = raw_dir
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    now = dt.datetime.now(dt.timezone.utc)
    run_id = now.strftime("%Y%m%dT%H%M%SZ")
    today_fy = now.year + (1 if now.month >= 10 else 0)
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{CONNECTOR}_{run_id}.log"))
    ip.RAW.open(CONNECTOR, run_id)
    results = []
    try:
        if ip.paused(CONNECTOR) or ip.paused_host(HOST):
            raise RuntimeError(f"{HOST} is paused (warehouse/metadata/paused_sources.csv): no request made")
        content, rec = ip.fetch_raw(CONNECTOR, BUDGET, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=120, pause=1)
        base = dict(source=SOURCE, source_url=BUDGET, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
        rows = parse_budget(json.loads(content), base, today_fy)
        for fy in YEARS:
            url = AWARDS.format(fy)
            content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=120, pause=1)
            rows += parse_awards(json.loads(content), fy, dict(source=SOURCE, source_url=url, retrieved_at=rec.get("retrieved_at") or "",
                                                               vintage=ip.vintage_of(rec)), today_fy)
        s = pd.DataFrame(rows)
        if s.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("a key given twice")
        cols = ip.SERIES_COLS + X_COLS
        s = s[cols].sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)
        fys = sorted(s.x_fiscal_year.astype(int).unique())
        head = [
            f"Energy Research Warehouse (ERW): USAspending.gov, the Department of Energy's budgetary resources, obligations and outlays, "
            f"fiscal years {fys[0]} to {fys[-1]}, and its award obligations by category (session 2188)",
            "Shape: series (docs/datastandard.md v0). entity usaspending:doe or usaspending:doe:<award category>; variable budgetary_resources, "
            "obligated, outlayed (P1Y), obligated_to_date (through a fiscal period: P1M from fiscal 2022, P3M before), award_obligations (P1Y); "
            "unit USD; ts_utc the fiscal year's first day (1 October) or the period's month; x_fiscal_year; x_period (1 is October); x_partial "
            "yes for a fiscal year not yet closed.",
            "Award categories need not sum to the year's obligated total (obligations outside awards are in the total only). A fiscal year "
            "with no figures has no row. Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/usaspending_doe.py; the budgetary resources retrieved {base['retrieved_at']}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Department of the Treasury, Bureau of the Fiscal Service, USAspending.gov, Department of Energy (toptier 089), {PAGE}",
            f"  access: {BUDGET} and {AWARDS.format('<year>')}",
            "License: internal until a ruling (the Treasury's terms are a standing question; see license_verdicts.csv). Cite USAspending.gov.",
        ]
        ip.write_snapshot(s, TABLE, head, log, cols)
        results.append(dict(table=TABLE, market="all", status="ok", detail=f"{len(s)} rows"))
        print(f"{TABLE}: {len(s):,} rows, fiscal years {fys[0]} to {fys[-1]}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{TABLE} FAILED, no output file written:\n{tb}")
        print(f"{TABLE} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=TABLE, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Department of the Treasury, Bureau of the Fiscal Service (USAspending.gov)",
                                    report="USAspending.gov: Department of Energy, budgetary resources and obligations by award category",
                                    report_url=PAGE, document_list=PAGE, license="internal", tables=[TABLE])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
