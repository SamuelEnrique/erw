"""Session 10234, evidence a7: how many stored answers lean on a number that only the question, a tool argument or the
day line holds.

For every stored answer replay.py replays, ask.unverified is run three ways: with the sources replay.check builds (the
question, the day line, every tool result, every tool argument); with the tool results and the day line only; with the
tool results only. An answer that passes the first and not a later one states a figure that no tool returned. Reads
saved files only; no model, no network."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "chat", "eval"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "chat"))
import replay as R  # noqa: E402
import ask  # noqa: E402

n, full_ok, no_q_args, results_only, examples = 0, 0, 0, 0, []
for name, graded, label in R.RUNS:
    for q in R.load(name)["questions"]:
        trace = R.trace_of(q)
        if not trace or not q.get("answer") or q.get("status") not in ("answered", "not_in_warehouse"):
            continue
        n += 1
        today = (q.get("asked_at_utc") or "")[:10]
        outs = [json.dumps(t.get("out"), default=str) for t in trace]
        args = [json.dumps(t.get("input"), default=str) for t in trace]
        day = f"Today is {today} (UTC)."
        a = q["answer"]
        if ask.unverified(a, [q.get("question") or "", day] + outs + args):
            continue
        full_ok += 1
        b = ask.unverified(a, [day] + outs)
        c = ask.unverified(a, outs)
        if b:
            no_q_args += 1
        if c:
            results_only += 1
        if (b or c) and len(examples) < 25:
            examples.append({"run": label, "id": q.get("id"), "status": q.get("status"), "without_question_and_arguments": b, "without_the_day_line_too": c})
print(json.dumps({"answers": n, "pass_as_stored": full_ok, "fail_without_question_and_arguments": no_q_args,
                  "fail_on_tool_results_alone": results_only, "examples": examples}, indent=1))
