"""Session 10232 (reports audit), r5: the rows of ai_power_regions the license hold of 21 October 2026 keeps from the
AI gigawatts draft (ISO-NE, MISO, NYISO), by the source each measure rests on (the builder's own header names them).

    python runs/c10232/r5_held_rows.py <csv dir>
"""
import csv
import os
import sys
from collections import Counter

GRID = ("flat_rt_price", "flat_da_price", "flat_1gw_cost", "rt_hours_priced", "scarcity_hours", "max_rt_hour", "rt_hours_seen", "queue_active")
held = Counter()
rows = []
with open(os.path.join(sys.argv[1], "ai_power_regions.csv"), encoding="utf-8") as f:
    for r in csv.DictReader(ln for ln in f if not ln.startswith("#")):
        reg = r["entity"].split(":")[1]
        if reg not in ("isone", "miso", "nyiso") or r["variable"].startswith("event_largest_is_"):
            continue
        kind = "grid operator's prices or queue" if r["variable"].startswith(GRID) else "EIA, Berkeley Lab (CC BY 4.0) or the event studies"
        held[(reg, kind)] += 1
        rows.append((reg, r["variable"], r["value"], kind))
for (reg, kind), n in sorted(held.items()):
    print(f"{reg}: {n} rows from {kind}")
print(f"total held rows: {sum(held.values())}; of them not from a grid operator: {sum(n for (r, k), n in held.items() if k.startswith('EIA'))}")
for reg, var, val, kind in rows:
    if kind.startswith("EIA") and var in ("carbon_intensity_kg_mwh", "lbnl_median_years_to_cod", "lbnl_completion_pct", "net_import_share_pct"):
        print(f"  {reg} {var} {float(val):.2f}")
