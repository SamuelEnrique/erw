"""Session 10220: the shape of site/data/conditions/congestion.json (read only)."""
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
F = json.load(open(os.path.join(ROOT, "site", "data", "conditions", "congestion.json"), encoding="utf-8"))
print("built", F["built"], "market", F["market"], "tables", F["tables"])
for o in F["operators"]:
    print("op", o)
for op, O in F["constraints"].items():
    print("\n==", op, O["time"], "first", O["first"], "last", O["last"])
    for y in O["years"]:
        print(" ", y, "days", O["days_held"][y], "constraints", O["constraints_by_year"][y], "hours", O["hours_by_year"][y])
    print("  detail entries", len(O["constraints"]))
    print("  top years", list(O["top"].keys()))
for op, P in F["places"].items():
    for p in P:
        print("place", p["id"], p["name"], p["years"], p["first"], p["last"], "months", len(p["monthly"]), p["monthly"][0][0], p["monthly"][-1][0])
        for y, v in p["by_year"].items():
            print("   ", y, v)
