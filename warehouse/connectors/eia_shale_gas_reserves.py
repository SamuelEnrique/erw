#!/usr/bin/env python3
"""EIA's shale gas proved reserves and their changes, the U.S., the states and the reporting districts, a year from 2007
to 2021 (session 2250, chain 101: a third source of the session's own choosing).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/eia_shale_gas_reserves_annual.csv, from the
U.S. Energy Information Administration's API v2, route natural-gas/enr/shalegas (U.S. Crude Oil and Natural Gas Proved
Reserves, shale gas):

    https://api.eia.gov/v2/natural-gas/enr/shalegas/data/?frequency=annual&data[]=value&start=2007

    entity    eia_shale_gas_reserves:<series>, EIA's series id (one a measure and area)
    variable  proved_reserves, reserves_based_production, revision_increases, revision_decreases, sales, acquisitions,
              extensions, extensions_and_discoveries, new_field_discoveries, new_reservoir_discoveries_in_old_fields and
              adjustments (EIA's processes R5301 to R5309, R5307A and R53R02), all in bcf (EIA's "BCF")
    ts_utc    the year's 1 January at 00:00:00Z (the reserves are as of 31 December of that year); freq P1Y
    geo       US for the U.S., the lower 48 and the federal offshore; US-<state> for a state (EIA's S<state>) and for the
              districts within a state (California's coastal, San Joaquin and state offshore, North and South Louisiana,
              East and West New Mexico, Texas's Railroad Commission districts and state offshore); node EIA's description

The route ends in 2021: EIA's metadata gives 2007 to 2021, and its shale gas production route ends there too (session
2250). The table is a closed record, not a running series. The states and their districts overlap, and the U.S. holds
both: a sum takes one level. A blank has no row; nothing is filled. A process, unit or area not in the map stops the
run; so does a key given twice.

    python warehouse/connectors/eia_shale_gas_reserves.py [--from 2007] [--offline | --fresh]

Ceiling: 10 requests a run (pages of 5,000, 3 seconds apart; a page an earlier run saved in warehouse/raw is reused
unless --fresh; --offline asks nothing). License: public (EIA, record 1 of license_reads.csv; cite "U.S. Energy
Information Administration, U.S. Crude Oil and Natural Gas Proved Reserves").
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

NAME = "eia_shale_gas_reserves_annual"
CONNECTOR = "eia_shale_gas_reserves"
SOURCE = "eia:natural-gas/enr/shalegas"
API = "https://api.eia.gov/v2/natural-gas/enr/shalegas/"
PAGE = "https://api.eia.gov/v2/natural-gas/enr/shalegas/"  # the route, as read in session 2250
CEILING, PAUSE, RETRY_WAIT = 10, 3, 60
FIRST = "2007"
SPLIT, EARLY_END = "2007", "2006"   # one window: the route starts in 2007
PROCESSES = {"R5301": "proved_reserves", "R5302": "reserves_based_production", "R5303": "revision_increases",
             "R5304": "revision_decreases", "R5305": "sales", "R5306": "acquisitions", "R5307": "extensions",
             "R5307A": "extensions_and_discoveries", "R5308": "new_field_discoveries",
             "R5309": "new_reservoir_discoveries_in_old_fields", "R53R02": "adjustments"}
STATES = ("AK AL AR CA CO KS KY LA MI MS MT ND NM NY OH OK PA TX UT VA WV WY").split()
DISTRICTS = {"RCAC": "CA", "RCAJ": "CA", "RCASF": "CA", "RLAN": "LA", "RLASO": "LA", "RNMEAST": "NM", "RNMWEST": "NM",
             "RTXSF": "TX", **{f"RTX{d}": "TX" for d in ("01", "02", "03", "04", "05", "06", "07B", "07C", "08", "08A", "09", "10")}}
AREAS = {"NUS", "R48", "RUSF"} | {"S" + st for st in STATES} | set(DISTRICTS)   # as EIA's route answered in session 2250


def GEO_OF(area):
    """US for the U.S., the lower 48 and the federal offshore; US-<state> for a state or a district within one."""
    if area in ("NUS", "R48", "RUSF"):
        return "US"
    return "US-" + (DISTRICTS[area] if area in DISTRICTS else area[1:])
UNITS = {"bcf": ("bcf", 1.0, "")}


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
        year = str(r["period"]).strip()
        dt.date(int(year), 1, 1)
        out.append(dict(entity=f"eia_shale_gas_reserves:{str(r['series']).strip()}", variable=PROCESSES[r["process"]] + suffix,
                        ts_utc=f"{year}-01-01T00:00:00Z", value=float(v) * factor, unit=unit, freq="P1Y",
                        geo=GEO_OF(str(r["duoarea"])), market="",
                        node=str(r.get("series-description") or "").strip(), source=SOURCE, source_url=url,
                        retrieved_at=retrieved, vintage=""))
    t = pd.DataFrame(out)
    if len(t) and t.duplicated(["entity", "variable", "ts_utc"]).any():
        raise RuntimeError("an (entity, variable, ts_utc) is given twice")
    return t


def main(argv=None):
    ap = argparse.ArgumentParser(description="EIA's shale gas proved reserves and their changes, a year")
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
                params = {"api_key": key, "frequency": "annual", "data[]": "value", "facets[process][]": list(PROCESSES),
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
            "Energy Research Warehouse (ERW): EIA, shale gas proved reserves and their changes, the U.S., the states and the reporting districts, a year, 2007 to 2021 (session 2250)",
            "Shape: series (docs/datastandard.md v0). entity eia_shale_gas_reserves:<series>; variable proved_reserves, reserves_based_production and the reserves' changes, in bcf; ts_utc the year's 1 January (as of 31 December); freq P1Y; "
            "geo US or US-<state>; node EIA's description. States and their districts overlap: a sum takes one level. EIA's route ends in 2021: a closed record.",
            f"A blank has no row; nothing is filled. Years {span[:4]} to {span[-7:-3]}; {total:,} records of EIA's, {len(s):,} rows.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia_shale_gas_reserves.py; {asked[0]} requests of {CEILING}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Energy Information Administration, U.S. Crude Oil and Natural Gas Proved Reserves, shale gas (API v2, route natural-gas/enr/shalegas), {PAGE}",
            f"  access: {API}data/?frequency=annual&data[]=value&" + "&".join(f"facets[process][]={k}" for k in PROCESSES) + f"&start={args.first}",
            'License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, U.S. Crude Oil and Natural Gas Proved Reserves").',
        ]
        ip.write_snapshot(s, NAME, header, log, ip.SERIES_COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Energy Information Administration (EIA)",
                                    report="U.S. Crude Oil and Natural Gas Proved Reserves, shale gas (API v2)", report_url=PAGE, document_list=API,
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
