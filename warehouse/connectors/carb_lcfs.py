#!/usr/bin/env python3
"""California's Low Carbon Fuel Standard credit price, weekly, from the Air Resources Board (session 132, approved pull).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/carb_lcfs_credit_prices.csv, from the
workbook the California Air Resources Board (CARB) publishes every Tuesday with its Weekly LCFS Credit Transfer
Activity Report (https://ww2.arb.ca.gov/resources/documents/weekly-lcfs-credit-transfer-activity-reports), sheet
"Weekly Average Credit Price", from the week of 2019-01-07. The workbook's address changes each week (its name carries
the date), so the connector reads the page and follows the one .xlsx link on it. Entity carb:lcfs_credit; a week is
Monday to Sunday and sits at 00:00:00Z of its Monday. Variables:

    credit_price_weekly_avg         CARB's volume-weighted average price of all non-zero transfers, USD per credit
                                    (one credit is one metric ton of CO2 equivalent)
    credit_price_type1_weekly_avg   the same for Type 1 transfers (executed within 10 days of the agreement)
    credit_volume                   credits transferred in all non-zero transfers (t CO2e)

    python warehouse/connectors/carb_lcfs.py [--out-dir DIR]

A week CARB lists with no value for a measure is not written for that measure. Nothing is filled. The table is written
only if its newest week is within 28 days.

License: public. California's Conditions of Use (https://www.ca.gov/use/): "In general, information presented on this
website, unless otherwise indicated, is considered in the public domain. It may be distributed or copied as permitted
by law." The workbook carries no other notice. Credit: California Air Resources Board. Ceiling: session 132's
1,500,000 rows in all; this pull reads about 550 (the workbook's weekly sheet; its transaction log is not read).
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

CONNECTOR = "carb_lcfs"
NAME = "carb_lcfs_credit_prices"
START = "2019-01-07"
STALE_DAYS = 28
PAGE = "https://ww2.arb.ca.gov/resources/documents/weekly-lcfs-credit-transfer-activity-reports"
SHEET = "Weekly Average Credit Price"
UA = {"User-Agent": "Mozilla/5.0 (Energy Research Warehouse; https://github.com/SamuelEnrique/erw)"}
COLUMNS = {"Weekly Average Credit Price ($)": ("credit_price_weekly_avg", "USD/tCO2"),
           "Type 1 Transfer Weekly Average Credit Price ($)": ("credit_price_type1_weekly_avg", "USD/tCO2"),
           "Total Volume (MT)": ("credit_volume", "tCO2")}
SOURCE_ENTRY = dict(source="carb:lcfs_weekly_credit_price", publisher="California Air Resources Board (CARB)",
                    report="Weekly LCFS Credit Transfer Activity Report, weekly average credit price", report_url=PAGE, document_list=PAGE, license="public", tables=[NAME])


def workbook_url(page_html):
    """The one weekly workbook the page links to."""
    links = sorted(set(re.findall(r'href="([^"]+\.xlsx)"', page_html)))
    weekly = [u for u in links if "weekly" in u.lower()]
    if len(weekly) != 1:
        raise RuntimeError(f"CARB's page links to {len(weekly)} weekly workbooks, expected one: {weekly[:3]}")
    return requests.compat.urljoin(PAGE, weekly[0])


def parse(content, url, retrieved):
    """The weekly sheet as the table's rows, the number of cells with no value from START on, and the weeks read."""
    df = pd.read_excel(io.BytesIO(content), sheet_name=SHEET, header=0)
    df.columns = [" ".join(str(c).split()) for c in df.columns]
    if "Week Of" not in df.columns or not set(COLUMNS) <= set(df.columns):
        raise RuntimeError(f"CARB's sheet has columns {list(df.columns)[:10]}")
    df = df[pd.to_datetime(df["Week Of"], errors="coerce").notna()].copy()
    df["week"] = pd.to_datetime(df["Week Of"])
    # CARB lists one week by its Tuesday (2021-09-07, the day after Labor Day): a date is kept as CARB writes it, and the
    # sheet is refused only when its weeks are not one a week
    gaps = df["week"].sort_values().diff().dt.days.dropna()
    if not df["week"].is_unique or ((gaps < 6) | (gaps > 8)).any():
        raise RuntimeError("CARB's sheet does not list one row a week")
    df = df[df["week"] >= pd.Timestamp(START)]
    rows, empty = [], 0
    for col, (variable, unit) in COLUMNS.items():
        v = pd.to_numeric(df[col], errors="coerce")
        bad = df[v.isna() & df[col].notna() & (df[col].astype(str).str.strip() != "")]
        if len(bad):
            raise RuntimeError(f"{col}: values that are not numbers {list(bad[col].astype(str).unique()[:5])}")
        empty += int(v.isna().sum())
        for week, value in zip(df["week"][v.notna()], v[v.notna()]):
            rows.append(dict(entity="carb:lcfs_credit", variable=variable, ts_utc=week.strftime("%Y-%m-%dT00:00:00Z"), value=float(value), unit=unit, freq="P1W",
                             geo="US-CA", market="", node="LCFS credit", source=SOURCE_ENTRY["source"], source_url=url, retrieved_at=retrieved, vintage=""))
    return pd.DataFrame(rows, columns=ip.SERIES_COLS), empty, len(df)


def build(run_id, log):
    page, _ = ip.fetch_raw(CONNECTOR, PAGE, log, fresh=True, headers=UA, pause=1)
    url = workbook_url(page.decode("utf-8", errors="replace"))
    content, rec = ip.fetch_raw(CONNECTOR, url, log, headers=UA)
    table, empty, weeks = parse(content, url, rec["retrieved_at"])
    age = (pd.Timestamp.now(tz="UTC") - pd.Timestamp(table["ts_utc"].max())).days
    if age > STALE_DAYS:
        raise RuntimeError(f"the newest week CARB holds is {table['ts_utc'].max()[:10]}, {age} days old (limit {STALE_DAYS})")
    header = [
        "Energy Research Warehouse (ERW): California's Low Carbon Fuel Standard credit price, weekly from 2019, as the Air Resources Board publishes it (session 132)",
        "Shape: series (docs/datastandard.md v0). credit_price_weekly_avg and credit_price_type1_weekly_avg: CARB's volume-weighted average price of the week's non-zero credit transfers (all, and Type 1), USD per credit, one credit being one metric ton of CO2 equivalent; credit_volume: the credits transferred. A week is Monday to Sunday; ts_utc is its Monday at 00:00:00Z; freq P1W.",
        f"Retrieved: {run_id} (UTC) by warehouse/connectors/carb_lcfs.py",
        f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
        f"Source: {SOURCE_ENTRY['source']} California Air Resources Board, {SOURCE_ENTRY['report']}, {PAGE}",
        f"  access: {url} (sheet {SHEET})",
        f"Rows read: {weeks:,} weeks. Cells CARB leaves empty, not written: {empty}. Nothing is filled.",
        "License: public. California's Conditions of Use (https://www.ca.gov/use/): information on the State's websites is, unless otherwise indicated, in the public domain. Credit: California Air Resources Board.",
    ]
    return table, header, f"{weeks} rows read"


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
