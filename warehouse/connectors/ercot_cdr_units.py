#!/usr/bin/env python3
"""ERCOT's resources as its Capacity, Demand and Reserves report lists them: each unit's code, county, zone, fuel, status,
in-service date and capacity (session 872, chain 047: a resource's county and zone for the All grids tab's ERCOT nodes,
from a report ERCOT posts where its robots file allows; ERCOT's resource lists on /misapp are not asked for).

Energy Research Warehouse (ERW) connector. One entities table, warehouse/output/ercot_cdr_units.csv, from the "Unit
Details" sheet of the newest CDR workbook, the one warehouse/connectors/ercot_cdr.py reads and saves (warehouse/raw/ercot_cdr/):

    entity_id   ercot_cdr_unit:<unit code, else interconnection request number, else the unit's name>:<fuel>
    entity_type generator; name ERCOT's unit name; geo US-TX; capacity_mw the installed capacity; status operating, planned or suspended
                from ERCOT's CDR status (x_cdr_status: OPER, PLAN, MOTH-IND and the others); status_date the in-service date; vintage the report's posting date
    x_*         ERCOT's fields: unit code, interconnection request number (INR), technology, fuel, resource attribute,
                county, zone; and the seasonal capability ERCOT counts (MW, at each season's start): x_summer_<year>,
                x_winter_<year>_<year+1>, x_spring_<year>, x_fall_<year>

A unit ERCOT lists twice with every field the same is kept once; two different rows under one key have no key and are
both left out, counted in the header (chain 030's rule). A heading the connector does not know stops the run.

    python warehouse/connectors/ercot_cdr_units.py [--offline]

Ceiling: two requests (the page and the workbook), none when both are saved (session 851 saved them). License: public
(ERCOT, licenses.md #2; cite "ERCOT, Capacity, Demand and Reserves Report").
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
from ercot_cdr import CONNECTOR, PAGE, UA, newest  # noqa: E402  the same page and workbook as ercot_cdr_reserve_margins

NAME = "ercot_cdr_units"
SOURCE = "ercot:cdr:unit_details"
SHEET = "Unit Details"
ENTITY_COLS = ["entity_id", "entity_type", "name", "geo", "lat", "lon", "capacity_mw", "status", "status_date", "operator",
               "source", "source_url", "retrieved_at", "vintage"]
FIELDS = {"unit name": "name", "interconnection request number (inr)": "x_inr", "unit code": "x_unit_code",
          "technology": "x_technology", "fuel": "x_fuel", "cdr status": "x_cdr_status", "cdr resource attribute": "x_attribute",
          "county": "x_county", "zone": "x_zone", "in-service date": "status_date", "installed capacity (mw)": "capacity_mw"}
# ERCOT's CDR status (its Acronyms sheet) to the data standard's status: operating, planned, suspended
STATUS = {"OPER": "operating", "RMR": "operating", "PLAN": "planned", "MOTH": "suspended", "EXT": "suspended"}
SEASONS = {"summer": "summer", "winter": "winter", "spring": "spring", "fall": "fall"}


def text(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return ""
    if isinstance(v, (pd.Timestamp, dt.datetime)):
        return v.strftime("%Y-%m-%d")
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return re.sub(r"\s+", " ", str(v)).strip()


def slug(v):
    return re.sub(r"[^A-Za-z0-9]+", "_", v).strip("_")


def layout(frame):
    """(heading row, {field: column}, {x_<season>_<year>: column})."""
    heads = [r for r in range(min(6, len(frame))) if text(frame.iloc[r, 0]).upper() == "UNIT NAME"]
    if not heads:
        raise RuntimeError("no heading row names 'UNIT NAME'")
    hr = heads[0]
    cols, caps, season = {}, {}, None
    for c in range(frame.shape[1]):
        group = text(frame.iloc[hr - 1, c]).lower() if hr >= 1 else ""
        s = next((v for k, v in SEASONS.items() if group.startswith(k)), None)
        if s:
            season = s
        name = text(frame.iloc[hr, c]).lower()
        if season is None:
            if name not in FIELDS:
                raise RuntimeError(f"column {c}: '{name}' is not in the map")
            cols[FIELDS[name]] = c
        else:
            years = re.findall(r"\d{4}", name)
            if not years:
                raise RuntimeError(f"column {c}: a {season} heading with no year: '{name}'")
            caps[f"x_{season}_{'_'.join(years)}"] = c
    missing = [v for v in FIELDS.values() if v not in cols]
    if missing or not caps:
        raise RuntimeError(f"the sheet lacks {missing or 'the seasonal capabilities'}")
    return hr, cols, caps


def units(frame, url, retrieved, vintage, notes):
    hr, cols, caps = layout(frame)
    out = []
    for _, r in frame.iloc[hr + 1:].iterrows():
        x = {k: text(r[c]) for k, c in cols.items()}
        if not x["name"]:
            continue
        ident = x["x_unit_code"] or x["x_inr"] or slug(x["name"])
        code = x["x_cdr_status"].split("-")[0]
        if code not in STATUS:
            raise RuntimeError(f"a CDR status not in the map: {x['x_cdr_status']!r}")
        row = dict(entity_id=f"ercot_cdr_unit:{ident}:{slug(x['x_fuel']) or 'none'}", entity_type="generator", geo="US-TX", lat="", lon="",
                   status=STATUS[code],
                   operator="", source=SOURCE, source_url=url, retrieved_at=retrieved, vintage=vintage, **x)
        row.update({k: text(r[c]) for k, c in caps.items()})
        out.append(row)
    t = pd.DataFrame(out).drop_duplicates()
    twice = t["entity_id"].duplicated(keep=False)
    if twice.any():
        notes["no key"] = sorted(t.loc[twice, "entity_id"].unique())
        t = t[~twice]
    return t.sort_values("entity_id").reset_index(drop=True), list(caps)


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERCOT's CDR unit details: each resource's code, county, zone, fuel and capacity")
    ap.add_argument("--offline", action="store_true", help="the saved page and workbook only, no request")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    args = ap.parse_args(argv)
    if args.out_dir:
        raw_dir = ip.RAW_DIR
        ip.set_out_dir(args.out_dir)
        ip.RAW_DIR = raw_dir
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"ercot_cdr_units_{run_id}.log"))
    ip.RAW.open(CONNECTOR, run_id)
    results = []
    try:
        if ip.paused("ercot"):
            raise RuntimeError("ERCOT is paused (warehouse/metadata/paused_sources.csv): nothing is requested")
        page, _ = ip.fetch_raw(CONNECTOR, PAGE, log, offline=args.offline, fresh=not args.offline, headers=UA)
        url, posted = newest(page.decode("utf-8", errors="replace"))
        content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, headers=UA, timeout=300)
        notes = {}
        t, cap_cols = units(pd.read_excel(io.BytesIO(content), SHEET, header=None), url, rec.get("retrieved_at") or "", posted, notes)
        cols = ENTITY_COLS + ["x_unit_code", "x_inr", "x_technology", "x_fuel", "x_cdr_status", "x_attribute", "x_county", "x_zone"] + cap_cols
        t = t[cols]
        report = url.rsplit("/", 1)[1]
        header = [
            "Energy Research Warehouse (ERW): ERCOT, the units of the Capacity, Demand and Reserves report: each resource's code, county, zone, fuel, status, in-service date and capacity (session 872)",
            "Shape: entities (docs/datastandard.md v0). entity_id ercot_cdr_unit:<unit code, else INR, else name>:<fuel>; entity_type generator; capacity_mw installed capacity; status from ERCOT's CDR status (x_cdr_status); status_date the in-service date; "
            "x_* ERCOT's fields and the seasonal capability it counts (MW) at each season's start: x_summer_<y>, x_winter_<y>_<y+1>, x_spring_<y>, x_fall_<y>.",
            f"Report: {report}, posted {posted[:10]}; {len(t):,} units ({t['x_unit_code'].ne('').sum():,} with a unit code), {t['x_county'].nunique()} counties."
            + (f" Left out, no key (two different rows): {', '.join(notes['no key'])}." if notes.get("no key") else ""),
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/ercot_cdr_units.py (the workbook as saved: {rec.get('retrieved_at', '')})",
            f"Run log: warehouse/output/logs/ercot_cdr_units_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Electric Reliability Council of Texas (ERCOT), Capacity, Demand and Reserves Report, Unit Details, {PAGE}",
            f"  access: {url}",
            'License: public (ERCOT, licenses.md #2; cite "ERCOT, Capacity, Demand and Reserves Report").',
        ]
        ip.write_snapshot(t, NAME, header, log, cols=cols)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Electric Reliability Council of Texas (ERCOT)",
                                    report="Capacity, Demand and Reserves Report, Unit Details", report_url=PAGE, document_list=PAGE,
                                    license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="ercot", status="ok", detail=f"{len(t):,} rows"))
        print(f"{NAME}: {len(t):,} units, {t['x_county'].nunique()} counties; {len(notes.get('no key', []))} without a key")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED, no output file written:\n{tb}")
        print(f"ercot_cdr_units FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="ercot", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        ip.write_status("ercot_cdr_units", run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
