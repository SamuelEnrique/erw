#!/usr/bin/env python3
"""EIA's petroleum supply and disposition: crude oil and the main products, the U.S. and the five PADDs, a month
(session 555).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/eia_petroleum_snd_monthly.csv, from the U.S.
Energy Information Administration's API v2, route petroleum/sum/snd (Petroleum Supply Monthly, supply and disposition):

    https://api.eia.gov/v2/petroleum/sum/snd/data/?frequency=monthly&data[]=value&facets[product][]=EP00...&start=2015-01

    entity    eia_petroleum_snd:<series>, EIA's series id (one a process, product and area, in one unit)
    variable  the process as a word (field_production, refinery_net_production, refinery_net_input, imports, exports,
              net_receipts, stock_change, ending_stocks, product_supplied, supply_adjustment, renewable_plant_production,
              transfers_to_crude_supply), with _per_day for EIA's thousand barrels a day
    value     kbbl (EIA's thousand barrels in the month) or kbbl/d
    ts_utc    the month's first day at 00:00:00Z; freq P1M; geo US; node EIA's series name

Twenty products, in two groups (GROUPS below): session 555's eight (the total, crude oil, finished motor gasoline,
distillate, jet fuel, propane, residual fuel and fuel ethanol) and session 574's twelve (kerosene, aviation gasoline,
asphalt, petroleum coke, lubricants, natural gas plant liquids, ethane, normal butane, isobutane, unfinished oils,
biodiesel and renewable diesel), from 2015: the route holds about 40 products and 3,949 records a month, beyond a
run's ceiling.
A blank has no row; nothing is filled. A unit, process or area not in the map stops the run; so does a key given twice.

    python warehouse/connectors/eia_petroleum_snd.py [--from 2015-01] [--offline | --fresh]

Ceiling: 29 requests a run (pages of 5,000, 3 seconds apart; a page an earlier run saved in warehouse/raw is reused
unless --fresh; --offline asks nothing). License: public (EIA, record 1 of license_reads.csv; cite "U.S. Energy
Information Administration, Petroleum Supply Monthly").
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

NAME = "eia_petroleum_snd_monthly"
CONNECTOR = "eia_petroleum_snd"
SOURCE = "eia:petroleum/sum/snd"
API = "https://api.eia.gov/v2/petroleum/sum/snd/"
PAGE = "https://www.eia.gov/petroleum/supply/monthly/"
CEILING, PAUSE, RETRY_WAIT = 29, 3, 60   # session 555: one of 30 went to the probe
FIRST = "2015-01"
PROCESSES = {"FPF": "field_production", "YPR": "refinery_net_production", "YIR": "refinery_net_input", "IM0": "imports",
             "EEX": "exports", "VNR": "net_receipts", "SCG": "stock_change", "SAE": "ending_stocks", "VPP": "product_supplied",
             "VUA": "supply_adjustment", "YNP": "renewable_plant_production", "TVP": "transfers_to_crude_supply"}
# the products, in groups a run reads one after another; the first group is session 555's (its saved pages answer the
# same addresses), the second session 574's, the third session 600's, the fourth session 601's
GROUPS = [["EP00", "EPC0", "EPM0F", "EPD0", "EPJK", "EPLLPA", "EPPR", "EPOOXE"],
          ["EPPK", "EPPV", "EPPA", "EPPC", "EPPL", "EPL2", "EPLLEA", "EPLLBAN", "EPLLBAI", "EPPU", "EPOORDB", "EPOORDO"],
          # session 600: the third group
          ["EPL0", "EPOL", "EPLLNG", "EPP2", "EPOO", "EPOOR", "EPOBG", "EPOBGC0", "EPM0C", "EPDXL0"],
          # session 601: the fourth group (eleven small products are left: EPPNS, EPPPN, EPPRH, EPPRX, EPLLBYI, EPLLEY,
          # EPOBV, EPOOOXH, EPOOOH, EPPCC, EPPS)
          ["EPOORXFE", "EPOBGR0", "EPPCM", "EPD00H", "EPDM10", "EPPM", "EPPP0", "EPLOLE", "EPPW", "EPLLPY", "EPOOXXFE",
           "EPPPO", "EPLLBYN", "EPLLCS", "EPOORO", "EPM0R", "EPPRY"]]
PRODUCTS = [p for g in GROUPS for p in g]
AREAS = {"NUS", "NUS-Z00", "R10", "R10-Z00", "R10-Z0P", "R20", "R20-Z00", "R20-Z0P", "R30", "R30-Z00", "R30-Z0P",
         "R40", "R40-Z00", "R40-Z0P", "R50", "R50-Z00", "R50-Z0P"}
UNITS = {"mbbl": ("kbbl", 1.0, ""), "mbbl/d": ("kbbl/d", 1.0, "_per_day")}


def rows(data, url, retrieved):
    out = []
    for r in data:
        if r.get("process") not in PROCESSES:
            raise RuntimeError(f"a process not asked for: {r.get('process')!r}")
        if str(r.get("duoarea")) not in AREAS:
            raise RuntimeError(f"an area not understood: {r.get('duoarea')!r}")
        v = pd.to_numeric(r.get("value"), errors="coerce")
        if pd.isna(v):
            continue
        u = str(r.get("units", "")).strip().lower()
        if u not in UNITS:
            raise RuntimeError(f"a unit not in the map: {r.get('units')!r}")
        unit, factor, suffix = UNITS[u]
        month = str(r["period"])[:7]
        dt.date.fromisoformat(month + "-01")
        out.append(dict(entity=f"eia_petroleum_snd:{str(r['series']).strip()}", variable=PROCESSES[r["process"]] + suffix,
                        ts_utc=f"{month}-01T00:00:00Z", value=float(v) * factor, unit=unit, freq="P1M", geo="US", market="",
                        node=str(r.get("series-description") or "").strip(), source=SOURCE, source_url=url,
                        retrieved_at=retrieved, vintage=""))
    t = pd.DataFrame(out)
    if len(t) and t.duplicated(["entity", "variable", "ts_utc"]).any():
        raise RuntimeError("an (entity, variable, ts_utc) is given twice")
    return t


def main(argv=None):
    ap = argparse.ArgumentParser(description="EIA's petroleum supply and disposition, a month")
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
        frames, totals = [], []
        for group in GROUPS:
            offset, total = 0, None
            while True:
                body, url = get({"api_key": key, "frequency": "monthly", "data[]": "value", "facets[product][]": group,
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
                raise RuntimeError(f"products {group[0]} and on: {offset:,} rows read of the {total:,} EIA counts")
            totals.append(total)
        total = sum(totals)
        s = pd.concat([f for f in frames if len(f)], ignore_index=True)
        if s.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("a row on two pages")
        s = s[ip.SERIES_COLS]
        span = f"{s['ts_utc'].min()[:7]} to {s['ts_utc'].max()[:7]}"
        header = [
            "Energy Research Warehouse (ERW): EIA, petroleum supply and disposition, crude oil and the main products, the U.S. and the five PADDs, a month (session 555)",
            "Shape: series (docs/datastandard.md v0). entity eia_petroleum_snd:<series>; variable the process as a word, with _per_day for kbbl/d; unit kbbl (the month) or kbbl/d; "
            "ts_utc the month's first day; freq P1M; node EIA's series name. Products: " + ", ".join(PRODUCTS) + " (EP00 the total holds the others).",
            f"A blank has no row; nothing is filled. Months {span}; {total:,} records of EIA's, {len(s):,} rows.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia_petroleum_snd.py; {asked[0]} requests of {CEILING}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Energy Information Administration, Petroleum Supply Monthly, supply and disposition (API v2, route petroleum/sum/snd), {PAGE}",
            f"  access: {API}data/?frequency=monthly&data[]=value&facets[product][]=<each of eight>&start={args.first}",
            'License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Petroleum Supply Monthly").',
        ]
        ip.write_snapshot(s, NAME, header, log, ip.SERIES_COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Energy Information Administration (EIA)",
                                    report="Petroleum Supply Monthly, supply and disposition (API v2)", report_url=PAGE, document_list=API,
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
