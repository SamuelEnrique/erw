# Session 10215: the page's functions (lib.json, site/scripts/deal-tracker-figures.mjs on the rows of to_rows.py) set
# beside the independent restatement (restate.json). Prints every key that differs or is on one side only.
#   python runs/c10215/compare.py <lib.json> <restate.json>
import json
import sys

lib = json.load(open(sys.argv[1], encoding="utf-8"))["figures"]
res = json.load(open(sys.argv[2], encoding="utf-8"))["figures"]
same, diff, only_lib, only_res = 0, [], [], []
big = 0.0
for k in sorted(set(lib) | set(res)):
    if k not in res:
        only_lib.append((k, lib[k]))
    elif k not in lib:
        only_res.append((k, res[k]))
    else:
        a, b = float(lib[k]), float(res[k])
        gap = abs(a - b) / max(1.0, abs(a), abs(b))
        if gap <= 1e-9:
            same += 1
            big = max(big, gap)
        else:
            diff.append((k, lib[k], res[k]))
print(f"keys on both sides: {same + len(diff)}; equal to 1e-9 relative: {same}; largest gap among the equal: {big:.2e}")
print(f"differ: {len(diff)}")
for k, a, b in diff:
    print(f"  {k}: page {a}  restated {b}")
print(f"only the page's functions: {len(only_lib)}")
for k, a in only_lib:
    print(f"  {k}: {a}")
print(f"only the restatement: {len(only_res)}")
for k, b in only_res:
    print(f"  {k}: {b}")
