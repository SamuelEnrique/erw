#!/usr/bin/env python3
"""Berkeley Lab's utility-scale solar projects: each project's place, technology, size, design, storage, offtaker, value,
cost and PPA price, and its capacity factor in each year from 2008 to 2024 (session 939, chain 053: the projects behind
lbnl_ppa_prices' solar contracts, from the same data file).

Energy Research Warehouse (ERW) connector. One entities table, warehouse/output/lbnl_solar_projects.csv, from the
"Individual_Project_Data" sheet of LBNL's Utility-Scale Solar, 2025 Data Update data file, the one lbnl_ppa_prices.py
saves (warehouse/raw/lbnl_ppa_prices/), read again from there:

    https://eta-publications.lbl.gov/sites/default/files/2025-10/2025_utility-scale_solar_data_update.xlsx

    entity_id    lbnl_solar:<EIA ID> as LBNL writes it (a suffix such as "ret", "a" or "b" kept); a project with no EIA id
                 lbnl_solar:none-<name as a slug>
    entity_type  plant; name the project's name; geo US-<state>; lat, lon; capacity_mw the AC capacity (MW-AC)
    status       empty (LBNL lists projects that reached commercial operation; its "ret" ids are named, not mapped)
    status_date  the solar commercial operation date
    the rest     LBNL's columns, renamed with their units: region, irradiance (GHI), technology and its sub-type, DC capacity,
                 inverter loading ratio, mount, tracking, tilt, azimuth, hybrid configuration, storage technology, coupling,
                 year, MW and MWh, 2024 energy and capacity value (USD/MWh), LCOE without and with federal tax credits (2024
                 USD/MWh), offtaker type, levelized PPA price (2024 USD/MWh), and the capacity factor of each year 2008 to 2024
                 (a fraction, as LBNL gives it)

Values as LBNL publishes them; a blank stays blank; nothing is filled. A heading not as read or an id given twice stops
the run.

    python warehouse/connectors/lbnl_solar_projects.py [--offline]

Ceiling: one request, and none while lbnl_ppa_prices' saved file is on the machine. License: CC BY 4.0, as the file's
copyright notice states ("This work is openly licensed via CC BY 4.0"); cite Berkeley Lab.
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

NAME = "lbnl_solar_projects"
CONNECTOR = "lbnl_solar_projects"
SAVED_BY = "lbnl_ppa_prices"
SOURCE = "lbnl:solar_projects"
PAGE = "https://eta-publications.lbl.gov/publications/us-utility-scale-solar-2025-data"
URL = "https://eta-publications.lbl.gov/sites/default/files/2025-10/2025_utility-scale_solar_data_update.xlsx"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
SHEET = "Individual_Project_Data"
ENTITY_COLS = ["entity_id", "entity_type", "name", "geo", "lat", "lon", "capacity_mw", "status", "status_date", "operator",
               "source", "source_url", "retrieved_at", "vintage"]
FIELDS = {"EIA ID": "eia_id", "Solar COD Year": "cod_year", "Region": "region", "State": "state", "Avg GHI": "ghi_kwh_m2_day",
          "Solar Tech Main": "technology", "Solar Tech Sub": "technology_sub", "Solar Capacity MW-DC": "capacity_dc_mw", "ILR": "ilr",
          "Mount": "mount", "Tracking Type": "tracking", "Tilt": "tilt", "Azimuth": "azimuth_deg", "Hybrid?": "hybrid",
          "Storage Tech": "storage_technology", "Storage Coupling": "storage_coupling", "Storage COD Year": "storage_cod_year",
          "Storage Capacity MW": "storage_mw", "Storage Energy MWh": "storage_mwh", "2024 Energy Value ($/MWh)": "energy_value_2024_usd_mwh",
          "2024 Capacity Value ($/MWh)": "capacity_value_2024_usd_mwh", "PV LCOE no Tax Credits (2024$/MWh)": "lcoe_no_credits_2024_usd_mwh",
          "PV LCOE with Federal Tax Credits (2024$/MWh)": "lcoe_with_credits_2024_usd_mwh", "Offtaker Type": "offtaker",
          "Levelized PV PPA 2024$/MWh": "ppa_2024_usd_mwh"}
CF_YEARS = list(range(2008, 2025))
NAMED = {"Project Name", "Solar COD", "Latitude", "Longitude", "Solar Capacity MW-AC"} | {f"{y} Capacity Factor" for y in CF_YEARS}
NUMBERS = {"Avg GHI", "Solar Capacity MW-DC", "ILR", "Azimuth", "Storage Capacity MW", "Storage Energy MWh", "2024 Energy Value ($/MWh)",
           "2024 Capacity Value ($/MWh)", "PV LCOE no Tax Credits (2024$/MWh)", "PV LCOE with Federal Tax Credits (2024$/MWh)",
           "Levelized PV PPA 2024$/MWh"}
EXTRA = list(FIELDS.values()) + [f"cf_{y}" for y in CF_YEARS]


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


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def projects(frame, url, retrieved, vintage):
    unknown = [c for c in frame.columns if c not in FIELDS and c not in NAMED]
    missing = [c for c in list(FIELDS) + sorted(NAMED) if c not in frame.columns]
    if unknown or missing:
        raise RuntimeError(f"headings not as read: unknown {unknown}, missing {missing}")
    rows = []
    for _, r in frame.iterrows():
        name, eia = cell(r["Project Name"]), cell(r["EIA ID"])
        if not name and not eia:
            continue
        cod = pd.to_datetime(cell(r["Solar COD"]), errors="coerce")
        st = cell(r["State"])
        row = {"entity_id": f"lbnl_solar:{eia}" if eia else f"lbnl_solar:none-{slug(name)}", "entity_type": "plant", "name": name,
               "geo": f"US-{st}" if re.fullmatch(r"[A-Z]{2}", st) else "", "lat": number(r["Latitude"]), "lon": number(r["Longitude"]),
               "capacity_mw": number(r["Solar Capacity MW-AC"]), "status": "", "status_date": "" if pd.isna(cod) else cod.strftime("%Y-%m-%d"),
               "operator": "", "source": SOURCE, "source_url": url, "retrieved_at": retrieved, "vintage": vintage}
        for k, v in FIELDS.items():
            row[v] = number(r[k]) if k in NUMBERS else cell(r[k])
        for y in CF_YEARS:
            row[f"cf_{y}"] = number(r[f"{y} Capacity Factor"])
        rows.append(row)
    t = pd.DataFrame(rows)
    if t.entity_id.duplicated().any():
        raise RuntimeError(f"an id given twice: {t.loc[t.entity_id.duplicated(), 'entity_id'].head(3).tolist()}")
    return t[ENTITY_COLS + EXTRA].sort_values("entity_id").reset_index(drop=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Berkeley Lab's utility-scale solar projects (Individual_Project_Data)")
    ap.add_argument("--offline", action="store_true", help="the saved data file only, no request")
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
        hit = ip.raw_cached(SAVED_BY, URL) or ip.raw_cached(CONNECTOR, URL)
        if hit:
            content, rec = hit
            log(f"  saved file reused: {rec['file']}")
        else:
            content, rec = ip.fetch_raw(CONNECTOR, URL, log, offline=args.offline, headers=UA, timeout=600)
        if content[:2] != b"PK":
            raise RuntimeError(f"{URL} is not a workbook")
        retrieved, vintage = rec.get("retrieved_at") or "", ip.vintage_of(rec)
        t = projects(pd.read_excel(io.BytesIO(content), sheet_name=SHEET, dtype=str), URL, retrieved, vintage)
        cap = pd.to_numeric(t.capacity_mw, errors="coerce")
        tech = t.technology.value_counts().to_dict()
        hyb = int((t.hybrid != "").sum())
        header = [
            "Energy Research Warehouse (ERW): Berkeley Lab, utility-scale solar projects (Utility-Scale Solar, 2025 Data Update, Individual_Project_Data) (session 939)",
            "Shape: entities (docs/datastandard.md v0). entity_id lbnl_solar:<EIA ID as LBNL writes it, suffixes kept> (none-<name> where it gives none); "
            "entity_type plant; geo US-<state>; capacity_mw the AC capacity; status empty; status_date the solar commercial operation date; x columns "
            "LBNL's, renamed with units: values, LCOE and PPA in 2024 USD/MWh; cf_<year> the capacity factor (a fraction) of 2008 to 2024.",
            f"{len(t):,} projects ({', '.join(f'{v:,} {k}' for k, v in tech.items())}), {cap.sum():,.0f} MW-AC; {hyb} with a hybrid configuration. "
            "Values as LBNL publishes them; a blank stays blank; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/lbnl_solar_projects.py; the data file retrieved {retrieved}, last modified {vintage}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{SAVED_BY}/ (not in git; the file lbnl_ppa_prices.py saves)",
            f"Source: {SOURCE} Lawrence Berkeley National Laboratory, Utility-Scale Solar, 2025 Data Update (October 2025), {PAGE}",
            f"  access: {URL}",
            "License: CC BY 4.0, as the data file's copyright notice states (Copyright The Regents of the University of California, through Lawrence "
            "Berkeley National Laboratory); cite Berkeley Lab and the report.",
        ]
        ip.write_snapshot(t, NAME, header, log, cols=ENTITY_COLS + EXTRA)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Lawrence Berkeley National Laboratory (Berkeley Lab)",
                                    report="Utility-Scale Solar Data Update (Individual_Project_Data)", report_url=PAGE,
                                    document_list=URL, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t):,} projects"))
        print(f"{NAME}: {len(t):,} projects, {cap.sum():,.0f} MW-AC")
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
