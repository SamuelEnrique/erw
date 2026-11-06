#!/usr/bin/env python3
"""EIA's underground natural gas storage by type, the U.S., a month from 1973: base gas, working gas, total, injections,
withdrawals and net withdrawals, in all fields and separately in salt caverns and in other (non-salt) fields, from
December 1973, the stocks with gaps in 1974 and 1975 where EIA gives none (session 2289's note) (session
2283, chain 104: in place of Argentina, whose operator CAMMESA resets every connection).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/eia_gas_storage_type_monthly.csv, from the
U.S. Energy Information Administration's API v2, route natural-gas/stor/type ("U.S. Underground Natural Gas Storage by
Storage Type"):

    https://api.eia.gov/v2/natural-gas/stor/type/data/?frequency=monthly&data[]=value&start=1973-01

    entity    eia_gas_storage_type:<series>, EIA's series id (one a measure)
    variable  all_base_gas, all_working_gas, all_total, all_injections, all_withdrawals, all_net_withdrawals and the
              same with salt_ and non_salt_ (EIA's processes SAB, SAO, SAT, SAI, SAW, SAN; SSB, SSO, SST, SSI, SSW, SSN;
              SNB, SNO, SNT, SNI, SNW, SNN), all in MMcf (EIA's "MMCF")
    ts_utc    the month's first day at 00:00:00Z; freq P1M; geo US; node EIA's series description

Base and working gas are stocks at the month's end; injections and withdrawals are the month's flows; salt plus non-salt
is all fields. The ERW's eia_gas_storage tables hold the regions and the weekly report, not the split by type. A blank has
no row; nothing is filled. A process, unit or area not in the map stops the run; so does a key given twice. Each row
carries the time EIA served its page (a reused page's first download).

    python warehouse/connectors/eia_gas_storage_type.py [--from 1973-01] [--offline | --fresh]

Ceiling: 10 requests a run (pages of 5,000, 3 seconds apart; a page an earlier run saved in warehouse/raw is reused
unless --fresh; --offline asks nothing). License: public (EIA, record 1 of license_reads.csv; cite "U.S. Energy
Information Administration, Natural Gas Monthly").
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

NAME = "eia_gas_storage_type_monthly"
CONNECTOR = "eia_gas_storage_type"
SOURCE = "eia:natural-gas/stor/type"
API = "https://api.eia.gov/v2/natural-gas/stor/type/"
PAGE = "https://api.eia.gov/v2/natural-gas/stor/type/"  # the route, as read in session 2283
CEILING, PAUSE, RETRY_WAIT = 10, 3, 60
FIRST = "1973-01"
SPLIT, EARLY_END = "1973-01", "1972-12"   # one window: the route starts in 1973
PROCESSES = {"SAB": "all_base_gas", "SAO": "all_working_gas", "SAT": "all_total", "SAI": "all_injections",
             "SAW": "all_withdrawals", "SAN": "all_net_withdrawals", "SSB": "salt_base_gas", "SSO": "salt_working_gas",
             "SST": "salt_total", "SSI": "salt_injections", "SSW": "salt_withdrawals", "SSN": "salt_net_withdrawals",
             "SNB": "non_salt_base_gas", "SNO": "non_salt_working_gas", "SNT": "non_salt_total", "SNI": "non_salt_injections",
             "SNW": "non_salt_withdrawals", "SNN": "non_salt_net_withdrawals"}
AREAS = {"NUS"}   # the route answers the U.S. only (session 2283)
UNITS = {"mmcf": ("MMcf", 1.0, "")}


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
        out.append(dict(entity=f"eia_gas_storage_type:{str(r['series']).strip()}", variable=PROCESSES[r["process"]] + suffix,
                        ts_utc=f"{month}-01T00:00:00Z", value=float(v) * factor, unit=unit, freq="P1M",
                        geo="US", market="",
                        node=str(r.get("series-description") or "").strip(), source=SOURCE, source_url=url,
                        retrieved_at=retrieved, vintage=""))
    t = pd.DataFrame(out)
    if len(t) and t.duplicated(["entity", "variable", "ts_utc"]).any():
        raise RuntimeError("an (entity, variable, ts_utc) is given twice")
    return t


def main(argv=None):
    ap = argparse.ArgumentParser(description="EIA's underground natural gas storage by type, a month")
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
                params = {"api_key": key, "frequency": "monthly", "data[]": "value", "facets[process][]": list(PROCESSES),
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
        span = f"{s['ts_utc'].min()[:7]} to {s['ts_utc'].max()[:7]}"
        header = [
            "Energy Research Warehouse (ERW): EIA, underground natural gas storage by type (all fields, salt, non-salt), the U.S., a month (session 2283)",
            "Shape: series (docs/datastandard.md v0). entity eia_gas_storage_type:<series>; variable all_, salt_ or non_salt_ base_gas, working_gas, total, injections, withdrawals, net_withdrawals (MMcf); "
            "ts_utc the month's first day; freq P1M; geo US. Base and working gas are month-end stocks, the rest the month's flows; salt plus non-salt is all fields.",
            f"A blank has no row; nothing is filled. Months {span}; {total:,} records of EIA's, {len(s):,} rows.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia_gas_storage_type.py; {asked[0]} requests of {CEILING}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Energy Information Administration, Natural Gas Monthly, underground natural gas storage by storage type (API v2, route natural-gas/stor/type), {PAGE}",
            f"  access: {API}data/?frequency=monthly&data[]=value&start={args.first}",
            'License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Natural Gas Monthly").',
        ]
        ip.write_snapshot(s, NAME, header, log, ip.SERIES_COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Energy Information Administration (EIA)",
                                    report="Natural Gas Monthly, underground natural gas storage by storage type (API v2)", report_url=PAGE, document_list=API,
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
