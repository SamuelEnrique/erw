#!/usr/bin/env python3
"""Oak Ridge National Laboratory's U.S. Hydropower Development Pipeline: every proposed hydropower and pumped storage
project in permitting, licensing or exemption, or under construction, on 31 December 2025, with its FERC docket,
capacity, status, place, developer, dam and waterway (session 916, chain 051: the sibling of ornl_eha.py, the fleet in
operation; the ERW held no list of planned pumped storage).

Energy Research Warehouse (ERW) connector. One entities table, warehouse/output/ornl_hydropower_pipeline.csv, from the
U.S. Hydropower Development Pipeline Data, 2026 (HydroSource, ORNL; DOI 10.21951/HMR_PipelineFY26/3025030), the workbook
its landing page links:

    https://hydrosource.ornl.gov/data/datasets/us-hydropower-development-pipeline-data-2026/
    https://hydrosource.s3.us-east-2.amazonaws.com/files/data/datasets/us-hydropower-development-pipeline-data-2026/ORNL_US_Hydropower_DevelopmentPipeline_Data_2026.xlsx

    entity_id    ornl_hydro_pipeline:<FERC docket>; a project with no docket (Reclamation's lease of power privilege and a
                 preliminary lease) ornl_hydro_pipeline:none-<the project name as a slug>
    entity_type  project; name Project_name; geo US-<state>; lat, lon NAD83 as ORNL gives them; capacity_mw Capacity_MW
    status       under_construction where ORNL's status is "Under Construction", else planned; ORNL's own status (issued or
                 pending preliminary permit, license, exemption, LOPP authorization) in permit_status (Decision 20)
    operator     the developer (Project_developer)
    the rest     the database's own fields, renamed: the docket, project type (HY or PSH) and subcategory (non-powered dam,
                 conduit, new stream-reach, pumped storage), county and FIPS code, developer type, dam name and owner,
                 waterway, pumped storage configuration (open or closed loop), NERC region and hydrologic unit code

Values as ORNL publishes them; a blank stays blank; nothing is filled. A heading not in the map or an id given twice stops
the run. The workbook's field description dates the status "as of December 31, 2023"; its summary and the landing page
date the snapshot 31 December 2025, which the header takes and names.

    python warehouse/connectors/ornl_hydro_pipeline.py [--offline]

Ceiling: one request (the workbook, saved in warehouse/raw/ornl_hydro_pipeline/ and reused offline). HydroSource's robots
file allows the landing page (crawl delay 10 s); the S3 host has no robots file (HTTP 403, session 911). License:
HydroSource's Data Use Policy, "openly shared, without restriction", with a citation (license_verdicts.csv, session 914).
"""

import argparse
import datetime as dt
import io
import os
import re
import sys
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "ornl_hydropower_pipeline"
CONNECTOR = "ornl_hydro_pipeline"
SOURCE = "ornl:hydro_pipeline"
PAGE = "https://hydrosource.ornl.gov/data/datasets/us-hydropower-development-pipeline-data-2026/"
URL = ("https://hydrosource.s3.us-east-2.amazonaws.com/files/data/datasets/us-hydropower-development-pipeline-data-2026/"
       "ORNL_US_Hydropower_DevelopmentPipeline_Data_2026.xlsx")
DOI = "10.21951/HMR_PipelineFY26/3025030"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
ENTITY_COLS = ["entity_id", "entity_type", "name", "geo", "lat", "lon", "capacity_mw", "status", "status_date", "operator",
               "source", "source_url", "retrieved_at", "vintage"]
FIELDS = {"FERC_docket": "ferc_docket", "Status": "permit_status", "Project_type": "project_type",
          "Project_subcategory": "project_subcategory", "State": "state", "County": "county", "FIPS_Census": "county_fips",
          "Developer_type": "developer_type", "Dam_Name": "dam_name", "Dam_Owner": "dam_owner", "Waterway": "waterway",
          "PSH_configuration": "psh_configuration", "NERC": "nerc_region", "HUC12_All": "huc"}
NAMED = {"Project_name", "Capacity_MW", "Latitude", "Longitude", "Project_developer"}
EXTRA_COLS = list(FIELDS.values())
SNAPSHOT = "2025-12-31"


