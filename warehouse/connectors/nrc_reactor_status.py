#!/usr/bin/env python3
"""NRC Power Reactor Status: each US reactor's power level by day (session 133, approved pull).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/nrc_reactor_status.csv, from the
U.S. Nuclear Regulatory Commission's daily Power Reactor Status Report, in the pipe-delimited text files the NRC
publishes (ReportDt|Unit|Power):

    the last 365 days   https://www.nrc.gov/reading-rm/doc-collections/event-status/reactor-status/powerreactorstatusforlast365days.txt
    a whole year        https://www.nrc.gov/reading-rm/doc-collections/event-status/reactor-status/<YYYY>/<YYYY>powerstatus.txt

    entity    nrc:<unit>, the NRC's unit name lower-cased with its spaces as underscores (nrc:comanche_peak_1)
    variable  power_pct: the reactor's power as a percent of its licensed power on the report's morning (0 to 100)
    freq      P1D; ts_utc is the report date at 00:00:00Z; node is the NRC's unit name as written

    python warehouse/connectors/nrc_reactor_status.py                # the last 365 days and each year from 2019
    python warehouse/connectors/nrc_reactor_status.py --recent       # the last 365 days only

The energy mix uses this for one thing: the note on nuclear's row, saying which reactors were off or reduced.

A file the NRC's server refuses (it answered HTTP 403 and 503 to some yearly files on 6 October 2026) is logged and
skipped: the table then holds the days of the files that were read, and its header says which. Rows are merged on
(entity, variable, ts_utc). A line whose power is not a number from 0 to 100 stops the run. Nothing is filled.

Ceiling: 300,000 rows (the approved pull): about 34,500 a year, so the last 365 days and seven whole years are about
276,000. The run stops before a file that could pass the ceiling. License: public (a work of the U.S. government;
cite "U.S. Nuclear Regulatory Commission, Power Reactor Status Reports").
"""

import argparse
import datetime as dt
import io
import os
import sys
import time
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "nrc_reactor_status"
CONNECTOR = "nrc_reactor_status"
SOURCE = "nrc:power_reactor_status"
PAGE = "https://www.nrc.gov/reading-rm/doc-collections/event-status/reactor-status/index"
BASE = "https://www.nrc.gov/reading-rm/doc-collections/event-status/reactor-status/"
RECENT = BASE + "powerreactorstatusforlast365days.txt"
FIRST_YEAR = 2019
CEILING = 300_000
PER_FILE = 36_000        # a year of about 94 reactors: the run stops before a file that could pass the ceiling
UA = {"User-Agent": "Mozilla/5.0 (Energy Research Warehouse; https://github.com/SamuelEnrique/erw)"}


def parse(text, url, retrieved):
    """One of the NRC's files as the table's rows."""
    d = pd.read_csv(io.StringIO(text), sep="|", dtype=str, keep_default_na=False)
    d.columns = [c.strip() for c in d.columns]
    if list(d.columns)[:3] != ["ReportDt", "Unit", "Power"]:
        raise RuntimeError(f"{url}: columns {list(d.columns)}")
    d = d[d["Unit"].str.strip() != ""]
    day = pd.to_datetime(d["ReportDt"].str.split(" ").str[0], format="%m/%d/%Y")
    power = pd.to_numeric(d["Power"], errors="coerce")
    if power.isna().any() or ((power < 0) | (power > 100)).any():
        raise RuntimeError(f"{url}: a power that is not a number from 0 to 100: {list(d['Power'][power.isna() | (power < 0) | (power > 100)].unique()[:5])}")
    unit = d["Unit"].str.strip()
    return pd.DataFrame({
        "entity": "nrc:" + unit.str.lower().str.replace(r"[^a-z0-9]+", "_", regex=True).str.strip("_"), "variable": "power_pct",
        "ts_utc": day.dt.strftime("%Y-%m-%dT00:00:00Z"), "value": power.astype(float), "unit": "pct", "freq": "P1D", "geo": "US", "market": "", "node": unit,
        "source": SOURCE, "source_url": url, "retrieved_at": retrieved, "vintage": ""})


def main(argv=None):
    ap = argparse.ArgumentParser(description="NRC Power Reactor Status: each reactor's power by day")
    ap.add_argument("--recent", action="store_true", help="the last 365 days only")
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
        this_year = dt.datetime.now(dt.timezone.utc).year
        urls = [RECENT] + ([] if args.recent else [f"{BASE}{y}/{y}powerstatus.txt" for y in range(this_year - 1, FIRST_YEAR - 1, -1)])
        frames, read, refused = [], 0, []
        for url in urls:
            if read + PER_FILE > CEILING:
                refused.append(f"{url} (not asked: the ceiling)")
                log(f"  {url}: not asked, {read:,} rows read and another file could pass the ceiling of {CEILING:,}")
                continue
            try:
                content, rec = ip.fetch_raw(CONNECTOR, url, log, fresh=url == RECENT, headers=UA, pause=3)
            except Exception as exc:        # the NRC's server refuses some files on some days: logged, skipped, said in the header
                refused.append(f"{url} ({ip.redact(str(exc))[:60]})")
                log(f"  {url}: refused, skipped: {ip.redact(repr(exc))[:200]}")
                time.sleep(3)
                continue
            t = parse(content.decode("utf-8", errors="replace"), url, rec["retrieved_at"])
            read += len(t)
            frames.append(t)
            log(f"  {url}: {len(t):,} rows, {t['ts_utc'].min()[:10]} to {t['ts_utc'].max()[:10]}; {read:,} in all")
        if not frames:
            raise RuntimeError(f"the NRC answered none of the files: {refused}")
        s = pd.concat(frames, ignore_index=True).drop_duplicates(["entity", "variable", "ts_utc"], keep="first")
        header = [
            "Energy Research Warehouse (ERW): NRC Power Reactor Status, each US reactor's power by day (session 133)",
            "Shape: series (docs/datastandard.md v0). power_pct: the reactor's power as a percent of its licensed power on the morning of the report, as the NRC publishes it; freq P1D; ts_utc is the report date at 00:00:00Z; node is the NRC's unit name.",
            f"Files read this run: {len(frames)} of {len(urls)}. " + (f"Not read: {'; '.join(refused)}." if refused else "None was refused."),
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/nrc_reactor_status.py",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Nuclear Regulatory Commission, Power Reactor Status Reports, {PAGE}",
            f"  access: {RECENT} and {BASE}<YYYY>/<YYYY>powerstatus.txt",
            f"Rows read: {read:,} of the {CEILING:,} ceiling. Nothing is filled.",
            'License: public (a work of the U.S. government; cite "U.S. Nuclear Regulatory Commission, Power Reactor Status Reports").',
        ]
        ip.write_csv(s[ip.SERIES_COLS], NAME, header, log)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Nuclear Regulatory Commission (NRC)", report="Power Reactor Status Reports (daily)", report_url=PAGE,
                                    document_list=BASE, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(s):,} rows; {read:,} read; {len(refused)} files not read"))
        print(f"{NAME}: {len(s):,} rows, {s['ts_utc'].min()[:10]} to {s['ts_utc'].max()[:10]}, {s['entity'].nunique()} units; {read:,} rows read of {CEILING:,}; {len(refused)} files not read")
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
