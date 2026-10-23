#!/usr/bin/env python3
"""EIA-860's schedules that EIA-860M does not hold: the owners of jointly owned generators, and the details of energy
storage, solar and wind generators (session 885, chain 048).

Energy Research Warehouse (ERW) connector. Four entities tables from the U.S. Energy Information Administration's Form
EIA-860 annual zip (the newest final year the page links outside /archive/; session 873 saved eia8602025.zip):

    eia860_generator_owners      4___Owner: each owner's share of a jointly owned generator. entity_id
                                 eia860_owner:<plant code>:<generator id>:<ownership id>; entity_type company; name the
                                 owner's name; operator the reporting utility's name; x_percent_owned EIA's fraction
                                 (0.6 is 60 percent)
    eia860_storage_generators    3_4_Energy_Storage: energy capacity, charge and discharge rates, storage technologies,
                                 enclosure, uses (arbitrage, frequency regulation and the rest), coupling, supported units
    eia860_solar_generators      3_3_Solar: tracking, tilt, azimuth, DC capacity, cell materials, net metering
    eia860_wind_generators       3_2_Wind: turbines, their maker and model, design wind speed, wind class, hub height

    entity_id   for the three generator tables eia860_<storage|solar|wind>:<plant code>:<generator id> (the same plant
                and generator EIA-860M's tables name eia860:<plant code>:<generator id>); entity_type generator; name
                the plant's name; geo US-<state>; capacity_mw the nameplate capacity; operator the utility's name;
                vintage the data year
    status      EIA's code as the data standard's word: OP, SB, OA, OS operating; P, L, T, OT planned; U, V, TS
                under_construction; RE retired; CN withdrawn (canceled); IP suspended (indefinitely postponed). EIA's
                code is kept in x_eia_status; a code not in the map stops the run
    status_date an operable generator's month of operation, a retired one's month of retirement; empty for the
                proposed and the canceled (a proposed generator's planned month is in x_current_year, x_current_month)
    x_*         every other column of EIA's sheet, its heading as a name, as EIA gives it; x_sheet the sheet (Operable,
                Proposed, Retired and Canceled)

A row with no plant code is EIA's footnote and is read past. A key EIA gives twice with two different rows has no key:
both are left out and named in the header (chain 030's rule); a row given twice the same is kept once. EIA's early
release (ER) zip is not read. EIA's robots file disallows /archive/ (session 666), where EIA moves earlier years.

    python warehouse/connectors/eia860_schedules.py [--offline]

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

STATUS = {"OP": "operating", "SB": "operating", "OA": "operating", "OS": "operating",
          "P": "planned", "L": "planned", "T": "planned", "OT": "planned",
          "U": "under_construction", "V": "under_construction", "TS": "under_construction",
          "RE": "retired", "CN": "withdrawn", "IP": "suspended"}
TABLES = {
    "4___Owner": dict(name="eia860_generator_owners", prefix="eia860_owner", source="eia:eia860:owner",
                      what="the owners of jointly owned generators"),
    "3_4_Energy_Storage": dict(name="eia860_storage_generators", prefix="eia860_storage", source="eia:eia860:energy_storage",
                               what="energy storage generators' details"),
    "3_3_Solar": dict(name="eia860_solar_generators", prefix="eia860_solar", source="eia:eia860:solar",
                      what="solar generators' details"),
    "3_2_Wind": dict(name="eia860_wind_generators", prefix="eia860_wind", source="eia:eia860:wind",
                     what="wind generators' details"),
}
MAIN = {"plant code": "plant", "plant name": "plant_name", "state": "state", "generator id": "generator",
        "status": "eia_status", "utility name": "operator", "nameplate capacity (mw)": "capacity_mw",
        "ownership id": "ownership", "owner name": "owner_name"}


def month_date(year, month):
    y, m = text(year), text(month)
    if not re.fullmatch(r"\d{4}", y):
        return ""
    return f"{y}-{int(m):02d}-01" if re.fullmatch(r"\d{1,2}", m) and 1 <= int(m) <= 12 else ""


def sheet_rows(frame, kind, sheet, year, url, retrieved):
    meta = TABLES[kind]
    heads = [r for r in range(min(5, len(frame))) if any(text(v) == "Plant Code" for v in frame.iloc[r])]
    if not heads:
        raise RuntimeError(f"{kind} {sheet}: no heading row names 'Plant Code'")
    hr = heads[0]
    cols = {}
    for c, v in enumerate(frame.iloc[hr]):
        n = text(v)
        if n:
            key = MAIN.get(n.lower(), "x_" + slug(n))
            if key in cols:
                raise RuntimeError(f"{kind} {sheet}: the heading {n!r} twice")
            cols[key] = c
    need = ("plant", "plant_name", "state", "generator", "eia_status") + (("ownership", "owner_name") if kind == "4___Owner" else ("capacity_mw",))
    for k in need:
        if k not in cols:
            raise RuntimeError(f"{kind} {sheet}: the sheet lacks '{k}'")
    out = []
    for _, r in frame.iloc[hr + 1:].iterrows():
        x = {k: text(r[c]) for k, c in cols.items()}
        if not re.fullmatch(r"\d+", x["plant"]):
            continue                                                   # EIA's footnote rows
        code = x.pop("eia_status")
        if code not in STATUS:
            raise RuntimeError(f"{kind} {sheet}: EIA status {code!r} is not in the map")
        state, plant, gen = x.pop("state"), x.pop("plant"), x.pop("generator")
        if kind == "4___Owner":
            row = dict(entity_id=f"{meta['prefix']}:{plant}:{gen}:{x.pop('ownership')}", entity_type="company",
                       name=x.pop("owner_name"), capacity_mw="", status_date="")
            x["x_plant_name"] = x.pop("plant_name")
        else:
            if code == "RE":
                sd = month_date(x.get("x_retirement_year"), x.get("x_retirement_month"))
            elif STATUS[code] == "operating":
                sd = month_date(x.get("x_operating_year"), x.get("x_operating_month"))
            else:
                sd = ""
            row = dict(entity_id=f"{meta['prefix']}:{plant}:{gen}", entity_type="generator", name=x.pop("plant_name"),
                       capacity_mw=x.pop("capacity_mw"), status_date=sd)
        row.update(geo=f"US-{state}" if state else "US", lat="", lon="", status=STATUS[code], operator=x.pop("operator", ""),
                   source=meta["source"], source_url=url, retrieved_at=retrieved, vintage=str(year),
                   x_plant_code=plant, x_generator_id=gen, x_state=state, x_eia_status=code, x_sheet=sheet, **x)
        out.append(row)
    return pd.DataFrame(out)


def keyed(t, skipped, name):
    """chain 030's rule: a row given twice the same is kept once; a key given twice with two rows is left out, counted."""
    t = t.drop_duplicates()
    twice = t["entity_id"].duplicated(keep=False)
    if twice.any():
        skipped[name] = sorted(set(t.loc[twice, "entity_id"]))
        t = t[~twice]
    return t.sort_values("entity_id").reset_index(drop=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description="EIA-860's owner, energy storage, solar and wind schedules")
    ap.add_argument("--offline", action="store_true", help="the saved page and zip only, no request")
    ap.add_argument("--out-dir", help="a trial: the tables under this folder, not warehouse/output")
    args = ap.parse_args(argv)
    if args.out_dir:
        raw_dir = ip.RAW_DIR
        ip.set_out_dir(args.out_dir)
        ip.RAW_DIR = raw_dir
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"eia860_schedules_{run_id}.log"))
    ip.RAW.open(CONNECTOR, run_id)
    results = []
    try:
        page, _ = ip.fetch_raw(CONNECTOR, PAGE, log, offline=args.offline, fresh=not args.offline, headers=UA)
        url, year = newest(page.decode("utf-8", errors="replace"))
        content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, headers=UA, timeout=600)
        if content[:2] != b"PK":
            raise RuntimeError(f"{url} is not a zip")
        zf = zipfile.ZipFile(io.BytesIO(content))
        skipped = {}
        for kind, meta in TABLES.items():
            name = next((n for n in zf.namelist() if n.startswith(kind)), None)
            if not name:
                raise RuntimeError(f"the zip holds no {kind} file: {zf.namelist()}")
            xl = pd.ExcelFile(io.BytesIO(zf.read(name)))
            parts = []
            for sheet in xl.sheet_names:
                t = sheet_rows(pd.read_excel(xl, sheet, header=None), kind, sheet, year, url, rec.get("retrieved_at") or "")
                log(f"{name} {sheet}: {len(t):,} rows")
                parts.append(t)
            t = keyed(pd.concat(parts, ignore_index=True), skipped, meta["name"])
            x_cols = [c for c in t.columns if c not in ENTITY_COLS]
            first = ["x_plant_code", "x_generator_id", "x_state", "x_eia_status", "x_sheet"]
            cols = ENTITY_COLS + first + [c for c in x_cols if c not in first]
            t = t.fillna("")[cols]
            gone = skipped.get(meta["name"], [])
            header = [
                f"Energy Research Warehouse (ERW): EIA-860, {meta['what']}, data year {year} (session 885)",
                ("Shape: entities (docs/datastandard.md v0). entity_id eia860_owner:<plant code>:<generator id>:<ownership id>; entity_type company "
                 "(an owner's share of one generator); name the owner's name; operator the reporting utility's name; geo US-<plant state>; "
                 "x_percent_owned EIA's fraction (0.6 is 60 percent); status the generator's, from EIA's code."
                 if kind == "4___Owner" else
                 f"Shape: entities (docs/datastandard.md v0). entity_id {meta['prefix']}:<plant code>:<generator id> (EIA-860M's tables name the same "
                 "generator eia860:<plant code>:<generator id>); entity_type generator; name the plant's name; capacity_mw nameplate; status from EIA's "
                 "code (x_eia_status); status_date the month of operation (operable) or of retirement (retired), empty for proposed and canceled.")
                + " x_* every other column of EIA's sheet, its heading as a name; x_sheet the sheet.",
                f"Data year {year} ({name}, sheets {', '.join(xl.sheet_names)}); {len(t):,} rows. EIA's early release is not read."
                + (f" Keys EIA gives twice with two rows, left out (no key): {', '.join(gone)}." if gone else ""),
                f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia860_schedules.py (the zip retrieved {rec.get('retrieved_at', '')})",
                f"Run log: warehouse/output/logs/eia860_schedules_{run_id}.log",
                f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
                f"Source: {meta['source']} U.S. Energy Information Administration, Form EIA-860 Annual Electric Generator Report, {name}, {PAGE}",
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
        print(f"eia860_schedules FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table="eia860_generator_owners", market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        ip.write_status("eia860_schedules", run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
