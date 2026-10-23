#!/usr/bin/env python3
"""The Bureau of Land Management's renewable energy rights-of-way in California: each verified or preliminary solar
and wind right-of-way on public lands, with its serial number, case type, disposition, dates and acreage (session 955,
chain 054: the projects on federal land beside ONRR's royalties).

Energy Research Warehouse (ERW) connector. One entities table, warehouse/output/blm_ca_renewable_rows.csv, from BLM
California's feature service "BLM CA Renewable Energy Projects" (gis.blm.gov), its two layers, read without geometry:

    https://gis.blm.gov/caarcgis/rest/services/RenewableEnergy/BLM_CA_Renewable_Energy_Projects/FeatureServer
      0  BLM CA Verified Renewable Energy ROW        1  BLM CA Preliminary Renewable Energy ROW

    entity_id    blm_row:<BLM serial number, spaces removed>; entity_type project; name BLM's project name (the holder or
                 applicant, as BLM writes it); geo US-CA; capacity_mw empty (BLM gives none); status empty (BLM's
                 disposition, Authorized, Pending or Closed, is in x_disposition); status_date the effective date
    x_*          the layer (verified or preliminary), disposition, case type and its code, commodity, project type,
                 application, effective and expiration dates, expiration year, project and BLM acres, the data source,
                 BLM's remarks, and "in time" as BLM gives it

Dates are BLM's (epoch milliseconds, read as UTC days). A field not as read or a serial number given twice stops the run;
a blank stays blank; nothing is filled.

    python warehouse/connectors/blm_renewable.py [--offline]

Ceiling: two requests (the layers, saved in warehouse/raw/blm_renewable/ and reused offline). gis.blm.gov has no robots
file (HTTP 404). Terms: the service's notice: data "as is", BLM to be cited as the source, changes described, not
represented as approved by BLM.
"""

import argparse
import datetime as dt
import json
import os
import re
import sys
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "blm_ca_renewable_rows"
CONNECTOR = "blm_renewable"
SOURCE = "blm:ca_renewable_energy_projects"
SERVICE = "https://gis.blm.gov/caarcgis/rest/services/RenewableEnergy/BLM_CA_Renewable_Energy_Projects/FeatureServer"
LAYERS = {0: "verified", 1: "preliminary"}
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
ENTITY_COLS = ["entity_id", "entity_type", "name", "geo", "lat", "lon", "capacity_mw", "status", "status_date", "operator",
               "source", "source_url", "retrieved_at", "vintage"]
FIELDS = ["GlobalID", "Shape__Area", "Shape__Length", "OBJECTID", "ProjectName", "SerialNumber", "Disposition", "CaseTypeCode",
          "ApplicationDate", "CaseType", "Commodity", "ExpirationDate", "ExpirationYear", "EffectiveDate", "UpdateDate", "InTime",
          "ProjectAcres", "BLMAcres", "DataSource", "Remarks", "ProjectType"]
PLSS = ["Section", "Township", "Range", "Meridian"]
EXTRA = ["x_layer", "x_serial_number", "x_disposition", "x_case_type", "x_case_type_code", "x_commodity", "x_project_type",
         "x_application_date", "x_effective_date", "x_expiration_date", "x_expiration_year", "x_project_acres", "x_blm_acres",
         "x_data_source", "x_remarks", "x_in_time"]


def url_of(layer):
    return f"{SERVICE}/{layer}/query?where=1%3D1&outFields=*&returnGeometry=false&f=json"


def day(ms):
    if ms in (None, ""):
        return ""
    return dt.datetime.fromtimestamp(int(ms) / 1000, tz=dt.timezone.utc).strftime("%Y-%m-%d")


def cell(v):
    return "" if v is None else re.sub(r"\s+", " ", str(v)).strip()


