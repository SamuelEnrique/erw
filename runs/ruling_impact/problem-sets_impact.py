#!/usr/bin/env python3
"""ERW, ruling impact for /learn/problems (session 7582, 17 November 2026).

The one line marked "Changes a figure" under the problem sets in docs/reviews/rulings-for-samuel-2026-11-17.md (branch
wip/7560-six-reads): read New Mexico's Taxation and Revenue Department table for September 2026 on, so question 4 of
"Storage and taxes" (1,000 bbl in October 2026) uses that month's rates, not the newest held (1 April to 31 August 2026).

The rates of September 2026 on are not held. What can be computed: the answer at the held rates, and the answer at the
one rate New Mexico's table can change between periods by statute, the conservation tax (0.19 or 0.24 percent by the
price of oil). Prices from warehouse/output/eia_fuel_spot_prices.csv; rules from site/data/severance_rules.json; the
problem sets' rule (the month's mean before rounding) as docs/reviews/severance-read-2026-11-16.md row 13 states it.

    .venv/Scripts/python.exe runs/ruling_impact/problem-sets_impact.py
"""
import importlib.util
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
spec = importlib.util.spec_from_file_location("sev", os.path.join(ROOT, "replication", "severance", "replicate.py"))
sev = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sev)
rules = sev.Rules(os.path.join(ROOT, "site", "data", "severance_rules.json"))
daily = sev.daily_prices(os.path.join(ROOT, "warehouse", "output"))
xs = daily["eia:wti_cushing"]["2026-10"]
mean = sum(xs) / len(xs)
nm = rules.product("NM", "oil")
held = {b["id"]: b["rate"] for b in nm["base"] if isinstance(b["rate"], float)}
print(f"WTI Cushing, October 2026: mean {mean:.6f} over {len(xs)} days; New Mexico's statewide rates held {held} ({nm['base'][0]['effective']})")
value = 1000 * mean
a = value * sum(held.values())
alt = dict(held, nm_cons_oil=0.0019)
b = value * sum(alt.values())
print(f"question 4, New Mexico, 1,000 bbl: at the held rates {a:,.2f} USD; with the conservation tax at 0.19 percent instead of 0.24 {b:,.2f} ({b - a:+,.2f}, {(b / a - 1) * 100:+.2f} percent)")
print("whether October's table sets 0.19 or 0.24 percent, or moves the other two rates, is in the Department's table, not held: the true October figure is not computed")
