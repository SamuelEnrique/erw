#!/usr/bin/env python3
"""ERCOT's four coincident peaks: the summer months' peak intervals by year, with ERCOT's load in each (session 359).

Energy Research Warehouse (ERW). Table: ercot_4cp_intervals, a series table (docs/methods/ercot_4cp.md, whose shape
section was written before the table).

The source. ERCOT's "Four Coincident Peak Calculations" (Market Information, Data Aggregation,
https://www.ercot.com/mktinfo/data_agg/4cp): the current years as data product NP9-83-M (report type 13037), one
workbook a year posted in late November (the protocols ask for it by 1 December), whose list kept 2022 to 2025 on 20
October 2026; the years before as one zip under the page's Key Documents, "1996-2020 Four Coincident Peak
Calculations". Each workbook names the four intervals in its column headers ("June\\n6/19/2025 17:00") and gives each
load entity's load in them, with a Total row: ERCOT's coincident peak load of the month, MW. The table keeps the
Total row and the interval, 2018 on.

**2021 is not held**: it is on neither the list (which keeps four years) nor the zip (which ends with 2020). It is
not filled. The summer of 2026 is published by 1 December 2026.

The interval. ERCOT prints a time with no word for whether it is the interval's start or end. ERCOT's settlement and
price reports name a 15-minute interval by its end, and this table reads the 4CP time the same way: ts_utc is the
interval's start, 15 minutes before the time ERCOT prints, in Central prevailing time converted to UTC; ERCOT's own
words are kept in x_interval_local.

    python warehouse/connectors/ercot_4cp.py --pull     # the list, then any workbook or the zip not yet held
    python warehouse/connectors/ercot_4cp.py --write    # the table, from the saved files only (data lock)

Terms: "raw data provided in public portions of this website may be used, reproduced, and redistributed in
compilations, charts, and analyses" (https://www.ercot.com/help/terms). License: public.
"""
import argparse
import csv
import datetime as dt
import glob
import hashlib
import io
import json
import os
import re
import sys
import time
import zipfile

import openpyxl
import pandas as pd
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import iso_prices as ip  # noqa: E402

TABLE = "ercot_4cp_intervals"
SOURCE = "ercot:NP9-83-M"
PAGE = "https://www.ercot.com/mktinfo/data_agg/4cp"
PRODUCT = "https://www.ercot.com/mp/data-products/data-product-details?id=NP9-83-M"
LIST = "https://www.ercot.com/misapp/servlets/IceDocListJsonWS?reportTypeId=13037"
FILE = "https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId={doc}"
HISTORY = "https://www.ercot.com/files/docs/2022/01/13/1996-2020_FourCoincidentPeakCalculations.zip"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
PAUSE = 1.5
MAX_REQUESTS = 20
TZ = "America/Chicago"
FIRST_YEAR = 2018
MONTHS = {"june": 6, "july": 7, "august": 8, "september": 9}
RAW = os.path.join(ROOT, "warehouse", "raw", "ercot_4cp")
FILES = os.path.join(RAW, "files")
MANIFEST = os.path.join(FILES, "manifest.csv")
MANIFEST_COLS = ["file", "url", "bytes", "sha256", "retrieved_at", "published"]
COLS = ip.SERIES_COLS + ["x_year", "x_month", "x_interval_local", "x_published", "x_document"]
HEAD = re.compile(r"^\s*(june|july|august|september)\s+(\d{1,2})/(\d{1,2})/(\d{4})\s+(\d{1,2}):(\d{2})\s*$", re.I | re.S)


def manifest():
    if not os.path.exists(MANIFEST):
        return []
    with open(MANIFEST, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def save(name, url, content, published, log):
    os.makedirs(FILES, exist_ok=True)
    with open(os.path.join(FILES, name), "wb") as f:
        f.write(content)
    new = not os.path.exists(MANIFEST)
    with open(MANIFEST, "a", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=MANIFEST_COLS, lineterminator="\n")
        if new:
            w.writeheader()
        w.writerow(dict(file=name, url=url, bytes=len(content), sha256=hashlib.sha256(content).hexdigest(),
                        retrieved_at=dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), published=published))
    log(f"  saved {name}, {len(content):,} bytes")


