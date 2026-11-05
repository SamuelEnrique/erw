#!/usr/bin/env python3
"""The U.S. Army Corps of Engineers' National Inventory of Dams: every dam in the inventory, with its owner type,
purposes, place, river, type, height, length, year completed, storage, surface and drainage area, discharge and locks
(session 982, chain 055: the dams beside ornl_npd_potential's non-powered dams and ornl_eha_hydropower_plants).

Energy Research Warehouse (ERW) connector. One entities table, warehouse/output/usace_nid_dams.csv, from the inventory's
national download (one CSV, its first line the date the data were last updated):

    https://nid.sec.usace.army.mil/api/nation/csv

    entity_id    usace_nid:<Federal ID> (unique; the NID ID repeats for a dam's associated structures, kept in nid_id);
                 entity_type dam (Decision 57); name the dam's name; geo US-<state>; lat, lon; capacity_mw empty;
                 status empty; operator the owners' names
    the rest     the inventory's fields, renamed with their units: NID ID, owner types and the primary one, primary purpose
                 and purposes (hydroelectric among them), associated structure, county, river, primary dam type, NID
                 height (ft), dam length (ft), year completed, NID and normal storage (acre-ft), surface area (acres),
                 drainage area (sq mi), maximum discharge (cfs), number of locks, the source agency and the record's date

The inventory's inspection, condition, hazard and emergency planning fields are not taken: the ERW holds dams for the
energy they hold or could. A heading not as read or a Federal ID given twice stops the run; a blank stays blank; nothing
is filled.

    python warehouse/connectors/usace_nid.py [--offline]

Ceiling: one request (the CSV, 70 MB, saved in warehouse/raw/usace_nid/ and reused offline). nid.sec.usace.army.mil has
no robots file (HTTP 404). License: a work of the U.S. Army Corps of Engineers, a federal agency (license_verdicts.csv).
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

NAME = "usace_nid_dams"
CONNECTOR = "usace_nid"
SOURCE = "usace:nid"
PAGE = "https://nid.sec.usace.army.mil/"
URL = "https://nid.sec.usace.army.mil/api/nation/csv"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
ENTITY_COLS = ["entity_id", "entity_type", "name", "geo", "lat", "lon", "capacity_mw", "status", "status_date", "operator",
               "source", "source_url", "retrieved_at", "vintage"]
FIELDS = {"NID ID": "nid_id", "Owner Types": "owner_types", "Primary Owner Type": "primary_owner_type", "Primary Purpose": "primary_purpose",
          "Purposes": "purposes", "Is Associated Structure?": "associated_structure", "County": "county", "River or Stream Name": "river",
          "Primary Dam Type": "primary_dam_type", "NID Height (Ft)": "nid_height_ft", "Dam Length (Ft)": "dam_length_ft",
          "Year Completed": "year_completed", "NID Storage (Acre-Ft)": "nid_storage_acre_ft", "Normal Storage (Acre-Ft)": "normal_storage_acre_ft",
          "Surface Area (Acres)": "surface_area_acres", "Drainage Area (Sq Miles)": "drainage_area_sq_mi",
          "Max Discharge (Cubic Ft/Second)": "max_discharge_cfs", "Number of Locks": "locks_n", "Source Agency": "source_agency",
          "Data Last Updated": "record_updated"}
NAMED = ["Dam Name", "Federal ID", "Owner Names", "Latitude", "Longitude", "State"]
STATES = {"Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA", "Colorado": "CO", "Connecticut": "CT",
          "Delaware": "DE", "District of Columbia": "DC", "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL",
          "Indiana": "IN", "Iowa": "IA", "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
          "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS", "Missouri": "MO", "Montana": "MT", "Nebraska": "NE",
          "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY", "North Carolina": "NC",
          "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI",
          "South Carolina": "SC", "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT", "Virginia": "VA",
          "Washington": "WA", "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY", "Puerto Rico": "PR", "Guam": "GU",
          "Virgin Islands": "VI", "American Samoa": "AS", "Northern Mariana Islands": "MP"}
EXTRA = list(FIELDS.values()) + ["coordinate_given"]


def cell(v):
    return re.sub(r"\s+", " ", str(v)).strip()


def dams(frame, base):
    missing = [c for c in NAMED + list(FIELDS) if c not in frame.columns]
    if missing:
        raise RuntimeError(f"headings not as read: missing {missing}")
    states = set(frame["State"]) - set(STATES) - {""}
    if states:
        raise RuntimeError(f"a state not in the map: {sorted(states)}")
    t = pd.DataFrame({"entity_id": "usace_nid:" + frame["Federal ID"].map(cell), "entity_type": "dam", "name": frame["Dam Name"].map(cell),
                      "geo": frame["State"].map(lambda s: f"US-{STATES[s]}" if s in STATES else ""), "lat": frame["Latitude"].map(cell),
                      "lon": frame["Longitude"].map(cell), "capacity_mw": "", "status": "", "status_date": "",
                      "operator": frame["Owner Names"].map(cell), **base})
    for k, v in FIELDS.items():
        t[v] = frame[k].map(cell)
    # a dam with one coordinate of the two: the pair left empty, the one given kept as given (session 982: two dams)
    one = (t.lat == "") != (t.lon == "")
    t["coordinate_given"] = ""
    t.loc[one, "coordinate_given"] = "lat " + t.loc[one, "lat"] + "; lon " + t.loc[one, "lon"]
    t.loc[one, ["lat", "lon"]] = ""
    if (frame["Federal ID"].map(cell) == "").any():
        raise RuntimeError("a dam without a Federal ID")
    if t.entity_id.duplicated().any():
        raise RuntimeError(f"a Federal ID given twice: {t.loc[t.entity_id.duplicated(), 'entity_id'].head(3).tolist()}")
    return t[ENTITY_COLS + EXTRA].sort_values("entity_id").reset_index(drop=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description="The National Inventory of Dams")
    ap.add_argument("--offline", action="store_true", help="the saved CSV only, no request")
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
        content, rec = ip.fetch_raw(CONNECTOR, URL, log, offline=args.offline, headers=UA, timeout=900)
        first = content[:200].decode("utf-8", "replace").splitlines()[0]
        m = re.match(r"Data Last Updated:,(\d{4}-\d{2}-\d{2})", first)
        if not m:
            raise RuntimeError(f"the file's first line is not its date: {first!r}")
        base = dict(source=SOURCE, source_url=URL, retrieved_at=rec.get("retrieved_at") or "", vintage=m.group(1))
        frame = pd.read_csv(io.BytesIO(content), skiprows=1, dtype=str, keep_default_na=False, low_memory=False)
        t = dams(frame, base)
        hydro = int(t.purposes.str.contains("Hydroelectric").sum())
        header = [
            f"Energy Research Warehouse (ERW): U.S. Army Corps of Engineers, National Inventory of Dams, every dam the inventory lists (data last updated {m.group(1)}) (session 982)",
            "Shape: entities (docs/datastandard.md v0). entity_id usace_nid:<Federal ID>; entity_type dam; geo US-<state>; operator the owners' names; "
            "capacity_mw and status empty; nid_id the NID ID (shared by a dam's associated structures); the inventory's fields renamed with their units.",
            f"{len(t):,} dams in {t.geo.nunique()} states and territories; {hydro:,} with hydroelectric among their purposes; {int((t.coordinate_given != '').sum())} "
            "with one coordinate of the two (the pair left empty, the one given in coordinate_given). The inspection, condition, "
            "hazard and emergency planning fields are not taken. A blank stays blank; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/usace_nid.py; the CSV retrieved {base['retrieved_at']}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Army Corps of Engineers, National Inventory of Dams, {PAGE}",
            f"  access: {URL}",
            "License: a work of the U.S. Army Corps of Engineers, a federal agency (license_verdicts.csv); cite the National Inventory of Dams.",
        ]
        ip.write_snapshot(t, NAME, header, log, cols=ENTITY_COLS + EXTRA)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Army Corps of Engineers (USACE)", report="National Inventory of Dams (national download)",
                                    report_url=PAGE, document_list=URL, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t):,} dams"))
        print(f"{NAME}: {len(t):,} dams, {hydro:,} hydroelectric")
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
