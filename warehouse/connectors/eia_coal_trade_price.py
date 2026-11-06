#!/usr/bin/env python3
"""EIA's price of U.S. coal exports and imports by country, rank and customs district, a year (session 573).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/eia_coal_trade_price_annual.csv, from the U.S.
Energy Information Administration's API v2, route coal/exports-imports-quantity-price (annual, 2000 on):

    https://api.eia.gov/v2/coal/exports-imports-quantity-price/data/?frequency=annual&data[]=price&start=2000

    entity    eia_coal_trade:<exportImportType>:<coalRankId>:<countryId>:<customsDistrictId>, EIA's codes
    variable  price (USD/short_ton, EIA's dollars per short ton); EIA's quantities in short tons are not taken
    ts_utc    the year's 1 January at 00:00:00Z; freq P1Y; geo US; node EIA's names

A figure EIA withholds has no row; nothing is filled. A unit not in the map stops the run; so does a key given twice.

    python warehouse/connectors/eia_coal_trade_price.py [--offline | --fresh]

Ceiling: 18 requests a run (pages of 5,000, 3 seconds apart; a page an earlier run saved in warehouse/raw is reused unless
--fresh; --offline asks nothing). License: public (EIA, record 1 of license_reads.csv; cite "U.S. Energy Information
Administration, Quarterly Coal Report").
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

NAME = "eia_coal_trade_price_annual"
CONNECTOR = "eia_coal_trade_price"
SOURCE = "eia:coal/exports-imports-quantity-price"
API = "https://api.eia.gov/v2/coal/exports-imports-quantity-price/"
PAGE = "https://www.eia.gov/coal/production/quarterly/"
CEILING, PAUSE, RETRY_WAIT = 18, 3, 60   # session 573: two of 20 went to the probes
FIRST = "2000"
UNITS = {"dollars per short ton": ("USD/short_ton", 1.0)}
STATES = set("AK AL AR AZ CA CO CT DC DE FL GA HI IA ID IL IN KS KY LA MA MD ME MI MN MO MS MT NC ND NE NH NJ NM NV NY OH "
             "OK OR PA RI SC SD TN TX UT VA VT WA WI WV WY".split())


def text(v):
    return "" if v is None or (isinstance(v, float) and pd.isna(v)) else str(v).strip()


def rows(data, url, retrieved):
    out = []
    for r in data:
        v = pd.to_numeric(r.get("price"), errors="coerce")
        if pd.isna(v):
            continue
        u = text(r.get("price-units")).lower()
        if u not in UNITS:
            raise RuntimeError(f"a unit not in the map: {r.get('price-units')!r}")
        unit, factor = UNITS[u]
        keys = [text(r.get(k)) for k in ['exportImportType', 'coalRankId', 'countryId', 'customsDistrictId']]
        if not all(keys):
            raise RuntimeError(f"a record with a key field blank: {r}")
        period = text(r.get("period"))
        year = int(period[:4])
        ts = f"{year}-01-01T00:00:00Z" if len(period) == 4 else f"{year}-{(int(period[-1]) - 1) * 3 + 1:02d}-01T00:00:00Z"
        out.append(dict(entity=f"eia_coal_trade:{keys[0]}:{keys[1]}:{keys[2]}:{keys[3]}", variable="price", ts_utc=ts, value=float(v) * factor, unit=unit,
                        freq="P1Y" if len(period) == 4 else "P3M", geo="US", market="", node=", ".join(x for x in (text(r.get("exportImportType")), text(r.get("countryDescription")), text(r.get("coalRankDescription")), text(r.get("customsDistrictDescription"))) if x), source=SOURCE,
                        source_url=url, retrieved_at=retrieved, vintage=""))
    t = pd.DataFrame(out)
    if len(t) and t.duplicated(["entity", "variable", "ts_utc"]).any():
        raise RuntimeError("an (entity, variable, ts_utc) is given twice")
    return t


def main(argv=None):
    ap = argparse.ArgumentParser(description="EIA's price of coal exports and imports, a year")
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
            body, url = get({"api_key": key, "frequency": "annual", "data[]": "price", "start": FIRST, "length": 5000,
                             "offset": offset, "sort[0][column]": "period", "sort[0][direction]": "asc",
                             "sort[1][column]": "exportImportType", "sort[1][direction]": "asc",
                             "sort[2][column]": "countryId", "sort[2][direction]": "asc",
                             "sort[3][column]": "coalRankId", "sort[3][direction]": "asc",
                             "sort[4][column]": "customsDistrictId", "sort[4][direction]": "asc"})
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
            "Energy Research Warehouse (ERW): EIA, the price of U.S. coal exports and imports by country, rank and customs district, a year (session 573)",
            "Shape: series (docs/datastandard.md v0). entity eia_coal_trade:<exportImportType>:<coalRankId>:<countryId>:<customsDistrictId>; variable price (USD/short_ton); ts_utc the year's 1 January; freq P1Y; "
            "geo US-<state> for a state, US for a region or the U.S.; node EIA's area and market names.",
            f"A figure EIA withholds has no row; nothing is filled. EIA's sales (short tons) are not taken. Years {span}; {total:,} records of EIA's, {len(s):,} with a price.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia_coal_trade_price.py; {asked[0]} requests of {CEILING}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Energy Information Administration, Quarterly Coal Report, exports and imports (API v2, route coal/exports-imports-quantity-price), {PAGE}",
            f"  access: {API}data/?frequency=annual&data[]=price&start={FIRST}",
            'License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Quarterly Coal Report").',
        ]
        ip.write_snapshot(s, NAME, header, log, ip.SERIES_COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Energy Information Administration (EIA)",
                                    report="Quarterly Coal Report, exports and imports (API v2)", report_url=PAGE, document_list=API,
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
