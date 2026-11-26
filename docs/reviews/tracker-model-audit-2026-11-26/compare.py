# Session 10211: the restatement (restate.json) beside the page's own functions (lib.json, from
# site/scripts/datacenter-tracker-figures.mjs on the same rows). Every key of either side; a gap is reported when the
# two differ by more than 1e-9 relative, or a key is on one side only. Exit 0 when every shared key agrees.
#   python runs/c10211/compare.py runs/c10211/restate.json runs/c10211/lib.json
import json
import sys

a = json.load(open(sys.argv[1], encoding="utf-8"))["figures"]
b = json.load(open(sys.argv[2], encoding="utf-8"))["figures"]
same, gaps, only_a, only_b = 0, [], sorted(set(a) - set(b)), sorted(set(b) - set(a))
worst = 0.0
for k in sorted(set(a) & set(b)):
    x, y = float(a[k]), float(b[k])
    rel = abs(x - y) / max(1.0, abs(y))
    worst = max(worst, rel)
    if rel > 1e-9:
        gaps.append((k, x, y))
    else:
        same += 1
print(f"shared keys: {same + len(gaps)}; equal: {same}; gaps: {len(gaps)}; largest relative gap: {worst:.3g}")
for k, x, y in gaps:
    print(f"  GAP {k}: restated {x} page {y}")
print(f"restated only ({len(only_a)}):", only_a)
print(f"page only ({len(only_b)}):", only_b)
sys.exit(1 if gaps else 0)
