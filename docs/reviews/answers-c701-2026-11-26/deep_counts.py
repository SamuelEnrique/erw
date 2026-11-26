"""Data request 8 of docs/state/data_requests_five_tools.md: the deep hunt's trial counts, read (never written) from the
day folders of runs/deep/ given as arguments. One line a family: claims tried, passed, drafts kept, loaded; then sums."""
import glob
import json
import os
import sys

tot = dict(claims=0, passed=0, drafts=0, loaded=0, families=0)
rows = []
for day in sys.argv[1:]:
    for fam in sorted(os.listdir(day)):
        p = os.path.join(day, fam, fam + ".json")
        if not os.path.exists(p):
            continue
        d = json.load(open(p, encoding="utf-8"))
        r = dict(day=os.path.basename(day.rstrip("/\\")), family=d.get("family", fam), claims=d.get("claims", 0), passed=d.get("passed", 0),
                 drafts=len(d.get("drafts") or []), loaded=len(d.get("loaded") or []), dry_run=d.get("dry_run"), computed_at=d.get("computed_at"))
        rows.append(r)
        for k in ("claims", "passed", "drafts", "loaded"):
            tot[k] += r[k]
        tot["families"] += 1
for r in rows:
    print(f"{r['day']} {r['family']:24} claims {r['claims']:4} passed {r['passed']:3} drafts {r['drafts']:3} loaded {r['loaded']:3} dry_run {r['dry_run']} {r['computed_at']}")
print("total", tot)
