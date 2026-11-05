#!/usr/bin/env python3
"""EIA's coal production and employees by mine, a year (session 694, chain 045: a public source the ERW did not hold,
taken where the chain's large-load tariffs wait on an OpenEI key).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/eia_coal_mine_production_annual.csv, from
the U.S. Energy Information Administration's API v2, route coal/mine-production (Form EIA-7A and MSHA Form 7000-2, the
Annual Coal Report's mine-level file):

    https://api.eia.gov/v2/coal/mine-production/data/?frequency=annual&data[]=production&data[]=average-employees
        &data[]=latitude&data[]=longitude&data[]=operating-company&data[]=refuse-flag&start=2001

    entity    eia_coal_mine:<mineMSHAId>:<coalRankId>:<mineTypeId>, one mine of MSHA's numbering, its coal rank and its
              mine type as EIA gives them (a preparation plant may report as surface and as underground)
    variable  production (short_ton), employees (count, EIA's average-employees). EIA's labor hours are not taken: the
              vocabulary's `hour` is an hour of the day, not a quantity of work (session 685)
    ts_utc    the year's 1 January at 00:00:00Z; freq P1Y; geo US-<state> (EIA's regions KYE, KYW, PAA, PAB, WVN and WVS
              are put in their state; x_state keeps EIA's code); node the mine's name
    x_*       EIA's own fields: MSHA id, state, county, supply region, rank, mine type, status, operating company,
              latitude, longitude, refuse flag

A figure EIA leaves empty has no row; a production of 0 that EIA gives is kept (a preparation plant, a mine idle all
year). Nothing is filled. A unit not in the map stops the run; so does a key given twice.

    python warehouse/connectors/eia_coal_mine_production.py [--offline | --fresh]

Ceiling: 12 requests a run (pages of 5,000, 3 seconds apart; a page an earlier run saved in warehouse/raw is reused unless
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

NAME = "eia_coal_mine_production_annual"
CONNECTOR = "eia_coal_mine_production"
SOURCE = "eia:coal/mine-production"
API = "https://api.eia.gov/v2/coal/mine-production/"
PAGE = "https://www.eia.gov/coal/data.php"
CEILING, PAUSE, RETRY_WAIT = 12, 3, 60
FIRST = "2001"
# EIA's data column -> (the ERW's variable, {EIA's unit, lower case: (the ERW's unit, factor)})
DATA = {"production": ("production", {"short tons": ("short_ton", 1.0)}),
        "average-employees": ("employees", {"number of employees": ("count", 1.0)})}
FIELDS = ["latitude", "longitude", "operating-company", "refuse-flag"]
# EIA's coal regions within a state (Kentucky East and West, Pennsylvania Anthracite and Bituminous, West Virginia North
# and South): the mine's geo is its state, x_state keeps EIA's code
SUBSTATE = {"KYE": "KY", "KYW": "KY", "PAA": "PA", "PAB": "PA", "WVN": "WV", "WVS": "WV"}
X_COLS = ["x_msha_id", "x_state", "x_county", "x_supply_region", "x_rank", "x_mine_type", "x_status", "x_operator",
          "x_latitude", "x_longitude", "x_refuse"]


def text(v):
    return "" if v is None or (isinstance(v, float) and pd.isna(v)) else str(v).strip()


def slug(v):
    return re.sub(r"[^A-Za-z0-9]+", "_", v).strip("_")


def rows(data, url, retrieved):
    out = []
    for r in data:
        mine, rank, kind, state = text(r.get("mineMSHAId")), text(r.get("coalRankId")), text(r.get("mineTypeId")), text(r.get("stateId"))
        if not mine or not rank or not kind or not state:
            raise RuntimeError(f"a record with no MSHA id, rank, mine type or state: {r}")
        year = int(r["period"])
        base = dict(entity=f"eia_coal_mine:{mine}:{slug(rank)}:{slug(kind)}", ts_utc=f"{year}-01-01T00:00:00Z", freq="P1Y",
                    geo=f"US-{SUBSTATE.get(state, state)}", market="", node=text(r.get("mineName")), source=SOURCE, source_url=url,
                    retrieved_at=retrieved, vintage="", x_msha_id=mine, x_state=state, x_county=text(r.get("mineCountyName")),
                    x_supply_region=text(r.get("supplyRegionDescription")), x_rank=text(r.get("coalRankDescription")),
                    x_mine_type=text(r.get("mineTypeDescription")), x_status=text(r.get("mineStatusDescription")),
                    x_operator=text(r.get("operating-company")), x_latitude=text(r.get("latitude")),
                    x_longitude=text(r.get("longitude")), x_refuse=text(r.get("refuse-flag")))
        for col, (var, units) in DATA.items():
            v = pd.to_numeric(r.get(col), errors="coerce")
            if pd.isna(v):
                continue
            u = text(r.get(f"{col}-units")).lower()
            if u not in units:
                raise RuntimeError(f"a unit not in the map for {col}: {r.get(f'{col}-units')!r}")
            unit, factor = units[u]
            out.append(dict(base, variable=var, value=float(v) * factor, unit=unit))
    t = pd.DataFrame(out)
    if len(t) and t.duplicated(["entity", "variable", "ts_utc"]).any():
        d = t[t.duplicated(["entity", "variable", "ts_utc"], keep=False)].head(4)
        raise RuntimeError(f"an (entity, variable, ts_utc) is given twice: {d[['entity', 'variable', 'ts_utc', 'value']].to_dict('records')}")
    return t


def main(argv=None):
    ap = argparse.ArgumentParser(description="EIA's coal production and employees by mine, a year")
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
            body, url = get({"api_key": key, "frequency": "annual", "data[]": list(DATA) + FIELDS, "start": FIRST, "length": 5000,
                             "offset": offset, "sort[0][column]": "period", "sort[0][direction]": "asc",
                             "sort[1][column]": "mineMSHAId", "sort[1][direction]": "asc",
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
        cols = ip.SERIES_COLS + X_COLS
        s = s[cols]
        span = f"{s['ts_utc'].min()[:4]} to {s['ts_utc'].max()[:4]}"
        header = [
            "Energy Research Warehouse (ERW): EIA, coal production and employees by mine, a year (session 694)",
            "Shape: series (docs/datastandard.md v0). entity eia_coal_mine:<mineMSHAId>:<coalRankId>:<mineTypeId>; variables production (short_ton), employees (count, EIA's average employees); "
            "ts_utc the year's 1 January; freq P1Y; geo US-<state> (EIA's regions KYE, KYW, PAA, PAB, WVN, WVS in their state); node the mine's name; x_* EIA's own fields (MSHA id, state, county, supply region, rank, mine type, status, operating company, latitude, longitude, refuse flag).",
            f"A figure EIA leaves empty has no row; a production of 0 EIA gives is kept; nothing is filled. EIA's labor hours are not taken. Years {span}; {total:,} records of EIA's, {len(s):,} rows.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia_coal_mine_production.py; {asked[0]} requests of {CEILING}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Energy Information Administration, Annual Coal Report, mine-level production (Form EIA-7A and MSHA Form 7000-2; API v2, route coal/mine-production), {PAGE}",
            f"  access: {API}data/?frequency=annual&data[]=production&data[]=average-employees&data[]=latitude&data[]=longitude&data[]=operating-company&data[]=refuse-flag&start={FIRST}",
            'License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Annual Coal Report").',
        ]
        ip.write_snapshot(s, NAME, header, log, cols)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Energy Information Administration (EIA)",
                                    report="Annual Coal Report, mine-level production (API v2)", report_url=PAGE, document_list=API,
                                    license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(s):,} rows"))
        print(f"{NAME}: {len(s):,} rows, {s['x_msha_id'].nunique():,} mines, {s['entity'].nunique():,} series, {span}; {asked[0]} requests")
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
