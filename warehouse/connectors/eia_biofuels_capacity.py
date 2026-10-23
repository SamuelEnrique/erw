#!/usr/bin/env python3
"""EIA's biofuels plant production capacity: each fuel ethanol, biodiesel and renewable diesel plant's capacity as of
1 January, with its state and PADD, a year a row (session 2031, chain 058: the plants behind the RINs of session 2030
and the ethanol EIA's monthly tables hold).

Energy Research Warehouse (ERW) connector. One entities table from EIA's yearly capacity workbooks (Form EIA-819):

    https://www.eia.gov/biofuels/capacity/biofuelscapacity.xlsx              U.S. Biofuels Plant Production Capacity, as
                                                                             of January 1, 2026 (one sheet: Entity,
                                                                             Facility, State, PADD, Capacity (MMgal/yr),
                                                                             Capacity (Mb/d), Facility type)
    https://www.eia.gov/petroleum/ethanolcapacity/ethanolcapacity.xlsx      Fuel ethanol, as of January 1, 2025
    https://www.eia.gov/biofuels/biodiesel/capacity/biodieselcapacity.xlsx  Biodiesel, as of January 1, 2025
    https://www.eia.gov/biofuels/renewable/capacity/renewablescapacity.xlsx Renewable diesel fuel and other biofuels, as
                                                                             of January 1, 2025 (each 2025 sheet: State,
                                                                             Respondent, City, MMgal/yr, Mb/d, a state
                                                                             written once above its plants, a PADD row
                                                                             above its states)

    eia_biofuel_plants   entity_id eia_biofuel:<year>:<fuel>:<state>:<n> (n the plant's place among its year, fuel and
                         state, in the workbook's order); entity_type plant; name the facility (2026) or the city (2025,
                         whose sheets name no facility); geo US-<state>; capacity_mw empty; status active; status_date
                         the 1 January the capacity is as of; operator the entity or respondent as EIA writes it; x_year,
                         x_fuel (ethanol, biodiesel, renewable_diesel_and_other), x_facility_type as published, x_padd,
                         x_city (2025), x_capacity_mmgal_per_year and x_capacity_kbbl_per_day as published ("(s)", less
                         than 0.5, kept), x_coprocessing yes where EIA's footnote 1 marks a refinery co-processing renewable
                         feedstock and petroleum

The capacities stay in x_ columns: an entity's capacity_mw is power, and a plant's yearly gallons or daily barrels are
not. EIA's capacity is what a plant can make in a year (MMgal/yr) or a day (Mb/d). Earlier years' issues sit under
www.eia.gov's /archive/, which its robots file disallows, so only the two current issues are taken. A workbook without
its columns, a plant before any state, or a capacity neither a number nor "(s)" stops the run. Nothing is filled.

    python warehouse/connectors/eia_biofuels_capacity.py [--offline] [--out-dir DIR]

Ceiling: four requests (the four workbooks), saved in warehouse/raw/eia_biofuels_capacity/ and reused offline. License:
public (EIA, read 1 of license_reads.csv).
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

CONNECTOR = "eia_biofuels_capacity"
SOURCE = "eia:biofuels_capacity"
HOST = "https://www.eia.gov"
COMBINED = HOST + "/biofuels/capacity/biofuelscapacity.xlsx"
SINGLES = {"ethanol": HOST + "/petroleum/ethanolcapacity/ethanolcapacity.xlsx",
           "biodiesel": HOST + "/biofuels/biodiesel/capacity/biodieselcapacity.xlsx",
           "renewable_diesel_and_other": HOST + "/biofuels/renewable/capacity/renewablescapacity.xlsx"}
PAGES = {"combined": HOST + "/biofuels/capacity/", "ethanol": HOST + "/petroleum/ethanolcapacity/",
         "biodiesel": HOST + "/biofuels/biodiesel/capacity/", "renewable_diesel_and_other": HOST + "/biofuels/renewable/capacity/"}
TABLE = "eia_biofuel_plants"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
FUEL_OF = {"ethanol": "ethanol", "biodiesel": "biodiesel", "renewable diesel fuel and other biofuels": "renewable_diesel_and_other"}
ENTITY_COLS = ["entity_id", "entity_type", "name", "geo", "lat", "lon", "capacity_mw", "status", "status_date", "operator",
               "source", "source_url", "retrieved_at", "vintage"]
X_COLS = ["x_year", "x_fuel", "x_facility_type", "x_padd", "x_city", "x_capacity_mmgal_per_year", "x_capacity_kbbl_per_day", "x_coprocessing"]
STATES = {"Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA", "Colorado": "CO", "Connecticut": "CT",
          "Delaware": "DE", "District of Columbia": "DC", "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL",
          "Indiana": "IN", "Iowa": "IA", "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
          "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS", "Missouri": "MO", "Montana": "MT", "Nebraska": "NE",
          "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY", "North Carolina": "NC",
          "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI",
          "South Carolina": "SC", "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT", "Virginia": "VA",
          "Washington": "WA", "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY"}


def text(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return ""
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return re.sub(r"\s+", " ", str(v)).strip()


def capacity(v, where):
    s = text(v).replace(",", "")
    if s == "(s)" or re.fullmatch(r"\d+(\.\d+)?", s):
        return s
    raise RuntimeError(f"{where}: a capacity neither a number nor (s): {s!r}")


def read_combined(content):
    """(year, rows) of the combined workbook: its title year from the page is not in the sheet, so the year is the
    caller's; the rows in sheet order."""
    d = pd.read_excel(io.BytesIO(content), sheet_name=0, dtype=object)
    d.columns = [text(c) for c in d.columns]
    need = ["Entity", "Facility", "State", "PADD", "Capacity (MMgal/yr)", "Capacity (Mb/d)", "Facility type"]
    miss = [c for c in need if c not in d.columns]
    if miss:
        raise RuntimeError(f"the combined workbook has no column {miss}; its columns are {list(d.columns)}")
    rows = []
    for i, r in d.iterrows():
        if all(text(r[c]) == "" for c in need):
            continue
        ftype = text(r["Facility type"])
        fuel = FUEL_OF.get(ftype.lower())
        if fuel is None:
            raise RuntimeError(f"combined row {i + 2}: a facility type not known: {ftype!r}")
        st = text(r["State"]).upper()
        if not re.fullmatch(r"[A-Z]{2}", st):
            raise RuntimeError(f"combined row {i + 2}: a state not a code: {st!r}")
        rows.append(dict(fuel=fuel, ftype=ftype, state=st, padd=text(r["PADD"]), name=text(r["Facility"]), operator=text(r["Entity"]), city="",
                         mmgal=capacity(r["Capacity (MMgal/yr)"], f"combined row {i + 2}"), kbd=capacity(r["Capacity (Mb/d)"], f"combined row {i + 2}"),
                         coproc=""))
    return rows