def cell(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return ""
    return re.sub(r"\s+", " ", str(v)).strip()


def number(v):
    s = cell(v)
    if s == "":
        return ""
    x = pd.to_numeric(s, errors="coerce")
    if pd.isna(x):
        raise RuntimeError(f"not a number: {v!r}")
    return int(x) if float(x).is_integer() else float(x)


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def projects(frame, url, retrieved, vintage):
    unknown = [c for c in frame.columns if c not in FIELDS and c not in NAMED]
    missing = [c for c in list(FIELDS) + sorted(NAMED) if c not in frame.columns]
    if unknown or missing:
        raise RuntimeError(f"headings not as read: unknown {unknown}, missing {missing}")
    rows = []
    for _, r in frame.iterrows():
        docket, name = cell(r["FERC_docket"]), cell(r["Project_name"])
        if not docket and not name:
            raise RuntimeError("a project with neither a docket nor a name")
        st = cell(r["Status"])
        row = {"entity_id": f"ornl_hydro_pipeline:{docket}" if docket else f"ornl_hydro_pipeline:none-{slug(name)}",
               "entity_type": "project", "name": name, "geo": f"US-{cell(r['State'])}" if cell(r["State"]) else "",
               "lat": number(r["Latitude"]), "lon": number(r["Longitude"]), "capacity_mw": number(r["Capacity_MW"]),
               "status": "under_construction" if st == "Under Construction" else "planned", "status_date": SNAPSHOT,
               "operator": cell(r["Project_developer"]), "source": SOURCE, "source_url": url, "retrieved_at": retrieved,
               "vintage": vintage}
        for k, v in FIELDS.items():
            row[v] = cell(r[k])
        rows.append(row)
    t = pd.DataFrame(rows)
    if t["entity_id"].duplicated().any():
        raise RuntimeError(f"an id given twice: {t.loc[t.entity_id.duplicated(), 'entity_id'].head(3).tolist()}")
    return t.sort_values("entity_id").reset_index(drop=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description="ORNL's U.S. Hydropower Development Pipeline")
    ap.add_argument("--offline", action="store_true", help="the saved workbook only, no request")
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
        content, rec = ip.fetch_raw(CONNECTOR, URL, log, offline=args.offline, headers=UA, timeout=300)
        if content[:2] != b"PK":
            raise RuntimeError(f"{URL} is not a workbook")
        retrieved, vintage = rec.get("retrieved_at") or "", ip.vintage_of(rec)
        t = projects(pd.read_excel(io.BytesIO(content), sheet_name="Data", dtype=str), URL, retrieved, vintage)
        cap = pd.to_numeric(t["capacity_mw"], errors="coerce")
        by = t.assign(c=cap).groupby("project_type").c.agg(["size", "sum"])
        kinds = ", ".join(f"{k} {int(v['size'])} ({v['sum']:,.0f} MW)" for k, v in by.iterrows())
        header = [
            "Energy Research Warehouse (ERW): Oak Ridge National Laboratory, U.S. Hydropower Development Pipeline, 2026: proposed hydropower and pumped storage projects on 31 December 2025 (session 916)",
            "Shape: entities (docs/datastandard.md v0). entity_id ornl_hydro_pipeline:<FERC docket> (none-<name> where there is no docket); entity_type project; "
            "geo US-<state>; lat, lon NAD83; capacity_mw the project's proposed capacity; status under_construction or planned, ORNL's own in permit_status; "
            "status_date the snapshot's day; operator the developer; project_type HY or PSH; psh_configuration open or closed loop.",
            f"{len(t):,} projects ({kinds}); {int((t.status == 'under_construction').sum())} under construction. The workbook's field description dates the "
            "status 31 December 2023; its summary and the landing page date the snapshot 31 December 2025, which is taken. Capacity additions at existing "
            "plants are not in the database (ORNL: they rest on a proprietary source). Values as published; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/ornl_hydro_pipeline.py; the workbook retrieved {retrieved}, last modified {vintage}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} M.M. Johnson and R. Uria-Martinez, U.S. Hydropower Development Pipeline Data, 2026, HydroSource, Oak Ridge National Laboratory, "
            f"Oak Ridge, Tennessee, DOI {DOI}, {PAGE}",
            f"  access: {URL}",
            "License: HydroSource's Data Use Policy: data hosted on HydroSource is openly shared, without restriction, in accordance with the Department of "
            "Energy's Public Access Plan; cite the authors, title, publisher and DOI.",
        ]
        ip.write_snapshot(t, NAME, header, log, cols=ENTITY_COLS + EXTRA_COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Oak Ridge National Laboratory (ORNL), HydroSource",
                                    report="U.S. Hydropower Development Pipeline Data", report_url=PAGE,
                                    document_list=URL, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t):,} projects"))
        print(f"{NAME}: {len(t):,} projects ({kinds})")
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
