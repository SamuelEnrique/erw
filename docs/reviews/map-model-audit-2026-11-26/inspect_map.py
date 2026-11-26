"""Session 10216: what the page's file holds (site/data/map.json), standard library only."""
import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.abspath(os.path.join(HERE, "..", "..", "site"))
f = json.load(open(os.path.join(SITE, "data", "map.json"), encoding="utf-8"))
print("keys:", sorted(f.keys()))
for k in ("tables", "vintage", "vintages", "retrieved", "source_url", "built", "held", "counts"):
    print(k, "=", f[k])
print("kinds:", f["kinds"])
print("grids:", [g["slug"] for g in f["grids"]])
print("statuses:", [(s["slug"], s["kind"]) for s in f["statuses"]])
print("rows:", len(f["k"]))
pr = collections.Counter((f["k"][i], f["pr"][i]) for i in range(len(f["k"])))
print("precision by kind:", sorted(pr.items()))
g = collections.Counter((f["k"][i], f["grids"][f["g"][i]]["slug"]) for i in range(len(f["k"])))
print("grid by kind:", sorted(g.items()))
# queue status by grid
qs = collections.Counter((f["grids"][f["g"][i]]["slug"], f["statuses"][f["st"][i]]["slug"]) for i in range(len(f["k"])) if f["k"][i] == 2)
print("queue status by grid:", sorted(qs.items()))
print("more.queue keys:", list(f["more"]["queue"].keys()), "statuses:", f["more"]["queue"]["statuses"][:60])
print("datacenter from:", collections.Counter(f["more"]["datacenter"]["from"]))
print("states:", f["states"])
nulls = sum(1 for i in range(len(f["k"])) if f["la"][i] is None or f["lo"][i] is None)
print("rows without coordinates:", nulls)
print("PR rows:", sum(1 for i in range(len(f["k"])) if f["states"][f["s"][i]] == "PR"),
      "PR with coordinates:", sum(1 for i in range(len(f["k"])) if f["states"][f["s"][i]] == "PR" and f["la"][i] is not None))
mw_null = collections.Counter(f["k"][i] for i in range(len(f["k"])) if f["mw"][i] is None)
print("mw null by kind:", mw_null)
