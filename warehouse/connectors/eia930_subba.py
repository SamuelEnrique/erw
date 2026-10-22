#!/usr/bin/env python3
"""EIA-930's demand by sub-region (sub-balancing-authority), hourly, the last 90 whole days (session 602).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/eia930_subba_demand_hourly.csv, from the U.S.
Energy Information Administration's API v2, route electricity/rto/region-sub-ba-data (Form EIA-930, demand by
subregion, hourly, UTC):

    https://api.eia.gov/v2/electricity/rto/region-sub-ba-data/data/?frequency=hourly&data[]=value&start=<day>T01&end=<day>T00

    entity    eia930_subba:<parent>:<subba>, EIA's parent balancing authority and sub-region codes
    variable  demand_mw (MW: EIA's megawatthours in the hour, the hour's mean), as eia930_all_demand
    ts_utc    the hour's start: EIA's period is the hour's end (session 5's check on EIA-930), so ts_utc is the period
              less one hour, as warehouse/connectors/eia930.py does; freq PT1H; geo US; node the sub-region's name

The window is the last 90 whole UTC days before the run's day. A blank has no row; nothing is filled; an hour EIA does not
give for a sub-region is missing, counted in the run log and the header. A unit not in the map stops the run; so does a key
given twice.

    python warehouse/connectors/eia930_subba.py [--days 90] [--offline | --fresh]

Ceiling: 59 requests a run (pages of 5,000, 3 seconds apart; a page an earlier run saved in warehouse/raw is reused unless
--fresh; --offline asks nothing). License: public (EIA, record 1 of license_reads.csv; cite "U.S. Energy Information
Administration, Hourly Electric Grid Monitor").
"""

import argparse
import datetime as dt
import json
import os
import sys
import time
import traceback

import pandas as pd
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "eia930_subba_demand_hourly"
CONNECTOR = "eia930_subba"
SOURCE = "eia:electricity/rto/region-sub-ba-data"
API = "https://api.eia.gov/v2/electricity/rto/region-sub-ba-data/"
PAGE = "https://www.eia.gov/electricity/gridmonitor/"
CEILING, PAUSE, RETRY_WAIT = 59, 3, 60   # session 602: one of 60 went to the probe
UNITS = {"megawatthours": ("MW", 1.0)}   # an hour's megawatthours are the hour's mean megawatts


def text(v):
    return "" if v is None or (isinstance(v, float) and pd.isna(v)) else str(v).strip()


def rows(data, url, retrieved):
    out = []
    for r in data:
        v = pd.to_numeric(r.get("value"), errors="coerce")
        if pd.isna(v):
            continue
        u = text(r.get("value-units")).lower()
        if u not in UNITS:
            raise RuntimeError(f"a unit not in the map: {r.get('value-units')!r}")
        unit, factor = UNITS[u]
        parent, sub = text(r.get("parent")), text(r.get("subba"))
        if not parent or not sub:
            raise RuntimeError(f"a record with no parent or sub-region: {r}")
        end = pd.Timestamp(text(r.get("period")) + ":00", tz="UTC")
        start = end - pd.Timedelta(hours=1)
        out.append(dict(entity=f"eia930_subba:{parent}:{sub}", variable="demand_mw", ts_utc=start.strftime("%Y-%m-%dT%H:%M:%SZ"),
                        value=float(v) * factor, unit=unit, freq="PT1H", geo="US", market="",
                        node=f"{text(r.get('subba-name'))} ({text(r.get('parent-name'))})", source=SOURCE, source_url=url,
                        retrieved_at=retrieved, vintage=""))
    t = pd.DataFrame(out)
    if len(t) and t.duplicated(["entity", "variable", "ts_utc"]).any():
        raise RuntimeError("an (entity, variable, ts_utc) is given twice")
    return t


def window(days, today=None):
    """(first period, last period) as EIA's hour-ending strings, for the last `days` whole UTC days before today."""
    today = today or dt.datetime.now(dt.timezone.utc).date()
    first_day = today - dt.timedelta(days=days)
    return f"{first_day:%Y-%m-%d}T01", f"{today:%Y-%m-%d}T00"


