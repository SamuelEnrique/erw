#!/usr/bin/env python3
"""ERW, ruling impact for the line across the five signed tools (session 7598, 17 November 2026).

The one line marked "Changes a figure" under "Across the five signed tools" in
docs/reviews/rulings-for-samuel-2026-11-17.md (branch wip/7560-six-reads): rebuild price_years_by_window in the data
machine's daily run, so each page's "Price years" default keeps up with its headline. This machine's copy of the table
(warehouse/output, the run of 20 October 2026) is read for its windows' last month, beside the newest whole month the
pages' monthly tables hold (battery_stack_monthly, cost_of_power_monthly as replication/bill/source_rows.csv holds it).
The rebuilt values themselves need site/scripts/price-years.mjs run over what each page reads from the live set, which
this machine cannot do (no build, no live-set copy): the pack's measured lag is quoted.

    .venv/Scripts/python.exe runs/ruling_impact/five-signed_impact.py
"""
import csv
import os
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "warehouse", "output")
to = Counter()
tools = Counter()
with open(os.path.join(OUT, "price_years_by_window.csv"), encoding="utf-8", newline="") as f:
    for r in csv.DictReader(l for l in f if not l.startswith("#")):
        to[(r["x_tool"], r["x_to"])] += 1
        tools[r["x_tool"]] += 1
print(f"price_years_by_window on this machine: rows by tool {dict(tools)}; the windows' last month by tool: {dict(sorted(to.items()))}")
newest = {}
with open(os.path.join(OUT, "battery_stack_monthly.csv"), encoding="utf-8", newline="") as f:
    for r in csv.DictReader(l for l in f if not l.startswith("#")):
        if r["variable"].endswith("_days_held") and r["value"]:
            newest[r["entity"]] = max(newest.get(r["entity"], ""), r["ts_utc"][:7])
print(f"battery_stack_monthly's newest month held by hub (the battery page's headline reads it): {newest}")
with open(os.path.join(ROOT, "replication", "bill", "source_rows.csv"), encoding="utf-8") as f:
    m = max(l.split(",")[2][:7] for l in f if not l.startswith("#") and "rt_load_weighted" in l)
print(f"cost_of_power_monthly as the live set served it on 16 November: newest month {m}")
print("the measured lag before the hand rebuild of 14 November (five-tools-signature-pack-2026-11-14.md ruling 2): CAISO's battery 79.31 against the headline's 79.80 "
      "(-0.49, -0.6 percent); the datacenter page 33.73 against 34.07 (-0.34, -1.0 percent)")
