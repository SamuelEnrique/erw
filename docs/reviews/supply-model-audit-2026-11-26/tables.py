"""Session 10222: what the main copy's tables hold (newest date of each entity the supply page reads), standard library."""
import csv
import sys
from collections import defaultdict

OUT = "C:/Users/lossa/Documents/erw/warehouse/output/"
for name in sys.argv[1:]:
    newest = defaultdict(str)
    n = defaultdict(int)
    variables = defaultdict(set)
    header = None
    with open(OUT + name + ".csv", encoding="utf-8") as f:
        lines = (l for l in f if not l.startswith("#"))
        rd = csv.DictReader(lines)
        for r in rd:
            e = r["entity"]
            n[e] += 1
            variables[e].add(r.get("variable", ""))
            if r["ts_utc"] > newest[e]:
                newest[e] = r["ts_utc"]
    print("==", name, len(n), "entities")
    for e in sorted(n):
        print(f"  {e:40} {n[e]:7} {newest[e]} {sorted(variables[e])[:4]}")