def pull(log, get=requests.get):
    """The list, then each listed workbook and the historical zip not yet held. At most MAX_REQUESTS requests."""
    if ip.paused("ercot"):
        raise RuntimeError("ERCOT is paused (warehouse/metadata/paused_sources.csv): nothing is requested")
    held = {m["file"] for m in manifest()}
    n = 0
    r = get(LIST, headers=UA, timeout=60)
    n += 1
    r.raise_for_status()
    os.makedirs(RAW, exist_ok=True)
    with open(os.path.join(RAW, "doclist_latest.json"), "w", encoding="utf-8") as f:
        f.write(r.text)
    docs = [x["Document"] for x in r.json()["ListDocsByRptTypeRes"]["DocumentList"]]
    log(f"{LIST}: {len(docs)} workbooks, posted {min(d['PublishDate'] for d in docs)[:10]} to {max(d['PublishDate'] for d in docs)[:10]}")
    todo = [(d["ConstructedName"], FILE.format(doc=d["DocID"]), d["PublishDate"]) for d in docs if d["ConstructedName"] not in held]
    name = os.path.basename(HISTORY)
    if name not in held:
        todo.append((name, HISTORY, ""))
    for name, url, published in todo:
        if n >= MAX_REQUESTS:
            log(f"STOPPED at the ceiling of {MAX_REQUESTS} requests")
            break
        time.sleep(PAUSE)
        g = get(url, headers=UA, timeout=120)
        n += 1
        if g.status_code != 200:
            log(f"  {name}: HTTP {g.status_code}; not saved")
            continue
        save(name, url, g.content, published, log)
    log(f"{n} requests this run")
    return n


def interval(header):
    """(month, local end as printed, the interval's UTC start) of a month's column header; None when it is not one."""
    m = HEAD.match(str(header or "").replace("\n", " "))
    if not m:
        return None
    mon, mm, dd, yy, hh, mi = m.groups()
    end = pd.Timestamp(int(yy), int(mm), int(dd), int(hh), int(mi))
    start = (end - pd.Timedelta(minutes=15)).tz_localize(TZ, ambiguous="raise", nonexistent="raise").tz_convert("UTC")
    return MONTHS[mon.lower()], end.strftime("%Y-%m-%d %H:%M"), start


def read_book(content):
    """The four months of one year's workbook: [(year, month, local end, UTC start, MW)] from its Total row."""
    wb = openpyxl.load_workbook(io.BytesIO(content), read_only=True, data_only=True)
    rows = [r for r in wb.worksheets[0].iter_rows(values_only=True) if any(v is not None for v in r)]
    head = next((r for r in rows if any(interval(v) for v in r)), None)
    # the Total row: "Total" in the entity name's column, its figures under the month headers
    total = [r for r in rows if any(isinstance(v, str) and v.strip().lower() == "total" for v in r[:3])]
    if head is None or len(total) != 1:
        raise ValueError("no month headers, or not one Total row")
    total = total[0]
    out = []
    for k, v in enumerate(head):
        it = interval(v)
        if not it:
            continue
        mw = total[k]
        if not isinstance(mw, (int, float)):
            raise ValueError(f"the Total row has no number under {v!r}")
        out.append((it[2].year, it[0], it[1], it[2], float(mw)))
    if sorted(o[1] for o in out) != [6, 7, 8, 9]:
        raise ValueError(f"months {sorted(o[1] for o in out)}, not June to September")
    return out


def books():
    """Each year's workbook: (year, file name inside, its bytes, the document, ERCOT's publication date or '')."""
    found = {}
    for m in manifest():
        path = os.path.join(FILES, m["file"])
        if not os.path.exists(path):
            continue
        with open(path, "rb") as f:
            content = f.read()
        if m["file"].endswith(".zip"):
            z = zipfile.ZipFile(io.BytesIO(content))
            for n in z.namelist():
                hit = re.search(r"/(\d{4})/ERCOTFourCoincidentPeakLoadCalculation\d{4}\.xlsx$", n)
                if hit and int(hit.group(1)) >= FIRST_YEAR:
                    found[int(hit.group(1))] = (n, z.read(n), m["url"], "")
        else:
            hit = re.search(r"4CP(\d{4})\d{4}\.xlsx$", m["file"])
            if hit:
                year = int(hit.group(1))
                pub = m["published"][:10]
                if year not in found or pub > found[year][3]:
                    found[year] = (m["file"], content, m["url"], pub)
    return found


