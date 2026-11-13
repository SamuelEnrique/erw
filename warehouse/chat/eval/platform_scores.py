#!/usr/bin/env python3
"""Session 5252 (chain 238): the platform set's scores, written into its review file from the stored runs alone.

Energy Research Warehouse (ERW). docs/reviews/ask-eval-2026-11-13.md says what was asked, what was right and what it
cost. Those tables are written here, between the two marker lines of the file, from the runs of the set
(eval_s<N>_site_platform_run.json) and their grades (eval_site.py writes both), so the file cannot say more than the runs
hold. A question asked in two sessions counts once, its newest answer standing. No model, no network.

    python warehouse/chat/eval/platform_scores.py            writes the section
    python warehouse/chat/eval/platform_scores.py --check    exit 1 when the file on disk is not what the runs give
"""
import importlib.util
import json
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(ROOT, "docs", "reviews", "ask-eval-2026-11-13.md")
BEGIN, END = "<!-- scores: written by warehouse/chat/eval/platform_scores.py from the stored runs; do not edit by hand -->", "<!-- scores: end -->"
SET = "platform"
SECTORS = ("power", "prices", "gas", "oil", "nuclear", "renewables", "storage", "transmission", "projects", "deals", "policy", "datacenters")
KINDS = ("figure", "hold", "pause", "not_live", "outside", "gap", "partial")
LIMIT = 12


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def load(S, E, here=HERE):
    """(the set's questions, [(session, run questions, grades by id)] oldest first)."""
    qs = E.questions(E.SETS[SET]["questions"])
    runs = []
    for s in S.sessions_of(SET, here):
        F = S.files(s, SET, here)
        run = S.read_json(F["run"])["questions"]
        grades = {g["id"]: g for g in S.read_json(F["grades"])["questions"]} if os.path.exists(F["grades"]) else {}
        runs.append((s, run, grades))
    return qs, runs


def newest(runs):
    """One record a question over the runs, the newest session's standing: {id: (session, answer record, grade)}."""
    out = {}
    for s, run, grades in runs:
        for q in run:
            out[q["id"]] = (s, q, grades.get(q["id"]))
    return out


def ids_line(ids):
    return ", ".join(ids) if ids else "none"


def text(qs, runs):
    by = {q["id"]: q for q in qs}
    last = newest(runs)
    asked = [i for i in by if i in last]
    right = [i for i in asked if (last[i][2] or {}).get("ok")]
    cost = sum(float(q.get("cost_usd") or 0) for _, run, _ in runs for q in run)
    lines = [BEGIN, "",
             f"**Asked: {len(asked)} of {len(qs)}. Right: {len(right)}. Cost: USD {cost:.2f}.** Graded under `{'`, `'.join(rules_of(runs))}`.", "",
             "### The askings", "",
             "| Session | Asked | Right | Cost | Tool calls: median, most | At 11 or 12 calls | Sent back once |",
             "|---|---:|---:|---|---|---:|---:|"]
    for s, run, grades in runs:
        calls = [int(q.get("tool_calls") or 0) for q in run]
        lines.append(f"| {s} | {len(run)} | {sum(1 for q in run if (grades.get(q['id']) or {}).get('ok'))} | USD {sum(float(q.get('cost_usd') or 0) for q in run):.2f} | "
                     f"{statistics.median(calls):g}, {max(calls)} | {sum(1 for c in calls if c >= LIMIT - 1)} | {sum(1 for q in run if q.get('retried'))} |")
    lines += ["", "### By kind", "", "| Kind | In the set | Asked | Right |", "|---|---:|---:|---:|"]
    for k in KINDS:
        of = [i for i in by if by[i].get("kind") == k]
        lines.append(f"| {k} | {len(of)} | {sum(1 for i in of if i in last)} | {sum(1 for i in of if i in right)} |")
    lines += ["", "### By area", "", "| Area | In the set | Asked | Right |", "|---|---:|---:|---:|"]
    for a in SECTORS:
        of = [i for i in by if by[i].get("sector") == a]
        lines.append(f"| {a} | {len(of)} | {sum(1 for i in of if i in last)} | {sum(1 for i in of if i in right)} |")
    wrong = [i for i in asked if i not in right]
    lines += ["", "### Not right", ""]
    if not wrong:
        lines.append("- None.")
    for i in wrong:
        s, q, g = last[i]
        failed = [k for k, v in ((g or {}).get("grade") or {}).items() if v is False and k != "ok"]
        lines.append(f"- `{i}` ({by[i].get('kind')}, {by[i].get('sector')}; session {s}; status `{q.get('status')}`, {q.get('tool_calls')} calls): not met: {ids_line(failed)}.")
    lines += ["", "### Tool calls and cost by kind", "", "| Kind | Asked | Calls: median, most | Mean cost |", "|---|---:|---|---|"]
    for k in KINDS:
        recs = [last[i][1] for i in asked if by[i].get("kind") == k]
        if recs:
            calls = [int(q.get("tool_calls") or 0) for q in recs]
            lines.append(f"| {k} | {len(recs)} | {statistics.median(calls):g}, {max(calls)} | USD {sum(float(q.get('cost_usd') or 0) for q in recs) / len(recs):.3f} |")
    lines += ["", f"Asked: {ids_line(asked)}.", "", END]
    return "\n".join(lines)


def rules_of(runs):
    """The rules the grades files name (the same in every one after a grading of all the runs)."""
    found = []
    for s, _, _ in runs:
        p = os.path.join(HERE, f"eval_s{s}_site_{SET}_grades.json")
        if os.path.exists(p):
            with open(p, encoding="utf-8") as f:
                for r in json.load(f).get("rules") or []:
                    if r not in found:
                        found.append(r)
    return found or ["no rule"]


def placed(doc, section):
    """The file's text with the section between its markers; the run stops when the markers are not both there once."""
    if doc.count(BEGIN) != 1 or doc.count(END) != 1 or doc.index(BEGIN) > doc.index(END):
        raise SystemExit(f"the two marker lines are not in {os.path.relpath(OUT, ROOT)} once each, in order")
    return doc[: doc.index(BEGIN)] + section + doc[doc.index(END) + len(END):]


def main(argv):
    S = module("eval_site_for_scores", os.path.join(HERE, "eval_site.py"))
    E = module("eval_s1113_for_scores", os.path.join(HERE, "eval_s1113.py"))
    qs, runs = load(S, E)
    with open(OUT, encoding="utf-8") as f:
        doc = f.read()
    new = placed(doc, text(qs, runs))
    if "--check" in argv:
        print("the review file's scores are the runs'" if new == doc else "the review file's scores are not what the runs give: python warehouse/chat/eval/platform_scores.py")
        return 0 if new == doc else 1
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(new)
    print(f"wrote the scores of {len(runs)} runs into {os.path.relpath(OUT, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
