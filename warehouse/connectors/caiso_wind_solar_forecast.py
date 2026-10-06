#!/usr/bin/env python3
"""CAISO wind and solar: the day-ahead forecast and the actual output, hourly, by trading hub (session 133, approved pull).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/caiso_wind_solar_forecast.csv, from
CAISO's public OASIS report "Wind and Solar Forecast" (SLD_REN_FCST), asked twice a month of days: market run DAM (the
day-ahead forecast) and ACTUAL (actual generation):

    https://oasis.caiso.com/oasisapi/SingleZip?resultformat=6&queryname=SLD_REN_FCST&version=1&market_run_id=<RUN>
        &startdatetime=<UTC>&enddatetime=<UTC>

    entity    caiso:NP15, caiso:SP15, caiso:ZP26 (CAISO's trading hubs)
    variable  wind_forecast_dam_mw, wind_actual_mw, solar_forecast_dam_mw, solar_actual_mw
    value     CAISO's MW for the hour, unchanged; ts_utc is the hour's start; freq PT1H

    python warehouse/connectors/caiso_wind_solar_forecast.py                 # January 2023 to yesterday
    python warehouse/connectors/caiso_wind_solar_forecast.py --start 2026-09-01

OASIS keeps this report for about three years: a window it answers with "No data returned for the specified
selection" (its error 1000) is logged and skipped, and the table begins where CAISO's answers begin. Rows are merged
on (entity, variable, ts_utc), so a later run adds days and replaces revised hours. An hour CAISO does not list is not
written. Nothing is filled.

Ceiling: 2,000,000 rows for session 133's forecast pulls in all (CAISO and ERCOT); this pull reads about 420,000. The
run stops if the rows read would pass the ceiling. License: public (CAISO OASIS public data; cite "California ISO,
OASIS").
"""

import argparse
import datetime as dt
import io
import os
import re
import sys
import time
import traceback
import zipfile

import pandas as pd
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "caiso_wind_solar_forecast"
CONNECTOR = "caiso_wind_solar_forecast"
SOURCE = "caiso:SLD_REN_FCST"
PAGE = "https://oasis.caiso.com/mrioasis/logon.do"
API = "https://oasis.caiso.com/oasisapi/SingleZip?resultformat=6&queryname=SLD_REN_FCST&version=1&market_run_id={run}&startdatetime={a}&enddatetime={b}"
FIRST = dt.date(2023, 1, 1)
CEILING = 2_000_000
PAUSE = 6          # seconds between requests: OASIS refuses a client that asks faster
RUNS = {"DAM": "forecast_dam", "ACTUAL": "actual"}
HUBS = {"NP15", "SP15", "ZP26"}
TYPES = {"Solar": "solar", "Wind": "wind"}


def parse(raw, run, url, retrieved):
    """One answer as the table's rows, or None when CAISO says it holds no data for the window."""
    z = zipfile.ZipFile(io.BytesIO(raw))
    name = z.namelist()[0]
    body = z.open(name).read()
    if name.endswith(".xml"):
        text = body.decode("utf-8", errors="replace")
        code = re.findall(r"<m:ERR_CODE>([^<]*)", text)
        if code == ["1000"]:
            return None
        raise RuntimeError(f"OASIS error {code}: {re.findall(r'<m:ERR_DESC>([^<]*)', text)}")
    d = pd.read_csv(io.BytesIO(body))
    need = {"INTERVALSTARTTIME_GMT", "INTERVALENDTIME_GMT", "TRADING_HUB", "RENEWABLE_TYPE", "MW", "MARKET_RUN_ID"}
    if not need <= set(d.columns):
        raise RuntimeError(f"OASIS columns {list(d.columns)}")
    # the report also lists areas outside CAISO's own grid (other balancing areas of its regional markets): only CAISO's
    # three trading hubs are kept
    d = d[d["TRADING_HUB"].isin(HUBS)]
    if d.empty:
        return None
    if set(d["MARKET_RUN_ID"]) != {run} or not set(d["RENEWABLE_TYPE"]) <= set(TYPES):
        raise RuntimeError(f"OASIS answered runs {set(d['MARKET_RUN_ID'])}, types {set(d['RENEWABLE_TYPE'])}")
    a, b = pd.to_datetime(d["INTERVALSTARTTIME_GMT"], utc=True), pd.to_datetime(d["INTERVALENDTIME_GMT"], utc=True)
    if ((b - a) != pd.Timedelta(hours=1)).any():
        raise RuntimeError("OASIS lists an interval that is not one hour")
    mw = pd.to_numeric(d["MW"], errors="coerce")
    keep = mw.notna()
    return pd.DataFrame({
        "entity": ("caiso:" + d["TRADING_HUB"])[keep].values, "variable": (d["RENEWABLE_TYPE"].map(TYPES) + f"_{RUNS[run]}_mw")[keep].values,
        "ts_utc": a[keep].dt.strftime("%Y-%m-%dT%H:%M:%SZ").values, "value": mw[keep].values, "unit": "MW", "freq": "PT1H", "geo": "US-CA", "market": "",
        "node": d["TRADING_HUB"][keep].values, "source": SOURCE, "source_url": url, "retrieved_at": retrieved, "vintage": ""})