def write(log, run_id):
    retrieved = {m["file"]: m["retrieved_at"] for m in manifest()}
    rows, years = [], []
    for year, (name, content, url, pub) in sorted(books().items()):
        for y, month, local, start, mw in read_book(content):
            if start.year != year:
                raise ValueError(f"{name}: an interval of {start.year} in the workbook of {year}")
            rows.append(dict(entity="ercot:system", variable="cp4_load_mw", ts_utc=start.strftime("%Y-%m-%dT%H:%M:%SZ"), value=round(mw, 6), unit="MW",
                             freq="PT15M", geo="US-TX", market="ercot_4cp", node="ERCOT", source=SOURCE, source_url=url,
                             retrieved_at=retrieved.get(os.path.basename(name) if not url.endswith(".zip") else os.path.basename(HISTORY), ""),
                             vintage=f"{pub}T00:00:00Z" if pub else "", x_year=str(year), x_month=f"{year}-{month:02d}", x_interval_local=local,
                             x_published=pub, x_document=os.path.basename(name)))
        years.append(year)
    if not rows:
        raise RuntimeError("no workbook read")
    s = pd.DataFrame(rows, columns=COLS).sort_values("ts_utc")
    missing = [y for y in range(FIRST_YEAR, max(years) + 1) if y not in years]
    header = [
        "Energy Research Warehouse (ERW): ERCOT's four coincident peaks, the summer months' peak intervals and ERCOT's load in them, by year (session 359)",
        "Shape: series (docs/datastandard.md v0). entity ercot:system; variable cp4_load_mw, MW: the Total row of ERCOT's Four Coincident Peak Load Calculation (the sum "
        "of the load entities' load in the month's coincident-peak interval; DC tie exports, block load transfer exports and wholesale storage load excluded, as ERCOT's "
        "note says); ts_utc the interval's start, freq PT15M; x_interval_local the time ERCOT prints, read as the interval's end in Central prevailing time; x_month the "
        "month; x_published ERCOT's posting date of the workbook (empty for the years of the 1996-2020 zip, which states none); x_document the workbook.",
        f"Years held: {', '.join(map(str, years))}. Not held: {', '.join(map(str, missing)) or 'none'} (2021 is on neither ERCOT's list, which keeps four years, nor the "
        "zip, which ends with 2020). The summer of 2026 is published by 1 December 2026.",
        "An interval is known only after its month: ERCOT names it from settlement data, and publishes the year's calculation in November.",
        f"Retrieved: {run_id} (UTC) by warehouse/connectors/ercot_4cp.py",
        f"Run log: warehouse/raw/ercot_4cp/run_{run_id}.log",
        f"Source: {SOURCE} ERCOT, Four Coincident Peak Calculations (report type 13037; prior years: the page's Key Documents), {PAGE}",
        "License: public. ERCOT's terms of use (https://www.ercot.com/help/terms): raw data in public portions of the website may be used, reproduced and redistributed "
        "in compilations, charts and analyses.",
    ]
    path = os.path.join(ip.OUT_DIR, TABLE + ".csv")
    if os.path.exists(path):
        os.remove(path)  # rebuilt whole from the saved files
    ip.write_csv(s, TABLE, header, log, cols=COLS)
    ip.update_sources([dict(source=SOURCE, publisher="Electric Reliability Council of Texas (ERCOT)",
                            report="Four Coincident Peak Calculations (NP9-83-M; the years before 2021 from the page's 1996-2020 zip)",
                            report_url=PAGE, document_list=LIST, license="public", tables=[TABLE])])
    log(f"{TABLE}: {len(s)} rows, years {years}; not held {missing}")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERCOT's four coincident peaks (session 359)")
    ap.add_argument("--pull", action="store_true")
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args(argv)
    os.makedirs(RAW, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    logf = open(os.path.join(RAW, f"run_{run_id}.log"), "a", encoding="utf-8")

    def log(m):
        print(m, flush=True)
        logf.write(m + "\n")
        logf.flush()
    try:
        if a.pull:
            pull(log)
        if a.write:
            return write(log, run_id)
        if not a.pull:
            ap.error("--pull or --write")
        return 0
    finally:
        logf.close()


if __name__ == "__main__":
    sys.exit(main())
