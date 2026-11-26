# Session 10211: the rows the page's own functions read, as the live set would serve them, written from the warehouse's
# CSVs on disk (no request to any service). The loader's rule (warehouse/supabase/load.py, records): the entity columns
# with "" as null and capacity_mw, lat, lon as numbers; every other column into extra, an empty value left out.
#   python runs/c10211/to_rows.py <warehouse output dir> <rows dir>
# Writes datacenter_facilities.json, queue_sites.json (datacenter_queue_positions of the queues not held: ERCOT, CAISO,
# SPP) and queue_active.json (ercot_interconnection_queue rows whose status is active: table_name, capacity_mw, status, zone).
import csv
import json
import os
import sys

OUT, ROWS = sys.argv[1], sys.argv[2]
os.makedirs(ROWS, exist_ok=True)
ENTITY = ["entity_id", "entity_type", "name", "geo", "lat", "lon", "capacity_mw", "status", "status_date", "operator", "source",
          "source_url", "retrieved_at", "vintage"]
NUM = {"lat", "lon", "capacity_mw"}
SELECT = ["entity_id", "entity_type", "name", "lat", "lon", "capacity_mw", "status", "status_date", "operator", "source",
          "source_url", "vintage"]


def table(name):
    with open(os.path.join(OUT, name + ".csv"), encoding="utf-8", newline="") as f:
        return list(csv.DictReader([ln for ln in f if not ln.startswith("#")]))


def live(name, r):
    o = {"table_name": name}
    for c in SELECT:
        v = r.get(c, "")
        o[c] = None if v == "" else (float(v) if c in NUM else v)
    o["extra"] = {c: v for c, v in r.items() if c not in ENTITY and v != ""}
    return o


fac = [live("datacenter_facilities", r) for r in table("datacenter_facilities")]
fac.sort(key=lambda r: r["entity_id"])
json.dump(fac, open(os.path.join(ROWS, "datacenter_facilities.json"), "w", encoding="utf-8"))
qs = []
for r in table("datacenter_queue_positions"):
    g = r["entity_id"].split("_", 1)[0]
    if g in ("ercot", "caiso", "spp"):
        qs.append(live(f"{g}_interconnection_queue", r))
json.dump(sorted(qs, key=lambda r: r["entity_id"]), open(os.path.join(ROWS, "queue_sites.json"), "w", encoding="utf-8"))
act = [{"table_name": "ercot_interconnection_queue", "capacity_mw": (float(r["capacity_mw"]) if r["capacity_mw"] != "" else None),
        "status": r["status"], "zone": (r.get("zone") or None)} for r in table("ercot_interconnection_queue") if r["status"] == "active"]
json.dump(act, open(os.path.join(ROWS, "queue_active.json"), "w", encoding="utf-8"))
print(json.dumps({"facilities": len(fac), "queue_sites": len(qs), "queue_active": len(act)}))
