#!/usr/bin/env python3
"""NOAA's U.S. Billion-Dollar Weather and Climate Disasters, 1980 to 2024: each event's name, type, dates, cost and
deaths, as NCEI's retired product last published them (session 2073, chain 067: the disasters' costs beside the storms of
noaa_ncei_storm_events).

Energy Research Warehouse (ERW) connector. One events table, warehouse/output/noaa_ncei_billion_disasters.csv, from the
product's events file (the product was retired in 2025; DOI 10.25921/stkw-7w73):

    https://www.ncei.noaa.gov/access/billions/events-US-1980-2024.csv

The file starts with two lines (its title and "Cost values are in millions of dollars"), then
"Name,Disaster,Begin Date,End Date,CPI-Adjusted Cost,Unadjusted Cost,Deaths", one line an event.

    event_id     noaa_billion:<begin date>:<12 hex of the SHA-1 of the event's name>, stable while NCEI keeps the name
    event_date   the event's begin date; x_end_date its end
    event_type   NCEI's disaster type in snake case (tropical_cyclone, severe_storm, flooding, drought, wildfire,
                 winter_storm, freeze); x_disaster keeps NCEI's words
    x_*          the event's name, its cost in USD adjusted for inflation as NCEI published it (the CPI to the record's
                 last year) and unadjusted, NCEI's millions written as dollars, and its deaths

The file names no state an event touched; the product's maps did, and are not taken. Values as published; a blank stays
blank; nothing is filled. A header not the one above, a date not YYYYMMDD, a cost that is not a number or an event given
twice stops the run.

    python warehouse/connectors/noaa_billion_disasters.py [--offline] [--out-dir DIR]

Ceiling: one request (the file, reused from warehouse/raw/noaa_billion_disasters/ when saved: the record no longer
changes). NCEI's robots file disallows /data* and /orders* and parts of /access/crn/; /access/billions/ is not among them.
License: NOAA's data, a U.S. Government work in the public domain (NOAA NCEI, read 9 and read 182).
"""

import argparse
import datetime as dt
import hashlib
import io
import os
import re
import sys
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "noaa_ncei_billion_disasters"
CONNECTOR = "noaa_billion_disasters"
SOURCE = "noaa:billion_dollar_disasters"
PAGE = "https://www.ncei.noaa.gov/access/billions/"
URL = "https://www.ncei.noaa.gov/access/billions/events-US-1980-2024.csv"
DOI = "10.25921/stkw-7w73"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
EVENT_COLS = ["event_id", "event_date", "event_type", "parties", "entity_ids", "mw", "price", "currency", "status",
              "source", "source_url", "retrieved_at"]
X_COLS = ["x_name", "x_disaster", "x_end_date", "x_cost_cpi_adjusted_usd", "x_cost_unadjusted_usd", "x_deaths"]
HEADER = ["Name", "Disaster", "Begin Date", "End Date", "CPI-Adjusted Cost", "Unadjusted Cost", "Deaths"]


def text(v):
    return re.sub(r"\s+", " ", str(v or "")).strip()


def day(v):
    s = text(v)
    if not re.fullmatch(r"\d{8}", s):
        raise RuntimeError(f"a date not YYYYMMDD: {s!r}")
    return f"{s[:4]}-{s[4:6]}-{s[6:]}"


def dollars(v):
    s = text(v)
    if s == "":
        return ""
    try:
        return f"{float(s) * 1_000_000:.0f}"
    except ValueError:
        raise RuntimeError(f"a cost that is not a number: {s!r}")


