"""Session 10220: what a price table holds (entities, markets, span), streamed line by line. Read only.
usage: s2_peek.py PATH"""
import csv
import sys
from collections import defaultdict

path = sys.argv[1]
span = defaultdict(lambda: [None, None, 0])
cols = None
with open(path, encoding="utf-8") as fh:
    for line in fh:
        if line.startswith("#"):
            continue
        cols = next(csv.reader([line]))
        break
    print("columns", cols)
    rd = csv.reader(fh)
    ie, iv, it, im = cols.index("entity"), cols.index("variable"), cols.index("ts_utc"), cols.index("market")
    inode = cols.index("node") if "node" in cols else None
    for row in rd:
        k = (row[im], row[ie], row[iv], row[inode] if inode is not None else "")
        s = span[k]
        t = row[it]
        if s[0] is None or t < s[0]:
            s[0] = t
        if s[1] is None or t > s[1]:
            s[1] = t
        s[2] += 1
for k in sorted(span):
    if k[0].startswith("spp") or k[0].startswith("caiso"):
        print(k, span[k])
print("markets", sorted({k[0] for k in span}))
