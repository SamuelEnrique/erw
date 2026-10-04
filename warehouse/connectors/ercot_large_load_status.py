#!/usr/bin/env python3
"""ERCOT's Large Load Interconnection Status Update: the figures its monthly report states in words.

Energy Research Warehouse (ERW) connector, session 106. An approved pull: ceiling 20,000 rows, USD 0.

    python warehouse/connectors/ercot_large_load_status.py                 # ask ERCOT, write the table
    python warehouse/connectors/ercot_large_load_status.py --from-dir DIR  # read documents saved by an earlier run; no request
    python warehouse/connectors/ercot_large_load_status.py --out-dir DIR   # a trial: the table under DIR

What ERCOT publishes. Its Large Load Integration team presents a "Large Load Interconnection Status Update" to the
Technical Advisory Committee (TAC) and the Large Load Working Group (LLWG): a slide deck, posted as a PDF or a
PowerPoint file on the meeting's page, alone or inside a zip. There is no request-level list (session 17: Protocol
3.2.7 has the report aggregate requests, customer data being confidential), and the deck's charts are pictures: the
queue by status ("No Studies Submitted", "Under ERCOT Review", "Planning Studies Approved", "Approved to Energize",
"Observed Energized") is drawn, not written. The ERW does not read a number off a picture. What the deck states in
words, and this connector takes:

  approved_to_energize_mw            "Of the N MW that have received Approval to Energize"
  observed_nonsimultaneous_peak_mw   "a non-simultaneous monthly peak consumption of N MW in <month>": the sum of each
                                     approved load's own highest hour of the month; what ERCOT "believes is now operational"
  observed_simultaneous_peak_mw      "a simultaneous monthly peak consumption of N MW in <month>": the highest hour of
                                     the loads together
  new_submissions_count, _mw         "ERCOT has recently received N new LLI submissions ... approximately M MW", where
                                     a report says so

One row per figure and report, dated the day on the report's first page. A report that does not hold a sentence gives
no row for it; a document whose first page is not a status update is not read further. Nothing is filled.

Where the reports are found: the meeting pages linked from ERCOT's pages for the LLWG and for TAC, this year and last
(the "View Other Years" pages). On each: a document whose name says TAC Report, status update or large load, and any
zip whose name says large load or LLWG, which is opened and searched the same way.

License: public. ERCOT's terms (https://www.ercot.com/help/terms, read 2026-10-04): "The publicly available contents
of this website may be used, reproduced, and redistributed, provided that the contents are not modified and that you
maintain all copyright and other notices contained in the contents, including this Agreement. Notwithstanding the
foregoing, raw data provided in public portions of this website may be used, reproduced, and redistributed in
compilations, charts, and analyses without maintaining such notices."
"""

import argparse
import datetime as dt
import glob
import io
import os
import re
import sys
import time
import traceback
import zipfile

import pandas as pd
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "ercot_large_load_status"
CONNECTOR = "ercot_large_load_status"
SOURCE = "ercot:large_load_status_update"
REPORT = "Large Load Interconnection Status Update (the Large Load Integration team's monthly report to TAC and the LLWG)"
BASE = "https://www.ercot.com"
INDEXES = ["/committees/tac/llwg", "/committees/tac"]            # each has a page per earlier year: <index>/<year>
TERMS = "https://www.ercot.com/help/terms"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
CEILING = 20_000
PAUSE = 1.0
ENTITY = "ercot:large_load"
EXTRA = ["x_month_as_written", "x_document"]
MEETING = re.compile(r'(?:https://www\.ercot\.com)?(/calendar/(\d{2})(\d{2})(\d{4})-(?:Special-)?(?:LLWG|TAC)-Meeting[^"\s]*)"')
DOC = re.compile(r"(?i)TAC[-_ .]*Report|Status[-_ .]*Update|Large[-_ .]*Load[-_ .]*Interconnection|LLI[-_ .]*Status")
ZIP = re.compile(r"(?i)large[-_ .]*load|LLWG|LLI")
MONTHS = {m: i for i, m in enumerate(["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"], 1)}
NUM = r"([\d,]+(?:\.\d+)?)"
FIGURES = [
    ("approved_to_energize_mw", "MW", re.compile(rf"Of the {NUM}\s*MW that have received Approval to Energize", re.I), None),
    ("observed_nonsimultaneous_peak_mw", "MW", re.compile(rf"non-?\s*simultaneous\s+monthly peak consumption of\s+{NUM}\s*MW in (\w+ \d{{4}})", re.I), 2),
    ("observed_simultaneous_peak_mw", "MW", re.compile(rf"observed a\s+simultaneous\s+monthly peak consumption of\s+{NUM}\s*MW in (\w+ \d{{4}})", re.I), 2),
    ("new_submissions_count", "count", re.compile(rf"received {NUM} new LLI submissions", re.I), None),
    ("new_submissions_mw", "MW", re.compile(rf"new LLI submissions\.?\s*Preliminary review indicates these total approximately {NUM}\s*MW", re.I), None),
]


