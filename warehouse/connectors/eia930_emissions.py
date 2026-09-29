#!/usr/bin/env python3
"""Hourly CO2 emissions estimates of EIA-930, from EIA's per-balancing-authority workbooks (session 32).

Energy Research Warehouse (ERW) connector. EIA publishes its hourly CO2 estimates for EIA-930 only in the
per-balancing-authority Excel workbooks of the Hourly Electric Grid Monitor (not in the API v2 and not in the six-month
bulk files: session 31), at

    https://www.eia.gov/electricity/gridmonitor/knownissues/xls/<BA>.xlsx     (CISO, ERCO, ISNE, MISO, NYIS, PJM, SWPP)
    https://www.eia.gov/electricity/gridmonitor/knownissues/xls/Region_US48.xlsx

Each workbook's sheet "Published Hourly Data" has one row per hour from 2015-07-01 (UTC time = the hour's END) and the
CO2 columns from 2018-07-01: by fuel (COL, NG, OIL, Other), Generated, Imported, Exported and Consumed, in metric tons,
with EIA's emission factors (lbs/kWh) and intensities. Its "Notes" sheet defines each column.

This connector writes one series table, warehouse/output/eia930_all_emissions.csv, partition column ba:

    co2_emissions_generated   EIA's "CO2 Emissions Generated": CO2 from all sources generated in the BA, tCO2
    co2_emissions_consumed    EIA's "CO2 Emissions Consumed": generated plus imported minus exported, tCO2

Only these two variables: the session's ceiling (1.2 million new rows) holds two over the eight BAs' 72,000-odd hours
since 2018-07-01, not three. The by-fuel, imported and exported columns stay in the saved raw workbooks, so a later
session can add them without a new pull.

Time: ts_utc = EIA's UTC time minus one hour (the hour's start), as eia930.py. Values as EIA writes them (floats, not
rounded). Completeness per UTC day (session 16): a day is written only when both variables have all 24 hours;
otherwise it is left out and recorded as a gap in run_status.csv.

    python warehouse/connectors/eia930_emissions.py                  # the whole series (session 32)
    python warehouse/connectors/eia930_emissions.py --days 3         # the daily run: the newest workbooks, last 3 days

Raw files and resume: every workbook is downloaded through requests into warehouse/raw/eia930_emissions/<run_id>/ with
a manifest (URL, Last-Modified, sha256). Before a download, the connector asks for the workbook's Last-Modified (HEAD)
and reuses a saved copy with the same Last-Modified from any earlier run, so an interrupted pull resumes from the files
already saved and never downloads one twice. Workbooks are read with openpyxl in read-only (streaming) mode, one at a
time, keeping three columns; the table is written and merged in a stream, never held whole.
"""

import argparse
import csv
import datetime as dt
import glob
import os
import sys
import traceback

import pandas as pd
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import eia930  # noqa: E402  (BAS: respondent codes and geo)
import iso_prices as ip  # noqa: E402

NAME = "eia930_all_emissions"
BASE = "https://www.eia.gov/electricity/gridmonitor/knownissues/xls/"
FILE = {"ciso": "CISO", "erco": "ERCO", "isne": "ISNE", "miso": "MISO", "nyis": "NYIS", "pjm": "PJM", "swpp": "SWPP",
        "us48": "Region_US48"}
SHEET = "Published Hourly Data"
COLUMNS = {"CO2 Emissions Generated": "co2_emissions_generated", "CO2 Emissions Consumed": "co2_emissions_consumed"}
SOURCE = "eia:gridmonitor/knownissues/xls"
REPORT = ("Form EIA-930, Hourly Electric Grid Monitor: per-balancing-authority workbooks, sheet Published Hourly Data "
          "(estimated CO2 emissions)")
PAGE = "https://www.eia.gov/electricity/gridmonitor/about"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-eia930-emissions/0.1; +https://github.com/SamuelEnrique/erw)"}
COLS = ip.SERIES_COLS + ["ba"]
KEY = ["entity", "variable", "ts_utc"]


