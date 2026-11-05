#!/usr/bin/env python3
"""ERCOT's transmission projects by a resource node's county: for each node ercot_node_places places, the project phases
of ERCOT's Transmission Project and Information Tracking report (TPIT) that begin or end in its county, counted by status,
with their new circuit miles, highest voltage and next projected in-service date (session 917, chain 051: the siting
gaps' "ERCOT nodes | Node panel | transmission projects by county", session 703).

Energy Research Warehouse (ERW) derived table, warehouse/output/ercot_node_transmission.csv, computed from two ERW tables,
no request:

    ercot_node_places            the placed resource nodes with their county and load zone (session 901)
    ercot_transmission_projects  every TPIT project phase, its status, kV, circuit miles, counties and dates (session 852)

The match: a phase touches a county when its start county or its end county (x_county_start, x_county_end) is that
county, compared in capitals with spaces trimmed; a line from one county to another counts in both. A node's county with
no phase has zeros: TPIT lists every project the transmission owners report, so none is a count, not a gap. "Open" is
TPIT's future and planned sheets together.

    entity_id   ercot_node:<settlement point> (as ercot_node_places); entity_type generator; name the settlement point;
                geo US-TX; x_county and x_zone ercot_node_places'
    x_*         x_phases_future, x_phases_planned, x_phases_completed, x_phases_cancelled (phases touching the county);
                x_open_projects (distinct project numbers among the open phases); x_open_new_circuit_miles and
                x_open_upgraded_circuit_miles (summed over the open phases); x_open_max_kv; x_open_next_in_service (the
                earliest projected in-service date among the open phases); x_tpit_edition (the workbook's line)

    python warehouse/derived/ercot_node_transmission.py [--out-dir DIR]
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

NODES, TPIT = "ercot_node_places", "ercot_transmission_projects"
NAME = "ercot_node_transmission"
SOURCE = "erw:ercot_node_transmission"
ENTITY_COLS = ["entity_id", "entity_type", "name", "geo", "lat", "lon", "capacity_mw", "status", "status_date", "operator",
               "source", "source_url", "retrieved_at", "vintage"]
SHEETS = ["future", "planned", "completed", "cancelled"]
EXTRA = ["x_county", "x_zone"] + [f"x_phases_{s}" for s in SHEETS] + [
    "x_open_projects", "x_open_new_circuit_miles", "x_open_upgraded_circuit_miles", "x_open_max_kv", "x_open_next_in_service", "x_tpit_edition"]
METHOD = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/ercot_node_transmission.md"


def read_table(path, cols=None):
    n, head = 0, []
    with open(path, encoding="utf-8") as f:
        for ln in f:
            if not ln.startswith("#"):
                break
            n += 1
            head.append(ln[1:].strip())
    return pd.read_csv(path, skiprows=n, dtype=str, keep_default_na=False, usecols=cols), head


def key(s):
    return re.sub(r"\s+", " ", str(s)).strip().upper()


def build(nodes, tpit, retrieved, edition):
    unknown = sorted(set(tpit["status"]) - set(SHEETS))
    if unknown:
        raise RuntimeError(f"a TPIT status not in the map: {unknown}")
    t = tpit.copy()
    for c in ("x_kv", "x_new_circuit_miles", "x_upgraded_circuit_miles"):
        t[c] = pd.to_numeric(t[c], errors="coerce")
    long = pd.concat([t.assign(county=t["x_county_start"].map(key)), t.assign(county=t["x_county_end"].map(key))])
    long = long[long["county"] != ""].drop_duplicates(["event_id", "county"])   # a phase within one county counts once
    counts = long.pivot_table(index="county", columns="status", values="event_id", aggfunc="count").reindex(columns=SHEETS).fillna(0)
    op = long[long["status"].isin(["future", "planned"])]
    proj = op.groupby("county")["x_project_number"].nunique()
    miles_new = op.groupby("county")["x_new_circuit_miles"].sum()
    miles_up = op.groupby("county")["x_upgraded_circuit_miles"].sum()
    kv = op.groupby("county")["x_kv"].max()
    nxt = op[op["x_date_kind"] == "projected"].groupby("county")["event_date"].min()
    n = nodes.copy()
    n["county"] = n["x_county"].map(key)
    if (n["county"] == "").any():
        raise RuntimeError("a placed node without a county")

    def get(s, c, zero=0):
        return s.get(c, zero) if c in s.index else zero

    rows = []
    for _, r in n.iterrows():
        c = r["county"]
        row = {"entity_id": r["entity_id"], "entity_type": "generator", "name": r["name"], "geo": "US-TX", "lat": "", "lon": "",
               "capacity_mw": "", "status": "", "status_date": "", "operator": "", "source": SOURCE, "source_url": METHOD,
               "retrieved_at": retrieved, "vintage": "", "x_county": r["x_county"], "x_zone": r["x_zone"]}
        for s in SHEETS:
            row[f"x_phases_{s}"] = int(counts.loc[c, s]) if c in counts.index else 0
        row["x_open_projects"] = int(get(proj, c))
        row["x_open_new_circuit_miles"] = round(float(get(miles_new, c)), 2)
        row["x_open_upgraded_circuit_miles"] = round(float(get(miles_up, c)), 2)
        k = get(kv, c, None)
        row["x_open_max_kv"] = "" if k is None or pd.isna(k) else int(k) if float(k).is_integer() else float(k)
        row["x_open_next_in_service"] = get(nxt, c, "") or ""
        row["x_tpit_edition"] = edition
        rows.append(row)
    out = pd.DataFrame(rows).sort_values("entity_id").reset_index(drop=True)
    stats = {"nodes": len(out), "counties": n["county"].nunique(),
             "counties with no phase": int(sum(1 for c in n["county"].unique() if c not in counts.index)),
             "tpit counties": long["county"].nunique()}
    return out, stats


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERCOT's TPIT projects by a resource node's county")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    args = ap.parse_args(argv)
    paths = {t: os.path.join(ip.OUT_DIR, t + ".csv") for t in (NODES, TPIT)}
    if args.out_dir:
        raw_dir = ip.RAW_DIR
        ip.set_out_dir(args.out_dir)
        ip.RAW_DIR = raw_dir
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{NAME}_{run_id}.log"))
    try:
        nodes, _ = read_table(paths[NODES], ["entity_id", "name", "x_county", "x_zone"])
        tpit, head = read_table(paths[TPIT], ["event_id", "event_date", "status", "x_project_number", "x_kv", "x_new_circuit_miles",
                                              "x_upgraded_circuit_miles", "x_county_start", "x_county_end", "x_date_kind"])
        edition = next((h.split(";")[0].replace("Workbook: ", "") for h in head if h.startswith("Workbook:")), "")
        retrieved = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        t, c = build(nodes, tpit, retrieved, edition)
        header = [
            "Energy Research Warehouse (ERW): ERCOT's transmission projects (TPIT) by the county of each placed resource node (session 917)",
            "Shape: entities (docs/datastandard.md v0). entity_id ercot_node:<settlement point> (as ercot_node_places); entity_type generator; x_county, x_zone "
            "ercot_node_places'; x_phases_<future|planned|completed|cancelled> TPIT phases whose start or end county is the node's; x_open_* over the future "
            "and planned phases: distinct projects, new and upgraded circuit miles summed, highest kV, earliest projected in-service date.",
            f"{c['nodes']:,} nodes in {c['counties']} counties; {c['counties with no phase']} of those counties have no TPIT phase (zeros: TPIT lists every "
            f"project the owners report); TPIT names {c['tpit counties']} counties. A line between two counties counts in both. Nothing is filled.",
            f"Derived from: {NODES}; {TPIT} ({edition})",
            f"Built by warehouse/derived/ercot_node_transmission.py; method docs/methods/ercot_node_transmission.md. Retrieved: {run_id} (UTC), computed from the tables held; no request was made.",
            f"Run log: warehouse/output/logs/{NAME}_{run_id}.log",
            "Source: ercot:tpit Electric Reliability Council of Texas (ERCOT), Transmission Project and Information Tracking; ercot:cdr ERCOT, Capacity, Demand "
            "and Reserves Report (the nodes' counties, through ercot_node_places)",
            "License: ERCOT's (its terms, read 2 of license_reads.csv, allow it); the join is the ERW's.",
        ]
        ip.write_snapshot(t, NAME, header, log, cols=ENTITY_COLS + EXTRA)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Energy Research Warehouse (ERW), derived",
                                    report="ERCOT's TPIT projects by a resource node's county (docs/methods/ercot_node_transmission.md)",
                                    report_url=METHOD, document_list="docs/methods/ercot_node_transmission.md", license="public", tables=[NAME])])
        print(f"{NAME}: {c['nodes']:,} nodes, {c['counties']} counties ({c['counties with no phase']} with no phase)")
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
