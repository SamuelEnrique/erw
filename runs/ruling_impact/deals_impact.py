#!/usr/bin/env python3
"""ERW, ruling impact for /deals (session 7595, 17 November 2026).

The five lines marked "Changes a figure" under the deal tracker in docs/reviews/rulings-for-samuel-2026-11-17.md (branch
wip/7560-six-reads). energy_deals is internal: only counts and sums are printed, never a deal's parties or its own
figures. Rows from warehouse/output/energy_deals.csv read as replication/deals/replicate.py reads them (imported: Deal,
GRID_OF_STATE), folded by the register site/data/deal_duplicates.json; each source's license from
warehouse/metadata/sources.csv.

    .venv/Scripts/python.exe runs/ruling_impact/deals_impact.py
"""
import csv
import importlib.util
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
spec = importlib.util.spec_from_file_location("rep", os.path.join(ROOT, "replication", "deals", "replicate.py"))
rep = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rep)
with open(os.path.join(ROOT, "warehouse", "output", "energy_deals.csv"), encoding="utf-8", newline="") as f:
    raw = list(csv.DictReader(l for l in f if not l.startswith("#")))
for r in raw:
    r["extra"] = r
pairs = json.load(open(os.path.join(ROOT, "site", "data", "deal_duplicates.json"), encoding="utf-8"))["pairs"]
ids = {r["event_id"] for r in raw}
fold = [p for p in pairs if p["ruling"] == "fold" and p["duplicate"] in ids and p["kept"] in ids]
gone = {p["duplicate"] for p in fold}
D = [rep.Deal(r) for r in raw if r["event_id"] not in gone]
byid = {r["event_id"]: r for r in raw}
mw = lambda ds: sum(d.mw for d in ds if d.mw is not None)
print(f"energy_deals: {len(raw)} rows, {len(gone)} folded by the register: {len(D)} deals; MW stated by {sum(1 for d in D if d.mw is not None)}: {mw(D):,.0f} MW "
      f"(the rulings file: 590 deals, 43,119 MW)")

print("\n== line 1: the deals table held whole (default) or the rows whose every source is public shown")
LIC = {r["source"]: r["license"] for r in csv.DictReader(open(os.path.join(ROOT, "warehouse", "metadata", "sources.csv"), encoding="utf-8"))}
src = {}
for r in raw:
    src[r["event_id"]] = r["source"]
pub = [d for d in D if LIC.get(src[d.id]) == "public"]
print(f"deals whose source is public in the registry: {len(pub)} of {len(D)}, MW {mw(pub):,.0f}; the others ({len(D) - len(pub)}) rest on news sources (internal). "
      f"Sources of the deals: {dict(sorted(((s, sum(1 for d in D if src[d.id] == s)) for s in {src[d.id] for d in D}), key=lambda kv: -kv[1])[:8])}")

print("\n== line 2: no floor of the extraction's confidence (default) or 'Sure at least' 0.5 or 0.7")
for fl in (None, 0.5, 0.7):
    k = D if fl is None else [d for d in D if d.sure is not None and d.sure >= fl]
    print(f"floor {fl}: {len(k)} deals ({len(k) / len(D) * 100:.1f} percent), MW {mw(k):,.0f} ({mw(k) / mw(D) * 100:.1f} percent), AI-power deals {sum(1 for d in k if d.ai)}, with a price {sum(1 for d in k if d.price is not None)}")

print("\n== line 3: the views read the grid from the state alone (default) or a grid the story names first, as the table's Grid column")
diff = [d for d in D if (byid[d.id].get("grid") or "") and (byid[d.id]["grid"].lower() != (d.grid or "").lower())]
print(f"deals whose table Grid differs from the state's grid: {len(diff)}; by pair (table, state's): {sorted({(byid[d.id]['grid'], d.grid or 'not stated') for d in diff})}")

print("\n== line 4: a folded row's figure carried to the kept row where only the folded row states it (the warehouse's own merge)")
add = 0.0
n = 0
for p in fold:
    k, g = byid[p["kept"]], byid[p["duplicate"]]
    km, gm = rep.num(k.get("mw")), rep.num(g.get("mw"))
    if km is None and gm is not None:
        add += gm
        n += 1
print(f"kept rows without MW whose folded row states it: {n}, {add:,.0f} MW; MW disclosed {mw(D):,.0f} -> {mw(D) + add:,.0f} ({add / mw(D) * 100:+.2f} percent)")

print("\n== line 5: 'a deal is energy's where its asset is energy' written into the extraction's prompt, and the older rows read again")
print("not computed: reading the rows again is a model call (spend USD 0, the key at its limit); the faults file's count is about 51 rows "
      f"(funding rounds, chip contracts, sales of non-energy businesses) of {len(D)}, which would leave every count")
