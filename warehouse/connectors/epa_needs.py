#!/usr/bin/env python3
"""EPA's National Electric Energy Data System (NEEDS) for its 2025 reference case: every generating unit EPA's power
sector model (IPM) starts from, with its capacity, heat rate, fuels, emission controls and IPM region, and the units EPA
retires by 2028, hard-wires into the model or drops from it (session 2183, chain 097: the fleet as EPA's regulatory
modelling sees it, beside EIA's inventory).

Energy Research Warehouse (ERW) connector. One entities table from EPA's workbook, linked from its NEEDS page:

    https://www.epa.gov/power-sector-modeling/national-electric-energy-data-system-needs
    https://www.epa.gov/system/files/documents/2025-12/needs-for-2025-reference-case.xlsx

    epa_needs_units   entity_id epa_needs:<EPA's UniqueID_Final (ORIS plant code, unit kind and unit id)>; entity_type
               generator (EPA's G, its one I, a 1,000 MW import into California, and C, a committed unit, of which this workbook has
               none) or equipment (B, a boiler; Decision 54); name the plant and unit; geo US-<state>
               (from EPA's state name, checked against its FIPS code where given); capacity_mw EPA's Capacity (MW), blank
               where EPA gives none (counted); status active for a unit of the
               NEEDS_Active sheet, else blank (Decision 20: the source's own status stays in its own column); x_needs_sheet
               the sheet (active, retired_by_2028, hardwired_capacity, dropped_capacity); x_ columns EPA's ORIS code, unit
               kind and id, CAMD unit id, plant type, IPM region, county and FIPS, heat rate (Btu/kWh), on-line and
               retirement year (EPA's 9999, no retirement, written blank), firing, bottom, cogeneration, modeled fuels,
               scrubber, NOx, PM and mercury controls, SO2 permit rate and mode 1 NOx rate (lb/MMBtu), CCS, coal to gas,
               BART, owner and share, holding company and share, regulatory status, and the reason a dropped unit was
               dropped

The four sheets must hold the 36 columns read (with EPA's reasons in the dropped sheet), or the run stops; so does a unit id given twice in any sheet or across sheets, a unit kind not in the map,
a state not in the map or unlike its code, or a capacity that does not read. Nothing is filled. The workbook's address names its
version; a later reference case is a new address, read from the page by a later session.

    python warehouse/connectors/epa_needs.py [--offline] [--out-dir DIR]

Ceiling: one request (the workbook, asked again unless --offline). www.epa.gov's robots file disallows its admin,
search, user, core and theme paths, not /power-sector-modeling/ or /system/files/. License: public (EPA, read 55; see
license_verdicts.csv).
"""

import argparse
import datetime as dt
import io
import os
import sys
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

CONNECTOR = "epa_needs"
SOURCE = "epa:needs_2025_reference_case"
HOST = "www.epa.gov"
PAGE = "https://www.epa.gov/power-sector-modeling/national-electric-energy-data-system-needs"
URL = "https://www.epa.gov/system/files/documents/2025-12/needs-for-2025-reference-case.xlsx"
TABLE = "epa_needs_units"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
SHEETS = {"NEEDS_Active": "active", "NEEDS_Retiredby2028": "retired_by_2028", "NEEDS_HardwiredCapMW": "hardwired_capacity",
          "NEEDS_DroppedCapMW": "dropped_capacity"}
KINDS = {"G": "generator", "I": "generator", "C": "generator", "B": "equipment"}
FIPS = {1: "AL", 2: "AK", 4: "AZ", 5: "AR", 6: "CA", 8: "CO", 9: "CT", 10: "DE", 11: "DC", 12: "FL", 13: "GA", 15: "HI", 16: "ID",
        17: "IL", 18: "IN", 19: "IA", 20: "KS", 21: "KY", 22: "LA", 23: "ME", 24: "MD", 25: "MA", 26: "MI", 27: "MN", 28: "MS",
        29: "MO", 30: "MT", 31: "NE", 32: "NV", 33: "NH", 34: "NJ", 35: "NM", 36: "NY", 37: "NC", 38: "ND", 39: "OH", 40: "OK",
        41: "OR", 42: "PA", 44: "RI", 45: "SC", 46: "SD", 47: "TN", 48: "TX", 49: "UT", 50: "VT", 51: "VA", 53: "WA", 54: "WV",
        55: "WI", 56: "WY", 72: "PR"}
