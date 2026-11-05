#!/usr/bin/env python3
"""Nova Scotia's in-province load an hour, January 2022 to the last month posted in 2026, as Nova Scotia Power (NS Power)
publishes it on its OASIS site in its Hourly Total Net Nova Scotia Load reports, one file a year (session 2708, chain 136; the
ERW held Nova Scotia only in Statistics Canada's monthly generation, and EIA-930 holds no Canadian Maritime area).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/nspower_ns_load_hourly.csv, from five CSV files (no
key), listed on the OASIS page https://www.nspower.ca/oasis/monthly-reports/hourly-total-net-nova-scotia-load:

    https://www.nspower.ca/docs/default-source/monthly-reports/<year>...nspi-hourly-loads-report-for-nbp-so....csv  (2022 to 2026)

    entity      nspower:ns:load
    variable    load
    unit        MW (the page: "All Load Values are in MW, totalized over 1 hour"); ts_utc the hour's start; freq PT1H; geo CA-NS
    node        Nova Scotia Power in-province load (the file's title)

The files give an hour of the year (HOUR), a local date and time and the load. The time is Atlantic local time with daylight
saving, by hour ending: each day's 24th hour carries its own date at 00:00 ("2025-01-01 00:00" is the hour ending at midnight
that ends 1 January), the spring day has 23 hours (no hour ending 03:00, and HOUR skips its number) and the autumn day has 24
rows for its 25 hours in the 2025 and 2026 files (the hour ending 02:00 happens twice and is given once), and 25 in the 2022 to
2024 files, which list 02:00 twice with the same value. Each hour is placed from its day's local midnight in UTC
(America/Halifax); the autumn day's 02:00 cannot be placed (which repeated hour a single row is, or whether a second is a copy,
the files do not say), so it has no row, and the day's hours from 04:00 and 05:00 UTC have none. HOUR is checked to rise row by
row (the 2025 file skips the spring hour's number, the 2022 file does not), and each day's hours against the ones its date has
(the autumn day's 02:00 once or twice). NS Power lost 1 to 25 April 2025 in a
cybersecurity incident (the page's note): those hours read "Data Lost Due To Cybersecurity Incident" and have no row, as has a
blank value; a file's last hours with no value are counted as not yet posted (the 2026 file lists the year's hours ahead of its
figures); nothing is filled. Only days ended before the file's retrieval are kept. A title, a header or a time not in this
form, a load not a positive number, an hour given twice or a date outside the file's year stops the run.

    python warehouse/connectors/nspower_ns_load.py [--offline] [--fresh] [--out-dir DIR]

Ceiling: five requests a run, saved in warehouse/raw/nspower/ and reused unless --fresh; --offline asks nothing.
www.nspower.ca's robots file closes only /WindFarmMap/ (session 2708); nspower.ca redirects to it. License: internal. NS Power's
Terms of Service (https://www.nspower.ca/legal, 3.1): the creative works on the site are its exclusive property and "You will not
use our Intellectual Property Rights ... for any purpose"; internal until a ruling or NS Power's permission.
"""

import argparse
import csv
import datetime as dt
import io
import os
import sys
import traceback
from zoneinfo import ZoneInfo

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "nspower_ns_load_hourly"
CONNECTOR = "nspower"
SOURCE = "nspower:oasis_hourly_total_net_ns_load"
HOST = "www.nspower.ca"
DIR = "https://www.nspower.ca/docs/default-source/monthly-reports/"
FILES = {2022: DIR + "2022---nspi-hourly-loads-report-for-nbp-sodd31c644-318f-47da-aec8-749508b9470a.csv?sfvrsn=877b232d_26&download=true",
         2023: DIR + "2023---nspi-hourly-loads-report-for-nbp-so.csv?sfvrsn=5097eaa3_27&download=true",
         2024: DIR + "2024---nspi-hourly-loads-report-for-nbp-so(csv).csv?sfvrsn=380aee56_30&download=true",
         2025: DIR + "2025---nspi-hourly-loads-report-for-nbp-so(csv).csv?sfvrsn=ce59ae78_11&download=true",
         2026: DIR + "2026-nspi-hourly-loads-report-for-nbp-so(csv).csv?sfvrsn=85a31a17_10&download=true"}
