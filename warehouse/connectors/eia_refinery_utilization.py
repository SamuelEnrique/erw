#!/usr/bin/env python3
"""EIA's refinery utilization and capacity, the U.S., the PADDs and the refining districts, a month from 1985: gross
input to refineries, operable, operating and idle operable capacity, and the utilization of operable capacity (session
2334, chain 108: a third source of the session's own choosing, the monthly companion of eia_refinery_weekly's PADDs).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/eia_refinery_utilization_monthly.csv,
from the U.S. Energy Information Administration's API v2, route petroleum/pnp/unc ("Refinery Utilization and
Capacity", Petroleum Supply Monthly):

    https://api.eia.gov/v2/petroleum/pnp/unc/data/?frequency=monthly&data[]=value&start=1985-01

    entity    eia_refinery_utilization:<series>, EIA's series id (one a measure and area)
    variable  gross_input (YIY, gross inputs to refineries), operable_capacity (YRL), operating_capacity (YRO),
              idle_capacity (YRI, idle operable capacity), all kbbl/d (EIA's thousand barrels a day); utilization (YUP,
              the utilization of operable capacity, ratio: EIA's percent divided by 100, as eia_refinery_weekly)
    ts_utc    the month's first day at 00:00:00Z; freq P1M; geo US; node EIA's series description (the U.S., PADDs R10
              to R50 and the refining districts within them, R2A to R3E, RAP and REC; a sum takes one level)

Utilization is EIA's own figure (gross input over operable capacity), not computed here. The weekly PADD figures are in
eia_refinery_weekly, and the annual capacity by refinery in eia_refinery_capacity_annual; the monthly districts are
this route's own. A blank has no row; nothing is filled. A process, unit or area not in the map stops the run; so does
a key given twice. Each row carries the time EIA served its page (a reused page's first download).

    python warehouse/connectors/eia_refinery_utilization.py [--from 1985-01] [--offline | --fresh]

Ceiling: 12 requests a run (pages of 5,000, 3 seconds apart; a page an earlier run saved in warehouse/raw is reused
unless --fresh; --offline asks nothing). License: public (EIA, record 1 of license_reads.csv; cite "U.S. Energy
Information Administration, Petroleum Supply Monthly").
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

NAME = "eia_refinery_utilization_monthly"
CONNECTOR = "eia_refinery_utilization"
SOURCE = "eia:petroleum/pnp/unc"
API = "https://api.eia.gov/v2/petroleum/pnp/unc/"
PAGE = "https://api.eia.gov/v2/petroleum/pnp/unc/"  # the route, as read in session 2334
CEILING, PAUSE, RETRY_WAIT = 12, 3, 60
FIRST = "1985-01"
SPLIT, EARLY_END = "1985-01", "1984-12"   # one window: the route starts in 1985
PROCESSES = {"YIY": "gross_input", "YRL": "operable_capacity", "YRO": "operating_capacity", "YRI": "idle_capacity",
             "YUP": "utilization"}
AREAS = {"NUS", "R10", "R20", "R30", "R40", "R50", "R2A", "R2B", "R2C", "R3A", "R3B", "R3C", "R3D",
         "R3E", "RAP", "REC"}
UNITS = {"mbbl/d": ("kbbl/d", 1.0, ""), "%": ("ratio", 0.01, "")}   # utilization as eia_refinery_weekly writes it


def rows(data, url, retrieved):
    out = []
    for r in data:
        if r.get("process") not in PROCESSES:
            raise RuntimeError(f"a process not asked for: {r.get('process')!r}")
        if str(r.get("duoarea")) not in AREAS:
            raise RuntimeError(f"an area not understood: {r.get('duoarea')!r}")
        v = pd.to_numeric(r.get("value"), errors="coerce")
        if pd.isna(v):
            continue
        u = str(r.get("units", "")).strip().lower()
        if u not in UNITS:
            raise RuntimeError(f"a unit not in the map: {r.get('units')!r}")
        unit, factor, suffix = UNITS[u]
        month = str(r["period"])[:7]
        dt.date.fromisoformat(month + "-01")
        out.append(dict(entity=f"eia_refinery_utilization:{str(r['series']).strip()}", variable=PROCESSES[r["process"]] + suffix,
                        ts_utc=f"{month}-01T00:00:00Z", value=float(v) * factor, unit=unit, freq="P1M",
                        geo="US", market="",
                        node=str(r.get("series-description") or "").strip(), source=SOURCE, source_url=url,
                        retrieved_at=retrieved, vintage=""))
    t = pd.DataFrame(out)
    if len(t) and t.duplicated(["entity", "variable", "ts_utc"]).any():
        raise RuntimeError("an (entity, variable, ts_utc) is given twice")
    return t


def main(argv=None):
    ap = argparse.ArgumentParser(description="EIA's refinery utilization and capacity, a month")
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

    def get(params):
        url = requests.Request("GET", API + "data/", params=params).prepare().url
        hit = None if args.fresh else ip.raw_cached(CONNECTOR, url)
        if hit:
            log(f"  raw file reused: {ip.redact(url)}")
            # session 2247: a reused page keeps the time EIA served it
            return json.loads(hit[0]), ip.redact(url), (hit[1] or {}).get("retrieved_at") or retrieved
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
                return r.json(), ip.redact(r.url), dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            log(f"  {ip.redact(r.url)}: HTTP {r.status_code}; " + (f"asked once more in {RETRY_WAIT} s" if attempt == 1 else "not asked again"))
            time.sleep(RETRY_WAIT)
        raise RuntimeError(f"HTTP {r.status_code} twice for {ip.redact(r.url)}")

    try:
        key = ip.load_key("EIA_API_KEY", log)
        if not key:
            raise RuntimeError("EIA_API_KEY is not set (.env or the environment)")
        retrieved = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        # session 635: months before SPLIT are a window of their own, so the pages of SPLIT on answer again
        windows = [(args.first, EARLY_END), (SPLIT, None)] if args.first < SPLIT else [(args.first, None)]
        frames, records = [], 0
        for first, last in windows:
            offset, total = 0, None
            while True:
                params = {"api_key": key, "frequency": "monthly", "data[]": "value", "facets[process][]": list(PROCESSES),
                          "start": first}
                if last:
                    params["end"] = last
                params.update({"length": 5000, "offset": offset, "sort[0][column]": "period", "sort[0][direction]": "asc",
                               "sort[1][column]": "series", "sort[1][direction]": "asc"})
                body, url, served = get(params)
                resp = body["response"]
                total = int(resp["total"])
                frames.append(rows(resp["data"], url.split("&length")[0], served))
                offset += len(resp["data"])
                if offset >= total or len(resp["data"]) < 5000:
                    break
            if offset != total:
                raise RuntimeError(f"{first} to {last or 'the latest'}: {offset:,} rows read of the {total:,} EIA counts")
            records += total
        total = records
        s = pd.concat([f for f in frames if len(f)], ignore_index=True)
        if s.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("a row on two pages")
        s = s[ip.SERIES_COLS]
        span = f"{s['ts_utc'].min()[:7]} to {s['ts_utc'].max()[:7]}"
        header = [
            "Energy Research Warehouse (ERW): EIA, refinery utilization and capacity, the U.S., the PADDs and the refining districts, a month (session 2334)",
            "Shape: series (docs/datastandard.md v0). entity eia_refinery_utilization:<series>; variable gross_input, operable_capacity, operating_capacity, idle_capacity (kbbl/d) or utilization (ratio, EIA's percent divided by 100); "
            "ts_utc the month's first day; freq P1M; geo US; node EIA's series description. The PADDs are parts of the U.S. and the districts parts of their PADDs: a sum takes one level.",
            f"A blank has no row; nothing is filled. Months {span}; {total:,} records of EIA's, {len(s):,} rows.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia_refinery_utilization.py; {asked[0]} requests of {CEILING}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Energy Information Administration, Petroleum Supply Monthly, refinery utilization and capacity (API v2, route petroleum/pnp/unc), {PAGE}",
            f"  access: {API}data/?frequency=monthly&data[]=value&start={args.first}",
            'License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Petroleum Supply Monthly").',
        ]
        ip.write_snapshot(s, NAME, header, log, ip.SERIES_COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Energy Information Administration (EIA)",
                                    report="Petroleum Supply Monthly, refinery utilization and capacity (API v2)", report_url=PAGE, document_list=API,
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
