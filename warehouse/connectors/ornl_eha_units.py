#!/usr/bin/env python3
"""Oak Ridge National Laboratory's Existing Hydropower Assets (EHA) Unit Database: every hydropower and pumped storage
generating unit in the U.S., with its plant, capacity, first and refurbishment years, turbine type and maker, speed, head,
power, minimum load and start time (session 943, chain 053: the units of ornl_eha_hydropower_plants).

Energy Research Warehouse (ERW) connector. One entities table, warehouse/output/ornl_eha_hydropower_units.csv, from the EHA
Unit Database, 2026 (HydroSource, ORNL; DOI 10.21951/FY2026/3374522), the workbook its landing page links:

    https://hydrosource.ornl.gov/data/datasets/eha-unit-2026/

    entity_id    ornl_eha_unit:<EHA_PtGnID>, the database's id of the unit; entity_type generator
    name         "<plant name>, unit <EHA unit id>"; geo empty (the sheet gives a county FIPS code, not a state; the plant's
                 state is in ornl_eha_hydropower_plants, joined by eha_plant_id); lat, lon the plant's
    capacity_mw  the unit's capacity (MW); status and operator empty (the plant's owner is in plant_owner)
    the rest     the database's fields, renamed with their units: the EHA plant id, owner, type (HY or PSH), the EIA plant and
                 generator ids, the EHA and FERC ids, first year of operation and refurbishment year, turbine type and maker,
                 speed (rpm), rated head (ft), power (hp), minimum load (MW), start time from cold shutdown (as given: 10M,
                 2H), hydrologic unit code and county FIPS code

Values as ORNL publishes them; "Unknown" kept as given; a blank stays blank; nothing is filled. A heading not in the map
or a unit id given twice stops the run.

    python warehouse/connectors/ornl_eha_units.py [--offline]

Ceiling: one request (the workbook, saved in warehouse/raw/ornl_eha_units/ and reused offline). HydroSource's robots file
allows the landing page (crawl delay 10 s); the S3 host has no robots file. License: HydroSource's Data Use Policy, "openly
shared, without restriction", with a citation (license_verdicts.csv, session 914).
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

NAME = "ornl_eha_hydropower_units"
CONNECTOR = "ornl_eha_units"
SOURCE = "ornl:eha_unit"
PAGE = "https://hydrosource.ornl.gov/data/datasets/eha-unit-2026/"
URL = "https://hydrosource.s3.us-east-2.amazonaws.com/files/data/datasets/eha-unit-2026/ORNL_EHAHydroUnit_PublicFY2026.xlsx"
DOI = "10.21951/FY2026/3374522"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
ENTITY_COLS = ["entity_id", "entity_type", "name", "geo", "lat", "lon", "capacity_mw", "status", "status_date", "operator",
               "source", "source_url", "retrieved_at", "vintage"]
FIELDS = {"EHA_PtID": "eha_plant_id", "Pt_Own": "plant_owner", "Type": "unit_type", "EIA_PtID": "eia_plant_id", "EIA_GnID": "eia_generator_id",
          "EHA_GnID": "eha_unit_id", "FC_PtID": "ferc_plant_id", "OpYear": "first_year", "RhYear": "refurbished_year", "TbType": "turbine_type",
          "Maker": "turbine_maker", "Speed_rpm": "speed_rpm", "Head_ft": "head_ft", "Power_hp": "power_hp", "MinMW": "min_load_mw",
          "StTime": "start_time", "HUC12_All": "huc", "FIPS_Census": "county_fips"}
NAMED = {"EHA_PtGnID", "PtName", "Latitude", "Longitude", "MW"}
NUMBERS = {"Speed_rpm", "Head_ft", "Power_hp", "MinMW"}
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
    return s if pd.isna(x) else (int(x) if float(x).is_integer() else float(x))


def units(frame, url, retrieved, vintage):
    unknown = [c for c in frame.columns if c not in FIELDS and c not in NAMED]
    missing = [c for c in list(FIELDS) + sorted(NAMED) if c not in frame.columns]
    if unknown or missing:
        raise RuntimeError(f"headings not as read: unknown {unknown}, missing {missing}")
    rows = []
    for _, r in frame.iterrows():
        uid = cell(r["EHA_PtGnID"])
        if not uid:
            raise RuntimeError("a unit without an EHA_PtGnID")
        cap = number(r["MW"])
        row = {"entity_id": f"ornl_eha_unit:{uid}", "entity_type": "generator", "name": f"{cell(r['PtName'])}, unit {cell(r['EHA_GnID'])}",
               "geo": "", "lat": number(r["Latitude"]), "lon": number(r["Longitude"]), "capacity_mw": cap if not isinstance(cap, str) else "",
               "status": "", "status_date": "", "operator": "", "source": SOURCE, "source_url": url, "retrieved_at": retrieved, "vintage": vintage}
        for k, v in FIELDS.items():
            row[v] = number(r[k]) if k in NUMBERS else cell(r[k])
        rows.append(row)
    t = pd.DataFrame(rows)
    if t.entity_id.duplicated().any():
        raise RuntimeError(f"a unit id given twice: {t.loc[t.entity_id.duplicated(), 'entity_id'].head(3).tolist()}")
    return t[ENTITY_COLS + EXTRA].sort_values("entity_id").reset_index(drop=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description="ORNL's Existing Hydropower Assets Unit Database")
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
        t = units(pd.read_excel(io.BytesIO(content), sheet_name="Data", dtype=str), URL, retrieved, vintage)
        cap = pd.to_numeric(t.capacity_mw, errors="coerce")
        kinds = t.unit_type.value_counts().to_dict()
        header = [
            "Energy Research Warehouse (ERW): Oak Ridge National Laboratory, Existing Hydropower Assets (EHA) Unit Database, 2026: every U.S. hydropower and pumped storage unit (session 943)",
            "Shape: entities (docs/datastandard.md v0). entity_id ornl_eha_unit:<EHA_PtGnID>; entity_type generator; name '<plant>, unit <EHA unit id>'; "
            "geo empty (the plant's state is in ornl_eha_hydropower_plants, joined by eha_plant_id); capacity_mw the unit's; speed_rpm, head_ft, power_hp, "
            "min_load_mw as ORNL gives them; start_time as given (10M minutes, 2H hours).",
            f"{len(t):,} units ({', '.join(f'{v:,} {k}' for k, v in kinds.items())}), {cap.sum():,.0f} MW in {t.eha_plant_id.nunique():,} plants. "
            "'Unknown' kept as ORNL writes it; a blank stays blank; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/ornl_eha_units.py; the workbook retrieved {retrieved}, last modified {vintage}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} M.M. Johnson, S.-C. Kao and R. Uria-Martinez, Existing Hydropower Assets (EHA) Unit Database, 2026, HydroSource, Oak Ridge "
            f"National Laboratory, Oak Ridge, Tennessee, DOI {DOI}, {PAGE}",
            f"  access: {URL}",
            "License: HydroSource's Data Use Policy: data hosted on HydroSource is openly shared, without restriction, in accordance with the Department of "
            "Energy's Public Access Plan; cite the authors, title, publisher and DOI.",
        ]
        ip.write_snapshot(t, NAME, header, log, cols=ENTITY_COLS + EXTRA)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Oak Ridge National Laboratory (ORNL), HydroSource",
                                    report="Existing Hydropower Assets (EHA) Unit Database", report_url=PAGE,
                                    document_list=URL, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t):,} units"))
        print(f"{NAME}: {len(t):,} units, {cap.sum():,.0f} MW")
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
