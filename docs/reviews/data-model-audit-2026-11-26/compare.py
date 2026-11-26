# Session 10233: the drawn pages (draw_data.mjs) set against the restatement (restate.py) and the files, cell by cell.
#   python runs/c10233/compare.py <worktree> <draw prefix> <restate.json> <out.json>
import csv
import json
import os
import re
import sys
from collections import Counter

ROOT, PREFIX, RJ, OUT = sys.argv[1:5]
P = lambda *a: os.path.join(ROOT, *a)
R = json.load(open(RJ, encoding="utf-8"))
TODAY = "2026-11-26"
with open(P("warehouse", "metadata", "coverage.csv"), encoding="utf-8", newline="") as f:
    cov = {r["table"]: r for r in csv.DictReader(f)}
ST = json.load(open(P("site", "data", "license_status.json"), encoding="utf-8"))["tables"]
held = {t for t, r in ST.items() if r["status"] == "license needed" and TODAY >= r["from"]}
verd = json.load(open(P("site", "data", "table_verdicts.json"), encoding="utf-8"))
drawn = json.load(open(PREFIX + "_data_rows.json", encoding="utf-8"))
res, gaps, keys = {}, [], 0
TIER = {"source": "source", "derived": "derived", "model_extracted": "model-extracted"}
for d in drawn:
    t, c = d["id"], d["cells"]
    r = cov[t]
    want = [
        t + (" (derived)" if r["derived"] == "yes" else ""),
        ", ".join(r["sector"].split(";")) if r["sector"] else "",
        r["interval"],
        r["ts_min"][:10],
        r["ts_max"][:10],
        r["last_run"][:10] if r["last_run"] else "not recorded",
        "license needed" if t in held else (f"{int(r['n_rows']):,}" if r["n_rows"] else ""),
        r["source_report"],
        "license needed" if t in held else r["license"],
        TIER.get(r["tier"], r["tier"]),
    ]
    for i, (a, b) in enumerate(zip(c[:10], want)):
        keys += 1
        if a != b:
            gaps.append((t, i, a, b))
    # the download cell and the tools cell
    keys += 2
    v = (verd.get(t) or ["public"])[0]
    dl = "Held: license needed" if t in held else None
    if dl and c[10] != dl:
        gaps.append((t, 10, c[10], dl))
    tools_want = f"Not public ({v})" if v != "public" else "Python, Stata, R"
    if not c[11].startswith(tools_want):
        gaps.append((t, 11, c[11][:60], tools_want))
res["rows_drawn"] = len(drawn)
res["keys_compared"] = keys
res["gaps_by_column"] = dict(Counter(g[1] for g in gaps))
res["gaps_not_held_row_count"] = [g for g in gaps if not (g[1] == 6 and g[0] in held)]
res["held_row_counts_drawn"] = sum(1 for g in gaps if g[1] == 6 and g[0] in held and g[2] != "license needed")
res["held_row_counts_drawn_sum"] = sum(int(g[2].replace(",", "")) for g in gaps if g[1] == 6 and g[0] in held and g[2].replace(",", "").isdigit())
res["gaps"] = gaps
res["download_cells"] = dict(Counter(c["cells"][10] for c in drawn))
res["tools_cells"] = dict(Counter(re.sub(r"\(.*", "", c["cells"][11])[:30] for c in drawn))
txt = open(PREFIX + "_data.txt", encoding="utf-8").read()
m = re.search(r"Coverage ([\d,]+) public tables", txt)
res["aside"] = m.group(0) if m else None
res["aside_matches_restated"] = bool(m) and int(m.group(1).replace(",", "")) == R["listed"]
res["methods_listed_drawn"] = len(re.findall(r'href="/data/methods/', open(PREFIX + "_data.html", encoding="utf-8").read()))
lic = open(PREFIX + "_licenses.txt", encoding="utf-8").read()
m = re.search(r"Held: license needed (\d+) tables are held from ([A-Za-z]+ \d+, \d{4})", lic)
res["licenses_held_sentence"] = m.group(0) if m else None
res["licenses_held_matches"] = bool(m) and int(m.group(1)) == R["held_count"]
pubs = []
for name, n in R["held_by_publisher"]:
    keys += 1
    if not re.search(re.escape(name) + r" " + str(n) + r"\b", lic):
        pubs.append((name, n))
res["licenses_publisher_rows_missing"] = pubs
m1 = re.search(r"(\d+) publishers' sentences allow the ERW as it is", lic)
m2 = re.search(r"(\d+) more allow the ERW as it is today", lic)
res["licenses_both"] = [m1.group(1) if m1 else None, R["permissive_both"]]
res["licenses_today_only"] = [m2.group(1) if m2 else None, R["permissive_today_only"]]
fl = open(PREFIX + "_faults.txt", encoding="utf-8").read()
m = re.search(r"(\d+) faults are recorded, touching (\d+) tables: ([^.]+)\. (\d+) carry a note", fl)
res["faults_summary_drawn"] = m.group(0) if m else None
fr = R["faults_restated"]
res["faults_summary_matches"] = bool(m) and [int(m.group(1)), int(m.group(2)), int(m.group(4))] == [fr["faults"], fr["tables_touched"], fr["with_open"]]
m = re.search(r"Where the ERW's own work stands: ([^.]+)\.", fl)
res["faults_resolution_drawn"] = m.group(1) if m else None
res["faults_register_date_drawn"] = (re.search(r"The register as of (\d{4}-\d{2}-\d{2})", fl) or [None])[0]
res["faults_articles_drawn"] = len(re.findall(r'data-fault="', open(PREFIX + "_faults.html", encoding="utf-8").read()))
json.dump(res, open(OUT, "w", encoding="utf-8"), indent=1)
for k, v in res.items():
    s = json.dumps(v)
    print(f"{k}: {s if len(s) < 600 else s[:600] + ' ...'}")
