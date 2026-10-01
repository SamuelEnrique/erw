#!/usr/bin/env python3
"""CAISO grid emergencies: every Flex Alert, Restricted Maintenance Operations notice, Energy Emergency Alert, stage
emergency and transmission emergency the California ISO lists, 1998 to the present (session 58).

Energy Research Warehouse (ERW) connector. Reads one public document, CAISO's "Grid Emergencies History Report" (1998
to present, https://www.caiso.com/documents/grid-emergencies-history-report-1998-to-present.pdf, revised by CAISO
operations; 191 pages on 2026-10-01) and writes one events table:

    warehouse/output/caiso_grid_emergencies.csv

One row per notice and day: a notice that covers several days is one row per local day it covers, because CAISO's own
yearly counts are "the total number of days that the event lasted"; event_id is the notice's key and the day. The
report has four layouts, each read from its tables (pdfplumber, the table cells as CAISO drew them):
    records    2016 to the present: one notice per row (date, region, time frame, event, reason; notice number and issue
               time where the page gives them)
    matrix     2005 to 2015: one row per day, one column per notice type, the hours in the cell
    stages     1998 to 2004: one row per emergency day, the stage columns and (2004) the transmission column
    day lists  1998 to 2001: the days of No Touch, Alert, Warning and Power Watch notices, by year
The yearly day counts per type are checked against the report's own summary tables (pages 1 and 3) and every
difference is logged and written to the header: the table states what it could not reconcile, nothing is adjusted.

event_type: CAISO's notice type, lower case: flex_alert (and its earlier name Power Watch, 1998 to 2006, which CAISO's
summary counts as Flex Alerts), rmo (Restricted Maintenance Operations, and its earlier name No Touch, which the summary
counts as RMO), transmission_emergency, eea_watch, eea1, eea2, eea3 (Energy Emergency Alerts, May 2022 on), alert,
warning, stage1, stage2, stage3 (the notices before May 2022), vlrp (Voluntary Load Reduction Program),
load_interruption (1-Hour Probable Load Interruptions); x_label keeps the name as printed. event_date: the local
(Pacific) day the notice covered.

License: public. CAISO's Privacy and Terms of Use: its materials "were generated, compiled or assembled from materials
and information that are freely available for public use consistent with the general policies of the Public Records
Act ... and may be used by you provided that you keep intact all copyright, trademark and other proprietary notices and
that you credit the California ISO". Every page and the table credit "California ISO, Grid Emergencies History Report".

    python warehouse/connectors/caiso_emergencies.py
"""

import datetime as dt
import hashlib
import os
import re
import sys
import traceback

import pandas as pd
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import iso_prices as ip  # noqa: E402

NAME = "caiso_grid_emergencies"
URL = "https://www.caiso.com/documents/grid-emergencies-history-report-1998-to-present.pdf"
TERMS = "https://www.caiso.com/privacy-terms-of-use"
SOURCE = "caiso:grid_emergencies_history"
CEILING = 20_000

TYPES = {
    "flex alert": "flex_alert", "restricted maintenance operations": "rmo", "rmo": "rmo", "rmo*": "rmo", "generation rmo": "rmo",
    "no touch": "rmo", "power watch": "flex_alert", "transmission emergency": "transmission_emergency", "trans.": "transmission_emergency", "eea watch": "eea_watch",
    "eea1": "eea1", "eea 1": "eea1", "eea2": "eea2", "eea 2": "eea2", "eea3": "eea3", "eea 3": "eea3", "alert": "alert", "warning": "warning",
    "stage 1": "stage1", "stage 2": "stage2", "stage 3": "stage3", "vlrp": "vlrp",
    "1-hour notification": "load_interruption", "1-hour probable load interruptions": "load_interruption",
}
# CAISO's summary columns (pages 1 and 3) and the event types they count
SUMMARY = {"Flex Alert": ["flex_alert"], "Restricted Maintenance Operations": ["rmo"], "Transmission Emergency": ["transmission_emergency"],
           "EEA Watch": ["eea_watch"], "EEA1": ["eea1"], "EEA2": ["eea2"], "EEA3": ["eea3"], "Alert": ["alert"], "Warning": ["warning"],
           "Stage 1 Emergency": ["stage1"], "Stage 2 Emergency": ["stage2"], "Stage 3 Emergency": ["stage3"],
           "1-Hour Probable Load Interruptions": ["load_interruption"], "Voluntary Load Reduction Program": ["vlrp"]}


def cell(x):
    return re.sub(r"\s+", " ", (x or "").replace("\n", " ")).strip()


def kind(label):
    k = TYPES.get(cell(label).lower())
    return k


