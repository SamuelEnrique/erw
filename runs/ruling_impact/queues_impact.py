#!/usr/bin/env python3
"""ERW, ruling impact for /queues (session 7593, 17 November 2026).

The two lines marked "Changes a figure" under the interconnection queue page in
docs/reviews/rulings-for-samuel-2026-11-17.md (branch wip/7560-six-reads). The page's file site/data/queues.json
(built 2026-11-17T05:10:41Z, Berkeley Lab's 2026 edition through 2025); the rows lbnl_interconnection_queue
(warehouse/output) read by replication/queues/replicate.py's rules (imported: rows_of, num, date, TECH, STATUS, PARTS);
the All grids tab's own file site/data/siting/connect.json for its wait.

    .venv/Scripts/python.exe runs/ruling_impact/queues_impact.py
"""
import importlib.util
import json
import os
import statistics
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
spec = importlib.util.spec_from_file_location("rep", os.path.join(ROOT, "replication", "queues", "replicate.py"))
rep = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rep)
Q = json.load(open(os.path.join(ROOT, "site", "data", "queues.json"), encoding="utf-8"))
raw = list(rep.rows_of(os.path.join(ROOT, "warehouse", "output", "lbnl_interconnection_queue.csv")))

print("== line 1: storage in the queue, the file's parts (default) or reconciled to Berkeley Lab's summary (approximately 749 GW)")
w = Q["views"]["us|all"]["whole"]
parts = w.get("active_mw_parts_battery", 0) + w.get("active_mw_parts_other_storage", 0)
print(f"the page's US storage, active MW of the battery and other storage parts (hybrids' parts included): {parts / 1000:,.1f} GW; reconciled to 749 GW: "
      f"{749 - parts / 1000:+,.1f} GW ({(749 / (parts / 1000) - 1) * 100:+.1f} percent)")
for g in ("ercot", "caiso", "spp", "pjm", "miso", "west", "southeast"):
    v = Q["views"].get(f"{g}|all", {}).get("whole", {})
    if v:
        print(f"   {g}: battery parts {v.get('active_mw_parts_battery', 0) / 1000:,.1f} GW active")
print("how the 196 GW would be spread across grids and years is not in the summary: a reconciled figure exists only for the US total")

print("\n== line 2: 'Request to operation', one median over every year (default), and a second over the last three operation years")
by = defaultdict(list)
for r in raw:
    st = rep.STATUS.get((r["q_status"] or "").strip().lower())
    if st != "operating":
        continue
    q, on = rep.date(r["q_date"]), rep.date(r["on_date"])
    if q and on and on >= q:
        g = "".join(ch for ch in (r["region"] or "").lower() if ch.isalnum())
        by[g].append(((on - q).days / 365.25, on.year))
conn = json.load(open(os.path.join(ROOT, "site", "data", "siting", "connect.json"), encoding="utf-8"))
print(f"the All grids tab's file: operation years {conn['from']} to {conn['to']} (at least {conn['min_n']} requests), {conn['vintage']}")
for g in sorted(by):
    xs = by[g]
    allm = statistics.median(x for x, _ in xs)
    last = [x for x, y in xs if conn["from"] <= y <= conn["to"]]
    page = Q["views"].get(f"{g}|all", {}).get("whole", {}).get("median_years_to_operation")
    cg = conn["grids"].get(g) or conn["grids"].get(g.upper()) or {}
    lm = statistics.median(last) if len(last) >= conn["min_n"] else None
    print(f"{g}: every year {allm:.2f} years over {len(xs)} (the page: {page}); {conn['from']} to {conn['to']} {('%.2f' % lm) if lm else 'too few'} years over {len(last)} "
          f"({((lm / allm - 1) * 100) if lm else float('nan'):+.1f} percent); the tab's median {cg.get('median')} months ({cg.get('n')})")
