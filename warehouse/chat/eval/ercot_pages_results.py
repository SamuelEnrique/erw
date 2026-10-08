#!/usr/bin/env python3
"""Energy Research Warehouse (ERW), session 153: the record of the 120 test questions of Ask ERCOT, asked on 8 October
2026 after the tool learned to read what stands behind four pages. No model and no request: it reads the runner's own
lines (site/scripts/eval-ask-speed.mjs writes one a question) and writes one row a question.

    python warehouse/chat/eval/ercot_pages_results.py --runs C:/.../runs/session153 --write
    python warehouse/chat/eval/ercot_pages_results.py --summary

The runs: `new20` (the 20 questions of the four pages, warehouse/chat/eval_ercot_pages.json, asked first), `old100`
(the 100 of session 137, warehouse/chat/eval_ercot_panel.json, one of each kind in turn) and `reask_p14` (the one new
question that failed, asked once more with the money left under the stop; its first answer stays the record and the
second is a row of its own, set "reask"). The tool was as the code stands: both of session 148's switches off, the
reserve tables and the four pages offered. Each question was asked once, on a local server; the judge is the rule in
code (site/scripts/eval-judge.mjs), which for the 20 also checks the expected number, the source and the chart's row.
"""
import argparse
import csv
import json
import os
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(ROOT, "warehouse", "chat", "eval_ercot_pages_results_153.csv")
COLS = ["set", "id", "kind", "page", "question", "pass", "why", "status", "form", "usd", "seconds_first_sign", "seconds_words", "seconds", "words_first", "withdrawn", "retried",
        "tool_calls", "model_calls", "planning_ms", "fetching_ms", "drawing_ms", "writing_ms", "other_ms", "total_ms", "citations", "series_rows", "tools"]
HEAD = [
    "# Energy Research Warehouse (ERW), session 153: Ask ERCOT on 120 test questions, 8 October 2026 (UTC), one row a question asked.",
    "# set new: the 20 questions of four pages (warehouse/chat/eval_ercot_pages.json). set old: the 100 of session 137 (warehouse/chat/eval_ercot_panel.json). set reask: p14 asked a second time; its first answer is the row of set new.",
    "# The tool as the code stands: both of session 148's switches off; the reserve tables by day and month and the four pages' sources offered. A local server; production was not asked.",
    "# pass: the rule of the question's kind (site/scripts/eval-judge.mjs), and for set new also the expected number, the source and the chart's row. usd: the server's own model calls for the question.",
    "# seconds_words: from the question to the answer's words, at the reader's end. Written by warehouse/chat/eval/ercot_pages_results.py from the runner's lines; do not edit by hand.",
]


def lines(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def row(kind_of_set, r):
    s = r.get("stages_ms") or {}
    tools = []
    for step in r.get("steps") or []:
        if step.get("what") == "tools":
            for c in step.get("calls") or []:
                args = c.get("args") or {}
                tools.append(f"{c.get('tool')}:{c.get('table') or args.get('table') or args.get('view') or args.get('page') or ''}")
    return {"set": kind_of_set, "id": r["id"], "kind": r["kind"], "page": r.get("page") or "", "question": r["q"], "pass": int(bool(r["pass"])), "why": "; ".join(r.get("why") or []), "status": r.get("status") or "",
            "form": r.get("form") or "", "usd": f"{r['cost_usd']:.6f}", "seconds_first_sign": r.get("seconds_first_sign"), "seconds_words": r.get("seconds_words"), "seconds": r.get("seconds"),
            "words_first": int(bool(r.get("words_first"))), "withdrawn": r.get("withdrawn") or 0, "retried": int(bool(r.get("retried"))), "tool_calls": r.get("tool_calls"), "model_calls": r.get("requests"),
            "planning_ms": s.get("planning"), "fetching_ms": s.get("fetching"), "drawing_ms": s.get("drawing"), "writing_ms": s.get("writing"), "other_ms": s.get("other"), "total_ms": s.get("total"),
            "citations": " ".join(r.get("citations") or []), "series_rows": " ".join(str(x.get("rows")) for x in r.get("series") or []), "tools": " ".join(tools)}


def read_record():
    with open(OUT, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(l for l in f if not l.startswith("#")))


def summary(rows):
    out = []
    num = lambda v: float(v) if v not in ("", None) else None
    for name in ("new", "old"):
        g = [r for r in rows if r["set"] == name]
        if not g:
            continue
        out.append(f"{name}: {sum(int(r['pass']) for r in g)} of {len(g)} pass; USD {sum(float(r['usd']) for r in g):.4f}, {sum(float(r['usd']) for r in g) / len(g):.4f} a question; "
                   f"seconds to the words, median {st.median([num(r['seconds_words']) for r in g if num(r['seconds_words']) is not None]):.2f}")
        for key in ("kind", "page"):
            for k in sorted({r[key] for r in g}):
                if not k:
                    continue
                h = [r for r in g if r[key] == k]
                out.append(f"  {key} {k}: {sum(int(r['pass']) for r in h)} of {len(h)}; USD {sum(float(r['usd']) for r in h) / len(h):.4f} a question; words {st.median([num(r['seconds_words']) for r in h if num(r['seconds_words']) is not None]):.2f} s")
    out.append("failed: " + (", ".join(f"{r['id']} ({r['why']})" for r in rows if not int(r["pass"])) or "none"))
    out.append(f"all rows: USD {sum(float(r['usd']) for r in rows):.4f} in {len(rows)} askings")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", help="the folder that holds new20.jsonl, old100.jsonl and reask_p14.jsonl")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--summary", action="store_true")
    a = ap.parse_args()
    if a.write:
        if not a.runs:
            print("--write needs --runs")
            return 2
        rows = [row("new", r) for r in lines(os.path.join(a.runs, "new20.jsonl"))] + [row("old", r) for r in lines(os.path.join(a.runs, "old100.jsonl"))] + [row("reask", r) for r in lines(os.path.join(a.runs, "reask_p14.jsonl"))]
        if not rows:
            print(f"no answers under {a.runs}: nothing is written")
            return 1
        with open(OUT, "w", encoding="utf-8", newline="") as f:
            f.write("\n".join(HEAD) + "\n")
            w = csv.DictWriter(f, fieldnames=COLS, lineterminator="\n")
            w.writeheader()
            w.writerows(rows)
        print(f"wrote {OUT}: {len(rows)} rows")
    if a.summary or a.write:
        print("\n".join(summary(read_record())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
