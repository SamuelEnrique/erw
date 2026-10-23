#!/usr/bin/env python3
"""EIA-860's environmental schedules: each plant's boilers with what they serve and what controls them, its cooling
systems, and its emissions control equipment (session 896, chain 049).

Energy Research Warehouse (ERW) connector. Three entities tables from the U.S. Energy Information Administration's Form
EIA-860 annual zip (the newest final year the page links outside /archive/; session 873 saved eia8602025.zip):

    eia860_boilers            6_2_EnviroEquip "Boiler Info & Design Parameters" (firing, fuels, steam flow, efficiency)
                              joined by plant and boiler with "Emission Standards & Strategies" (the regulations, standards
                              and control strategies for sulfur, nitrogen oxides, particulates and mercury), and from
                              6_1_EnviroAssoc each boiler's generators, cooling systems, particulate, SO2, NOx and mercury
                              controls and stacks, each list joined with ";" (x_generator_ids, x_cooling_ids and the rest)
    eia860_cooling_systems    6_2_EnviroEquip "Cooling" (type, water source and discharge, intake rate, ponds, towers, costs)
    eia860_emission_controls  6_1_EnviroAssoc "Emissions Control Equipment" (type, the control ids it carries, status, in
                              service and retirement dates, total cost)

    entity_id   eia860_boiler:<plant>:<boiler id>, eia860_cooling:<plant>:<cooling id>,
                eia860_control:<plant>:<equipment type>:<its control ids joined with "+">; entity_type equipment (Decision
                54); name the plant's name and the part; geo US-<state> (the plant's state; the association and control
                sheets give none, so it is taken from the plant's other rows; US where none gives one); capacity_mw empty
    status      EIA's code as the data standard's word (as eia860_schedules.py maps it: OP, SB, OA, OS operating; P, L, T,
                OT planned; U, V, TS under_construction; RE retired; CN withdrawn; IP suspended; and the environmental
                schedules' own: SC cold standby and OZ ozone season only operating, CO under_construction, PL planned),
                read in capitals (EIA writes a few in lower case), the code kept as given in x_eia_status; an empty code
                stays empty; a code not in the map stops the run; status_date the month in service (operating) or
                retired (retired, where the sheet gives a retirement date: the cooling sheet gives none), else empty
    x_*         every other column of EIA's sheets, its heading as a name, as EIA gives it (costs in EIA's thousand dollars,
                named so)

A row with no plant code is EIA's footnote and is read past. A key EIA gives twice with two different rows has no key:
both are left out and named in the header (chain 030's rule); a row given twice the same is kept once. The flue gas
particulate (FGP) and desulfurization (FGD) details and the stacks are not taken (named in the header).

    python warehouse/connectors/eia860_environment.py [--offline]

Ceiling: two requests (the page and the zip; the zip saved in warehouse/raw/eia860_plants/ by eia860_plants.py is
reused). License: public (EIA, record 1 of license_reads.csv; cite "U.S. Energy Information Administration, Form EIA-860").
"""

import argparse
import datetime as dt
import io
import os
import re
import sys
import traceback
import zipfile

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402
from eia860_plants import CONNECTOR, ENTITY_COLS, PAGE, UA, newest, slug, text  # noqa: E402  the same page and zip
from eia860_schedules import STATUS, keyed, month_date  # noqa: E402  the same status words and key rule

# the environmental schedules' own codes (EIA-860's layout, reference tables 7 to 9, 16 to 21): CO new unit under
# construction, PL planned, SC cold standby, OZ operated only in the ozone season; the rest as eia860_schedules.py maps them
EQUIP_STATUS = dict(STATUS, CO="under_construction", PL="planned", SC="operating", OZ="operating")
TABLES = {
    "boilers": dict(name="eia860_boilers", source="eia:eia860:boilers", what="boilers, what they serve and what controls them"),
    "cooling": dict(name="eia860_cooling_systems", source="eia:eia860:cooling", what="cooling systems"),
    "controls": dict(name="eia860_emission_controls", source="eia:eia860:emission_controls", what="emissions control equipment"),
}
# the association sheets of 6_1 and the boiler column each list goes to
ASSOC = {"Boiler Generator": "x_generator_ids", "Boiler Cooling": "x_cooling_ids", "Boiler Particulate Matter": "x_pm_control_ids",
         "Boiler SO2": "x_so2_control_ids", "Boiler NOx": "x_nox_control_ids", "Boiler Mercury": "x_mercury_control_ids",
         "Boiler Stack Flue": "x_stack_flue_ids"}


