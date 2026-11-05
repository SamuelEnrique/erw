#!/usr/bin/env python3
"""Alberta's hourly internal load (AIL), as the Alberta Electric System Operator publishes it beside its pool price
(session 2071, chain 067: Alberta beside the U.S. grids).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/aeso_alberta_load_hourly.csv, from the
AESO's Historical Pool Price report on its Energy Trading System site, asked as CSV for a range of days:

    http://ets.aeso.ca/ets_web/ip/Market/Reports/HistoricalPoolPriceReportServlet?beginDate=MMDDYYYY&endDate=MMDDYYYY&contentType=csv

The report's lines after its title are "Date (HE),Price ($),30Ravg ($),AIL Demand (MW)", one an hour; its end date is
not included. Its hour is an hour ending in Alberta's local time with daylight saving: the spring's skipped hour has no line (the
day has 23), and the autumn's repeated hour is written "02" then "02*" (the day has 25). So an hour is placed by its order
within its local day: the day's local midnight in UTC (through America/Edmonton) plus one hour a line before it.

    entity      aeso:alberta
    variable    ail_demand, Alberta internal load, MW
    ts_utc      the hour's start in UTC, freq PT1H; geo CA-AB; node Alberta

The pool price and its 30-day average are not taken: the ERW has no Canadian dollar unit (a standing question for the
owner). An hour the report lists with "-" (not yet reached) is no row. Values as the AESO publishes them; nothing is
filled. A header not the one above, a time not in the AESO's form, an hour given twice or a value that is not a number
stops the run.

    python warehouse/connectors/aeso_load.py [--offline] [--out-dir DIR]

Ceiling: two requests, last year (1 January to 30 December: the report's end date, 31 December, is not included) and
this year to tomorrow (31 December of last year to tomorrow, the end again not included): the AESO's report is asked for at most a year at a time. ets.aeso.ca has no robots file
(HTTP 404, session 2071). License: the AESO's legal page: "The material may be used and copied for non-commercial,
personal or educational purposes, provided that the material is not modified and that copyright notices are not
deleted" (read 46; commercial use needs the AESO's written permission).
"""

import argparse
import datetime as dt
import io
import os
import re
import sys
import traceback
from zoneinfo import ZoneInfo

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "aeso_alberta_load_hourly"
CONNECTOR = "aeso_load"
SOURCE = "aeso:historical_pool_price"
REPORT = "http://ets.aeso.ca/ets_web/ip/Market/Reports/HistoricalPoolPriceReportServlet"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "market", "node", "source", "source_url",
        "retrieved_at", "vintage"]
HEADER = ["Date (HE)", "Price ($)", "30Ravg ($)", "AIL Demand (MW)"]
ZONE = ZoneInfo("America/Edmonton")
TIME_RE = re.compile(r"^(\d{2})/(\d{2})/(\d{4}) (\d{2})(\*?)$")


def url_for(begin, end):
    return f"{REPORT}?beginDate={begin:%m%d%Y}&endDate={end:%m%d%Y}&contentType=csv"


def midnight_utc(day):
    return dt.datetime(day.year, day.month, day.day, tzinfo=ZONE).astimezone(dt.timezone.utc)