STATES = {"Alabama": 1, "Alaska": 2, "Arizona": 4, "Arkansas": 5, "California": 6, "Colorado": 8, "Connecticut": 9, "Delaware": 10,
          "District of Columbia": 11, "Florida": 12, "Georgia": 13, "Hawaii": 15, "Idaho": 16, "Illinois": 17, "Indiana": 18, "Iowa": 19,
          "Kansas": 20, "Kentucky": 21, "Louisiana": 22, "Maine": 23, "Maryland": 24, "Massachusetts": 25, "Michigan": 26,
          "Minnesota": 27, "Mississippi": 28, "Missouri": 29, "Montana": 30, "Nebraska": 31, "Nevada": 32, "New Hampshire": 33,
          "New Jersey": 34, "New Mexico": 35, "New York": 36, "North Carolina": 37, "North Dakota": 38, "Ohio": 39, "Oklahoma": 40,
          "Oregon": 41, "Pennsylvania": 42, "Rhode Island": 44, "South Carolina": 45, "South Dakota": 46, "Tennessee": 47, "Texas": 48,
          "Utah": 49, "Vermont": 50, "Virginia": 51, "Washington": 53, "West Virginia": 54, "Wisconsin": 55, "Wyoming": 56,
          "Puerto Rico": 72}
X_MAP = {"x_unique_id": "UniqueID_Final", "x_oris": "ORIS Plant Code", "x_unit_kind": "Boiler/Generator/Committed Unit",
         "x_unit_id": "Unit ID", "x_camd_unit_id": "CAMD Database UnitID", "x_plant_type": "PlantType",
         "x_ct_ic": "Combustion Turbine/IC Engine", "x_ipm_region": "Region Name", "x_county": "County", "x_fips5": "FIPS5",
         "x_heat_rate_btu_kwh": "Heat Rate (Btu/kWh)", "x_online_year": "On Line Year", "x_retirement_year": "Retirement Year",
         "x_firing": "Firing", "x_bottom": "Bottom", "x_cogen": "Cogen?", "x_fuels": "Modeled Fuels", "x_scrubber": "Wet/DryScrubber",
         "x_nox_comb_control": "NOx Comb Control", "x_nox_post_comb_control": "NOx Post-Comb Control", "x_pm_control": "PM Control",
         "x_mercury_controls": "Mercury_Controls", "x_so2_permit_rate": "SO2 Permit Rate (lbs/mmBtu)",
         "x_nox_rate_mode1": "Mode 1 NOx Rate (lbs/mmBtu)", "x_ccs": "CCS", "x_c2g": "C2G", "x_bart": "BART Affected Unit",
         "x_owner": "Owner Name", "x_owner_percent": "Owner Percent", "x_holding_company": "Holding Company",
         "x_holding_company_percent": "Holding Company Percent", "x_regulatory_status": "Regulatory Status"}
ENTITY_COLS = ["entity_id", "entity_type", "name", "geo", "lat", "lon", "capacity_mw", "status", "status_date", "operator",
               "source", "source_url", "retrieved_at", "vintage"]
DROP_REASON = "Reasons for Dropping the Unit from NEEDS"
X_COLS = ["x_needs_sheet"] + list(X_MAP) + ["x_drop_reason"]


def text(x):
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return ""
    if isinstance(x, float) and x.is_integer():
        return str(int(x))
    return str(x).strip()


