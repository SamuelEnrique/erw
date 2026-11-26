# Session 10215: the AI view's US-dollar sums, cell by cell: how many kinds of supply (lib/dealsai.ts supplyOf, as the
# restatement reads it) each cell's US-dollar sum adds, by buyer (the default), grid and quarter. From the page's own
# figures (lib.json) and the restatement's reading of the kind of supply on the same rows.
#   python runs/c10215/measures3.py <rows dir> <deal_duplicates.json> <out.json>
import json
import os
import re
import sys
from collections import defaultdict

ROWS, DUPS, DEST = sys.argv[1:4]
rows = json.load(open(os.path.join(ROWS, "energy_deals.json"), encoding="utf-8"))
pairs = json.load(open(DUPS, encoding="utf-8"))["pairs"]
ids = {r["event_id"] for r in rows}
gone = {p["duplicate"] for p in pairs if p["ruling"] == "fold" and p["duplicate"] in ids and p["kept"] in ids}
FORM = {"ppa": "ppa", "offtake": "offtake", "project_finance": "project_finance", "m_and_a": "m_and_a", "debt": "capital",
        "equity_raise": "capital", "tax_equity": "capital", "joint_venture": "capital", "fuel_supply": "fuel_supply",
        "behind_the_meter": "behind_the_meter", "nuclear_restart": "nuclear_restart_uprate", "smr": "smr"}


SG = {"TX": "ERCOT", "CA": "CAISO", "NY": "NYISO", "PA": "PJM", "NJ": "PJM", "MD": "PJM", "DE": "PJM", "VA": "PJM", "WV": "PJM",
      "OH": "PJM", "DC": "PJM", "MN": "MISO", "IA": "MISO", "WI": "MISO", "MI": "MISO", "LA": "MISO", "OK": "SPP", "KS": "SPP", "NE": "SPP",
      "CT": "ISO-NE", "ME": "ISO-NE", "MA": "ISO-NE", "NH": "ISO-NE", "RI": "ISO-NE", "VT": "ISO-NE"}


def supply(x):
    t = (x.get("technology") or "").lower()
    k = x.get("kind") or FORM.get(x.get("deal_type", ""), "other")
    if k in ("nuclear_restart_uprate", "smr") or re.search(r"nuclear|reactor|smr|fusion", t):
        return "nuclear"
    if k == "gas_buildout" or re.search(r"\bgas\b|lng|turbine", t):
        return "gas"
    if k == "storage" or re.search(r"solar|wind|batter|storage|hydro|geotherm|renewable", t):
        return "renewables_storage"
    if k == "compute_capacity":
        return "compute"
    if k in ("ppa", "offtake", "behind_the_meter"):
        return "grid"
    if k in ("capital", "m_and_a", "project_finance"):
        return "capital"
    return "other"


ai = [r for r in rows if r["event_id"] not in gone and (r["extra"].get("ai_power") or "").lower() == "true" and r["extra"].get("dollars")]
M = {}
for dim in ("buyer", "grid", "quarter"):
    cells = defaultdict(list)
    for r in ai:
        x = r["extra"]
        if dim == "buyer":
            v = x.get("buyer_name") or x.get("buyer") or x.get("seller_name") or x.get("seller") or ""
        elif dim == "grid":
            v = SG.get((x.get("state") or "").upper(), "")
        else:
            d = r["event_date"]
            v = f"{d[:4]}-Q{(int(d[5:7]) - 1) // 3 + 1}"
        cells[v].append((supply(x), float(x["dollars"])))
    mixed = {k: v for k, v in cells.items() if len(set(s for s, _ in v)) > 1}
    M[dim] = {"cells_with_usd": len(cells), "cells_adding_two_or_more_kinds": len(mixed),
              "usd_in_mixed_cells": sum(u for v in mixed.values() for _, u in v),
              "largest_mixed": sorted(((round(sum(u for _, u in v) / 1e9, 1), sorted(set(s for s, _ in v))) for v in mixed.values()), reverse=True)[:5]}
M["usd_total"] = sum(float(r["extra"]["dollars"]) for r in ai)
json.dump(M, open(DEST, "w", encoding="utf-8"), indent=1)
print(json.dumps(M, indent=1))
