#!/usr/bin/env python3
"""The NRC's Reactor Oversight Process findings and violations: each inspection finding or violation at an operating
reactor site, with its issue date, inspection report, procedure, type, cornerstone, significance color, cross-cutting
aspect and how it was identified (session 2178, chain 097: the reactors' inspection record, beside their status).

Energy Research Warehouse (ERW) connector. One events table from the NRC's published dataset, linked from its data page:

    https://www.nrc.gov/documents-reports/nrc-data
    https://www.nrc.gov/sites/default/files/doc_library/cdn/data/reactors/operating/dataset/findings-violations.xlsx

    nrc_rop_findings   event_id nrc_rop:<a hash of the docket, report number, issue date, procedure, title, type and
               cornerstone attribute, which together are unique>; event_date the issue date; event_type the NRC's type in
               lower case (ncv non-cited violation, fin finding, vio violation, nov notice of violation, ncviv and noviv the
               same at severity IV, av apparent violation); parties the site as the NRC names it; entity_ids
               nrc_reactor:<docket number> (the ERW's nrc_power_reactors ids); mw, price, currency empty; status the
               significance color (green, white, yellow, red, greater than green); x_ columns keep the NRC's procedure,
               report number, cornerstone and its code, title, site code, cross-cutting aspect and area, who identified it,
               region, ADAMS accession number, traditional enforcement, severity, cornerstone attribute, year, quarter and
               the report's link

The sheet must hold the 23 columns the NRC's data dictionary lists, or the run stops; so does a row whose key is given
twice or whose issue date does not read. An issue date the file holds as an Excel serial number is read as one and
counted in the header. The report links point to /docs/ (ADAMS documents), which the NRC's robots file disallows to two
named crawlers (Akamai-SiteSnapshot and Amazonbot), not to every reader; they are kept as the NRC prints them and never
asked. Nothing is filled.

    python warehouse/connectors/nrc_rop_findings.py [--offline] [--out-dir DIR]

Ceiling: one request (the workbook, asked again unless --offline, since the NRC updates it at the same address).
www.nrc.gov's robots file disallows its search pages, ads.txt and autodiscover to every reader (and /docs/ to two named
crawlers), not /sites/ or /documents-reports/. License: the NRC's, as
license_verdicts.csv records it (the ERW's other NRC tables, nrc_power_reactors and nrc_event_notifications).
"""

import argparse
import datetime as dt
import hashlib
import io
import os
import sys
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

CONNECTOR = "nrc_rop_findings"
SOURCE = "nrc:rop_findings_violations"
HOST = "www.nrc.gov"
PAGE = "https://www.nrc.gov/documents-reports/nrc-data"
URL = "https://www.nrc.gov/sites/default/files/doc_library/cdn/data/reactors/operating/dataset/findings-violations.xlsx"
TABLE = "nrc_rop_findings"
PUBLISHER = "U.S. Nuclear Regulatory Commission (NRC)"
LICENSE = "public"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
EVENT_COLS = ["event_id", "event_date", "event_type", "parties", "entity_ids", "mw", "price", "currency", "status", "source", "source_url"]
COLUMNS = ["Procedure", "Issue Date", "Report Number", "Type", "CornerstoneCode", "Cornerstone", "Title", "Docket Number", "Site Name",
           "Site Code", "CrossCuttingAspect", "Idby", "Region", "Accession Number", "IsTraditionalEnforcement", "Item Severity Type Code",
           "Cornerstone Attribute Type", "Link", "Year", "Quarter", "CrossCutting Area", "Significance", "SignificanceSort"]
KEY = ["Docket Number", "Report Number", "Issue Date", "Procedure", "Title", "Type", "Cornerstone Attribute Type"]
X_MAP = {"x_procedure": "Procedure", "x_report_number": "Report Number", "x_cornerstone": "Cornerstone", "x_cornerstone_code": "CornerstoneCode",
         "x_title": "Title", "x_site_code": "Site Code", "x_cross_cutting_aspect": "CrossCuttingAspect", "x_cross_cutting_area": "CrossCutting Area",
         "x_identified_by": "Idby", "x_region": "Region", "x_accession": "Accession Number", "x_traditional_enforcement": "IsTraditionalEnforcement",
         "x_severity": "Item Severity Type Code", "x_cornerstone_attribute": "Cornerstone Attribute Type", "x_year": "Year", "x_quarter": "Quarter",
         "x_link": "Link"}