def read_single(content, fuel, ftype):
    """The rows of a 2025 single-fuel workbook: a state written once above its plants, a PADD row above its states."""
    d = pd.read_excel(io.BytesIO(content), sheet_name=0, header=None, dtype=object)
    head = None
    for i in range(min(len(d), 10)):
        if [text(v) for v in d.iloc[i].tolist()[:5]] == ["State", "Respondent", "City", "MMgal/yr", "Mb/d"]:
            head = i
            break
    if head is None:
        raise RuntimeError(f"{fuel}: no header row State, Respondent, City, MMgal/yr, Mb/d")
    rows, state, padd = [], None, ""
    for i in range(head + 1, len(d)):
        c = [text(v) for v in d.iloc[i].tolist()[:5]]
        if c[0].startswith("PADD"):
            padd = c[0]
            continue
        if c[0] == "U.S. Total":
            break
        if c[0] in STATES:
            state = STATES[c[0]]
        elif c[0]:
            raise RuntimeError(f"{fuel} row {i + 1}: a first cell neither a state nor a PADD: {c[0]!r}")
        if not c[1]:
            continue
        if state is None:
            raise RuntimeError(f"{fuel} row {i + 1}: a plant before any state")
        name, coproc = c[1], ""
        m = re.fullmatch(r"(.*\S)\s+1", name)
        if m:
            name, coproc = m.group(1), "yes"
        rows.append(dict(fuel=fuel, ftype=ftype, state=state, padd=padd, name=c[2], operator=name, city=c[2],
                         mmgal=capacity(c[3], f"{fuel} row {i + 1}"), kbd=capacity(c[4], f"{fuel} row {i + 1}"), coproc=coproc))
    if not rows:
        raise RuntimeError(f"{fuel}: no plant")
    return rows