PAGE = "https://www.nspower.ca/oasis/monthly-reports/hourly-total-net-nova-scotia-load"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
CITATION = "Nova Scotia Power, OASIS, Hourly Total Net Nova Scotia Load"
TITLE = "Nova Scotia Power in-province load"
LOST = "Data Lost Due To Cybersecurity Incident"
ZONE = ZoneInfo("America/Halifax")
X_COLS = []


def day_hours(d):
    a = dt.datetime(d.year, d.month, d.day, tzinfo=ZONE).astimezone(dt.timezone.utc)
    n = d + dt.timedelta(days=1)
    b = dt.datetime(n.year, n.month, n.day, tzinfo=ZONE).astimezone(dt.timezone.utc)
    return a, int((b - a).total_seconds() // 3600)


def place(he, n):
    """The hour's start, in hours after the day's local midnight, for hour ending `he` (1 to 24) on a day of `n` hours; None for
    the autumn day's 02:00, which cannot be placed."""
    if n == 24:
        return he - 1
    if n == 23:
        if he == 3:
            raise RuntimeError("an hour ending 03:00 on the spring day")
        return he - 1 if he < 3 else he - 2
    if n == 25:
        if he == 2:
            return None
        return 0 if he == 1 else he
    raise RuntimeError(f"a day of {n} hours")


def parse_rows(rows, year, retrieved):
    """The hours of one year's file, as (ts_utc, value); and the counts of hours lost, blank and not placed."""
    if not rows or rows[0][0].strip() != TITLE:
        raise RuntimeError(f"{year}: the title is {rows[0][:1] if rows else rows!r}")
    h = next((i for i, r in enumerate(rows) if r and r[0].strip() == "HOUR"), None)
    if h is None or [x.strip() for x in rows[h][:3]] != ["HOUR", "Date/time", "Load [MW]"]:
        raise RuntimeError(f"{year}: no header row HOUR, Date/time, Load [MW]")
    days, counts, last = {}, {"lost": 0, "blank": 0, "not_posted": 0, "not_placed": 0}, 0
    for r in rows[h + 1:]:
        if all(not x.strip() for x in r):
            continue
        stamp = None
        for form in ("%Y-%m-%d %H:%M", "%m/%d/%Y %H:%M"):  # the 2023 file writes "1/1/2023 1:00"
            try:
                stamp = dt.datetime.strptime(r[1].strip(), form)
                break
            except ValueError:
                pass
        if stamp is None:
            raise RuntimeError(f"{year}: a time not in the form YYYY-MM-DD HH:MM or M/D/YYYY H:MM: {r[:3]}")
        if stamp.minute or stamp.year != year:
            raise RuntimeError(f"{year}: a time outside the year or not on the hour: {r[1]!r}")
        d, he = stamp.date(), stamp.hour or 24
        if not r[0].strip().isdigit() or int(r[0]) <= last:
            raise RuntimeError(f"{d} {he}: HOUR {r[0]!r} does not follow {last}")
        last = int(r[0])
        if he in days.setdefault(d, {}):
            if he == 2 and day_hours(d)[1] == 25:
                days[d][he] = days[d][he] + [r[2].strip()]  # the autumn day's 02:00 listed twice (the 2022 to 2024 files)
                continue
            raise RuntimeError(f"{d}: the hour ending {he} given twice")
        days[d][he] = [r[2].strip()]
    out, run = [], 0
    for d in sorted(days):
        start, n = day_hours(d)
        want = {24: set(range(1, 25)), 23: set(range(1, 25)) - {3}, 25: set(range(1, 25))}[n]
        if set(days[d]) != want:
            raise RuntimeError(f"{d}: the hours {sorted(days[d])} are not the {n} its date has")
        if start + dt.timedelta(hours=n) > retrieved:
            continue  # not ended at the file's retrieval
        for he, vs in sorted(days[d].items()):
            if place(he, n) is None:
                counts["not_placed"] += len(vs)
                continue
            v = vs[0]
            if v == LOST:
                counts["lost"] += 1
                run = 0
                continue
            if not v:
                counts["blank"] += 1
                run += 1
                continue
            run = 0
            try:
                x = float(v)
            except ValueError:
                raise RuntimeError(f"{d} {he}: not a load: {v!r}")
            if x <= 0:
                raise RuntimeError(f"{d} {he}: not a positive load: {v!r}")
            out.append(((start + dt.timedelta(hours=place(he, n))).strftime("%Y-%m-%dT%H:%M:%SZ"), x))
    counts["blank"] -= run  # the file's last hours with no value: months not yet posted (the year in progress)
    counts["not_posted"] = run
    return out, counts


def main(argv=None):
    ap = argparse.ArgumentParser(description="NS Power: Nova Scotia's in-province load an hour")
    ap.add_argument("--offline", action="store_true", help="the saved files only, no request")
    ap.add_argument("--fresh", action="store_true", help="ask for the files again")
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
        rows, got, tally = [], {}, {}
        for y, url in sorted(FILES.items()):
            content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, fresh=args.fresh, headers=UA, timeout=180, pause=1)
            retrieved = dt.datetime.strptime(rec.get("retrieved_at"), "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)
            lines = list(csv.reader(io.StringIO(content.decode("utf-8-sig"))))
            base = dict(source=SOURCE, source_url=url, retrieved_at=rec.get("retrieved_at"), vintage=ip.vintage_of(rec))
            got[y] = base
            hours, tally[y] = parse_rows(lines, y, retrieved)
            rows += [dict(entity="nspower:ns:load", variable="load", ts_utc=ts, value=v, unit="MW", freq="PT1H", geo="CA-NS",
                          market="", node=TITLE, **base) for ts, v in hours]
        t = pd.DataFrame(rows)
        if t.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("an hour given twice")
        cols = ip.SERIES_COLS + X_COLS
        t = t[cols].sort_values(["entity", "ts_utc"]).reset_index(drop=True)
        yr = t.groupby(t.ts_utc.str[:4]).value.agg(["sum", "max", "size"])
        gaps = "; ".join(f"{y}: {c['lost']} lost, {c['blank']} blank, {c['not_posted']} not yet posted, {c['not_placed']} not placed" for y, c in sorted(tally.items()))
        head = [
            "Energy Research Warehouse (ERW): Nova Scotia Power, OASIS, Hourly Total Net Nova Scotia Load: Nova Scotia's in-province "
            f"load an hour, {t.ts_utc.min()[:10]} to {t.ts_utc.max()[:10]} UTC (session 2708)",
            "Shape: series (docs/datastandard.md v0). entity nspower:ns:load; variable load; unit MW (totalized over the hour); ts_utc "
            "the hour's start (the files' Atlantic local hours ending, daylight saving kept, placed from each day's local midnight); "
            "freq PT1H; geo CA-NS; node the file's title.",
            f"{len(t)} rows; " + "; ".join(f"{k}: {int(r['size'])} hours, {r['sum'] / 1e6:.2f} TWh, peak {r['max']:,.0f} MW"
                                           for k, r in yr.iterrows())
            + f". Hours without a row: {gaps} (the autumn day's 02:00, listed once or twice, is not placed). Whole days only, ended before "
            "retrieval; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/nspower_ns_load.py; the files retrieved "
            + ", ".join(f"{y} {b['retrieved_at']}" for y, b in sorted(got.items())),
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} {CITATION}",
            f"  access: {DIR}... (five CSV files, 2022 to 2026; listed on {PAGE})",
            "License: internal. NS Power's Terms of Service keep the site's creative works as its property, not to be used for any "
            f"purpose; internal until a ruling or NS Power's permission. Cite: {CITATION}.",
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
            ip.update_sources([dict(source=SOURCE, publisher="Nova Scotia Power (NS Power)",
                                    report="OASIS, Hourly Total Net Nova Scotia Load, 2022 to 2026",
                                    report_url=PAGE, document_list=PAGE, license="internal", tables=[NAME])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
