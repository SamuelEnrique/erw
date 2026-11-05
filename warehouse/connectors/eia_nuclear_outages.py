#!/usr/bin/env python3
"""EIA's U.S. nuclear outages: the U.S. fleet's capacity and the capacity out of service, a day (session 513, a public
source probed in place of DOE's OE-417, which has no file to pull).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/eia_nuclear_outages_daily.csv, from the
U.S. Energy Information Administration's API v2, route nuclear-outages/us-nuclear-outages (daily, 2007 on):

    https://api.eia.gov/v2/nuclear-outages/us-nuclear-outages/data/?frequency=daily&data[]=capacity&data[]=outage
        &data[]=percentOutage&start=2007-01-01

    entity    eia_nuclear_outages:US; geo US
    variable  capacity (MW), outage (MW), outage_share (ratio; EIA's percent divided by 100)
    ts_utc    the day at 00:00:00Z; freq P1D

EIA estimates the outages from the Nuclear Regulatory Commission's daily power reactor status reports (each reactor's
percent of full power, set against its capacity); the figures are EIA's as it publishes them. A blank has no row; nothing
is filled. A unit not in the map stops the run; so does a day given twice.

    python warehouse/connectors/eia_nuclear_outages.py

Ceiling: 4 requests a run (pages of 5,000, 3 seconds apart; a page an earlier run saved in warehouse/raw is reused unless
it holds the newest days). License: public (EIA, record 1 of license_reads.csv; cite "U.S. Energy Information
Administration, Status of U.S. Nuclear Outages").
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

NAME = "eia_nuclear_outages_daily"
CONNECTOR = "eia_nuclear_outages"
SOURCE = "eia:nuclear-outages/us-nuclear-outages"
API = "https://api.eia.gov/v2/nuclear-outages/us-nuclear-outages/"
PAGE = "https://www.eia.gov/nuclear/outages/"
CEILING, PAUSE, RETRY_WAIT = 4, 3, 60
FIRST = "2007-01-01"
DATA = {"capacity": ("capacity", {"megawatts": ("MW", 1.0)}),
        "outage": ("outage", {"megawatts": ("MW", 1.0)}),
        "percentOutage": ("outage_share", {"percent": ("ratio", 0.01)})}


def rows(data, url, retrieved):
    out = []
    for r in data:
        day = str(r["period"])[:10]
        dt.date.fromisoformat(day)
        for col, (variable, units) in DATA.items():
            v = pd.to_numeric(r.get(col), errors="coerce")
            if pd.isna(v):
                continue
            u = str(r.get(f"{col}-units", "")).strip().lower()
            if u not in units:
                raise RuntimeError(f"{col}: a unit not in the map: {u!r}")
            unit, factor = units[u]
            out.append(dict(entity="eia_nuclear_outages:US", variable=variable, ts_utc=f"{day}T00:00:00Z", value=float(v) * factor,
                            unit=unit, freq="P1D", geo="US", market="", node="U.S. nuclear fleet", source=SOURCE,
                            source_url=url, retrieved_at=retrieved, vintage=""))
    t = pd.DataFrame(out)
    if len(t) and t.duplicated(["entity", "variable", "ts_utc"]).any():
        raise RuntimeError("an (entity, variable, ts_utc) is given twice")
    return t


def main(argv=None):
    ap = argparse.ArgumentParser(description="EIA's U.S. nuclear outages, a day")
    ap.add_argument("--offline", action="store_true", help="the pages from warehouse/raw only, no request")
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
        if args.offline:
            hit = ip.raw_cached(CONNECTOR, url)
            if not hit:
                raise RuntimeError(f"offline: {ip.redact(url)} is not in warehouse/raw/{CONNECTOR}/")
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
        frames, offset, total = [], 0, None
        while True:
            body, url = get({"api_key": key, "frequency": "daily", "data[]": list(DATA), "start": FIRST, "length": 5000,
                             "offset": offset, "sort[0][column]": "period", "sort[0][direction]": "asc"})
            resp = body["response"]
            total = int(resp["total"])
            frames.append(rows(resp["data"], url.split("&length")[0], retrieved))
            offset += len(resp["data"])
            if offset >= total or not resp["data"]:
                break
        if offset != total:
            raise RuntimeError(f"{offset:,} days read of the {total:,} EIA counts")
        s = pd.concat([f for f in frames if len(f)], ignore_index=True)
        if s.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("a day on two pages")
        s = s[ip.SERIES_COLS]
        span = f"{s['ts_utc'].min()[:10]} to {s['ts_utc'].max()[:10]}"
        header = [
            "Energy Research Warehouse (ERW): EIA, status of U.S. nuclear outages, the U.S. fleet's capacity and outages, a day (session 513)",
            "Shape: series (docs/datastandard.md v0). entity eia_nuclear_outages:US; variable capacity (MW), outage (MW) or outage_share (ratio, EIA's percent divided by 100); ts_utc the day; freq P1D.",
            f"EIA's estimates from the NRC's daily power reactor status reports, as EIA publishes them; nothing is filled. Days {span}.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia_nuclear_outages.py; {asked[0]} requests of {CEILING}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Energy Information Administration, Status of U.S. Nuclear Outages (API v2), {PAGE}",
            f"  access: {API}data/?frequency=daily&data[]=capacity&data[]=outage&data[]=percentOutage&start={FIRST}",
            'License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Status of U.S. Nuclear Outages").',
        ]
        ip.write_snapshot(s, NAME, header, log, ip.SERIES_COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Energy Information Administration (EIA)",
                                    report="Status of U.S. Nuclear Outages (API v2, daily)", report_url=PAGE, document_list=API,
                                    license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(s):,} rows"))
        print(f"{NAME}: {len(s):,} rows, {span}; {asked[0]} requests")
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
