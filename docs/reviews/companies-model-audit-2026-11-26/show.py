"""Print chosen keys of measures.json on one line each. Session 10228."""
import json
import os
import sys

M = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), sys.argv[1] if len(sys.argv) > 1 else "measures.json"), encoding="utf-8"))
dc = M.get("double_count", {})
for k in ("top10", "top10_without_overlap", "top10_operated_planned_queue", "largest"):
    if k in dc:
        print(k, json.dumps(dc[k]))
for k, v in M.get("families", {}).items():
    print("family", k, json.dumps(v))
