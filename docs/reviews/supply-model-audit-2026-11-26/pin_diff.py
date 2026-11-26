"""Session 10222: two pins of /supply set side by side: which addresses moved, by how many bytes, and whether any
address's count of checked figures moved."""
import json
import sys

a = json.load(open(sys.argv[1], encoding="utf-8"))
b = json.load(open(sys.argv[2], encoding="utf-8"))


def entries(p):
    for k in ("pages", "addresses", "pins"):
        if k in p:
            return p[k]
    return p


ea, eb = entries(a), entries(b)
if isinstance(ea, dict):
    keys = sorted(set(ea) | set(eb))
    get = lambda e, k: e.get(k)   # noqa: E731
else:
    ea = {x.get("address", x.get("url", str(i))): x for i, x in enumerate(ea)}
    eb = {x.get("address", x.get("url", str(i))): x for i, x in enumerate(eb)}
    keys = sorted(set(ea) | set(eb))
    get = lambda e, k: e.get(k)   # noqa: E731
moved = figs = 0
for k in keys:
    x, y = get(ea, k), get(eb, k)
    if x != y:
        moved += 1
        fx = x.get("figures") if isinstance(x, dict) else None
        fy = y.get("figures") if isinstance(y, dict) else None
        if fx != fy:
            figs += 1
        lx = x.get("length") if isinstance(x, dict) else None
        ly = y.get("length") if isinstance(y, dict) else None
        print(f"  {k}: length {lx} -> {ly}; figures {fx} -> {fy}")
print(f"addresses {len(keys)}; moved {moved}; with a count of figures moved {figs}")