def sheet(xl, name):
    """EIA's sheet with its heading row as column names (slugged, x_ prefixed; the first of a repeated name kept, a
    repeat stops the run)."""
    raw = pd.read_excel(xl, name, header=None)
    heads = [r for r in range(min(5, len(raw))) if any(text(v) == "Plant Code" for v in raw.iloc[r])]
    if not heads:
        raise RuntimeError(f"{name}: no heading row names 'Plant Code'")
    hr = heads[0]
    names = []
    for v in raw.iloc[hr]:
        n = "x_" + slug(text(v)) if text(v) else ""
        if n and n in names:
            raise RuntimeError(f"{name}: the heading {text(v)!r} twice")
        names.append(n)
    d = raw.iloc[hr + 1:].copy()
    d.columns = [n or f"_blank{i}" for i, n in enumerate(names)]
    d = d[[c for c in d.columns if not c.startswith("_blank")]]
    d = d.map(text)
    return d[d["x_plant_code"].str.fullmatch(r"\d+")].reset_index(drop=True)


def entities(d, kind, key_cols, id_of, label_of, status_col, in_service, retired, url, retrieved, states):
    meta = TABLES[kind]
    out = []
    for _, r in d.iterrows():
        code = r.get(status_col, "") if status_col else ""
        if code and code.upper() not in EQUIP_STATUS:                # a few codes come in lower case (op, re, os)
            raise RuntimeError(f"{meta['name']}: EIA status {code!r} is not in the map")
        word = EQUIP_STATUS.get(code.upper(), "")                      # an empty code stays empty
        if code.upper() == "RE":
            sd = month_date(r.get(retired[1], ""), r.get(retired[0], "")) if retired else ""
        elif word == "operating":
            sd = month_date(r.get(in_service[1], ""), r.get(in_service[0], "")) if in_service else ""
        else:
            sd = ""
        state = r.get("x_state", "") or states.get(r["x_plant_code"], "")
        row = dict(entity_id=id_of(r), entity_type="equipment", name=label_of(r), geo=f"US-{state}" if state else "US", lat="",
                   lon="", capacity_mw="", status=word, status_date=sd, operator=r.get("x_utility_name", ""),
                   source=meta["source"], source_url=url, retrieved_at=retrieved, vintage="", x_eia_status=code)
        row.update({c: r[c] for c in d.columns if c not in ("x_utility_name",)})
        row["x_state"] = state
        out.append(row)
    return pd.DataFrame(out)


def build(zf, url, retrieved):
    a_name = next(n for n in zf.namelist() if n.startswith("6_1_EnviroAssoc"))
    e_name = next(n for n in zf.namelist() if n.startswith("6_2_EnviroEquip"))
    ax = pd.ExcelFile(io.BytesIO(zf.read(a_name)))
    ex = pd.ExcelFile(io.BytesIO(zf.read(e_name)))
    info = sheet(ex, "Boiler Info & Design Parameters")
    std = sheet(ex, "Emission Standards & Strategies")
    cool = sheet(ex, "Cooling")
    ctrl = sheet(ax, "Emissions Control Equipment")
    states = {}
    for d in (info, std, cool):
        if "x_state" in d.columns:
            for p, s in zip(d["x_plant_code"], d["x_state"]):
                if s:
                    states.setdefault(p, s)
    # the boiler: its design, its standards (their columns that the design sheet does not carry), its associations
    boilers = info.drop_duplicates()
    extra = [c for c in std.columns if c not in boilers.columns]
    std2 = std[["x_plant_code", "x_boiler_id"] + extra].drop_duplicates()
    if std2.duplicated(["x_plant_code", "x_boiler_id"]).any():
        raise RuntimeError("Emission Standards & Strategies: a boiler given twice with two rows")
    boilers = boilers.merge(std2, on=["x_plant_code", "x_boiler_id"], how="left").fillna("")
    for sheet_name, col in ASSOC.items():
        a = sheet(ax, sheet_name)
        other = [c for c in a.columns if c not in ("x_utility_id", "x_utility_name", "x_plant_code", "x_plant_name", "x_boiler_id",
                                                    "x_steam_plant_type")]
        if len(other) != 1:
            raise RuntimeError(f"{sheet_name}: {other} is not one associated id")
        lists = a.groupby(["x_plant_code", "x_boiler_id"])[other[0]].agg(lambda v: ";".join(sorted({x for x in v if x})))
        boilers = boilers.merge(lists.rename(col).reset_index(), on=["x_plant_code", "x_boiler_id"], how="left").fillna("")
    b = entities(boilers, "boilers", None, lambda r: f"eia860_boiler:{r['x_plant_code']}:{r['x_boiler_id']}",
                 lambda r: f"{r['x_plant_name']} boiler {r['x_boiler_id']}", "x_boiler_status",
                 ("x_inservice_month", "x_inservice_year"), ("x_retirement_month", "x_retirement_year"), url, retrieved, states)
    c = entities(cool.drop_duplicates(), "cooling", None, lambda r: f"eia860_cooling:{r['x_plant_code']}:{r['x_cooling_id']}",
                 lambda r: f"{r['x_plant_name']} cooling {r['x_cooling_id']}", "x_cooling_status",
                 ("x_inservice_month", "x_inservice_year"), None, url, retrieved, states)
    ids = [c for c in ctrl.columns if c.endswith("_control_id")]

    def ctrl_id(r):
        carried = "+".join(f"{c[2:-11]}_{r[c]}" for c in ids if r[c])       # e.g. nox_1+mercury_2
        return f"eia860_control:{r['x_plant_code']}:{r['x_equipment_type']}:{carried}"
    k = entities(ctrl.drop_duplicates(), "controls", None, ctrl_id, lambda r: f"{r['x_plant_name']} {r['x_equipment_type']}", "x_status",
                 ("x_inservice_month", "x_inservice_year"), ("x_retirement_month", "x_retirement_year"), url, retrieved, states)
    return {"boilers": b, "cooling": c, "controls": k}, (a_name, e_name)


