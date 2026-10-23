#!/usr/bin/env python3
"""ERCOT's resource nodes placed: each settlement point of node_basis_daily with the county and load zone of the units
ERCOT's Capacity, Demand and Reserves report lists at its station (session 901, chain 049: the siting gaps' "A node's
zone, hub, wires utility and county", session 733).

Energy Research Warehouse (ERW) derived table, warehouse/output/ercot_node_places.csv, computed from two ERW tables, no
request:

    node_basis_daily    the settlement points (entity ercot:<settlement point>), their resource type and class
    ercot_cdr_units     ERCOT's CDR units with their unit code, county and zone (session 872)

The match: a settlement point's station code is its name up to the first "_" (7RNCHSLR_ALL gives 7RNCHSLR); a CDR unit's
is its unit code up to the first "_" (7RNCHSLR_UNIT1 gives 7RNCHSLR). A node takes the county and the zone of the units
at its station only when every such unit gives the same county and the same zone; a node whose station's units disagree,
or whose station no unit carries, is left out and counted in the header: no match is guessed. The hubs and load zones
(x_class hub or zone) are not resources and are left out.

    entity_id   ercot_node:<settlement point>; entity_type generator (the resource ERCOT settles at the node); name the
                settlement point; geo US-TX; x_county and x_zone (ERCOT's load zone as the CDR names it); x_class and
                x_resource_type node_basis_daily's; x_station; x_cdr_units the units matched, joined with ";"; x_cdr_units_n

The wires utility is not given: the CDR names no EIA plant id, so `eia860_plants_annual`'s owner cannot be joined without a
guess; named in the method note.

    python warehouse/derived/ercot_node_places.py [--out-dir DIR]
"""

import argparse
import datetime as dt
import os
import sys
import traceback

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import iso_prices as ip  # noqa: E402

NODES, UNITS = "node_basis_daily", "ercot_cdr_units"
NAME = "ercot_node_places"
SOURCE = "erw:ercot_node_places"
ENTITY_COLS = ["entity_id", "entity_type", "name", "geo", "lat", "lon", "capacity_mw", "status", "status_date", "operator",
               "source", "source_url", "retrieved_at", "vintage"]
EXTRA = ["x_station", "x_county", "x_zone", "x_class", "x_resource_type", "x_cdr_units", "x_cdr_units_n"]
METHOD = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/ercot_node_places.md"


def read_table(path, cols=None):
    n = 0
    with open(path, encoding="utf-8") as f:
        for ln in f:
            if not ln.startswith("#"):
                break
            n += 1
    return pd.read_csv(path, skiprows=n, dtype=str, keep_default_na=False, usecols=cols)


def place(nodes, units, retrieved):
    """(the placed nodes, the counts of those left out)."""
    nb = nodes.drop_duplicates("entity").copy()
    nb = nb[~nb["x_class"].isin(["hub", "zone"])]
    nb["sp"] = nb["entity"].str.split(":", n=1).str[1]
    nb["station"] = nb["sp"].str.split("_").str[0]
    u = units[units["x_unit_code"] != ""].copy()
    u["station"] = u["x_unit_code"].str.split("_").str[0]
    st = u.groupby("station").agg(counties=("x_county", lambda v: sorted(set(v))), zones=("x_zone", lambda v: sorted(set(v))),
                                   codes=("x_unit_code", lambda v: ";".join(sorted(set(v)))), n=("x_unit_code", "nunique"))
    m = nb.merge(st, left_on="station", right_index=True, how="left")
    counts = {"nodes": len(nb), "no unit at the station": int(m["codes"].isna().sum())}
    m = m[m["codes"].notna()]
    one = m["counties"].map(len).eq(1) & m["zones"].map(len).eq(1)
    counts["units disagree"] = int((~one).sum())
    m = m[one]
    out = pd.DataFrame({
        "entity_id": "ercot_node:" + m["sp"], "entity_type": "generator", "name": m["sp"], "geo": "US-TX", "lat": "", "lon": "",
        "capacity_mw": "", "status": "", "status_date": "", "operator": "", "source": SOURCE, "source_url": METHOD,
        "retrieved_at": retrieved, "vintage": "",
        "x_station": m["station"], "x_county": m["counties"].str[0], "x_zone": m["zones"].str[0], "x_class": m["x_class"],
        "x_resource_type": m["x_resource_type"], "x_cdr_units": m["codes"], "x_cdr_units_n": m["n"].astype(int).astype(str),
    })
    counts["placed"] = len(out)
    return out.sort_values("entity_id").reset_index(drop=True), counts


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERCOT's resource nodes with the county and zone of their CDR units")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    args = ap.parse_args(argv)
    paths = {t: os.path.join(ip.OUT_DIR, t + ".csv") for t in (NODES, UNITS)}
    if args.out_dir:
        raw_dir = ip.RAW_DIR
        ip.set_out_dir(args.out_dir)
        ip.RAW_DIR = raw_dir
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"ercot_node_places_{run_id}.log"))
    try:
        nodes = read_table(paths[NODES], ["entity", "x_resource_type", "x_class"])
        units = read_table(paths[UNITS], ["x_unit_code", "x_county", "x_zone"])
        retrieved = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        t, c = place(nodes, units, retrieved)
        header = [
            "Energy Research Warehouse (ERW): ERCOT's resource nodes with the county and load zone of the CDR units at their station (session 901)",
            "Shape: entities (docs/datastandard.md v0). entity_id ercot_node:<settlement point>; entity_type generator; x_county and x_zone ERCOT's CDR; "
            "x_station the code before the first '_'; x_cdr_units the units matched; x_class and x_resource_type node_basis_daily's.",
            f"Placed {c['placed']:,} of {c['nodes']:,} resource nodes; left out: {c['no unit at the station']:,} whose station no CDR unit carries, "
            f"{c['units disagree']:,} whose station's units give two counties or zones (no match guessed). The wires utility is not given.",
            f"Derived from: {NODES}; {UNITS}",
            f"Built by warehouse/derived/ercot_node_places.py; method docs/methods/ercot_node_places.md. Retrieved: {run_id} (UTC), computed from the tables held; no request was made.",
            f"Run log: warehouse/output/logs/ercot_node_places_{run_id}.log",
            "Source: ercot:cdr Electric Reliability Council of Texas (ERCOT), Capacity, Demand and Reserves Report (the units' county and zone), "
            "and ERCOT's settlement points as node_basis_daily holds them",
            "License: ERCOT's (its terms, read 2 of license_reads.csv, allow it); the match is the ERW's.",
        ]
        ip.write_snapshot(t, NAME, header, log, cols=ENTITY_COLS + EXTRA)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Energy Research Warehouse (ERW), derived",
                                    report="ERCOT's resource nodes with the county and zone of their CDR units (docs/methods/ercot_node_places.md)",
                                    report_url=METHOD, document_list="docs/methods/ercot_node_places.md", license="public", tables=[NAME])])
        print(f"{NAME}: {c['placed']:,} of {c['nodes']:,} nodes placed")
        rc = 0
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED, no output file written:\n{tb}")
        print(f"ercot_node_places FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        rc = 1
    log.close()
    return rc


if __name__ == "__main__":
    sys.exit(main())
