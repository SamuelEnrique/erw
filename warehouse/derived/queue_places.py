#!/usr/bin/env python3
"""ERW: interconnection queues outside the seven grids, by place: the page file site/data/queue_places.json (session 8014, chain 581 part F2).

Energy Research Warehouse (ERW). Writes one new page file; no table, no request. Read by /queues/places. Method:
docs/methods/queue_places.md.

The warehouse holds the queues outside the seven ISOs in one table: Lawrence Berkeley National Laboratory's "Queued Up"
compilation (lbnl_interconnection_queue), whose rows of the regions "West" and "Southeast" are the public queues of the
utilities and federal power marketers there, each under LBNL's own name of the queue's owner (lbnl_entity). For each
owner: its entries by LBNL's status, the MW by status and by type, the states its entries name, and the active MW by the
year each entered. For each state with a population outside the seven grids (site/data/states/, from eia_county_region):
whether any entry of LBNL's West or Southeast names it; a state with none is listed as such. Nothing is matched by name:
an owner keeps LBNL's name, and a state is joined by its two-letter code alone.

    python warehouse/derived/queue_places.py                # site/data/queue_places.json
    python warehouse/derived/queue_places.py --site-dir DIR # a trial
"""
import argparse
import datetime as dt
import json
import os
import sys

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import iso_prices as ip  # noqa: E402

OUT = os.path.join(ROOT, "warehouse", "output")
SITE_FILE = os.path.join(ROOT, "site", "data", "queue_places.json")
REGIONS = ("West", "Southeast")
STATUSES = ["active", "suspended", "operational", "withdrawn", "unknown"]


def r1(v):
    return None if v is None or pd.isna(v) else round(float(v), 1)


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW: queues outside the seven grids, by place")
    ap.add_argument("--site-dir")
    a = ap.parse_args(argv)
    p = os.path.join(OUT, "lbnl_interconnection_queue.csv")
    fh = open(p, "rb")
    for _ in range(ip.header_rows(p)):
        fh.readline()
    d = pd.read_csv(fh, dtype=str, keep_default_na=False)
    fh.close()
    vintage = d["vintage"].iloc[0]
    d = d[d["region"].isin(REGIONS)].copy()
    d["mw"] = pd.to_numeric(d["capacity_mw"], errors="coerce")
    owners = []
    for (region, ent), g in d.groupby(["region", "lbnl_entity"]):
        act = g[g["q_status"] == "active"]
        owners.append({
            "owner": ent, "region": region, "entries": int(len(g)),
            "by_status": {s: {"entries": int((g["q_status"] == s).sum()), "mw": r1(g.loc[g["q_status"] == s, "mw"].sum())} for s in STATUSES if (g["q_status"] == s).any()},
            "active_mw_by_type": {t: r1(x["mw"].sum()) for t, x in act.groupby("type_clean")},
            "active_mw_by_year": {y.split(".")[0]: r1(x["mw"].sum()) for y, x in act.groupby("q_year") if y},
            "states": {st: int(n) for st, n in g["state"].value_counts().items() if st},
            "first_year": min((y.split(".")[0] for y in g["q_year"] if y), default=None),
            "last_year": max((y.split(".")[0] for y in g["q_year"] if y), default=None),
        })
    owners.sort(key=lambda o: -(o["by_status"].get("active", {}).get("mw") or 0))
    # the states with people outside the seven grids, from the states' page files
    idx_path = os.path.join(ROOT, "site", "data", "states", "index.json")
    states = []
    if os.path.exists(idx_path):
        with open(idx_path, encoding="utf-8") as f:
            idx = json.load(f)
        for row in idx["states"]:
            st = row["state"]
            if st == "US":
                continue
            with open(os.path.join(ROOT, "site", "data", "states", row["file"]), encoding="utf-8") as f:
                serving = json.load(f)["serving"]
            outside = (serving.get("by_grid_pct") or {}).get("none of the seven")
            if not outside:   # a state with no share outside the seven grids (or none computed, Connecticut's) is not listed
                continue
            g = d[d["state"] == st]
            states.append({"state": st, "name": row["name"], "share_outside_pct": outside,
                           "entries": int(len(g)), "active_entries": int((g["q_status"] == "active").sum()),
                           "active_mw": r1(g.loc[g["q_status"] == "active", "mw"].sum()) if len(g) else None,
                           "owners": sorted(g["lbnl_entity"].unique().tolist()),
                           "no_public_queue": len(g) == 0})
        states.sort(key=lambda s: s["state"])
    doc = {"built": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "method": "docs/methods/queue_places.md", "license": "public",
           "tables": ["lbnl_interconnection_queue", "eia_county_region", "census_county_population"], "vintage": vintage,
           "source": "Lawrence Berkeley National Laboratory, Queued Up: interconnection queue data (the regions West and Southeast, outside the ISOs), as the ERW's table lbnl_interconnection_queue holds it",
           "rule": "Each queue owner under LBNL's own name; MW is LBNL's capacity of the entry; nothing matched by name. A state is listed when some of its people live outside the seven grids (eia_county_region and the Census Bureau's county estimates); 'no public queue' means no entry of LBNL's West or Southeast names it.",
           "owners": owners, "states": states}
    path = os.path.join(a.site_dir, "queue_places.json") if a.site_dir else SITE_FILE
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, separators=(",", ":"), allow_nan=False)
    print(f"queue_places: {len(owners)} owners, {len(states)} states ({sum(s['no_public_queue'] for s in states)} with no entry); {os.path.getsize(path):,} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
