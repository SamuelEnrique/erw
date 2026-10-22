#!/usr/bin/env python3
"""Where can a large load go: the site's own files for the All grids tab of /cost-of-power (session 700).

Energy Research Warehouse (ERW). No warehouse table is written and no request is made: this reads tables this machine
holds and writes the tab's files under site/data/siting/. Method: docs/methods/siting.md. The hub and zone rows and
their prices are "Your load"'s own files (site/data/datacenter, warehouse/derived/datacenter_page.py), never rebuilt here.

    python warehouse/derived/siting_page.py                                  # the tables from warehouse/output
    python warehouse/derived/siting_page.py --in-dir runs/archive_restore    # a table not in warehouse/output is read
                                                                             # from these directories, in order
    python warehouse/derived/siting_page.py --out-dir DIR                    # a trial: the files under DIR

Files:
    nodes.json    every settlement point of node_basis_daily that is neither a hub nor a load zone: its id, its class and
                  ERCOT's resource types at it (x_class, x_resource_type), and its day-ahead basis to HB_HUBAVG by Central
                  month, {"YYYY-MM": [mean of the daily basis, days held]}, USD/MWh to four decimals. The node's
                  twelve-month price on the page is the hub's own twelve-month mean plus the mean of these days.
    ercot_4cp.json  (session 702) ERCOT's four coincident-peak intervals by summer from ercot_4cp_intervals: each
                  interval's start in UTC, its local time as ERCOT prints it, and ERCOT's load in it (MW); the summers
                  held and the table's own note of what is not held.
    capacity.json (session 704) the capacity table's newest delivery period of each market, its auction, unit and
                  license, and the zones that auction priced; NO PRICE. iso_all_capacity_prices is internal (the
                  publishers' terms bar republishing) and the repository is public: the tab draws each price as
                  "license needed". With --internal FILE the prices are computed here, per row of the tab, in USD per
                  MWh for a load that runs every hour, and written to FILE (outside the repository; never committed).
    connect.json  (session 705) from lbnl_interconnection_queue (public): by grid, the median, quartiles and count of the
                  months from queue entry (q_date) to commercial operation (on_date) of the requests operational and
                  online in the last three whole years of the file's edition; no median under five requests.
    headroom.json (session 706) from eia860m_planned_generators (public): by grid (balancing authority), the MW and
                  count of generators due to operate in the twelve months after the table's vintage month, by EIA's
                  status: under construction or complete (U, V, TS), approvals received (T), and the rest (P, L); and
                  from eia_state_capacity_annual (public) the newest year's installed net summer capacity of the grids
                  that are whole states (NYISO: New York; ISO-NE: the six New England states).

Each file names the table it was read from, the table's first and last day and when it was built. A table that cannot
be found stops the run (exit 1): no file is written from part of a table.
"""

import argparse
import datetime as dt
import json
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
SITE_DIR = os.path.join(ROOT, "site", "data", "siting")
OUTPUT = os.path.join(ROOT, "warehouse", "output")
NODE_TABLE = "node_basis_daily"
CP_TABLE = "ercot_4cp_intervals"
CAP_TABLE = "iso_all_capacity_prices"
CAP_MARKETS = ["pjm_bra", "isone_fca", "miso_pra", "nyiso_icap_spot"]
LBNL_TABLE = "lbnl_interconnection_queue"
LBNL_GRIDS = {"ERCOT": "ercot", "CAISO": "caiso", "NYISO": "nyiso", "ISO-NE": "isone", "SPP": "spp", "MISO": "miso", "PJM": "pjm"}
MIN_N = 5
PLANNED_TABLE, STATECAP_TABLE = "eia860m_planned_generators", "eia_state_capacity_annual"
BA_GRIDS = {"ERCO": "ercot", "CISO": "caiso", "NYIS": "nyiso", "ISNE": "isone", "SWPP": "spp", "MISO": "miso", "PJM": "pjm"}
WHOLE_STATES = {"nyiso": ["NY"], "isone": ["CT", "MA", "ME", "NH", "RI", "VT"]}
CONSTRUCTION, APPROVED = {"U", "V", "TS"}, {"T"}
PER_MW_YEAR = {"USD/MW-day": 365.0, "USD/kW-month": 12000.0}   # to USD per MW a year


