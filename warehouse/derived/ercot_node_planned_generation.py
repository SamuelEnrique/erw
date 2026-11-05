#!/usr/bin/env python3
"""The planned generation near an ERCOT resource node: for each node ercot_node_places places, the active projects of
ERCOT's interconnection queue in its county, counted with their megawatts by kind, and EIA-860M's planned generators in
the same county (session 931, chain 052: the siting gaps' "a node's county, so the planned generation near it", which
chain 072 left open: "the county is known; the sum by county is not built").

Energy Research Warehouse (ERW) derived table, warehouse/output/ercot_node_planned_generation.csv, computed from three ERW
tables, no request:

    ercot_node_places               the placed resource nodes with their county and load zone (session 901)
    ercot_interconnection_queue     ERCOT's queue positions with county, fuel and technology, status and dates
    eia860m_planned_generators      EIA-860M's planned generators with their state and county

The match: a queue project or an EIA-860M generator (state TX) is in a node's county when its county, in capitals with
runs of spaces made one, is the node's. A county with none has zeros: both tables list every project they hold in Texas.
The kind: ERCOT's fuel and technology's first word (Solar, Wind, Gas, Other - Battery Energy Storage as storage, the rest
other); EIA-860M's technology group as it gives it.

    entity_id   ercot_node:<settlement point> (as ercot_node_places); entity_type generator; geo US-TX; x_county, x_zone
    x_*         x_queue_projects and x_queue_mw (ERCOT's active projects in the county), x_queue_<solar|wind|storage|gas|other>_mw,
                x_queue_next_in_service (the earliest proposed in-service date among them); x_eia_planned_generators and
                x_eia_planned_mw (EIA-860M's planned generators in the county, nameplate MW), x_eia_<group>_mw

    python warehouse/derived/ercot_node_planned_generation.py [--out-dir DIR]
"""

import argparse
import datetime as dt
import os
import re
import sys
import traceback

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import iso_prices as ip  # noqa: E402

NODES, QUEUE, EIA = "ercot_node_places", "ercot_interconnection_queue", "eia860m_planned_generators"
NAME = "ercot_node_planned_generation"
SOURCE = "erw:ercot_node_planned_generation"
ENTITY_COLS = ["entity_id", "entity_type", "name", "geo", "lat", "lon", "capacity_mw", "status", "status_date", "operator",
               "source", "source_url", "retrieved_at", "vintage"]
QUEUE_KINDS = ["solar", "wind", "storage", "gas", "other"]
EIA_GROUPS = ["solar", "wind", "storage", "natural_gas", "nuclear", "petroleum", "hydro", "biomass", "geothermal", "other"]
EXTRA = (["x_county", "x_zone", "x_queue_projects", "x_queue_mw"] + [f"x_queue_{k}_mw" for k in QUEUE_KINDS] + ["x_queue_next_in_service",
         "x_eia_planned_generators", "x_eia_planned_mw"] + [f"x_eia_{g}_mw" for g in EIA_GROUPS])
METHOD = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/ercot_node_planned_generation.md"


def read_table(path, cols=None):
    n = 0
    with open(path, encoding="utf-8") as f:
        for ln in f:
            if not ln.startswith("#"):
                break
            n += 1
    return pd.read_csv(path, skiprows=n, dtype=str, keep_default_na=False, usecols=cols)


def key(s):
    return re.sub(r"\s+", " ", str(s)).strip().upper()


def queue_kind(fuel):
    f = fuel.strip()
    if f.startswith("Solar"):
        return "solar"
    if f.startswith("Wind"):
        return "wind"
    if f.startswith("Gas"):
        return "gas"
    if f == "Other - Battery Energy Storage":
        return "storage"
    return "other"


