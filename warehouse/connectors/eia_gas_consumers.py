#!/usr/bin/env python3
"""EIA's number of natural gas consumers by state and sector, a year (session 861, chain 046: a public source the ERW
did not hold, beside its natural gas consumption by state).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/eia_gas_consumers_state_annual.csv, from
the U.S. Energy Information Administration's API v2, route natural-gas/cons/num ("Number of Natural Gas Consumers",
Natural Gas Annual):

    https://api.eia.gov/v2/natural-gas/cons/num/data/?frequency=annual&data[]=value

    entity    eia_gas_consumers:<EIA area code> (NUS the U.S., S<state> a state)
    variable  EIA's process as a name: residential_consumers, commercial_consumers, industrial_consumers and the others
              the route gives (count)
    ts_utc    the year's 1 January at 00:00:00Z; freq P1Y; geo US-<state> for a state, US for the U.S.; node EIA's series
              description

Counts only: the route's average consumption per consumer (unit MCF) is a ratio of two series and is left out, counted
in the header. A value EIA leaves empty has no row; nothing is filled. Any other unit stops the run; so does a key given twice.

    python warehouse/connectors/eia_gas_consumers.py [--offline | --fresh]

Ceiling: 6 requests a run (pages of 5,000, 3 seconds apart; a page an earlier run saved in warehouse/raw is reused unless
--fresh; --offline asks nothing). License: public (EIA, record 1 of license_reads.csv; cite "U.S. Energy Information
Administration, Natural Gas Annual").
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

NAME = "eia_gas_consumers_state_annual"
CONNECTOR = "eia_gas_consumers"
SOURCE = "eia:natural-gas/cons/num"
API = "https://api.eia.gov/v2/natural-gas/cons/num/"
PAGE = "https://www.eia.gov/dnav/ng/ng_cons_num_dcu_nus_a.htm"
CEILING, PAUSE, RETRY_WAIT = 6, 3, 60
SKIPPED = {}   # rows left out by unit, for the header


def var_of(process_name):
    """EIA's process name as a variable: "Number of Residential Consumers" is residential_consumers."""
    n = re.sub(r"^number of ", "", process_name.strip().lower())
    return re.sub(r"[^a-z0-9]+", "_", n).strip("_")


def text(v):
    return "" if v is None or (isinstance(v, float) and pd.isna(v)) else str(v).strip()


def rows(data, url, retrieved):
    out = []
    for r in data:
        area, u = text(r.get("duoarea")), text(r.get("units"))
        if not area or not text(r.get("process-name")):
            raise RuntimeError(f"a record with no area or process: {r}")
        if u == "MCF":
            SKIPPED["MCF"] = SKIPPED.get("MCF", 0) + 1   # average consumption per consumer: a ratio, not taken
            continue
        if u != "COUNT":
            raise RuntimeError(f"a unit not in the map: {u!r}")
        v = pd.to_numeric(r.get("value"), errors="coerce")
        if pd.isna(v):
            continue
        state = area[1:] if area.startswith("S") and len(area) == 3 else ""
        out.append(dict(entity=f"eia_gas_consumers:{area}", variable=var_of(text(r.get("process-name"))), ts_utc=f"{r['period']}-01-01T00:00:00Z",
                        value=float(v), unit="count", freq="P1Y", geo=f"US-{state}" if state else "US", market="",
                        node=text(r.get("series-description")), source=SOURCE, source_url=url, retrieved_at=retrieved, vintage=""))
    t = pd.DataFrame(out)
    if len(t) and t.duplicated(["entity", "variable", "ts_utc"]).any():
        raise RuntimeError("an (entity, variable, ts_utc) is given twice")
    return t


def main(argv=None):
    ap = argparse.ArgumentParser(description="EIA's number of natural gas consumers by state and sector, a year")
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
            body, url = get({"api_key": key, "frequency": "annual", "data[]": "value", "length": 5000, "offset": offset,
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
        s = s[ip.SERIES_COLS]
        span = f"{s['ts_utc'].min()[:4]} to {s['ts_utc'].max()[:4]}"
        header = [
            "Energy Research Warehouse (ERW): EIA, number of natural gas consumers by state and sector, a year (session 861)",
            "Shape: series (docs/datastandard.md v0). entity eia_gas_consumers:<EIA area: NUS or S<state>>; variable EIA's process (residential_consumers, commercial_consumers, industrial_consumers and the others the route gives), count; "
            "ts_utc the year's 1 January; freq P1Y; geo US-<state> or US; node EIA's series description.",
            f"Counts only: EIA's average consumption per consumer (Mcf, {SKIPPED.get('MCF', 0):,} records) is a ratio of two series and is not taken. A value EIA leaves empty has no row; nothing is filled. Years {span}; {total:,} records of EIA's, {len(s):,} rows.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia_gas_consumers.py; {asked[0]} requests of {CEILING}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Energy Information Administration, Natural Gas Annual, number of consumers (API v2, route natural-gas/cons/num), {PAGE}",
            f"  access: {API}data/?frequency=annual&data[]=value",
            'License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Natural Gas Annual").',
        ]
        ip.write_snapshot(s, NAME, header, log, ip.SERIES_COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Energy Information Administration (EIA)",
                                    report="Natural Gas Annual, number of consumers (API v2)", report_url=PAGE, document_list=API,
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
