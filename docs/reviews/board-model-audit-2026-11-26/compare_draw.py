# Session 10206: a branch's drawn /cost-of-power against origin/main's: every changed line of the words a reader sees
# (hovers in brackets) and every changed piece of the HTML (split at tags), plus em dashes in the branch's drawing.
#   python compare_draw.py <base dir> <branch dir>
import difflib
import os
import re
import sys

base, branch = sys.argv[1], sys.argv[2]
EM = chr(0x2014)
for name in sorted(os.listdir(base)):
    if not name.endswith(".txt"):
        continue
    stem = name[:-4]
    a = open(os.path.join(base, name), encoding="utf-8").read().splitlines()
    b = open(os.path.join(branch, name), encoding="utf-8").read().splitlines()
    ha = re.split(r"(?=<)", open(os.path.join(base, stem + ".html"), encoding="utf-8").read())
    hb_text = open(os.path.join(branch, stem + ".html"), encoding="utf-8").read()
    hb = re.split(r"(?=<)", hb_text)
    print(f"===== {stem}: {len(a)} lines on main, {len(b)} on the branch; em dashes in the branch's HTML: {hb_text.count(EM)}")
    for line in difflib.unified_diff(a, b, lineterm="", n=0):
        if line.startswith(("---", "+++")):
            continue
        print("  TXT " + line[:1600])
    changed = [l for l in difflib.unified_diff(ha, hb, lineterm="", n=0) if l[:1] in "+-" and not l.startswith(("---", "+++"))]
    print(f"  HTML pieces changed: {len(changed)}")
    for l in changed[:12]:
        print("  HTML " + l[:400])