def links(html):
    """(url, text) of every link of a page that ends in a document's extension."""
    out, seen = [], set()
    for m in re.finditer(r'<a\s[^>]*href="([^"]+)"[^>]*>([\s\S]*?)</a>', html, re.I):
        href = m.group(1)
        if not re.search(r"\.(pdf|pptx|zip)(\?|$)", href, re.I) or href in seen:
            continue
        seen.add(href)
        out.append((href if href.startswith("http") else BASE + href, " ".join(re.sub(r"<[^>]+>", " ", m.group(2)).split())))
    return out


def meetings(html, today):
    """(yyyymmdd, url) of the LLWG and TAC meetings a page links, those not after today."""
    out = {}
    for path, mm, dd, yyyy in MEETING.findall(html):
        day = f"{yyyy}{mm}{dd}"
        if day <= today:
            out[day + path] = (day, BASE + path)
    return sorted(out.values())


def pages_of(name, content):
    """The text of a document, a string per page or slide. PDF through pdfplumber; PowerPoint from its own XML."""
    if name.lower().endswith(".pdf"):
        import pdfplumber
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            return [" ".join((p.extract_text() or "").split()) for p in pdf.pages]
    if name.lower().endswith(".pptx"):
        z = zipfile.ZipFile(io.BytesIO(content))
        slides = sorted((n for n in z.namelist() if re.match(r"ppt/slides/slide\d+\.xml$", n)), key=lambda s: int(re.findall(r"\d+", s)[-1]))
        out = []
        for s in slides:
            xml = z.read(s).decode("utf-8", "replace")
            # a paragraph's runs are joined without a space (PowerPoint splits a word across runs), paragraphs with one
            paras = ["".join(re.findall(r"<a:t>([^<]*)</a:t>", p)) for p in re.findall(r"<a:p>[\s\S]*?</a:p>|<a:p [\s\S]*?</a:p>", xml)]
            out.append(" ".join(" ".join(paras).replace("&amp;", "&").split()))
        return out
    return []


def report_date(first):
    """The day on a status update's first page ("March 13, 2026"), or None."""
    m = re.search(r"(" + "|".join(MONTHS) + r")\s+(\d{1,2}),\s*(\d{4})", first)
    if not m:
        return None
    try:
        return dt.date(int(m.group(3)), MONTHS[m.group(1)], int(m.group(2)))
    except ValueError:
        return None


def is_status_update(pages):
    first = pages[0] if pages else ""
    return bool(re.search(r"Large\s+Load\s+Interconnection", first, re.I) and re.search(r"Status\s+Update", first, re.I))


def figures(pages):
    """The figures a status update states in words: [(variable, unit, value, the month as written or "")]. A figure is
    taken once, from the first sentence that matches; a deck that states one twice with two values is an error."""
    text = " ".join(pages)
    out = []
    for variable, unit, pattern, month_group in FIGURES:
        found = [(m.group(1), m.group(month_group) if month_group else "") for m in pattern.finditer(text)]
        values = {v.replace(",", "") for v, _ in found}
        if len(values) > 1:
            raise ValueError(f"{variable} is stated with {len(values)} different values: {sorted(values)}")
        if found:
            out.append((variable, unit, float(found[0][0].replace(",", "")), found[0][1]))
    return out


