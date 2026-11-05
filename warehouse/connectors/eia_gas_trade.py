#!/usr/bin/env python3
"""EIA's natural gas exports and imports by country, volumes and prices, a month (session 625, made from session
622's eia_padd_movements.py).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/eia_gas_trade_country_monthly.csv, from the
U.S. Energy Information Administration's API v2, two routes of Natural Gas Monthly:

    https://api.eia.gov/v2/natural-gas/move/expc/data/?frequency=monthly&data[]=value   (exports by country)
    https://api.eia.gov/v2/natural-gas/move/impc/data/?frequency=monthly&data[]=value   (imports by country)

    entity    eia_gas_trade:<series>, EIA's series id (one a mode, country and unit)
    variable  volume (MMcf, EIA's million cubic feet in the month) or price (USD/Mcf, dollars per thousand cubic feet)
    ts_utc    the month's first day at 00:00:00Z; freq P1M; geo US; node EIA's series name, which names the mode (by
              pipeline, by vessel as LNG, by truck, compressed, re-exports) and the country of destination or origin

The mode is EIA's process code, kept in the series id and named in the node; EIA's area NUS-<country> (NUS-Z00 the
U.S. total) likewise. A blank has no row; nothing is filled. A unit or area not in the map stops the run; so does a key
given twice.

    python warehouse/connectors/eia_gas_trade.py [--from 1973-01] [--offline | --fresh]

Ceiling: 20 requests a run (pages of 5,000, 3 seconds apart; a page an earlier run saved in warehouse/raw is reused
unless --fresh; --offline asks nothing). License: public (EIA, record 1 of license_reads.csv; cite "U.S. Energy
Information Administration, Natural Gas Monthly").
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

NAME = "eia_gas_trade_country_monthly"
CONNECTOR = "eia_gas_trade"
ROUTES = {"natural-gas/move/expc": "exports", "natural-gas/move/impc": "imports"}
SOURCES = {r: f"eia:{r}" for r in ROUTES}
BASE = "https://api.eia.gov/v2/"
PAGE = "https://www.eia.gov/naturalgas/monthly/"
CEILING, PAUSE, RETRY_WAIT = 20, 3, 60   # session 625: four of 30 went to the probes
FIRST = "1973-01"
AREA = re.compile(r"^NUS-(Z00|ZXC|N[A-Z0-9]{2})$")
UNITS = {"mmcf": ("MMcf", 1.0, "volume"), "$/mcf": ("USD/Mcf", 1.0, "price")}


def rows(data, url, retrieved, route):
    out = []
    for r in data:
        if not AREA.match(str(r.get("duoarea"))):
            raise RuntimeError(f"an area not understood: {r.get('duoarea')!r}")
        v = pd.to_numeric(r.get("value"), errors="coerce")
        if pd.isna(v):
            continue
        u = str(r.get("units", "")).strip().lower()
        if u not in UNITS:
            raise RuntimeError(f"a unit not in the map: {r.get('units')!r}")
        unit, factor, variable = UNITS[u]
        month = str(r["period"])[:7]
        dt.date.fromisoformat(month + "-01")
        out.append(dict(entity=f"eia_gas_trade:{str(r['series']).strip()}", variable=variable,
                        ts_utc=f"{month}-01T00:00:00Z", value=float(v) * factor, unit=unit, freq="P1M", geo="US", market="",
                        node=str(r.get("series-description") or "").strip(), source=SOURCES[route], source_url=url,
                        retrieved_at=retrieved, vintage=""))
    t = pd.DataFrame(out)
    if len(t) and t.duplicated(["entity", "variable", "ts_utc"]).any():
        raise RuntimeError("an (entity, variable, ts_utc) is given twice")
    return t


def main(argv=None):
    ap = argparse.ArgumentParser(description="EIA's natural gas exports and imports by country, a month")
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
        windows = [(args.first, None)]
        for route in ROUTES:
            api = BASE + route + "/"
            records[route] = 0
            for first, last in windows:
                offset, total = 0, None
                while True:
                    params = {"api_key": key, "frequency": "monthly", "data[]": "value", "start": first}
                    if last:
                        params["end"] = last
                    params.update({"length": 5000, "offset": offset, "sort[0][column]": "period", "sort[0][direction]": "asc",
                                   "sort[1][column]": "series", "sort[1][direction]": "asc"})
                    body, url = get(api, params)
                    resp = body["response"]
                    total = int(resp["total"])
                    frames.append(rows(resp["data"], url.split("&length")[0], retrieved, route))
                    offset += len(resp["data"])
                    if offset >= total or len(resp["data"]) < 5000:
                        break
                if offset != total:
                    raise RuntimeError(f"{route}, {first} to {last or 'the latest'}: {offset:,} rows read of the {total:,} EIA counts")
                records[route] += total
                log(f"  {route}, {first} to {last or 'the latest'}: {total:,} records")
        s = pd.concat([f for f in frames if len(f)], ignore_index=True)
        if s.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("a row on two pages, or a series in both routes")
        s = s[ip.SERIES_COLS]
        span = f"{s['ts_utc'].min()[:7]} to {s['ts_utc'].max()[:7]}"
        header = [
            "Energy Research Warehouse (ERW): EIA, natural gas exports and imports by country, volumes and prices, a month (session 625)",
            "Shape: series (docs/datastandard.md v0). entity eia_gas_trade:<series>; variable volume (MMcf) or price (USD/Mcf); ts_utc the month's first day; freq P1M; "
            "node EIA's series name (the mode and the country). The countries are parts of the U.S. total (NUS-Z00) of the same mode: a sum takes one level.",
            f"A blank has no row; nothing is filled. Months {span}; records of EIA's: exports {records['natural-gas/move/expc']:,}, imports {records['natural-gas/move/impc']:,}; {len(s):,} rows.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia_gas_trade.py; {asked[0]} requests of {CEILING}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCES['natural-gas/move/expc']} U.S. Energy Information Administration, Natural Gas Monthly, exports by country (API v2, route natural-gas/move/expc), {PAGE}",
            f"Source: {SOURCES['natural-gas/move/impc']} U.S. Energy Information Administration, Natural Gas Monthly, imports by country (API v2, route natural-gas/move/impc), {PAGE}",
            f"  access: {BASE}<route>/data/?frequency=monthly&data[]=value&start={args.first}",
            'License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Natural Gas Monthly").',
        ]
        ip.write_snapshot(s, NAME, header, log, ip.SERIES_COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCES[r], publisher="U.S. Energy Information Administration (EIA)",
                                    report=f"Natural Gas Monthly, {ROUTES[r]} by country (API v2)", report_url=PAGE,
                                    document_list=BASE + r + "/", license="public", tables=[NAME]) for r in ROUTES])
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
