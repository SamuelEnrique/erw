"""Session 10234, evidence a6: what a held grid's question got in the stored runs.

Every stored run of runs.json with a tool record; a record whose trace holds a result with "held": true (a held grid's
rows asked for, answered with the hold's words and the public grids' figures) is counted by its final status. The
general form heads status "answered" with "Answered from the warehouse" (site/app/ask/AskForm.tsx STATUS). Reads saved
files only; prints no figure."""
import json
import os
from collections import Counter

EVAL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "warehouse", "chat", "eval")
runs = json.load(open(os.path.join(EVAL, "runs.json"), encoding="utf-8"))["runs"]
by_status, grids, ids = Counter(), Counter(), []
for r in runs:
    try:
        doc = json.load(open(os.path.join(EVAL, r["file"]), encoding="utf-8"))
    except (OSError, ValueError):
        continue
    for q in doc.get("questions") or []:
        if not isinstance(q, dict):
            continue
        held = [t.get("out") for t in (q.get("trace") or []) if isinstance(t, dict) and isinstance(t.get("out"), dict) and t["out"].get("held") is True]
        if not held:
            continue
        by_status[q.get("status")] += 1
        for h in held:
            grids[h.get("grid")] += 1
        ids.append(f"{r['label']}|{q.get('id')}|{q.get('status')}")
print(json.dumps({"held_questions": sum(by_status.values()), "by_status": by_status.most_common(), "held_results_by_grid": grids.most_common(),
                  "records": ids}, indent=1))
