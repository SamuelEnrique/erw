#!/usr/bin/env python3
"""EIA's natural gas delivered for the account of others (customer choice and transportation gas), by state and
sector, a year from 1982: the volumes delivered to residential, commercial and industrial consumers whose gas is
bought from someone other than the local distribution company, and their share of each sector's deliveries (session
2377, chain 112: a source of the session's own choosing).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/eia_gas_for_others_annual.csv, from the
U.S. Energy Information Administration's API v2, route natural-gas/cons/acct ("Natural Gas Delivered for the Account
of Others", Natural Gas Annual):

    https://api.eia.gov/v2/natural-gas/cons/acct/data/?frequency=annual&data[]=value&start=1982

    entity    eia_gas_for_others:<series>, EIA's series id (one a measure and area)
    variable  residential_for_others (VRT), commercial_for_others (VF8), industrial_for_others (VFT), all MMcf;
              residential_share, commercial_share, industrial_share (VF9, VF6, VFI: the share of the sector's deliveries
              delivered for the account of others, ratio, EIA's percent divided by 100)
    ts_utc    the year's 1 January at 00:00:00Z; freq P1Y; geo US or US-<state> (EIA's NUS and S<state>); node EIA's
              series description

The shares are EIA's own, not computed here; the residential share is in whole percents (the others to 0.1), so a
small residential volume can sit beside a share of 0. Where a state has no such deliveries EIA gives a 0 (kept), a record
with no value or no record at all (no row); nothing is filled. EIA's areas are the U.S., 49 states and DC: Hawaii has no
record in any process, DC no industrial series and Vermont no commercial series (session 2380's note). A
process, unit or area not in the map stops the run; so does a key given twice. Each row carries the time EIA served
its page (a reused page's first download).

    python warehouse/connectors/eia_gas_for_others.py [--from 1982] [--offline | --fresh] [--out-dir DIR]

Ceiling: 10 requests a run (pages of 5,000, 3 seconds apart; a page an earlier run saved in warehouse/raw is reused
unless --fresh; --offline asks nothing). License: public (EIA, record 1 of license_reads.csv; cite "U.S. Energy
Information Administration, Natural Gas Annual").
"""

import argparse
import datetime as dt
import json
import re
import os
import sys
import time
import traceback

import pandas as pd
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "eia_gas_for_others_annual"
CONNECTOR = "eia_gas_for_others"
SOURCE = "eia:natural-gas/cons/acct"
API = "https://api.eia.gov/v2/natural-gas/cons/acct/"
PAGE = "https://api.eia.gov/v2/natural-gas/cons/acct/"  # the route, as read in session 2377
CEILING, PAUSE, RETRY_WAIT = 10, 3, 60
FIRST = "1982"
SPLIT, EARLY_END = "1982", "1981"   # one window: the route starts in 1982
PROCESSES = {"VRT": "residential_for_others", "VF8": "commercial_for_others", "VFT": "industrial_for_others",
             "VF9": "residential_share", "VF6": "commercial_share", "VFI": "industrial_share"}
AREAS = {"NUS": "US", "SAK": "US-AK", "SAL": "US-AL", "SAR": "US-AR", "SAZ": "US-AZ", "SCA": "US-CA", "SCO": "US-CO", "SCT": "US-CT", "SDC": "US-DC", "SDE": "US-DE", "SFL": "US-FL", "SGA": "US-GA", "SHI": "US-HI", "SIA": "US-IA", "SID": "US-ID", "SIL": "US-IL", "SIN": "US-IN", "SKS": "US-KS", "SKY": "US-KY", "SLA": "US-LA", "SMA": "US-MA", "SMD": "US-MD", "SME": "US-ME", "SMI": "US-MI", "SMN": "US-MN", "SMO": "US-MO", "SMS": "US-MS", "SMT": "US-MT", "SNC": "US-NC", "SND": "US-ND", "SNE": "US-NE", "SNH": "US-NH", "SNJ": "US-NJ", "SNM": "US-NM", "SNV": "US-NV", "SNY": "US-NY", "SOH": "US-OH", "SOK": "US-OK", "SOR": "US-OR", "SPA": "US-PA", "SRI": "US-RI", "SSC": "US-SC", "SSD": "US-SD", "STN": "US-TN", "STX": "US-TX", "SUT": "US-UT", "SVA": "US-VA", "SVT": "US-VT", "SWA": "US-WA", "SWI": "US-WI", "SWV": "US-WV", "SWY": "US-WY"}
UNITS = {"mmcf": ("MMcf", 1.0, ""), "%": ("ratio", 0.01, "")}   # a share as eia_refinery_utilization writes it


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
        year = str(r["period"])
        if not re.fullmatch(r"\d{4}", year):
            raise RuntimeError(f"a period not a year: {year!r}")
        out.append(dict(entity=f"eia_gas_for_others:{str(r['series']).strip()}", variable=PROCESSES[r["process"]] + suffix,
                        ts_utc=f"{year}-01-01T00:00:00Z", value=float(v) * factor, unit=unit, freq="P1Y",
                        geo=AREAS[str(r["duoarea"])], market="",
                        node=str(r.get("series-description") or "").strip(), source=SOURCE, source_url=url,
                        retrieved_at=retrieved, vintage=""))
    t = pd.DataFrame(out)
    if len(t) and t.duplicated(["entity", "variable", "ts_utc"]).any():
        raise RuntimeError("an (entity, variable, ts_utc) is given twice")
    return t


