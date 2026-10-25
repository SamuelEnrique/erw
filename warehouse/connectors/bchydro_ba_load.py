#!/usr/bin/env python3
"""British Columbia's balancing authority load an hour, January 2024 to September 2026, as BC Hydro publishes it in its Hourly
Control Area Load Reports, one workbook a year (session 2679, chain 134, the session's second own choice; EIA-930 holds BC
Hydro's balancing authority (BCHA) only as a partner in US interchange, and the ERW held no BC load).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/bchydro_ba_load_hourly.csv, from three workbooks
(no key), listed on BC Hydro's historical transmission data page:

    https://www.bchydro.com/content/dam/BCHydro/customer-portal/documents/corporate/suppliers/transmission-system/
        balancing_authority_load_data/Historical%20Transmission%20Data/BalancingAuthorityLoad%20<2024|2025>.xls
    https://www.bchydro.com/content/dam/BCHydro/customer-portal/documents/corporate/suppliers/transmission-system/
        balancing_authority_load_data/BalancingAuthorityLoad%202026.xls   (the year in progress)

    entity      bchydro:bcha:load
    variable    load
    unit        MW (the hour's control area load as published); ts_utc the hour's start; freq PT1H; geo CA-BC
    node        BCHA (the report's area group)

The reports are in Pacific local time with daylight saving, by hour ending (HE 1 to 24): the spring day has 23 hours (no HE 2),
and the autumn day 25, its repeated hour marked "2*" and placed after HE 2 in time, wherever the sheet lists it (the 2025 sheet
lists "2*" before HE 2). Each day's hours are put in that order and counted from the day's local midnight in UTC
(America/Vancouver); a day whose hours are not the ones its date has (23, 24 or 25, and the right labels) stops the run. Only
whole days that ended before the workbook's retrieval are kept; nothing is filled. Each sheet is checked for its title ("Hourly
Control Area Load Report"), its area group (BCHA), its year and its header ("Date", "HE", "Control Area Load"). A load not a
positive number, a date outside the sheet's year, a day given twice or a gap of a day stops the run.

    python warehouse/connectors/bchydro_ba_load.py [--offline] [--fresh] [--out-dir DIR]

Ceiling: three requests a run, saved in warehouse/raw/bchydro/ and reused unless --fresh; --offline asks nothing.
www.bchydro.com's robots file closes extranet, media library and account paths, not these documents (session 2679). License:
internal. BC Hydro's Legal page: its content "may not be copied without the express permission of British Columbia Hydro and
Power Authority (BC Hydro)"; internal until a ruling or BC Hydro's permission.
"""

import argparse
import datetime as dt
import os
import re
import sys
import traceback
from zoneinfo import ZoneInfo

import pandas as pd
import xlrd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "bchydro_ba_load_hourly"
CONNECTOR = "bchydro"
SOURCE = "bchydro:hourly_control_area_load_report"
HOST = "www.bchydro.com"
DIR = ("https://www.bchydro.com/content/dam/BCHydro/customer-portal/documents/corporate/suppliers/transmission-system/"
       "balancing_authority_load_data/")
FILES = {2024: DIR + "Historical%20Transmission%20Data/BalancingAuthorityLoad%202024.xls",
         2025: DIR + "Historical%20Transmission%20Data/BalancingAuthorityLoad%202025.xls",
         2026: DIR + "BalancingAuthorityLoad%202026.xls"}
PAGE = ("https://www.bchydro.com/energy-in-bc/operations/transmission/transmission-system/balancing-authority-load-data/"
        "historical-transmission-data.html")
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
CITATION = "BC Hydro, Hourly Control Area Load Report (balancing authority load data), BCHA"
ZONE = ZoneInfo("America/Vancouver")
X_COLS = []


