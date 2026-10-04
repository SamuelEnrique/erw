#!/usr/bin/env python3
"""The loop shared by the day-ahead reserve price connectors of session 85.

Energy Research Warehouse (ERW). Four connectors need the same code (nyiso_as_prices, isone_as_prices,
miso_as_prices, spp_as_prices), so it lives here once: the arguments, the documents to fetch, the complete-day rule,
the ceiling, the write, the source registry and the run status. What differs stays in each connector: where the
report is, how its file is read, which regions and products are kept, and the license with its terms quoted.
caiso_as_prices.py (session 65) is the pattern and is left as it is.

A connector hands run() a spec:

    name, connector   the table and the raw-file directory
    label             the grid, for messages ("NYISO")
    tz                the time zone of the operating day (a fixed offset for a report that does not change clocks)
    first             the first operating day the report holds (not before START)
    geo, market       the columns of every row
    source, report, page, document_list, publisher, license
    documents(start, until, log, offline)   the documents to read: dicts with at least "url" and "days" (the
                                            operating days it holds), and "settled" (False: fetch it again)
    fetch(doc, log, offline)                optional: (bytes, record); default is iso_prices.fetch_raw
    parse(raw, doc, log)                    rows: region, variable, ts (UTC, start of the hour), value, day
    regions, variables                      what a complete day must hold: {region: [variables]}
    header(regions, days, gaps)             the lines of the file header that are the connector's own
    narrow(rows, log)                       optional: called when the rows pass the ceiling; returns fewer rows

Never fill: a (region, variable, operating day) is written only when every hour of that day is there exactly once
(24, or 23 and 25 at the clock changes); a day short of that is left out, logged and reported as a gap. A document
the source does not hold (HTTP 404) is a gap. Ceiling: 500,000 rows a grid (session 85); past it nothing is written.
"""

import argparse
import datetime as dt
import os
import sys
import time
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

START = "2024-09-01"
CEILING = 500_000
UNIT = "USD/MW-hour"


def hours_in(day, tz):
    a = pd.Timestamp(day).tz_localize(tz)
    return int(((a + pd.DateOffset(days=1)) - a) / pd.Timedelta(hours=1))


def day_hours(day, tz):
    """The UTC starts of the hours of one operating day, in order."""
    a = pd.Timestamp(day).tz_localize(tz).tz_convert("UTC")
    return [a + pd.Timedelta(hours=k) for k in range(hours_in(day, tz))]


def complete(rows, wanted, tz, log):
    """Keep the (region, variable, day) series that hold every hour of the day exactly once; name the others.
    wanted: {region: [variables]}. A day in `rows` is judged whole: a region or variable absent from it is a gap."""
    if rows.duplicated(["region", "variable", "ts"]).any():
        d = rows[rows.duplicated(["region", "variable", "ts"], keep=False)].iloc[0]
        raise RuntimeError(f"rows repeat a (region, variable, hour): {d['region']} {d['variable']} {d['ts']}")
    keep, gaps = [], []
    for day, g in rows.groupby("day", sort=True):
        hours = set(day_hours(day, tz))
        for region, variables in wanted.items():
            for v in variables:
                s = g[(g["region"] == region) & (g["variable"] == v)]
                if len(s) == len(hours) and set(s["ts"]) == hours:
                    keep.append(s)
                elif len(s) or region in set(g["region"]):
                    gaps.append(f"{region} {v} {day}: {len(s)} of {len(hours)} hours")
    for x in gaps:
        log(f"  gap, left out: {x}")
    return (pd.concat(keep, ignore_index=True) if keep else rows.iloc[0:0]), gaps


def fetch(spec, doc, log, offline):
    if "fetch" in spec:
        return spec["fetch"](doc, log, offline)
    return ip.fetch_raw(spec["connector"], doc["url"], log, offline=offline, fresh=not doc.get("settled", True),
                        pause=0)


