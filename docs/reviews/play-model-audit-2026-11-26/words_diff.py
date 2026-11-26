"""Session 10227: the drawn views of two tags set side by side: for each view, the sentences only one of them has.
    python words_diff.py <drawn dir> <tag a> <tag b>"""
import glob
import os
import re
import sys

d, a, b = sys.argv[1:4]
for pa in sorted(glob.glob(os.path.join(d, f"{a}_*.txt"))):
    view = os.path.basename(pa)[len(a) + 1:]
    pb = os.path.join(d, f"{b}_{view}")
    if not os.path.exists(pb):
        print(f"{view}: not drawn under {b}")
        continue
    split = lambda s: [x.strip() for x in re.split(r"(?<=[.;:])\s+|\n", s) if x.strip()]  # noqa: E731
    A, B = split(open(pa, encoding="utf-8").read()), split(open(pb, encoding="utf-8").read())
    only_a, only_b = [x for x in A if x not in set(B)], [x for x in B if x not in set(A)]
    print(f"{view}: {len(only_a)} only in {a}, {len(only_b)} only in {b}")
    for x in only_a:
        print(f"   - {x}")
    for x in only_b:
        print(f"   + {x}")
