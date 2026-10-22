#!/usr/bin/env python3
"""EIA's weekly heating oil and propane prices, residential and wholesale, by state and PADD (session 605, a public
source chosen by the chain's rule).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/eia_heating_fuel_prices_weekly.csv, from the
U.S. Energy Information Administration's API v2, route petroleum/pri/wfr (the State Heating Oil and Propane Program,
weekly, in the heating season, October to March):

    https://api.eia.gov/v2/petroleum/pri/wfr/data/?frequency=weekly&data[]=value&start=2012-01-01

    entity    eia_heating_price:<series>, EIA's series id (one a product, process and area)
    variable  residential_price (PRS) or wholesale_price (PWR)
    value     USD/gal (EIA's dollars per gallon); ts_utc EIA's week date at 00:00:00Z; freq P1W; geo US-<state> for a state,
              US for the U.S. and the PADDs; node EIA's series name (heating oil or propane)

A blank has no row; nothing is filled; the weeks outside the heating season have no rows, as EIA publishes none. A unit,
process or area not in the map stops the run; so does a key given twice.

    python warehouse/connectors/eia_heating_fuel_prices.py [--from 2012-01-01] [--offline | --fresh]

Ceiling: 13 requests a run (pages of 5,000, 3 seconds apart; a page an earlier run saved in warehouse/raw is reused unless
--fresh; --offline asks nothing). License: public (EIA, record 1 of license_reads.csv; cite "U.S. Energy Information
Administration, Heating Oil and Propane Update").
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

NAME = "eia_heating_fuel_prices_weekly"
CONNECTOR = "eia_heating_fuel_prices"
SOURCE = "eia:petroleum/pri/wfr"
API = "https://api.eia.gov/v2/petroleum/pri/wfr/"
PAGE = "https://www.eia.gov/petroleum/heatingoilpropane/"
CEILING, PAUSE, RETRY_WAIT = 13, 3, 60   # session 605: seven of 20 went to the probes (BOEM and EIA)
FIRST = "2012-01-01"
PROCESSES = {"PRS": "residential_price", "PWR": "wholesale_price"}
AREAS = {"NUS", "R10", "R1X", "R1Y", "R1Z", "R20", "R30", "R40", "R50"}   # and any state, S<state>
UNITS = {"$/gal": ("USD/gal", 1.0)}


def rows(data, url, retrieved):
    out = []
    for r in data:
        if r.get("process") not in PROCESSES:
            raise RuntimeError(f"a process not asked for: {r.get('process')!r}")
        area = str(r.get("duoarea"))
        if not (area in AREAS or (len(area) == 3 and area.startswith("S"))):
            raise RuntimeError(f"an area not understood: {r.get('duoarea')!r}")
        v = pd.to_numeric(r.get("value"), errors="coerce")
        if pd.isna(v):
            continue
        u = str(r.get("units", "")).strip().lower()
        if u not in UNITS:
            raise RuntimeError(f"a unit not in the map: {r.get('units')!r}")
        unit, factor = UNITS[u]
        day = str(r["period"])[:10]
        dt.date.fromisoformat(day)
        out.append(dict(entity=f"eia_heating_price:{str(r['series']).strip()}", variable=PROCESSES[r["process"]],
                        ts_utc=f"{day}T00:00:00Z", value=float(v) * factor, unit=unit, freq="P1W",
                        geo=f"US-{area[1:]}" if area.startswith("S") else "US", market="",
                        node=str(r.get("series-description") or "").strip(), source=SOURCE, source_url=url,
                        retrieved_at=retrieved, vintage=""))
    t = pd.DataFrame(out)
    if len(t) and t.duplicated(["entity", "variable", "ts_utc"]).any():
        raise RuntimeError("an (entity, variable, ts_utc) is given twice")
    return t


def main(argv=None):
    ap = argparse.ArgumentParser(description="EIA's weekly heating oil and propane prices")
    ap.add_argument("--from", dest="first", default=FIRST, help="the first week, YYYY-MM-DD")
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
            body, url = get({"api_key": key, "frequency": "weekly", "data[]": "value", "facets[process][]": list(PROCESSES),
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
        span = f"{s['ts_utc'].min()[:10]} to {s['ts_utc'].max()[:10]}"
        header = [
            "Energy Research Warehouse (ERW): EIA, weekly heating oil and propane prices, residential and wholesale, by state and PADD, the heating season (session 605)",
            "Shape: series (docs/datastandard.md v0). entity eia_heating_price:<series>; variable residential_price or wholesale_price; unit USD/gal; ts_utc EIA's week date; freq P1W; "
            "node EIA's series name (heating oil or propane). Weeks outside the heating season have no rows, as EIA publishes none.",
            f"A blank has no row; nothing is filled. Weeks {span}; {total:,} records of EIA's, {len(s):,} rows.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia_heating_fuel_prices.py; {asked[0]} requests of {CEILING}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Energy Information Administration, Heating Oil and Propane Update (API v2, route petroleum/pri/wfr), {PAGE}",
            f"  access: {API}data/?frequency=weekly&data[]=value&facets[process][]=PRS&facets[process][]=PWR&start={args.first}",
            'License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Heating Oil and Propane Update").',
        ]
        ip.write_snapshot(s, NAME, header, log, ip.SERIES_COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Energy Information Administration (EIA)",
                                    report="Heating Oil and Propane Update, weekly prices (API v2)", report_url=PAGE, document_list=API,
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
