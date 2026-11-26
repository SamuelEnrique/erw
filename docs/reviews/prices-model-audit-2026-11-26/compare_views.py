"""Session 10218: main's drawing of /prices/compare against the merged words branch's, view by view: every marked figure
the same, in order; and the words that changed (sentences in one and not the other)."""
import json
import re
import sys

a = json.load(open(sys.argv[1], encoding="utf-8"))
b = json.load(open(sys.argv[2], encoding="utf-8"))
for v in a:
    same = list(a[v]["marked"].items()) == list(b[v]["marked"].items())
    print(f"{v}: {len(a[v]['marked'])} marked figures on main, {len(b[v]['marked'])} on the branch; identical: {same}; em dashes {b[v]['emDashes']}")
    sa = set(re.split(r"(?<=[.;])\s+", a[v]["text"]))
    sb = set(re.split(r"(?<=[.;])\s+", b[v]["text"]))
    for s in sorted(sb - sa):
        print("   + " + s[:400])
    for s in sorted(sa - sb):
        print("   - " + s[:400])
    if v != "default":
        break
