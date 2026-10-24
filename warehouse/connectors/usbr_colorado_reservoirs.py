#!/usr/bin/env python3
"""Lake Mead and Lake Powell a day: pool elevation, storage, total release and inflow, as the Bureau of Reclamation's
hydrodata pages publish them (session 2211, chain 098: the reservoirs behind Hoover and Glen Canyon dams, whose levels
set the Southwest's hydropower).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/usbr_mead_powell_daily.csv, from the
reservoir data files Reclamation's Upper Colorado region publishes for both lakes (one CSV a reservoir and data type,
"datetime,<name>", one line a day, the whole period of record):

    https://www.usbr.gov/uc/water/hydrodata/reservoir_data/<site>/csv/<data type>.csv
        site 919 Lake Powell (Glen Canyon Dam), 921 Lake Mead (Hoover Dam)
        data type 49 pool elevation, 17 storage, 42 total release, 29 inflow (Lake Powell only: Lake Mead's dashboard
        lists no inflow and its file answers HTTP 404)

The files state no unit; Reclamation's status pages do ("ft=feet above mean sea level, cfs=cubic feet per second,
kaf=1000 acre-feet", the Lower Colorado levels page; Lake Powell's elevation in feet and storage in acre-feet, the Glen
Canyon Dam page), and the values match them (Lake Powell at the end of September 2026: 3,518.08 feet and 5.16 million
acre-feet on the Glen Canyon page; session 2211's cross-check):

    entity      usbr_hydrodata:<site> (919, 921); node the reservoir's name
    variable    pool_elevation (ft, Decision 71), storage (acre-ft, Decision 72), total_release and inflow (ft3/s,
                Decision 65)
    ts_utc      the day at 00:00:00Z (Decision 11; Reclamation's day is the reservoir's local day); freq P1D; geo US-AZ
                (both dams stand on Arizona's border, Hoover with Nevada, Glen Canyon near Utah's)

Reclamation's pages say "All data considered provisional and subject to revision." Values as published; a blank has no
row; nothing is filled. A header not "datetime,<name>", a date not YYYY-MM-DD, a value that is not a number or a day
given twice stops the run. A day not yet ended when the file was fetched (Arizona's time, no daylight saving) is left out and
counted (session 2218).

    python warehouse/connectors/usbr_colorado_reservoirs.py [--offline] [--out-dir DIR]

Ceiling: seven requests (two sites, four data types, Lake Mead's inflow not published), each reused from warehouse/raw/usbr_colorado_reservoirs/ with
--offline. www.usbr.gov's robots file disallows only /pn-bin and /gp-bin (sessions 2003 and 2211); data.usbr.gov's
/rise/api is not asked. License: public (Reclamation's disclaimer, record 173: the Department of the Interior's notice,
materials of federal agencies in the public domain).
"""

import argparse
import datetime as dt
import io
import os
import re
import sys
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "usbr_mead_powell_daily"
CONNECTOR = "usbr_colorado_reservoirs"
SOURCE = "usbr:hydrodata_reservoirs"
PAGE = "https://www.usbr.gov/uc/water/hydrodata/reservoir_data/919/dashboard.html"
URL = "https://www.usbr.gov/uc/water/hydrodata/reservoir_data/{site}/csv/{dtype}.csv"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
SITES = {"919": "Lake Powell (Glen Canyon Dam)", "921": "Lake Mead (Hoover Dam)"}
TYPES = {"49": ("pool elevation", "pool_elevation", "ft"), "17": ("storage", "storage", "acre-ft"),
         "42": ("total release", "total_release", "ft3/s"), "29": ("inflow", "inflow", "ft3/s")}
NOT_PUBLISHED = {"921": ("29",)}   # Lake Mead has no inflow file (HTTP 404, session 2211)
TZ = "America/Phoenix"  # session 2218: the reservoirs' local day, for leaving out the day in progress
COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "market", "node", "source", "source_url",
        "retrieved_at", "vintage"]


