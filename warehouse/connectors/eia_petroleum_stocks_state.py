#!/usr/bin/env python3
"""EIA's petroleum product stocks at refineries, bulk terminals and natural gas plants by state: gasoline and its
blending components, distillate fuel oil and its sulfur grades, kerosene, residual fuel oil and propane, the states, the
PADDs and the U.S., a month (session 2339, chain 109).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/eia_petroleum_stocks_state_monthly.csv,
from the U.S. Energy Information Administration's API v2, route petroleum/stoc/st ("EIA petroleum gas survey data"),
process STR (stocks at refineries, bulk terminals, and natural gas plants), 13 products, monthly from January 1993:

    https://api.eia.gov/v2/petroleum/stoc/st/data/?frequency=monthly&data[]=value&facets[process][]=STR&start=<first>

    entity    eia_petroleum_stocks_state:<series>, EIA's series id (one a product and area)
    variable  stocks_refineries_terminals_gas_plants (kbbl, EIA's thousand barrels at the month's end)
    ts_utc    the month's first day at 00:00:00Z; freq P1M; geo US-<state>, or US for the U.S. and the PADDs; node EIA's
              series name; x_area and x_product EIA's codes

Totals and parts are EIA's (the U.S., the PADDs and the states; finished gasoline and its kinds; distillate and its
grades): a sum takes one level. A blank has no row; nothing is filled. A unit, process or area not understood stops
the run; so does a key given twice, or EIA's count not met.

    python warehouse/connectors/eia_petroleum_stocks_state.py [--from 1993-01] [--offline | --fresh]

Ceiling: 12 requests a run (pages of 5,000, 3 seconds apart; a page an earlier run saved in warehouse/raw is reused
unless --fresh; --offline asks nothing). License: public (EIA, record 1 of license_reads.csv; cite "U.S. Energy
Information Administration").
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

NAME = "eia_petroleum_stocks_state_monthly"
CONNECTOR = "eia_petroleum_stocks_state"
SOURCE = "eia:petroleum/stoc/st"
API = "https://api.eia.gov/v2/petroleum/stoc/st/"
PAGE = "https://www.eia.gov/petroleum/supply/monthly/"
CEILING, PAUSE, RETRY_WAIT = 12, 3, 60   # session 2339: three of 15 went to the probe
FIRST = "1993-01"
PROCESSES = {"STR": "stocks_refineries_terminals_gas_plants"}
REGIONS = {"R10", "R1X", "R1Y", "R1Z", "R20", "R30", "R40", "R50"}
X_COLS = ["x_area", "x_product"]


def geo_of(area):
    a = str(area).strip().upper()
    if a == "NUS" or a in REGIONS:
        return "US"
    if len(a) == 3 and a.startswith("S") and a[1:].isalpha():
        return f"US-{a[1:]}"
    raise RuntimeError(f"an area not understood: {area!r}")
UNITS = {"mbbl": ("kbbl", 1.0, ""), "mbbl/d": ("kbbl/d", 1.0, "_per_day")}


def rows(data, url, retrieved):
    out = []
    for r in data:
        if r.get("process") not in PROCESSES:
            raise RuntimeError(f"a process not asked for: {r.get('process')!r}")
        v = pd.to_numeric(r.get("value"), errors="coerce")
        if pd.isna(v):
            continue
        u = str(r.get("units", "")).strip().lower()
        if u not in UNITS:
            raise RuntimeError(f"a unit not in the map: {r.get('units')!r}")
        unit, factor, suffix = UNITS[u]
        month = str(r["period"])[:7]
        dt.date.fromisoformat(month + "-01")
        out.append(dict(entity=f"eia_petroleum_stocks_state:{str(r['series']).strip()}", variable=PROCESSES[r["process"]] + suffix,
                        ts_utc=f"{month}-01T00:00:00Z", value=float(v) * factor, unit=unit, freq="P1M", geo=geo_of(r.get("duoarea")), market="",
                        node=str(r.get("series-description") or "").strip(), source=SOURCE, source_url=url,
                        retrieved_at=retrieved, vintage="", x_area=str(r.get("duoarea")).strip(), x_product=str(r.get("product")).strip()))
    t = pd.DataFrame(out)
    if len(t) and t.duplicated(["entity", "variable", "ts_utc"]).any():
        raise RuntimeError("an (entity, variable, ts_utc) is given twice")
    return t


def main(argv=None):
    ap = argparse.ArgumentParser(description="EIA's petroleum product stocks at refineries, bulk terminals and gas plants by state, a month")
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
            body, url = get({"api_key": key, "frequency": "monthly", "data[]": "value", "facets[process][]": list(PROCESSES),
                             "start": args.first, "length": 5000, "offset": offset,
                             "sort[0][column]": "period", "sort[0][direction]": "asc",
                             "sort[1][column]": "series", "sort[1][direction]": "asc"})
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
        s = s[ip.SERIES_COLS + X_COLS]
        span = f"{s['ts_utc'].min()[:7]} to {s['ts_utc'].max()[:7]}"
        header = [
            "Energy Research Warehouse (ERW): EIA, petroleum product stocks at refineries, bulk terminals and natural gas plants, by state, the PADDs and the U.S., a month (session 2339)",
            "Shape: series (docs/datastandard.md v0). entity eia_petroleum_stocks_state:<series>; variable stocks_refineries_terminals_gas_plants (kbbl at the month's end); "
            "ts_utc the month's first day; freq P1M; geo US-<state> or US; node EIA's series name; x_area and x_product EIA's codes. Totals and parts are EIA's: a sum takes one level.",
            f"A blank has no row; nothing is filled. Months {span}; {total:,} records of EIA's, {len(s):,} rows.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia_petroleum_stocks_state.py; {asked[0]} requests of {CEILING}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Energy Information Administration, petroleum stocks at refineries, bulk terminals and natural gas plants by state (API v2, route petroleum/stoc/st), {PAGE}",
            f"  access: {API}data/?frequency=monthly&data[]=value&facets[process][]=STR&start={args.first}",
            'License: public (a work of the U.S. government; cite "U.S. Energy Information Administration").',
        ]
        ip.write_snapshot(s, NAME, header, log, ip.SERIES_COLS + X_COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Energy Information Administration (EIA)",
                                    report="Petroleum stocks at refineries, bulk terminals and natural gas plants by state (API v2, petroleum/stoc/st)", report_url=PAGE, document_list=API,
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
