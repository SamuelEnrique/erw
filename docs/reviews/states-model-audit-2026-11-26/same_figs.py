"""Session 10223: are two drawings' marked figures the same (key and printed value; hovers may differ)?

    python same_figs.py <a_figures.json> <b_figures.json>
"""
import json
import sys

a = json.load(open(sys.argv[1], encoding="utf-8"))
b = json.load(open(sys.argv[2], encoding="utf-8"))
fa = [(k, v) for k, v, _ in a["figs"]] + [(k, v) for k, v, _ in a["notHeld"]]
fb = [(k, v) for k, v, _ in b["figs"]] + [(k, v) for k, v, _ in b["notHeld"]]
diff = [x for x in fa if x not in fb] + [x for x in fb if x not in fa]
print(f"{sys.argv[1]} against {sys.argv[2]}: {len(fa)} and {len(fb)} figures; differences: {len(diff)} {diff[:10]}")
sys.exit(1 if diff else 0)
