#!/usr/bin/env python3
"""USGS's U.S. Large-Scale Solar Photovoltaic Database: the large-scale solar facilities of the United States as the
database selects them (most ground-mounted and of 1 MW AC or more; it also holds some under 1 MW AC that are 1 MW DC or
more, and some rooftop, canopy and floating ones, counted in the header), each outline's place, capacity and design
(session 890, chain 048: the solar sibling of the U.S. Wind Turbine Database, uswtdb.py; session 891 corrected the
scope, which the first header gave as "every ground-mounted facility of 1 MW (AC) and more").

Energy Research Warehouse (ERW) connector. One entities table, warehouse/output/uspvdb_solar_facilities.csv, from the
U.S. Large-Scale Solar Photovoltaic Database (USPVDB) of the U.S. Geological Survey and Lawrence Berkeley National
Laboratory, through USGS's public API (no key):

    https://energy.usgs.gov/api/uspvdb/v1/projects?limit=<n>&offset=<k>

    entity_id    uspvdb:<case_id>, the database's id of the facility
    entity_type  plant; name the facility's name (p_name); geo US-<state>; lat, lon ylat, xlong (the outline's centroid)
    capacity_mw  the facility's AC capacity (p_cap_ac, MW); its DC capacity is in capacity_dc_mw
    status       empty: the database lists facilities in operation and gives no status
    operator     empty (the database names no owner)
    the rest     the database's own fields, renamed with their units: EIA's plant id, the year of operation, the outline's
                 area (square meters), the technology, tracking, azimuth and tilt, a battery, agrivoltaics, the site and
                 system type, the image date and the digitizing confidence

Values as USGS publishes them; a blank stays blank; a case_id given twice stops the run. The image date is written as a
date where USGS's YYYYMMDD is one, and kept as given in image_date_usgs; a value that is no calendar date (USGS gives
20240231) leaves image_date empty and is named in the header; a value not of eight digits stops the run.

    python warehouse/connectors/uspvdb.py [--offline]

Ceiling: 10 requests (pages of 10,000 facilities, 3 seconds apart). The host has no robots file (HTTP 404, session 890).
License: public (USGS: "USGS-authored or produced data and information are considered to be in the U.S. Public Domain",
record 87 of license_reads.csv; cite "U.S. Large-Scale Solar Photovoltaic Database, U.S. Geological Survey and Lawrence
Berkeley National Laboratory").
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

NAME = "uspvdb_solar_facilities"
CONNECTOR = "uspvdb"
SOURCE = "usgs:uspvdb"
API = "https://energy.usgs.gov/api/uspvdb/v1/projects"
PAGE = "https://energy.usgs.gov/uspvdb/"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
PER_PAGE, CEILING, PAUSE = 10_000, 10, 3
ENTITY_COLS = ["entity_id", "entity_type", "name", "geo", "lat", "lon", "capacity_mw", "status", "status_date", "operator",
               "source", "source_url", "retrieved_at", "vintage"]
FIELDS = {"case_id": "case_id", "eia_id": "eia_plant_id", "p_name": "project_name", "p_year": "project_year", "p_state": "state",
          "p_county": "county", "p_pwr_reg": "power_region", "p_cap_ac": "capacity_ac_mw", "p_cap_dc": "capacity_dc_mw",
          "p_area": "area_m2", "p_tech_pri": "technology_primary", "p_tech_sec": "technology_secondary", "p_axis": "axis",
          "p_azimuth": "azimuth_deg", "p_tilt": "tilt_deg", "p_battery": "battery", "p_agrivolt": "agrivoltaic", "p_type": "site_type",
          "p_sys_type": "system_type", "p_img_date": "image_date", "p_dig_conf": "digitizing_confidence", "p_zscore": "zscore",
          "multi_poly": "multi_polygon", "p_comm": "comments"}
EXTRA_COLS = list(FIELDS.values()) + ["image_date_usgs"]


def cell(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return ""
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return str(v).strip()


def facilities(records, url, retrieved):
    d = pd.DataFrame(records)
    missing = [c for c in FIELDS if c not in d.columns] + [c for c in ("xlong", "ylat") if c not in d.columns]
    if missing:
        raise RuntimeError(f"the API's projects lack {missing}")
    if d["case_id"].duplicated().any():
        raise RuntimeError(f"a case_id given twice: {sorted(d.loc[d['case_id'].duplicated(), 'case_id'])[:5]}")
    ids = d["case_id"].astype(int).astype(str)
    out = pd.DataFrame({
        "entity_id": "uspvdb:" + ids, "entity_type": "plant", "name": d["p_name"].map(cell),
        "geo": "US-" + d["p_state"].map(cell), "lat": pd.to_numeric(d["ylat"], errors="coerce"),
        "lon": pd.to_numeric(d["xlong"], errors="coerce"), "capacity_mw": pd.to_numeric(d["p_cap_ac"], errors="coerce"),
        "status": "", "status_date": "", "operator": "", "source": SOURCE, "source_url": url, "retrieved_at": retrieved, "vintage": "",
    })
    for code, col in FIELDS.items():
        out[col] = d[code].map(cell)
    # the image date as the standard writes a date (YYYY-MM-DD); USGS writes YYYYMMDD, kept as given in image_date_usgs.
    # A value of eight digits that is no calendar date (USGS gives 20240231) is left empty in image_date, never mended,
    # and named in the header; anything else not eight digits stops the run
    raw = out["image_date"]
    out["image_date_usgs"] = raw
    if (raw[raw != ""].str.fullmatch(r"\d{8}") == False).any():  # noqa: E712
        raise RuntimeError(f"an image date that is not eight digits: {sorted(raw[(raw != '') & ~raw.str.fullmatch(r'[0-9]{8}')].unique())[:5]}")
    iso = pd.to_datetime(raw.where(raw != ""), format="%Y%m%d", errors="coerce")
    out["image_date"] = iso.dt.strftime("%Y-%m-%d").fillna("")
    out.attrs["no_date"] = sorted(raw[(raw != "") & iso.isna()].unique())
    t = out.sort_values("entity_id").reset_index(drop=True)
    t.attrs["no_date"] = out.attrs["no_date"]
    return t


def main(argv=None):
    ap = argparse.ArgumentParser(description="USGS U.S. Large-Scale Solar Photovoltaic Database")
    ap.add_argument("--offline", action="store_true", help="the saved pages only, no request")
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
            if not args.offline:
                time.sleep(PAUSE)
            content, rec = ip.fetch_raw(CONNECTOR, f"{API}?limit={PER_PAGE}&offset={offset}", log, offline=args.offline,
                                        fresh=not args.offline, headers=UA, timeout=300)
            if args.offline:
                retrieved = rec.get("retrieved_at") or retrieved
            page = json.loads(content)
            records += page
            log(f"  offset {offset:,}: {len(page):,} facilities")
            if len(page) < PER_PAGE:
                break
            offset += PER_PAGE
        t = facilities(records, API, retrieved)
        header = [
            "Energy Research Warehouse (ERW): USGS U.S. Large-Scale Solar Photovoltaic Database, the large-scale solar facilities as the database selects them (session 890)",
            "Shape: entities (docs/datastandard.md v0). entity_id uspvdb:<case_id>; entity_type plant; capacity_mw the facility's AC capacity (DC in capacity_dc_mw); "
            "lat, lon the outline's centroid; status empty (the database lists facilities in operation); the database's own fields after, renamed with their units.",
            f"Facilities: {len(t):,}; AC capacity {t['capacity_mw'].sum():,.0f} MW; with an EIA plant id {int((t['eia_plant_id'] != '').sum()):,}; "
            f"with a battery {int((t['battery'] != '').sum()):,}; under 1 MW AC {int((t['capacity_mw'] < 1).sum()):,}; with a system type that is not ground "
            f"(rooftop, canopy, floating) {int(((t['system_type'] != '') & ~t['system_type'].str.contains('ground')).sum()):,}. "
            "A blank stays blank; nothing is filled. image_date is USGS's image date as a date; "
            "image_date_usgs as USGS gives it (YYYYMMDD)"
            + (f"; given as no calendar date, so image_date left empty: {', '.join(t.attrs['no_date'])}." if t.attrs.get("no_date") else "."),
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/uspvdb.py; {asked} pages of {CEILING}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Geological Survey and Lawrence Berkeley National Laboratory, U.S. Large-Scale Solar Photovoltaic Database (API v1), {PAGE}",
            f"  access: {API}?limit={PER_PAGE}&offset=<k>",
            'License: public (USGS data are in the U.S. public domain; cite "U.S. Large-Scale Solar Photovoltaic Database, USGS and LBNL").',
        ]
        ip.write_snapshot(t, NAME, header, log, cols=ENTITY_COLS + EXTRA_COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Geological Survey (USGS), with LBNL",
                                    report="U.S. Large-Scale Solar Photovoltaic Database (API v1)", report_url=PAGE, document_list=API,
                                    license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t):,} facilities"))
        print(f"{NAME}: {len(t):,} facilities, {t['capacity_mw'].sum():,.0f} MW AC; {asked} pages")
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