def header_rows(path):
    """The count of the file's leading '#' lines (its provenance header)."""
    n = 0
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.startswith("#"):
                break
            n += 1
    return n


def find(table, dirs):
    for d in [OUTPUT, *dirs]:
        p = os.path.join(d, f"{table}.csv")
        if os.path.exists(p):
            return p
    raise FileNotFoundError(f"{table}.csv is in none of: {', '.join([OUTPUT, *dirs])}")


def nodes_file(path):
    """nodes.json's content from node_basis_daily."""
    cols = ["entity", "variable", "ts_utc", "value", "x_resource_type", "x_class"]
    keep = []
    for ch in pd.read_csv(path, skiprows=header_rows(path), usecols=cols, dtype={"value": float, "x_resource_type": str}, chunksize=500_000):
        keep.append(ch[ch["variable"].isin(["dam_basis", "dam_mean"])])
    d = pd.concat(keep, ignore_index=True)
    first, last = d["ts_utc"].min()[:10], d["ts_utc"].max()[:10]
    points = d["entity"].nunique()
    kinds = d.drop_duplicates("entity").set_index("entity")["x_class"]
    hubs, zones = int((kinds == "hub").sum()), int((kinds == "zone").sum())
    b = d[(d["variable"] == "dam_basis") & ~d["x_class"].isin(["hub", "zone"])].copy()
    b["m"] = b["ts_utc"].str[:7]
    g = b.groupby(["entity", "m"])["value"].agg(["mean", "count"]).reset_index()
    meta = b.drop_duplicates("entity").set_index("entity")[["x_class", "x_resource_type"]]
    nodes = []
    for ent, rows in g.groupby("entity"):
        nodes.append({
            "id": ent.split(":", 1)[1], "cls": str(meta.at[ent, "x_class"]), "types": "" if pd.isna(meta.at[ent, "x_resource_type"]) else str(meta.at[ent, "x_resource_type"]),
            "dam_basis": {r.m: [round(float(r.mean), 4), int(r.count)] for r in rows.itertuples()},
        })
    # a node with no day-ahead basis day is still a node of the table (a point held only in real time)
    for ent in sorted(set(kinds.index[~kinds.isin(["hub", "zone"])]) - set(g["entity"])):
        nodes.append({"id": ent.split(":", 1)[1], "cls": str(kinds[ent]), "types": "", "dam_basis": {}})
    nodes.sort(key=lambda n: n["id"])
    return {"table": NODE_TABLE, "built": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "first": first, "last": last,
            "points": int(points), "hubs": hubs, "zones": zones, "nodes": nodes}


def cp_file(path):
    """ercot_4cp.json's content from ercot_4cp_intervals (session 702)."""
    d = pd.read_csv(path, skiprows=header_rows(path), dtype=str)
    d = d[d["variable"] == "cp4_load_mw"].sort_values("ts_utc")
    with open(path, encoding="utf-8") as f:
        head = [ln[2:].rstrip() for ln in f if ln.startswith("#")]
    held = next((h for h in head if h.startswith("Years held:")), "")
    summers = {}
    for r in d.itertuples():
        summers.setdefault(str(r.x_year), []).append({"ts": r.ts_utc, "local": r.x_interval_local, "mw": round(float(r.value), 3)})
    return {"table": CP_TABLE, "built": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "note": held,
            "summers": [{"year": int(y), "intervals": v} for y, v in sorted(summers.items())]}


def cap_frame(path):
    d = pd.read_csv(path, skiprows=header_rows(path), dtype=str)
    d = d[d["market"].isin(CAP_MARKETS) & (d["variable"] == "capacity_price")]
    return d


def cap_file(path):
    """capacity.json's content (session 704): the newest period of each market and its zones, no price."""
    d = cap_frame(path)
    markets = {}
    for m in CAP_MARKETS:
        x = d[d["market"] == m]
        last = x["ts_utc"].max()
        y = x[x["ts_utc"] == last]
        markets[m] = {"market": m, "table": CAP_TABLE, "license": "internal", "unit": str(y["unit"].iloc[0]), "period_start": last,
                      "period_end": str(y["x_period_end"].iloc[0]), "auction": str(y["x_auction"].iloc[0]), "zones": sorted(y["entity"].unique().tolist())}
    return {"built": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "tables": [CAP_TABLE], "markets": markets}


