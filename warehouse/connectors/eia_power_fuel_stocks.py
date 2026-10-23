#!/usr/bin/env python3
"""Fuel stocks at power plants: each month's end-of-month stocks of coal, petroleum liquids and petroleum coke held at
U.S. power plants, by state and census region, for the electric power sector and for all sectors (session 927, chain
052: the stocks behind the coal and oil burns that eia_state_generation_monthly records).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/eia_power_fuel_stocks_monthly.csv, from the
U.S. Energy Information Administration's API v2, route electricity/electric-power-operational-data (Form EIA-923), data
column `stocks`:

    https://api.eia.gov/v2/electricity/electric-power-operational-data/data/?frequency=monthly&data[]=stocks
        &facets[fueltypeid][]=COL&facets[fueltypeid][]=PEL&facets[fueltypeid][]=PC
        &facets[sectorid][]=98&facets[sectorid][]=99&start=<FIRST>

    entity    eia_power_stocks:<location>:<sectorid>:<fueltypeid> (location the state's postal code, a census region's code
              such as ENC, or US; sector 98 electric power, 99 all sectors; fuel COL coal excluding waste coal, PEL
              petroleum liquids, PC petroleum coke)
    variable  stocks; unit short_ton (EIA's thousand short tons times 1,000) or kbbl (EIA's thousand barrels)
    ts_utc    the month's first day (EIA's stocks are at the month's end); freq P1M; geo US-<state> for a state, US for
              the U.S., empty for a census region; node "<location>, <sector>, <fuel>" as EIA names them

A record EIA gives without a stocks figure has no row; nothing is filled. A unit not in the map stops the run, as does a
page count that does not reach the API's total or a key given twice.

    python warehouse/connectors/eia_power_fuel_stocks.py [--offline | --fresh]

Ceiling: 14 requests a run (pages of 5,000, 3 seconds apart; a page an earlier run saved in warehouse/raw is reused
unless --fresh; --offline asks nothing). License: public (EIA, record 1 of license_reads.csv; cite "U.S. Energy
Information Administration, Form EIA-923, electric power operational data").
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

NAME = "eia_power_fuel_stocks_monthly"
CONNECTOR = "eia_power_fuel_stocks"
SOURCE = "eia:electricity/electric-power-operational-data:stocks"
API = "https://api.eia.gov/v2/electricity/electric-power-operational-data/data/"
PAGE = "https://www.eia.gov/electricity/data/browser/"
FUELS, SECTORS, FIRST = ["COL", "PEL", "PC"], ["98", "99"], "2008-01"
CEILING, PAUSE, RETRY_WAIT = 14, 3, 60
UNITS = {"thousand short tons": ("short_ton", 1000.0), "thousand barrels": ("kbbl", 1.0)}


def geo_of(location):
    if location == "US":
        return "US"
    return f"US-{location}" if re.fullmatch(r"[A-Z]{2}", location) else ""


def rows(data, url, retrieved):
    out = []
    for r in data:
        v = pd.to_numeric(r.get("stocks"), errors="coerce")
        if pd.isna(v):
            continue
        u = r.get("stocks-units") or ""
        if u not in UNITS:
            raise RuntimeError(f"a unit not in the map: {u!r}")
        unit, scale = UNITS[u]
        loc = r["location"]
        out.append(dict(entity=f"eia_power_stocks:{loc}:{r['sectorid']}:{r['fueltypeid']}", variable="stocks",
                        ts_utc=f"{r['period']}-01T00:00:00Z", value=float(v) * scale, unit=unit, freq="P1M", geo=geo_of(loc), market="",
                        node=f"{r.get('stateDescription', loc)}, {r.get('sectorDescription', '')}, {r.get('fuelTypeDescription', '')}",
                        source=SOURCE, source_url=url, retrieved_at=retrieved, vintage=""))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="EIA's fuel stocks at power plants, by state and sector, a month")
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
        url = requests.Request("GET", API, params=params).prepare().url
        hit = None if args.fresh else ip.raw_cached(CONNECTOR, url)
        if hit:
            log(f"  raw file reused: {ip.redact(url)}")
            return json.loads(hit[0])["response"], ip.redact(url)
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
                return r.json()["response"], ip.redact(r.url)
            log(f"  {ip.redact(r.url)}: HTTP {r.status_code}; " + (f"asked once more in {RETRY_WAIT} s" if attempt == 1 else "not asked again"))
            time.sleep(RETRY_WAIT)
        raise RuntimeError(f"EIA answered HTTP {r.status_code} twice for {ip.redact(r.url)}")

    try:
        key = ip.load_key("EIA_API_KEY", log)
        if not key:
            raise RuntimeError("EIA_API_KEY is not set (.env or the environment)")
        retrieved = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        got, offset, total, records = [], 0, None, 0
        while True:
            resp, url = get({"api_key": key, "frequency": "monthly", "data[]": "stocks", "start": FIRST,
                             "facets[fueltypeid][]": FUELS, "facets[sectorid][]": SECTORS, "length": 5000, "offset": offset,
                             "sort[0][column]": "period", "sort[0][direction]": "asc",
                             "sort[1][column]": "location", "sort[1][direction]": "asc",
                             "sort[2][column]": "sectorid", "sort[2][direction]": "asc",
                             "sort[3][column]": "fueltypeid", "sort[3][direction]": "asc"})
            total = int(resp["total"])
            got += rows(resp["data"], url.split("&length")[0], retrieved)
            records += len(resp["data"])
            offset += len(resp["data"])
            log(f"  offset {offset:,} of {total:,}")
            if offset >= total or len(resp["data"]) < 5000:
                break
        if offset != total:
            raise RuntimeError(f"{offset:,} records read of the {total:,} EIA counts")
        s = pd.DataFrame(got)
        if s.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("an (entity, variable, ts_utc) is given twice")
        s = s[ip.SERIES_COLS].sort_values(["entity", "ts_utc"]).reset_index(drop=True)
        span = f"{s.ts_utc.min()[:7]} to {s.ts_utc.max()[:7]}"
        header = [
            "Energy Research Warehouse (ERW): EIA, fuel stocks at power plants (coal, petroleum liquids, petroleum coke) by state and census region, electric power sector and all sectors, a month (session 927)",
            "Shape: series (docs/datastandard.md v0). entity eia_power_stocks:<location>:<sector 98 electric power or 99 all sectors>:<fuel COL coal "
            "excluding waste coal, PEL petroleum liquids, PC petroleum coke>; variable stocks (the month's end); unit short_ton (EIA's thousand short "
            "tons times 1,000) or kbbl; ts_utc the month's first day; freq P1M; geo US-<state>, US, or empty for a census region; a region's and the "
            "U.S.'s rows sum their states: a sum takes one level.",
            f"Months {span}; {total:,} records of EIA's, {len(s):,} rows with a stocks figure (a record without one has no row); "
            f"{s.entity.nunique()} series. Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia_power_fuel_stocks.py; {asked[0]} requests of {CEILING}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Energy Information Administration, Form EIA-923, electric power operational data (API v2), {PAGE}",
            f"  access: {API}?frequency=monthly&data[]=stocks&facets[fueltypeid][]=COL,PEL,PC&facets[sectorid][]=98,99&start={FIRST}",
            'License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Form EIA-923").',
        ]
        ip.write_snapshot(s, NAME, header, log, ip.SERIES_COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Energy Information Administration (EIA)",
                                    report="Electric power operational data: fuel stocks (Form EIA-923, API v2)", report_url=PAGE,
                                    document_list=API, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(s):,} rows"))
        print(f"{NAME}: {len(s):,} rows of {records:,} records, {s.entity.nunique()} series, {span}; {asked[0]} requests")
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
