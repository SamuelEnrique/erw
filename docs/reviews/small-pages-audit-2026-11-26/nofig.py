"""Session 10238: every number drawn on the five pages, origin/main's drawing against the words branch's (same rows).
    python runs/c10238/nofig.py runs/c10238/main/d runs/c10238/words/d
Prints, page by page, the numbers that appear a different number of times; a moved figure would show here."""
import collections
import re
import sys

a, b = sys.argv[1], sys.argv[2]
NUM = re.compile(r"(?<![\w.])[-+]?\d[\d,]*(?:\.\d+)?")
moved = 0
for page in ("about", "subscribe", "shoulder", "attention", "resources"):
    x = collections.Counter(NUM.findall(open(f"{a}_{page}.txt", encoding="utf-8").read()))
    y = collections.Counter(NUM.findall(open(f"{b}_{page}.txt", encoding="utf-8").read()))
    diff = {k: (x.get(k, 0), y.get(k, 0)) for k in set(x) | set(y) if x.get(k, 0) != y.get(k, 0)}
    print(f"{page}: {sum(x.values())} numbers on main, {sum(y.values())} on the branch; differing: {dict(sorted(diff.items()))}")
    moved += len(diff)
print(f"{moved} numbers differ in count")
