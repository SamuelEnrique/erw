#!/usr/bin/env python3
"""ERW, ruling impact for /curtailment (session 7592, 17 November 2026).

The three lines marked "Changes a figure" under /curtailment in docs/reviews/rulings-for-samuel-2026-11-17.md (branch
wip/7560-six-reads). The page's ERCOT file is site/data/curtailment/ercot.json (built 2026-11-15T15:18:13Z), its rule
docs/methods/curtailment.md (below the limit = max(0, HSL less output) each hour; a day whole with every hour); the
battery page's figure from battery_stack_monthly (warehouse/output), the model the battery page draws.

    .venv/Scripts/python.exe runs/ruling_impact/curtailment_impact.py
"""
import csv
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
J = json.load(open(os.path.join(ROOT, "site", "data", "curtailment", "ercot.json"), encoding="utf-8"))
H = J["hours"]

print("== line 1: ERCOT, 1 November 2026 (the autumn clock change): the hour whose wind limit reads twice its neighbours")
day = [h for h in H if h["local"].startswith("2026-11-01")]
below = lambda h, f: max(0.0, h[f + "_hsl"] - h[f + "_gen"]) if h.get(f + "_hsl") is not None and h.get(f + "_gen") is not None else None
w_all = [below(h, "wind") for h in day]
odd = [h for h in day if h["ts"] == "2026-11-01T07:00:00Z"]
for h in day:
    if h["ts"] in ("2026-11-01T05:00:00Z", "2026-11-01T06:00:00Z", "2026-11-01T07:00:00Z", "2026-11-01T08:00:00Z"):
        print(f"   {h['ts']} ({h['local']}): wind {h.get('wind_gen')} MW, limit {h.get('wind_hsl')}; below the limit {below(h, 'wind')}")
tot = sum(x for x in w_all if x is not None)
odd_b = below(odd[0], "wind") if odd else 0
print(f"the day's {len(day)} hours held; wind below the limit {tot:,.1f} MWh, of which {odd_b:,.1f} in that hour; without it {tot - odd_b:,.1f} ({-odd_b / tot * 100:.1f} percent)")
nov = J["months"].get("2026-11", {})
print(f"November 2026 in the file: {json.dumps({k: v for k, v in nov.items() if k != 'missing'})[:300]}")
whole_nov = sorted({h['local'][:10] for h in H if h['local'].startswith('2026-11')})
print("the day is out of every month either way unless the day's rule changes too (23 of its 25 hours hold all four values); leaving the hour out lowers the day's own row by that much")

print("\n== line 2: the battery section (California, a battery of 4 hours) with one line of the battery page's revenue for the same hub and duration")
rows = {}
with open(os.path.join(ROOT, "warehouse", "output", "battery_stack_monthly.csv"), encoding="utf-8", newline="") as f:
    for r in csv.DictReader(l for l in f if not l.startswith("#")):
        if r["entity"] == "caiso:TH_SP15_GEN-APND" and r["variable"] in ("foresight_4h_revenue_total_usd_per_mw", "dayahead_4h_revenue_total_usd_per_mw") and r["value"]:
            rows[(r["variable"], r["ts_utc"][:7])] = float(r["value"])
for m in sorted({k[1] for k in rows})[-6:]:
    a, b = rows.get(("foresight_4h_revenue_total_usd_per_mw", m)), rows.get(("dayahead_4h_revenue_total_usd_per_mw", m))
    print(f"   {m}: SP15, 4 hours, perfect foresight {a / 1000 if a else float('nan'):.2f} USD per kW; on the day-ahead schedule {b / 1000 if b else float('nan'):.2f}")

print("\n== line 3: ERCOT's view: three shares of output below the limit over three spans (the read's 6.23, 5.91 and 6.05 percent) or the head's alone")
print(f"the file: {J['whole_days']} whole days from {J['first_day']} to {J['last_day']}; October 2026 wind share {J['months']['2026-10']['wind']['share_pct']} percent. "
      "Showing the head's span only removes two figures from the view; none of the three is recomputed differently")
