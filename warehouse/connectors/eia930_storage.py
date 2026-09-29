#!/usr/bin/env python3
"""Hourly battery storage net generation from EIA-930 (fuel type BAT), for the ISOs and the US Lower 48.

Energy Research Warehouse (ERW) connector, session 31 (Part B1). Writes one series table,

    warehouse/output/eia930_all_storage.csv    net_generation_battery_mw, column ba (the partition column)

from the EIA API v2 route electricity/rto/fuel-type-data, facet fueltype BAT, hourly. The value is net generation
as EIA publishes it: positive while the batteries discharge, negative while they charge. MW.

    python warehouse/connectors/eia930_storage.py --since 2024-07-01      # the history (session 31)
    python warehouse/connectors/eia930_storage.py --days 3                # the daily run

Why a table of its own: eia930_all_generation carries the same series, but only for the rolling 30 days of that
table; this one keeps it from EIA's first BAT hour. Which BAs report BAT (checked 2026-09-29): ERCO from 2024-11-06,
ISNE from 2024-11-06, MISO from 2025-01-15, SWPP from 2026-02-04 and US48 from 2024-07-15. CISO, NYIS and PJM report
no BAT series in EIA-930 (the API returns 0 rows); CAISO's own battery output is caiso_battery_storage.

Time: EIA's hourly period is the END of the hour in UTC (see eia930.py), so ts_utc = period minus one hour.
Completeness: per UTC day, as the EIA-930 generation tables (session 16): a day is written only when every one of its
24 hours has a value; a day with a missing hour is not written and is recorded as a gap in run_status.csv. Nothing is
filled.

Paging and resume: the pull goes one BA and one calendar month at a time, 5,000 rows a page, through requests, so
every page is saved under warehouse/raw/eia930_storage/<run_id>/ with a manifest. Each finished month of a past
month is also kept as a checkpoint (warehouse/raw/eia930_storage/checkpoints/<ba>_<YYYY-MM>.csv): an interrupted
pull resumes from the months not yet checkpointed, and never restarts from zero. The current month is always
pulled again. The key comes from EIA_API_KEY and is removed from every URL, log line and row.
"""

import argparse
import datetime as dt
import os
import sys
import traceback

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import eia930  # noqa: E402  (fetch_route, to_rows, BAS, REPORT_PAGE: the EIA-930 connector's own code)
import iso_prices as ip  # noqa: E402

NAME = "eia930_all_storage"
ROUTE = "electricity/rto/fuel-type-data"
SOURCE = f"eia:{ROUTE}"
VARIABLE = "net_generation_battery_mw"
BAS = ["erco", "isne", "miso", "swpp", "us48"]   # the BAs with a BAT series (docstring)
NO_BAT = ["ciso", "nyis", "pjm"]
COLS = ip.SERIES_COLS + ["ba"]


def checkpoint_dir():
    return os.path.join(ip.RAW_DIR, "eia930_storage", "checkpoints")


def months(start, end):
    m = pd.Timestamp(start.year, start.month, 1, tz="UTC")
    while m < end:
        n = m + pd.offsets.MonthBegin(1)
        yield m, min(n, end)
        m = n


