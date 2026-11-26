# Session 10203: set restate.py's JSON beside lib_figures.mjs's, number by number; print the largest gap.
#   python runs/c10203/compare.py <restate.json> <lib.json>
import json
import sys

a = json.load(open(sys.argv[1], encoding="utf-8"))
b = json.load(open(sys.argv[2], encoding="utf-8"))
rows = []


def walk(x, y, path):
    if isinstance(x, dict) and isinstance(y, dict):
        for k in sorted(set(x) | set(y)):
            if k not in x or k not in y:
                rows.append((path + "." + k, "missing in " + ("restate" if k not in x else "lib"), None))
                continue
            walk(x[k], y[k], path + "." + k)
    elif isinstance(x, (int, float)) and isinstance(y, (int, float)) and not isinstance(x, bool):
        rows.append((path, x, abs(x - y)))
    elif x != y:
        rows.append((path, f"{x} != {y}", None))


walk(a, b, "")
bad = [r for r in rows if r[2] is None or r[2] > 1e-6 * max(1, abs(r[1]) if isinstance(r[1], (int, float)) else 1)]
print(f"numbers compared: {sum(1 for r in rows if r[2] is not None)}; differing beyond 1e-6 (relative): {len(bad)}")
for r in bad[:40]:
    print("  ", r)
print("largest absolute gap:", max((r for r in rows if r[2] is not None), key=lambda r: r[2]))
sys.exit(1 if bad else 0)
