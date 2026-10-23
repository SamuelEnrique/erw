#!/usr/bin/env python3
"""Oak Ridge National Laboratory's hydropower potential at existing non-powered dams: the 597 U.S. dams without power
whose estimated potential is above 1 MW, with each dam's place, owner, river, year built, storage, estimated head and
flow, and its potential energy and capacity (session 938, chain 053: the dams beside ornl_hydropower_pipeline's
non-powered dam projects).

Energy Research Warehouse (ERW) connector. One entities table, warehouse/output/ornl_npd_potential.csv, from ORNL's
"U.S. Hydropower Potential from Existing Non-powered Dams (greater than 1MW)" (HydroSource; NHAAP_NPD_FY11_1MW, created
April 2012 for the national assessment: B. Hadjerioua, Y. Wei and S.-C. Kao, An Assessment of Energy Potential at
Non-Powered Dams in the United States, DOE/EE-0711, 2012), the workbook its landing page links:

    https://hydrosource.ornl.gov/data/datasets/us-hydropower-potential-existing-non-powered-dams-greater-1mw/

    entity_id    ornl_npd:<NID id>, the National Inventory of Dams' id; entity_type project (a potential site at a dam);
                 name the dam's name; geo US-<state> (empty for a dam on a border, whose states, IL/KY, stay in state); lat, lon
    capacity_mw  the potential capacity (ORNL's mw: the potential energy over a regional capacity factor); status empty
                 (a potential, not a plan)
    operator     the dam's owner
    the rest     the county, nearest city, river, year built, storage (acre-feet), federal regulator, estimated head (ft)
                 and its source, the 2-digit hydrologic region, the annual mean flow (cfs), the potential annual energy
                 (MWh) and the regional capacity factor (percent)

These are estimates from flows and heads not measured at the dams, as ORNL states; not a design or a feasibility study.
The monthly flows and energies are not taken. A heading not as read or a NID id given twice stops the run; a blank stays
blank; nothing is filled.

    python warehouse/connectors/ornl_npd.py [--offline]

Ceiling: one request (the workbook, saved in warehouse/raw/ornl_npd/ and reused offline). HydroSource's robots file
allows the landing page (crawl delay 10 s); the S3 host has no robots file. License: HydroSource's Data Use Policy,
"openly shared, without restriction", with a citation (license_verdicts.csv, session 914).
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

NAME = "ornl_npd_potential"
CONNECTOR = "ornl_npd"
SOURCE = "ornl:npd_potential"
PAGE = "https://hydrosource.ornl.gov/data/datasets/us-hydropower-potential-existing-non-powered-dams-greater-1mw/"
URL = ("https://hydrosource.s3.us-east-2.amazonaws.com/files/data/datasets/us-hydropower-potential-existing-non-powered-dams-greater-1mw/"
       "NHAAP_NPD_FY11_1MW.XLS")
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
ENTITY_COLS = ["entity_id", "entity_type", "name", "geo", "lat", "lon", "capacity_mw", "status", "status_date", "operator",
               "source", "source_url", "retrieved_at", "vintage"]
FIELDS = {"nid_id1": "nid_id", "state": "state", "county": "county", "city": "city", "water": "river", "btyear": "year_built",
          "stor": "storage_acre_ft", "fedreg": "federal_regulator", "esth": "head_ft", "esthfr": "head_source", "huc02": "huc02",
          "qyr": "flow_cfs", "mwhyr": "potential_mwh_year", "cf": "capacity_factor_pct", "cordfrom": "coordinates_from"}
NAMED = {"lat", "lon", "dmname", "owname", "mw"}
MONTHLY = {f"q{m:02d}" for m in range(1, 13)} | {f"mwh{m:02d}" for m in range(1, 13)}
NUMBERS = {"stor", "esth", "qyr", "mwhyr", "cf"}
EXTRA = list(FIELDS.values())


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


def geo(state):
    parts = [p.strip() for p in state.split("/") if p.strip()]
    if not all(re.fullmatch(r"[A-Z]{2}", p) for p in parts):
        raise RuntimeError(f"a state not of two letters: {state!r}")
    return f"US-{parts[0]}" if len(parts) == 1 else ""   # the entities shape takes one code: a border dam keeps its states in state


def dams(frame, url, retrieved, vintage):
    unknown = [c for c in frame.columns if c not in FIELDS and c not in NAMED and c not in MONTHLY]
    missing = [c for c in list(FIELDS) + sorted(NAMED) if c not in frame.columns]
    if unknown or missing:
        raise RuntimeError(f"headings not as read: unknown {unknown}, missing {missing}")
    rows = []
    for _, r in frame.iterrows():
        nid = cell(r["nid_id1"])
        if not nid:
            continue
        row = {"entity_id": f"ornl_npd:{nid}", "entity_type": "project", "name": cell(r["dmname"]), "geo": geo(cell(r["state"])),
               "lat": number(r["lat"]), "lon": number(r["lon"]), "capacity_mw": number(r["mw"]), "status": "", "status_date": "",
               "operator": cell(r["owname"]), "source": SOURCE, "source_url": url, "retrieved_at": retrieved, "vintage": vintage}
        for k, v in FIELDS.items():
            row[v] = number(r[k]) if k in NUMBERS else cell(r[k])
        rows.append(row)
    t = pd.DataFrame(rows)
    if t.entity_id.duplicated().any():
        raise RuntimeError(f"a NID id given twice: {t.loc[t.entity_id.duplicated(), 'entity_id'].head(3).tolist()}")
    return t[ENTITY_COLS + EXTRA].sort_values("entity_id").reset_index(drop=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description="ORNL's hydropower potential at existing non-powered dams (greater than 1 MW)")
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
        retrieved, vintage = rec.get("retrieved_at") or "", ip.vintage_of(rec)
        frame = pd.read_excel(io.BytesIO(content), sheet_name="NPD", header=2, dtype=str)
        t = dams(frame, URL, retrieved, vintage)
        cap = pd.to_numeric(t.capacity_mw, errors="coerce")
        top = t.assign(c=cap).sort_values("c", ascending=False).head(3)
        header = [
            "Energy Research Warehouse (ERW): Oak Ridge National Laboratory, U.S. hydropower potential at existing non-powered dams greater than 1 MW (the 2012 national assessment) (session 938)",
            "Shape: entities (docs/datastandard.md v0). entity_id ornl_npd:<NID id>; entity_type project (a potential site at a dam); geo US-<state> "
            "(empty for a dam on a border: its states, as ORNL writes them, IL/KY, are in state); capacity_mw ORNL's potential capacity (the potential annual energy over a regional capacity factor); "
            "status empty (a potential, not a plan); operator the dam's owner; head_ft, flow_cfs (annual mean), potential_mwh_year, capacity_factor_pct, "
            "storage_acre_ft as ORNL estimates them.",
            f"{len(t)} dams, {cap.sum():,.0f} MW of potential in all; the largest: " + "; ".join(f"{r['name']} ({r.geo}, {r.c:,.0f} MW)" for _, r in top.iterrows())
            + ". Estimates from flows and heads not measured at the dams (ORNL's caution); the monthly flows and energies are not taken. Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/ornl_npd.py; the workbook retrieved {retrieved}, last modified {vintage}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Oak Ridge National Laboratory, HydroSource, U.S. Hydropower Potential from Existing Non-powered Dams (greater than 1MW), "
            f"NHAAP_NPD_FY11_1MW (B. Hadjerioua, Y. Wei and S.-C. Kao, 2012, DOE/EE-0711), {PAGE}",
            f"  access: {URL}",
            "License: HydroSource's Data Use Policy: data hosted on HydroSource is openly shared, without restriction, in accordance with the Department of "
            "Energy's Public Access Plan; cite the authors, title, publisher and DOI.",
        ]
        ip.write_snapshot(t, NAME, header, log, cols=ENTITY_COLS + EXTRA)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Oak Ridge National Laboratory (ORNL), HydroSource",
                                    report="U.S. Hydropower Potential from Existing Non-powered Dams (greater than 1MW)", report_url=PAGE,
                                    document_list=URL, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} dams"))
        print(f"{NAME}: {len(t)} dams, {cap.sum():,.0f} MW")
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