def saved_copy(url, last_modified):
    """A workbook saved by an earlier run with the same Last-Modified, or None."""
    for man in sorted(glob.glob(os.path.join(ip.RAW_DIR, "eia930_emissions", "*", "manifest.csv")), reverse=True):
        with open(man, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                # the HEAD request is captured too, as a 0-byte 200: only a whole xlsx counts as a saved copy
                if r["url"] == url and r["last_modified"] == last_modified and r["status"] == "200" \
                        and int(r["bytes"]) > 0:
                    path = os.path.join(os.path.dirname(man), r["file"])
                    if os.path.exists(path) and os.path.getsize(path) == int(r["bytes"]):
                        with open(path, "rb") as f:
                            if f.read(2) == b"PK":
                                return path
    return None


def workbook(code, log):
    """(path, url, last_modified) of the newest workbook of a BA, downloaded unless a saved copy is current."""
    url = BASE + FILE[code] + ".xlsx"
    head = ip.with_retries(f"HEAD {url}", lambda: requests.head(url, headers=UA, timeout=60), log)
    lm = head.headers.get("Last-Modified", "")
    path = saved_copy(url, lm) if lm else None
    if path:
        log(f"  {code}: saved copy of {url} (Last-Modified {lm}): {os.path.relpath(path, ip.ROOT)}")
        return path, url, lm

    def get():
        r = requests.get(url, headers=UA, timeout=900)
        if r.status_code != 200 or not r.content.startswith(b"PK"):
            raise RuntimeError(f"{url}: HTTP {r.status_code}, {len(r.content)} bytes, not an xlsx")
        return r
    with ip.RAW.collect() as recs:
        r = ip.with_retries(f"GET {url}", get, log)
    rec = [x for x in recs if x["url"] == url and str(x["status"]) == "200"][-1]
    path = os.path.join(ip.RAW.dir, rec["file"])
    log(f"  {code}: downloaded {url}, {len(r.content):,} bytes, Last-Modified {r.headers.get('Last-Modified')}")
    return path, url, r.headers.get("Last-Modified", "")


def read_hours(path, code, start, end, log):
    """[(interval_start, {variable: value})] of the workbook's hours in [start, end), streamed."""
    import openpyxl
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    if SHEET not in wb.sheetnames:
        raise RuntimeError(f"{path}: no sheet {SHEET!r} (sheets {wb.sheetnames})")
    ws = wb[SHEET]
    rows = ws.iter_rows(values_only=True)
    hdr = list(next(rows))
    # the BA workbooks name the first column "BA", the region workbook (US48) "Region"
    who = "BA" if "BA" in hdr else "Region"
    missing = [c for c in [who, "UTC time", *COLUMNS] if c not in hdr]
    if missing:
        raise RuntimeError(f"{path}: columns {missing} not in {SHEET}; EIA changed the layout")
    ir, it = hdr.index(who), hdr.index("UTC time")
    iv = {v: hdr.index(c) for c, v in COLUMNS.items()}
    want = eia930.BAS[code][0]
    out, other = [], 0
    for row in rows:
        if row[it] is None:
            continue
        if row[ir] != want:
            other += 1
            continue
        ts = pd.Timestamp(row[it], tz="UTC") - pd.Timedelta(hours=1)  # EIA's UTC time is the hour's end
        if ts < start or ts >= end:
            continue
        vals = {v: row[i] for v, i in iv.items() if isinstance(row[i], (int, float))}
        if vals:
            out.append((ts, vals))
    wb.close()
    if other:
        raise RuntimeError(f"{path}: {other} rows name a region other than {want}")
    log(f"  {code}: {len(out):,} hours with a CO2 value in the window")
    return out


def complete_rows(code, hours, url, retrieved, gaps, start, end):
    """Rows of the complete UTC days (both variables, 24 hours); the other days become gap records."""
    respondent, geo = eia930.BAS[code]
    entity = f"eia930:{respondent}"
    by_day = {}
    for ts, vals in hours:
        by_day.setdefault(ts.floor("D"), []).append((ts, vals))
    rows = []
    first = min(by_day) if by_day else None
    for day, hs in sorted(by_day.items()):
        full = len({t for t, v in hs if len(v) == len(COLUMNS)}) == 24 and len(hs) == 24
        if not full:
            if day != first or len(hs) == 24:  # the partial first day of a window is not a gap of the source
                gaps.append(dict(table=NAME, market=f"{code} {day:%Y-%m-%d}", status="gap",
                                 detail=f"{len(hs)} of 24 hours with CO2 values; day not written"))
            continue
        for ts, vals in hs:
            t = ts.strftime("%Y-%m-%dT%H:%M:%SZ")
            for var, v in vals.items():  # a tuple in COLS order: a million rows as dicts would not fit in memory
                rows.append((entity, var, t, repr(float(v)), "tCO2", "PT1H", geo, "", "", SOURCE, url, retrieved, "",
                             code))
    return rows


def merge_write(new, header, log):
    """Stream the existing table, drop the rows the new ones replace, append the new, write through a temporary
    file: the table (hundreds of MB) is never held whole. Returns (kept, replaced, added)."""
    path = os.path.join(ip.OUT_DIR, NAME + ".csv")
    tmp = path + ".tmp"
    newkeys = {r[:3] for r in new}
    kept = replaced = 0
    with open(tmp, "w", encoding="utf-8", newline="") as out:
        for h in header:
            out.write("# " + h + "\n")
        w = csv.writer(out, lineterminator="\n")
        w.writerow(COLS)
        if os.path.exists(path):
            with open(path, encoding="utf-8", newline="") as f:
                rd = csv.reader(ln for ln in f if not ln.startswith("#"))
                if next(rd) != COLS:
                    raise RuntimeError(f"{path}: columns are not {COLS}; not merging into a file of another shape")
                for r in rd:
                    if tuple(r[:3]) in newkeys:
                        replaced += 1
                        continue
                    w.writerow(r)
                    kept += 1
        new.sort(key=lambda r: r[:3])
        w.writerows(new)
    os.replace(tmp, path)
    return kept, replaced, len(new) - replaced


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW EIA-930 CO2 emissions connector (session 32)")
    ap.add_argument("--days", type=int, help="keep only the last N complete UTC days (the daily run)")
    ap.add_argument("--ba", action="append", choices=sorted(FILE))
    ap.add_argument("--out-dir")
    args = ap.parse_args(argv)
    if args.out_dir:
        ip.set_out_dir(args.out_dir)
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"eia930_emissions_{run_id}.log"))
    ip.RAW.open("eia930_emissions", run_id)
    end = pd.Timestamp.now(tz="UTC").normalize()
    start = end - pd.Timedelta(days=args.days) if args.days else pd.Timestamp("2018-07-01", tz="UTC")
    codes = args.ba or list(FILE)
    results, gaps, new, used = [], [], [], []
    log(f"ERW eia930_emissions run {run_id}; window [{ip.utc_iso(start)}, {ip.utc_iso(end)}); BAs {codes}")
    try:
        retrieved = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
        for code in codes:
            path, url, lm = workbook(code, log)
            used.append(f"{code}: {url} (Last-Modified {lm})")
            hours = read_hours(path, code, start, end, log)
            rows = complete_rows(code, hours, url, retrieved, gaps, start, end)
            log(f"  {code}: {len(rows):,} rows in complete UTC days; first {rows[0][2] if rows else None}")
            new += rows
            del hours
        if not new:
            raise RuntimeError("no complete day of CO2 values in the window")
        header = [
            "Energy Research Warehouse (ERW): EIA-930 hourly CO2 emissions estimates by balancing authority",
            "Shape: series (docs/datastandard.md v0), partition column ba. tCO2 = metric tons of CO2, as EIA states "
            "them. co2_emissions_generated: EIA's CO2 Emissions Generated (all sources in the BA); co2_emissions_consumed: "
            "EIA's CO2 Emissions Consumed (generated plus imported minus exported). ts_utc is the hour's start (EIA's UTC "
            "time, the hour's end, minus one hour).",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia930_emissions.py",
            f"Run log: warehouse/output/logs/eia930_emissions_{run_id}.log",
            f"Raw files: warehouse/raw/eia930_emissions/<run_id>/ (not in git; manifest.csv lists each workbook, its URL, "
            f"Last-Modified and sha256). Workbooks read by this run: " + "; ".join(used),
            f"Source: {SOURCE} {REPORT}, {PAGE}",
            f"  document list: {BASE}",
            "EIA's method: estimated emissions = positive generation by fuel x EIA's CO2 emission factor per fuel and BA "
            "(lbs/kWh; https://www.eia.gov/tools/faqs/faq.php?id=74&t=11); imported and exported CO2 follow the "
            "interchange. See docs/methods/emissions.md.",
            "Completeness per UTC day (session 16): a day is written only when both variables have all 24 hours; each "
            "day left out is a gap row in warehouse/metadata/run_status.csv. Values are EIA's, not rounded.",
        ]
        kept, replaced, added = merge_write(new, header, log)
        summary = (f"{NAME}.csv: this run {len(new):,} rows ({added:,} new, {replaced:,} replacing earlier rows with "
                   f"the same key); {kept:,} rows kept from earlier runs; {len(gaps)} incomplete BA-days left out")
        log(summary)
        print(summary)
        ip.update_sources([{"source": SOURCE, "publisher": "U.S. Energy Information Administration (EIA)",
                            "report": REPORT, "report_url": PAGE, "document_list": BASE, "license": "public",
                            "tables": [NAME]}])
        results.append(dict(table=NAME, market="all", status="ok", detail=summary[:300]))
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED:\n{tb}")
        print(f"eia930_emissions {NAME} FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    ip.write_status("eia930_emissions", run_id, results + gaps)
    log.close()
    return 0 if all(r["status"] != "failed" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
