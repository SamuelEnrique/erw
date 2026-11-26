"""Session 10223 (states audit): a first look at the page's files: the index and Texas's parts, their windows and vintages."""
import json
import os
import sys

D = os.path.join(os.path.dirname(__file__), "..", "..", "site", "data", "states")
idx = json.load(open(os.path.join(D, "index.json"), encoding="utf-8"))
print("index built", idx["built"], "generation months", idx["generation_months"], "places", len(idx["states"]))
rows = sorted(idx["states"], key=lambda r: -(r["generation_last12_mwh"] or 0))
print("top by twelve-month generation:", [(r["state"], r["generation_last12_mwh"]) for r in rows[:4]])
st = sys.argv[1] if len(sys.argv) > 1 else "tx"
f = json.load(open(os.path.join(D, f"{st}.json"), encoding="utf-8"))
print("built", f["built"])
for part in ("generation", "retail", "plants", "co2", "gas", "energy", "disposition", "serving", "large_load_laws", "severance"):
    p = f[part]
    keys = list(p.keys())
    print(f"\n== {part}: keys {keys}")
    for k in ("table", "vintage", "reason", "research_status", "population_year", "basis", "shares_reason"):
        if k in p:
            print(f"  {k}: {p[k]}")
    if p.get("months"):
        print("  months", p["months"][0], "to", p["months"][-1], len(p["months"]))
    if p.get("years"):
        print("  years", p["years"][0], "to", p["years"][-1], len(p["years"]))
g = f["generation"]
print("\nlast12", json.dumps(g["last12"]))
print("annual total tail", list(zip(g["years"][-4:], g["annual"]["total"][-4:])))
# nulls inside the last twelve months, by source
for s, a in g["by_source"].items():
    tail = a[-12:]
    n = sum(v is None for v in tail)
    print(f"  {s}: nulls in last 12 = {n}; last 3 = {tail[-3:]}")
r = f["retail"]
print("\nretail last12", json.dumps(r["last12"]))
print("customers", json.dumps(r["customers"]))
for s in r["sales_mwh"]:
    print(f"  {s}: sales tail {r['sales_mwh'][s][-3:]} price tail {r['price_usd_per_mwh'][s][-3:]}")
print("\nserving", json.dumps(f["serving"])[:2500])
print("\nco2 tail", f["co2"]["years"][-3:], {k: v[-3:] for k, v in f["co2"]["tons_by_fuel"].items()}, f["co2"]["rate_kg_per_mwh"][-3:])
print("\ndisposition", f["disposition"]["years"][-3:], {k: (v[-3:] if v else v) for k, v in f["disposition"]["values"].items()})
e = f["energy"]
print("\nenergy years", e["years"][-3:], {k: (v[-3:] if v else v) for k, v in e["by_source"].items()}, {k: (v[-3:] if v else v) for k, v in e["by_sector"].items()})
ga = f["gas"]
print("\ngas months tail", ga["months"][-3:] if ga["months"] else None, {k: (v[-3:] if v else v) for k, v in ga["consumption"].items()}, (ga["marketed_production"] or [None])[-3:])
pl = f["plants"]
print("\nplants vintage", pl["vintage"], "total", pl["capacity_total_mw"], "plants", pl["plants"])
print(json.dumps(pl["capacity_by_technology"]))
print("coming years", list(pl["coming_by_year"].keys()))
print("laws", json.dumps(f["large_load_laws"])[:800])
print("severance", f["severance"])