def main(argv=None):
    ap = argparse.ArgumentParser(description="EIA-860's environmental schedules: boilers, cooling systems, emissions controls")
    ap.add_argument("--offline", action="store_true", help="the saved page and zip only, no request")
    ap.add_argument("--out-dir", help="a trial: the tables under this folder, not warehouse/output")
    args = ap.parse_args(argv)
    if args.out_dir:
        raw_dir = ip.RAW_DIR
        ip.set_out_dir(args.out_dir)
        ip.RAW_DIR = raw_dir
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"eia860_environment_{run_id}.log"))
    ip.RAW.open(CONNECTOR, run_id)
    results = []
    try:
        page, _ = ip.fetch_raw(CONNECTOR, PAGE, log, offline=args.offline, fresh=not args.offline, headers=UA)
        url, year = newest(page.decode("utf-8", errors="replace"))
        content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, headers=UA, timeout=600)
        if content[:2] != b"PK":
            raise RuntimeError(f"{url} is not a zip")
        frames, files = build(zipfile.ZipFile(io.BytesIO(content)), url, rec.get("retrieved_at") or "")
        frames = {k: v.assign(vintage=str(year)) for k, v in frames.items()}
        for kind, meta in TABLES.items():
            skipped = {}
            t = keyed(frames[kind], skipped, meta["name"])
            first = ["x_plant_code", "x_state", "x_eia_status"]
            cols = ENTITY_COLS + first + [c for c in t.columns if c not in ENTITY_COLS and c not in first]
            t = t.fillna("")[cols]
            gone = skipped.get(meta["name"], [])
            header = [
                f"Energy Research Warehouse (ERW): EIA-860, {meta['what']}, data year {year} (session 896)",
                "Shape: entities (docs/datastandard.md v0). entity_type equipment (Decision 54); entity_id eia860_boiler:<plant>:<boiler>, "
                "eia860_cooling:<plant>:<cooling id> or eia860_control:<plant>:<equipment type>:<control ids>; name the plant's name and the part; "
                "status from EIA's code (x_eia_status); status_date the month in service (operating) or retired; x_* EIA's columns, headings as names"
                + ("; the boiler's generators, cooling systems, controls and stacks as lists joined with ';' (x_generator_ids and the rest)." if kind == "boilers" else "."),
                f"Data year {year} ({', '.join(files)}); {len(t):,} rows. The FGP and FGD details and the stacks are not taken. EIA's early release is not read."
                + (f" Keys EIA gives twice with two rows, left out (no key): {', '.join(gone)}." if gone else ""),
                f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia860_environment.py (the zip retrieved {rec.get('retrieved_at', '')})",
                f"Run log: warehouse/output/logs/eia860_environment_{run_id}.log",
                f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
                f"Source: {meta['source']} U.S. Energy Information Administration, Form EIA-860 Annual Electric Generator Report, environmental schedules, {PAGE}",
                f"  access: {url}",
                'License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Form EIA-860").',
            ]
            ip.write_snapshot(t, meta["name"], header, log, cols=cols)
            if not args.out_dir:
                ip.update_sources([dict(source=meta["source"], publisher="U.S. Energy Information Administration (EIA)",
                                        report=f"Form EIA-860 Annual Electric Generator Report, {meta['what']}", report_url=PAGE,
                                        document_list=PAGE, license="public", tables=[meta["name"]])])
            results.append(dict(table=meta["name"], market="all", status="ok", detail=f"{year}: {len(t):,} rows"))
            print(f"{meta['name']}: {year}, {len(t):,} rows" + (f", {len(gone)} keys left out" if gone else ""))
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED, no output file written:\n{tb}")
        print(f"eia860_environment FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table="eia860_boilers", market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        ip.write_status("eia860_environment", run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
