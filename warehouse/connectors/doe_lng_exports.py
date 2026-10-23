#!/usr/bin/env python3
"""DOE's long-term applications and authorizations to export LNG: each application in the Department's summary, with
its applicant, quantity, and the status and docket of its free trade (FTA) and non-free trade (non-FTA) parts (session
2044, chain 059: the export side of the gas market beside eia_lng_exports_monthly).

Energy Research Warehouse (ERW) connector. One entities table, warehouse/output/doe_lng_export_applications.csv, from
the Summary of LNG Export Applications of the Lower 48 States, a PDF the Department's Hydrocarbons and Geothermal
Energy Office (formerly the Office of Fossil Energy and Carbon Management) posts each quarter:

    https://www.energy.gov/fecm/articles/summary-lng-export-applications-lower-48-states

The summary has three tables, kept apart in x_section: the Lower-48 applications (lower48), the applications to export
U.S. gas as LNG from Canada and Mexico (canada_mexico), and the small-scale applications (small_scale). Its pages of
notes are not taken. One row an application as the summary lists it (a row of the table).

    entity_id    doe_lng:<docket>, the first docket the row names (FTA, else non-FTA), with -2 for a docket a second row
                 names first; entity_type project; name the applicant as printed; a footnote letter printed in the name's own size ("(g)")
                 would go to x_footnotes, but in the summary of 30 September 2026 every marker is 7-point text, so the
                 column is empty
    status       active when either part is approved, planned when a part is under review and none is approved,
                 withdrawn when every part is vacated, withdrawn, dismissed or expired; x_fta_status and
                 x_non_fta_status keep the Department's words ("Approved (F)", "Under DOE Review")
    x_*          the section, the quantity as printed, the FTA and non-FTA quantities in Bcf/d (a single quantity is the
                 application's for both parts; a design increase is added to its part), the two dockets, whether the
                 row is marked as waiting for its NEPA review (*), the summary's date and page

The summary's footnote markers are 7-point link text printed over the names; only text of 9 points or more is read.
Values as published; a blank stays blank; nothing is filled. A row without a docket, a status not in STATUSES or a
page whose columns cannot be found stops the run. The summary's own totals are read and printed in the header.

    python warehouse/connectors/doe_lng_exports.py [--offline] [--pdf URL] [--out-dir DIR]

Ceiling: two requests (the article page, fresh each run, and the PDF it links, reused from warehouse/raw/doe_lng_exports/
when saved). energy.gov's robots file disallows only Drupal's own paths and search. License: "Government information at
DOE websites is in the public domain" (DOE's web policies, read 54).
"""

import argparse
import collections
import datetime as dt
import io
import os
import re
import sys
import traceback
import urllib.parse

import pandas as pd
import pdfplumber

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "doe_lng_export_applications"
CONNECTOR = "doe_lng_exports"
SOURCE = "doe:lng_export_applications"
PAGE = "https://www.energy.gov/fecm/articles/summary-lng-export-applications-lower-48-states"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
ENTITY_COLS = ["entity_id", "entity_type", "name", "geo", "lat", "lon", "capacity_mw", "status", "status_date",
               "operator", "source"]
X_COLS = ["x_section", "x_quantity_as_published", "x_fta_bcfd", "x_non_fta_bcfd", "x_fta_status", "x_fta_docket",
          "x_non_fta_status", "x_non_fta_docket", "x_nepa_pending", "x_footnotes", "x_as_of", "x_page", "source_url",
          "retrieved_at"]
STATUSES = {"Approved": "approved", "Approved (F)": "approved", "Under DOE Review": "review", "Vacated": "ended",
            "Vacated (F)": "ended", "Withdrawn": "ended", "Dismissed": "ended", "Expired": "ended", "In Abeyance": "review", "n/a": "none", "": "none"}
DOCKET_RE = re.compile(r"\((\d{2})\s*-\s*(\d{1,3})\s*-?\s*(LNG|CNG|CGL)\)")
NOTE_RE = re.compile(r"\s*\((?:[a-z]{1,3})\)|\s*\*+")
NUM_RE = re.compile(r"(\d+(?:\.\d+)?)\s*(?:Bcf/d|billion cubic feet per day(?: \(Bcf/d\))?)?")


def text(v):
    return re.sub(r"\s+", " ", str(v or "")).strip()


def clusters(values, gap=3.0):
    out = []
    for v in sorted(values):
        if out and v - out[-1][-1] <= gap:
            out[-1].append(v)
        else:
            out.append([v])
    return [sum(c) / len(c) for c in out]


def section_of(page_text, before):
    """The table a page holds: a page that names no table continues the one before it."""
    if "CANADA and MEXICO APPLICATIONS" in page_text:
        return "canada_mexico"
    if "SMALL-SCALE APPLICATIONS" in page_text:
        return "small_scale"
    return before


