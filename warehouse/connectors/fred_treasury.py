#!/usr/bin/env python3
"""US Treasury yields at 2, 10 and 30 years, daily, from the Federal Reserve's public series on FRED (session 132, approved pull).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/fred_treasury_yields.csv: the market
yield on U.S. Treasury securities at 2-year, 10-year and 30-year constant maturity, quoted on an investment basis,
percent a year, by business day from 2019-01-01. The numbers are the Board of Governors of the Federal Reserve
System's (release H.15, Selected Interest Rates), read from FRED's graph CSV route, which needs no key:
https://fred.stlouisfed.org/graph/fredgraph.csv?id=<ID>&cosd=2019-01-01. Entities are fred:<series id>.

    python warehouse/connectors/fred_treasury.py [--out-dir DIR]

FRED writes "." (or nothing) for a business day without a value (a market holiday): such a day is not written and is
counted. Nothing is filled. The table is written only if its newest day is within 10 days.

License: public. The H.15 release is a work of the Federal Reserve Board, a U.S. government agency; FRED marks these
series "Public Domain: Citation Requested". Cite: Board of Governors of the Federal Reserve System (US), retrieved from
FRED, Federal Reserve Bank of St. Louis. Ceiling: session 132's 1,500,000 rows in all; this pull reads about 6,100.
"""

import argparse
import datetime as dt
import io
import os
import re
import sys
import traceback

import pandas as pd
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import iso_prices as ip  # noqa: E402

CONNECTOR = "fred_treasury"
NAME = "fred_treasury_yields"
START = "2019-01-01"
STALE_DAYS = 10
SERIES = {"DGS2": "2-year", "DGS10": "10-year", "DGS30": "30-year"}
RELEASE = "https://www.federalreserve.gov/releases/h15/"
SOURCE_ENTRY = dict(source="fred:h15_treasury_yields", publisher="Board of Governors of the Federal Reserve System, through FRED (Federal Reserve Bank of St. Louis)",
                    report="H.15 Selected Interest Rates: market yield on U.S. Treasury securities at constant maturity (DGS2, DGS10, DGS30)",
                    report_url=RELEASE, document_list="https://fred.stlouisfed.org/graph/fredgraph.csv", license="public", tables=[NAME])


def parse(sid, text, url, retrieved):
    """FRED's CSV of one series as the table's rows, and the number of days listed with no value."""
    df = pd.read_csv(io.StringIO(text), dtype=str, keep_default_na=False)
    if list(df.columns) != ["observation_date", sid]:
        raise RuntimeError(f"{sid}: FRED's columns are {list(df.columns)}")
    blank = df[sid].isin(["", "."])
    value = pd.to_numeric(df[sid].where(~blank), errors="coerce")
    bad = df[value.isna() & ~blank]
    if len(bad):
        raise RuntimeError(f"{sid}: values that are not numbers {list(bad[sid].unique()[:5])}")
    keep = value.notna()
    return pd.DataFrame({
        "entity": f"fred:{sid}", "variable": "yield", "ts_utc": pd.to_datetime(df.loc[keep, "observation_date"]).dt.strftime("%Y-%m-%dT00:00:00Z").values,
        "value": value[keep].values, "unit": "pct", "freq": "P1D", "geo": "US", "market": "", "node": SERIES[sid], "source": SOURCE_ENTRY["source"],
        "source_url": url, "retrieved_at": retrieved, "vintage": "",
    }), int((~keep).sum())


def build(run_id, log):
    frames, empty, rows = [], 0, 0
    for sid in SERIES:
        url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}&cosd={START}"
        content, rec = ip.fetch_raw(CONNECTOR, url, log, fresh=True, pause=1)
        t, n = parse(sid, content.decode("utf-8"), url, rec["retrieved_at"])
        rows += len(t) + n
        empty += n
        frames.append(t)
        log(f"  {sid}: {len(t)} values, {n} days with no value, newest {t['ts_utc'].max()[:10]}")
    table = pd.concat(frames, ignore_index=True)
    age = (pd.Timestamp.now(tz="UTC") - pd.Timestamp(table["ts_utc"].max())).days
    if age > STALE_DAYS:
        raise RuntimeError(f"the newest day FRED holds is {table['ts_utc'].max()[:10]}, {age} days old (limit {STALE_DAYS})")
    header = [
        "Energy Research Warehouse (ERW): US Treasury yields at 2, 10 and 30 years, constant maturity, daily from 2019 (session 132)",
        "Shape: series (docs/datastandard.md v0). yield: the market yield on U.S. Treasury securities at constant maturity, quoted on an investment basis, percent a year (unit pct); ts_utc is the business day at 00:00:00Z; freq P1D. node is the maturity.",
        f"Retrieved: {run_id} (UTC) by warehouse/connectors/fred_treasury.py",
        f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
        f"Source: {SOURCE_ENTRY['source']} {SOURCE_ENTRY['publisher']}, {SOURCE_ENTRY['report']}, {RELEASE}",
        f"  access: https://fred.stlouisfed.org/graph/fredgraph.csv?id=<series>&cosd={START} for " + ", ".join(SERIES),
        f"Rows read: {rows:,}. Business days FRED lists with no value (market holidays), not written: {empty}. Nothing is filled.",
        "License: public. A work of the Federal Reserve Board; FRED marks the series Public Domain: Citation Requested.",
    ]
    return table, header, f"{rows} rows read"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    args = ap.parse_args(argv)
    if args.out_dir:
        raw_dir = ip.RAW_DIR
        ip.set_out_dir(args.out_dir)
        ip.RAW_DIR = raw_dir
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{CONNECTOR}_{run_id}.log"))
    results = []
    try:
        ip.RAW.open(CONNECTOR, run_id)
        table, header, note = build(run_id, log)
        path = os.path.join(ip.OUT_DIR, NAME + ".csv")
        if os.path.exists(path):
            os.remove(path)     # the whole history from START is read each run, so revisions are picked up
        ip.write_csv(table[ip.SERIES_COLS], NAME, header, log)
        if not args.out_dir:
            ip.update_sources([SOURCE_ENTRY])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(table)} rows; {note}"))
        print(f"{NAME}: {len(table):,} values, newest {table['ts_utc'].max()[:10]}; {note}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED:\n{tb}")
        print(f"{CONNECTOR} FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
