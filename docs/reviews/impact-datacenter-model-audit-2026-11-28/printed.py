"""Session 11404: the figures a case prints (page.json), with its inputs and its years, for the audit's tables."""
import json
import sys

P = json.load(open("runs/c770/s11404/page.json"))
for cid in [a for a in sys.argv[1:] if not a.startswith("-")]:
    c = P[cid]
    print("==", cid, "ok", c["ok"], "exemption", c["exemption"], "chain", c["chain"])
    print("inputs", {k: v for k, v in c["x"].items()})
    for k, f in c["figs"].items():
        print(f"  {k:18s} {f['v']!r:28} {f['text']}")
    if "-y" in sys.argv:
        for y in c["years"]:
            print("  ", {k: (round(v, 2) if isinstance(v, float) else v) for k, v in y.items()})
if "-o" in sys.argv:
    for st0, rows in P["_other"].items():
        rows = sorted([r for r in rows if r["ok"]], key=lambda r: -r["taxes"])
        print("other states for", st0, "count", len(rows))
        for i, r in enumerate(rows):
            print(f"  {i+1:2d} {r['st']} {r['taxes']:.2f} forgone {r['forgone']:.2f}")
