#!/usr/bin/env python3
"""Energy Research Warehouse (ERW), session 161: the record of Ask ERCOT's test questions asked on 8 October 2026 (UTC)
after the session's three changes: the average day by hour drawn as a line, "this week" as one call, and generation by
fuel over a stretch of days as two reads planned by rule. No model and no request: it reads the runner's own lines
(site/scripts/eval-ask-speed.mjs writes one a question) and writes one row a question asked.

    python warehouse/chat/eval/ercot_results_161.py --runs C:/.../runs/session161 --write
    python warehouse/chat/eval/ercot_results_161.py --summary

The runs, in the order asked: `targets` (six of the 100 that this session and session 156 changed, asked first so that
they are measured whatever the spending cap does), `old100` (the rest of the 100 of session 137, one of each kind in
turn) and `new20` (the 20 questions of the four pages, as far as the cap of USD 2 allowed). Each question was asked
once, on a local server; production was not asked. A question the cap left unasked has no row: the header of the table
says how many were asked. s156_ sets each answer beside the same question in session 156's record
(warehouse/chat/eval_ercot_ready_results_156.csv).
"""
import argparse
import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ercot_ready_results_156 as base  # noqa: E402  the same reading of a runner's line, and the same summary

ROOT = base.ROOT
OUT = os.path.join(ROOT, "warehouse", "chat", "eval_ercot_results_161.csv")
R156 = base.OUT
COLS = [c for c in base.COLS if not c.startswith(("s148_", "s153_"))] + ["s156_pass", "s156_seconds_words", "s156_model_calls", "s156_usd"]


def head(asked_old, asked_new):
    return [
        "# Energy Research Warehouse (ERW), session 161: Ask ERCOT on its 120 test questions, 8 October 2026 (UTC), one row a question asked.",
        f"# Asked: {asked_old} of the 100 of session 137 (set old; warehouse/chat/eval_ercot_panel.json) and {asked_new} of the 20 of four pages (set new; warehouse/chat/eval_ercot_pages.json). The session's spending cap of USD 2 stopped the run before the rest; a question not asked has no row.",
        "# The tool as the code stands after the session: the hours of a day as one line, day \"this_week\" in the query, generation by fuel over a stretch of days planned by rule. A local server; production was not asked.",
        "# pass: the rule of the question's kind (site/scripts/eval-judge.mjs), for set new also the expected number, the source and the chart's row. usd: the server's own model calls for the question.",
        "# seconds_words: from the question to the answer's words, at the reader's end. planned_by rule: the read was written by code. s156_: the same question in session 156's record.",
        "# Written by warehouse/chat/eval/ercot_results_161.py from the runner's lines; do not edit by hand.",
    ]


def before():
    out = {}
    with open(R156, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(l for l in f if not l.startswith("#")):
            if r["set"] in ("new", "old"):
                out[r["id"]] = r
    return out


def row(kind_of_set, r, b156):
    x = base.row(kind_of_set, r, {}, {})
    for step in r.get("steps") or []:
        if step.get("what") == "tools" and any((c.get("args") or {}).get("day") == "this_week" for c in step.get("calls") or []):
            x["tools"] += "+this_week"
    b = b156.get(r["id"], {})
    x = {k: v for k, v in x.items() if k in COLS}
    x.update({"s156_pass": b.get("pass", ""), "s156_seconds_words": b.get("seconds_words", ""), "s156_model_calls": b.get("model_calls", ""), "s156_usd": b.get("usd", "")})
    return x


def read_record():
    with open(OUT, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(l for l in f if not l.startswith("#")))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", help="the folder that holds targets.jsonl, old100.jsonl and new20.jsonl")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--summary", action="store_true")
    a = ap.parse_args()
    if a.write:
        if not a.runs:
            print("--write needs --runs")
            return 2
        b156 = before()
        old = base.lines(os.path.join(a.runs, "targets.jsonl")) + base.lines(os.path.join(a.runs, "old100.jsonl"))
        new = base.lines(os.path.join(a.runs, "new20.jsonl"))
        rows = [row("old", r, b156) for r in old] + [row("new", r, b156) for r in new]
        if not rows:
            print(f"no answers under {a.runs}: nothing is written")
            return 1
        if os.path.exists(OUT):
            print(f"{OUT} exists: it is not written over (remove it by hand to write it again)")
            return 1
        with open(OUT, "w", encoding="utf-8", newline="") as f:
            f.write("\n".join(head(len(old), len(new))) + "\n")
            w = csv.DictWriter(f, fieldnames=COLS, lineterminator="\n")
            w.writeheader()
            w.writerows(rows)
        print(f"wrote {OUT}: {len(rows)} rows")
    if a.summary or a.write:
        print("\n".join(base.summary(read_record())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