def main(argv=None):
    ap = argparse.ArgumentParser(description="EIA-930's demand by sub-region, hourly")
    ap.add_argument("--days", type=int, default=90)
    ap.add_argument("--through", help="the run's day (UTC, YYYY-MM-DD): the window ends at its first hour (default today)")
    ap.add_argument("--offline", action="store_true", help="the pages from warehouse/raw only, no request")
    ap.add_argument("--fresh", action="store_true", help="ask every page again, even one saved in warehouse/raw")
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
    asked = [0]

    def get(params):
        url = requests.Request("GET", API + "data/", params=params).prepare().url
        hit = None if args.fresh else ip.raw_cached(CONNECTOR, url)
        if hit:
            log(f"  raw file reused: {ip.redact(url)}")
            return json.loads(hit[0]), ip.redact(url)
        if args.offline:
            raise RuntimeError(f"offline: {ip.redact(url)} is not in warehouse/raw/{CONNECTOR}/")
        for attempt in (1, 2):
            if asked[0] >= CEILING:
                raise RuntimeError(f"the ceiling of {CEILING} requests is reached")
            asked[0] += 1
            time.sleep(PAUSE)
            r = requests.get(url, timeout=180)
            if r.status_code < 500 and r.status_code != 429:
                r.raise_for_status()
                return r.json(), ip.redact(r.url)
            log(f"  {ip.redact(r.url)}: HTTP {r.status_code}; " + (f"asked once more in {RETRY_WAIT} s" if attempt == 1 else "not asked again"))
            time.sleep(RETRY_WAIT)
        raise RuntimeError(f"HTTP {r.status_code} twice for {ip.redact(r.url)}")

    try:
        key = ip.load_key("EIA_API_KEY", log)
        if not key:
            raise RuntimeError("EIA_API_KEY is not set (.env or the environment)")
        today = dt.date.fromisoformat(args.through) if args.through else None
        first, last = window(args.days, today)
        retrieved = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        frames, offset, total = [], 0, None
        while True:
            body, url = get({"api_key": key, "frequency": "hourly", "data[]": "value", "start": first, "end": last, "length": 5000,
                             "offset": offset, "sort[0][column]": "period", "sort[0][direction]": "asc",
                             "sort[1][column]": "subba", "sort[1][direction]": "asc"})
            resp = body["response"]
            total = int(resp["total"])
            frames.append(rows(resp["data"], url.split("&length")[0], retrieved))
            offset += len(resp["data"])
            if offset >= total or len(resp["data"]) < 5000:
                break
        if offset != total:
            raise RuntimeError(f"{offset:,} rows read of the {total:,} EIA counts")
        s = pd.concat([f for f in frames if len(f)], ignore_index=True)
        if s.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("a row on two pages")
        s = s[ip.SERIES_COLS]
        hours = args.days * 24
        n = s.groupby("entity").size()
        short = n[n < hours]
        log(f"{s['entity'].nunique()} sub-regions; {len(short)} with fewer than {hours} hours (missing hours {int((hours - short).sum()):,})")
        span = f"{s['ts_utc'].min()} to {s['ts_utc'].max()}"
        header = [
            "Energy Research Warehouse (ERW): EIA-930, demand by sub-region (sub-balancing-authority), hourly, the last 90 whole days (session 602)",
            "Shape: series (docs/datastandard.md v0). entity eia930_subba:<parent>:<subba>; variable demand_mw (MW, the hour's mean); ts_utc the hour's start (EIA's hour-ending period less one hour); freq PT1H; node the sub-region's and parent's names.",
            f"A blank has no row; nothing is filled. Hours {span}; {s['entity'].nunique()} sub-regions, {len(short)} of them with fewer than {hours} hours ({int((hours - short).sum()):,} hours missing as EIA gives them).",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia930_subba.py; {asked[0]} requests of {CEILING}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Energy Information Administration, Hourly Electric Grid Monitor, demand by subregion (API v2, route electricity/rto/region-sub-ba-data), {PAGE}",
            f"  access: {API}data/?frequency=hourly&data[]=value&start={first}&end={last}",
            'License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Hourly Electric Grid Monitor").',
        ]
        ip.write_snapshot(s, NAME, header, log, ip.SERIES_COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Energy Information Administration (EIA)",
                                    report="Form EIA-930, demand by subregion (API v2, hourly)", report_url=PAGE, document_list=API,
                                    license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(s):,} rows"))
        print(f"{NAME}: {len(s):,} rows, {s['entity'].nunique()} sub-regions, {span}; {asked[0]} requests")
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
