"""Session 10234: print the tool results of chosen questions of a saved run, whole, to check an answer's every fact by hand."""
import json
import os
import sys

EVAL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "warehouse", "chat", "eval")
run = json.load(open(os.path.join(EVAL, sys.argv[1]), encoding="utf-8"))
ids = set(sys.argv[2].split(","))
limit = int(sys.argv[3]) if len(sys.argv) > 3 else 3000
for q in run["questions"]:
    if q["id"] not in ids:
        continue
    print("=" * 80)
    print(q["id"], q.get("answer"))
    for i, t in enumerate(q.get("trace") or []):
        print(f"--- call {i + 1} {t.get('tool')} {json.dumps(t.get('input'), default=str)}")
        print(json.dumps(t.get("out"), default=str)[:limit])
