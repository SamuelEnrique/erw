"""Session 11404: the four plant types before chain 740 (2b958ba16) and on origin/main, figure by figure."""
import json, sys
d = sys.argv[1] if len(sys.argv) > 1 else "runs/c770/s11404"
a = json.load(open(f"{d}/plants_old.json"))
b = json.load(open(f"{d}/plants_new.json"))
assert sorted(a) == sorted(b)
nfig = nyear = 0
diffs = []
for k in sorted(a):
    x, y = a[k], b[k]
    if x["ok"] != y["ok"] or x["key"] != y["key"]:
        diffs.append((k, "ok/key", x["key"], y["key"]))
    for f, v in x["figs"].items():
        w = y["figs"][f]
        nfig += 1
        if (v is None) != (w is None) or (v is not None and abs(v - w) > 1e-9 * max(1, abs(v))):
            diffs.append((k, f, v, w))
    if len(x["years"]) != len(y["years"]):
        diffs.append((k, "years", len(x["years"]), len(y["years"])))
        continue
    for ry, sy in zip(x["years"], y["years"]):
        for i, v in enumerate(ry):
            w = sy[i]
            nyear += 1
            if (v is None) != (w is None) or (v is not None and abs(v - w) > 1e-9 * max(1, abs(v))):
                diffs.append((k, f"year {ry[0]} col {i}", v, w))
print(f"runs {len(a)}, figures compared {nfig}, year cells compared {nyear}, differences {len(diffs)}")
for t in diffs[:40]:
    print(t)
