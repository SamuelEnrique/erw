#!/usr/bin/env python3
"""EIA-923: each power plant's net generation and fuel consumed, by fuel, a year (session 510).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/eia923_plant_fuel_annual.csv, from the U.S.
Energy Information Administration's API v2, route electricity/facility-fuel (Form EIA-923, annual, prime mover ALL):

    https://api.eia.gov/v2/electricity/facility-fuel/data/?frequency=annual&data[]=generation&data[]=total-consumption-btu
        &facets[primeMover][]=ALL&start=<year>&end=<year>

    entity    eia923:<plantCode>:<fuel2002>:<fuelType>; fuel2002 ALL with fuelType ALL is the plant's own total, which EIA
              publishes beside its fuels (a sum over a plant's fuels must leave it out)
    variable  net_generation (MWh, EIA's "generation"; negative where a plant used more than it made, pumped storage)
              and fuel_consumed (EIA's "total-consumption-btu", MMBtu, as TBtu: times 0.000001)
    ts_utc    the year's 1 January; freq P1Y; geo US-<state>; node "<plant name>: <fuel type>"

Annual only: every plant reports its year on the form, while EIA imputes the monthly figures of plants outside its
monthly sample and the API marks no row as imputed, so no monthly row is taken. Fuel2002 and fuelType together are the
key: a pumped-storage and a conventional hydro unit share fuel2002 WAT (session 510's probe). A blank value has no row;
nothing is filled. A unit not in the map stops the run; so does a key given twice.

    python warehouse/connectors/eia923_plant_fuel.py [--from 2001] [--to 2024]

Ceiling: 130 requests a run (pages of 5,000, 3 seconds apart; a 429 or a 5xx asked once more after 60 seconds; a page an
earlier run saved in warehouse/raw/eia923_plant_fuel/ is reused and not asked again). License:
public (EIA, record 1 of license_reads.csv; cite "U.S. Energy Information Administration, Form EIA-923").
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

NAME = "eia923_plant_fuel_annual"
CONNECTOR = "eia923_plant_fuel"
SOURCE = "eia:electricity/facility-fuel"
API = "https://api.eia.gov/v2/electricity/facility-fuel/"
PAGE = "https://www.eia.gov/electricity/data/eia923/"
CEILING, PAUSE, RETRY_WAIT = 130, 3, 60   # session 524: 2001 on, about 6 pages a year
FIRST, LAST = 2001, 2024   # session 524: from 2001 (2020 to 2024 since session 510)
DATA = {"generation": ("net_generation", {"megawatthours": ("MWh", 1.0)}),
        "total-consumption-btu": ("fuel_consumed", {"mmbtu": ("TBtu", 1e-6)})}


def rows(data, url, retrieved):
    out = []
    for r in data:
        for col, (variable, units) in DATA.items():
            v = pd.to_numeric(r.get(col), errors="coerce")
            if pd.isna(v):
                continue
            u = str(r.get(f"{col}-units", "")).strip().lower()
            if u not in units:
                raise RuntimeError(f"{col}: a unit not in the map: {u!r}")
            unit, factor = units[u]
            st = str(r.get("state") or "")
            out.append(dict(entity=f"eia923:{r['plantCode']}:{r['fuel2002']}:{r['fuelType']}", variable=variable,
                            ts_utc=f"{int(r['period'])}-01-01T00:00:00Z", value=float(v) * factor, unit=unit, freq="P1Y",
                            geo=f"US-{st}" if st else "US", market="",
                            node=f"{r.get('plantName', '')}: {r.get('fuelTypeDescription', '')}", source=SOURCE,
                            source_url=url, retrieved_at=retrieved, vintage=""))
    t = pd.DataFrame(out)
    if len(t) and t.duplicated(["entity", "variable", "ts_utc"]).any():
        raise RuntimeError("an (entity, variable, ts_utc) is given twice")
    return t


def main(argv=None):
    ap = argparse.ArgumentParser(description="EIA-923: each plant's net generation and fuel consumed, by fuel, a year")
    ap.add_argument("--from", dest="first", type=int, default=FIRST)
    ap.add_argument("--to", dest="last", type=int, default=LAST)
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
        """(the response's JSON, its address without the key): a page an earlier run saved in warehouse/raw is reused
        (the year's figures are final), else asked, under the ceiling."""
        url = requests.Request("GET", API + "data/", params=params).prepare().url
        hit = ip.raw_cached(CONNECTOR, url)
        if hit:
            log(f"  raw file reused: {ip.redact(url)}")
            return json.loads(hit[0]), ip.redact(url)
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
        frames = []
        for year in range(args.first, args.last + 1):
            offset, total = 0, None
            while True:
                body, url = get({"api_key": key, "frequency": "annual", "data[]": list(DATA), "facets[primeMover][]": "ALL",
                                 "start": str(year), "end": str(year), "length": 5000, "offset": offset,
                                 "sort[0][column]": "plantCode", "sort[0][direction]": "asc",
                                 "sort[1][column]": "fuel2002", "sort[1][direction]": "asc",
                                 "sort[2][column]": "fuelType", "sort[2][direction]": "asc"})
                resp = body["response"]
                total = int(resp["total"])
                frames.append(rows(resp["data"], url.split("&length")[0], retrieved))
                offset += len(resp["data"])
                if offset >= total or not resp["data"]:
                    break
            if offset != total:
                raise RuntimeError(f"{year}: {offset:,} rows read of the {total:,} EIA counts")
            log(f"{year}: {total:,} rows of EIA's")
        s = pd.concat([f for f in frames if len(f)], ignore_index=True)
        if s.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("a row on two pages")
        s = s[ip.SERIES_COLS]
        years = f"{s['ts_utc'].min()[:4]} to {s['ts_utc'].max()[:4]}"
        header = [
            "Energy Research Warehouse (ERW): Form EIA-923, each power plant's net generation and fuel consumed, by fuel, a year (session 510)",
            "Shape: series (docs/datastandard.md v0). entity eia923:<plantCode>:<fuel2002>:<fuelType> (fuel2002 ALL with fuelType ALL is the plant's own total: leave it out of a sum over fuels); "
            "variable net_generation (MWh) or fuel_consumed (TBtu, EIA's MMBtu times 0.000001); ts_utc the year's 1 January; freq P1Y; node the plant's name and the fuel.",
            f"Annual only (EIA imputes the monthly figures of plants outside its monthly sample, unmarked); prime mover ALL; years {years}. A blank value has no row; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia923_plant_fuel.py; {asked[0]} requests of {CEILING}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Energy Information Administration, Form EIA-923 (API v2, route electricity/facility-fuel), {PAGE}",
            f"  access: {API}data/?frequency=annual&data[]=generation&data[]=total-consumption-btu&facets[primeMover][]=ALL&start=<year>&end=<year>",
            'License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Form EIA-923").',
        ]
        ip.write_snapshot(s, NAME, header, log, ip.SERIES_COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Energy Information Administration (EIA)",
                                    report="Form EIA-923, facility fuel (API v2, annual)", report_url=PAGE, document_list=API,
                                    license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(s):,} rows"))
        plants = s["entity"].str.split(":").str[1].nunique()
        print(f"{NAME}: {len(s):,} rows, {plants:,} plants, {years}; {asked[0]} requests")
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
