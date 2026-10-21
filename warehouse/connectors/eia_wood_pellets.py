#!/usr/bin/env python3
"""EIA's densified biomass (wood pellets): prices, plants and employees, a month (session 558).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/eia_wood_pellets_monthly.csv, from the U.S.
Energy Information Administration's API v2, three routes of densified-biomass (the Monthly Densified Biomass Fuel Report,
2016 on):

    sales-and-price-by-region   average-price           variable domestic_price (USD/short_ton), by region
    export-sales-and-price      average-price           variable export_price (USD/short_ton), the U.S.
    capacity-by-region          number-of-facilities    variable facilities (count), by region
                                number-of-fte-employees variable fte_employees (count), by region
    feedstocks-and-cost         cost                    variable feedstock_cost (USD/short_ton), by fuel type (session 575)

    entity    eia_wood_pellets:<route>:<region or fuel type>; ts_utc the month's first day at 00:00:00Z; freq P1M; geo US; node EIA's
              region name. EIA's tons are short tons. Its quantities and capacity in tons are not taken: the vocabulary
              has no tonnage (a ruling asked in sessions 490 and 519)

A figure EIA withholds has no row; nothing is filled. A unit not in the map stops the run; so does a key given twice.

    python warehouse/connectors/eia_wood_pellets.py [--offline | --fresh]

Ceiling: 13 requests a run (pages of 5,000, 3 seconds apart; a page an earlier run saved in warehouse/raw is reused unless
--fresh; --offline asks nothing). License: public (EIA, record 1 of license_reads.csv; cite "U.S. Energy Information
Administration, Monthly Densified Biomass Fuel Report").
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

NAME = "eia_wood_pellets_monthly"
CONNECTOR = "eia_wood_pellets"
SOURCE = "eia:densified-biomass"
API = "https://api.eia.gov/v2/densified-biomass/"
PAGE = "https://www.eia.gov/biofuels/biomass/"
CEILING, PAUSE, RETRY_WAIT = 13, 3, 60   # session 558: seven of 20 went to the probes
FIRST = "2016-01"
# route: [(EIA's data column, variable, {EIA's unit: (unit, factor)})]
ROUTES = {
    "sales-and-price-by-region": [("average-price", "domestic_price", {"usd per ton": ("USD/short_ton", 1.0)})],
    "export-sales-and-price": [("average-price", "export_price", {"usd per ton": ("USD/short_ton", 1.0)})],
    "capacity-by-region": [("number-of-facilities", "facilities", {"number of facilities": ("count", 1.0)}),
                           ("number-of-fte-employees", "fte_employees", {"number of fte employees": ("count", 1.0)})],
    # session 575: the feedstocks' cost by fuel type (the route is keyed by fuelTypeId, not by region)
    "feedstocks-and-cost": [("cost", "feedstock_cost", {"usd per ton": ("USD/short_ton", 1.0)})],
}
SHORT = {"sales-and-price-by-region": "sales", "export-sales-and-price": "export", "capacity-by-region": "capacity",
         "feedstocks-and-cost": "feedstocks"}


def text(v):
    return "" if v is None or (isinstance(v, float) and pd.isna(v)) else str(v).strip()


def rows(route, data, url, retrieved):
    out = []
    for r in data:
        month = text(r.get("period"))[:7]
        dt.date.fromisoformat(month + "-01")
        region = text(r.get("region") or r.get("fuelTypeId")) or "US"
        name = text(r.get("regionDescription") or r.get("region-name") or r.get("regionName") or r.get("fuelTypeDescription")) or region
        for col, variable, units in ROUTES[route]:
            v = pd.to_numeric(r.get(col), errors="coerce")
            if pd.isna(v):
                continue
            u = text(r.get(f"{col}-units")).lower()
            if u not in units:
                raise RuntimeError(f"{route} {col}: a unit not in the map: {r.get(col + '-units')!r}")
            unit, factor = units[u]
            out.append(dict(entity=f"eia_wood_pellets:{SHORT[route]}:{region}", variable=variable, ts_utc=f"{month}-01T00:00:00Z",
                            value=float(v) * factor, unit=unit, freq="P1M", geo="US", market="", node=name, source=SOURCE,
                            source_url=url, retrieved_at=retrieved, vintage=""))
    t = pd.DataFrame(out)
    if len(t) and t.duplicated(["entity", "variable", "ts_utc"]).any():
        raise RuntimeError(f"{route}: an (entity, variable, ts_utc) is given twice")
    return t


def main(argv=None):
    ap = argparse.ArgumentParser(description="EIA's densified biomass (wood pellets): prices, plants and employees, a month")
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

    def get(route, params):
        url = requests.Request("GET", API + route + "/data/", params=params).prepare().url
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
        frames, counts = [], {}
        for route, cols in ROUTES.items():
            offset, total = 0, None
            while True:
                body, url = get(route, {"api_key": key, "frequency": "monthly", "data[]": [c for c, _, _ in cols], "start": FIRST,
                                        "length": 5000, "offset": offset, "sort[0][column]": "period", "sort[0][direction]": "asc"})
                resp = body["response"]
                total = int(resp["total"])
                frames.append(rows(route, resp["data"], url.split("&length")[0], retrieved))
                offset += len(resp["data"])
                if offset >= total or len(resp["data"]) < 5000:
                    break
            if offset != total:
                raise RuntimeError(f"{route}: {offset:,} records read of the {total:,} EIA counts")
            counts[route] = total
        s = pd.concat([f for f in frames if len(f)], ignore_index=True)
        if s.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("a row on two pages")
        s = s[ip.SERIES_COLS]
        span = f"{s['ts_utc'].min()[:7]} to {s['ts_utc'].max()[:7]}"
        header = [
            "Energy Research Warehouse (ERW): EIA, densified biomass (wood pellets): domestic and export prices, plants and employees, a month (session 558)",
            "Shape: series (docs/datastandard.md v0). entity eia_wood_pellets:<sales|export|capacity>:<region>; variable domestic_price or export_price (USD/short_ton), "
            "facilities or fte_employees (count), feedstock_cost (USD/short_ton, by fuel type); ts_utc the month's first day; freq P1M; node EIA's region or fuel name. EIA's tonnages are not taken.",
            f"A figure EIA withholds has no row; nothing is filled. Months {span}; records of EIA's: " + ", ".join(f"{k} {v:,}" for k, v in counts.items()) + ".",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia_wood_pellets.py; {asked[0]} requests of {CEILING}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Energy Information Administration, Monthly Densified Biomass Fuel Report (API v2, routes densified-biomass/sales-and-price-by-region, export-sales-and-price, capacity-by-region), {PAGE}",
            f"  access: {API}<route>/data/?frequency=monthly&data[]=<column>&start={FIRST}",
            'License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Monthly Densified Biomass Fuel Report").',
        ]
        ip.write_snapshot(s, NAME, header, log, ip.SERIES_COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Energy Information Administration (EIA)",
                                    report="Monthly Densified Biomass Fuel Report (API v2)", report_url=PAGE, document_list=API,
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