def cap_internal(path, rows):
    """The tab's capacity figures, USD per MWh for a load that runs every hour, per row: never written to the site."""
    d = cap_frame(path)
    out = {}
    for r in rows:
        m = d[(d["market"] == r["market"]) & (d["entity"] == r["entity"]) & (d["ts_utc"] == r["period_start"])]
        if len(m) != 1:
            continue
        v = float(m["value"].iloc[0]) * PER_MW_YEAR[m["unit"].iloc[0]]
        out[r["row"]] = {"entity": r["entity"], "auction": r["auction"], "as_published": float(m["value"].iloc[0]), "unit": m["unit"].iloc[0], "usd_per_mw_year": v, "usd_per_mwh_every_hour": v / 8760}
    return out


def connect_file(path):
    """connect.json's content (session 705)."""
    d = pd.read_csv(path, skiprows=header_rows(path), dtype=str, usecols=["region", "q_status", "q_date", "on_date", "vintage"])
    vintage = str(d["vintage"].dropna().iloc[0])
    o = d[d["q_status"] == "operational"].copy()
    o["q"], o["on"] = pd.to_datetime(o["q_date"], errors="coerce"), pd.to_datetime(o["on_date"], errors="coerce")
    o = o.dropna(subset=["q", "on"])
    last = int(o["on"].dt.year.max())
    first = last - 2
    o = o[(o["on"].dt.year >= first) & (o["on"].dt.year <= last) & (o["on"] >= o["q"])]
    o["months"] = (o["on"] - o["q"]).dt.days / 30.4375
    grids = {}
    for region, g in LBNL_GRIDS.items():
        m = o.loc[o["region"] == region, "months"]
        n = int(len(m))
        ok = n >= MIN_N
        grids[g] = {"n": n, "median": round(float(m.median()), 2) if ok else None, "p25": round(float(m.quantile(0.25)), 2) if ok else None,
                    "p75": round(float(m.quantile(0.75)), 2) if ok else None}
    return {"table": LBNL_TABLE, "built": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "vintage": vintage, "from": first, "to": last, "min_n": MIN_N, "grids": grids}


def headroom_file(ppath, cpath):
    """headroom.json's content (session 706)."""
    with open(ppath, encoding="utf-8") as fh:
        head = [ln for ln in fh if ln.startswith("#")]
    vintage = next((h.split("vintage")[-1].strip() for h in head if "vintage" in h), "")
    p = pd.read_csv(ppath, skiprows=header_rows(ppath), dtype=str, usecols=["balancing_authority", "eia_status", "planned_operation_date", "nameplate_mw"])
    v0 = pd.Period(vintage, "M")
    first, last = (v0 + 1).strftime("%Y-%m"), (v0 + 12).strftime("%Y-%m")
    p["m"] = p["planned_operation_date"].str[:7]
    p = p[(p["m"] >= first) & (p["m"] <= last)]
    p["mw"] = pd.to_numeric(p["nameplate_mw"], errors="coerce").fillna(0.0)
    planned = {}
    for ba, g in BA_GRIDS.items():
        x = p[p["balancing_authority"] == ba]
        c, a = x[x["eia_status"].isin(CONSTRUCTION)], x[x["eia_status"].isin(APPROVED)]
        o = x[~x["eia_status"].isin(CONSTRUCTION | APPROVED)]
        planned[g] = {"construction_mw": round(float(c["mw"].sum()), 1), "construction_n": int(len(c)), "approved_mw": round(float(a["mw"].sum()), 1),
                      "approved_n": int(len(a)), "other_mw": round(float(o["mw"].sum()), 1), "other_n": int(len(o))}
    s = pd.read_csv(cpath, skiprows=header_rows(cpath), dtype=str, usecols=["entity", "ts_utc", "value"])
    s = s[s["entity"].str.endswith(":TOT:ALL")]
    s["state"] = s["entity"].str.split(":").str[1]
    year = int(s["ts_utc"].max()[:4])
    s = s[s["ts_utc"].str[:4] == str(year)]
    cap = {}
    for g, states in WHOLE_STATES.items():
        x = s[s["state"].isin(states)]
        if len(x) == len(states):
            cap[g] = {"states": states, "year": year, "mw": round(float(pd.to_numeric(x["value"]).sum()), 1)}
    return {"built": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "planned_table": PLANNED_TABLE, "vintage": vintage, "from": first, "to": last,
            "planned": planned, "capacity_table": STATECAP_TABLE, "capacity": cap}


