#!/usr/bin/env python3
"""Oak Ridge National Laboratory's U.S. Hydropower Relicensing and License Surrender data: every hydropower project in
FERC relicensing or license surrender, with its milestones, process, capacity before and after, settlement, planned
construction and turbine investment, and for a surrender whether its dam was removed and why (session 930, chain 052: the
fleet of ornl_eha_hydropower_plants as its licenses turn over).

Energy Research Warehouse (ERW) connector. One events table, warehouse/output/ornl_hydropower_relicensing.csv, from the
U.S. Hydropower Relicensing and License Surrender Data, 2026 (HydroSource, ORNL; DOI 10.21951/HMR_RelicenseSurrender/3031244),
sheets "Relicenses" and "Surrenders" of the workbook its landing page links:

    https://hydrosource.ornl.gov/data/datasets/us-hydropower-relicensing-and-license-surrender-data-2026/

    event_id     ornl_relicense:<FERC docket>:<relicense|surrender>, with -2 for a docket the sheet gives twice
    event_date   FERC's issuance (FcIssue) where given, else the application's date, else the notice of intent's;
                 x_date_kind says which
    event_type   hydro_relicense or hydro_license_surrender; parties the licensee; entity_ids ornl_eha:<EHA_PtID>, the
                 plant in ornl_eha_hydropower_plants, where ORNL gives one
    mw           the new license's capacity (relicense) or the surrendered project's (surrender); status ORNL's own (Issued
                 Relicense, Pending Relicense, Submitted NOI to Relicense, Issued Surrender and the rest) on 31 December 2025
    x_*          ORNL's other fields, renamed (the old capacity, the dates, the process ALP/TLP/ILP, the new mode, the
                 settlement, construction and turbine-generator flags, the dam's removal, the reason)

Values as ORNL publishes them; a blank stays blank; nothing is filled. A heading not in the map stops the run.

    python warehouse/connectors/ornl_hydro_relicensing.py [--offline]

Ceiling: one request (the workbook, saved in warehouse/raw/ornl_hydro_relicensing/ and reused offline). HydroSource's
robots file allows the landing page (crawl delay 10 s); the S3 host has no robots file (HTTP 403, session 911). License:
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

NAME = "ornl_hydropower_relicensing"
CONNECTOR = "ornl_hydro_relicensing"
SOURCE = "ornl:hydro_relicensing"
PAGE = "https://hydrosource.ornl.gov/data/datasets/us-hydropower-relicensing-and-license-surrender-data-2026/"
URL = ("https://hydrosource.s3.us-east-2.amazonaws.com/files/data/datasets/us-hydropower-relicensing-and-license-surrender-data-2026/"
       "ORNL_US_Hydropower_Relicensing_and_License_Surrender_2026.xlsx")
DOI = "10.21951/HMR_RelicenseSurrender/3031244"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
EVENT_COLS = ["event_id", "event_date", "event_type", "parties", "entity_ids", "mw", "price", "currency", "status",
              "source", "source_url", "retrieved_at"]
SHEETS = {"Relicenses": ("relicense", "hydro_relicense", "Capacity_new_MW"), "Surrenders": ("surrender", "hydro_license_surrender", "Capacity_old_MW")}
FIELDS = {"FERC_docket": "x_ferc_docket", "EHA_PtID": "x_eha_plant_id", "Project_name": "x_project_name", "Licensee_type": "x_licensee_type",
          "Waterway": "x_waterway", "Project_type": "x_project_type", "Latitude": "x_lat", "Longitude": "x_lon", "State": "x_state",
          "NOI_date": "x_noi_date", "Application_date": "x_application_date", "Proc_type": "x_process", "FcIssue": "x_ferc_issued",
          "FcExpire": "x_ferc_expires", "Mode_new": "x_mode_new", "Settlement": "x_settlement", "Construction": "x_construction",
          "T_G_investment": "x_turbine_generator_investment", "Capacity_new_MW": "x_capacity_new_mw", "Capacity_old_MW": "x_capacity_old_mw",
          "Dam_removal": "x_dam_removal", "Reason_category": "x_reason"}
NAMED = {"Project_licensee", "Status"}
DATES = {"NOI_date", "Application_date", "FcIssue", "FcExpire"}
X_COLS = ["x_record", "x_date_kind"] + list(FIELDS.values())


def text(v):
    return "" if v is None or (isinstance(v, float) and pd.isna(v)) else re.sub(r"\s+", " ", str(v)).strip()


def day(v):
    s = text(v)
    if not s:
        return ""
    d = pd.to_datetime(s, errors="coerce")
    if pd.isna(d):
        raise RuntimeError(f"not a date: {v!r}")
    return d.strftime("%Y-%m-%d")


def events(sheets, url, retrieved):
    out, seen = [], {}
    for sheet, frame in sheets.items():
        record, etype, cap_col = SHEETS[sheet]
        unknown = [c for c in frame.columns if c not in FIELDS and c not in NAMED]
        if unknown:
            raise RuntimeError(f"{sheet}: headings not in the map: {unknown}")
        for _, r in frame.iterrows():
            docket = text(r["FERC_docket"])
            if not docket:
                raise RuntimeError(f"{sheet}: a row without a FERC docket")
            key = f"{docket}:{record}"
            seen[key] = seen.get(key, 0) + 1
            row = {"event_id": f"ornl_relicense:{key}" + (f"-{seen[key]}" if seen[key] > 1 else ""), "event_type": etype,
                   "parties": text(r.get("Project_licensee")), "price": "", "currency": "", "status": text(r.get("Status")),
                   "source": SOURCE, "source_url": url, "retrieved_at": retrieved, "x_record": record}
            for k, v in FIELDS.items():
                row[v] = day(r[k]) if (k in DATES and k in frame.columns) else (text(r[k]) if k in frame.columns else "")
            for k, kind in (("x_ferc_issued", "ferc_issued"), ("x_application_date", "application"), ("x_noi_date", "notice_of_intent")):
                if row[k]:
                    row["event_date"], row["x_date_kind"] = row[k], kind
                    break
            else:
                raise RuntimeError(f"{sheet}: {docket} has no date")
            eha = row["x_eha_plant_id"]
            row["entity_ids"] = f"ornl_eha:{eha}" if eha else ""
            cap = pd.to_numeric(text(r.get(cap_col)), errors="coerce")
            row["mw"] = "" if pd.isna(cap) else float(cap)
            out.append(row)
    t = pd.DataFrame(out)
    return t[EVENT_COLS + X_COLS].sort_values(["event_type", "event_date", "event_id"]).reset_index(drop=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description="ORNL's U.S. hydropower relicensing and license surrender data")
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
        retrieved = rec.get("retrieved_at") or ""
        sheets = {s: pd.read_excel(io.BytesIO(content), sheet_name=s, dtype=str) for s in SHEETS}
        t = events(sheets, URL, retrieved)
        by = t.groupby(["event_type", "status"]).size()
        twice = int(t.event_id.str.contains(r"-\d+$").sum())
        header = [
            "Energy Research Warehouse (ERW): Oak Ridge National Laboratory, U.S. Hydropower Relicensing and License Surrender data, 2026: every project in FERC relicensing or surrender on 31 December 2025 (session 930)",
            "Shape: events (docs/datastandard.md v0). event_id ornl_relicense:<FERC docket>:<relicense|surrender>; event_date FERC's issuance, else the "
            "application's date, else the notice of intent's (x_date_kind); event_type hydro_relicense or hydro_license_surrender; parties the licensee; "
            "entity_ids ornl_eha:<EHA_PtID> where given; mw the new license's capacity (relicense) or the surrendered project's (surrender); status ORNL's own.",
            f"{len(t)} records: " + "; ".join(f"{s} {n}" for (e, s), n in by.items()) + f". {int((t.entity_ids != '').sum())} name an EHA plant. "
            + (f"{twice} docket given twice in a sheet, kept with -2. " if twice else "") + "Values as published; a blank stays blank; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/ornl_hydro_relicensing.py; the workbook retrieved {retrieved}, last modified {ip.vintage_of(rec)}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} M.M. Johnson and R. Uria-Martinez, U.S. Hydropower Relicensing and License Surrender Data and Metadata, 2026, HydroSource, "
            f"Oak Ridge National Laboratory, Oak Ridge, Tennessee, DOI {DOI}, {PAGE}",
            f"  access: {URL}",
            "License: HydroSource's Data Use Policy: data hosted on HydroSource is openly shared, without restriction, in accordance with the Department of "
            "Energy's Public Access Plan; cite the authors, title, publisher and DOI.",
        ]
        ip.write_snapshot(t, NAME, header, log, cols=EVENT_COLS + X_COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Oak Ridge National Laboratory (ORNL), HydroSource",
                                    report="U.S. Hydropower Relicensing and License Surrender Data", report_url=PAGE,
                                    document_list=URL, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} records"))
        print(f"{NAME}: {len(t)} records ({by.groupby(level=0).sum().to_dict()})")
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
