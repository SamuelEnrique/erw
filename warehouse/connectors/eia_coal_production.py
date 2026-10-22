#!/usr/bin/env python3
"""EIA's coal production by producing state, coal rank and mine type, with the mines and their employees, a year
(session 685, chain 044: the gap session 519 left, once the unit vocabulary holds short tons, Decision 50).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/eia_coal_production_annual.csv, from the
U.S. Energy Information Administration's API v2, route coal/aggregate-production (Form EIA-7A and MSHA Form 7000-2, the
Annual Coal Report's state aggregates):

    https://api.eia.gov/v2/coal/aggregate-production/data/?frequency=annual&data[]=production&data[]=number-of-mines
        &data[]=average-employees&start=2001

    entity    eia_coal_production:<stateRegionId>:<coalRankId>:<mineTypeId>, EIA's codes
    variable  production (short_ton), mines (count, EIA's number-of-mines), employees (count, EIA's average-employees).
              EIA's labor hours and productivity are not taken: the vocabulary's `hour` is an hour of the day, not a
              quantity of work
    ts_utc    the year's 1 January at 00:00:00Z; freq P1Y; geo US-<state> for a state, US for a region or the U.S.;
              node EIA's area, rank and mine type names

A figure EIA withholds has no row; nothing is filled. A unit not in the map stops the run; so does a key given twice.

    python warehouse/connectors/eia_coal_production.py [--offline | --fresh]

Ceiling: 8 requests a run (pages of 5,000, 3 seconds apart; a page an earlier run saved in warehouse/raw is reused unless
--fresh; --offline asks nothing). License: public (EIA, record 1 of license_reads.csv; cite "U.S. Energy Information
Administration, Annual Coal Report").
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

NAME = "eia_coal_production_annual"
CONNECTOR = "eia_coal_production"
SOURCE = "eia:coal/aggregate-production"
API = "https://api.eia.gov/v2/coal/aggregate-production/"
PAGE = "https://www.eia.gov/coal/annual/"
CEILING, PAUSE, RETRY_WAIT = 8, 3, 60
FIRST = "2001"
# EIA's data column -> (the ERW's variable, {EIA's unit, lower case: (the ERW's unit, factor)})
DATA = {"production": ("production", {"short tons": ("short_ton", 1.0)}),
        "number-of-mines": ("mines", {"number of mines": ("count", 1.0)}),
        "average-employees": ("employees", {"number of employees": ("count", 1.0)})}
STATES = set("AK AL AR AZ CA CO CT DC DE FL GA HI IA ID IL IN KS KY LA MA MD ME MI MN MO MS MT NC ND NE NH NJ NM NV NY OH "
             "OK OR PA RI SC SD TN TX UT VA VT WA WI WV WY".split())


def text(v):
    return "" if v is None or (isinstance(v, float) and pd.isna(v)) else str(v).strip()


def slug(v):
    return re.sub(r"[^A-Za-z0-9]+", "_", v).strip("_")


def rows(data, url, retrieved):
    out = []
    for r in data:
        area, rank, mine = text(r.get("stateRegionId")), text(r.get("coalRankId")), text(r.get("mineTypeId"))
        if not area or not rank or not mine:
            raise RuntimeError(f"a record with no area, rank or mine type: {r}")
        year = int(r["period"])
        name = " ".join(x for x in (text(r.get("stateRegionDescription")), text(r.get("coalRankDescription")),
                                    text(r.get("mineTypeDescription"))) if x)
        for col, (var, units) in DATA.items():
            v = pd.to_numeric(r.get(col), errors="coerce")
            if pd.isna(v):
                continue
            u = text(r.get(f"{col}-units")).lower()
            if u not in units:
                raise RuntimeError(f"a unit not in the map for {col}: {r.get(f'{col}-units')!r}")
            unit, factor = units[u]
            out.append(dict(entity=f"eia_coal_production:{area}:{slug(rank)}:{slug(mine)}", variable=var,
                            ts_utc=f"{year}-01-01T00:00:00Z", value=float(v) * factor, unit=unit, freq="P1Y",
                            geo=f"US-{area}" if area in STATES else "US", market="", node=name, source=SOURCE,
                            source_url=url, retrieved_at=retrieved, vintage=""))
    t = pd.DataFrame(out)
    if len(t) and t.duplicated(["entity", "variable", "ts_utc"]).any():
        raise RuntimeError("an (entity, variable, ts_utc) is given twice")
    return t


def main(argv=None):
    ap = argparse.ArgumentParser(description="EIA's coal production by state, rank and mine type, a year")
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
            body, url = get({"api_key": key, "frequency": "annual", "data[]": list(DATA), "start": FIRST, "length": 5000,
                             "offset": offset, "sort[0][column]": "period", "sort[0][direction]": "asc",
                             "sort[1][column]": "stateRegionId", "sort[1][direction]": "asc",
                             "sort[2][column]": "coalRankId", "sort[2][direction]": "asc",
                             "sort[3][column]": "mineTypeId", "sort[3][direction]": "asc"})
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
            "Energy Research Warehouse (ERW): EIA, coal production by producing state or region, coal rank and mine type, with the mines and their employees, a year (session 685)",
            "Shape: series (docs/datastandard.md v0). entity eia_coal_production:<stateRegionId>:<coalRankId>:<mineTypeId>; variables production (short_ton), mines (count), employees (count, EIA's average employees); "
            "ts_utc the year's 1 January; freq P1Y; geo US-<state> for a state, US for a region or the U.S.; node EIA's area, rank and mine type names.",
            f"A figure EIA withholds has no row; nothing is filled. EIA's labor hours and productivity are not taken. Years {span}; {total:,} records of EIA's, {len(s):,} rows.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia_coal_production.py; {asked[0]} requests of {CEILING}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Energy Information Administration, Annual Coal Report, state aggregates (Form EIA-7A and MSHA Form 7000-2; API v2, route coal/aggregate-production), {PAGE}",
            f"  access: {API}data/?frequency=annual&data[]=production&data[]=number-of-mines&data[]=average-employees&start={FIRST}",
            'License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Annual Coal Report").',
        ]
        ip.write_snapshot(s, NAME, header, log, ip.SERIES_COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Energy Information Administration (EIA)",
                                    report="Annual Coal Report, state aggregate production (API v2)", report_url=PAGE, document_list=API,
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
