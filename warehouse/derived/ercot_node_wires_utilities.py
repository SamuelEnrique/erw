#!/usr/bin/env python3
"""The wires utilities in an ERCOT resource node's county: for each node ercot_node_places places, the utilities EIA-861
lists as serving its county, with the delivery-only companies (Texas's transmission and distribution utilities) among
them named apart (session 945, chain 053: the siting gaps' "a node's wires utility", which chain 072 left open: "the CDR
names no EIA plant number").

Energy Research Warehouse (ERW) derived table, warehouse/output/ercot_node_wires_utilities.csv, computed from four ERW
tables, no request:

    ercot_node_places               the placed resource nodes with their county and load zone (session 901)
    utility_service_territories     EIA-861's utility and county pairs, 2025 (session 667)
    eia861_delivery_only            EIA-861's delivery-only companies (session 853): those of Texas in the latest year
    eia861_utility_data             EIA-861's utility data (NERC regions), the same year

The match: a utility serves a node's county when the territories list the pair (state TX), the county in capitals with
runs of spaces made one. EIA gives no share of a county and no boundary, so a utility serving the county may not serve
the node's site; a transmission-only company (one with no customers) is in no territory and so in no row.

    entity_id   ercot_node:<settlement point> (as ercot_node_places); entity_type generator; geo US-TX; x_county, x_zone
    x_*         x_utilities_n and x_utilities ("<name> (<EIA utility number>)", joined by "; "), x_delivery_only_n and
                x_delivery_only (the delivery-only companies among them), x_outside_tre_n and x_outside_tre (those whose
                EIA-861 utility data names a NERC region but not Texas RE: the county's part outside ERCOT's region),
                x_short_form_n (those filing EIA's short form, which gives no region)

    python warehouse/derived/ercot_node_wires_utilities.py [--out-dir DIR]
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

NODES, TERR, DELIV, UDATA = "ercot_node_places", "utility_service_territories", "eia861_delivery_only", "eia861_utility_data"
NAME = "ercot_node_wires_utilities"
SOURCE = "erw:ercot_node_wires_utilities"
ENTITY_COLS = ["entity_id", "entity_type", "name", "geo", "lat", "lon", "capacity_mw", "status", "status_date", "operator",
               "source", "source_url", "retrieved_at", "vintage"]
EXTRA = ["x_county", "x_zone", "x_utilities_n", "x_utilities", "x_delivery_only_n", "x_delivery_only", "x_outside_tre_n",
         "x_outside_tre", "x_short_form_n"]
NERC = ["x_nerc_tre", "x_nerc_frcc", "x_nerc_mro", "x_nerc_npcc", "x_nerc_rfc", "x_nerc_serc", "x_nerc_spp", "x_nerc_wecc"]
METHOD = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/ercot_node_wires_utilities.md"


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


def build(nodes, terr, deliv, udata, retrieved):
    t = terr[terr["x_state"] == "TX"].copy()
    years = sorted(set(t["x_data_year"]))
    if len(years) != 1:
        raise RuntimeError(f"the territories give more than one year: {years}")
    year = years[0]
    t["county_k"] = t["x_county"].map(key)
    t["label"] = t["name"] + " (" + t["x_utility_number"] + ")"
    d = deliv[(deliv["x_state"] == "TX") & deliv["ts_utc"].str.startswith(year)]
    delivery = set(d["x_utility_number"])
    if not delivery:
        raise RuntimeError(f"no Texas delivery-only company in {DELIV} for {year}")
    u = udata[(udata["x_state"] == "TX") & (udata["x_year"] == year)]
    named = u[u[NERC].eq("Y").any(axis=1)]
    outside = set(named.loc[named["x_nerc_tre"] != "Y", "x_utility_number"])
    short = set(t.loc[t["x_short_form"] == "Y", "x_utility_number"])
    by = {c: g.drop_duplicates("x_utility_number").sort_values("label") for c, g in t.groupby("county_k")}
    rows = []
    for _, r in nodes.iterrows():
        c = key(r["x_county"])
        if not c:
            raise RuntimeError(f"a placed node without a county: {r['entity_id']}")
        if c not in by:
            raise RuntimeError(f"a node's county in no territory: {r['x_county']}")
        g = by[c]
        dl = g[g["x_utility_number"].isin(delivery)]
        ol = g[g["x_utility_number"].isin(outside)]
        rows.append({"entity_id": r["entity_id"], "entity_type": "generator", "name": r["name"], "geo": "US-TX", "lat": "", "lon": "",
                     "capacity_mw": "", "status": "", "status_date": "", "operator": "", "source": SOURCE, "source_url": METHOD,
                     "retrieved_at": retrieved, "vintage": f"EIA-861 {year}", "x_county": r["x_county"], "x_zone": r["x_zone"],
                     "x_utilities_n": len(g), "x_utilities": "; ".join(g["label"]), "x_delivery_only_n": len(dl),
                     "x_delivery_only": "; ".join(dl["label"]), "x_outside_tre_n": len(ol), "x_outside_tre": "; ".join(ol["label"]),
                     "x_short_form_n": int(g["x_utility_number"].isin(short).sum())})
    out = pd.DataFrame(rows)[ENTITY_COLS + EXTRA].sort_values("entity_id").reset_index(drop=True)
    stats = {"nodes": len(out), "counties": out["x_county"].map(key).nunique(), "year": year, "delivery": len(delivery),
             "with_delivery": int((out["x_delivery_only_n"] > 0).sum()), "one_delivery": int((out["x_delivery_only_n"] == 1).sum()),
             "with_outside": int((out["x_outside_tre_n"] > 0).sum())}
    return out, stats


def main(argv=None):
    ap = argparse.ArgumentParser(description="The wires utilities in a placed ERCOT node's county")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    args = ap.parse_args(argv)
    paths = {t: os.path.join(ip.OUT_DIR, t + ".csv") for t in (NODES, TERR, DELIV, UDATA)}
    if args.out_dir:
        raw_dir = ip.RAW_DIR
        ip.set_out_dir(args.out_dir)
        ip.RAW_DIR = raw_dir
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{NAME}_{run_id}.log"))
    try:
        nodes = read_table(paths[NODES], ["entity_id", "name", "x_county", "x_zone"])
        terr = read_table(paths[TERR], ["name", "x_utility_number", "x_state", "x_county", "x_short_form", "x_data_year"])
        deliv = read_table(paths[DELIV], ["ts_utc", "x_utility_number", "x_state"])
        udata = read_table(paths[UDATA], ["x_utility_number", "x_state", "x_year"] + NERC)
        retrieved = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        t, c = build(nodes, terr, deliv, udata, retrieved)
        header = [
            "Energy Research Warehouse (ERW): the wires utilities in each placed ERCOT resource node's county, from EIA-861's service territories, with Texas's delivery-only companies named apart (session 945)",
            "Shape: entities (docs/datastandard.md v0). entity_id ercot_node:<settlement point> (as ercot_node_places); entity_type generator; x_county, x_zone "
            "ercot_node_places'; x_utilities the utilities EIA-861 lists in the county ('<name> (<number>)', '; '); x_delivery_only the delivery-only companies "
            "among them; x_outside_tre those whose EIA-861 utility data names a NERC region but not Texas RE; x_short_form_n those filing the short form.",
            f"{c['nodes']:,} nodes in {c['counties']} counties, EIA-861 {c['year']}. {c['with_delivery']:,} nodes have a delivery-only company in their county "
            f"({c['one_delivery']:,} exactly one) of the {c['delivery']} EIA lists in Texas; {c['with_outside']:,} have a utility outside Texas RE in the county. "
            "A utility serving the county may not serve the node's site; a transmission-only company is in no territory. Nothing is filled.",
            f"Derived from: {NODES}; {TERR}; {DELIV}; {UDATA}",
            f"Built by warehouse/derived/ercot_node_wires_utilities.py; method docs/methods/ercot_node_wires_utilities.md. Retrieved: {run_id} (UTC), computed from the tables held; no request was made.",
            f"Run log: warehouse/output/logs/{NAME}_{run_id}.log",
            "Source: eia:eia861_territory and eia:eia861 U.S. Energy Information Administration, Form EIA-861 (service territories, delivery companies, "
            "utility data); ercot:cdr ERCOT, Capacity, Demand and Reserves Report (the nodes' counties, through ercot_node_places)",
            "License: EIA's (public) and ERCOT's (read 2 of license_reads.csv); the join is the ERW's.",
        ]
        ip.write_snapshot(t, NAME, header, log, cols=ENTITY_COLS + EXTRA)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Energy Research Warehouse (ERW), derived",
                                    report="The wires utilities in a placed ERCOT node's county (docs/methods/ercot_node_wires_utilities.md)",
                                    report_url=METHOD, document_list="docs/methods/ercot_node_wires_utilities.md", license="public", tables=[NAME])])
        print(f"{NAME}: {c['nodes']:,} nodes, {c['counties']} counties; {c['with_delivery']} with a delivery-only company")
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
