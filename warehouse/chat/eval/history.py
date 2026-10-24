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
    """Session 1315: the runs and their rows from runs.json, the one list of the stored runs."""
    out = []
    for e in load("runs.json")["runs"]:
        h = e["history"]
        if h["kind"] == "answers":
            out.append(row_answers(e["file"], h["set"], h["what"], h["where"]))
        elif h["kind"] == "regrade":
            r = load(e["file"])
            out.append([(r.get("keys_computed_at_utc") or "")[:10], h["set"], h["what"], f"{r['right_under_hold']} of {len(r['questions'])} ({r['right_now']} on the figure keys)", "none (no model)", h["where"]])
        else:
            g, run = load(e["grades"]), load(e["file"])["questions"]
            right = (f"{g['right_under_hold']} of {g['asked']} ({g['right_now']} on the figure keys; {g['right_if_ruled']} if session 320's rulings went the answers' way)"
                     if h["kind"] == "held" else f"{g['right']} of {g['asked']}")
            out.append([asked_day(run), h["set"], h["what"].format(asked=g["asked"]), right, f"USD {g['cost_usd']:.2f}", h["where"]])
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
