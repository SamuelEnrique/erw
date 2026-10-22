#!/usr/bin/env python3
"""EIA's movements of crude oil and petroleum products between PADDs by rail and by tanker and barge, a month (session
622, a public source chosen by the chain's rule).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/eia_padd_rail_barge_movements_monthly.csv,
from the U.S. Energy Information Administration's API v2, two routes of the Petroleum Supply Monthly:

    https://api.eia.gov/v2/petroleum/move/rail/data/?frequency=monthly&data[]=value&start=2010-01   (receipts by rail)
    https://api.eia.gov/v2/petroleum/move/tb/data/?frequency=monthly&data[]=value&start=2010-01     (by tanker and barge)

    entity    eia_padd_movements:<series>, EIA's series id (one a product, mode and pair of areas)
    variable  rail_receipts (RAIL) or tanker_barge_receipts (BMV), kbbl (EIA's thousand barrels in the month)
    ts_utc    the month's first day at 00:00:00Z; freq P1M; geo US; node EIA's series name, which names the receiving
              area and the area of origin ("East Coast (PADD 1) Receipts by Rail from Midwest (PADD 2) of Crude Oil")

EIA's area pair <receiving>-<origin> (R10-R20: PADD 1 receives from PADD 2; R1X, R1Y and R1Z are PADD 1's
subdistricts New England, Central Atlantic and Lower Atlantic) is kept in the series id. The pipeline movements of
crude oil are eia_padd_crude_pipeline_flows (eia_series.py). A blank has no row; nothing is filled. A process, unit or
area not in the map stops the run; so does a key given twice.

    python warehouse/connectors/eia_padd_movements.py [--from 2010-01] [--offline | --fresh]

Ceiling: 17 requests a run (pages of 5,000, 3 seconds apart; a page an earlier run saved in warehouse/raw is reused
unless --fresh; --offline asks nothing). License: public (EIA, record 1 of license_reads.csv; cite "U.S. Energy
Information Administration, Petroleum Supply Monthly").
"""

import argparse
import datetime as dt
import json
import os
import re
import sys
import time
import traceback

import pandas as pd
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "eia_padd_rail_barge_movements_monthly"
CONNECTOR = "eia_padd_movements"
ROUTES = {"petroleum/move/rail": "RAIL", "petroleum/move/tb": "BMV"}
SOURCES = {r: f"eia:{r}" for r in ROUTES}
BASE = "https://api.eia.gov/v2/"
PAGE = "https://www.eia.gov/petroleum/supply/monthly/"
CEILING, PAUSE, RETRY_WAIT = 17, 3, 60   # session 622: two of 20 went to the probes, one is left for a retry
FIRST = "2010-01"
PROCESSES = {"RAIL": "rail_receipts", "BMV": "tanker_barge_receipts"}
AREA = re.compile(r"^R(10|20|30|40|50|1X|1Y|1Z)-R(10|20|30|40|50|1X|1Y|1Z)$")
UNITS = {"mbbl": ("kbbl", 1.0)}


def rows(data, url, retrieved, route):
    out = []
    for r in data:
        if r.get("process") != ROUTES[route]:
            raise RuntimeError(f"a process not of {route}: {r.get('process')!r}")
        if not AREA.match(str(r.get("duoarea"))):
            raise RuntimeError(f"an area pair not understood: {r.get('duoarea')!r}")
        v = pd.to_numeric(r.get("value"), errors="coerce")
        if pd.isna(v):
            continue
        u = str(r.get("units", "")).strip().lower()
        if u not in UNITS:
            raise RuntimeError(f"a unit not in the map: {r.get('units')!r}")
        unit, factor = UNITS[u]
        month = str(r["period"])[:7]
        dt.date.fromisoformat(month + "-01")
        out.append(dict(entity=f"eia_padd_movements:{str(r['series']).strip()}", variable=PROCESSES[r["process"]],
                        ts_utc=f"{month}-01T00:00:00Z", value=float(v) * factor, unit=unit, freq="P1M", geo="US", market="",
                        node=str(r.get("series-description") or "").strip(), source=SOURCES[route], source_url=url,
                        retrieved_at=retrieved, vintage=""))
    t = pd.DataFrame(out)
    if len(t) and t.duplicated(["entity", "variable", "ts_utc"]).any():
        raise RuntimeError("an (entity, variable, ts_utc) is given twice")
    return t