def write(name, obj, out_dir):
    """Write a file, unless it holds the same content but for its build time (no change, no new commit)."""
    os.makedirs(out_dir, exist_ok=True)
    p = os.path.join(out_dir, name)
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            old = json.load(f)
        if {k: v for k, v in old.items() if k != "built"} == {k: v for k, v in obj.items() if k != "built"}:
            print(f"kept {p}: the same content")
            return
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, separators=(",", ":"), ensure_ascii=False)
        f.write("\n")
    print(f"wrote {p} ({os.path.getsize(p):,} bytes)")


def main(argv=None):
    ap = argparse.ArgumentParser(description="The All grids tab's files for /cost-of-power")
    ap.add_argument("--in-dir", action="append", default=[], help="a directory to read a table from when warehouse/output lacks it")
    ap.add_argument("--out-dir", default=SITE_DIR, help="where the files go (default site/data/siting)")
    ap.add_argument("--internal", help="session 704: write the capacity prices per row to this file (outside the repository)")
    ap.add_argument("--rows", help="with --internal: the tab's rows and their capacity zones as JSON (node scripts/siting-files.mjs capzones)")
    a = ap.parse_args(argv)
    try:
        path = find(NODE_TABLE, a.in_dir)
        print(f"reading {path}")
        f = nodes_file(path)
    except Exception as e:  # loud: no file from part of a table
        print(f"FAILED: {e}", file=sys.stderr)
        return 1
    print(f"{NODE_TABLE}: {f['points']} points, {f['hubs']} hubs, {f['zones']} zones, {len(f['nodes'])} nodes, {f['first']} to {f['last']}")
    try:
        cpath = find(CP_TABLE, a.in_dir)
        print(f"reading {cpath}")
        cp = cp_file(cpath)
    except Exception as e:
        print(f"FAILED: {e}", file=sys.stderr)
        return 1
    print(f"{CP_TABLE}: {len(cp['summers'])} summers, {sum(len(s['intervals']) for s in cp['summers'])} intervals")
    try:
        kpath = find(CAP_TABLE, a.in_dir)
        print(f"reading {kpath}")
        cap = cap_file(kpath)
    except Exception as e:
        print(f"FAILED: {e}", file=sys.stderr)
        return 1
    print(f"{CAP_TABLE}: " + "; ".join(f"{m['auction']} ({len(m['zones'])} zones)" for m in cap["markets"].values()))
    write("nodes.json", f, a.out_dir)
    write("ercot_4cp.json", cp, a.out_dir)
    write("capacity.json", cap, a.out_dir)
    try:
        lpath = find(LBNL_TABLE, a.in_dir)
        print(f"reading {lpath}")
        con = connect_file(lpath)
    except Exception as e:
        print(f"FAILED: {e}", file=sys.stderr)
        return 1
    print(f"{LBNL_TABLE}: " + "; ".join(f"{g} {v['median']} ({v['n']})" for g, v in con["grids"].items()))
    write("connect.json", con, a.out_dir)
    try:
        ppath, spath = find(PLANNED_TABLE, a.in_dir), find(STATECAP_TABLE, a.in_dir)
        print(f"reading {ppath} and {spath}")
        hr = headroom_file(ppath, spath)
    except Exception as e:
        print(f"FAILED: {e}", file=sys.stderr)
        return 1
    print(f"{PLANNED_TABLE} {hr['from']} to {hr['to']}: " + "; ".join(f"{g} {v['construction_mw']}" for g, v in hr["planned"].items()))
    write("headroom.json", hr, a.out_dir)
    if a.internal:
        if not a.rows:
            print("FAILED: --internal needs --rows", file=sys.stderr)
            return 1
        with open(a.rows, encoding="utf-8") as fh:
            rows = json.load(fh)
        got = cap_internal(kpath, rows)
        with open(a.internal, "w", encoding="utf-8") as fh:
            json.dump({"table": CAP_TABLE, "license": "internal: never in the repository", "rows": got}, fh, indent=1)
        print(f"wrote {a.internal}: {len(got)} rows (internal, outside the repository)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
