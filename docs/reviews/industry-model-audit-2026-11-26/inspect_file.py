"""Session 10224: a first look at site/data/industry.json (keys, spans, the default view's inputs). Reads only."""
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
f = json.load(open(os.path.join(ROOT, "site", "data", "industry.json"), encoding="utf-8"))
print("built", f["built"], "license", f["license"], "tables", f["tables"])
print("sources", json.dumps(f["sources"], indent=1))
m = f["monthly"]
print("monthly", m["unit"], m["months"][0], m["months"][-1], len(m["months"]), list(m["by_source"]))
for k, a in m["by_source"].items():
    held = [m["months"][i] for i, v in enumerate(a) if v is not None]
    print("  ", k, held[0] if held else None, held[-1] if held else None, len(held), a[-14:])
ind = f["industries"]
print("mecs", ind["survey_year"], ind["unit"], ind["regions"], ind["fuels"], len(ind["industries"]))
print("ranked_3_digit", ind["ranked_3_digit"])
print("note", ind["note"])
for n in ind["ranked_3_digit"][:4]:
    e = ind["industries"][n]
    print(n, e["name"], e.get("rank_us_total"), e["by_region"].get("us"), e.get("electricity_mwh", {}).get("us"))
s = f["states_annual"]
print("seds", s["unit"], s["years"][0], s["years"][-1], len(s["years"]), len(s["states"]), sorted(s["states"]))
us = s["states"]["US"]
print("US keys", list(us["consumption_tbtu"]), list(us["expenditures_usd"]))
print("US total last 6", us["consumption_tbtu"]["total"][-6:], "price", us["price_usd_per_mmbtu"][-6:])
for st in ("TX", "LA"):
    print(st, {k: v[-3:] for k, v in s["states"][st]["consumption_tbtu"].items()})
es = f["electricity_sales_monthly"]
print("sales", es["unit"], es["months"][0], es["months"][-1], len(es["months"]), len(es["states"]))
print("  TX last 14", es["states"]["TX"][-14:])
o = f["outlook"]
print("outlook", o["unit"], o.get("release"), o.get("projections"), o["years"][0], o["years"][-1], len(o["years"]), "history", o["history_years"])
print("cases", o["cases"])
print("industries", list(o["industries"]))
for name in list(o["industries"]["iron_and_steel"])[:60]:
    print("   ", name)
sys.exit(0)
