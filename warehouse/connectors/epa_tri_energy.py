#!/usr/bin/env python3
"""EPA's Toxics Release Inventory for the energy industries: each facility's releases of each chemical by year, for the
electric utilities, the petroleum refineries and products plants, the natural gas processing plants, the coal mines and
the petroleum bulk terminals (session 2121, chain 079: beside the greenhouse gases of epa_ghgrp_facility_emissions, the
toxic chemicals the same plants report).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/epa_tri_energy_releases_annual.csv, from
the TRI's basic data file of each reporting year on data.epa.gov (one form a facility and chemical, 122 columns):

    https://data.epa.gov/efservice/downloads/tri/mv_tri_basic_download/<year>_US/csv

Rows are kept where the form's "INDUSTRY SECTOR CODE" is one of SECTORS (EPA's TRI sectors, from the form's primary
NAICS code): 2211 Electric Utilities, 324 Petroleum, 211 Natural Gas Processing, 2121 Coal Mining, 4247 Petroleum Bulk
Terminals. Natural gas processing plants (NAICS 211130) report from reporting year 2022, when EPA added them to the
inventory; the few forms of earlier years are those of plants under another code. Three of the form's totals are taken, as EPA computes them:

    total_releases           "TOTAL RELEASES": on-site and off-site disposal or other releases
    on_site_release_total    "ON-SITE RELEASE TOTAL": to air (fugitive and stack), water, underground injection and land
    off_site_release_total   "OFF-SITE RELEASE TOTAL": transferred off site for disposal or release

    entity      tri:<TRIFD>:<TRI chemical id>:<document control number>, one form: a facility files a form a chemical,
                but some sites file several forms of one chemical in a year (one an establishment, or a refinery's and its
                terminal's under two NAICS codes: BP Whiting, Phillips 66 Ponca City), so the form's document control
                number keeps each as EPA published it; x_trifd and x_chemical_id group the forms, and no sum is made here.
                node the facility's name
    unit        lb, or g for dioxin and dioxin-like compounds (Decision 66), the unit EPA printed on the form; never
                converted or summed across units
    ts_utc      the reporting year's 1 January; freq P1Y; geo US-<state> (the facility's state, territories included)
    x_*         the TRIFD, the FRS id (EPA's Facility Registry Service, which epa_ghgrp_facility_emissions' x_frs_id
                also carries) and the chemical id, the chemical's name and CAS number, EPA's sector and its code, the primary NAICS code, the county, the
                latitude and longitude, the parent company (standardized), whether the chemical is a carcinogen, a PBT or a
                PFAS, the form type (R or A: a Form A reports no quantities, so its totals are as EPA printed them)

Values as published, zeros kept (a zero is what the form reports); a blank cell has no row; nothing is filled. A file
without the columns named here, a year not the file's, a value that is not a number, a unit not Pounds or Grams or a
form given twice stops the run. Each year's file is read in chunks.

    python warehouse/connectors/epa_tri_energy.py [--first-year 2015] [--last-year 2023] [--offline] [--out-dir DIR]

Ceiling: one request a year (nine for 2015 to 2023), each reused from warehouse/raw/epa_tri_energy/. data.epa.gov's
robots file holds no rules (session 2121). License: public (EPA, record 55 of license_reads.csv; cite "U.S. EPA, Toxics
Release Inventory, basic data files, reporting year <year>").
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

NAME = "epa_tri_energy_releases_annual"
CONNECTOR = "epa_tri_energy"
SOURCE = "epa:tri_basic"
PAGE = "https://www.epa.gov/toxics-release-inventory-tri-program/tri-basic-data-files-calendar-years-1987-present"
URL = "https://data.epa.gov/efservice/downloads/tri/mv_tri_basic_download/{year}_US/csv"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
SECTORS = {"2211": "Electric Utilities", "324": "Petroleum", "211": "Natural Gas Processing", "2121": "Coal Mining",
           "4247": "Petroleum Bulk Terminals"}
MEASURES = {"107. TOTAL RELEASES": "total_releases", "65. ON-SITE RELEASE TOTAL": "on_site_release_total",
            "88. OFF-SITE RELEASE TOTAL": "off_site_release_total"}
UNITS = {"Pounds": "lb", "Grams": "g"}
KEEP = {"1. YEAR": "year", "2. TRIFD": "trifd", "36. DOC_CTRL_NUM": "doc", "3. FRS ID": "frs", "4. FACILITY NAME": "name", "7. COUNTY": "county", "8. ST": "st",
        "12. LATITUDE": "lat", "13. LONGITUDE": "lon", "17. STANDARD PARENT CO NAME": "parent",
        "22. INDUSTRY SECTOR CODE": "sector_code", "23. INDUSTRY SECTOR": "sector", "30. PRIMARY NAICS": "naics",
        "37. CHEMICAL": "chemical", "39. TRI CHEMICAL/COMPOUND ID": "chem_id", "40. CAS#": "cas",
        "46. CARCINOGEN": "carcinogen", "47. PBT": "pbt", "48. PFAS": "pfas", "49. FORM TYPE": "form",
        "50. UNIT OF MEASURE": "unit", **{k: k for k in MEASURES}}
COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "market", "node", "source", "source_url",
        "retrieved_at", "vintage", "x_trifd", "x_frs_id", "x_chemical_id", "x_chemical", "x_cas", "x_sector", "x_sector_code", "x_naics", "x_county", "x_latitude",
        "x_longitude", "x_parent", "x_carcinogen", "x_pbt", "x_pfas", "x_form_type"]


def text(v):
    return re.sub(r"\s+", " ", str(v or "")).strip()


def year_rows(content, year, url, retrieved, vintage, chunksize=20000):
    """One year's file, read in chunks: the energy sectors' forms as rows of COLS."""
    out = []
    reader = pd.read_csv(io.BytesIO(content), dtype=str, keep_default_na=False, chunksize=chunksize, encoding="utf-8",
                         encoding_errors="replace")
    for chunk in reader:
        missing = [c for c in KEEP if c not in chunk.columns]
        if missing:
            raise RuntimeError(f"{url}: no column {missing[:3]}")
        c = chunk[list(KEEP)].rename(columns=KEEP)
        c = c[c.sector_code.map(text).isin(SECTORS)]
        for r in c.to_dict("records"):
            if text(r["year"]) != str(year):
                raise RuntimeError(f"{url}: a form of year {r['year']!r}")
            unit = UNITS.get(text(r["unit"]))
            if unit is None:
                raise RuntimeError(f"{url}: a unit not Pounds or Grams: {r['unit']!r}")
            st = text(r["st"])
            base = {"ts_utc": f"{year}-01-01T00:00:00Z", "unit": unit, "freq": "P1Y", "geo": f"US-{st}" if st else "",
                    "market": "", "node": text(r["name"]), "source": SOURCE, "source_url": url, "retrieved_at": retrieved,
                    "vintage": vintage, "x_trifd": text(r["trifd"]), "x_frs_id": text(r["frs"]), "x_chemical_id": text(r["chem_id"]),
                    "x_chemical": text(r["chemical"]), "x_cas": text(r["cas"]),
                    "x_sector": text(r["sector"]), "x_sector_code": text(r["sector_code"]), "x_naics": text(r["naics"]),
                    "x_county": text(r["county"]), "x_latitude": text(r["lat"]), "x_longitude": text(r["lon"]),
                    "x_parent": text(r["parent"]), "x_carcinogen": text(r["carcinogen"]), "x_pbt": text(r["pbt"]),
                    "x_pfas": text(r["pfas"]), "x_form_type": text(r["form"])}
            entity = f"tri:{text(r['trifd'])}:{text(r['chem_id'])}:{text(r['doc'])}"
            for col, var in MEASURES.items():
                v = text(r[col])
                if v == "":
                    continue
                try:
                    value = float(v.replace(",", ""))
                except ValueError:
                    raise RuntimeError(f"{entity} {year}: {var} not a number: {v!r}")
                out.append({"entity": entity, "variable": var, "value": value, **base})
    return out


def build(files):
    """files: [(year, content, url, retrieved, vintage)]."""
    rows = []
    for year, content, url, retrieved, vintage in files:
        rows += year_rows(content, year, url, retrieved, vintage)
    return finish(rows)


def finish(rows):
    t = pd.DataFrame(rows, columns=COLS)
    twice = t[t.duplicated(["entity", "variable", "ts_utc"], keep=False)]
    if len(twice):
        raise RuntimeError(f"a form given twice: {twice.entity.iloc[0]} {twice.ts_utc.iloc[0]}")
    return t.sort_values(["ts_utc", "entity", "variable"]).reset_index(drop=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description="EPA TRI: the energy industries' releases by facility, chemical and year")
    ap.add_argument("--first-year", type=int, default=2015)
    ap.add_argument("--last-year", type=int, default=2023)
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
        if not args.offline and (ip.paused("epa") or ip.paused_host("data.epa.gov")):
            raise RuntimeError("EPA is paused (warehouse/metadata/paused_sources.csv): not requested")
        rows, got = [], []
        for year in range(args.first_year, args.last_year + 1):
            url = URL.format(year=year)
            content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, headers=UA, timeout=900)
            rows += year_rows(content, year, url, rec.get("retrieved_at") or "", ip.vintage_of(rec))
            got.append((year, rec.get("retrieved_at") or "", ip.vintage_of(rec)))
            del content
        t = finish(rows)
        forms = t[t.variable == "total_releases"]
        by = forms.groupby("x_sector").agg(facilities=("x_trifd", "nunique"), forms=("entity", "size"))
        header = [
            f"Energy Research Warehouse (ERW): U.S. EPA, Toxics Release Inventory, basic data files, reporting years {args.first_year} to {args.last_year}: the energy industries' releases by facility, chemical and year (session 2121)",
            "Shape: series (docs/datastandard.md v0). entity tri:<TRIFD>:<TRI chemical id>:<document control number>, one form (x_trifd and x_chemical_id group a site's forms of a chemical; no sum is made); variable total_releases, on_site_release_total or off_site_release_total, EPA's totals of the form; "
            "unit lb, or g for dioxins (Decision 66), as printed, never converted or summed across units; ts_utc the year's 1 January; freq P1Y; node the facility's name.",
            f"{len(t)} rows, {len(forms)} forms: " + "; ".join(f"{s} {r.forms} forms ({r.facilities} facilities)" for s, r in by.iterrows())
            + ". Sectors by EPA's TRI industry sector code: 2211, 324, 211, 2121, 4247; natural gas processing plants report from 2022, when EPA added them. Zeros kept as reported; a blank cell has no row; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/epa_tri_energy.py; the files retrieved "
            + "; ".join(f"{y} {r}" + (f" (last modified {v})" if v else "") for y, r, v in got),
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Environmental Protection Agency, Toxics Release Inventory (TRI) Program, TRI Basic Data Files, {PAGE}",
            f"  access: {URL}",
            f"License: public (a work of the U.S. government). Cite: U.S. EPA, Toxics Release Inventory, basic data files, reporting years {args.first_year} to {args.last_year}.",
        ]
        ip.write_csv(t, NAME, header, log, cols=COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Environmental Protection Agency (EPA)",
                                    report="Toxics Release Inventory (TRI) basic data files, US, by reporting year",
                                    report_url=PAGE, document_list=URL, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows, {len(forms)} forms, {args.first_year} to {args.last_year}")
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