def build(content, url, retrieved):
    lines = content.replace("\r\n", "\n").split("\n")
    head = next((i for i, ln in enumerate(lines) if ln.startswith("Name,Disaster,")), None)
    if head is None:
        raise RuntimeError("no header line")
    if not any("millions of dollars" in ln for ln in lines[:head]):
        raise RuntimeError("the file no longer says its costs are in millions of dollars")
    t = pd.read_csv(io.StringIO("\n".join(lines[head:])), dtype=str, keep_default_na=False)
    if list(t.columns) != HEADER:
        raise RuntimeError(f"the header is not the one expected: {list(t.columns)}")
    out = []
    for r in t.to_dict("records"):
        name, begin = text(r["Name"]), day(r["Begin Date"])
        deaths = text(r["Deaths"])
        if deaths and not re.fullmatch(r"\d+", deaths):
            raise RuntimeError(f"{name}: deaths not a whole number: {deaths!r}")
        out.append({"event_id": f"noaa_billion:{begin}:{hashlib.sha1(name.encode('utf-8')).hexdigest()[:12]}",
                    "event_date": begin, "event_type": re.sub(r"[^a-z0-9]+", "_", text(r["Disaster"]).lower()).strip("_"),
                    "parties": "", "entity_ids": "", "mw": "", "price": "", "currency": "", "status": "", "source": SOURCE,
                    "source_url": url, "retrieved_at": retrieved, "x_name": name, "x_disaster": text(r["Disaster"]),
                    "x_end_date": day(r["End Date"]), "x_cost_cpi_adjusted_usd": dollars(r["CPI-Adjusted Cost"]),
                    "x_cost_unadjusted_usd": dollars(r["Unadjusted Cost"]), "x_deaths": deaths})
    t = pd.DataFrame(out, columns=EVENT_COLS + X_COLS)
    twice = t.event_id[t.event_id.duplicated()]
    if len(twice):
        raise RuntimeError(f"an event given twice: {list(twice)[:3]}")
    return t.sort_values(["event_date", "event_id"]).reset_index(drop=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description="NOAA's billion-dollar disasters, 1980 to 2024")
    ap.add_argument("--offline", action="store_true", help="the saved file only, no request")
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
        content, rec = ip.fetch_raw(CONNECTOR, URL, log, offline=args.offline, headers=UA, timeout=120)
        t = build(content.decode("utf-8", errors="replace"), URL, rec.get("retrieved_at") or "")
        by = t.groupby("event_type").size().sort_values(ascending=False)
        cost = pd.to_numeric(t.x_cost_cpi_adjusted_usd, errors="coerce").sum()
        header = [
            "Energy Research Warehouse (ERW): NOAA NCEI, U.S. Billion-Dollar Weather and Climate Disasters, 1980 to 2024 (the product retired in 2025) (session 2073)",
            "Shape: events (docs/datastandard.md v0). event_id noaa_billion:<begin date>:<12 hex of the SHA-1 of the name>; event_date the begin date; event_type NCEI's "
            "disaster type in snake case; x_cost_cpi_adjusted_usd and x_cost_unadjusted_usd NCEI's millions written as dollars; x_deaths as published.",
            f"{len(t)} events, CPI-adjusted cost USD {cost:,.0f}: " + "; ".join(f"{k} {v}" for k, v in by.items())
            + ". The file names no state; the product's maps are not taken. Values as published; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/noaa_billion_disasters.py; the file retrieved {rec.get('retrieved_at') or ''}, last modified {ip.vintage_of(rec)}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} NOAA National Centers for Environmental Information (NCEI) U.S. Billion-Dollar Weather and Climate Disasters (2025), {PAGE}, DOI: {DOI}",
            f"  access: {URL}",
            "License: NOAA's data, a U.S. Government work in the public domain. Cite: NOAA NCEI U.S. Billion-Dollar Weather and Climate Disasters (2025), DOI 10.25921/stkw-7w73.",
        ]
        ip.write_snapshot(t, NAME, header, log, cols=EVENT_COLS + X_COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="NOAA National Centers for Environmental Information (NCEI)",
                                    report="U.S. Billion-Dollar Weather and Climate Disasters, events 1980 to 2024 (retired 2025)",
                                    report_url=PAGE, document_list=URL, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} events"))
        print(f"{NAME}: {len(t)} events, CPI-adjusted USD {cost:,.0f}")
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
