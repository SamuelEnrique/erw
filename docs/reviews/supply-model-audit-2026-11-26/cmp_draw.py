"""Session 10222: two drawings of /supply set side by side: every marked figure, every hover and the visible text.

    python cmp_draw.py <before prefix_default> <after prefix_default>
"""
import difflib
import json
import sys

a, b = sys.argv[1], sys.argv[2]
fa, fb = json.load(open(a + "_figures.json", encoding="utf-8")), json.load(open(b + "_figures.json", encoding="utf-8"))
print("marked figures equal:", fa["n"] == fb["n"], len(fa["n"]), len(fb["n"]))
print("country figures equal:", fa["cn"] == fb["cn"], len(fa["cn"]), len(fb["cn"]))


def parts(p):
    t = open(p + ".txt", encoding="utf-8").read()
    titles = t.split("== titles")[1].split("== visible text")[0].strip().split("\n")
    text = t.split("== visible text")[1]
    return titles, text


ta, xa = parts(a)
tb, xb = parts(b)
print("visible text equal:", xa == xb)
if xa != xb:
    sm = difflib.SequenceMatcher(None, xa, xb, autojunk=False)
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op != "equal":
            print(f"  text {op}: {xa[max(0, i1 - 60):i2 + 20]!r} -> {xb[max(0, j1 - 60):j2 + 20]!r}")
changed = [(x, y) for x, y in zip(ta, tb) if x != y]
print("titles:", len(ta), len(tb), "changed:", len(changed))
for x, y in changed[:40]:
    print("  BEFORE:", x[:220])
    print("  AFTER: ", y[:600])