def main(argv=None):
    ap = argparse.ArgumentParser(description="EIA's natural gas delivered for the account of others, a year")
    ap.add_argument("--from", dest="first", default=FIRST, help="the first year, YYYY")
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
            # session 2247: a reused page keeps the time EIA served it
            return json.loads(hit[0]), ip.redact(url), (hit[1] or {}).get("retrieved_at") or retrieved
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
                return r.json(), ip.redact(r.url), dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            log(f"  {ip.redact(r.url)}: HTTP {r.status_code}; " + (f"asked once more in {RETRY_WAIT} s" if attempt == 1 else "not asked again"))
            time.sleep(RETRY_WAIT)
        raise RuntimeError(f"HTTP {r.status_code} twice for {ip.redact(r.url)}")

    try:
        key = ip.load_key("EIA_API_KEY", log)
        if not key:
            raise RuntimeError("EIA_API_KEY is not set (.env or the environment)")
        retrieved = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        # session 635: months before SPLIT are a window of their own, so the pages of SPLIT on answer again
        windows = [(args.first, EARLY_END), (SPLIT, None)] if args.first < SPLIT else [(args.first, None)]
        frames, records = [], 0
        for first, last in windows:
            offset, total = 0, None
            while True:
                params = {"api_key": key, "frequency": "annual", "data[]": "value", "facets[process][]": list(PROCESSES),
                          "start": first}
                if last:
                    params["end"] = last
                params.update({"length": 5000, "offset": offset, "sort[0][column]": "period", "sort[0][direction]": "asc",
                               "sort[1][column]": "series", "sort[1][direction]": "asc"})
                body, url, served = get(params)
                resp = body["response"]
                total = int(resp["total"])
                frames.append(rows(resp["data"], url.split("&length")[0], served))
                offset += len(resp["data"])
                if offset >= total or len(resp["data"]) < 5000:
                    break
            if offset != total:
                raise RuntimeError(f"{first} to {last or 'the latest'}: {offset:,} rows read of the {total:,} EIA counts")
            records += total
        total = records
        s = pd.concat([f for f in frames if len(f)], ignore_index=True)
        if s.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("a row on two pages")
        s = s[ip.SERIES_COLS]
        span = f"{s['ts_utc'].min()[:4]} to {s['ts_utc'].max()[:4]}"
        header = [
            "Energy Research Warehouse (ERW): EIA, natural gas delivered for the account of others (customer choice and transportation gas), by state and sector, a year (session 2377)",
            "Shape: series (docs/datastandard.md v0). entity eia_gas_for_others:<series>; variable residential_for_others, commercial_for_others, industrial_for_others (MMcf) or residential_share, commercial_share, industrial_share "
            "(ratio, EIA's percent divided by 100); ts_utc the year's 1 January; freq P1Y; geo US or US-<state>; node EIA's series description. The states are parts of the U.S.: a sum takes one level.",
            f"EIA gives a 0 (kept), a record without a value or no record (no row) where a state has none; nothing is filled. Hawaii has no record, DC no industrial and Vermont no commercial series. "
            f"The residential share is in whole percents. Years {span}; {total:,} records of EIA's, {len(s):,} rows.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia_gas_for_others.py; {asked[0]} requests of {CEILING}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Energy Information Administration, Natural Gas Annual, natural gas delivered for the account of others (API v2, route natural-gas/cons/acct), {PAGE}",
            f"  access: {API}data/?frequency=annual&data[]=value&start={args.first}",
            'License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Natural Gas Annual").',
        ]
        ip.write_snapshot(s, NAME, header, log, ip.SERIES_COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Energy Information Administration (EIA)",
                                    report="Natural Gas Annual, natural gas delivered for the account of others (API v2)", report_url=PAGE, document_list=API,
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
