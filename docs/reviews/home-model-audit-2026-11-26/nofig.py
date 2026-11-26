"""Session 10236: the numbers printed on each drawn page of a branch against origin/main's drawing of the same rows:
every number token of each page, as a multiset, main against the branch; prints what is gone and what is new.
Run from the worktree root: <venv python> runs/c10236/nofig.py <main prefix> <branch prefix>"""
import glob
import os
import re
import sys
from collections import Counter

a, b = sys.argv[1], sys.argv[2]
num = re.compile(r"\d[\d,]*(?:\.\d+)?")
bad = 0
for p in sorted(glob.glob(a + "_*.txt")):
    name = p[len(a) + 1:-4]
    q = f"{b}_{name}.txt"
    if not os.path.exists(q):
        print(f"{name}: not drawn on the branch")
        bad = 1
        continue
    x = Counter(num.findall(open(p, encoding="utf-8").read()))
    y = Counter(num.findall(open(q, encoding="utf-8").read()))
    gone, new = x - y, y - x
    print(f"{name}: {sum(x.values())} numbers on main, {sum(y.values())} on the branch; gone {dict(gone) or 'none'}; new {dict(new) or 'none'}")
sys.exit(bad)