def bands(page):
    """The table's rows of one page: [{column: text}], the rows between the company column's ruling lines."""
    q = page.filter(lambda o: o.get("object_type") != "char" or o["size"] >= 9)
    words = q.extract_words(keep_blank_chars=False, use_text_flow=False)
    head = [w for w in words if w["text"] == "Company"
            and any(v["text"] == "Quantity" and abs(v["top"] - w["top"]) < 3 for v in words)]
    if not head:
        return None  # a page of notes
    cols = clusters([e["x0"] for e in page.edges if e["orientation"] == "v" and e["height"] > 20])
    if len(cols) != 5:
        raise RuntimeError(f"page {page.page_number}: {len(cols)} column lines, not 5: {[round(c) for c in cols]}")
    tops = clusters([e["top"] for e in page.edges if e["orientation"] == "h" and abs(e["x0"] - cols[0]) < 4
                     and abs(e["x1"] - cols[1]) < 4], gap=2.5)
    start = max(w["bottom"] for w in words if w["text"] == "(Docket" or w["text"] == "Number)")
    tops = [t for t in tops if t >= start - 2]
    rows = []
    for t0, t1 in zip(tops, tops[1:]):
        cells = collections.defaultdict(list)
        for w in words:
            mid = (w["x0"] + w["x1"]) / 2
            if t0 - 1 <= w["top"] < t1 - 1:
                for k, (a, b) in enumerate(zip(cols, cols[1:])):
                    if a <= mid < b:
                        cells[k].append(w)
        if not cells:
            continue
        row = {}
        for k in range(4):
            ws = sorted(cells.get(k, []), key=lambda w: (round(w["top"]), w["x0"]))
            lines, last = [], None
            for w in ws:
                if last is not None and abs(w["top"] - last) <= 3:
                    lines[-1].append(w["text"])
                else:
                    lines.append([w["text"]])
                    last = w["top"]
            row[k] = [" ".join(x) for x in lines]
        rows.append(row)
    return rows


def quantities(lines, fta_on, non_on):
    """FTA and non-FTA Bcf/d from the quantity cell's lines: "1.0 Bcf/d: FTA", "0.77 Bcf/d: non-FTA", a design
    increase added to its part, or one quantity for each part the row applies for. A design increase printed without
    its part beside an FTA and a non-FTA quantity is left in the printed text only."""
    s = text(" ".join(lines))
    fta = non = 0.0
    seen_part = False
    for m in re.finditer(r"(\d+(?:\.\d+)?)\s*(?:Bcf/d)?\s*:\s*(non-FTA|FTA)", s, re.I):
        seen_part = True
        if m.group(2).upper() == "FTA":
            fta += float(m.group(1))
        else:
            non += float(m.group(1))
    if seen_part:
        return (f"{fta:g}" if fta else ""), (f"{non:g}" if non else "")
    nums = [float(x) for x in re.findall(r"(?<![\w.])(\d+(?:\.\d+)?)(?=\s*(?:Bcf/d|billion|\(|\*|$|\s))", s)]
    if not nums:
        return "", ""
    q = sum(nums)  # a base quantity and its design increase
    return (f"{q:g}" if fta_on else ""), (f"{q:g}" if non_on else "")


def part(lines):
    """(status as the Department writes it, docket, NEPA mark) of an FTA or non-FTA cell."""
    s = text(" ".join(lines))
    nepa = "*" in s
    dockets = ["-".join(m) for m in DOCKET_RE.findall(s)]
    first = DOCKET_RE.split(s)[0] if dockets else s
    status = text(re.sub(r"\*", "", first))
    status = re.sub(r"\s*\(Design Increase\).*", "", status)
    if status not in STATUSES:
        raise RuntimeError(f"a status not in the map: {status!r} in {s!r}")
    return status, (dockets[0] if dockets else ""), nepa


