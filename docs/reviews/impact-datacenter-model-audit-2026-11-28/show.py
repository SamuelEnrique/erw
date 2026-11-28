"""Session 11404: print announced rows by id, and a state's datacenter rule, sales and income rows, wages."""
import json
import sys

A = json.load(open("site/data/forecast/datacenter_announced.json", encoding="utf-8"))
R = json.load(open("site/data/forecast/datacenter_rules.json", encoding="utf-8"))
S = json.load(open("site/data/forecast/sales_tax.json", encoding="utf-8"))
I = json.load(open("site/data/forecast/income_tax.json", encoding="utf-8"))
W = json.load(open("site/data/forecast/datacenter_wages.json", encoding="utf-8"))
D = json.load(open("site/data/forecast/deflator.json", encoding="utf-8"))
byid = {r["id"]: r for r in A["rows"]}
for a in sys.argv[1:]:
    if a in byid:
        print(json.dumps(byid[a], indent=1, ensure_ascii=False))
    elif a == "deflator":
        print(json.dumps(D, indent=1)[:1500])
    elif a == "sources":
        print(json.dumps(R["sources"], indent=1, ensure_ascii=False))
    else:
        print("RULE", json.dumps(R["states"].get(a), indent=1, ensure_ascii=False))
        print("SALES", S["states"].get(a))
        print("INCOME", json.dumps(I["states"].get(a)))
        print("WAGES", W["year"], W["states"].get(a))
        print("MULT", json.dumps(R["multipliers"].get(a))[:1500])