def parse(content, base, counts):
    xl = pd.ExcelFile(io.BytesIO(content))
    missing = [s for s in SHEETS if s not in xl.sheet_names]
    if missing:
        raise RuntimeError(f"sheets not in the workbook: {missing}")
    out, seen = [], set()
    for sheet, label in SHEETS.items():
        d = pd.read_excel(xl, sheet_name=sheet, dtype=object)
        need = list(X_MAP.values()) + ["Plant Name", "State Name", "State Code", "Capacity (MW)"] + ([DROP_REASON] if label == "dropped_capacity" else [])
        lack = [c for c in need if c not in d.columns]
        if lack:
            raise RuntimeError(f"{sheet}: columns not as read: {lack}")
        d = d[~d.isna().all(axis=1)]
        counts[label] = len(d)
        for i, r in d.iterrows():
            uid = text(r["UniqueID_Final"])
            if not uid or uid in seen:
                raise RuntimeError(f"{sheet} row {i}: a unit id blank or given twice: {uid!r}")
            seen.add(uid)
            kind = text(r["Boiler/Generator/Committed Unit"])
            if kind not in KINDS:
                raise RuntimeError(f"{sheet} row {i}: a unit kind not in the map: {kind!r}")
            name, code = text(r["State Name"]), text(r["State Code"])
            if name not in STATES or (code and int(code) != STATES[name]):
                raise RuntimeError(f"{sheet} row {i}: a state not in the map or unlike its code: {name!r} {code!r}")
            st = FIPS[STATES[name]]
            cap = text(r["Capacity (MW)"])
            if cap:
                try:
                    mw = float(cap)
                except ValueError:
                    raise RuntimeError(f"{sheet} row {i}: a capacity that does not read: {cap!r}")
            else:
                mw = ""
                counts["no capacity"] = counts.get("no capacity", 0) + 1
            row = dict(base, entity_id=f"epa_needs:{uid}", entity_type=KINDS[kind], name=f"{text(r['Plant Name'])} {text(r['Unit ID'])}".strip(),
                       geo=f"US-{st}", lat="", lon="", capacity_mw=mw, status="active" if label == "active" else "", status_date="", operator="",
                       x_needs_sheet=label, x_drop_reason=text(r[DROP_REASON]) if label == "dropped_capacity" else "")
            for k, c in X_MAP.items():
                row[k] = text(r[c])
            if row["x_retirement_year"] == "9999":
                row["x_retirement_year"] = ""
            out.append(row)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="EPA NEEDS, the 2025 reference case's generating units")
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
        counts = {}
        t = pd.DataFrame(parse(content, base, counts))
        cols = ENTITY_COLS + X_COLS
        t = t[cols].sort_values("entity_id").reset_index(drop=True)
        mw = pd.to_numeric(t.capacity_mw, errors="coerce").groupby(t.x_needs_sheet).sum().round(0).astype(int).to_dict()
        sheets = {k: v for k, v in counts.items() if k in SHEETS.values()}
        head = [
            f"Energy Research Warehouse (ERW): EPA, National Electric Energy Data System (NEEDS) for the 2025 reference case, {len(t):,} units "
            f"({', '.join(f'{k} {v:,}' for k, v in sheets.items())}; MW {', '.join(f'{k} {v:,}' for k, v in mw.items())}) (session 2183)",
            "Shape: entities (docs/datastandard.md v0). entity_id epa_needs:<UniqueID_Final>; entity_type generator or equipment (a boiler); "
            "geo US-<state>; capacity_mw EPA's; status active for the NEEDS_Active sheet, else blank; x_needs_sheet EPA's sheet (active, "
            "retired_by_2028, hardwired_capacity, dropped_capacity); x_ columns EPA's ORIS code, unit, plant type, IPM region, county, heat "
            "rate (Btu/kWh), on-line and retirement year (9999 written blank), fuels, controls, emission rates (lb/MMBtu), owners, regulatory "
            "status and a dropped unit's reason.",
            f"Every unit id once across the four sheets. Units with no capacity in EPA's file (capacity_mw blank): {counts.get('no capacity', 0)}. Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/epa_needs.py; the workbook retrieved {base['retrieved_at']}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Environmental Protection Agency, National Electric Energy Data System (NEEDS) for the 2025 Reference Case, {PAGE}",
            f"  access: {URL}",
            "License: public (EPA; see license_verdicts.csv). Cite the U.S. Environmental Protection Agency, NEEDS for the 2025 Reference Case.",
        ]
        ip.write_snapshot(t, TABLE, head, log, cols)
        results.append(dict(table=TABLE, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{TABLE}: {len(t):,} units; {counts}; MW {mw}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{TABLE} FAILED, no output file written:\n{tb}")
        print(f"{TABLE} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=TABLE, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Environmental Protection Agency (EPA)", report="National Electric Energy Data System (NEEDS) for the 2025 Reference Case",
                                    report_url=PAGE, document_list=PAGE, license="public", tables=[TABLE])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
