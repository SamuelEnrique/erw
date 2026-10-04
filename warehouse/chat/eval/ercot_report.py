#!/usr/bin/env python3
"""The ERCOT evaluation, before and after, in one table (session 92).

Energy Research Warehouse (ERW).

    python warehouse/chat/eval/ercot_report.py [--after RUN] [--out results/ercot_summary.md]

Reads the records ercot_eval.py wrote (results/ercot_before_*.jsonl, results/ercot_after_*.jsonl), scores each again
with the question set as it is now (the tables a question accepts were widened once, where the chat as it was gave
the right number from another table that holds it), and writes one summary. No model call.

before  every record of the "before" arm; a question asked more than once counts by its newest record that is not a
        network error. The arm was not asked every question (the session's spend cap): the questions not asked are
        listed, and never counted as right or wrong.
after   one run, whole: the newest "after" run that holds every question (or --after <run id>).
"""

import argparse
import glob
import json
import os
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, ".."))
RES = os.path.join(HERE, "results")
KINDS = ["lookup", "series", "join", "refuse", "context"]


def records(arm):
    out = []
    for f in sorted(glob.glob(os.path.join(RES, f"ercot_{arm}_*.jsonl"))):
        run = os.path.basename(f)[len(f"ercot_{arm}_"):-6]
        for line in open(f, encoding="utf-8"):
            if line.strip():
                out.append(dict(json.loads(line), run=run))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="The ERCOT evaluation, before and after")
    ap.add_argument("--after", help="the run id of the after arm (default: the newest run that holds every question)")
    ap.add_argument("--out", default=os.path.join(RES, "ercot_summary.md"))
    a = ap.parse_args(argv)
    import eval as base
    import ercot_eval
    spec = yaml.safe_load(open(os.path.join(HERE, "questions_ercot.yaml"), encoding="utf-8"))
    qs = {q["id"]: q for q in spec["questions"]}
    by_text = {q["question"]: q for q in spec["questions"]}

    def rescored(rec, arm):
        q = by_text.get(rec["question"]) or qs[rec["id"]]
        s = base.score(q, rec)
        if arm == "after":
            x = ercot_eval.extras(q, rec)
            s.update(x)
            s["full"] = s["correct"] and all(x.values())
        return q["id"], s

    before = {}
    for r in records("before"):
        if r.get("status") == "error" and r["id"] in before:
            continue
        i, s = rescored(r, "before")
        if r.get("status") == "error" and i not in before:
            before[i] = (r, s)
        elif r.get("status") != "error":
            before[i] = (r, s)
    runs = {}
    for r in records("after"):
        runs.setdefault(r["run"], []).append(r)
    whole = [k for k, v in sorted(runs.items()) if len({x["question"] for x in v}) == len(qs)]
    run = a.after or (whole[-1] if whole else None)
    if run is None:
        raise SystemExit("no after run holds every question")
    after = dict(rescored(r, "after")[0:1] + ((r, rescored(r, "after")[1]),) for r in runs[run])
    first = dict(rescored(r, "after")[0:1] + ((r, rescored(r, "after")[1]),) for r in runs[whole[0]]) if len(whole) > 1 and whole[0] != run else None

    def tally(d, key="correct"):
        return sum(s[key] for _, s in d.values() if key in s), sum(1 for _, s in d.values() if key in s)

    def cost(d):
        return sum((r.get("cost_usd") or 0) for r, _ in d.values())

    not_asked = [i for i in qs if i not in before]
    b_ok, b_n = tally(before)
    a_ok, a_n = tally(after)
    same = [i for i in before if i in after]
    lines = ["# ERCOT evaluation: before and after", "",
             f"{len(qs)} questions (questions_ercot.yaml, today = {spec['today']}), backend local. Before: the grid page's chat as it was "
             f"(ask.py --grid ercot), {b_n} questions asked. After: Ask ERCOT, the reference version (ercot.py), run {run}, all {a_n}.", "",
             "| Measure | Before | After |", "|---|---|---|",
             f"| Correct, on the questions the arm was asked | {b_ok} of {b_n} ({100 * b_ok / max(b_n, 1):.0f}%) | {a_ok} of {a_n} ({100 * a_ok / max(a_n, 1):.0f}%) |",
             f"| Correct, on the {len(same)} questions both were asked | {sum(before[i][1]['correct'] for i in same)} of {len(same)} | {sum(after[i][1]['correct'] for i in same)} of {len(same)} |"]
    for k in KINDS:
        bk = {i: v for i, v in before.items() if qs[i]["kind"] == k}
        ak = {i: v for i, v in after.items() if qs[i]["kind"] == k}
        lines.append(f"| Correct, {k} | {tally(bk)[0]} of {tally(bk)[1]} | {tally(ak)[0]} of {tally(ak)[1]} |")
    for k in ("followups", "series", "full"):
        ok, n = tally(after, k)
        lines.append(f"| {k} | not offered | {ok} of {n} |")
    lines += [f"| Retried after the check | {sum(bool(r.get('retried')) for r, _ in before.values())} of {b_n} | {sum(bool(r.get('retried')) for r, _ in after.values())} of {a_n} |",
              f"| Mean tool calls | {sum(r.get('tool_calls', 0) for r, _ in before.values()) / max(b_n, 1):.2f} | {sum(r.get('tool_calls', 0) for r, _ in after.values()) / max(a_n, 1):.2f} |",
              f"| Cost of the records counted | USD {cost(before):.4f} | USD {cost(after):.4f} |",
              f"| Mean cost per question | USD {cost(before) / max(b_n, 1):.4f} | USD {cost(after) / max(a_n, 1):.4f} |"]
    if first:
        f_ok, f_n = tally(first)
        lines += ["", f"The reference version's first whole run ({whole[0]}), before the three fixes it led to: {f_ok} of {f_n} correct, "
                      f"{sum(bool(r.get('retried')) for r, _ in first.values())} sent back once by the check, USD {cost(first):.4f}."]
    if not_asked:
        lines += ["", f"Not asked of the chat as it was ({len(not_asked)}; the spend cap): " + ", ".join(not_asked) + ". Each needs a table outside its scope; they are not counted."]
    lines += ["", "| Id | Kind | Before | After | Question |", "|---|---|---|---|---|"]
    for i, q in qs.items():
        b = "not asked" if i not in before else ("correct" if before[i][1]["correct"] else f"wrong ({before[i][0].get('status')})")
        s = after[i][1]
        x = "correct" if s["full"] else ("correct, but " + ", ".join(k for k in ("followups", "series") if k in s and not s[k]) if s["correct"] else f"wrong ({after[i][0].get('status')})")
        lines.append(f"| {i} | {q['kind']} | {b} | {x} | {q['question']} |")
    with open(a.out, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines[:22 + (2 if first else 0) + (2 if not_asked else 0)]))
    print(f"summary: {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
