#!/usr/bin/env python3
"""EIA's international electricity statistics for the U.S. and its two interconnected neighbors, Canada and Mexico: each
year's generation and capacity by source, consumption, imports, exports and losses (session 886, chain 048).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/eia_international_electricity_annual.csv,
from the U.S. Energy Information Administration's API v2, route international (EIA's International Energy Statistics):

    https://api.eia.gov/v2/international/data/?frequency=annual&data[]=value&start=1980
        &facets[countryRegionId][]=CAN&facets[countryRegionId][]=MEX&facets[countryRegionId][]=USA
        &facets[activityId][]=<12 generation, 7 capacity, 2 consumption, 3 imports, 4 exports, 23 net imports, 9 distribution losses>
        &facets[unit][]=BKWH&facets[unit][]=MK

    entity    eia_intl:<EIA country code>:<EIA product id> (2 electricity, 27 nuclear, 28 fossil fuels, 29 renewables,
              30 coal, 31 natural gas, 32 oil, 33 hydroelectricity, 37 wind, 116 solar and the rest, as EIA names them in node)
    variable  generation, consumption, imports, exports, net_imports, distribution_losses (MWh: EIA's billion kWh times
              1,000,000) and capacity (MW: EIA's million kW times 1,000)
    ts_utc    the year's 1 January; freq P1Y; geo CA, MX or US; node "<country>, <product>" as EIA names them;
              x_data_flag EIA's flag where it gives one

Only billion kWh and million kW are asked: EIA gives the same energy again in quadrillion Btu, terajoules and million
tonnes of oil equivalent, which are not taken. A value EIA leaves empty or marks ("NA", "--", "(s)") has no row; nothing
is filled. A unit or activity not in the map stops the run; so does a key given twice.

    python warehouse/connectors/eia_international_electricity.py [--offline | --fresh] [--ceiling N]

Ceiling: 20 requests a run unless --ceiling says fewer (pages of 5,000, 3 seconds apart; a page an earlier run saved in
warehouse/raw is reused unless --fresh; --offline asks nothing). License: public (EIA, record 1 of license_reads.csv; cite
"U.S. Energy Information Administration, International Energy Statistics").
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

NAME = "eia_international_electricity_annual"
CONNECTOR = "eia_international_electricity"
SOURCE = "eia:international"
API = "https://api.eia.gov/v2/international/"
PAGE = "https://www.eia.gov/international/data/world"
CEILING, PAUSE, RETRY_WAIT = 20, 3, 60
FIRST = "1980"
COUNTRIES = {"CAN": "CA", "MEX": "MX", "USA": "US"}
ACTIVITIES = {"12": "generation", "7": "capacity", "2": "consumption", "3": "imports", "4": "exports", "23": "net_imports",
              "9": "distribution_losses"}
UNITS = {"BKWH": ("MWh", 1e6), "MK": ("MW", 1e3)}


def text(v):
    return "" if v is None or (isinstance(v, float) and pd.isna(v)) else str(v).strip()


def rows(data, url, retrieved):
    out = []
    for r in data:
        country, product, act, u = text(r.get("countryRegionId")), text(r.get("productId")), text(r.get("activityId")), text(r.get("unit"))
        if country not in COUNTRIES:
            raise RuntimeError(f"a country not asked for: {country!r}")
        if act not in ACTIVITIES:
            raise RuntimeError(f"an activity not in the map: {act!r} {r.get('activityName')}")
        if u not in UNITS:
            raise RuntimeError(f"a unit not in the map: {u!r}")
        v = pd.to_numeric(r.get("value"), errors="coerce")
        if pd.isna(v):
            continue
        unit, scale = UNITS[u]
        out.append(dict(entity=f"eia_intl:{country}:{product}", variable=ACTIVITIES[act], ts_utc=f"{text(r['period'])}-01-01T00:00:00Z",
                        value=float(v) * scale, unit=unit, freq="P1Y", geo=COUNTRIES[country], market="",
                        node=f"{text(r.get('countryRegionName'))}, {text(r.get('productName'))}", source=SOURCE, source_url=url,
                        retrieved_at=retrieved, vintage="", x_data_flag=text(r.get("dataFlagDescription"))))
    t = pd.DataFrame(out)
    if len(t) and t.duplicated(["entity", "variable", "ts_utc"]).any():
        raise RuntimeError("an (entity, variable, ts_utc) is given twice")
    return t


def main(argv=None):
    ap = argparse.ArgumentParser(description="EIA's international electricity statistics, the U.S., Canada and Mexico")
    ap.add_argument("--offline", action="store_true", help="the pages from warehouse/raw only, no request")
    ap.add_argument("--fresh", action="store_true", help="ask every page again, even one saved in warehouse/raw")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    ap.add_argument("--ceiling", type=int, default=CEILING, help=f"at most this many requests (default {CEILING})")
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
            if asked[0] >= args.ceiling:
                raise RuntimeError(f"the ceiling of {args.ceiling} requests is reached")
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
            body, url = get({"api_key": key, "frequency": "annual", "data[]": "value", "start": FIRST,
                             "facets[countryRegionId][]": list(COUNTRIES), "facets[activityId][]": list(ACTIVITIES),
                             "facets[unit][]": list(UNITS), "length": 5000, "offset": offset,
                             "sort[0][column]": "period", "sort[0][direction]": "asc",
                             "sort[1][column]": "countryRegionId", "sort[1][direction]": "asc",
                             "sort[2][column]": "productId", "sort[2][direction]": "asc",
                             "sort[3][column]": "activityId", "sort[3][direction]": "asc"})
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
        cols = ip.SERIES_COLS + ["x_data_flag"]
        s = s[cols]
        span = f"{s['ts_utc'].min()[:4]} to {s['ts_utc'].max()[:4]}"
        header = [
            "Energy Research Warehouse (ERW): EIA, International Energy Statistics, electricity of the U.S., Canada and Mexico, a year (session 886)",
            "Shape: series (docs/datastandard.md v0). entity eia_intl:<EIA country code CAN, MEX, USA>:<EIA product id: 2 electricity, 27 nuclear, "
            "28 fossil fuels, 29 renewables, 30 coal, 31 natural gas, 32 oil, 33 hydroelectricity, 37 wind, 116 solar, and the rest as node names them>; "
            "variables generation, consumption, imports, exports, net_imports, distribution_losses (MWh, EIA's billion kWh times 1,000,000) and "
            "capacity (MW, EIA's million kW times 1,000); a product's parts overlap (fossil fuels holds coal, gas and oil; renewables holds hydro, "
            "wind, solar and the rest): a sum takes one level; ts_utc the year's 1 January; freq P1Y; geo CA, MX, US.",
            f"Years {span}; {total:,} records of EIA's, {len(s):,} rows. Only billion kWh and million kW are asked (EIA's Btu, terajoule and "
            "oil-equivalent copies of the same energy are not). A value EIA leaves empty or marks has no row; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia_international_electricity.py; {asked[0]} requests of {args.ceiling}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Energy Information Administration, International Energy Statistics (API v2, route international), {PAGE}",
            f"  access: {API}data/?frequency=annual&data[]=value&start={FIRST}&facets[countryRegionId][]=CAN,MEX,USA&facets[activityId][]="
            f"{','.join(ACTIVITIES)}&facets[unit][]=BKWH,MK",
            'License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, International Energy Statistics").',
        ]
        ip.write_snapshot(s, NAME, header, log, cols)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Energy Information Administration (EIA)",
                                    report="International Energy Statistics (API v2)", report_url=PAGE, document_list=API,
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