def windows(first, last, days=30):
    """Spans of at most `days` days from first to last as (start day, end day exclusive). OASIS refuses a span it counts
    as more than 31 days, and it counted a 31-day month from 07:00 to 07:00 as more, so a span is 30."""
    out, a = [], first
    while a <= last:
        b = min(a + dt.timedelta(days=days), last + dt.timedelta(days=1))
        out.append((a, b))
        a = b
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="CAISO wind and solar: day-ahead forecast and actual output, hourly")
    ap.add_argument("--start", help=f"first day (default {FIRST})")
    ap.add_argument("--end", help="last day (default yesterday, Pacific)")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    args = ap.parse_args(argv)
    first = dt.date.fromisoformat(args.start) if args.start else FIRST
    last = dt.date.fromisoformat(args.end) if args.end else pd.Timestamp.now(tz="America/Los_Angeles").date() - dt.timedelta(days=1)
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
        frames, read, empty = [], 0, []
        for a, b in windows(first, last):
            for run in RUNS:
                # each span runs from 07:00 UTC of its first day to 07:00 UTC of the day after its last; the spans meet end to
                # start, so no hour falls between two of them
                url = API.format(run=run, a=f"{a:%Y%m%d}T07:00-0000", b=f"{b:%Y%m%d}T07:00-0000")

                def call():
                    r = requests.get(url, timeout=180)
                    if r.status_code != 200 or r.content[:2] != b"PK":
                        raise RuntimeError(f"OASIS HTTP {r.status_code} for {url}: {r.text[:120]}")
                    return r
                r = ip.with_retries(f"OASIS SLD_REN_FCST {run} {a}", call, log, wait=PAUSE * 2)
                t = parse(r.content, run, url, ip.utc_iso(pd.Timestamp.now(tz="UTC")))
                if t is None:
                    empty.append(f"{run} {a} to {b}")
                    log(f"  {run} {a} to {b}: CAISO holds no data for the window")
                else:
                    read += len(t)
                    frames.append(t)
                    log(f"  {run} {a} to {b}: {len(t)} rows; {read:,} in all")
                if read > CEILING:
                    raise RuntimeError(f"{read:,} rows read, over the ceiling of {CEILING:,}: nothing written")
                time.sleep(PAUSE)
        if not frames:
            raise RuntimeError(f"CAISO answered no data for every window from {first} to {last}")
        s = pd.concat(frames, ignore_index=True).drop_duplicates(["entity", "variable", "ts_utc"], keep="last")
        header = [
            "Energy Research Warehouse (ERW): CAISO wind and solar, the day-ahead forecast and the actual output, hourly, by trading hub (session 133)",
            "Shape: series (docs/datastandard.md v0). freq PT1H; ts_utc is the hour's start. Variables: wind_forecast_dam_mw and solar_forecast_dam_mw (CAISO's day-ahead forecast, market run DAM), "
            "wind_actual_mw and solar_actual_mw (actual generation, market run ACTUAL), MW, as CAISO publishes them. Entities are CAISO's trading hubs NP15, SP15 and ZP26.",
            f"Window: this run asked {first} to {last}; CAISO answered no data for {len(empty)} of the spans asked{(': ' + '; '.join(empty[:4]) + (' ...' if len(empty) > 4 else '')) if empty else ''}. OASIS keeps the report for about three years.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/caiso_wind_solar_forecast.py",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/{run_id}/ (not in git)",
            f"Source: {SOURCE} California ISO, OASIS, Wind and Solar Forecast (SLD_REN_FCST), {PAGE}",
            "  access: " + API.format(run="<DAM|ACTUAL>", a="<UTC>", b="<UTC>"),
            f"Rows read: {read:,} of the {CEILING:,} ceiling the session's forecast pulls share. An hour CAISO does not list is not written. Nothing is filled.",
            'License: public (CAISO OASIS public data; cite "California ISO, OASIS").',
        ]
        ip.write_csv(s[ip.SERIES_COLS], NAME, header, log)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="California ISO (CAISO)", report="OASIS: Wind and Solar Forecast (SLD_REN_FCST), day-ahead forecast and actual generation",
                                    report_url=PAGE, document_list="https://oasis.caiso.com/oasisapi/SingleZip", license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(s):,} rows; {read:,} read"))
        print(f"{NAME}: {len(s):,} rows, {s['ts_utc'].min()[:10]} to {s['ts_utc'].max()[:10]}; {read:,} rows read of {CEILING:,}")
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
