"""Session 10234, evidence a6b: in the stored held-grid questions, does any tool result hold a value of a held grid's
row? Every trace entry of the 48 records a6 finds is walked; a dict whose entity (or grid) names NYISO or ISO-NE and
that carries a numeric value is counted. Prints counts and record ids only, never a value."""
import json
import os

EVAL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "warehouse", "chat", "eval")
runs = json.load(open(os.path.join(EVAL, "runs.json"), encoding="utf-8"))["runs"]
HELD = ("nyiso", "isone", "iso-ne", "iso_ne")


def held_values(x):
    n = 0
    if isinstance(x, dict):
        who = " ".join(str(x.get(k) or "") for k in ("entity", "grid", "iso")).lower()
        if any(h in who for h in HELD) and any(isinstance(x.get(k), (int, float)) and not isinstance(x.get(k), bool) for k in ("value", "count", "sum", "mean")):
            n += 1
        for v in x.values():
            n += held_values(v)
    elif isinstance(x, list):
        for v in x:
            n += held_values(v)
    return n


questions, with_values = 0, []
for r in runs:
    try:
        doc = json.load(open(os.path.join(EVAL, r["file"]), encoding="utf-8"))
    except (OSError, ValueError):
        continue
    for q in doc.get("questions") or []:
        if not isinstance(q, dict):
            continue
        trace = [t for t in (q.get("trace") or []) if isinstance(t, dict)]
        if not any(isinstance(t.get("out"), dict) and t["out"].get("held") is True for t in trace):
            continue
        questions += 1
        n = sum(held_values(t.get("out")) for t in trace)
        if n:
            with_values.append({"run": r["label"], "id": q.get("id"), "held_rows_with_a_value": n})
print(json.dumps({"held_questions": questions, "with_a_held_rows_value_in_a_tool_result": with_values}, indent=1))
