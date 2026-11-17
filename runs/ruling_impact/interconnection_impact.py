#!/usr/bin/env python3
"""ERW, ruling impact for /explore/interconnection (session 7578, 17 November 2026).

The four lines marked "Changes a figure" under the interconnection queue explorer in
docs/reviews/rulings-for-samuel-2026-11-17.md (branch wip/7560-six-reads). Tables: iso_queue_statistics and
ercot_interconnection_queue (warehouse/output). Only the three queues the page draws (CAISO, ERCOT, SPP; public) are
printed; the held queues (NYISO, MISO, ISO-NE: "license needed") are not read.

    .venv/Scripts/python.exe runs/ruling_impact/interconnection_impact.py
"""
import csv
import os
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "warehouse", "output")
SHOWN = ("caiso", "ercot", "spp")
TODAY = "2026-11-17"


def rows(name):
    with open(os.path.join(OUT, name + ".csv"), encoding="utf-8", newline="") as f:
        yield from csv.DictReader(l for l in f if not l.startswith("#"))


S = defaultdict(dict)
for r in rows("iso_queue_statistics"):
    q, y = r["entity"].split(":")[0], r["x_entry_year"]
    if q in SHOWN:
        S[(q, y)][r["variable"]] = float(r["value"])


def pct(a, b):
    return "n/a" if not a else f"{(b - a) / a * 100:+.1f}%"


def head(q, y):
    s = S[(q, y)]
    return (f"{q.upper()} {y}: entered {s.get('positions_entered', 0):,.0f} positions ({s.get('mw_entered', 0):,.0f} MW); reached operation {s.get('positions_operating', 0):,.0f}; "
            f"withdrawn share {s.get('withdrawal_rate', float('nan')):.2f}; waiting {s.get('positions_waiting', 0):,.0f}")


# ---- line 1: the view the page opens on
print("== line 1: the opening view, CAISO's newest year that is over (default) or a year with tens of positions, or ERCOT, or SPP")
years = {q: sorted(y for (qq, y) in S if qq == q) for q in SHOWN}
print("default: " + head("caiso", "2023"))
tens = [y for y in years["caiso"] if y <= "2025" and S[("caiso", y)].get("positions_entered", 0) >= 20]
print(f"CAISO's newest year with 20 or more positions: {tens[-1]}: " + head("caiso", tens[-1]))
for q in ("ercot", "spp"):
    print(f"{q.upper()}'s newest year that is over (2025): " + head(q, "2025"))

# ---- line 2: the withdrawn share by MW
print("\n== line 2: 'Withdrawn, share of positions entered' by count (default) or by MW, in the MW view")
for q in SHOWN:
    parts = []
    for y in years[q]:
        s = S[(q, y)]
        if s.get("mw_entered") and "withdrawal_rate" in s and "mw_withdrawn" in s and s.get("positions_entered", 0) >= 10:
            by_mw = s["mw_withdrawn"] / s["mw_entered"]
            parts.append((y, s["withdrawal_rate"], by_mw))
    if not parts:
        print(f"{q.upper()}: no year holds a withdrawn MW and a share (the queue file lists no withdrawn positions): nothing moves")
        continue
    big = max(parts, key=lambda p: abs(p[2] - p[1]))
    print(f"{q.upper()}: {len(parts)} years with 10 or more positions; " + "; ".join(f"{y} {a:.2f} -> {b:.2f}" for y, a, b in parts[-6:])
          + f"; the largest gap {big[0]} {big[1]:.2f} -> {big[2]:.2f} ({(big[2] - big[1]) * 100:+.0f} points)")

# ---- line 3: ERCOT's "Reached operation"
print("\n== line 3: ERCOT's 'Reached operation' as the connector reads it (an agreement signed) or by an in-service day")
by = defaultdict(lambda: [0, 0, 0, 0.0, 0.0])
for r in rows("ercot_interconnection_queue"):
    y = (r["queue_date"] or "")[:4]
    if not y:
        continue
    b = by[y]
    try:
        mw = float(r["capacity_mw"] or 0)
    except ValueError:
        mw = 0.0
    if r["status"] == "completed":   # the connector maps "IA Signed" to completed, the table counts it as operating
        b[0] += 1
        b[3] += mw
        if r["actual_in_service_date"] and r["actual_in_service_date"][:10] <= TODAY:
            b[1] += 1
            b[4] += mw
        elif r["proposed_in_service_date"] and r["proposed_in_service_date"][:10] <= TODAY:
            b[2] += 1
statuses = defaultdict(int)
for r in rows("ercot_interconnection_queue"):
    statuses[r["status"]] += 1
print(f"the queue table's statuses: {dict(statuses)}")
for y in sorted(by):
    if y < "2018":
        continue
    a, inserv, past, mw, mw_in = by[y]
    t = S.get(("ercot", y), {})
    print(f"entry {y}: the table's positions_operating {t.get('positions_operating', 0):,.0f} ({t.get('mw_operating', 0):,.0f} MW); in the queue file 'operating' {a} ({mw:,.0f} MW), "
          f"of which an actual in-service day held {inserv} ({mw_in:,.0f} MW), a projected day already past {past}, the rest a day still to come")

# ---- line 4: MW cells "not held" where the count is 0
print("\n== line 4: MW cells of a status with no position: 'not held' (default) or 0")
STAT = ("operating", "waiting", "withdrawn", "status_not_stated")
for q in SHOWN:
    n = sum(1 for y in years[q] for st in STAT if S[(q, y)].get(f"positions_{st}") == 0 and f"mw_{st}" not in S[(q, y)])
    print(f"{q.upper()}: {n} MW cells read 'not held' where the count is 0 and would read 0")