def rows_of(docs, retrieved):
    """The table's rows from the status updates read: docs is [(url, name, pages)]. Returns (rows, notes)."""
    rows, notes, seen = [], [], {}
    for url, name, pages in docs:
        day = report_date(pages[0])
        if day is None:
            notes.append(f"{name}: a status update with no day on its first page; not written ({url})")
            continue
        got = figures(pages)
        if not got:
            notes.append(f"{name} ({day}): a status update that states none of the figures in words; not written ({url})")
            continue
        for variable, unit, value, month in got:
            key = (variable, day)
            if key in seen:      # the same report posted twice (a meeting page and a zip): one row, the first found
                if seen[key][0] != value:
                    notes.append(f"{name} ({day}): {variable} is {value:g} here and {seen[key][0]:g} in {seen[key][1]}; the first is kept")
                continue
            seen[key] = (value, name)
            rows.append(dict(entity=ENTITY, variable=variable, ts_utc=f"{day}T00:00:00Z", value=value, unit=unit, freq="P1M", geo="US-TX", market="", node="",
                             source=SOURCE, source_url=url, retrieved_at=retrieved, vintage=f"{day}T00:00:00Z", x_month_as_written=month, x_document=name))
    return rows, notes


def fetch(url, log):
    r = ip.with_retries(url, lambda: requests.get(url, headers=UA, timeout=180), log, attempts=3, wait=5)
    time.sleep(PAUSE)
    if r.status_code != 200:
        raise RuntimeError(f"{url}: HTTP {r.status_code}")
    return r


def collect(log, today):
    """Ask ERCOT: every status update on the LLWG's and TAC's meeting pages of this year and last. [(url, name, pages)]."""
    year = int(today[:4])
    found, n_pages, n_docs = [], 0, 0
    for index in INDEXES:
        for page in (index, f"{index}/{year - 1}"):
            html = fetch(BASE + page, log).text
            ms = meetings(html, today)
            log(f"{BASE + page}: {len(ms)} meetings to {today}")
            for day, url in ms:
                n_pages += 1
                for doc_url, text in links(fetch(url, log).text):
                    fname = doc_url.split("/")[-1]
                    if fname.lower().endswith(".zip"):
                        if not ZIP.search(fname + " " + text):
                            continue
                        z = zipfile.ZipFile(io.BytesIO(fetch(doc_url, log).content))
                        n_docs += 1
                        for inner in z.namelist():
                            if DOC.search(inner) and inner.lower().endswith((".pdf", ".pptx")):
                                pages = pages_of(inner, z.read(inner))
                                if is_status_update(pages):
                                    found.append((f"{doc_url}#{inner}", inner.split("/")[-1], pages))
                                    log(f"  {day}: status update {inner} in {fname}")
                    elif DOC.search(fname + " " + text):
                        pages = pages_of(fname, fetch(doc_url, log).content)
                        n_docs += 1
                        if is_status_update(pages):
                            found.append((doc_url, fname, pages))
                            log(f"  {day}: status update {fname}")
    log(f"{n_pages} meeting pages and {n_docs} documents read; {len(found)} status updates")
    return found


