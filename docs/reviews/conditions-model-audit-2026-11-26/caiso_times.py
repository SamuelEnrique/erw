"""Session 10219: CAISO's notices whose time frame is printed but whose start and end the table leaves empty, by kind,
and the same in the page file's alerts list (what the table on /conditions draws). argv: worktree, output folder."""
import csv
import json
import os
import sys
from collections import Counter

ROOT, OUTDIR = sys.argv[1], sys.argv[2]
with open(os.path.join(OUTDIR, "caiso_grid_emergencies.csv"), encoding="utf-8", newline="") as fh:
    rows = list(csv.DictReader([ln for ln in fh if not ln.startswith("#")]))
blank = [r for r in rows if not r["x_start"] and r["x_time_frame"]]
print("rows", len(rows), "time frame printed, start empty:", len(blank))
print(" by kind", dict(Counter(r["event_type"] for r in blank)))
print(" by year", dict(sorted(Counter(r["event_date"][:4] for r in blank).items())))
print(" examples", [(r["event_date"], r["event_type"], r["x_time_frame"]) for r in blank if r["event_date"] >= "2018"][:6])
since = [r for r in blank if r["event_date"] >= "2018-07-01"]
print(" since 2018-07-01 (the page's first day):", len(since), dict(Counter(r["event_type"] for r in since)))
with open(os.path.join(ROOT, "site", "data", "conditions", "caiso.json"), encoding="utf-8") as fh:
    f = json.load(fh)
pb = [a for a in f["alerts"] if a[2] is None]
print("page file: alerts with no start", len(pb), "of", len(f["alerts"]), "; since 2018-07-01", sum(1 for a in pb if a[0] >= "2018-07-01"),
      dict(Counter(a[1] for a in pb if a[0] >= "2018-07-01")))
# reissues: rows of one kind, region and day whose start and end repeat
dup = Counter((r["event_date"], r["event_type"], r["x_region"], r["x_start"], r["x_end"]) for r in rows if r["x_start"])
extra = sum(n - 1 for n in dup.values() if n > 1)
print("rows that repeat another of the same day, kind, region, start and end:", extra, "of", len(rows))
since_extra = sum(n - 1 for k, n in dup.items() if n > 1 and k[0] >= "2018-07-01")
print(" since 2018-07-01:", since_extra, "of", sum(1 for r in rows if r["event_date"] >= "2018-07-01"))
