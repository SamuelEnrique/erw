#!/usr/bin/env python3
"""EIA's crude oil proved reserves and their changes by state and area, a year (session 551).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/eia_crude_reserves_annual.csv, from the U.S.
Energy Information Administration's API v2, route petroleum/crd/pres (U.S. Crude Oil and Natural Gas Proved Reserves, 1977 on):

    https://api.eia.gov/v2/petroleum/crd/pres/data/?frequency=annual&data[]=value&start=1977

    entity    eia_crude_reserves:<process>:<area>, EIA's process and area codes (S<state>, NUS for the U.S., R48 the Lower 48,
              and EIA's parts of states and offshore areas: RTX01 to RTX10 Texas's districts, RLAN and RLASO Louisiana's
              north and south, RCAC, RCAJ and RCAL California's coastal, San Joaquin and Los Angeles basins, RNMEAST and
              RNMWEST New Mexico's, RUSF, R5F, R44F, R1901F, RCASF, RLASF and RTXSF federal and state offshore)
    variable  the process as a word: proved_reserves and its changes (adjustments, revisions, sales, acquisitions,
              extensions and discoveries, production)
    value     kbbl (EIA's million barrels times 1,000); ts_utc the year's 1 January (reserves at the year's end); freq P1Y; geo US-<state> for a
              state, US otherwise; node EIA's series name

A figure EIA withholds has no row; nothing is filled. A unit or process not in the map stops the run; so does a key given
twice with two values. Parts of states and the Lower 48 repeat what states and the U.S. hold: a sum takes one level.

    python warehouse/connectors/eia_crude_reserves.py [--from 1977] [--offline | --fresh]

Ceiling: 9 requests a run (pages of 5,000, 3 seconds apart; a page an earlier run saved in warehouse/raw is reused unless
--fresh; --offline asks nothing). License: public (EIA, record 1 of license_reads.csv; cite "U.S. Energy Information
Administration, U.S. Crude Oil and Natural Gas Proved Reserves").
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

NAME = "eia_crude_reserves_annual"
CONNECTOR = "eia_crude_reserves"
SOURCE = "eia:petroleum/crd/pres"
API = "https://api.eia.gov/v2/petroleum/crd/pres/"
PAGE = "https://www.eia.gov/naturalgas/crudeoilreserves/"
CEILING, PAUSE, RETRY_WAIT = 9, 3, 60   # session 551: one of 10 went to the probe
FIRST = "1977"
PROCESSES = {"R01": "proved_reserves", "R02": "adjustments", "R03": "revision_increases", "R04": "revision_decreases",
             "R05": "sales", "R06": "acquisitions", "R07A": "extensions_and_discoveries", "R10": "production"}
UNITS = {"mmbbl": ("kbbl", 1000.0)}
DUPLICATES = [0]   # rows EIA gives twice with the same value, kept once


def geo_of(pair):
    first = str(pair).upper()
    return f"US-{first[1:]}" if len(first) == 3 and first.startswith("S") else "US"


def rows(data, url, retrieved):
    out = []
    for r in data:
        if r.get("process") not in PROCESSES:
            raise RuntimeError(f"a process not asked for: {r.get('process')!r}")
        v = pd.to_numeric(r.get("value"), errors="coerce")
        if pd.isna(v):
            continue
        u = str(r.get("units", "")).strip().lower()
        if u not in UNITS:
            raise RuntimeError(f"a unit not in the map: {r.get('units')!r}")
        unit, factor = UNITS[u]
        pair = str(r["duoarea"]).strip()
        year = int(str(r["period"])[:4])
        out.append(dict(entity=f"eia_crude_reserves:{r['process']}:{pair}", variable=PROCESSES[r["process"]],
                        ts_utc=f"{year}-01-01T00:00:00Z", value=float(v) * factor, unit=unit, freq="P1Y", geo=geo_of(pair),
                        market="", node=str(r.get("series-description") or "").strip(), source=SOURCE, source_url=url,
                        retrieved_at=retrieved, vintage=""))
    t = pd.DataFrame(out)
    # session 550: EIA gives a few series under two ids with the same figure (Louisiana's 2016 net receipts from the
    # United Arab Emirates, NA1290_SLA-NTC_2 and NGM_EPG0_IMB_SLA-NTC_MMCF): a row repeated with the same value is kept
    # once; the same key with two values stops the run
    if len(t):
        same = t.duplicated(["entity", "variable", "ts_utc", "value"])
        DUPLICATES[0] += int(same.sum())
        t = t[~same]
        if t.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("an (entity, variable, ts_utc) is given twice with two values")
    return t


def main(argv=None):
    ap = argparse.ArgumentParser(description="EIA's crude oil proved reserves and their changes by state and area, a year")
    ap.add_argument("--from", dest="first", default=FIRST, help="the first year, YYYY")
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
        retrieved = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        frames, offset, total = [], 0, None
        while True:
            body, url = get({"api_key": key, "frequency": "annual", "data[]": "value", "facets[process][]": list(PROCESSES),
                             "start": args.first, "length": 5000, "offset": offset,
                             "sort[0][column]": "period", "sort[0][direction]": "asc",
                             "sort[1][column]": "series", "sort[1][direction]": "asc"})
            resp = body["response"]
            total = int(resp["total"])
            frames.append(rows(resp["data"], url.split("&length")[0], retrieved))
            offset += len(resp["data"])
            if offset >= total or len(resp["data"]) < 5000:
                break
        if offset != total:
            raise RuntimeError(f"{offset:,} rows read of the {total:,} EIA counts")
        s = pd.concat([f for f in frames if len(f)], ignore_index=True)
        same = s.duplicated(["entity", "variable", "ts_utc", "value"])
        DUPLICATES[0] += int(same.sum())
        s = s[~same]
        if s.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("a row on two pages with two values")
        log(f"{DUPLICATES[0]} rows EIA gives twice with the same value, kept once")
        s = s[ip.SERIES_COLS]
        span = f"{s['ts_utc'].min()[:4]} to {s['ts_utc'].max()[:4]}"
        header = [
            "Energy Research Warehouse (ERW): EIA, crude oil proved reserves and their changes by state and area, a year (session 551)",
            "Shape: series (docs/datastandard.md v0). entity eia_crude_reserves:<process>:<area>; variable proved_reserves or a change (adjustments, revisions, sales, acquisitions, "
            "extensions and discoveries, production); unit kbbl; ts_utc the year's 1 January (reserves at the year's end); freq P1Y; node EIA's series name. "
            "Parts of states and the Lower 48 repeat states and the U.S.: a sum takes one level.",
            f"A figure EIA withholds has no row; nothing is filled. Years {span}; {total:,} records of EIA's, {len(s):,} rows.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia_crude_reserves.py; {asked[0]} requests of {CEILING}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Energy Information Administration, U.S. Crude Oil and Natural Gas Proved Reserves (API v2, route petroleum/crd/pres), {PAGE}",
            f"  access: {API}data/?frequency=annual&data[]=value&facets[process][]=<each>&start={args.first}",
            'License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, U.S. Crude Oil and Natural Gas Proved Reserves").',
        ]
        ip.write_snapshot(s, NAME, header, log, ip.SERIES_COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Energy Information Administration (EIA)",
                                    report="U.S. Crude Oil and Natural Gas Proved Reserves, crude oil (API v2)", report_url=PAGE, document_list=API,
                                    license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(s):,} rows"))
        print(f"{NAME}: {len(s):,} rows, {s['entity'].nunique()} series, {span}; {asked[0]} requests")
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
