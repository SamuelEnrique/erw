#!/usr/bin/env python3
"""Session 1147 (chain 085): the history of Ask's evaluations, one table, written from the stored runs alone.

Energy Research Warehouse (ERW). Every stored run of warehouse/chat/eval/ (its answers or its grades) is one row: the
day it was asked or graded, the set, what was graded, how many were right, its cost, and where it is described. Nothing
is read but these files, so the table cannot say more than they hold; a new run adds its file to RUNS and its row
appears. No model, no network.

    python warehouse/chat/eval/history.py            writes docs/reviews/ask-history.md
    python warehouse/chat/eval/history.py --check    exit 1 when the file on disk is not what the runs give
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(ROOT, "docs", "reviews", "ask-history.md")


def load(name):
    with open(os.path.join(HERE, name), encoding="utf-8") as f:
        return json.load(f)


def asked_day(qs):
    days = sorted(q["asked_at_utc"][:10] for q in qs if q.get("asked_at_utc"))
    return days[0] if days else ""


def cost(qs):
    vals = [float(q.get("cost_usd") or 0) for q in qs]
    return f"USD {sum(vals):.2f}" if any(vals) else "not recorded"


def ok_of(q):
    if "verdict" in q:
        return q["verdict"] == "right"
    g = q.get("grade") or {}
    return bool(g.get("ok"))


def row_answers(name, set_name, what, where):
    qs = load(name)["questions"]
    return [asked_day(qs), set_name, what, f"{sum(ok_of(q) for q in qs)} of {len(qs)}", cost(qs), where]


def rows():
    out = [
        row_answers("eval_s267_fixtures.json", "`questions_s267.yaml`", "every public grid, asked through `/api/ask` (the stored answers as fixed)", "session 267's report; `tests/test_session267.py`"),
        row_answers("eval_s302_fixtures.json", "`questions_s302.yaml`", "asked as the pages ask them (the stored answers after the fix at the cause)", "session 302's report"),
        row_answers("eval_s320_first_run.json", "`questions_s320.yaml`", "the three economics pages, first asking", "session 320's report"),
    ]
    r = load("eval_s539_regrade.json")
    out.append([(r.get("keys_computed_at_utc") or "")[:10], "`questions_s320.yaml`", "session 320's answers graded again on the keys of the day, under the license hold", f"{r['right_under_hold']} of {len(r['questions'])} ({r['right_now']} on the figure keys)", "none (no model)", "`docs/reviews/ask-thirty-2026-10-21.md`"])
    g = load("eval_s1113_grades.json")
    run = load("eval_s1113_run.json")["questions"]
    out.append([asked_day(run), "`questions_s320.yaml`", "asked again, graded under the hold", f"{g['right_under_hold']} of {g['asked']} ({g['right_now']} on the figure keys; {g['right_if_ruled']} if session 320's rulings went the answers' way)", f"USD {g['cost_usd']:.2f}", "`docs/reviews/ask-thirty-2026-10-23.md`"])
    g = load("eval_s1114_grades.json")
    run = load("eval_s1114_run.json")["questions"]
    out.append([asked_day(run), "`questions_s1114.yaml`", "thirty a trading, a finance and a policy lead ask, first asking", f"{g['right']} of {g['asked']}", f"USD {g['cost_usd']:.2f}", "`docs/reviews/ask-sixty-2026-10-23.md`"])
    # session 1190: session 1149's asking again after chains 076 and 085 (eval_s1133_*), the second set stopped by its cap
    g = load("eval_s1133_s320_grades.json")
    run = load("eval_s1133_s320_run.json")["questions"]
    out.append([asked_day(run), "`questions_s320.yaml`", "asked again after chains 076 and 085, graded under the hold", f"{g['right_under_hold']} of {g['asked']} ({g['right_now']} on the figure keys; {g['right_if_ruled']} if session 320's rulings went the answers' way)", f"USD {g['cost_usd']:.2f}", "`docs/reviews/ask-sixty-2026-10-25.md`"])
    g = load("eval_s1133_s1114_grades.json")
    run = load("eval_s1133_s1114_run.json")["questions"]
    out.append([asked_day(run), "`questions_s1114.yaml`", f"asked again after chains 076 and 085, {g['asked']} of the thirty (the cap)", f"{g['right']} of {g['asked']}", f"USD {g['cost_usd']:.2f}", "`docs/reviews/ask-sixty-2026-10-25.md`"])
    return out


def text():
    lines = ["# Ask's evaluations: the history", "",
             "Energy Research Warehouse (ERW). Written by `python warehouse/chat/eval/history.py` from the stored runs of `warehouse/chat/eval/` alone (session 1147); a test holds this file to what they give. A row is a run: the day it was asked (or graded), the set, what was graded, how many were right, its cost through the model, and where it is described.", "",
             "| Day | Set | What | Right | Cost | Described in |", "|---|---|---|---|---|---|"]
    lines += ["| " + " | ".join(r) + " |" for r in rows()]
    return "\n".join(lines) + "\n"


def main(argv):
    body = text()
    if "--check" in argv:
        with open(OUT, encoding="utf-8") as f:
            return 0 if f.read().replace("\r\n", "\n") == body else 1
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(body)
    print(body)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