X_COLS = list(X_MAP)
EXCEL_EPOCH = dt.date(1899, 12, 30)


def text(x):
    return "" if x is None or (isinstance(x, float) and pd.isna(x)) else str(x).strip()


def issue_day(x, where, serials):
    if isinstance(x, (dt.datetime, pd.Timestamp)):
        return pd.Timestamp(x).strftime("%Y-%m-%d")
    if isinstance(x, (int, float)) and not isinstance(x, bool) and 20000 < float(x) < 80000:
        serials.append(where)
        return (EXCEL_EPOCH + dt.timedelta(days=int(x))).isoformat()
    raise RuntimeError(f"{where}: an issue date that does not read: {x!r}")


def parse(content, base, serials):
    v = pd.read_excel(io.BytesIO(content), sheet_name=0, dtype=object, keep_default_na=False)
    if list(v.columns) != COLUMNS:
        raise RuntimeError(f"the columns are not the data dictionary's: {list(v.columns)}")
    out, seen = [], set()
    for i, r in v.iterrows():
        key = "|".join(text(r[c]) for c in KEY)
        if key in seen:
            raise RuntimeError(f"row {i}: a finding given twice: {key[:120]}")
        seen.add(key)
        docket = text(r["Docket Number"])
        row = dict(base, event_id="nrc_rop:" + hashlib.sha1(key.encode("utf-8")).hexdigest()[:14],
                   event_date=issue_day(r["Issue Date"], f"row {i}", serials), event_type=text(r["Type"]).lower(),
                   parties=text(r["Site Name"]), entity_ids=f"nrc_reactor:{docket}" if docket else "", mw="", price="", currency="",
                   status=text(r["Significance"]).lower())
        for k, c in X_MAP.items():
            row[k] = text(r[c])
        out.append(row)
    if not out:
        raise RuntimeError("no row")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="The NRC's Reactor Oversight Process findings and violations")
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
        if ip.paused(CONNECTOR) or ip.paused_host(HOST):
            raise RuntimeError(f"{HOST} is paused (warehouse/metadata/paused_sources.csv): no request made")
        content, rec = ip.fetch_raw(CONNECTOR, URL, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=180, pause=1)
        base = dict(source=SOURCE, source_url=URL, retrieved_at=rec.get("retrieved_at") or "")
        serials = []
        t = pd.DataFrame(parse(content, base, serials))
        cols = EVENT_COLS + X_COLS
        t = t[cols].sort_values(["event_date", "event_id"]).reset_index(drop=True)
        head = [
            f"Energy Research Warehouse (ERW): U.S. Nuclear Regulatory Commission, Reactor Oversight Process findings and violations, {len(t):,} "
            f"findings at {t.parties.nunique()} sites, issued {t.event_date.min()} to {t.event_date.max()} (session 2178)",
            "Shape: events (docs/datastandard.md v0). event_id nrc_rop:<hash of the key fields>; event_date the issue date; event_type the NRC's "
            "type (ncv, fin, vio, nov, ncviv, noviv, av); parties the site; entity_ids nrc_reactor:<docket>; status the significance color; x_ "
            "columns the NRC's procedure, report, cornerstone, title, site code, cross-cutting aspect and area, identified by, region, accession, "
            "traditional enforcement, severity, cornerstone attribute, year, quarter and link.",
            f"The NRC's data dictionary's 23 columns, as read; no key given twice. Issue dates held as Excel serial numbers, read as such: "
            f"{len(serials)}. The links point to /docs/ (ADAMS documents): kept as printed, never asked. Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/nrc_rop_findings.py; the workbook retrieved {base['retrieved_at']}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Nuclear Regulatory Commission, NRC Data, Reactor Oversight Process: Findings and Violations, {PAGE}",
            f"  access: {URL}",
            "License: the NRC's (see license_verdicts.csv). Cite the U.S. Nuclear Regulatory Commission.",
        ]
        ip.write_snapshot(t, TABLE, head, log, cols)
        results.append(dict(table=TABLE, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{TABLE}: {len(t):,} findings, {t.parties.nunique()} sites, {t.event_date.min()} to {t.event_date.max()}; serial dates {len(serials)}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{TABLE} FAILED, no output file written:\n{tb}")
        print(f"{TABLE} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=TABLE, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher=PUBLISHER, report="NRC Data: Reactor Oversight Process findings and violations",
                                    report_url=PAGE, document_list=PAGE, license=LICENSE, tables=[TABLE])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
