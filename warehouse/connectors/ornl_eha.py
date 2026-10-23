#!/usr/bin/env python3
"""Oak Ridge National Laboratory's Existing Hydropower Assets (EHA) Plant Database: every U.S. hydropower and pumped
storage plant, with its place, owner, dam owner, FERC authorization, mode of operation, capacity, average generation,
first year of operation, waterway and grid (session 911, chain 051).

Energy Research Warehouse (ERW) connector. One entities table, warehouse/output/ornl_eha_hydropower_plants.csv, from the
EHA Plant Database, 2026 (HydroSource, ORNL; DOI 10.21951/EHA_FY2026/3374497), the workbook its landing page links:

    https://hydrosource.ornl.gov/data/datasets/eha-plant-2026/
    https://hydrosource.s3.us-east-2.amazonaws.com/files/data/datasets/EHA2026/ORNL_EHAHydroPlant_PublicFY2026.xlsx

    entity_id    ornl_eha:<EHA_PtID>, the database's id of the plant
    entity_type  plant; name PtName; geo US-<state>; lat, lon as the database gives them (NAD83)
    capacity_mw  the plant's hydro capacity and pumped storage capacity summed (HY_MW plus PSH_MW, each also in its column)
    status       empty: the database lists the plants in operation and gives no status
    operator     empty: the database names the plant's owner (plant_owner) and the dam's owner, not an operator
    the rest     the database's own fields, renamed with their units (the workbook's "Field Descriptions" sheet): the EIA
                 plant id, county and FIPS code, owner type, plant type (HY, PSH, HY/PSH), the FERC docket and its
                 authorization's issue and expiry dates, the mode of operation and permitting agency, the number of units,
                 hydro and pumped storage capacity (MW), average annual generation since 2002 or the FERC authorization's
                 estimate (MWh: net for hydro, gross for pumped storage), capacity factor (percent) and first year of
                 operation, the waterway, the hydrologic unit code, the NERC region, the balancing authority, EIA's sector
                 and the transmission or distribution system owner

Values as ORNL publishes them; a blank stays blank; nothing is filled. A heading not in the map or an EHA_PtID given
twice stops the run; an EIA plant id shared by two plants is kept and counted in the header.

    python warehouse/connectors/ornl_eha.py [--offline]

Ceiling: one request (the workbook, saved in warehouse/raw/ornl_eha/ and reused offline). HydroSource's robots file
allows the landing page (it disallows /wp-admin/ and asks a crawl delay of 10 s); the workbook's S3 host has no robots
file (HTTP 403, session 911). License: "Data hosted on HydroSource is openly shared, without restriction, in accordance
with Department of Energy's Public Access Plan", with a citation of the authors, title, publisher and DOI (HydroSource's
Data Use Policy, read by session 911).
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

NAME = "ornl_eha_hydropower_plants"
CONNECTOR = "ornl_eha"
SOURCE = "ornl:eha_plant"
PAGE = "https://hydrosource.ornl.gov/data/datasets/eha-plant-2026/"
URL = "https://hydrosource.s3.us-east-2.amazonaws.com/files/data/datasets/EHA2026/ORNL_EHAHydroPlant_PublicFY2026.xlsx"
DOI = "10.21951/EHA_FY2026/3374497"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
ENTITY_COLS = ["entity_id", "entity_type", "name", "geo", "lat", "lon", "capacity_mw", "status", "status_date", "operator",
               "source", "source_url", "retrieved_at", "vintage"]
FIELDS = {"EHA_PtID": "eha_plant_id", "EIA_PtID": "eia_plant_id", "State": "state", "County": "county", "FIPS_Census": "county_fips",
          "Pt_Own": "plant_owner", "OwType": "owner_type", "Dam_Own": "dam_owner", "Type": "plant_type", "FC_Dock": "ferc_docket",
          "FcIssue": "ferc_issued", "FcExpire": "ferc_expires", "Mode": "mode", "Pm_Type": "permitting", "Number_of_Units": "units",
          "HY_MW": "hy_mw", "HY_MWh": "hy_avg_mwh", "HY_Pf": "hy_capacity_factor_pct", "HY_OpYear": "hy_first_year",
          "PSH_MW": "psh_mw", "PSH_MWh": "psh_avg_mwh", "PSH_Pf": "psh_capacity_factor_pct", "PSH_OpYear": "psh_first_year",
          "Water": "waterway", "HUC12_All": "huc", "NERC": "nerc_region", "BACode": "balancing_authority", "Sector": "eia_sector",
          "Trans": "transmission_owner"}
NAMED = {"PtName", "Latitude", "Longitude"}
EXTRA_COLS = list(FIELDS.values())


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


def day(v):
    s = cell(v)
    if s == "":
        return ""
    d = pd.to_datetime(s, errors="coerce")
    if pd.isna(d):
        raise RuntimeError(f"not a date: {v!r}")
    return d.strftime("%Y-%m-%d")


def plants(frame, url, retrieved, vintage):
    unknown = [c for c in frame.columns if c not in FIELDS and c not in NAMED]
    missing = [c for c in list(FIELDS) + sorted(NAMED) if c not in frame.columns]
    if unknown or missing:
        raise RuntimeError(f"headings not as read: unknown {unknown}, missing {missing}")
    rows = []
    for _, r in frame.iterrows():
        pid = cell(r["EHA_PtID"])
        if not pid:
            raise RuntimeError("a plant without an EHA_PtID")
        hy, psh = number(r["HY_MW"]), number(r["PSH_MW"])
        cap = (hy or 0) + (psh or 0) if (hy != "" or psh != "") else ""
        row = {"entity_id": f"ornl_eha:{pid}", "entity_type": "plant", "name": cell(r["PtName"]),
               "geo": f"US-{cell(r['State'])}" if cell(r["State"]) else "", "lat": number(r["Latitude"]), "lon": number(r["Longitude"]),
               "capacity_mw": cap, "status": "", "status_date": "", "operator": "", "source": SOURCE, "source_url": url,
               "retrieved_at": retrieved, "vintage": vintage}
        for k, v in FIELDS.items():
            if k in ("FcIssue", "FcExpire"):
                row[v] = day(r[k])
            elif k in ("HY_MW", "HY_MWh", "HY_Pf", "PSH_MW", "PSH_MWh", "PSH_Pf", "Number_of_Units", "HY_OpYear", "PSH_OpYear"):
                row[v] = number(r[k])
            elif k == "EIA_PtID":
                n = number(r[k])
                row[v] = "" if n == "" else str(int(n))
            else:
                row[v] = cell(r[k])
        rows.append(row)
    t = pd.DataFrame(rows)
    if t["entity_id"].duplicated().any():
        raise RuntimeError(f"an EHA_PtID given twice: {t.loc[t.entity_id.duplicated(), 'entity_id'].head(3).tolist()}")
    return t.sort_values("entity_id").reset_index(drop=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description="ORNL's Existing Hydropower Assets Plant Database")
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
        t = plants(pd.read_excel(io.BytesIO(content), sheet_name="Data", dtype=str), URL, retrieved, vintage)
        kinds = t["plant_type"].value_counts().to_dict()
        shared = t.loc[t.eia_plant_id != "", "eia_plant_id"]
        shared = int(shared.duplicated(keep=False).sum())
        no_eia = int((t.eia_plant_id == "").sum())
        cap = pd.to_numeric(t["capacity_mw"], errors="coerce")
        header = [
            "Energy Research Warehouse (ERW): Oak Ridge National Laboratory, Existing Hydropower Assets (EHA) Plant Database, 2026: every U.S. hydropower and pumped storage plant (session 911)",
            "Shape: entities (docs/datastandard.md v0). entity_id ornl_eha:<EHA_PtID>; entity_type plant; geo US-<state>; lat, lon NAD83 as ORNL gives them; capacity_mw "
            "hy_mw plus psh_mw (the plant's conventional hydro and pumped storage capacity); status and operator empty (the database lists plants in operation and "
            "names owners, in plant_owner and dam_owner); hy_avg_mwh the average annual net hydro generation since 2002 (or the FERC authorization's estimate), "
            "psh_avg_mwh the same for gross pumped storage generation; *_capacity_factor_pct percent; *_first_year the year the first unit came online; "
            "ferc_issued and ferc_expires the latest FERC authorization's dates (exemptions and conduits do not expire); huc the hydrologic unit code as given.",
            f"{len(t):,} plants ({', '.join(f'{v:,} {k}' for k, v in kinds.items())}), {cap.sum():,.0f} MW in all; {no_eia:,} without an EIA plant id; "
            f"{shared} plants share an EIA plant id with another (kept as ORNL gives them). Values as published; a blank stays blank; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/ornl_eha.py; the workbook retrieved {retrieved}, last modified {vintage}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} M.M. Johnson, S.-C. Kao and R. Uria-Martinez, Existing Hydropower Assets (EHA) Plant Database, 2026, HydroSource, "
            f"Oak Ridge National Laboratory, Oak Ridge, Tennessee, DOI {DOI}, {PAGE}",
            f"  access: {URL}",
            "License: HydroSource's Data Use Policy: data hosted on HydroSource is openly shared, without restriction, in accordance with the Department of "
            "Energy's Public Access Plan; cite the authors, title, publisher and DOI.",
        ]
        ip.write_snapshot(t, NAME, header, log, cols=ENTITY_COLS + EXTRA_COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Oak Ridge National Laboratory (ORNL), HydroSource",
                                    report="Existing Hydropower Assets (EHA) Plant Database", report_url=PAGE,
                                    document_list=URL, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t):,} plants"))
        print(f"{NAME}: {len(t):,} plants, {cap.sum():,.0f} MW")
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