def parse_date(s, year=None):
    """M/D/YYYY, MM/DD/YY, or D-Mon (with the year given)."""
    s = cell(s).replace("*", "")
    for fmt in ("%m/%d/%Y", "%m/%d/%y"):
        try:
            return dt.datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    m = re.fullmatch(r"(\d{1,2})-([A-Za-z]{3})", s)
    if m and year:
        return dt.datetime.strptime(f"{m.group(1)}-{m.group(2)}-{year}", "%d-%b-%Y").date()
    return None


def span(time_frame, day):
    """The local days a record's time frame covers: 'MM/DD/YYYY HH:MM through MM/DD/YYYY HH:MM' gives every day from
    the first to the last; a frame of hours alone ('10:00 - 21:00') is the record's own day."""
    ds = re.findall(r"(\d{1,2}/\d{1,2}/\d{4})\s+(\d{1,2}:\d{2})", time_frame)
    if len(ds) >= 2:
        a, b = parse_date(ds[0][0]), parse_date(ds[-1][0])
        if a and b and a <= b and (b - a).days < 60:
            return [a + dt.timedelta(days=k) for k in range((b - a).days + 1)], f"{a} {ds[0][1]}", f"{b} {ds[-1][1]}"
    m = re.search(r"(\d{1,2}:?\d{2})\s*-\s*(\d{1,2}:?\d{2})", time_frame)
    if m:
        return [day], f"{day} {m.group(1)}", f"{day} {m.group(2)}"
    return [day], "", ""


def records(pdf, log):
    """Every row of the four layouts, as dicts: day, type, region, frame, notice, issued, reason, layout, page."""
    out, last_head = [], {}
    for pno, page in enumerate(pdf.pages, start=1):
        text = page.extract_text() or ""
        year_m = re.search(r"(?:Record For|Emergencies [Ff]or|Days for) (\d{4})", text)
        page_year = int(year_m.group(1)) if year_m else None
        notice = re.search(r"Notice No:\s*([\w-]+)|\[(\d{8,})\]", text)
        notice = (notice.group(1) or notice.group(2)) if notice else ""
        issued = re.search(r"Notice issued at:\s*\[?([\d/]+\s+[\d:]+)", text)
        issued = issued.group(1) if issued else ""
        words = page.extract_words()
        for tbl in page.find_tables():
            t = tbl.extract()
            if not t or not t[0]:
                continue
            head = [cell(c) for c in t[0]]
            body = t[1:]
            if head[0] and parse_date(head[0].split()[-1]) and len(head) in last_head:
                head, body = last_head[len(head)], t  # a continuation table whose first row is data
            elif head[0].startswith("Date") or head[0] in ("", "1998", "1998*", "No Touch", "RMO*"):
                last_head[len(head)] = head
            else:
                continue
            low = [h.lower() for h in head]
            if "awe event" in low:  # records
                k, r_reg, r_tf = low.index("awe event"), low.index("region"), low.index("time frame")
                r_reason = next((i for i, h in enumerate(low) if h.startswith("reason")), None)
                for r in body:
                    listed = expand(cell(r[0]))
                    typ = kind(r[k])
                    if not listed or not typ:
                        continue
                    day = listed[0]
                    tf = cell(r[r_tf])
                    days, a, b = span(tf, day)
                    if len(listed) > 1:
                        days = listed  # a row naming a range of days: those days
                    reason = cell(r[r_reason]) if r_reason is not None else ""
                    for d in days:
                        out.append(dict(day=d, type=typ, label=cell(r[k]), region=cell(r[r_reg]), frame=tf, start=a, end=b, notice=notice if len(body) == 1 else "",
                                        issued=issued if len(body) == 1 else "", reason=reason[:300], layout="records", page=pno))
            elif low[0].startswith("date") and any(x in low for x in ("stage 1", "stage 2", "stage 3")):  # stages, 1998 to 2004
                cols = {i: kind(h) for i, h in enumerate(head) if kind(h)}
                date0 = head[0].replace("Date", "").strip()
                for j, r in enumerate(body):
                    raw = cell(r[0]) or (date0 if j == 0 else "")
                    day = parse_date(raw)
                    if not day:
                        continue
                    for i, typ in cols.items():
                        v = cell(r[i]) if i < len(r) else ""
                        if v and v.lower() not in ("none", "n/a"):
                            out.append(dict(day=day, type=typ, label=head[i], region="ISO", frame=v, start="", end="", notice="", issued="", reason="",
                                            layout="stages", page=pno))
            elif low[0].startswith("date"):  # matrix, 2005 to 2015
                cols = {i: kind(h) for i, h in enumerate(head) if kind(h)}
                r_reg = low.index("region") if "region" in low else None
                for r in body:
                    raw = cell(r[0])
                    days = expand(raw)
                    if not days:
                        continue
                    for i, typ in cols.items():
                        v = cell(r[i]) if i < len(r) else ""
                        if v and v.lower() not in ("none", "n/a"):
                            for d in days:
                                out.append(dict(day=d, type=typ, label=head[i], region=cell(r[r_reg]) if r_reg is not None else "ISO", frame=v, start="", end="",
                                                notice="", issued="", reason="", layout="matrix", page=pno))
            elif low[0] in ("1998", "1998*") or low[0] in ("no touch", "rmo*"):  # day lists, 1998 to 2001
                out += day_list(head, body, text, pno, log, tbl.bbox, words)
    return out


