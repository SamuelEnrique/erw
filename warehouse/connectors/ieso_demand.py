#!/usr/bin/env python3
"""Ontario's hourly electricity demand, as the Independent Electricity System Operator publishes it (session 2070, chain
067: Ontario beside the U.S. grids).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/ieso_ontario_demand_hourly.csv, from the
IESO's yearly Hourly Demand Reports on its public reports site:

    https://reports-public.ieso.ca/public/Demand/PUB_Demand_<YEAR>.csv

Each file starts with lines beginning "\\\\" (the report's name, when it was created, its year), then a header
"Date,Hour,Market Demand,Ontario Demand" and one line an hour. The IESO's hour is an hour ending (1 to 24) in Eastern
Standard Time, all year (no daylight saving), so an hour's start in UTC is the date's midnight plus the hour less one,
plus five hours.

    entity      ieso:ontario
    variable    ontario_demand (the load of Ontario's consumers) or market_demand (Ontario demand plus exports), MW
    ts_utc      the hour's start in UTC, freq PT1H; geo CA-ON; node Ontario
    vintage     the file's "Created at" time, read as Eastern Standard Time and written in UTC

The prices are not taken: the Hourly Ontario Energy Price ends with April 2025 (the market renewal of 1 May 2025
replaced it with the Ontario zonal price, published only as daily and hourly files), and the ERW has no Canadian dollar
unit (a standing question for the owner). Values as the IESO publishes them; nothing is filled. A header not the one
above, an hour outside 1 to 24, an hour given twice or a value that is not a number stops the run.

    python warehouse/connectors/ieso_demand.py [--offline] [--years 2025 2026] [--out-dir DIR]

Ceiling: one request a year's file (the current year's fetched fresh each run, earlier years reused from
warehouse/raw/ieso_demand/). reports-public.ieso.ca has no robots file (HTTP 404, session 2070). License: the IESO's Terms
of Use grant "a limited, non-exclusive, non-sublicensable, non-transferrable licence to use and reproduce the Content",
provided each reproduction carries the IESO's copyright notice, which this table's header does.
"""

import argparse
import datetime as dt
import io
import os
import re
import sys
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "ieso_ontario_demand_hourly"
CONNECTOR = "ieso_demand"
SOURCE = "ieso:demand"
BASE = "https://reports-public.ieso.ca/public/Demand/"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "market", "node", "source", "source_url",
        "retrieved_at", "vintage"]
HEADER = ["Date", "Hour", "Market Demand", "Ontario Demand"]
VARIABLES = {"Market Demand": "market_demand", "Ontario Demand": "ontario_demand"}
NOTICE = ("Copyright " + chr(0xA9) + " 2004-2022 Independent Electricity System Operator, all rights reserved. This information is subject to "
          "the Terms of Use set out in the IESO's website (www.ieso.ca).")


def parse(text, url, retrieved):
    """The rows of one year's file, and its "Created at" time in UTC."""
    lines = text.replace("\r\n", "\n").split("\n")
    meta = [ln for ln in lines if ln.startswith("\\\\")]
    created = ""
    for ln in meta:
        m = re.search(r"Created at (\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2})", ln)
        if m:
            created = (dt.datetime.fromisoformat(f"{m.group(1)}T{m.group(2)}") + dt.timedelta(hours=5)).strftime("%Y-%m-%dT%H:%M:%SZ")
    body = "\n".join(ln for ln in lines if ln and not ln.startswith("\\\\"))
    t = pd.read_csv(io.StringIO(body), dtype=str, keep_default_na=False)
    if list(t.columns) != HEADER:
        raise RuntimeError(f"{url}: the header is not the one expected: {list(t.columns)}")
    hours = pd.to_numeric(t["Hour"], errors="coerce")
    if hours.isna().any() or ((hours < 1) | (hours > 24)).any():
        raise RuntimeError(f"{url}: an hour outside 1 to 24")
    day = pd.to_datetime(t["Date"], format="%Y-%m-%d", errors="coerce")
    if day.isna().any():
        raise RuntimeError(f"{url}: a date not in the IESO's form")
    start = day + pd.to_timedelta(hours - 1, unit="h") + pd.Timedelta(hours=5)
    out = []
    for col, var in VARIABLES.items():
        v = pd.to_numeric(t[col], errors="coerce")
        if v.isna().any():
            raise RuntimeError(f"{url}: {col}: a value that is not a number")
        out.append(pd.DataFrame({"entity": "ieso:ontario", "variable": var, "ts_utc": start.dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
                                 "value": v.astype(float), "unit": "MW", "freq": "PT1H", "geo": "CA-ON", "market": "",
                                 "node": "Ontario", "source": SOURCE, "source_url": url, "retrieved_at": retrieved,
                                 "vintage": created}))
    return pd.concat(out, ignore_index=True), created


def build(files):
    """files: [(text, url, retrieved)]. Returns the table and each file's creation time."""
    parts, created = [], {}
    for text, url, retrieved in files:
        t, c = parse(text, url, retrieved)
        parts.append(t)
        created[url] = c
    t = pd.concat(parts, ignore_index=True)
    twice = t[t.duplicated(["entity", "variable", "ts_utc"], keep=False)]
    if len(twice):
        raise RuntimeError(f"an hour given twice: {twice.ts_utc.head(3).tolist()}")
    return t.sort_values(["variable", "ts_utc"]).reset_index(drop=True), created


def main(argv=None):
    ap = argparse.ArgumentParser(description="The IESO's hourly Ontario demand")
    ap.add_argument("--offline", action="store_true", help="the saved files only, no request")
    this_year = dt.datetime.now(dt.timezone.utc).year
    ap.add_argument("--years", type=int, nargs="+", default=[this_year - 1, this_year])
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
        files = []
        for y in sorted(args.years):
            url = f"{BASE}PUB_Demand_{y}.csv"
            content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline,
                                        fresh=(y == this_year and not args.offline), headers=UA, timeout=120)
            files.append((content.decode("utf-8", errors="replace"), url, rec.get("retrieved_at") or ""))
        t, created = build(files)
        header = [
            f"Energy Research Warehouse (ERW): Independent Electricity System Operator (IESO), Hourly Demand Report, Ontario, {min(args.years)} to {t.ts_utc.max()[:10]} (session 2070)",
            "Shape: series (docs/datastandard.md v0). entity ieso:ontario; variables ontario_demand (Ontario's consumers) and market_demand (Ontario demand plus "
            "exports), MW; ts_utc the hour's start in UTC (the IESO's hour ending, Eastern Standard Time all year, less one hour plus five); freq PT1H; vintage the file's creation.",
            f"{len(t)} rows. The prices are not taken: the HOEP ends with April 2025, and the ERW has no Canadian dollar unit. Values as published; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/ieso_demand.py; the files created " + ", ".join(f"{u.rsplit('/', 1)[1]} {c}" for u, c in created.items()),
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Independent Electricity System Operator, Hourly Demand Report, {BASE}",
            f"  access: {BASE}PUB_Demand_<YEAR>.csv",
            f"License: the IESO's Terms of Use, a licence to use and reproduce with its notice: {NOTICE}",
        ]
        ip.write_csv(t, NAME, header, log, cols=COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Independent Electricity System Operator (IESO), Ontario",
                                    report="Hourly Demand Report (PUB_Demand)", report_url="https://reports-public.ieso.ca/public/Demand/",
                                    document_list=f"{BASE}PUB_Demand_<YEAR>.csv", license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows, {t.ts_utc.min()} to {t.ts_utc.max()}")
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
