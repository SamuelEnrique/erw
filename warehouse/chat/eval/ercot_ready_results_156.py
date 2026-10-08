#!/usr/bin/env python3
"""Energy Research Warehouse (ERW), session 156: the record of the 120 test questions of Ask ERCOT, asked on 8 October
2026 on the tool brought to ready. No model and no request: it reads the runner's own lines
(site/scripts/eval-ask-speed.mjs writes one a question) and writes one row a question asked.

    python warehouse/chat/eval/ercot_ready_results_156.py --runs C:/.../runs/session156 --write
    python warehouse/chat/eval/ercot_ready_results_156.py --summary

The runs: `new20` (the 20 questions of the four pages, warehouse/chat/eval_ercot_pages.json, asked first), `old100`
(the 100 of session 137, warehouse/chat/eval_ercot_panel.json, one of each kind in turn) and `reask` (each question
that failed, asked once more with the money left under the stop; its first answer stays the record and the second is a
row of its own, set "reask"). The tool was as the code stands after phase 1 of the session: both of session 148's
switches on by default, the query's three forms, the briefing's rule of source precedence and its sentence on Texas's
curtailment share, the closing words of a refusal. Each question was asked once, on a local server; production was not
asked. The judge is the rule in code (site/scripts/eval-judge.mjs): since this session it also asks the thirteen
refusals about another grid for the closing words, so it is stricter on those than in sessions 148 and 153.

before_148 and before_153 set each question's answer beside those sessions' own records
(warehouse/chat/eval_ercot_speed_results_148.csv, its "after" columns: every change on;
warehouse/chat/eval_ercot_pages_results_153.csv: the switches off): pass, seconds to the words and model calls.
"""
import argparse
import csv
import json
import os
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(ROOT, "warehouse", "chat", "eval_ercot_ready_results_156.csv")
R148 = os.path.join(ROOT, "warehouse", "chat", "eval_ercot_speed_results_148.csv")
R153 = os.path.join(ROOT, "warehouse", "chat", "eval_ercot_pages_results_153.csv")
COLS = ["set", "id", "kind", "page", "question", "pass", "why", "status", "form", "usd", "seconds_first_sign", "seconds_words", "seconds", "words_first", "withdrawn", "retried",
        "tool_calls", "model_calls", "planned_by", "efforts", "planning_ms", "fetching_ms", "drawing_ms", "writing_ms", "other_ms", "total_ms", "citations", "series_rows", "tools",
        "s148_pass", "s148_seconds_words", "s148_model_calls", "s148_usd", "s153_pass", "s153_seconds_words", "s153_model_calls", "s153_usd"]
HEAD = [
    "# Energy Research Warehouse (ERW), session 156: Ask ERCOT on 120 test questions, 8 October 2026 (UTC), one row a question asked.",
    "# set new: the 20 questions of four pages (warehouse/chat/eval_ercot_pages.json). set old: the 100 of session 137 (warehouse/chat/eval_ercot_panel.json). set reask: a question that failed, asked a second time; its first answer is the row of set new or old.",
    "# The tool as the code stands after the session's phase 1: the plan made by rule and the lower effort of the reading turn on by default; the query's three forms; the rule of source precedence; the closing words of a refusal. A local server; production was not asked.",
    "# pass: the rule of the question's kind (site/scripts/eval-judge.mjs), for set new also the expected number, the source and the chart's row, and since this session, for the thirteen refusals about another grid, the closing words. usd: the server's own model calls for the question.",
    "# seconds_words: from the question to the answer's words, at the reader's end. planned_by rule: the read was written by code. s148_ and s153_: the same question in those sessions' records (148: every change on; 153: the switches off); empty: not asked there.",
    "# Written by warehouse/chat/eval/ercot_ready_results_156.py from the runner's lines; do not edit by hand.",
]


