# Session 10206: for each drawn case of a branch, are the numbers a reader sees (in order, words and hovers) the same as
# on origin/main? Prints the changed lines' numbers when they differ.
#   python numbers_same.py <base dir> <branch dir>
import os
import re
import sys

base, branch = sys.argv[1], sys.argv[2]
NUM = re.compile(r"-?\d[\d,]*\.?\d*")
for name in sorted(os.listdir(base)):
    if not name.endswith(".txt"):
        continue
    a = NUM.findall(open(os.path.join(base, name), encoding="utf-8").read())
    b = NUM.findall(open(os.path.join(branch, name), encoding="utf-8").read())
    print(f"{name}: {len(a)} numbers on main, {len(b)} on the branch, the same in order: {a == b}")
    if a != b:
        for i, (x, y) in enumerate(zip(a, b)):
            if x != y:
                print("   first difference at", i, x, y)
                break
