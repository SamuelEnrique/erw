#!/usr/bin/env python3
"""EIA's nuclear outages by reactor: each nuclear reactor's capacity and the capacity out of service, a day (sessions 548
and 549, from session 516's connector by plant).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/eia_nuclear_outages_generator_daily.csv, from
the U.S. Energy Information Administration's API v2, route nuclear-outages/generator-nuclear-outages (daily, 2007 on),
read in two windows, 2007 to 2014 and 2015 on, each within a run's ceiling (session 523):

    https://api.eia.gov/v2/nuclear-outages/generator-nuclear-outages/data/?frequency=daily&data[]=capacity&data[]=outage
        &data[]=percentOutage&start=2007-01-01&end=2014-12-31   and   ...&start=2015-01-01

    entity    eia_nuclear_outages_gen:<facility>:<generator>, EIA's plant and reactor ids; node the plant's name and the
              reactor; geo US
    variable  capacity (MW), outage (MW), outage_share (ratio; EIA's percent divided by 100)
    ts_utc    the day at 00:00:00Z; freq P1D

EIA estimates the outages from the Nuclear Regulatory Commission's daily power reactor status reports (each reactor's
percent of full power, set against its capacity); the figures are EIA's as it publishes them. A blank has no row; nothing
is filled. A unit not in the map stops the run; so does a day given twice.

    python warehouse/connectors/eia_nuclear_outages_generator.py [--from 2015-01-01] [--offline | --fresh]   # one window
    python warehouse/connectors/eia_nuclear_outages_generator.py [--offline | --fresh]                     # both windows

Ceiling: 98 requests a run (pages of 5,000, 3 seconds apart; about 36,000 rows a year, so each window is about 50 to
60 pages; a page an earlier run saved in warehouse/raw is reused unless --fresh, so a window already read asks nothing;
--offline asks nothing). License: public (EIA, record 1 of license_reads.csv; cite "U.S. Energy Information
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

NAME = "eia_nuclear_outages_generator_daily"
CONNECTOR = "eia_nuclear_outages_generator"
SOURCE = "eia:nuclear-outages/generator-nuclear-outages"
API = "https://api.eia.gov/v2/nuclear-outages/generator-nuclear-outages/"
PAGE = "https://www.eia.gov/nuclear/outages/"
CEILING, PAUSE, RETRY_WAIT = 98, 3, 60
FIRST = "2015-01-01"
# session 523: the windows a run reads, in order; the last one open-ended (its pages saved by session 516)
WINDOWS = [("2007-01-01", "2014-12-31"), ("2015-01-01", None)]
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
            fac, gen = str(r["facility"]).strip(), str(r["generator"]).strip()
            out.append(dict(entity=f"eia_nuclear_outages_gen:{fac}:{gen}", variable=variable, ts_utc=f"{day}T00:00:00Z", value=float(v) * factor,
                            unit=unit, freq="P1D", geo="US", market="", node=f"{str(r.get('facilityName') or '').strip()}, reactor {gen}", source=SOURCE,
                            source_url=url, retrieved_at=retrieved, vintage=""))
    t = pd.DataFrame(out)
    if len(t) and t.duplicated(["entity", "variable", "ts_utc"]).any():
        raise RuntimeError("an (entity, variable, ts_utc) is given twice")
    return t


def main(argv=None):
    ap = argparse.ArgumentParser(description="EIA's nuclear outages by reactor, a day")
    ap.add_argument("--from", dest="first", help="one window from this day, YYYY-MM-DD (default: the windows of WINDOWS)")
    ap.add_argument("--to", dest="last", help="the window's last day, YYYY-MM-DD (with --from)")
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
        # Session 516: EIA's "total" for this route counts more rows than the data hold (on 21 October 2026, 413,039
        # from 2015 on, while the pages ran day by day to the newest day and ended at 247,167; for one day it counts 95
        # plants and returns 55, the plants whose figures are blank being left out of the data). So the run reads until
        # a page comes back short, and checks that the pages run in order with no day missing; the per-day sums are
        # checked against EIA's U.S. total in session 516's report.
        windows = [(args.first, args.last)] if args.first else WINDOWS
        frames, days, offset = [], [], 0
        for start, end in windows:
            offset = 0
            while True:
                params = {"api_key": key, "frequency": "daily", "data[]": list(DATA), "start": start}
                if end:
                    params["end"] = end
                params.update({"length": 5000, "offset": offset, "sort[0][column]": "period", "sort[0][direction]": "asc",
                               "sort[1][column]": "facility", "sort[1][direction]": "asc",
                               "sort[2][column]": "generator", "sort[2][direction]": "asc"})
                body, url = get(params)
                resp = body["response"]
                data = resp["data"]
                p = [str(r["period"])[:10] for r in data]
                if p != sorted(p) or (days and p and p[0] < days[-1]) or (end and p and p[-1] > end):
                    raise RuntimeError(f"window from {start}: the page at offset {offset:,} is not in day order")
                days.extend(p)
                frames.append(rows(data, url.split("&length")[0], retrieved))
                offset += len(data)
                if len(data) < 5000:
                    break
            log(f"window {start} to {end or 'the newest day'}: {offset:,} rows")
        if not days:
            raise RuntimeError("no rows")
        have = set(days)
        want = pd.date_range(days[0], days[-1], freq="D").strftime("%Y-%m-%d")
        missing = [d for d in want if d not in have]
        if missing:
            raise RuntimeError(f"{len(missing)} days with no row, from {missing[0]}")
        log(f"{len(days):,} rows, {len(want):,} days from {days[0]} to {days[-1]}, none missing (EIA's total for the last window says {int(resp['total']):,})")
        s = pd.concat([f for f in frames if len(f)], ignore_index=True)
        if s.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("a row on two pages")
        s = s[ip.SERIES_COLS]
        span = f"{s['ts_utc'].min()[:10]} to {s['ts_utc'].max()[:10]}"
        header = [
            "Energy Research Warehouse (ERW): EIA, status of U.S. nuclear outages, each reactor's capacity and outages, a day (sessions 548 and 549)",
            "Shape: series (docs/datastandard.md v0). entity eia_nuclear_outages_gen:<facility>:<generator> (EIA's plant and reactor ids), node the plant's name and the reactor; variable capacity (MW), outage (MW) or outage_share (ratio, EIA's percent divided by 100); ts_utc the day; freq P1D.",
            f"EIA's estimates from the NRC's daily power reactor status reports, as EIA publishes them; nothing is filled. Days {span}.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia_nuclear_outages_generator.py; {asked[0]} requests of {CEILING}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Energy Information Administration, Status of U.S. Nuclear Outages (API v2), {PAGE}",
            f"  access: {API}data/?frequency=daily&data[]=capacity&data[]=outage&data[]=percentOutage&start=<first day>[&end=<last day>], the windows " + "; ".join(f"{a} to {b or 'the newest day'}" for a, b in windows),
            'License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Status of U.S. Nuclear Outages").',
        ]
        ip.write_snapshot(s, NAME, header, log, ip.SERIES_COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Energy Information Administration (EIA)",
                                    report="Status of U.S. Nuclear Outages, by reactor (API v2, daily)", report_url=PAGE, document_list=API,
                                    license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(s):,} rows"))
        print(f"{NAME}: {len(s):,} rows, {s['entity'].nunique()} reactors, {span}; {asked[0]} requests")
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
