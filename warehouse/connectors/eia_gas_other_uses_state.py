#!/usr/bin/env python3
"""EIA's natural gas consumption by state that the monthly table does not hold: vehicle fuel, lease and plant fuel,
pipeline fuel and the volume delivered to consumers, a year (session 2164, chain 094: natural gas by end use and state,
the uses beside eia_gas_consumption_state_monthly's residential, commercial, industrial and electric power).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/eia_gas_other_uses_state_annual.csv, from
the U.S. Energy Information Administration's API v2, route natural-gas/cons/sum (the Natural Gas Annual's consumption
by end use and state), the same route as session 518's monthly table, asked for its four other processes, a year:

    https://api.eia.gov/v2/natural-gas/cons/sum/data/?frequency=annual&data[]=value&facets[process][]=VDV...&start=2001

    entity    eia_gas_other_uses:<process>:<area>, EIA's process code and area code (S<state>, or NUS for the U.S.)
    variable  consumption_vehicle_fuel (VDV), consumption_lease_and_plant_fuel (VGL, one figure: EIA does not part lease
              from plant fuel here, and gives it for the nation only, not by state), consumption_pipeline_fuel (VGP, pipeline and distribution use), and
              delivered_to_consumers (VGT: residential, commercial, industrial, electric power and vehicle fuel together;
              a sum over the variables must leave it out). Total consumption is delivered_to_consumers plus lease and plant
              fuel plus pipeline fuel (EIA's VC0, eia_gas_consumption_state_monthly's consumption_total, session 2164's cross-check)
    value     MMcf (EIA's million cubic feet, kept)
    ts_utc    the year's 1 January at 00:00:00Z; freq P1Y; geo US-<state> or US; node EIA's series name

EIA withholds some figures (a blank in the API): a blank has no row; nothing is filled. A unit not in the map stops the
run; so does a key given twice.

    python warehouse/connectors/eia_gas_other_uses_state.py [--from 2001] [--offline | --fresh]

Ceiling: 15 requests a run (pages of 5,000, 3 seconds apart; a page an earlier run saved in warehouse/raw is reused
unless --fresh; --offline asks nothing). License: public (EIA, record 1 of license_reads.csv; cite "U.S. Energy
Information Administration, Natural Gas Annual").
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

NAME = "eia_gas_other_uses_state_annual"
CONNECTOR = "eia_gas_other_uses_state"
SOURCE = "eia:natural-gas/cons/sum:annual"
API = "https://api.eia.gov/v2/natural-gas/cons/sum/"
PAGE = "https://www.eia.gov/naturalgas/annual/"
CEILING, PAUSE, RETRY_WAIT = 15, 3, 60
FIRST = "2001"
PROCESSES = {"VDV": "consumption_vehicle_fuel", "VGL": "consumption_lease_and_plant_fuel", "VGP": "consumption_pipeline_fuel",
             "VGT": "delivered_to_consumers"}
UNITS = {"mmcf": ("MMcf", 1.0)}


def geo_of(area):
    a = str(area).strip().upper()
    if a == "NUS":
        return "US"
    if len(a) == 3 and a.startswith("S"):
        return f"US-{a[1:]}"
    raise RuntimeError(f"an area not understood: {area!r}")


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
        year = str(r["period"]).strip()
        if len(year) != 4 or not year.isdigit():
            raise RuntimeError(f"a period not a year: {r['period']!r}")
        out.append(dict(entity=f"eia_gas_other_uses:{r['process']}:{r['duoarea']}", variable=PROCESSES[r["process"]],
                        ts_utc=f"{year}-01-01T00:00:00Z", value=float(v) * factor, unit=unit, freq="P1Y", geo=geo_of(r["duoarea"]),
                        market="", node=str(r.get("series-description") or "").strip(), source=SOURCE, source_url=url,
                        retrieved_at=retrieved, vintage=""))
    t = pd.DataFrame(out)
    if len(t) and t.duplicated(["entity", "variable", "ts_utc"]).any():
        raise RuntimeError("an (entity, variable, ts_utc) is given twice")
    return t


def main(argv=None):
    ap = argparse.ArgumentParser(description="EIA's natural gas vehicle, lease and plant, pipeline fuel and deliveries by state, a year")
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
        if s.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("a row on two pages")
        s = s[ip.SERIES_COLS]
        span = f"{s['ts_utc'].min()[:4]} to {s['ts_utc'].max()[:4]}"
        header = [
            "Energy Research Warehouse (ERW): EIA, natural gas consumption by state: vehicle fuel, lease and plant fuel, pipeline fuel and the volume delivered to consumers, a year (session 2164)",
            "Shape: series (docs/datastandard.md v0). entity eia_gas_other_uses:<process>:<area>; variable consumption_vehicle_fuel, consumption_lease_and_plant_fuel, consumption_pipeline_fuel "
            "or delivered_to_consumers (which holds residential, commercial, industrial, electric power and vehicle fuel: leave it out of a sum); unit MMcf; ts_utc the year's 1 January; freq P1Y; node EIA's series name.",
            f"A figure EIA withholds has no row; nothing is filled. Years {span}; {total:,} records of EIA's, {len(s):,} with a value. Lease and plant fuel is the nation's only. The latest year may be partial (rows a year: " + "; ".join(f"{y} {n}" for y, n in s.groupby(s.ts_utc.str[:4]).size().tail(2).items()) + "). Residential, commercial, industrial and electric power are eia_gas_consumption_state_monthly's.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia_gas_other_uses_state.py; {asked[0]} requests of {CEILING}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Energy Information Administration, Natural Gas Annual, consumption by end use and state (API v2, route natural-gas/cons/sum), {PAGE}",
            f"  access: {API}data/?frequency=annual&data[]=value&facets[process][]=VDV&facets[process][]=VGL&facets[process][]=VGP&facets[process][]=VGT&start={args.first}",
            'License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Natural Gas Annual").',
        ]
        ip.write_snapshot(s, NAME, header, log, ip.SERIES_COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Energy Information Administration (EIA)",
                                    report="Natural Gas Annual, consumption by end use and state: vehicle, lease and plant, pipeline fuel, deliveries (API v2)", report_url=PAGE, document_list=API,
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
