# Session 10233: a words branch's drawings set against main's: the /data table's 111 rows cell by cell, and every number
# printed on each page (the multiset of digit groups in its visible text, the new words' own numbers named apart).
#   python runs/c10233/nofig.py <main prefix> <branch prefix> [allowed number ...]
import json
import re
import sys
from collections import Counter

a, b, allowed = sys.argv[1], sys.argv[2], set(sys.argv[3:])
ra = json.load(open(a + "_data_rows.json", encoding="utf-8"))
rb = json.load(open(b + "_data_rows.json", encoding="utf-8"))
cells = sum(len(x["cells"]) for x in ra)
diff = [(x["id"], i) for x, y in zip(ra, rb) for i, (p, q) in enumerate(zip(x["cells"], y["cells"])) if p != q]
print(f"/data rows {len(ra)} and {len(rb)}; cells {cells}; cells that differ {len(diff)} {diff[:5]}")
bad = 0
for page in ("data", "faults", "licenses", "standard", "method_impossible_hours", "method_packages"):
    na = Counter(re.findall(r"\d[\d,.]*\d|\d", open(f"{a}_{page}.txt", encoding="utf-8").read()))
    nb = Counter(re.findall(r"\d[\d,.]*\d|\d", open(f"{b}_{page}.txt", encoding="utf-8").read()))
    gone = {k: v for k, v in (na - nb).items()}
    new = {k: v for k, v in (nb - na).items() if k not in allowed}
    print(f"{page}: numbers {sum(na.values())} and {sum(nb.values())}; gone {gone}; new (not allowed) {new}")
    bad += bool(gone) or bool(new)
print("no figure moved" if not diff and not bad else "A FIGURE MOVED")
sys.exit(1 if diff or bad else 0)
