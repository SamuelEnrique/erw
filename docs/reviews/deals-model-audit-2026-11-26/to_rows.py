# Session 10215: the rows the deal pages' own functions read, as the live set would serve them, written from the
# warehouse's CSV on disk (no request to any service). The loader's rule (warehouse/supabase/load.py, records, events):
# the event columns with "" as null and mw, price as numbers; every other column into extra, an empty value left out.
# The select of site/lib/data.ts deals(): event_id,event_date,status,mw,price,currency,parties,source,source_url,extra,
# ordered event_date desc then event_id.
#   python runs/c10215/to_rows.py <energy_deals.csv> <rows dir>
import csv
import json
import os
import sys

SRC, ROWS = sys.argv[1], sys.argv[2]
os.makedirs(ROWS, exist_ok=True)
EVENT = ["event_id", "event_date", "event_type", "parties", "entity_ids", "mw", "price", "currency", "status", "source", "source_url"]
SELECT = ["event_id", "event_date", "status", "mw", "price", "currency", "parties", "source", "source_url"]
NUM = {"mw", "price"}

with open(SRC, encoding="utf-8", newline="") as f:
    rows = list(csv.DictReader([ln for ln in f if not ln.startswith("#")]))

out = []
for r in rows:
    o = {}
    for c in SELECT:
        v = r.get(c, "")
        o[c] = None if v == "" else (float(v) if c in NUM else v)
    o["extra"] = {c: v for c, v in r.items() if c not in EVENT and v != ""}
    out.append(o)
out.sort(key=lambda r: r["event_id"])
out.sort(key=lambda r: r["event_date"], reverse=True)
with open(os.path.join(ROWS, "energy_deals.json"), "w", encoding="utf-8") as f:
    json.dump(out, f)
print(json.dumps({"rows": len(out), "first": min(r["event_date"] for r in out), "last": max(r["event_date"] for r in out)}))
