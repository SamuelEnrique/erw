"""Session 11404: the audit's two random draws, each by a stated seed, from site/data/forecast/datacenter_announced.json.

1. Three projects for the tax lines worked by hand: random.Random(11404).sample(k=3) of the rows the picker offers an
   investment for (an investment stated, not including generation, not partial), in file order.
2. Twelve rows for the figures against their documents: random.Random(20261128).sample(k=12) of all rows, in file order.
"""
import json
import random

A = json.load(open("site/data/forecast/datacenter_announced.json", encoding="utf-8"))
rows = A["rows"]
print("rows", len(rows), "to date", sum(1 for r in rows if r.get("to_date")))
taxable = [r for r in rows if r.get("investment") and not r.get("investment_includes_generation") and not r.get("investment_partial")]
print("rows with an investment the picker takes", len(taxable))
three = random.Random(11404).sample(taxable, 3)
print("THREE (seed 11404):")
for r in three:
    print(" ", r["id"], r["state"], "mw", (r.get("mw") or {}).get("value"), "inv", r["investment"]["value"], r["investment"].get("year"),
          "perm", (r.get("permanent_jobs") or {}).get("value"), "cons", (r.get("construction_jobs") or {}).get("value"), "to_date", r.get("to_date"))
twelve = random.Random(20261128).sample(rows, 12)
print("TWELVE (seed 20261128):")
for r in twelve:
    print(" ", r["id"])