def day_hours(d):
    a = dt.datetime(d.year, d.month, d.day, tzinfo=ZONE).astimezone(dt.timezone.utc)
    n = d + dt.timedelta(days=1)
    b = dt.datetime(n.year, n.month, n.day, tzinfo=ZONE).astimezone(dt.timezone.utc)
    return a, int((b - a).total_seconds() // 3600)


def he_key(he):
    """A label's place in the day: HE 1 to 24, and "2*", the repeated hour, after HE 2."""
    if isinstance(he, str) and he.strip() == "2*":
        return 2.5
    if isinstance(he, (int, float)) and he == int(he) and 1 <= he <= 24:
        return float(he)
    raise RuntimeError(f"an hour label not HE 1 to 24 or 2*: {he!r}")


def parse_rows(rows, year, retrieved):
    if str(rows[0][0]).strip() != "Hourly Control Area Load Report":
        raise RuntimeError(f"{year}: the title is {rows[0][0]!r}")
    if str(rows[2][1]).strip() != "BCHA":
        raise RuntimeError(f"{year}: the area group is {rows[2][1]!r}")
    if abs(float(rows[1][1])) != year:
        raise RuntimeError(f"{year}: the date range is {rows[1][1]!r}")
    if [re.sub(r"[^A-Za-z ]", "", str(x)).strip() for x in rows[3][:3]] != ["Date", "HE", "Control Area Load"]:  # 2024 has "Date" and a stray mark
        raise RuntimeError(f"{year}: the header is {rows[3][:3]}")
    days = {}
    for r in rows[4:]:
        if all(str(x).strip() == "" for x in r[:3]):
            continue
        d = dt.datetime.strptime(str(r[0]).strip(), "%m/%d/%Y").date()
        if d.year != year:
            raise RuntimeError(f"{year}: a date of another year: {d}")
        v = r[2]
        if not isinstance(v, float) or v <= 0:
            raise RuntimeError(f"{d} HE {r[1]}: not a positive load: {v!r}")
        days.setdefault(d, []).append((he_key(r[1]), v))
    out, prev = [], None
    for d in sorted(days):
        if prev is not None and d != prev + dt.timedelta(days=1):
            raise RuntimeError(f"{year}: a gap after {prev}")
        prev = d
        start, n = day_hours(d)
        keys = sorted(k for k, _ in days[d])
        want = {23: [1.0] + [float(h) for h in range(3, 25)], 24: [float(h) for h in range(1, 25)],
                25: [1.0, 2.0, 2.5] + [float(h) for h in range(3, 25)]}[n]
        if keys != want:
            raise RuntimeError(f"{d}: the hours {keys} are not the {n} its date has")
        if start + dt.timedelta(hours=n) > retrieved:
            continue  # not ended at the workbook's retrieval
        for i, (_, v) in enumerate(sorted(days[d])):
            out.append(((start + dt.timedelta(hours=i)).strftime("%Y-%m-%dT%H:%M:%SZ"), v))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="BC Hydro: British Columbia's balancing authority load an hour")
    ap.add_argument("--offline", action="store_true", help="the saved workbooks only, no request")
    ap.add_argument("--fresh", action="store_true", help="ask for the workbooks again")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    args = ap.parse_args(argv)
    if ip.paused(CONNECTOR) or ip.paused_host(HOST):
        print(f"{NAME}: the publisher is paused (warehouse/metadata/paused_sources.csv); nothing asked")
        return 0
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
        rows, got = [], {}
        for y, url in sorted(FILES.items()):
            content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, fresh=args.fresh, headers=UA, timeout=180, pause=1)
            retrieved = dt.datetime.strptime(rec.get("retrieved_at"), "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)
            sh = xlrd.open_workbook(file_contents=content).sheet_by_index(0)
            sheet = [[sh.cell_value(r, c) for c in range(sh.ncols)] for r in range(sh.nrows)]
            base = dict(source=SOURCE, source_url=url, retrieved_at=rec.get("retrieved_at"), vintage=ip.vintage_of(rec))
            got[y] = base
            rows += [dict(entity="bchydro:bcha:load", variable="load", ts_utc=ts, value=v, unit="MW", freq="PT1H", geo="CA-BC",
                          market="", node="BCHA", **base) for ts, v in parse_rows(sheet, y, retrieved)]
        t = pd.DataFrame(rows)
        if t.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("an hour given twice")
        cols = ip.SERIES_COLS + X_COLS
        t = t[cols].sort_values(["entity", "ts_utc"]).reset_index(drop=True)
        yr = t.groupby(t.ts_utc.str[:4]).value.agg(["sum", "max", "size"])
        head = [
            "Energy Research Warehouse (ERW): BC Hydro, Hourly Control Area Load Report: British Columbia's balancing authority "
            f"(BCHA) load an hour, {t.ts_utc.min()[:10]} to {t.ts_utc.max()[:10]} UTC (session 2679)",
            "Shape: series (docs/datastandard.md v0). entity bchydro:bcha:load; variable load; unit MW; ts_utc the hour's start "
            "(the reports' Pacific local hours ending, daylight saving kept, counted from each day's local midnight); freq PT1H; "
            "geo CA-BC; node BCHA.",
            f"{len(t)} rows; " + "; ".join(f"{k}: {int(r['size'])} hours, {r['sum'] / 1e6:.1f} TWh, peak {r['max']:,.0f} MW"
                                           for k, r in yr.iterrows())
            + ". Whole days only, ended before retrieval; each day's hours checked against its date; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/bchydro_ba_load.py; the workbooks retrieved "
            + ", ".join(f"{y} {b['retrieved_at']}" for y, b in sorted(got.items())),
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} {CITATION}",
            f"  access: {DIR}... (three workbooks; listed on {PAGE})",
            "License: internal. BC Hydro's Legal page: its content may not be copied without its express permission; internal "
            f"until a ruling. Cite: {CITATION}.",
        ]
        ip.write_snapshot(t, NAME, head, log, cols)
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows, {t.entity.nunique()} entities")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{NAME} FAILED, no output file written:\n{tb}")
        print(f"{NAME} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="BC Hydro (British Columbia Hydro and Power Authority)",
                                    report="Hourly Control Area Load Report (balancing authority load data), 2024 to 2026",
                                    report_url=PAGE, document_list=PAGE, license="internal", tables=[NAME])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