def from_dir(d, log):
    """Documents saved by an earlier run: no request is made. The raw store keeps each response as a file and names its
    address in manifest.csv; with a manifest each document keeps the address it came from, without one its file name."""
    saved = []
    manifest = os.path.join(d, "manifest.csv")
    if os.path.exists(manifest):
        m = pd.read_csv(manifest, dtype=str, keep_default_na=False)
        saved = [(os.path.join(d, r["file"]), r["url"]) for r in m.to_dict("records") if r.get("status", "200") == "200"]
    else:
        saved = [(f, os.path.basename(f)) for f in sorted(glob.glob(os.path.join(d, "*")))]
    found = []
    for path, url in saved:
        name = url.split("?")[0].split("/")[-1]
        if not name.lower().endswith((".zip", ".pdf", ".pptx")) or not os.path.exists(path):
            continue
        with open(path, "rb") as fh:
            content = fh.read()
        if name.lower().endswith(".zip"):
            try:
                z = zipfile.ZipFile(io.BytesIO(content))
            except zipfile.BadZipFile:
                continue
            for inner in z.namelist():
                if DOC.search(inner) and inner.lower().endswith((".pdf", ".pptx")):
                    pages = pages_of(inner, z.read(inner))
                    if is_status_update(pages):
                        found.append((f"{url}#{inner}", inner.split("/")[-1], pages))
        else:
            pages = pages_of(name, content)
            if is_status_update(pages):
                found.append((url, name, pages))
    log(f"{d}: {len(found)} status updates among the saved documents")
    return found


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERCOT Large Load Interconnection Status Update: the figures stated in words")
    ap.add_argument("--from-dir", help="read the documents saved in this directory instead of asking ERCOT")
    ap.add_argument("--out-dir", help="a trial run: the table and its log under this directory; nothing in warehouse/output")
    a = ap.parse_args(argv)
    if a.out_dir:
        ip.set_out_dir(a.out_dir)
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    now = dt.datetime.now(dt.timezone.utc)
    run_id = now.strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{CONNECTOR}_{run_id}.log"))
    status = dict(table=NAME, market="large_load", status="ok", detail="")
    gaps = []
    try:
        if ip.paused("ercot"):
            raise ip.SourceGap(ip.pause_line("ercot"))
        if a.from_dir:
            docs = from_dir(a.from_dir, log)
        else:
            ip.RAW.open(CONNECTOR, run_id)
            docs = collect(log, now.strftime("%Y%m%d"))
        if not docs:
            raise ip.SourceGap("no Large Load Interconnection Status Update was found on ERCOT's LLWG and TAC meeting pages; no table written")
        rows, notes = rows_of(docs, ip.utc_iso(pd.Timestamp(now)))
        for n in notes:
            log("  " + n)
            gaps.append(n)
        if not rows:
            raise ip.SourceGap(f"{len(docs)} status updates were read and none states a figure in words; no table written")
        if len(rows) > CEILING:
            raise RuntimeError(f"{len(rows)} rows would pass the pull's ceiling of {CEILING}; nothing written")
        t = pd.DataFrame(rows).sort_values(["variable", "ts_utc"]).reset_index(drop=True)
        reports = sorted({v[:10] for v in t["vintage"]})
        ip.write_csv(t, NAME, [
            "Energy Research Warehouse (ERW): ERCOT's Large Load Interconnection Status Update, the figures each report states in words (session 106)",
            "Shape: series (docs/datastandard.md v0). One row per figure and report; ts_utc is the day on the report's first page. Variables: "
            "approved_to_energize_mw (MW that have received ERCOT's Approval to Energize), observed_nonsimultaneous_peak_mw (the sum of each approved "
            "load's own highest hour in the month: what ERCOT believes is operational), observed_simultaneous_peak_mw (the highest hour of the loads "
            "together), new_submissions_count and new_submissions_mw (where a report gives them). x_month_as_written: the month the sentence names, as "
            "ERCOT wrote it. x_document: the file.",
            "NOT in this table: the queue by status (no studies submitted, under review, planning studies approved). ERCOT publishes it as a picture of a "
            "chart, and the ERW does not read a number off a picture. A request is not a built facility.",
            f"An approved pull (session 106): ceiling {CEILING:,} rows. {len(reports)} reports, {reports[0]} to {reports[-1]}.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/{CONNECTOR}.py" + (f"; documents read from {a.from_dir}, saved by an earlier run" if a.from_dir else ""),
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Source: {SOURCE} ERCOT, {REPORT}; found on the meeting pages of {BASE}{INDEXES[0]} and {BASE}{INDEXES[1]}",
            "License: public. ERCOT's terms (https://www.ercot.com/help/terms): \"raw data provided in public portions of this website may be used, "
            "reproduced, and redistributed in compilations, charts, and analyses without maintaining such notices.\"",
        ], log, cols=ip.SERIES_COLS + EXTRA)
        ip.update_sources([dict(source=SOURCE, publisher=ip.ISO_PUBLISHERS["ercot"], report=REPORT, report_url=BASE + INDEXES[0],
                                document_list=BASE + INDEXES[0], license="public", tables=[NAME])])
        status["detail"] = f"{len(t)} rows of {CEILING} from {len(reports)} reports, {reports[0]} to {reports[-1]}"
    except Exception:
        tb = ip.redact(traceback.format_exc())
        last = tb.strip().splitlines()[-1]
        log(f"FAILED, no output file written:\n{tb}")
        print(f"{CONNECTOR} {NAME} FAILED, no output file written: {last}", file=sys.stderr)
        status.update(status="failed", detail=last[:300])
    results = [status] + [dict(table=NAME, market="large_load", status="gap", detail=g[:300]) for g in gaps]
    ip.write_status(CONNECTOR, run_id, results)
    log.close()
    print(f"{CONNECTOR}: {status['status']}: {status['detail']}; run log {os.path.relpath(log.path, ip.ROOT)}")
    return 1 if status["status"] == "failed" else 0


if __name__ == "__main__":
    sys.exit(main())
