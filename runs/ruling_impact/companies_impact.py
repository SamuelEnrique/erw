#!/usr/bin/env python3
"""ERW, ruling impact for /companies (session 7596, 17 November 2026).

The one line marked "Changes a figure" under the company database in docs/reviews/rulings-for-samuel-2026-11-17.md
(branch wip/7560-six-reads): does a parent company's page sum its listed subsidiaries' operating and owned megawatts?
The page's own files, site/data/companies/c/*.json (built 2026-11-16, each company's figures and its parent where one is
named). The figures are EIA-860 and EIA-860M's (public); held figures (deals, facilities) are not summed or printed.

    .venv/Scripts/python.exe runs/ruling_impact/companies_impact.py
"""
import glob
import json
import os
import re
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
C = {}
for p in glob.glob(os.path.join(ROOT, "site", "data", "companies", "c", "*.json")):
    C.update(json.load(open(p, encoding="utf-8")))
print(f"companies in the directory: {len(C):,}")
kids = defaultdict(list)
for c in C.values():
    if c.get("parent_id") and c["parent_id"] != c["id"]:
        kids[c["parent_id"].replace("company:", "")].append(c)
print(f"companies naming a parent: {sum(len(v) for v in kids.values())}; parents named: {len(kids)}; parents with a page here: {sum(1 for k in kids if k in C)}")
F = lambda c, k: (c.get("figures") or {}).get(k, 0) or 0
rows = []
for pid, ks in kids.items():
    p = C.get(pid)
    own_pl, own_ow = (F(p, "plants_mw"), F(p, "owned_mw")) if p else (0, 0)
    add_pl, add_ow = sum(F(k, "plants_mw") for k in ks), sum(F(k, "owned_mw") for k in ks)
    rows.append((add_pl + add_ow, p["name"] if p else pid, len(ks), own_pl, own_pl + add_pl, own_ow, own_ow + add_ow))
rows.sort(reverse=True)
print("the parents whose page would gain most (operating MW of plants operated; owned MW), own figures -> with the subsidiaries summed:")
for _, name, n, a, b, c, d in rows[:12]:
    print(f"   {name}: {n} subsidiaries; operated {a:,.1f} -> {b:,.1f} MW; owned {c:,.1f} -> {d:,.1f} MW")
moved = sum(1 for r in rows if r[0] > 0)
print(f"parents whose figures would move: {moved}")

print("\nthe rulings line's example, Constellation Energy Corporation, by name (no parent list names its subsidiaries yet):")
const = [c for c in C.values() if re.match(r"constellation", c["name"], re.I)]
for c in sorted(const, key=lambda c: -F(c, "plants_mw")):
    print(f"   {c['name']} ({c['id']}): operated {F(c, 'plants_mw'):,.1f} MW, owned {F(c, 'owned_mw'):,.1f} MW, parent '{c.get('parent', '')}'")
print(f"   summed by name: operated {sum(F(c, 'plants_mw') for c in const):,.1f} MW, owned {sum(F(c, 'owned_mw') for c in const):,.1f} MW; a subsidiary not named Constellation is not found this way")
