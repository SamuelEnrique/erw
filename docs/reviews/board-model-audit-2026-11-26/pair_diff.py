# Session 10206: for one drawn case, each changed line of a branch against origin/main reduced to what was inserted,
# deleted or replaced inside the line, and a count of the distinct edits (so "nothing else changed" can be read).
#   python pair_diff.py <base txt> <branch txt>
import collections
import difflib
import sys

a = open(sys.argv[1], encoding="utf-8").read().splitlines()
b = open(sys.argv[2], encoding="utf-8").read().splitlines()
edits = collections.Counter()
sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
for tag, i1, i2, j1, j2 in sm.get_opcodes():
    if tag == "equal":
        continue
    if tag != "replace" or (i2 - i1) != (j2 - j1):
        edits[f"lines {tag}: {i2 - i1} to {j2 - j1}"] += 1
        continue
    for x, y in zip(a[i1:i2], b[j1:j2]):
        s = difflib.SequenceMatcher(None, x, y, autojunk=False)
        for t, p1, p2, q1, q2 in s.get_opcodes():
            if t != "equal":
                edits[f"{t}: [{x[p1:p2]}] -> [{y[q1:q2]}]"] += 1
for k, v in edits.most_common():
    print(f"{v:4d}  {k}")
