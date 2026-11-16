#!/usr/bin/env python3
"""ERCOT's zones' wires utilities, for the All grids tab's rows that name no place (session 7009, chain 301; the old
laptop's data request 20 of docs/state/data_requests_large_load.md).

Energy Research Warehouse (ERW). Reads warehouse/output/ercot_node_wires_utilities.csv (for each ERCOT settlement point
of ERCOT's Capacity, Demand and Reserves report: its county, its CDR zone, and the utilities EIA-861 lists in that
county, the delivery-only companies apart: in ERCOT's competitive areas those are the wires utilities, the TDSPs) and
writes site/data/siting/ercot_zone_wires.json: for each CDR zone, each delivery-only company with the number of the
zone's node counties it serves, most counties first, and the counties named. No request, no model call, no table
written.

What it is not. The CDR zones (WEST, NORTH, SOUTH, COASTAL, HOUSTON, PANHANDLE) are where ERCOT's report places its
nodes; they are not the settlement load zones (LZ_WEST, LZ_NORTH, LZ_SOUTH, LZ_HOUSTON) the tab's price rows name, though
those take the same names for the same regions, and the tab says which it reads. The zones of the municipal and
cooperative utilities outside retail choice (LZ_AEN, LZ_CPS, LZ_LCRA, LZ_RAYBN) have no delivery-only company: their
own utility is the wires utility, and EIA-861's territories list it beside the others in each county; this file names
none for them. A county counts once a zone however many nodes it holds.

    python warehouse/derived/ercot_zone_wires.py [--in-dir DIR] [--out FILE]
"""
import argparse
import csv
import datetime as dt
import json
import os
import sys
from collections import defaultdict

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "site", "data", "siting", "ercot_zone_wires.json")


def build(rows):
    counties = defaultdict(set)
    serve = defaultdict(lambda: defaultdict(set))
    for r in rows:
        zone, county = r["x_zone"].strip(), r["x_county"].strip()
        if not zone or not county:
            continue
        counties[zone].add(county)
        for u in (x.strip() for x in r.get("x_delivery_only", "").split(";")):
            if u:
                serve[zone][u].add(county)
    zones = {}
    for zone in sorted(counties):
        zones[zone] = dict(node_counties=len(counties[zone]),
                           wires=[dict(utility=u, counties=len(c), named=sorted(c))
                                  for u, c in sorted(serve[zone].items(), key=lambda kv: (-len(kv[1]), kv[0]))])
    return zones


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERCOT's zones' wires utilities")
    ap.add_argument("--in-dir", default=os.path.join(ROOT, "warehouse", "output"))
    ap.add_argument("--out", default=OUT)
    a = ap.parse_args(argv)
    src = os.path.join(a.in_dir, "ercot_node_wires_utilities.csv")
    with open(src, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(ln for ln in f if not ln.startswith("#")))
    with open(src, encoding="utf-8") as f:
        line = next((ln for ln in f if ln.startswith("#") and "Retrieved" in ln), "")
    retrieved = ("retrieved " + line.split("Retrieved", 1)[1].strip(" :\n").split(" ")[0]) if line else "retrieval not stated"
    zones = build(rows)
    doc = dict(built=dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
               method="warehouse/derived/ercot_zone_wires.py (its docstring says what the zones are and are not)",
               source=f"ercot_node_wires_utilities ({len(rows)} settlement points; {retrieved}); EIA-861 service territories and ERCOT's CDR report through it",
               zones=zones)
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(doc, ensure_ascii=False, indent=1) + "\n")
    print(f"ercot_zone_wires: {len(zones)} zones; {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