def lines(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def earlier():
    """Each question's row in the records of sessions 148 (after) and 153 (first asking), by id."""
    b148, b153 = {}, {}
    if os.path.exists(R148):
        with open(R148, encoding="utf-8", newline="") as f:
            for r in csv.DictReader(l for l in f if not l.startswith("#")):
                b148[r["id"]] = {"pass": r["after_pass"], "words": r["after_seconds_words"], "calls": r["after_model_calls"], "usd": r["after_usd"]}
    if os.path.exists(R153):
        with open(R153, encoding="utf-8", newline="") as f:
            for r in csv.DictReader(l for l in f if not l.startswith("#")):
                if r["set"] in ("new", "old"):
                    b153[r["id"]] = {"pass": r["pass"], "words": r["seconds_words"], "calls": r["model_calls"], "usd": r["usd"]}
    return b148, b153


def row(kind_of_set, r, b148, b153):
    s = r.get("stages_ms") or {}
    tools = []
    for step in r.get("steps") or []:
        if step.get("what") == "tools":
            for c in step.get("calls") or []:
                args = c.get("args") or {}
                form = "+hour_of_day" if args.get("group_by") == "hour_of_day" else ""
                form += "+date_column" if args.get("date_column") else ""
                form += "+newest" if args.get("day") == "newest" else ""
                tools.append(f"{c.get('tool')}:{c.get('table') or args.get('table') or args.get('view') or args.get('page') or ''}{form}")
    a, b = b148.get(r["id"], {}), b153.get(r["id"], {})
    return {"set": kind_of_set, "id": r["id"], "kind": r["kind"], "page": r.get("page") or "", "question": r["q"], "pass": int(bool(r["pass"])), "why": "; ".join(r.get("why") or []), "status": r.get("status") or "",
            "form": r.get("form") or "", "usd": f"{r['cost_usd']:.6f}", "seconds_first_sign": r.get("seconds_first_sign"), "seconds_words": r.get("seconds_words"), "seconds": r.get("seconds"),
            "words_first": int(bool(r.get("words_first"))), "withdrawn": r.get("withdrawn") or 0, "retried": int(bool(r.get("retried"))), "tool_calls": r.get("tool_calls"), "model_calls": r.get("requests"),
            "planned_by": r.get("planned_by") or "", "efforts": " ".join(r.get("efforts") or []),
            "planning_ms": s.get("planning"), "fetching_ms": s.get("fetching"), "drawing_ms": s.get("drawing"), "writing_ms": s.get("writing"), "other_ms": s.get("other"), "total_ms": s.get("total"),
            "citations": " ".join(r.get("citations") or []), "series_rows": " ".join(str(x.get("rows")) for x in r.get("series") or []), "tools": " ".join(tools),
            "s148_pass": a.get("pass", ""), "s148_seconds_words": a.get("words", ""), "s148_model_calls": a.get("calls", ""), "s148_usd": a.get("usd", ""),
            "s153_pass": b.get("pass", ""), "s153_seconds_words": b.get("words", ""), "s153_model_calls": b.get("calls", ""), "s153_usd": b.get("usd", "")}


def read_record():
    with open(OUT, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(l for l in f if not l.startswith("#")))


def num(v):
    return float(v) if v not in ("", None) else None


def med(vals):
    vals = [v for v in vals if v is not None]
    return st.median(vals) if vals else None


def fmt(v, d=2):
    return "none" if v is None else f"{v:.{d}f}"


def summary(rows):
    out = []
    for name in ("new", "old"):
        g = [r for r in rows if r["set"] == name]
        if not g:
            continue
        out.append(f"{name}: {sum(int(r['pass']) for r in g)} of {len(g)} pass; USD {sum(float(r['usd']) for r in g):.4f}, {sum(float(r['usd']) for r in g) / len(g):.4f} a question; "
                   f"seconds to the words, median {fmt(med([num(r['seconds_words']) for r in g]))}")
        for key in ("kind", "page"):
            for k in sorted({r[key] for r in g}):
                if not k:
                    continue
                h = [r for r in g if r[key] == k]
                w = [num(r["seconds_words"]) for r in h]
                out.append(f"  {key} {k}: {sum(int(r['pass']) for r in h)} of {len(h)}; USD {sum(float(r['usd']) for r in h) / len(h):.4f} a question; words {fmt(med(w))} s; "
                           f"under 5 s {sum(1 for x in w if x is not None and x < 5)}, under 2 s {sum(1 for x in w if x is not None and x < 2)}")
        numbers = [r for r in g if r["kind"] in ("chart", "sentence")]
        w = [num(r["seconds_words"]) for r in numbers]
        out.append(f"  questions about numbers: {len(numbers)}; words {fmt(med(w))} s; under 5 s {sum(1 for x in w if x is not None and x < 5)} of {len(numbers)}")
        ruled = [r for r in g if r["planned_by"] == "rule"]
        if ruled:
            out.append(f"  planned by rule: {len(ruled)}, of them pass {sum(int(r['pass']) for r in ruled)}; words {fmt(med([num(r['seconds_words']) for r in ruled]))} s")
    out.append("failed: " + (", ".join(f"{r['set']} {r['id']} ({r['why']})" for r in rows if not int(r["pass"])) or "none"))
    out.append(f"all rows: USD {sum(float(r['usd']) for r in rows):.4f} in {len(rows)} askings")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", help="the folder that holds new20.jsonl, old100.jsonl and reask.jsonl")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--summary", action="store_true")
    a = ap.parse_args()
    if a.write:
        if not a.runs:
            print("--write needs --runs")
            return 2
        b148, b153 = earlier()
        rows = ([row("new", r, b148, b153) for r in lines(os.path.join(a.runs, "new20.jsonl"))] + [row("old", r, b148, b153) for r in lines(os.path.join(a.runs, "old100.jsonl"))]
                + [row("reask", r, b148, b153) for r in lines(os.path.join(a.runs, "reask.jsonl"))])
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
