# Session 10233: the live catalogue as the loader would write it (warehouse/supabase/load.py: coverage.csv less
# live_set.yaml's catalogue_hold, in_live_set "yes", "no" or "review" by the live-set rules and review_hold) and as the
# anon key reads it (row-level security: license = 'public'), for drawing /data with the site's own code without a
# request to the database. Assumes the loading machine holds every table (the data machine does).
#   python runs/c10233/make_catalogue.py <worktree> <out.json>
import csv
import json
import os
import re
import sys

import yaml

ROOT, OUT = sys.argv[1], sys.argv[2]
P = lambda *a: os.path.join(ROOT, *a)
live = yaml.safe_load(open(P("warehouse", "supabase", "live_set.yaml"), encoding="utf-8"))
full, recent = live.get("full") or [], (live.get("recent") or {}).get("tables") or []
chold, rhold = set(live.get("catalogue_hold") or []), set(live.get("review_hold") or [])
with open(P("warehouse", "metadata", "coverage.csv"), encoding="utf-8", newline="") as f:
    cov = list(csv.DictReader(f))
rows = []
for r in cov:
    if r["table"] in chold or r["license"] != "public":
        continue
    isl = any(re.match(p, r["table"]) for p in full) or any(re.match(p, r["table"]) for p in recent)
    row = {("table_name" if k == "table" else k): (None if v == "" else v) for k, v in r.items()}
    for k in ("n_nodes", "n_rows"):
        row[k] = None if row.get(k) is None else int(row[k])
    row["in_live_set"] = ("review" if r["table"] in rhold else "yes") if isl else "no"
    rows.append(row)
rows.sort(key=lambda x: x["table_name"])
json.dump(rows, open(OUT, "w", encoding="utf-8"))
print(f"{len(rows)} catalogue rows as the anon key reads them; {sum(1 for x in rows if x['in_live_set'] == 'review')} under review")
