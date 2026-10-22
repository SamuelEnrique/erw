#!/usr/bin/env python3
"""EIA's crude oil imports by country of origin, destination and grade, a month (session 632).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/eia_crude_imports_detail_monthly.csv, from
the U.S. Energy Information Administration's API v2, route crude-oil-imports (Form EIA-814, company level imports), the
origins that are countries:

    https://api.eia.gov/v2/crude-oil-imports/data/?frequency=monthly&data[]=quantity&facets[originType][]=CTY&start=2011-01

    entity    eia_crude_imports:<originId>:<destinationId>:<gradeId>, EIA's ids (CTY_SA for Saudi Arabia; US, a PADD,
              a port, a state or a refinery as the destination; LSW, LSO, MED, HSW, HSO for the grade)
    variable  imports (kbbl, EIA's thousand barrels in the month)
    ts_utc    the month's first day at 00:00:00Z; freq P1M; geo US; node "<origin> to <destination> (<destination
              type>), <grade>" in EIA's names

The destinations nest (a refinery within its state and PADD, a port within its state and PADD, all within the U.S.):
a sum takes one destination type. EIA's region, OPEC and world origins are sums of the countries and are not taken.
A blank has no row; nothing is filled. A unit, origin type, destination type or grade not in the map stops the run;
so does a key given twice.

    python warehouse/connectors/eia_crude_imports_detail.py [--from 2011-01] [--offline | --fresh]

Ceiling: 37 requests a run (pages of 5,000, 3 seconds apart; a page an earlier run saved in warehouse/raw is reused
unless --fresh; --offline asks nothing). From 2011: the country origins hold 191,815 records from 2009, beyond session
632's ceiling. License: public (EIA, record 1 of license_reads.csv; cite "U.S. Energy Information Administration,
Company Level Imports").
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

NAME = "eia_crude_imports_detail_monthly"
CONNECTOR = "eia_crude_imports_detail"
SOURCE = "eia:crude-oil-imports"
API = "https://api.eia.gov/v2/crude-oil-imports/"
PAGE = "https://www.eia.gov/petroleum/imports/companylevel/"
CEILING, PAUSE, RETRY_WAIT = 37, 3, 60   # session 632: three of 40 went to the probes
FIRST = "2011-01"
DESTINATIONS = {"US", "PP", "PS", "PT", "RP", "RS", "RF"}   # the U.S., port PADD, port state, port, refinery PADD, state, refinery
GRADES = {"LSW", "LSO", "MED", "HSW", "HSO"}
UNITS = {"thousand barrels": ("kbbl", 1.0)}


def text(v):
    return "" if v is None or (isinstance(v, float) and pd.isna(v)) else str(v).strip()


def rows(data, url, retrieved):
    out = []
    for r in data:
        if text(r.get("originType")) != "CTY":
            raise RuntimeError(f"an origin not a country: {r.get('originType')!r}")
        if text(r.get("destinationType")) not in DESTINATIONS:
            raise RuntimeError(f"a destination type not understood: {r.get('destinationType')!r}")
        if text(r.get("gradeId")) not in GRADES:
            raise RuntimeError(f"a grade not understood: {r.get('gradeId')!r}")
        v = pd.to_numeric(r.get("quantity"), errors="coerce")
        if pd.isna(v):
            continue
        u = text(r.get("quantity-units")).lower()
        if u not in UNITS:
            raise RuntimeError(f"a unit not in the map: {r.get('quantity-units')!r}")
        unit, factor = UNITS[u]
        month = text(r.get("period"))[:7]
        dt.date.fromisoformat(month + "-01")
        out.append(dict(entity=f"eia_crude_imports:{text(r['originId'])}:{text(r['destinationId'])}:{text(r['gradeId'])}",
                        variable="imports", ts_utc=f"{month}-01T00:00:00Z", value=float(v) * factor, unit=unit, freq="P1M",
                        geo="US", market="",
                        node=f"{text(r.get('originName'))} to {text(r.get('destinationName'))} ({text(r.get('destinationTypeName'))}), {text(r.get('gradeName'))}",
                        source=SOURCE, source_url=url, retrieved_at=retrieved, vintage=""))
    t = pd.DataFrame(out)
    if len(t) and t.duplicated(["entity", "variable", "ts_utc"]).any():
        raise RuntimeError("an (entity, variable, ts_utc) is given twice")
    return t


def main(argv=None):
    ap = argparse.ArgumentParser(description="EIA's crude oil imports by country, destination and grade, a month")
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
            body, url = get({"api_key": key, "frequency": "monthly", "data[]": "quantity", "facets[originType][]": "CTY",
                             "start": args.first, "length": 5000, "offset": offset,
                             "sort[0][column]": "period", "sort[0][direction]": "asc",
                             "sort[1][column]": "originId", "sort[1][direction]": "asc",
                             "sort[2][column]": "destinationId", "sort[2][direction]": "asc",
                             "sort[3][column]": "gradeId", "sort[3][direction]": "asc"})
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
        span = f"{s['ts_utc'].min()[:7]} to {s['ts_utc'].max()[:7]}"
        header = [
            "Energy Research Warehouse (ERW): EIA, crude oil imports by country of origin, destination and grade, a month (session 632)",
            "Shape: series (docs/datastandard.md v0). entity eia_crude_imports:<originId>:<destinationId>:<gradeId>; variable imports (kbbl); ts_utc the month's first day; freq P1M; "
            "node the origin, destination (with its type) and grade in EIA's names. Destinations nest (refinery, state, PADD, the U.S.): a sum takes one destination type. Countries only: EIA's region, OPEC and world origins are their sums.",
            f"A blank has no row; nothing is filled. Months {span}; {total:,} records of EIA's, {len(s):,} rows.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia_crude_imports_detail.py; {asked[0]} requests of {CEILING}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Energy Information Administration, Company Level Imports, crude oil imports by country to destination (API v2, route crude-oil-imports, Form EIA-814), {PAGE}",
            f"  access: {API}data/?frequency=monthly&data[]=quantity&facets[originType][]=CTY&start={args.first}",
            'License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Company Level Imports").',
        ]
        ip.write_snapshot(s, NAME, header, log, ip.SERIES_COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Energy Information Administration (EIA)",
                                    report="Company Level Imports, crude oil imports by country to destination (API v2, Form EIA-814)",
                                    report_url=PAGE, document_list=API, license="public", tables=[NAME])])
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