def file_rows(text, site, dtype, url, retrieved, vintage):
    name, var, unit = TYPES[dtype]
    t = pd.read_csv(io.StringIO(text), dtype=str, keep_default_na=False)
    if [c.strip().lower() for c in t.columns] != ["datetime", name]:
        raise RuntimeError(f"{url}: the header is not 'datetime,{name}': {list(t.columns)}")
    out = []
    for day, v in zip(t.iloc[:, 0], t.iloc[:, 1]):
        day, v = day.strip(), v.strip()
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", day):
            raise RuntimeError(f"{url}: a date not YYYY-MM-DD: {day!r}")
        if v == "":
            continue
        try:
            value = float(v)
        except ValueError:
            raise RuntimeError(f"{url}: {day}: not a number: {v!r}")
        out.append({"entity": f"usbr_hydrodata:{site}", "variable": var, "ts_utc": f"{day}T00:00:00Z", "value": value,
                    "unit": unit, "freq": "P1D", "geo": "US-AZ", "market": "", "node": SITES[site], "source": SOURCE,
                    "source_url": url, "retrieved_at": retrieved, "vintage": vintage})
    return out


def finish(rows):
    t = pd.DataFrame(rows, columns=COLS)
    twice = t[t.duplicated(["entity", "variable", "ts_utc"], keep=False)]
    if len(twice):
        raise RuntimeError(f"a day given twice: {twice.entity.iloc[0]} {twice.variable.iloc[0]} {twice.ts_utc.iloc[0]}")
    return t.sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)


def ended_days(t):
    """Session 2218: only days that had ended where the reservoir is when the file was fetched. Reclamation's file can
    end with the day in progress (Lake Mead's total release of 23 October 2026, fetched at 18:35 that day, was a part
    day); a day on or after the retrieval's local date is left out, and counted."""
    local = pd.to_datetime(t.retrieved_at, utc=True).dt.tz_convert(TZ).dt.strftime("%Y-%m-%d")
    keep = t.ts_utc.str[:10] < local
    return t[keep].reset_index(drop=True), t[~keep]


def main(argv=None):
    ap = argparse.ArgumentParser(description="Reclamation: Lake Mead and Lake Powell, elevation, storage, release, inflow, a day")
    ap.add_argument("--offline", action="store_true", help="the saved files only, no request")
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
    try:
        if not args.offline and (ip.paused("usbr") or ip.paused_host("www.usbr.gov")):
            raise RuntimeError("Reclamation is paused (warehouse/metadata/paused_sources.csv): not requested")
        rows, got = [], []
        for site in SITES:
            for dtype in TYPES:
                if dtype in NOT_PUBLISHED.get(site, ()):
                    continue
                url = URL.format(site=site, dtype=dtype)
                content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=120)
                rows += file_rows(content.decode("utf-8", errors="replace"), site, dtype, url, rec.get("retrieved_at") or "", ip.vintage_of(rec))
                got.append((site, dtype, rec.get("retrieved_at") or ""))
        t, part = ended_days(finish(rows))
        span = t.groupby(["node", "variable"]).ts_utc.agg(["min", "max"])
        header = [
            "Energy Research Warehouse (ERW): Bureau of Reclamation, Upper Colorado region's hydrodata, Lake Powell and Lake Mead, pool elevation, storage, total release and inflow, a day (session 2211)",
            "Shape: series (docs/datastandard.md v0). entity usbr_hydrodata:<site> (919 Lake Powell, 921 Lake Mead); variable pool_elevation (ft, feet above mean sea level, Decision 71), storage (acre-ft, Decision 72), "
            "total_release and inflow (ft3/s); ts_utc the day at 00:00:00Z; freq P1D; geo US-AZ. Reclamation: 'All data considered provisional and subject to revision.'",
            f"{len(t)} rows: " + "; ".join(f"{n}, {v} {a[:10]} to {b[:10]}" for (n, v), (a, b) in span.iterrows())
            + f". {len(part)} rows of a day not yet ended when its file was fetched are left out (session 2218). The files state no unit; Reclamation's status pages give them (ft feet above mean sea level, cfs cubic feet per second, storage in acre-feet). A blank has no row; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/usbr_colorado_reservoirs.py; the files retrieved " + "; ".join(f"{s}/{d} {r}" for s, d, r in got),
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Bureau of Reclamation, Upper Colorado Basin Region, reservoir data (hydrodata), {PAGE}",
            f"  access: {URL.format(site='<site>', dtype='<data type>')}",
            "License: public (U.S. Bureau of Reclamation, a work of the U.S. government; the Department of the Interior's notice). Cite: U.S. Bureau of Reclamation, reservoir data, provisional.",
        ]
        ip.write_csv(t, NAME, header, log, cols=COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Bureau of Reclamation (USBR)",
                                    report="Upper Colorado region's reservoir data (hydrodata): Lake Powell and Lake Mead",
                                    report_url=PAGE, document_list=URL.format(site="<site>", dtype="<data type>"), license="public",
                                    tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows")
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
