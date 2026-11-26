"""energy_companies.csv (the main copy's, read only) as the live set would serve it to lib/data.ts companies(): the
entity columns and each extra field by name, an empty value as null. Written to runs/c10228/energy_companies.json for
draw_companies.mjs. Session 10228."""
import csv
import io
import json
import os

SRC = r"C:\Users\lossa\Documents\erw\warehouse\output\energy_companies.csv"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "energy_companies.json")
F = ["description", "sector", "niche_tags", "stage", "raised", "location", "founders", "website", "sources", "confidence",
     "confidence_note", "first_seen"]
lines = [ln for ln in open(SRC, encoding="utf-8") if not ln.startswith("#")]
rows = list(csv.DictReader(io.StringIO("".join(lines))))
out = []
for r in sorted(rows, key=lambda r: r["name"]):
    o = {"entity_id": r["entity_id"], "name": r["name"], "source_url": r.get("source_url") or None}
    for k in F:
        o[k] = r.get(k) or None
    out.append(o)
json.dump(out, open(OUT, "w", encoding="utf-8"))
print(len(out), "rows written")