def expand(raw):
    """A matrix date: MM/DD/YY, or a range of days of one month such as 7/29-31/10."""
    d = parse_date(raw)
    if d:
        return [d]
    m = re.fullmatch(r"(\d{1,2})/(\d{1,2})-(\d{1,2})/(\d{2,4})", raw)
    if m:
        y = int(m.group(4)) + (2000 if len(m.group(4)) == 2 else 0)
        return [dt.date(y, int(m.group(1)), k) for k in range(int(m.group(2)), int(m.group(3)) + 1)]
    m = re.fullmatch(r"(\d{1,2})/(\d{1,2})-(\d{1,2})/(\d{1,2})/(\d{4})", raw)  # 2/8-2/29/2012, 4/30-5/31/2012
    if m:
        y = int(m.group(5))
        a, b = dt.date(y, int(m.group(1)), int(m.group(2))), dt.date(y, int(m.group(3)), int(m.group(4)))
        return [a + dt.timedelta(days=k) for k in range((b - a).days + 1)] if a <= b else []
    return []


def day_list(head, body, text, pno, log, bbox, words):
    """The 1998 to 2002 day lists. A table headed by years lists one notice type's days per year, the type printed above
    it (the words within 30 points above the table and inside its width: No Touch, Alert, Warning, Power Watch); a table
    headed by types lists one year's days per type, the year in the page title."""
    out = []
    low = [h.lower().replace("*", "") for h in head]
    if low[0] == "1998":
        x0, top, x1 = bbox[0], bbox[1], bbox[2]
        label = " ".join(w["text"] for w in sorted(words, key=lambda w: w["x0"]) if top - 30 <= w["top"] < top and x0 <= w["x0"] < x1)
        typ = kind(label)
        if not typ:
            log(f"  page {pno}: a day list whose label above it ({label!r}) names no notice type; left out")
            return out
        for r in body:
            for i, y in enumerate(head):
                yy = re.sub(r"\D", "", y)
                d = parse_date(cell(r[i]) if i < len(r) else "", yy) if yy else None
                if d:
                    out.append(dict(day=d, type=typ, label=label, region="ISO", frame="", start="", end="", notice="", issued="", reason="",
                                    layout="day_lists", page=pno))
    else:
        ym = re.search(r"Days for (\d{4})", text)
        if not ym:
            log(f"  page {pno}: a day list without its year; left out")
            return out
        for r in body:
            for i, h in enumerate(head):
                typ = kind(h)
                d = parse_date(cell(r[i]) if i < len(r) else "", ym.group(1)) if typ else None
                if d:
                    out.append(dict(day=d, type=typ, label=h, region="ISO", frame="", start="", end="", notice="", issued="", reason="",
                                    layout="day_lists", page=pno))
    return out


def summary_counts(pdf):
    """CAISO's own yearly day counts per type, from the report's summary tables (pages 1 and 3)."""
    want = {}
    for pno in (1, 3):
        for t in pdf.pages[pno - 1].extract_tables():
            head = [cell(c) for c in t[0]]
            for r in t[1:]:
                y = cell(r[0])
                if not re.fullmatch(r"\d{4}", y):
                    continue
                for i, h in enumerate(head[1:], start=1):
                    v = cell(r[i]) if i < len(r) else ""
                    if h in SUMMARY and re.fullmatch(r"\d+", v):
                        # 2022 is in both tables: January to April on page 3, May on on page 1; the year is their sum
                        want[(int(y), SUMMARY[h][0])] = want.get((int(y), SUMMARY[h][0]), 0) + int(v)
    return want


