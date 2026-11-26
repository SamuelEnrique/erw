"""Session 10222: list the rows of site/data/supply.json (id, group, status, last date, last value, unit)."""
import json
import sys

f = json.load(open(sys.argv[1], encoding="utf-8"))
print("built", f["built"], "rows", len(f["rows"]))
for r in f["rows"]:
    last = r.get("last") or {}
    print(f'{r["group"]:9} {r["id"]:40} {r["status"]:9} {r.get("freq",""):1} {last.get("t",""):10} {last.get("v","")!s:>14} {r.get("unit","")}')
print("sources:")
for i, s in enumerate(f["sources"]):
    print(i, s)
print("calendar", json.dumps(f["calendar"])[:600])