def starts_utc(times):
    """The UTC start of each of the report's hours, in the report's order: a day's local midnight in UTC plus one hour a
    line before it. A day's lines must be its hours ending in order (24, or 23 on the spring day, 25 with "02*" on the
    autumn day); only the report's last day may stop short (its hours not yet reached are no lines)."""
    parsed = []
    for text in times:
        m = TIME_RE.match(text)
        if not m:
            raise RuntimeError(f"a time not in the AESO's form: {text!r}")
        day = dt.date(int(m.group(3)), int(m.group(1)), int(m.group(2)))
        parsed.append((day, int(m.group(4)), m.group(5) == "*", text))
    out, days = [], []
    for day, he, star, text in parsed:
        if not days or days[-1][0] != day:
            days.append((day, []))
        days[-1][1].append((he, star, text))
    for i, (day, rows) in enumerate(days):
        start = midnight_utc(day)
        length = int((midnight_utc(day + dt.timedelta(days=1)) - start).total_seconds() // 3600)
        expect = []
        for he in range(1, 25):
            if length == 23 and he == 2:
                continue
            expect.append((he, False))
            if length == 25 and he == 2:
                expect.append((2, True))
        got = [(he, star) for he, star, _ in rows]
        if got != expect[:len(got)] or (len(got) < len(expect) and i != len(days) - 1):
            raise RuntimeError(f"the hours of {day} are not the AESO's {length}: {[t for _, _, t in rows][:4]} ...")
        out.extend((start + dt.timedelta(hours=k)).strftime("%Y-%m-%dT%H:%M:%SZ") for k in range(len(rows)))
    return out


def parse(text, url, retrieved):
    lines = text.replace("\r\n", "\n").split("\n")
    head = next((i for i, ln in enumerate(lines) if ln.startswith("Date (HE)")), None)
    if head is None:
        raise RuntimeError(f"{url}: no header line")
    t = pd.read_csv(io.StringIO("\n".join(lines[head:])), dtype=str, keep_default_na=False)
    if list(t.columns) != HEADER:
        raise RuntimeError(f"{url}: the header is not the one expected: {list(t.columns)}")
    t = t[t["AIL Demand (MW)"].str.strip() != "-"]
    v = pd.to_numeric(t["AIL Demand (MW)"], errors="coerce")
    if v.isna().any():
        raise RuntimeError(f"{url}: a load that is not a number: {t.loc[v.isna(), 'AIL Demand (MW)'].head(3).tolist()}")
    return pd.DataFrame({"entity": "aeso:alberta", "variable": "ail_demand", "ts_utc": starts_utc(t["Date (HE)"].tolist()),
                         "value": v.astype(float).values, "unit": "MW", "freq": "PT1H", "geo": "CA-AB", "market": "",
                         "node": "Alberta", "source": SOURCE, "source_url": url, "retrieved_at": retrieved, "vintage": ""})


def build(files):
    t = pd.concat([parse(text, url, retrieved) for text, url, retrieved in files], ignore_index=True)
    twice = t[t.duplicated(["entity", "variable", "ts_utc"], keep=False)]
    if len(twice):
        raise RuntimeError(f"an hour given twice: {twice.ts_utc.head(3).tolist()}")
    return t.sort_values("ts_utc").reset_index(drop=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description="The AESO's hourly Alberta internal load")
    ap.add_argument("--offline", action="store_true", help="the saved files only, no request")
    ap.add_argument("--today", help="YYYY-MM-DD in place of today's UTC date (a rerun of saved files)")
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
        today = dt.date.fromisoformat(args.today) if args.today else dt.datetime.now(dt.timezone.utc).date()
        last = today.year - 1
        ranges = [(dt.date(last, 1, 1), dt.date(last, 12, 31), False), (dt.date(last, 12, 31), today + dt.timedelta(days=1), True)]
        files = []
        for begin, end, fresh in ranges:
            url = url_for(begin, end)
            content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, fresh=fresh and not args.offline,
                                        headers=UA, timeout=180)
            files.append((content.decode("utf-8", errors="replace"), url, rec.get("retrieved_at") or ""))
        t = build(files)
        header = [
            f"Energy Research Warehouse (ERW): Alberta Electric System Operator (AESO), Historical Pool Price report, Alberta internal load, {last} to {t.ts_utc.max()[:10]} (session 2071)",
            "Shape: series (docs/datastandard.md v0). entity aeso:alberta; variable ail_demand (Alberta internal load), MW; ts_utc the hour's start in UTC (the AESO's hour "
            "ending in Alberta's local time, read through America/Edmonton; the autumn's repeated hour \"02*\" is the standard time one); freq PT1H.",
            f"{len(t)} rows. The pool price is not taken: the ERW has no Canadian dollar unit. Hours not yet reached (\"-\") are no rows. Values as published; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/aeso_load.py",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Alberta Electric System Operator, Historical Pool Price report (Energy Trading System), {REPORT}",
            f"  access: {REPORT}?beginDate=MMDDYYYY&endDate=MMDDYYYY&contentType=csv",
            "License: the AESO's legal page: the material may be used and copied for non-commercial, personal or educational purposes, unmodified, with its copyright notices "
            "(Copyright Alberta Electric System Operator); any other use needs the AESO's written permission.",
        ]
        ip.write_csv(t, NAME, header, log, cols=COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Alberta Electric System Operator (AESO), Canada",
                                    report="Historical Pool Price report, Alberta internal load", report_url=REPORT,
                                    document_list=f"{REPORT}?beginDate=MMDDYYYY&endDate=MMDDYYYY&contentType=csv", license="public",
                                    tables=[NAME])])
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