def pull_month(code, m0, m1, key, log, current):
    """Rows of one BA and month, from its checkpoint if a past month was pulled before."""
    cp = os.path.join(checkpoint_dir(), f"{code}_{m0:%Y-%m}.csv")
    if os.path.exists(cp) and not current:
        log(f"  {code} {m0:%Y-%m}: from checkpoint {os.path.relpath(cp, ip.ROOT)}")
        return pd.read_csv(cp, dtype=str, keep_default_na=False)
    respondent = eia930.BAS[code][0]
    # EIA's hourly period is the hour's end: the hours starting in [m0, m1) end in (m0, m1]
    start = (m0 + pd.Timedelta(hours=1)).strftime("%Y-%m-%dT%H")
    end = m1.strftime("%Y-%m-%dT%H")
    df = eia930.fetch_route(ROUTE, key, {"respondent": [respondent], "fueltype": ["BAT"]}, start, end, log)
    if not current:
        os.makedirs(checkpoint_dir(), exist_ok=True)
        df.astype(str).to_csv(cp, index=False)
    return df.astype(str) if len(df) else df


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW EIA-930 battery storage connector (session 31)")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--days", type=int, default=3, help="the last N complete UTC days")
    g.add_argument("--since", help="from this UTC date (YYYY-MM-DD) to the end of yesterday")
    ap.add_argument("--ba", action="append", choices=BAS)
    ap.add_argument("--out-dir")
    args = ap.parse_args(argv)
    if args.out_dir:
        ip.set_out_dir(args.out_dir)
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"eia930_storage_{run_id}.log"))
    ip.RAW.open("eia930_storage", run_id)
    end = pd.Timestamp.now(tz="UTC").normalize()  # the end of yesterday, UTC
    start = pd.Timestamp(args.since, tz="UTC") if args.since else end - pd.Timedelta(days=args.days)
    codes = args.ba or BAS
    results, gaps = [], []
    log(f"ERW eia930_storage run {run_id}; window [{ip.utc_iso(start)}, {ip.utc_iso(end)}); BAs {codes}; "
        f"no BAT series in EIA-930: {NO_BAT}")
    try:
        key = ip.load_key("EIA_API_KEY", log)
        if not key:
            raise RuntimeError("EIA_API_KEY is empty")
        frames = []
        for code in codes:
            got = []
            for m0, m1 in months(start, end):
                current = m1 >= end - pd.Timedelta(days=1) or m1 > pd.Timestamp.now(tz="UTC") - pd.Timedelta(days=40)
                df = pull_month(code, m0, m1, key, log, current)
                if len(df):
                    got.append(df)
            if not got:
                log(f"  {code}: no BAT rows in the window")
                continue
            raw = pd.concat(got, ignore_index=True)
            rows = eia930.to_rows(raw, ROUTE, {"BAT": VARIABLE}, "fueltype")
            rows = rows[(rows["interval_start"] >= start) & (rows["interval_start"] < end)]
            rows = rows.dropna(subset=["value"])
            rows = rows.drop_duplicates(["interval_start"], keep="last")
            day = rows["interval_start"].dt.floor("D")
            n = rows.groupby(day)["value"].size()
            full = set(n[n == 24].index)
            first = rows["interval_start"].min().floor("D")
            for d in pd.date_range(max(first, start), end - pd.Timedelta(days=1), freq="D", tz="UTC"):
                if d not in full:
                    have = int(n.get(d, 0))
                    gaps.append(dict(table=NAME, market=f"{code} {d:%Y-%m-%d}", status="gap",
                                     detail=f"{VARIABLE}: {have} of 24 hours; day not written"))
            keep = rows[day.isin(full)]
            respondent, geo = eia930.BAS[code]
            frames.append(pd.DataFrame({
                "entity": f"eia930:{respondent}", "variable": VARIABLE,
                "ts_utc": keep["interval_start"].dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "value": keep["value"].map(lambda v: f"{v:g}"), "unit": "MW", "freq": "PT1H", "geo": geo,
                "market": "", "node": "", "source": SOURCE, "source_url": keep["source_url"],
                "retrieved_at": keep["retrieved_at"], "vintage": "", "ba": code}))
            log(f"  {code}: {len(keep)} hours written in {len(full)} complete days; "
                f"{len(rows) - len(keep)} hours of incomplete days left out")
        if not frames:
            raise RuntimeError("no BAT rows in the window for any BA")
        s = pd.concat(frames, ignore_index=True)[COLS]
        s["value"] = pd.to_numeric(s["value"])
        report, page, doc_list = eia930.REPORTS[SOURCE]
        header = [
            "Energy Research Warehouse (ERW): EIA-930 hourly battery storage net generation (fuel type BAT) by "
            "balancing authority",
            "Shape: series (docs/datastandard.md v0), partition column ba. net_generation_battery_mw, MW, as EIA "
            "publishes it: positive while discharging, negative while charging. ts_utc is the hour's start (EIA's "
            "period, the hour's end, minus one hour).",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia930_storage.py via the EIA API v2",
            f"Run log: warehouse/output/logs/eia930_storage_{run_id}.log (every API request, key removed)",
            f"Raw files: warehouse/raw/eia930_storage/{run_id}/ (not in git; manifest.csv lists each file and URL); "
            "finished months kept in warehouse/raw/eia930_storage/checkpoints/",
            f"Source: {SOURCE} {report}, {page}",
            f"  document list: {doc_list}",
            "BAs: erco, isne, miso, swpp, us48 (their BAT series start 2024-11-06, 2024-11-06, 2025-01-15, "
            "2026-02-04 and 2024-07-15). CISO, NYIS and PJM report no BAT series in EIA-930.",
            "Completeness per UTC day (session 16 rule of the EIA-930 generation tables): a day with any hour missing "
            "is not written; each is a gap row in warehouse/metadata/run_status.csv.",
        ]
        ip.write_csv(s, NAME, header, log, cols=COLS, key=["entity", "variable", "ts_utc"])
        ip.update_sources([{"source": SOURCE, "publisher": "U.S. Energy Information Administration (EIA)",
                            "report": report, "report_url": page, "document_list": doc_list,
                            "license": "public", "tables": [NAME]}])
        results.append(dict(table=NAME, market="all", status="ok",
                            detail=f"{len(s)} hours written, {len(gaps)} incomplete days left out"))
        print(f"eia930_storage: {len(s)} hours written; {len(gaps)} incomplete BA-days left out")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED:\n{tb}")
        print(f"eia930_storage {NAME} FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    ip.write_status("eia930_storage", run_id, results + gaps)
    log.close()
    return 0 if all(r["status"] != "failed" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