def run(spec, argv=None):
    name, connector = spec["name"], spec["connector"]
    ap = argparse.ArgumentParser(description=f"ERW: {spec['label']} day-ahead reserve prices")
    ap.add_argument("--out-dir", help="write the table, log, registry and status under this directory instead of "
                    "the repository (raw files stay in warehouse/raw)")
    ap.add_argument("--offline", action="store_true", help="read the raw files only; make no request")
    ap.add_argument("--start", default=max(START, spec["first"]))
    ap.add_argument("--until", help="first operating day not pulled (default: tomorrow, the grid's time)")
    a = ap.parse_args(argv)
    if a.start < START:
        ap.error(f"the approved window starts {START}")
    raw_dir = ip.RAW_DIR
    if a.out_dir:
        ip.set_out_dir(a.out_dir)
        ip.RAW_DIR = raw_dir  # source documents are kept once, in warehouse/raw, whatever the output directory
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{connector}_{run_id}.log"))
    ip.RAW.open(connector, run_id)
    results = []
    try:
        tz = spec["tz"]
        until = (pd.Timestamp(a.until) if a.until
                 else pd.Timestamp.now(tz=tz).tz_localize(None).normalize() + pd.Timedelta(days=1))
        start = pd.Timestamp(max(a.start, spec["first"]))
        docs = spec["documents"](start, until, log, a.offline)
        log(f"ERW {connector} run {run_id}: operating days {start.date()} to {(until - pd.Timedelta(days=1)).date()}, "
            f"{len(docs)} documents; ceiling {CEILING:,} rows")
        frames, gaps, t0 = [], [], time.time()
        for i, doc in enumerate(docs):
            try:
                raw, rec = fetch(spec, doc, log, a.offline)
            except ip.SourceGap as exc:
                gaps.append(f"{doc['label']}: not at the source")
                log(f"  gap: {exc}")
                continue
            rows = spec["parse"](raw, doc, log)
            rows = rows[(rows["day"] >= str(start.date())) & (rows["day"] < str(until.date()))]
            rows, g = complete(rows, spec["wanted"], tz, log)
            gaps += g
            rows = rows.assign(source_url=rec["url"], retrieved_at=rec["retrieved_at"])
            frames.append(rows)
            if not rec.get("cached") and spec.get("pause"):
                time.sleep(spec["pause"])
            if i % 50 == 0:
                print(f"{connector}: {doc['label']} ({i + 1} of {len(docs)}), {time.time() - t0:.0f} s", flush=True)
        rows = pd.concat(frames, ignore_index=True) if frames else None
        if rows is None or rows.empty:
            raise RuntimeError("no complete day was read; nothing written")
        if len(rows) > CEILING and "narrow" in spec:
            rows = spec["narrow"](rows, log)
        if len(rows) > CEILING:
            raise RuntimeError(f"{len(rows):,} rows would pass the ceiling of {CEILING:,}; nothing written")
        if rows.duplicated(["region", "variable", "ts"]).any():
            raise RuntimeError("two documents hold the same (region, variable, hour)")
        s = pd.DataFrame({
            "entity": spec["namespace"] + ":" + rows["region"], "variable": rows["variable"],
            "ts_utc": rows["ts"].map(ip.utc_iso), "value": rows["value"], "unit": UNIT, "freq": "PT1H",
            "geo": spec["geo"], "market": spec["market"], "node": rows["region"], "source": spec["source"],
            "source_url": rows["source_url"], "retrieved_at": rows["retrieved_at"], "vintage": "",
        }).sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)[ip.SERIES_COLS]
        days = sorted(set(rows["day"]))
        header = spec["header"](sorted(set(rows["region"])), days, gaps) + [
            f"Window: operating days {days[0]} to {days[-1]} ({tz}). Never filled: a (region, product, day) is "
            f"written only when every hour of the day is there; {len(gaps)} are left out of this run"
            + (": " + "; ".join(gaps[:20]) if gaps else "") + ".",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/{connector}.py",
            f"Run log: warehouse/output/logs/{connector}_{run_id}.log",
            f"Raw files: warehouse/raw/{connector}/ (not in git; each run's manifest.csv lists each file and URL)",
            f"Source: {spec['source']} {spec['label']}, {spec['report']}, {spec['page']}",
            spec["license_line"],
            "Method: docs/methods/capacity_and_ancillary.md",
        ]
        ip.write_csv(s, name, header, log)
        ip.update_sources([dict(source=spec["source"], publisher=spec["publisher"], report=spec["report"],
                                report_url=spec["page"], document_list=spec["document_list"],
                                license=spec["license"], tables=[name])])
        results.append(dict(table=name, market="DAM", status="ok", detail=f"{len(s)} rows of {CEILING}"))
        for g in gaps:
            results.append(dict(table=name, market="DAM", status="gap", detail=g))
    except Exception:
        tb = ip.redact(traceback.format_exc())
        last = tb.strip().splitlines()[-1]
        log(f"{name} FAILED, no output file written:\n{tb}")
        print(f"{connector} {name} FAILED, no output file written: {last}", file=sys.stderr)
        results.append(dict(table=name, market="DAM", status="failed", detail=last[:300]))
    ip.write_status(connector, run_id, results)
    failures = sum(r["status"] == "failed" for r in results)
    log(f"done, failures={failures}")
    log.close()
    print(f"{connector} run log: {os.path.relpath(log.path, ip.ROOT)}")
    return 1 if failures else 0
