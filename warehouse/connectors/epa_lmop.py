#!/usr/bin/env python3
"""EPA's Landfill Methane Outreach Program (LMOP) database: every municipal solid waste landfill the program tracks and
each landfill gas energy project at it, operational, planned, under construction, shut down or a candidate (session 2127,
chain 079: the landfill gas plants and pipelines beside the GHGRP's landfills and EIA's landfill gas generators).

Energy Research Warehouse (ERW) connector. One entities table, warehouse/output/epa_lmop_landfill_projects.csv, from the
sheet "LMOP Database" of EPA's composite data file, which its database page links:

    https://www.epa.gov/lmop/lmop-landfill-and-project-database
    https://www.epa.gov/system/files/documents/2024-09/lmopcompositedata.xlsx   (the data as of September 2024)

One row a landfill and project, as EPA lists them (a landfill without a project has a row of its own with a project id
and a status such as Candidate or Low Potential):

    entity_id     lmop:<Landfill ID>:<Project ID>; entity_type project
    name          the landfill's name, then the project's name where it has one ("Anchorage Regional Landfill: Project #1")
    capacity_mw   "Rated MW Capacity" as EPA gives it. A project fed by several landfills is listed on each landfill's row
                  with the same capacity (project 1016-0, 22.5 MW, on three New Jersey landfills), so capacity is never
                  summed over rows: one row a project id counts it once
    status        operating (Operational), under_construction (Construction), planned (Planned), retired (Shutdown); blank
                  for Candidate, Future Potential, Low Potential and Unknown, which are landfills, not projects. lmop_status
                  keeps EPA's word
    status_date   blank; project_start_date and project_shutdown_date keep EPA's dates
    operator      the project's owner(s) as EPA writes them
    geo           US-<state>; lat and lon as EPA gives them
    the rest      every other column of the sheet, its header in snake case (ghgrp_id, landfill_id, waste_in_place_tons,
                  lfg_collected_mmscfd, project_type_category, lfg_energy_project_type, actual_mw_generation and the rest)

EPA's own counts on the file's Summary sheet (unique landfills, unique operational projects, a project's expansions
counted with it) are checked against the rows: a difference stops the run. Values as published; a blank stays blank;
nothing is filled. A sheet without the columns named here, a landfill and project given twice or a status not EPA's
stops the run.

    python warehouse/connectors/epa_lmop.py [--offline] [--out-dir DIR]

Ceiling: two requests (the database page, for the file's address, and the file), reused from warehouse/raw/epa_lmop/
with --offline. www.epa.gov's robots file disallows Drupal's own paths and search pages (session 2127). License: public
(EPA, record 55 of license_reads.csv; cite "U.S. EPA, Landfill Methane Outreach Program (LMOP) Database").
"""

import argparse
import datetime as dt
import io
import os
import re
import sys
import traceback
import urllib.parse

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "epa_lmop_landfill_projects"
CONNECTOR = "epa_lmop"
SOURCE = "epa:lmop"
PAGE = "https://www.epa.gov/lmop/lmop-landfill-and-project-database"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
SHEET = "LMOP Database"
STATUS = {"Operational": "operating", "Construction": "under_construction", "Planned": "planned", "Shutdown": "retired",
          "Candidate": "", "Future Potential": "", "Low Potential": "", "Unknown": ""}
NEEDED = ["Landfill ID", "Project ID", "Landfill Name", "Project Name", "State", "Latitude", "Longitude",
          "Rated MW Capacity", "Current Project Status", "Project Owner(s)", "Project Start Date", "Project Shutdown Date"]
BASE = ["entity_id", "entity_type", "name", "geo", "lat", "lon", "capacity_mw", "status", "status_date", "operator",
        "source", "source_url", "retrieved_at", "vintage"]


def snake(h):
    return re.sub(r"_+", "_", re.sub(r"[^a-z0-9]+", "_", h.lower())).strip("_")