def rows(layer, body, base):
    names = [f["name"] for f in body.get("fields", [])]
    if [n for n in names if n not in PLSS] != FIELDS:
        raise RuntimeError(f"layer {layer}: fields not as read: {names}")
    if body.get("exceededTransferLimit"):
        raise RuntimeError(f"layer {layer}: the service holds more records than one answer gives")
    out = []
    for f in body.get("features", []):
        a = f["attributes"]
        serial = cell(a["SerialNumber"])
        if not serial:
            raise RuntimeError(f"layer {layer}: a record without a serial number: {a.get('ProjectName')}")
        out.append(dict(base, entity_id=f"blm_row:{re.sub(r'[^A-Za-z0-9]', '', serial)}", entity_type="project", name=cell(a["ProjectName"]),
                        geo="US-CA", lat="", lon="", capacity_mw="", status="", status_date=day(a["EffectiveDate"]), operator="",
                        x_layer=LAYERS[layer], x_serial_number=serial, x_disposition=cell(a["Disposition"]), x_case_type=cell(a["CaseType"]),
                        x_case_type_code=cell(a["CaseTypeCode"]), x_commodity=cell(a["Commodity"]), x_project_type=cell(a["ProjectType"]),
                        x_application_date=day(a["ApplicationDate"]), x_effective_date=day(a["EffectiveDate"]),
                        x_expiration_date=day(a["ExpirationDate"]), x_expiration_year=cell(a["ExpirationYear"]),
                        x_project_acres=cell(a["ProjectAcres"]), x_blm_acres=cell(a["BLMAcres"]), x_data_source=cell(a["DataSource"]),
                        x_remarks=cell(a["Remarks"]), x_in_time=cell(a["InTime"])))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="BLM California's renewable energy rights-of-way")
    ap.add_argument("--offline", action="store_true", help="the saved answers only, no request")
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
        out, got = [], []
        for layer in LAYERS:
            content, rec = ip.fetch_raw(CONNECTOR, url_of(layer), log, offline=args.offline, headers=UA, timeout=120)
            base = dict(source=SOURCE, source_url=url_of(layer), retrieved_at=rec.get("retrieved_at") or "", vintage="")
            got.append(base["retrieved_at"])
            out += rows(layer, json.loads(content.decode("utf-8")), base)
        t = pd.DataFrame(out)
        if t.entity_id.duplicated().any():
            raise RuntimeError(f"a serial number given twice: {t.loc[t.entity_id.duplicated(), 'entity_id'].tolist()[:3]}")
        t = t[ENTITY_COLS + EXTRA].sort_values("entity_id").reset_index(drop=True)
        disp = t.x_disposition.value_counts().to_dict()
        kinds = t.x_case_type.value_counts().to_dict()
        header = [
            "Energy Research Warehouse (ERW): Bureau of Land Management, California's verified and preliminary renewable energy rights-of-way on public lands (BLM CA Renewable Energy Projects) (session 955)",
            "Shape: entities (docs/datastandard.md v0). entity_id blm_row:<BLM serial number>; entity_type project; name BLM's project name; geo US-CA; "
            "capacity_mw empty (BLM gives none); status empty (BLM's disposition in x_disposition); status_date the effective date; x_* BLM's fields.",
            f"{len(t)} rights-of-way ({', '.join(f'{v} {k}' for k, v in t.x_layer.value_counts().items())}); dispositions "
            f"{', '.join(f'{v} {k}' for k, v in disp.items())}; case types {', '.join(f'{v} {k}' for k, v in kinds.items())}. California only: "
            "BLM publishes no national layer of renewable projects that this session found. Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/blm_renewable.py; the layers retrieved {', '.join(sorted(set(got)))}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Department of the Interior, Bureau of Land Management, California State Office, BLM CA Renewable Energy Projects, {SERVICE}",
            f"  access: {url_of(0)}; {url_of(1)}",
            "License: the service's notice: data provided as is; cite BLM as the source; describe modifications; do not imply BLM approved changes.",
        ]
        ip.write_snapshot(t, NAME, header, log, cols=ENTITY_COLS + EXTRA)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Department of the Interior, Bureau of Land Management (BLM)",
                                    report="BLM CA Renewable Energy Projects (verified and preliminary renewable energy rights-of-way)",
                                    report_url=SERVICE, document_list=SERVICE, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rights-of-way"))
        print(f"{NAME}: {len(t)} rights-of-way {disp}")
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
