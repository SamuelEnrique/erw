"""Session 10217: the page's own functions (page.json) against the independent restatement (restate.json), key by key.
    python runs/c10217/compare.py runs/c10217/page.json runs/c10217/restate.json
Prints every key that differs or is on one side only, then the counts. Exit 0 always (the differences are findings).
"""
import json
import sys

a = json.load(open(sys.argv[1], encoding="utf-8"))
b = json.load(open(sys.argv[2], encoding="utf-8"))
same = diff = 0
only_a, only_b = [], []
for k in sorted(set(a) | set(b)):
    if k not in b:
        only_a.append(k)
        continue
    if k not in a:
        only_b.append(k)
        continue
    x, y = a[k], b[k]
    if x == y or (isinstance(x, (int, float)) and isinstance(y, (int, float)) and abs(x - y) <= 1e-9 * max(1, abs(x))):
        same += 1
    else:
        diff += 1
        print(f"DIFF {k}: page {x!r} | restated {y!r}")
for k in only_a:
    print(f"PAGE ONLY {k}: {a[k]!r}")
for k in only_b:
    print(f"RESTATED ONLY {k}: {b[k]!r}")
print(f"equal {same}, differ {diff}, page only {len(only_a)}, restated only {len(only_b)}, of {len(set(a) | set(b))} keys")
