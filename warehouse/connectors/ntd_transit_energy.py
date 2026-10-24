#!/usr/bin/env python3
"""The Federal Transit Administration's National Transit Database (NTD): the fuel and electricity each transit agency
used, by mode and type of service, a report year (session 2182, chain 097: the electricity and fuel that public
transit draws, beside the grids and fuel markets that supply it).

Energy Research Warehouse (ERW) connector. One series table from the FTA's dataset on DOT DataHub:

    https://data.transportation.gov/d/8ehq-7his   (2022 - 2025 NTD Annual Data - Fuel and Energy)
    https://data.transportation.gov/api/views/8ehq-7his/rows.csv?accessType=DOWNLOAD

    ntd_transit_energy_annual   entity ntd_mode:<NTD ID>:<mode code>:<type of service code>; variable diesel,
               gasoline, biodiesel and other_fuel (gal), lpg_gal_equivalent and cng_gal_equivalent (gal, the FTA's gallon
               equivalents), hydrogen (t, the FTA's kilograms divided by 1,000), electric_propulsion (MWh, electricity fed
               to vehicles by third rail or overhead wire) and electric_battery (MWh, electricity charged into vehicles'
               batteries), the FTA's kWh divided by 1,000; ts_utc the report year's first day; freq P1Y; geo US-<state>
               (the agency's headquarters); node the agency, mode and type of service as the FTA names them; x_ntd_id;
               x_agency; x_city; x_mode; x_tos (DO directly operated, PT purchased transportation, and the FTA's other
               codes); x_uza the urbanized area; x_mode_voms vehicles operated in maximum service; x_reporter_type;
               x_questionable yes where the FTA marks the figure Questionable

A blank cell has no row; a zero the FTA prints is kept. Miles and miles per gallon are not taken (no unit for a
distance in the standard; the ratios are the FTA's own arithmetic). The dataset's columns must be the 67 read on 24
October 2026, or the run stops; so does a key (NTD ID, mode, type of service, report year) given twice, a number that
does not read, a negative quantity, a state not two letters, or a Questionable column holding anything but blank or
Questionable for a quantity taken. Nothing is filled. Only Full Reporters report energy consumption (the FTA's
description); demand response taxi is not in the dataset, and non-dedicated fleets report energy but not miles.

    python warehouse/connectors/ntd_transit_energy.py [--offline] [--out-dir DIR]

Ceiling: one request (the CSV, asked again unless --offline, since the FTA revises it at the same address).
data.transportation.gov's robots file asks a crawl delay of 1 second and disallows browse and facet searches, OData and
login paths, not /api/views/. License: public (the dataset's record: Public Domain U.S. Government,
https://www.usa.gov/government-works; see license_verdicts.csv).
"""

import argparse
import csv
import datetime as dt
import io
import os
import re
import sys
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

CONNECTOR = "ntd_transit_energy"
SOURCE = "fta:ntd_fuel_energy"
HOST = "data.transportation.gov"
PAGE = "https://data.transportation.gov/d/8ehq-7his"
URL = "https://data.transportation.gov/api/views/8ehq-7his/rows.csv?accessType=DOWNLOAD"
TABLE = "ntd_transit_energy_annual"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
X_COLS = ["x_ntd_id", "x_agency", "x_city", "x_mode", "x_tos", "x_uza", "x_mode_voms", "x_reporter_type", "x_questionable"]
# variable, the FTA's column, its Questionable column, unit, divisor
TAKEN = [("diesel", "Diesel (gal)", "Diesel (gal) Questionable", "gal", 1),
         ("gasoline", "Gasoline (gal)", "Gasoline (gal) Questionable", "gal", 1),
         ("lpg_gal_equivalent", "Liquefied Petroleum Gas (gal equivalent)", "Liquefied Petroleum Gas (gal equivalent) Questionable", "gal", 1),
         ("cng_gal_equivalent", "Compressed Natural Gas (gal equivalent)", "Compressed Natural Gas (gal equivalent) Questionable", "gal", 1),
         ("biodiesel", "Bio-Diesel (gal)", "Bio-Diesel (gal) Questionable", "gal", 1),
         ("hydrogen", "Hydrogen (kg)", "Hydrogen (kg) Questionable", "t", 1000),
         ("other_fuel", "Other Fuel (gal/gal equivalent)", "Other Fuel (gal/gal equivalent) Questionable", "gal", 1),
         ("electric_propulsion", "Electric Propulsion (kWh)", "Electric Propulsion (kWh) Questionable", "MWh", 1000),
         ("electric_battery", "Electric Battery (kWh)", "Electric Battery (kWh) Questionable", "MWh", 1000)]
IDENT = ["Agency", "City", "State", "NTD ID", "Organization Type", "Reporter Type", "Report Year", "UACE Code", "UZA Name",
         "Primary UZA Population", "Agency VOMS", "Mode", "Mode Name", "TOS", "Mode VOMS"]
N_COLUMNS = 67


def number(s, where):
    s = s.strip().replace(",", "")
    try:
        v = float(s)
    except ValueError:
        raise RuntimeError(f"{where}: a number that does not read: {s!r}")
    if v < 0:
        raise RuntimeError(f"{where}: a negative quantity: {v}")
    return v


