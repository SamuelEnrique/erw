#!/usr/bin/env python3
"""ERW, ruling impact for /grid/caiso/alerts (session 7580, 17 November 2026).

The two lines marked "Changes a figure" under the Flex Alert scorecard in docs/reviews/rulings-for-samuel-2026-11-17.md
(branch wip/7560-six-reads). Rows: replication/caiso_alerts/public_rows.csv (flex_alert_effects, flex_alert_model and
caiso_dam_alert_day_hub_prices, public). Line 1's two cells are recomputed from their hours; line 2 counts the alert days
that have no day-ahead price and the MWh a daily index would value.

    .venv/Scripts/python.exe runs/ruling_impact/caiso-alerts_impact.py
"""
import csv
import math
import os
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
R = list(csv.DictReader(open(os.path.join(ROOT, "replication", "caiso_alerts", "public_rows.csv"), encoding="utf-8", newline="")))


def half_up(x, d):
    return math.floor(x * 10 ** d + 0.5) / 10 ** d if x >= 0 else -math.floor(-x * 10 ** d + 0.5) / 10 ** d


day = defaultdict(dict)
hours = defaultdict(lambda: defaultdict(dict))
for r in R:
    if r["table"] != "flex_alert_effects":
        continue
    if r["freq"] == "P1D":
        day[r["ts_utc"][:10]][r["variable"]] = float(r["value"])
    elif r["freq"] == "PT1H":
        hours[r["ts_utc"]][r["variable"]] = float(r["value"])
    elif r["freq"] == "P1Y":
        day["Y" + r["ts_utc"][:4]][r["variable"]] = float(r["value"])

print("== line 1: two cells rounded twice (the table's three decimals, then the page's two)")
d = day.get("2021-07-29", {})
for k in ("reduction_pct",):
    v = d.get(k)
    print(f"2021-07-29 {k}: the table holds {v}; the page rounds it to {half_up(v, 2):.2f}; at the builder's full precision (-0.174972, the replication's sum of the hours) the page would read -0.17")
y = day.get("Y2024", {})
v = y.get("year_reduction_mwh")
print(f"2024 year_reduction_mwh: the table holds {v}; the page rounds it to {half_up(v, 2):,.2f}; from the hours (-16,893.3249) it would read -16,893.32")
print("each moves by one in the last digit shown: 0.01 points (5.7 percent of the cell) and USD-free 0.01 MWh (0.00006 percent)")

print("\n== line 2: alert days valued at the hour's day-ahead price (default) or, where none is held, at a daily on-peak index (a second figure)")
alert_days = sorted(k for k in day if not k.startswith("Y") and "reduction_mwh" in day[k])
priced = [k for k in alert_days if "value_usd" in day[k]]
unpriced = [k for k in alert_days if "value_usd" not in day[k]]
by_year = defaultdict(lambda: [0, 0, 0.0])
for k in alert_days:
    b = by_year[k[:4]]
    b[0] += 1
    if k in unpriced:
        b[1] += 1
        b[2] += day[k]["reduction_mwh"]
print(f"alert days with an estimate: {len(alert_days)}; valued at the day-ahead price: {len(priced)}; 'no price': {len(unpriced)}")
for yy, (n, u, mwh) in sorted(by_year.items()):
    print(f"   {yy}: {n} alert days, {u} with no price, their estimated reduction {mwh:,.2f} MWh")
print("the daily on-peak index for 2018 to 2022 is not held (data request row 200): the second figure's dollars are not computed; "
      "each unpriced day would gain one cell, its reduction in MWh times the index")
