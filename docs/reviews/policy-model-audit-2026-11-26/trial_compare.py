"""Session 10217: the monitor's file built twice by its own builder (warehouse/policy/monitor_site.py) from the main copy's
tables of 13 and 14 November, with and without utility_large_load_rule_changes.csv: which records the 15 large-load
orders of FERC and the grid operators make or join, and what the view as it opens (significance 5 or more) shows of them.
    python runs/c10217/trial_compare.py runs/c10217/trial_with.json runs/c10217/trial_without.json
"""
import json
import sys

w = json.load(open(sys.argv[1], encoding="utf-8"))
wo = json.load(open(sys.argv[2], encoding="utf-8"))
a = {r["id"]: r for r in w["rows"]}
b = {r["id"]: r for r in wo["rows"]}
new = [a[k] for k in a if k not in b]
joined = [a[k] for k in a if k in b and a[k]["n"] != b[k]["n"]]
print(f"documents {wo['documents']} -> {w['documents']}; records {wo['records']} -> {w['records']}")
print(f"records made by the changes alone: {len(new)}; records they join: {len(joined)}")
op = lambda r: r.get("significance") is not None and r["significance"] >= 5
for r in new:
    print(f"  new {r['id']} {r['date']} {r['body']} {r['instrument']} {r['status']} sig {r.get('significance')} states {r.get('states')} title {r['title'][:80]!r}")
for r in joined:
    print(f"  joined {r['id']} {r['date']} {r['body']} n {b[r['id']]['n']}->{r['n']} sig {r.get('significance')} newest now {r['title'][:70]!r}; status {b[r['id']]['status']}->{r['status']}; date {b[r['id']]['date']}->{r['date']}")
print("shown as the view opens:", sum(1 for r in wo["rows"] if op(r)), "->", sum(1 for r in w["rows"] if op(r)))
print("of the records the changes make or join, shown as the view opens:", sum(1 for r in new + joined if op(r)))