def parse(content, base):
    rows = list(csv.DictReader(io.StringIO(content.decode("utf-8-sig"))))
    if not rows:
        raise RuntimeError("no row")
    cols = list(rows[0].keys())
    need = IDENT + [c for _, c, q, _, _ in TAKEN] + [q for _, c, q, _, _ in TAKEN]
    if len(cols) != N_COLUMNS or [c for c in need if c not in cols]:
        raise RuntimeError(f"the columns are not the 67 read: {len(cols)}, missing {[c for c in need if c not in cols]}")
    out, seen = [], set()
    for i, r in enumerate(rows):
        key = (r["NTD ID"], r["Mode"], r["TOS"], r["Report Year"])
        if key in seen:
            raise RuntimeError(f"row {i}: {key} given twice")
        seen.add(key)
        if not re.fullmatch(r"\d{4}", r["Report Year"]) or not re.fullmatch(r"[A-Z]{2}", r["State"]) or not r["NTD ID"].strip():
            raise RuntimeError(f"row {i}: a year, state or NTD ID that does not read: {key} {r['State']!r}")
        ent = f"ntd_mode:{r['NTD ID'].strip()}:{r['Mode'].strip()}:{r['TOS'].strip()}"
        for var, col, qcol, unit, div in TAKEN:
            if not r[col].strip():
                continue
            q = r[qcol].strip()
            if q not in ("", "Questionable"):
                raise RuntimeError(f"row {i}: {qcol} holds {q!r}")
            out.append(dict(base, entity=ent, variable=var, ts_utc=f"{r['Report Year']}-01-01T00:00:00Z",
                            value=round(number(r[col], f"row {i} {col}") / div, 6), unit=unit, freq="P1Y", geo=f"US-{r['State']}",
                            market="", node=f"{r['Agency'].strip()}: {r['Mode Name'].strip()} ({r['TOS'].strip()})",
                            x_ntd_id=r["NTD ID"].strip(), x_agency=r["Agency"].strip(), x_city=r["City"].strip(), x_mode=r["Mode"].strip(),
                            x_tos=r["TOS"].strip(), x_uza=r["UZA Name"].strip(), x_mode_voms=r["Mode VOMS"].strip(),
                            x_reporter_type=r["Reporter Type"].strip(), x_questionable="yes" if q else ""))
    if not out:
        raise RuntimeError("no figure")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="FTA National Transit Database: fuel and energy used by transit, a report year")
    ap.add_argument("--offline", action="store_true", help="the saved file only, no request")
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
        if ip.paused(CONNECTOR) or ip.paused_host(HOST):
            raise RuntimeError(f"{HOST} is paused (warehouse/metadata/paused_sources.csv): no request made")
        content, rec = ip.fetch_raw(CONNECTOR, URL, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=180, pause=1)
        base = dict(source=SOURCE, source_url=URL, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
        s = pd.DataFrame(parse(content, base))
        cols = ip.SERIES_COLS + X_COLS
        s = s[cols].sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)
        head = [
            "Energy Research Warehouse (ERW): Federal Transit Administration, National Transit Database, fuel and energy used by each "
            f"agency, mode and type of service, report years {s.ts_utc.min()[:4]} to {s.ts_utc.max()[:4]}, {s.x_ntd_id.nunique()} agencies (session 2182)",
            "Shape: series (docs/datastandard.md v0). entity ntd_mode:<NTD ID>:<mode>:<type of service>; variable diesel, gasoline, biodiesel, "
            "other_fuel (gal), lpg_gal_equivalent, cng_gal_equivalent (gal equivalents as the FTA reports them), hydrogen (t: the FTA's kg / "
            "1,000), electric_propulsion, electric_battery (MWh: the FTA's kWh / 1,000); freq P1Y; ts_utc the report year's first day; geo "
            "US-<state of the agency's headquarters>; x_ columns the agency, city, mode, type of service, urbanized area, vehicles in maximum "
            "service, reporter type and x_questionable yes where the FTA marks the figure Questionable.",
            "A blank has no row; a zero the FTA prints is kept. Miles and miles per gallon are not taken. Only Full Reporters report energy "
            "(the FTA's description). Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/ntd_transit_energy.py; the file retrieved {base['retrieved_at']}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Federal Transit Administration, 2022 - 2025 NTD Annual Data - Fuel and Energy (DOT DataHub 8ehq-7his), {PAGE}",
            f"  access: {URL}",
            "License: public (Public Domain U.S. Government, https://www.usa.gov/government-works; see license_verdicts.csv). Cite the "
            "Federal Transit Administration, National Transit Database.",
        ]
        ip.write_snapshot(s, TABLE, head, log, cols)
        results.append(dict(table=TABLE, market="all", status="ok", detail=f"{len(s)} rows"))
        print(f"{TABLE}: {len(s):,} rows, {s.entity.nunique()} agency modes, {s.x_ntd_id.nunique()} agencies, years "
              f"{s.ts_utc.min()[:4]} to {s.ts_utc.max()[:4]}; questionable {(s.x_questionable == 'yes').sum()}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{TABLE} FAILED, no output file written:\n{tb}")
        print(f"{TABLE} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=TABLE, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Department of Transportation, Federal Transit Administration (FTA)",
                                    report="2022 - 2025 NTD Annual Data - Fuel and Energy", report_url=PAGE, document_list=PAGE,
                                    license="public", tables=[TABLE])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
