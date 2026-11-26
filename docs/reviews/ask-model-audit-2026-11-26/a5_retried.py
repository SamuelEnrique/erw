"""Session 10234, evidence a5: why the stored answers that were sent back once were sent back.

Every stored run named in runs.json; a record with retried true is classed by its first violations: a number in no tool
result (a violation that is a bare number), a unit, a cited table no tool read, an empty or uncited answer, or another of
the loop's checks (a refusal that states a figure, an answer cut short, an answer to a table the site cannot read).
The page draws "the first draft was sent back because a number could not be traced" for every one of them
(site/app/ask/AskForm.tsx). Reads saved files only."""
import json
import os
import re
from collections import Counter

EVAL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "warehouse", "chat", "eval")
runs = json.load(open(os.path.join(EVAL, "runs.json"), encoding="utf-8"))["runs"]
count, kinds, examples, unknown = 0, Counter(), [], 0
for r in runs:
    try:
        doc = json.load(open(os.path.join(EVAL, r["file"]), encoding="utf-8"))
    except (OSError, ValueError):
        continue
    for q in doc.get("questions") or []:
        if not isinstance(q, dict) or not q.get("retried"):
            continue
        count += 1
        fv = q.get("first_violations")
        if not fv:
            unknown += 1
            continue
        k = set()
        for v in fv:
            s = str(v)
            if re.fullmatch(r"-?[\d.,]+", s.strip()):
                k.add("number")
            elif s.startswith("unit:"):
                k.add("unit")
            elif s.startswith("cited table not read"):
                k.add("uncited")
            elif s.startswith("empty or uncited"):
                k.add("empty")
            else:
                k.add("other: " + s[:60])
        kinds["number" if "number" in k else "no number: " + ", ".join(sorted(k))] += 1
        if "number" not in k and len(examples) < 10:
            examples.append({"run": r["label"], "id": q.get("id"), "first_violations": [str(x)[:140] for x in fv]})
print(json.dumps({"retried": count, "without_a_record_of_why": unknown, "classes": kinds.most_common(), "examples": examples}, indent=1))
