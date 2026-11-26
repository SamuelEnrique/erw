"""Session 10210: the restatement (restate.json) against the figures the drawn page carries (main_default_n.json, every
data-n of /curtailment as the site's own code draws it). Prints each key, both values, and the count that agree."""
import json
import sys

R = json.load(open(sys.argv[1], encoding="utf-8"))
P = json.load(open(sys.argv[2], encoding="utf-8"))
keys = [k for k in P if not k.isdigit()]
same = diff = 0
for k in keys:
    if k not in R:
        print(f"NOT RESTATED {k}: page {P[k]}")
        continue
    ok = R[k] == P[k]
    same += ok
    diff += not ok
    if not ok:
        print(f"DIFF {k}: page {P[k]} restated {R[k]}")
print(f"{same} of {len(keys)} figures of the drawn page equal the restatement; {diff} differ; {len([k for k in keys if k not in R])} not restated")
print("monthly table and days, restated:", {k: v for k, v in R.items() if k.startswith("_")})