def text(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return ""
    if isinstance(v, (dt.datetime, pd.Timestamp)):
        return v.strftime("%Y-%m-%d")
    s = re.sub(r"\s+", " ", str(v)).strip()
    return "" if s.lower() == "nan" else s


def summary_counts(sheet):
    """EPA's (unique landfills, unique operational projects) from the Summary sheet's first two rows."""
    head = [text(v) for v in sheet.iloc[0].tolist()]
    vals = sheet.iloc[1].tolist()
    got = dict(zip(head, vals))
    return int(got["Count of Unique Landfills in this File"]), int(got["Count of Unique Operational Projects in this File"])


def build(workbook, url, retrieved, vintage):
    x = pd.ExcelFile(io.BytesIO(workbook))
    if SHEET not in x.sheet_names:
        raise RuntimeError(f"the workbook has no sheet {SHEET!r}: {x.sheet_names}")
    t = x.parse(SHEET, dtype=object)
    missing = [c for c in NEEDED if c not in t.columns]
    if missing:
        raise RuntimeError(f"the sheet lacks {missing}")
    extra = [c for c in t.columns if c not in ("Latitude", "Longitude", "Rated MW Capacity", "Project Owner(s)")]
    rows = []
    for r in t.to_dict("records"):
        status = text(r["Current Project Status"])
        if status not in STATUS:
            raise RuntimeError(f"a status not EPA's: {status!r}")
        landfill, project, st = text(r["Landfill ID"]), text(r["Project ID"]), text(r["State"])
        name = text(r["Landfill Name"]) + (f": {text(r['Project Name'])}" if text(r["Project Name"]) else "")
        row = {"entity_id": f"lmop:{landfill}:{project}", "entity_type": "project", "name": name,
               "geo": f"US-{st}" if st else "", "lat": text(r["Latitude"]), "lon": text(r["Longitude"]),
               "capacity_mw": text(r["Rated MW Capacity"]), "status": STATUS[status], "status_date": "",
               "operator": text(r["Project Owner(s)"]), "source": SOURCE, "source_url": url, "retrieved_at": retrieved,
               "vintage": vintage}
        for c in extra:
            row[snake(c) if snake(c) != "current_project_status" else "lmop_status"] = text(r[c])
        rows.append(row)
    cols = BASE + [snake(c) if snake(c) != "current_project_status" else "lmop_status" for c in extra]
    out = pd.DataFrame(rows, columns=cols)
    twice = out.entity_id[out.entity_id.duplicated()]
    if len(twice):
        raise RuntimeError(f"a landfill and project given twice: {list(twice)[:3]}")
    landfills, operational = summary_counts(x.parse("Summary", header=None, dtype=object))
    have_l = out.landfill_id.nunique()
    have_o = out[out.lmop_status == "Operational"].project_id.str.split("-").str[0].nunique()
    if (have_l, have_o) != (landfills, operational):
        raise RuntimeError(f"EPA's summary counts {landfills} landfills and {operational} operational projects; the rows hold {have_l} and {have_o}")
    return out.sort_values("entity_id").reset_index(drop=True), landfills, operational


def main(argv=None):
    ap = argparse.ArgumentParser(description="EPA LMOP: landfills and landfill gas energy projects")
    ap.add_argument("--offline", action="store_true", help="the saved files only, no request")
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
        if not args.offline and (ip.paused("epa") or ip.paused_host("www.epa.gov")):
            raise RuntimeError("EPA is paused (warehouse/metadata/paused_sources.csv): not requested")
        page, _ = ip.fetch_raw(CONNECTOR, PAGE, log, offline=args.offline, headers=UA, timeout=120)
        links = re.findall(r'href="([^"]*lmopcompositedata[^"]*\.xlsx)"', page.decode("utf-8", errors="replace"))
        if not links:
            raise RuntimeError(f"{PAGE} links no composite data file")
        url = urllib.parse.urljoin(PAGE, links[0])
        content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, headers=UA, timeout=300)
        t, landfills, operational = build(content, url, rec.get("retrieved_at") or "", ip.vintage_of(rec))
        by = t.lmop_status.value_counts()
        op = t[t.lmop_status == "Operational"].drop_duplicates("project_id")
        mw = pd.to_numeric(op.capacity_mw, errors="coerce").sum()
        header = [
            "Energy Research Warehouse (ERW): U.S. EPA, Landfill Methane Outreach Program (LMOP) Database, composite data file: every landfill the program tracks and its landfill gas energy projects (session 2127)",
            "Shape: entities (docs/datastandard.md v0). entity_id lmop:<Landfill ID>:<Project ID>, one row a landfill and project as EPA lists them; entity_type project; capacity_mw EPA's rated MW capacity, "
            "repeated on each landfill's row of a project fed by several landfills, so never summed over rows (one row a project id counts it once); status operating, under_construction, planned or retired, blank for a landfill without a project (lmop_status keeps EPA's word).",
            f"{len(t)} rows, {landfills} landfills and {operational} operational projects, as EPA's summary counts them (a project's expansions with it); by EPA's status: "
            + "; ".join(f"{k} {v}" for k, v in by.items())
            + f". Operational project ids hold {mw:,.1f} MW of rated capacity, counted once each. Values as published; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/epa_lmop.py; the file retrieved {rec.get('retrieved_at') or ''}"
            + (f", last modified {ip.vintage_of(rec)}" if ip.vintage_of(rec) else ""),
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Environmental Protection Agency, Landfill Methane Outreach Program (LMOP) Database, composite data file, {PAGE}",
            f"  access: {url}",
            "License: public (a work of the U.S. government). Cite: U.S. EPA, Landfill Methane Outreach Program (LMOP) Database.",
        ]
        ip.write_snapshot(t, NAME, header, log, cols=list(t.columns))
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Environmental Protection Agency (EPA)",
                                    report="Landfill Methane Outreach Program (LMOP) Database, composite data file",
                                    report_url=PAGE, document_list=url, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows, {landfills} landfills, {operational} operational projects, {mw:,.1f} MW")
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
