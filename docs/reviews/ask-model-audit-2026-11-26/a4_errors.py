"""Session 10234, evidence a4: the stored questions that ended in an error, and the cost each was recorded at.

Every JSON file of warehouse/chat/eval that holds a "questions" list; a record with an error (or status error) is
listed with its loop (python or site), its recorded cost and its tool calls. Reads saved files only."""
import glob
import json
import os

EVAL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "warehouse", "chat", "eval")
rows = []
for path in sorted(glob.glob(os.path.join(EVAL, "*.json"))):
    try:
        doc = json.load(open(path, encoding="utf-8"))
    except ValueError:
        continue
    qs = doc.get("questions") if isinstance(doc, dict) else None
    if not isinstance(qs, list):
        continue
    for q in qs:
        if not isinstance(q, dict):
            continue
        if q.get("error") or q.get("status") == "error":
            loop = q.get("loop") or ("python" if "_loop_" in os.path.basename(path) else "site")
            rows.append({"file": os.path.basename(path), "id": q.get("id"), "loop": loop, "cost_usd": q.get("cost_usd"),
                         "tool_calls": q.get("tool_calls"), "trace_calls": len(q.get("trace") or []),
                         "error": str(q.get("error"))[:140]})
print(json.dumps({"errors": len(rows),
                  "python_loop": [r for r in rows if r["loop"] == "python"],
                  "site_loop_zero_cost": [r for r in rows if r["loop"] != "python" and not r["cost_usd"]],
                  "site_loop_with_cost": len([r for r in rows if r["loop"] != "python" and r["cost_usd"]])}, indent=1))