def build(rows, year, base):
    out, seen = [], {}
    for r in rows:
        k = (r["fuel"], r["state"])
        seen[k] = seen.get(k, 0) + 1
        out.append(dict(entity_id=f"eia_biofuel:{year}:{r['fuel']}:{r['state'].lower()}:{seen[k]}", entity_type="plant", name=r["name"],
                        geo=f"US-{r['state']}", lat="", lon="", capacity_mw="", status="active", status_date=f"{year}-01-01",
                        operator=r["operator"], **base, x_year=str(year), x_fuel=r["fuel"], x_facility_type=r["ftype"], x_padd=r["padd"],
                        x_city=r["city"], x_capacity_mmgal_per_year=r["mmgal"], x_capacity_kbbl_per_day=r["kbd"], x_coprocessing=r["coproc"]))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="EIA's biofuels plant production capacity, a plant and year a row")
    ap.add_argument("--offline", action="store_true", help="the saved files only, no request")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    ap.add_argument("--combined-year", type=int, default=2026, help="the year the combined workbook is as of (its page: 2026)")
    ap.add_argument("--single-year", type=int, default=2025, help="the year the single-fuel workbooks are as of (their pages: 2025)")
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
        out, counts = [], {}
        content, rec = ip.fetch_raw(CONNECTOR, COMBINED, log, offline=args.offline, headers=UA, timeout=120, pause=1)
        base = dict(source=SOURCE, source_url=COMBINED, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
        rows = read_combined(content)
        out += build(rows, args.combined_year, base)
        counts[args.combined_year] = len(rows)
        for fuel, url in SINGLES.items():
            content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, headers=UA, timeout=120, pause=1)
            base = dict(source=SOURCE, source_url=url, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
            ftype = {"ethanol": "Ethanol", "biodiesel": "Biodiesel", "renewable_diesel_and_other": "Renewable Diesel Fuel and Other Biofuels"}[fuel]
            rows = read_single(content, fuel, ftype)
            out += build(rows, args.single_year, base)
            counts[args.single_year] = counts.get(args.single_year, 0) + len(rows)
        e = pd.DataFrame(out)
        if e.entity_id.duplicated().any():
            raise RuntimeError("an entity_id given twice")
        cols = ENTITY_COLS + X_COLS
        e = e[cols].sort_values("entity_id").reset_index(drop=True)
        by = e.groupby(["x_year", "x_fuel"]).size().to_dict()
        by_s = "; ".join(f"{y} {f} {n}" for (y, f), n in sorted(by.items()))
        head = [
            "Energy Research Warehouse (ERW): U.S. Energy Information Administration (EIA), U.S. Biofuels Plant Production Capacity (as of January 1, "
            f"{args.combined_year}) and the fuel ethanol, biodiesel and renewable diesel plant capacity reports (as of January 1, {args.single_year}), Form "
            "EIA-819: each plant's capacity, state and PADD, a year a row (session 2031)",
            "Shape: entities (docs/datastandard.md v0). entity_id eia_biofuel:<year>:<fuel>:<state>:<n> (n the plant's place among its year, fuel and "
            "state in EIA's workbook); entity_type plant; name the facility (the 2025 sheets name only the city); geo US-<state>; status active; "
            "status_date the 1 January the capacity is as of; operator the entity or respondent as EIA writes it; x_capacity_mmgal_per_year and "
            "x_capacity_kbbl_per_day as published ((s) is less than 0.5); x_coprocessing yes where EIA marks a refinery co-processing renewable "
            "feedstock and petroleum.",
            f"{len(e)} plant years: {by_s}. Earlier issues sit under www.eia.gov's /archive/, which its robots file disallows. Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia_biofuels_capacity.py",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} EIA, U.S. Biofuels Plant Production Capacity, {PAGES['combined']}",
            "  access: " + "; ".join([COMBINED] + list(SINGLES.values())),
            'License: public (EIA: "U.S. government publications are in the public domain"; cite "U.S. Energy Information Administration").',
        ]
        ip.write_snapshot(e, TABLE, head, log, cols)
        results.append(dict(table=TABLE, market="all", status="ok", detail=f"{len(e)} rows"))
        print(f"{TABLE}: {len(e)} plant years ({by_s})")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{TABLE} FAILED, no output file written:\n{tb}")
        print(f"{TABLE} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=TABLE, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Energy Information Administration (EIA)",
                                    report="U.S. Biofuels Plant Production Capacity; U.S. Fuel Ethanol, Biodiesel, and Renewable Diesel Fuel and Other Biofuels Plant Production Capacity",
                                    report_url=PAGES["combined"], document_list=PAGES["combined"], license="public", tables=[TABLE])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
