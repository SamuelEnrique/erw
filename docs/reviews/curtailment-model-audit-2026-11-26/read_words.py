"""Session 10210: read a words fix once more in the drawn page. For each needle, prints the drawn view that holds it and
the sentence around it, or MISSING; exit 1 when a needle is missing.

    python read_words.py <draw dir> <tag> <needle> [needle ...]
"""
import glob
import os
import sys

d, tag, needles = sys.argv[1], sys.argv[2], sys.argv[3:]
texts = {os.path.basename(p)[len(tag) + 1:-4]: open(p, encoding="utf-8").read() for p in glob.glob(os.path.join(d, f"{tag}_*.txt")) if not p.endswith("_asked.txt")}
bad = 0
for n in needles:
    hit = [(v, t) for v, t in sorted(texts.items()) if n in t]
    if not hit:
        print(f"MISSING: {n}")
        bad += 1
        continue
    v, t = hit[0]
    i = t.index(n)
    a = max(t.rfind(". ", 0, max(0, i - 300)), 0)
    print(f"PASS [{', '.join(x for x, _ in hit)}]: ...{t[a:i + len(n) + 250]}...")
print("em dash in a drawn view:", [v for v, t in texts.items() if chr(0x2014) in t] or "none")
sys.exit(1 if bad else 0)
