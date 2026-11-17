#!/usr/bin/env python3
"""ERW, ruling impact for /cost-of-power (session 7599, 17 November 2026).

The eight lines marked "Changes a figure" under /cost-of-power (with its All grids tab and the large-load rules) in
docs/reviews/rulings-for-samuel-2026-11-17.md (branch wip/7560-six-reads). The page's own files under site/data/siting/
and site/data/datacenter/, and ercot_4cp_intervals (warehouse/output, ERCOT's four coincident peaks). Held rows are
counted, never printed.

    .venv/Scripts/python.exe runs/ruling_impact/cost-of-power_impact.py
"""
import csv
import json
import os
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
S = lambda f: json.load(open(os.path.join(ROOT, "site", "data", "siting", f + ".json"), encoding="utf-8"))
MW = 300

print("== line 1: a Texas row's all-in figure with the Commission's transmission rate for all wires utilities (USD 7.83 per MWh) or the row's own utility's (Oncor 8.58)")
print(f"the read's case: +0.75 USD/MWh (+9.6 percent of the transmission part) on every row whose wires utility is Oncor; a 300 MW load at a 90 percent load factor: "
      f"{MW * 8760 * 0.9 * 0.75:,.0f} USD a year more (an example load factor)")
z = S("ercot_zone_wires")["zones"]
print("ERCOT zones and the wires utilities their counties hold (the page's file): " + "; ".join(f"{k}: {len(v['wires'])}" for k, v in z.items()))

print("\n== lines 3 and 4: ERCOT's four summer peaks: a way of running off in the forecast peak intervals; and which year's rate")
rows = []
with open(os.path.join(ROOT, "warehouse", "output", "ercot_4cp_intervals.csv"), encoding="utf-8", newline="") as f:
    for r in csv.DictReader(l for l in f if not l.startswith("#")):
        if r["x_year"] == "2025":
            rows.append((r["x_month"], r["x_interval_local"], float(r["value"])))
print(f"summer 2025's four coincident peak intervals (ERCOT): {rows}")
for label, rate in (("2025's rate, the newest approved when read", 68.547301), ("the 2026 rate the summer 2025 peaks set", 75.527270)):
    print(f"   {label}: USD {rate} per kW a year: a {MW} MW load off in all four intervals avoids USD {rate * MW * 1000:,.0f} a year; off in none, 0")
print(f"line 4: the saving under the 2026 rate is {(75.527270 / 68.547301 - 1) * 100:+.2f} percent (+USD {(75.527270 - 68.547301) * MW * 1000:,.0f} a year for {MW} MW)")
print("line 3: today's ways follow prices and avoided 0 of 4 peaks in summer 2025 (the read); a way that is off in the forecast peak intervals avoids up to all four if the forecast is right; "
      "how many a forecast would have caught is not computed here (no forecast of the peaks is held)")

print("\n== line 7: the large-load rules read from hosts whose terms bar robots or ask permission, held")
L = S("large_load_rules")
held = L["held_rules"]
fields = L["fields"] if isinstance(L["fields"], list) else list(L["fields"])
print(f"rules shown {len(L['rules'])}, held {len(held)} (blank 'license needed'); held by utility: {dict(Counter(h['utility'] for h in held))}")
print(f"made public, up to {len(held)} rows by {len(fields)} fields ({len(held) * len(fields)} cells) would be drawn")

print("\n== line 6: Massachusetts Electric's filed rates, for ISO-NE's Boston rows' 'Transmission and 4CP' cell")
T = S("tariffs")
ma = [u for u in (T["utilities"] if isinstance(T["utilities"], list) else T["utilities"].values()) if "Massachusetts" in json.dumps(u)[:300]]
print(f"tariff rows naming Massachusetts in the page's file: {len(ma)}; the cell stays blank until the rates are held: not computed")

print("\n== line 8: CAISO's large-load steps, the straw proposal's 60 to 90 days and the draft final proposal's none")
C = S("conn_rules")["grids"].get("caiso") or []
for r in C:
    if "60" in (r.get("printed") or "") or "straw" in (r.get("document") or "").lower() or "draft final" in (r.get("document") or "").lower():
        print(f"   {r.get('date')}: {r.get('document', '')[:90]} | duration '{r.get('duration')}' {r.get('unit')}")
print("one cell: the draft final proposal's duration, blank, would read 60 to 90 days if the straw's figure stood for it")
