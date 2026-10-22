#!/usr/bin/env python3
"""EIA's refinery capacity: operable atmospheric distillation and downstream charge capacity, and the number of
refineries, as of January 1, by state, PADD and the U.S., a year (session 614).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/eia_refinery_capacity_annual.csv, from the
U.S. Energy Information Administration's API v2, route petroleum/pnp/cap1 (Refinery Capacity Report, Form EIA-820):

    https://api.eia.gov/v2/petroleum/pnp/cap1/data/?frequency=annual&data[]=value&start=1995

    entity    eia_refinery_capacity:<series>, EIA's series id (one a process, area and unit)
    variable  capacity_per_calendar_day (EIA's barrels per calendar day, B/CD), capacity_per_stream_day (barrels per
              stream day, B/SD), both in kbbl/d; refineries (count: operable, operating or idle, by EIA's process)
    value     kbbl/d (EIA's barrels a day divided by 1,000) or count
    ts_utc    January 1 of EIA's year at 00:00:00Z (EIA's "as of January 1"); freq P1Y; geo US-<state> for a state,
              US-PR, US-GU and US-VI for Puerto Rico, Guam and the Virgin Islands, US for the U.S. and the PADDs; node
              EIA's series name (the process, area and unit)

A barrel per stream day is a day's capacity running without downtime; a barrel per calendar day allows for it. The
process (atmospheric distillation, vacuum distillation, cracking, reforming, hydrotreating, coking and others) is in
the entity and the node. A blank has no row; nothing is filled. A unit or area not in the map stops the run; so does
a key given twice.

    python warehouse/connectors/eia_refinery_capacity.py [--from 1995] [--offline | --fresh]

Ceiling: 12 requests a run (pages of 5,000, 3 seconds apart; a page an earlier run saved in warehouse/raw is reused
unless --fresh; --offline asks nothing). From 1995: the route holds 65,350 rows from 1982, beyond session 614's
ceiling. License: public (EIA, record 1 of license_reads.csv; cite "U.S. Energy Information Administration, Refinery
Capacity Report").
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

NAME = "eia_refinery_capacity_annual"
CONNECTOR = "eia_refinery_capacity"
SOURCE = "eia:petroleum/pnp/cap1"
API = "https://api.eia.gov/v2/petroleum/pnp/cap1/"
PAGE = "https://www.eia.gov/petroleum/refinerycapacity/"
CEILING, PAUSE, RETRY_WAIT = 12, 3, 60   # session 614: three of 15 went to the probes
FIRST = "1995"
AREAS = {"NUS", "R10", "R20", "R30", "R40", "R50"}   # and any state, S<state>
TERRITORIES = {"NPZ": "US-PR", "NGQ": "US-GU", "NVQ": "US-VI"}
UNITS = {"b/cd": ("kbbl/d", 0.001, "capacity_per_calendar_day"),
         "b/sd": ("kbbl/d", 0.001, "capacity_per_stream_day"), "count": ("count", 1.0, "refineries")}


def rows(data, url, retrieved):
    out = []
    for r in data:
        area = str(r.get("duoarea"))
        if not (area in AREAS or area in TERRITORIES or (len(area) == 3 and area.startswith("S"))):
            raise RuntimeError(f"an area not understood: {r.get('duoarea')!r}")
        v = pd.to_numeric(r.get("value"), errors="coerce")
        if pd.isna(v):
            continue
        u = str(r.get("units", "")).strip().lower()
        if u not in UNITS:
            raise RuntimeError(f"a unit not in the map: {r.get('units')!r}")
        unit, factor, variable = UNITS[u]
        year = str(r["period"])
        dt.date.fromisoformat(year + "-01-01")
        geo = TERRITORIES.get(area) or (f"US-{area[1:]}" if area.startswith("S") else "US")
        out.append(dict(entity=f"eia_refinery_capacity:{str(r['series']).strip()}", variable=variable,
                        ts_utc=f"{year}-01-01T00:00:00Z", value=float(v) * factor, unit=unit, freq="P1Y", geo=geo, market="",
                        node=str(r.get("series-description") or "").strip(), source=SOURCE, source_url=url,
                        retrieved_at=retrieved, vintage=""))
    t = pd.DataFrame(out)
    if len(t) and t.duplicated(["entity", "variable", "ts_utc"]).any():
        raise RuntimeError("an (entity, variable, ts_utc) is given twice")
    return t


def main(argv=None):
    ap = argparse.ArgumentParser(description="EIA's refinery capacity, a year")
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
            body, url = get({"api_key": key, "frequency": "annual", "data[]": "value", "start": args.first, "length": 5000, "offset": offset,
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
        if s.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("a row on two pages")
        s = s[ip.SERIES_COLS]
        span = f"{s['ts_utc'].min()[:4]} to {s['ts_utc'].max()[:4]}"
        header = [
            "Energy Research Warehouse (ERW): EIA, refinery capacity as of January 1: operable distillation and downstream charge capacity and the number of refineries, by state, PADD and the U.S., a year (session 614)",
            "Shape: series (docs/datastandard.md v0). entity eia_refinery_capacity:<series>; variable capacity_per_calendar_day or capacity_per_stream_day (kbbl/d, EIA's barrels a day / 1,000) or refineries (count); "
            "ts_utc January 1 of the year; freq P1Y; node EIA's series name (the process, area and unit). The PADDs and the states are parts of the U.S.: a sum takes one level.",
            f"A blank has no row; nothing is filled. Years {span}; {total:,} records of EIA's, {len(s):,} rows.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia_refinery_capacity.py; {asked[0]} requests of {CEILING}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Energy Information Administration, Refinery Capacity Report (API v2, route petroleum/pnp/cap1), {PAGE}",
            f"  access: {API}data/?frequency=annual&data[]=value&start={args.first}",
            'License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Refinery Capacity Report").',
        ]
        ip.write_snapshot(s, NAME, header, log, ip.SERIES_COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Energy Information Administration (EIA)",
                                    report="Refinery Capacity Report, Form EIA-820 (API v2)", report_url=PAGE, document_list=API,
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
