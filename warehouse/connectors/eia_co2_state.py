#!/usr/bin/env python3
"""EIA's energy-related CO2 emissions by state, sector and fuel, a year (session 530).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/eia_co2_state_annual.csv, from the U.S.
Energy Information Administration's API v2, route co2-emissions/co2-emissions-aggregates (State Energy-Related Carbon
Dioxide Emissions, 1970 on):

    https://api.eia.gov/v2/co2-emissions/co2-emissions-aggregates/data/?frequency=annual&data[]=value&start=1970

    entity    eia_co2:<state>:<sectorId>:<fuelId>, EIA's codes: sectors CC, EC, IC, RC, TC (commercial, electric power,
              industrial, residential, transportation) and TT (all), fuels CO, NG, PE (coal, natural gas, petroleum) and
              TO (all): a sum takes one level and leaves TT and TO out
    variable  co2 (tCO2: EIA's million metric tons of CO2 times 1,000,000)
    ts_utc    the year's 1 January at 00:00:00Z; freq P1Y; geo US-<state> (US for the U.S.); node EIA's names

A blank has no row; nothing is filled. A unit not in the map stops the run; so does a key given twice.

    python warehouse/connectors/eia_co2_state.py [--offline | --fresh]

Ceiling: 17 requests a run (pages of 5,000, 3 seconds apart; about 14 pages from 1970; a page an earlier run saved in
warehouse/raw is reused unless --fresh; --offline asks nothing). License: public (EIA, record 1 of license_reads.csv; cite
"U.S. Energy Information Administration, State Energy-Related Carbon Dioxide Emissions").
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

NAME = "eia_co2_state_annual"
CONNECTOR = "eia_co2_state"
SOURCE = "eia:co2-emissions/co2-emissions-aggregates"
API = "https://api.eia.gov/v2/co2-emissions/co2-emissions-aggregates/"
PAGE = "https://www.eia.gov/environment/emissions/state/"
CEILING, PAUSE, RETRY_WAIT = 17, 3, 60
FIRST = "1970"
UNITS = {"million metric tons of co2": ("tCO2", 1e6)}
STATES = set("AK AL AR AZ CA CO CT DC DE FL GA HI IA ID IL IN KS KY LA MA MD ME MI MN MO MS MT NC ND NE NH NJ NM NV NY OH "
             "OK OR PA RI SC SD TN TX UT VA VT WA WI WV WY".split())


def text(v):
    return "" if v is None or (isinstance(v, float) and pd.isna(v)) else str(v).strip()


def rows(data, url, retrieved):
    out = []
    for r in data:
        v = pd.to_numeric(r.get("value"), errors="coerce")
        if pd.isna(v):
            continue
        u = text(r.get("value-units")).lower()
        if u not in UNITS:
            raise RuntimeError(f"a unit not in the map: {r.get('value-units')!r}")
        unit, factor = UNITS[u]
        st, sec, fuel = text(r.get("stateId")), text(r.get("sectorId")), text(r.get("fuelId"))
        if not st or not sec or not fuel:
            raise RuntimeError(f"a record with no state, sector or fuel: {r}")
        year = int(r["period"])
        name = ", ".join(x for x in (text(r.get("state-name")), text(r.get("sector-name")), text(r.get("fuel-name"))) if x)
        out.append(dict(entity=f"eia_co2:{st}:{sec}:{fuel}", variable="co2", ts_utc=f"{year}-01-01T00:00:00Z",
                        value=float(v) * factor, unit=unit, freq="P1Y", geo=f"US-{st}" if st in STATES else "US", market="",
                        node=name, source=SOURCE, source_url=url, retrieved_at=retrieved, vintage=""))
    t = pd.DataFrame(out)
    if len(t) and t.duplicated(["entity", "variable", "ts_utc"]).any():
        raise RuntimeError("an (entity, variable, ts_utc) is given twice")
    return t


def main(argv=None):
    ap = argparse.ArgumentParser(description="EIA's energy-related CO2 emissions by state, sector and fuel, a year")
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
            body, url = get({"api_key": key, "frequency": "annual", "data[]": "value", "start": FIRST, "length": 5000,
                             "offset": offset, "sort[0][column]": "period", "sort[0][direction]": "asc",
                             "sort[1][column]": "stateId", "sort[1][direction]": "asc",
                             "sort[2][column]": "sectorId", "sort[2][direction]": "asc",
                             "sort[3][column]": "fuelId", "sort[3][direction]": "asc"})
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
            "Energy Research Warehouse (ERW): EIA, energy-related CO2 emissions by state, sector and fuel, a year (session 530)",
            "Shape: series (docs/datastandard.md v0). entity eia_co2:<state>:<sectorId>:<fuelId>; variable co2 (tCO2, EIA's million metric tons times 1,000,000); ts_utc the year's 1 January; freq P1Y. "
            "Sectors CC, EC, IC, RC, TC and TT (all); fuels CO, NG, PE and TO (all): a sum takes one level and leaves TT and TO out.",
            f"A blank has no row; nothing is filled. Years {span}; {total:,} records of EIA's, {len(s):,} with a value.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia_co2_state.py; {asked[0]} requests of {CEILING}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Energy Information Administration, State Energy-Related Carbon Dioxide Emissions (API v2, route co2-emissions/co2-emissions-aggregates), {PAGE}",
            f"  access: {API}data/?frequency=annual&data[]=value&start={FIRST}",
            'License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, State Energy-Related Carbon Dioxide Emissions").',
        ]
        ip.write_snapshot(s, NAME, header, log, ip.SERIES_COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Energy Information Administration (EIA)",
                                    report="State Energy-Related Carbon Dioxide Emissions (API v2)", report_url=PAGE, document_list=API,
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
