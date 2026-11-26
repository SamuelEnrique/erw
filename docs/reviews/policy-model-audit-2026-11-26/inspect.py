"""Session 10217: a first look at the policy monitor's two site files and the warehouse CSVs it is built from.
Prints shapes, keys and counts only (no row of a held table is printed whole).
    .venv python runs/c10217/inspect.py <worktree root> <main copy warehouse/output>
"""
import collections
import csv
import json
import os
import sys

root, out = sys.argv[1], sys.argv[2]
m = json.load(open(os.path.join(root, "site", "data", "policy", "monitor.json"), encoding="utf-8"))
print("monitor.json keys:", [k for k in m if k != "rows"])
print("built", m["built"], "documents", m["documents"], "records", m["records"], "rows", len(m["rows"]))
print("fields_from", m["fields_from"])
keys = collections.Counter(k for r in m["rows"] for k in r)
print("row keys:", dict(keys))
print("last date", max(r["date"] for r in m["rows"]), "first date", min(r["date"] for r in m["rows"]))
print("statuses", collections.Counter(r["status"] for r in m["rows"]).most_common())
print("bodies", collections.Counter(r["body"] for r in m["rows"]).most_common())
print("instruments", collections.Counter(r["instrument"] for r in m["rows"]).most_common())
print("significance", sorted(collections.Counter(r.get("significance")for r in m["rows"]).items(), key=lambda x: (x[0] is None, x[0] or 0)))
print("sample steps", [r["steps"][:2] for r in m["rows"] if r.get("steps")][:2])
print("sample history", [r["history"] for r in m["rows"] if r.get("n", 1) > 2][:2])

ll = json.load(open(os.path.join(root, "site", "data", "siting", "large_load_rules.json"), encoding="utf-8"))
print("large_load_rules.json keys:", list(ll))
print("built", ll["built"], "retrieved", ll["retrieved"], "counts", ll.get("counts"))
print("laws", len(ll["laws"]), "held_laws", len(ll["held_laws"]), "rules", len(ll["rules"]), "held_rules", len(ll["held_rules"]), "changes", len(ll["changes"]), "held_changes", len(ll["held_changes"]))
print("law keys", list(ll["laws"][0]))
print("change keys", list(ll["changes"][0]))
print("law_searches", len(ll.get("law_searches", [])), ll.get("law_searches", [])[:2])
print("change dates", sorted(collections.Counter(c["date"][:7] for c in ll["changes"]).items()))
print("change date kinds", collections.Counter(c.get("date_kind") for c in ll["changes"]))
print("min max change date", min(c["date"] for c in ll["changes"]), max(c["date"] for c in ll["changes"]))

for name in ["policy_actions", "policy_reads", "state_large_load_laws", "utility_large_load_rule_changes", "utility_large_load_rules"]:
    p = os.path.join(out, name + ".csv")
    with open(p, encoding="utf-8") as f:
        head = []
        for ln in f:
            if ln.startswith("#"):
                head.append(ln.rstrip()[:220])
            else:
                break
    with open(p, encoding="utf-8") as f:
        rows = list(csv.DictReader(ln for ln in f if not ln.startswith("#")))
    print(name, len(rows), "rows; header:")
    for h in head:
        print("   ", h)
    print("    columns:", list(rows[0])[:40])
