# Session 10233: the third set of measures (the hold's reach over the grids' own tables, the per-row retrieval time,
# the news index's dated row, the namespaces of three listed tables).
#   python runs/c10233/measures2.py <worktree> <main copy's warehouse/output> <out.json>
# Counts and table names only; the one news_index row printed is from a public table.
import csv
import json
import os
import re
import sys
from collections import Counter

import yaml

ROOT, OUTDIR, OUTJSON = sys.argv[1:4]
P = lambda *a: os.path.join(ROOT, *a)
TODAY = "2026-11-26"
csv.field_size_limit(10 ** 8)


def rows(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


cov = {r["table"]: r for r in rows(P("warehouse", "metadata", "coverage.csv"))}
live = yaml.safe_load(open(P("warehouse", "supabase", "live_set.yaml"), encoding="utf-8"))
full, recent = live.get("full") or [], (live.get("recent") or {}).get("tables") or []
chold, rhold = set(live.get("catalogue_hold") or []), set(live.get("review_hold") or [])
loaded = lambda t: any(re.match(p, t) for p in full) or any(re.match(p, t) for p in recent)
ST = json.load(open(P("site", "data", "license_status.json"), encoding="utf-8"))["tables"]
held = {t for t, r in ST.items() if r["status"] == "license needed" and TODAY >= r["from"]}
listed = {t for t, r in cov.items() if r["license"] == "public" and t not in chold and not (loaded(t) and t in rhold)}
rel = {r["table"]: r for r in rows(P("docs", "redivis", "release-v1", "tables.csv"))}
stan = {r["table"]: r for r in rows(P("docs", "redivis", "release-v1-stanford", "tables.csv"))}
verd = json.load(open(P("site", "data", "table_verdicts.json"), encoding="utf-8"))
out = {}

# 1. public tables fed by a source of a grid whose verdict asks for permission (NYISO, ISO-NE, MISO), and not held
src = rows(P("warehouse", "metadata", "sources.csv"))
reach = {}
for g, pre in (("NYISO", "nyiso:"), ("ISO-NE", "isone:"), ("MISO", "miso:")):
    ts = sorted({t.strip() for r in src if r["source"].lower().startswith(pre) for t in r["tables"].split(";") if t.strip()})
    for t in ts:
        c = cov.get(t)
        if not c or c["license"] != "public" or t in held:
            continue
        reach.setdefault(t, dict(grids=[], listed=t in listed, loaded=loaded(t), catalogue_hold=t in chold,
                                 old_dataset=rel.get(t, {}).get("in_v1", "absent"), stanford=stan.get(t, {}).get("in_v1", "absent"),
                                 verdict=(verd.get(t) or [""])[0]))["grids"].append(g)
out["public_unheld_tables_with_a_permission_grid_source"] = reach

# 2. the per-row retrieval time the lead promises ("the source report and retrieval time of every row")
per = Counter()
lack = []
for t in sorted(listed):
    fp = os.path.join(OUTDIR, t + ".csv")
    if not os.path.isfile(fp):
        per["not on this machine"] += 1
        continue
    with open(fp, encoding="utf-8", errors="replace", newline="") as f:
        for line in f:
            if not line.startswith("#"):
                cols = next(csv.reader([line]))
                break
    has_r, has_s = "retrieved_at" in cols, "source" in cols
    per[f"retrieved_at {'yes' if has_r else 'no'}, source {'yes' if has_s else 'no'}"] += 1
    if not has_r:
        lack.append(t)
out["listed_per_row_columns"] = dict(per)
out["listed_without_retrieved_at"] = lack

# 3. the news index's row dated after the coverage build (a public table)
ni = os.path.join(OUTDIR, "news_index.csv")
with open(ni, encoding="utf-8", newline="") as f:
    lines = [l for l in f if not l.startswith("#")]
rr = list(csv.DictReader(lines))
out["news_index_future_rows"] = [{k: r.get(k, "")[:140] for k in ("event_id", "event_date", "source", "headline", "source_url")} for r in rr if r["event_date"][:10] > TODAY]

# 4. the first row's namespace of the tables the standard's rule is set against
for t in ("carbon_intensity_hourly", "caiso_interconnection_queue", "eia860m_operating_generators", "ba_supply_monthly", "energy_companies"):
    fp = os.path.join(OUTDIR, t + ".csv")
    if not os.path.isfile(fp):
        continue
    with open(fp, encoding="utf-8", errors="replace", newline="") as f:
        it = (l for l in f if not l.startswith("#"))
        next(it)
        first = next(csv.reader([next(it)]))
    out.setdefault("first_namespace", {})[t] = first[0].split(":", 1)[0]

# 5. the four unsettled tables listed as public: what /data draws in each cell
for t in ("state_large_load_laws", "utility_large_load_queue_totals", "utility_large_load_rule_changes", "utility_large_load_rules"):
    c = cov[t]
    out.setdefault("unsettled_listed", {})[t] = dict(license=c["license"], tier=c["tier"], loaded=loaded(t), held=t in held,
                                                     verdict=verd[t][0], old_dataset=rel.get(t, {}).get("in_v1"), n_rows=c["n_rows"])

json.dump(out, open(OUTJSON, "w", encoding="utf-8"), indent=1, default=str)
for k, v in out.items():
    s = json.dumps(v, default=str)
    print(f"{k}: {s if len(s) < 1500 else s[:1500] + ' ...'}")