def build(nodes, queue, eia, retrieved):
    q = queue[queue["status"] == "active"].copy()
    q["county_k"] = q["county"].map(key)
    q["mw"] = pd.to_numeric(q["capacity_mw"], errors="coerce")
    q["kind"] = q["fuel_technology"].map(queue_kind)
    e = eia[eia["state"] == "TX"].copy()
    e["county_k"] = e["county"].map(key)
    e["mw"] = pd.to_numeric(e["nameplate_mw"], errors="coerce")
    unknown = sorted(set(e["technology_group"]) - set(EIA_GROUPS))
    if unknown:
        raise RuntimeError(f"an EIA-860M technology group not in the map: {unknown}")
    qk = q.pivot_table(index="county_k", columns="kind", values="mw", aggfunc="sum").reindex(columns=QUEUE_KINDS).fillna(0)
    qn = q.groupby("county_k").size()
    qnext = q[q["proposed_in_service_date"] != ""].groupby("county_k")["proposed_in_service_date"].min()
    ek = e.pivot_table(index="county_k", columns="technology_group", values="mw", aggfunc="sum").reindex(columns=EIA_GROUPS).fillna(0)
    en = e.groupby("county_k").size()
    rows = []
    for _, r in nodes.iterrows():
        c = key(r["x_county"])
        if not c:
            raise RuntimeError(f"a placed node without a county: {r['entity_id']}")
        row = {"entity_id": r["entity_id"], "entity_type": "generator", "name": r["name"], "geo": "US-TX", "lat": "", "lon": "",
               "capacity_mw": "", "status": "", "status_date": "", "operator": "", "source": SOURCE, "source_url": METHOD,
               "retrieved_at": retrieved, "vintage": "", "x_county": r["x_county"], "x_zone": r["x_zone"],
               "x_queue_projects": int(qn.get(c, 0)), "x_eia_planned_generators": int(en.get(c, 0))}
        for k in QUEUE_KINDS:
            row[f"x_queue_{k}_mw"] = round(float(qk.loc[c, k]), 2) if c in qk.index else 0.0
        row["x_queue_mw"] = round(sum(row[f"x_queue_{k}_mw"] for k in QUEUE_KINDS), 2)
        row["x_queue_next_in_service"] = qnext.get(c, "")
        for g in EIA_GROUPS:
            row[f"x_eia_{g}_mw"] = round(float(ek.loc[c, g]), 2) if c in ek.index else 0.0
        row["x_eia_planned_mw"] = round(sum(row[f"x_eia_{g}_mw"] for g in EIA_GROUPS), 2)
        rows.append(row)
    out = pd.DataFrame(rows)[ENTITY_COLS + EXTRA].sort_values("entity_id").reset_index(drop=True)
    counties = {key(c) for c in nodes["x_county"]}
    stats = {"nodes": len(out), "counties": len(counties), "queue_active": len(q), "queue_mw": float(q["mw"].sum()),
             "queue_in_node_counties": int(q["county_k"].isin(counties).sum()), "eia_tx": len(e),
             "eia_in_node_counties": int(e["county_k"].isin(counties).sum()),
             "counties_without_queue": len([c for c in counties if c not in qn.index])}
    return out, stats


def main(argv=None):
    ap = argparse.ArgumentParser(description="The planned generation in a placed ERCOT node's county")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    args = ap.parse_args(argv)
    paths = {t: os.path.join(ip.OUT_DIR, t + ".csv") for t in (NODES, QUEUE, EIA)}
    if args.out_dir:
        raw_dir = ip.RAW_DIR
        ip.set_out_dir(args.out_dir)
        ip.RAW_DIR = raw_dir
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{NAME}_{run_id}.log"))
    try:
        nodes = read_table(paths[NODES], ["entity_id", "name", "x_county", "x_zone"])
        queue = read_table(paths[QUEUE], ["status", "county", "capacity_mw", "fuel_technology", "proposed_in_service_date"])
        eia = read_table(paths[EIA], ["state", "county", "nameplate_mw", "technology_group"])
        retrieved = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        t, c = build(nodes, queue, eia, retrieved)
        header = [
            "Energy Research Warehouse (ERW): the planned generation in each placed ERCOT resource node's county: ERCOT's active queue projects and EIA-860M's planned generators (session 931)",
            "Shape: entities (docs/datastandard.md v0). entity_id ercot_node:<settlement point> (as ercot_node_places); entity_type generator; x_county, x_zone "
            "ercot_node_places'; x_queue_* ERCOT's active interconnection queue projects in the county (count, MW, MW by solar, wind, storage, gas, other; "
            "the earliest proposed in-service date); x_eia_* EIA-860M's planned generators in the county (count, nameplate MW, MW by technology group).",
            f"{c['nodes']:,} nodes in {c['counties']} counties. ERCOT's queue: {c['queue_active']:,} active projects ({c['queue_mw']:,.0f} MW), "
            f"{c['queue_in_node_counties']:,} of them in a node's county; {c['counties_without_queue']} of the counties have none (zeros). "
            f"EIA-860M: {c['eia_tx']} planned generators in Texas, {c['eia_in_node_counties']} in a node's county. A project in the county is not a "
            "project at the node. Nothing is filled.",
            f"Derived from: {NODES}; {QUEUE}; {EIA}",
            f"Built by warehouse/derived/ercot_node_planned_generation.py; method docs/methods/ercot_node_planned_generation.md. Retrieved: {run_id} (UTC), computed from the tables held; no request was made.",
            f"Run log: warehouse/output/logs/{NAME}_{run_id}.log",
            "Source: ercot:interconnection_queue Electric Reliability Council of Texas (ERCOT), GIS report; eia:eia860m U.S. Energy Information "
            "Administration, Form EIA-860M; ercot:cdr ERCOT, Capacity, Demand and Reserves Report (the nodes' counties, through ercot_node_places)",
            "License: ERCOT's (read 2 of license_reads.csv) and EIA's (public); the join is the ERW's.",
        ]
        ip.write_snapshot(t, NAME, header, log, cols=ENTITY_COLS + EXTRA)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Energy Research Warehouse (ERW), derived",
                                    report="The planned generation in a placed ERCOT node's county (docs/methods/ercot_node_planned_generation.md)",
                                    report_url=METHOD, document_list="docs/methods/ercot_node_planned_generation.md", license="public", tables=[NAME])])
        print(f"{NAME}: {c['nodes']:,} nodes, {c['counties']} counties; queue {c['queue_in_node_counties']} of {c['queue_active']} in node counties")
        rc = 0
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED, no output file written:\n{tb}")
        print(f"{NAME} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        rc = 1
    log.close()
    return rc


if __name__ == "__main__":
    sys.exit(main())
