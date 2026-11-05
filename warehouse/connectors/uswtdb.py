#!/usr/bin/env python3
"""USGS's U.S. Wind Turbine Database: every utility-scale land-based and offshore wind turbine in the United States
(session 496, a public source probed while the data lock was held).

Energy Research Warehouse (ERW) connector. One entities table, warehouse/output/uswtdb_wind_turbines.csv, from the U.S.
Wind Turbine Database (USWTDB) of the U.S. Geological Survey, Lawrence Berkeley National Laboratory and the American
Clean Power Association, through USGS's public API (no key):

    https://energy.usgs.gov/api/uswtdb/v1/turbines?limit=<n>&offset=<k>

    entity_id    uswtdb:<case_id>, the database's id of the turbine
    entity_type  generator; name the project's name (p_name) and the turbine's id; geo US-<state>; lat, lon ylat, xlong
    capacity_mw  the turbine's rated capacity (t_cap, kW) divided by 1,000
    status       empty: the database lists installed turbines and gives no status
    operator     empty (the database names no owner)
    the rest     the database's own fields, renamed with their units: the project's year, size and capacity, the maker
                 and model, hub height, rotor diameter, total height, the confidence flags, EIA's plant id, offshore

Values as USGS publishes them; a blank stays blank; a case_id given twice stops the run.

    python warehouse/connectors/uswtdb.py

Ceiling: 30 requests (pages of 10,000 turbines, 3 seconds apart). License: public (USGS: "USGS-authored or produced data
and information are considered to be in the U.S. Public Domain", record 87 of license_reads.csv; cite "U.S. Wind
Turbine Database, U.S. Geological Survey, Lawrence Berkeley National Laboratory and American Clean Power Association").
"""

import argparse
import datetime as dt
import json
import os
import sys
import time
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "uswtdb_wind_turbines"
CONNECTOR = "uswtdb"
SOURCE = "usgs:uswtdb"
API = "https://energy.usgs.gov/api/uswtdb/v1/turbines"
PAGE = "https://energywind.usgs.gov/uswtdb/"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
PER_PAGE, CEILING, PAUSE = 10_000, 30, 3
ENTITY_COLS = ["entity_id", "entity_type", "name", "geo", "lat", "lon", "capacity_mw", "status", "status_date", "operator",
               "source", "source_url", "retrieved_at", "vintage"]
FIELDS = {"case_id": "case_id", "eia_id": "eia_plant_id", "p_name": "project_name", "p_year": "project_year", "p_tnum": "project_turbines",
          "p_cap": "project_capacity_mw", "t_state": "state", "t_county": "county", "t_fips": "fips_county", "t_manu": "manufacturer",
          "t_model": "model", "t_cap": "turbine_capacity_kw", "t_hh": "hub_height_m", "t_rd": "rotor_diameter_m", "t_rsa": "rotor_swept_area_m2",
          "t_ttlh": "total_height_m", "t_conf_atr": "confidence_attributes", "t_conf_loc": "confidence_location", "t_img_date": "image_date",
          "t_img_src": "image_source", "t_retrofit": "retrofit", "t_retro_yr": "retrofit_year", "t_offshore": "offshore",
          "faa_ors": "faa_ors", "faa_asn": "faa_asn", "usgs_pr_id": "usgs_project_id"}
EXTRA_COLS = list(FIELDS.values())


def turbines(records, url, retrieved):
    d = pd.DataFrame(records)
    missing = [c for c in FIELDS if c not in d.columns] + [c for c in ("xlong", "ylat") if c not in d.columns]
    if missing:
        raise RuntimeError(f"the API's turbines lack {missing}")
    if d["case_id"].duplicated().any():
        raise RuntimeError(f"a case_id given twice: {sorted(d.loc[d['case_id'].duplicated(), 'case_id'])[:5]}")
    text = lambda c: d[c].where(d[c].notna(), "").astype(str).str.strip()  # noqa: E731
    out = pd.DataFrame({
        "entity_id": "uswtdb:" + d["case_id"].astype(int).astype(str), "entity_type": "generator",
        "name": text("p_name") + " turbine " + d["case_id"].astype(int).astype(str), "geo": "US-" + text("t_state"),
        "lat": pd.to_numeric(d["ylat"], errors="coerce"), "lon": pd.to_numeric(d["xlong"], errors="coerce"),
        "capacity_mw": pd.to_numeric(d["t_cap"], errors="coerce") / 1000.0, "status": "", "status_date": "", "operator": "",
        "source": SOURCE, "source_url": url, "retrieved_at": retrieved, "vintage": "",
    })
    for code, col in FIELDS.items():
        out[col] = d[code].map(lambda v: "" if v is None or (isinstance(v, float) and pd.isna(v)) else (str(int(v)) if isinstance(v, float) and v.is_integer() else str(v)))
    # the image date as the standard writes a date (YYYY-MM-DD); USGS writes M/D/YYYY. A date that does not parse stops the run
    raw = out["image_date"]
    iso = pd.to_datetime(raw.where(raw != ""), format="%m/%d/%Y", errors="coerce")
    bad = raw[(raw != "") & iso.isna()]
    if len(bad):
        raise RuntimeError(f"an image date that is not M/D/YYYY: {sorted(bad.unique())[:5]}")
    out["image_date"] = iso.dt.strftime("%Y-%m-%d").fillna("")
    return out.sort_values("entity_id").reset_index(drop=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description="USGS U.S. Wind Turbine Database: every utility-scale wind turbine")
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
        records, offset, asked = [], 0, 0
        retrieved = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        while True:
            if asked >= CEILING:
                raise RuntimeError(f"the ceiling of {CEILING} requests is reached at offset {offset:,}")
            asked += 1
            time.sleep(PAUSE)
            content, _ = ip.fetch_raw(CONNECTOR, f"{API}?limit={PER_PAGE}&offset={offset}", log, fresh=True, headers=UA, timeout=300)
            page = json.loads(content)
            records += page
            log(f"  offset {offset:,}: {len(page):,} turbines")
            if len(page) < PER_PAGE:
                break
            offset += PER_PAGE
        t = turbines(records, API, retrieved)
        header = [
            "Energy Research Warehouse (ERW): USGS U.S. Wind Turbine Database, every utility-scale land-based and offshore wind turbine (session 496)",
            "Shape: entities (docs/datastandard.md v0). entity_id uswtdb:<case_id>; entity_type generator; capacity_mw the turbine's rated capacity; status empty (the database lists installed turbines); the database's own fields after, renamed with their units.",
            f"Turbines: {len(t):,}; capacity {t['capacity_mw'].sum():,.0f} MW; offshore {int((t['offshore'] == '1').sum()):,}; with an EIA plant id {int((t['eia_plant_id'] != '').sum()):,}. A blank stays blank; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/uswtdb.py; {asked} requests of {CEILING}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Geological Survey, Lawrence Berkeley National Laboratory and American Clean Power Association, U.S. Wind Turbine Database (API v1), {PAGE}",
            f"  access: {API}?limit={PER_PAGE}&offset=<k>",
            'License: public (USGS data are in the U.S. public domain; cite "U.S. Wind Turbine Database, USGS, LBNL and ACP").',
        ]
        ip.write_snapshot(t, NAME, header, log, cols=ENTITY_COLS + EXTRA_COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Geological Survey (USGS), with LBNL and ACP",
                                    report="U.S. Wind Turbine Database (API v1)", report_url=PAGE, document_list=API, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t):,} turbines"))
        print(f"{NAME}: {len(t):,} turbines, {t['capacity_mw'].sum():,.0f} MW; {asked} requests")
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