def main(argv=None):
    ap = argparse.ArgumentParser(description="EIA's movements between PADDs by rail and by tanker and barge, a month")
    ap.add_argument("--from", dest="first", default=FIRST, help="the first month, YYYY-MM")
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

    def get(api, params):
        url = requests.Request("GET", api + "data/", params=params).prepare().url
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
        frames, records = [], {}
        for route in ROUTES:
            api = BASE + route + "/"
            offset, total = 0, None
            while True:
                body, url = get(api, {"api_key": key, "frequency": "monthly", "data[]": "value", "start": args.first,
                                      "length": 5000, "offset": offset, "sort[0][column]": "period", "sort[0][direction]": "asc",
                                      "sort[1][column]": "series", "sort[1][direction]": "asc"})
                resp = body["response"]
                total = int(resp["total"])
                frames.append(rows(resp["data"], url.split("&length")[0], retrieved, route))
                offset += len(resp["data"])
                if offset >= total or len(resp["data"]) < 5000:
                    break
            if offset != total:
                raise RuntimeError(f"{route}: {offset:,} rows read of the {total:,} EIA counts")
            records[route] = total
            log(f"  {route}: {total:,} records")
        s = pd.concat([f for f in frames if len(f)], ignore_index=True)
        if s.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("a row on two pages, or a series in both routes")
        s = s[ip.SERIES_COLS]
        span = f"{s['ts_utc'].min()[:7]} to {s['ts_utc'].max()[:7]}"
        header = [
            "Energy Research Warehouse (ERW): EIA, movements of crude oil and petroleum products between PADDs by rail and by tanker and barge, a month (session 622)",
            "Shape: series (docs/datastandard.md v0). entity eia_padd_movements:<series>; variable rail_receipts or tanker_barge_receipts (kbbl); ts_utc the month's first day; freq P1M; "
            "node EIA's series name (the receiving area, the area of origin and the product). EIA's area pair is <receiving>-<origin>.",
            f"A blank has no row; nothing is filled. Months {span}; records of EIA's: rail {records['petroleum/move/rail']:,}, tanker and barge {records['petroleum/move/tb']:,}; {len(s):,} rows.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia_padd_movements.py; {asked[0]} requests of {CEILING}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCES['petroleum/move/rail']} U.S. Energy Information Administration, Petroleum Supply Monthly, receipts by rail between PADDs (API v2, route petroleum/move/rail), {PAGE}",
            f"Source: {SOURCES['petroleum/move/tb']} U.S. Energy Information Administration, Petroleum Supply Monthly, movements by tanker and barge between PADDs (API v2, route petroleum/move/tb), {PAGE}",
            f"  access: {BASE}<route>/data/?frequency=monthly&data[]=value&start={args.first}",
            'License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Petroleum Supply Monthly").',
        ]
        ip.write_snapshot(s, NAME, header, log, ip.SERIES_COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCES["petroleum/move/rail"], publisher="U.S. Energy Information Administration (EIA)",
                                    report="Petroleum Supply Monthly, receipts by rail between PADDs (API v2)", report_url=PAGE,
                                    document_list=BASE + "petroleum/move/rail/", license="public", tables=[NAME]),
                               dict(source=SOURCES["petroleum/move/tb"], publisher="U.S. Energy Information Administration (EIA)",
                                    report="Petroleum Supply Monthly, movements by tanker and barge between PADDs (API v2)", report_url=PAGE,
                                    document_list=BASE + "petroleum/move/tb/", license="public", tables=[NAME])])
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