def build(pages, url, retrieved, as_of):
    rows, totals, seen = [], [], collections.Counter()
    section = "lower48"
    for number, page in pages:
        ptext = page.extract_text() or ""
        got = bands(page)
        if got is None:
            continue
        section = section_of(ptext, section)
        for r in got:
            name_raw = text(" ".join(r[0]))
            if not name_raw and not any(r[k] for k in (1, 2, 3)):
                continue
            if name_raw.startswith("Total of all"):
                totals.append((section, text(" ".join(r[2] or r[1])), text(" ".join(r[3]))))
                continue
            fta_s, fta_d, n1 = part(r[2])
            non_s, non_d, n2 = part(r[3])
            if not (fta_d or non_d):
                raise RuntimeError(f"page {number}: a row without a docket: {name_raw!r}")
            notes = [x.strip(" ()") for x in re.findall(r"\(([a-z]{1,3})\)", name_raw)]
            name = text(NOTE_RE.sub("", name_raw))
            fta_q, non_q = quantities(r[1], STATUSES[fta_s] != "none", STATUSES[non_s] != "none")
            kinds = {STATUSES[fta_s], STATUSES[non_s]} - {"none"}
            status = "active" if "approved" in kinds else ("planned" if "review" in kinds else "withdrawn")
            first = fta_d or non_d
            seen[first] += 1
            rows.append({"entity_id": f"doe_lng:{first}" + (f"-{seen[first]}" if seen[first] > 1 else ""),
                         "entity_type": "project", "name": name, "geo": "", "lat": "", "lon": "", "capacity_mw": "",
                         "status": status, "status_date": as_of, "operator": "", "source": SOURCE,
                         "x_section": section, "x_quantity_as_published": text(" ".join(r[1])), "x_fta_bcfd": fta_q,
                         "x_non_fta_bcfd": non_q, "x_fta_status": fta_s, "x_fta_docket": fta_d, "x_non_fta_status": non_s,
                         "x_non_fta_docket": non_d, "x_nepa_pending": "yes" if (n1 or n2) else "",
                         "x_footnotes": ";".join(notes), "x_as_of": as_of, "x_page": str(number), "source_url": url,
                         "retrieved_at": retrieved})
    if not rows:
        raise RuntimeError("no application read")
    return pd.DataFrame(rows, columns=ENTITY_COLS + X_COLS), totals


def as_of_date(pdf):
    m = re.search(r"\(as of (\w+ \d{1,2}, \d{4})\)", pdf.pages[0].extract_text() or "")
    if not m:
        raise RuntimeError("the summary's date not found")
    return dt.datetime.strptime(m.group(1), "%B %d, %Y").strftime("%Y-%m-%d")


def main(argv=None):
    ap = argparse.ArgumentParser(description="DOE's summary of LNG export applications")
    ap.add_argument("--offline", action="store_true", help="the saved files only, no request")
    ap.add_argument("--pdf", help="the summary at this address, the article page not asked")
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
        url = args.pdf
        if not url:
            page, _ = ip.fetch_raw(CONNECTOR, PAGE, log, offline=args.offline, fresh=True, headers=UA, timeout=120)
            links = re.findall(r'href="([^"]+Summary[^"]*LNG[^"]*\.pdf)"', page.decode("utf-8", errors="replace"))
            if not links:
                raise RuntimeError(f"{PAGE} links no summary PDF")
            url = urllib.parse.urljoin(PAGE, links[0])
        content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, headers=UA, timeout=180)
        if content[:4] != b"%PDF":
            raise RuntimeError(f"{url} is not a PDF")
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            as_of = as_of_date(pdf)
            t, totals = build(list(enumerate(pdf.pages, start=1)), url, rec.get("retrieved_at") or "", as_of)
        by = t.groupby(["x_section", "status"]).size()
        header = [
            f"Energy Research Warehouse (ERW): U.S. Department of Energy, Summary of LNG Export Applications of the Lower 48 States, as of {as_of}: "
            "each long-term (and small-scale) application to export LNG, CNG or CGL, with its FTA and non-FTA parts (session 2044)",
            "Shape: entities (docs/datastandard.md v0). entity_id doe_lng:<docket> (the row's first docket); entity_type project; name the applicant as "
            "printed; status active (a part approved), planned (under review), withdrawn (every part vacated, withdrawn, dismissed or expired); "
            "status_date the summary's date; x_fta_bcfd and x_non_fta_bcfd the quantities in billion cubic feet a day; x_*_status the Department's words.",
            f"{len(t)} applications: " + "; ".join(f"{a} {b} {n}" for (a, b), n in by.items()) + ". The summary's totals: "
            + "; ".join(f"{s} FTA {f} non-FTA {n}" for s, f, n in totals) + ". The notes pages are not taken. Values as published; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/doe_lng_exports.py; the PDF retrieved {rec.get('retrieved_at') or ''}, last modified {ip.vintage_of(rec)}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Department of Energy, Hydrocarbons and Geothermal Energy Office, Summary of LNG Export Applications of the Lower 48 States, {PAGE}",
            f"  access: {url}",
            "License: public domain (DOE: \"Government information at DOE websites is in the public domain\").",
        ]
        ip.write_snapshot(t, NAME, header, log, cols=ENTITY_COLS + X_COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Department of Energy (DOE)",
                                    report="Summary of LNG Export Applications of the Lower 48 States (Hydrocarbons and Geothermal Energy Office)", report_url=PAGE,
                                    document_list=url, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} applications"))
        print(f"{NAME}: {len(t)} applications as of {as_of}; totals {totals}")
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