def main(argv=None):
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    log = ip.Log(os.path.join(ip.LOG_DIR, f"caiso_emergencies_{run_id}.log"))
    ip.RAW.open("caiso_emergencies", run_id)
    results = []
    try:
        import io
        import pdfplumber
        r = requests.get(URL, timeout=180, headers={"User-Agent": "Mozilla/5.0 (ERW research; github.com/SamuelEnrique/erw)"})
        if r.status_code != 200 or not r.content.startswith(b"%PDF"):
            raise RuntimeError(f"{URL}: HTTP {r.status_code}, not a PDF")
        retrieved = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
        pdf = pdfplumber.open(io.BytesIO(r.content))
        revised = re.search(r"Revision Date:\s*([\d/]+)", pdf.pages[0].extract_text() or "")
        revised = revised.group(1) if revised else ""
        log(f"ERW caiso_emergencies {run_id}: {URL} ({len(r.content):,} bytes, {len(pdf.pages)} pages, revised {revised})")
        rows = records(pdf, log)
        df = pd.DataFrame(rows)
        n_raw = len(df)
        # one row per type and day: CAISO repeats a multi-day notice on each day's page (2021), and a day may hold
        # several notices of a type (regions); the yearly counts are days
        df["region_key"] = df["region"].str.lower()
        df = df.sort_values(["day", "type", "page"]).drop_duplicates(["day", "type", "region_key", "frame"], keep="first")
        log(f"{n_raw} rows read from the report's tables, {len(df)} after removing repeated pages")
        # the check against CAISO's own counts (days per type and year)
        want = summary_counts(pdf)
        got = df.assign(y=pd.to_datetime(df["day"]).dt.year).groupby(["y", "type"])["day"].nunique().to_dict()
        diffs = [(y, t, w, got.get((y, t), 0)) for (y, t), w in sorted(want.items()) if got.get((y, t), 0) != w]
        match = len(want) - len(diffs)
        log(f"CAISO's summary: {len(want)} year-type counts; {match} match the table's days")
        for y, t, w, g in diffs:
            log(f"  {y} {t}: CAISO counts {w} days, the table holds {g}")
        if len(df) > CEILING:
            raise RuntimeError(f"{len(df)} rows, over the {CEILING} ceiling")
        key = lambda r: hashlib.sha1(f"{r['day']}|{r['type']}|{r['region_key']}|{r['frame']}".encode()).hexdigest()[:10]  # noqa: E731
        out = pd.DataFrame({
            "event_id": [f"caiso_awe:{r['day']}:{r['type']}:{key(r)}" for _, r in df.iterrows()],
            "event_date": df["day"].astype(str), "event_type": df["type"], "parties": "California ISO", "entity_ids": "", "mw": "", "price": "",
            "currency": "", "status": "declared", "source": SOURCE, "source_url": URL,
            "x_label": df["label"], "x_region": df["region"], "x_time_frame": df["frame"], "x_start": df["start"], "x_end": df["end"], "x_notice": df["notice"],
            "x_issued_at": df["issued"], "x_reason": df["reason"], "x_layout": df["layout"], "x_page": df["page"]})
        cols = list(out.columns)
        header = [
            "Energy Research Warehouse (ERW): CAISO grid emergencies, every Flex Alert, Restricted Maintenance Operations notice, Energy "
            "Emergency Alert, stage emergency and transmission emergency in CAISO's Grid Emergencies History Report (session 58)",
            "Shape: events (docs/datastandard.md v0, decision 35). One row per notice type, region and local (Pacific) day covered; "
            "event_type is CAISO's notice type (flex_alert, rmo, transmission_emergency, eea_watch, eea1 to eea3, alert, warning, stage1 to "
            "stage3, power_watch, vlrp, load_interruption). x_label: the notice's name as printed; x_layout: the report's layout the row was read from (records 2016 on, matrix "
            "2005 to 2015, stages 1998 to 2004, day_lists 1998 to 2001); x_page: its page.",
            f"Check against CAISO's own yearly day counts (the report's pages 1 and 3): {match} of {len(want)} year-type counts match; "
            + ("; ".join(f"{y} {t}: CAISO {w}, table {g}" for y, t, w, g in diffs) if diffs else "all match") + ".",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/caiso_emergencies.py; the report's revision date {revised}",
            f"Run log: warehouse/output/logs/caiso_emergencies_{run_id}.log",
            f"Raw files: warehouse/raw/caiso_emergencies/{run_id}/ (not in git)",
            f"Source: {SOURCE} California ISO, Grid Emergencies History Report (1998 to present), {URL}",
            f"License: public. CAISO's Privacy and Terms of Use ({TERMS}): its materials may be used provided copyright notices are kept "
            "and the California ISO is credited. Credit: California ISO, Grid Emergencies History Report.",
        ]
        path = os.path.join(ip.OUT_DIR, NAME + ".csv")
        if os.path.exists(path):
            os.remove(path)  # a snapshot of the report's current revision
        ip.write_csv(out, NAME, header, log, cols=cols, key=["event_id"], time_col="event_date")
        ip.update_sources([dict(source=SOURCE, publisher="California Independent System Operator (CAISO)",
                                report="Grid Emergencies History Report (1998 to present)", report_url=URL, document_list=TERMS,
                                license="public", tables=[NAME])])
        msg = f"{len(out)} rows, {out['event_date'].min()} to {out['event_date'].max()}; CAISO's counts: {match} of {len(want)} match"
        results.append(dict(table=NAME, market="all", status="ok", detail=msg))
        print(f"caiso_emergencies: {msg}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED:\n{tb}")
        print(f"caiso_emergencies FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    ip.write_status("caiso_emergencies", run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
