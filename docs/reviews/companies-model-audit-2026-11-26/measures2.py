"""Two more measures on the company pages' files. (a) The search reads the name and "aka", which the builder cuts to six
other names: how many listed companies have more, and how many of their names the search cannot find. (b) The ERCOT
queue's statuses by company kind. Session 10228. Writes measures2.json beside it."""
import json
import os
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", ".."))
D = os.path.join(WT, "site", "data", "companies")
ix = json.load(open(os.path.join(D, "index.json"), encoding="utf-8"))
cols = ix["columns"]
irows = {r[0]: dict(zip(cols, r)) for r in ix["rows"]}
comp = {}
for f in sorted(os.listdir(os.path.join(D, "c"))):
    comp.update(json.load(open(os.path.join(D, "c", f), encoding="utf-8")))
over, lost = 0, 0
for cid, c in comp.items():
    others = sorted({n[0] for n in c["names"]} - {c["name"]})
    aka = irows[cid]["aka"]
    if len(others) > 6:
        over += 1
        lost += sum(1 for n in others if n not in aka and n.lower() not in c["name"].lower())
M = dict(companies_more_than_six_other_names=over, names_the_search_cannot_reach=lost)
json.dump(M, open(os.path.join(HERE, "measures2.json"), "w", encoding="utf-8"), indent=1)
print(json.dumps(M))
