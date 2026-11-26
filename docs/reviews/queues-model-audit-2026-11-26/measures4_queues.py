"""Session 10213: the active requests by Berkeley Lab's study phase (ia_phase), which the page does not summarize.

    python measures4_queues.py <lbnl csv>
"""
import csv
import sys
from collections import defaultdict

rows = [r for r in csv.DictReader(ln for ln in open(sys.argv[1], encoding="utf-8", newline="") if not ln.startswith("#")) if r["q_status"] == "active"]
by = defaultdict(lambda: [0, 0.0])
for r in rows:
    try:
        mw = max(float(r["capacity_mw"]), 0.0)
    except ValueError:
        mw = 0.0
    k = r["ia_phase"] or "(empty)"
    by[k][0] += 1
    by[k][1] += mw
tot = sum(v[1] for v in by.values())
for k, (n, mw) in sorted(by.items(), key=lambda x: -x[1][1]):
    print(f"{k}: {n:,} requests, {mw:,.1f} MW ({100 * mw / tot:.1f} percent)")
ia = [r for r in rows if r["ia_date"]]
print(f"active with an agreement date: {len(ia):,} requests, {sum(max(float(r['capacity_mw'] or 0), 0) for r in ia):,.1f} MW of {tot:,.1f}")
