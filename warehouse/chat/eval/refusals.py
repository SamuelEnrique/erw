#!/usr/bin/env python3
"""Session 1304 (chain 093): Ask's stored refusals, each classed from its tool record alone.

Energy Research Warehouse (ERW). Every stored answer that is a refusal ("not in the warehouse", or the fixed refusal of
the number check) and carries its tool record (the runs replay.py reads, and session 320's first run, which has none,
counted apart) is put in the first class its record shows:

  pause      a tool answered with MISO's pause (MISO_PAUSED)
  held       a tool answered with a license hold ("license needed", or a held grid's answer)
  limit      the loop used every tool call its day allowed (8 until session 1111 on 23 October 2026, 12 since)
  lacks      the tools were asked only for lists, notes or counts, or every read matched no row: the warehouse does not
             hold the figure, as far as the record shows
  read       rows were read and the answer still refused: a refusal to look at
  checked    the number check's fixed refusal (the draft is not stored)

    python warehouse/chat/eval/refusals.py            writes docs/reviews/ask-refusals.md
    python warehouse/chat/eval/refusals.py --check    exit 1 when the file on disk is not what the runs give
No network, no model.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import replay as R  # noqa: E402

OUT = os.path.join(ROOT, "docs", "reviews", "ask-refusals.md")
EIGHT = {"session 267", "session 302"}   # the runs asked under the limit of 8
REFUSED = ("not_in_warehouse", "refused_unverified")
CLASSES = [("pause", "MISO's pause"), ("held", "a license hold"), ("limit", "the call limit"), ("lacks", "the warehouse lacks the figure"),
           ("read", "rows read, then refused"), ("checked", "the number check's refusal")]


def calls_of(q):
    t = q.get("tool_calls")
    return len(t) if isinstance(t, list) else int(t or 0)


def classify(q, label):
    trace = R.trace_of(q) or []
    outs = [t.get("out") if isinstance(t.get("out"), dict) else {} for t in trace]
    errors = [str(o.get("error") or "") for o in outs]
    if any("MISO is paused" in e for e in errors):
        return "pause"
    if any(o.get("held") for o in outs) or any("license needed" in e for e in errors):
        return "held"
    if q.get("status") == "refused_unverified":
        return "checked"
    if calls_of(q) >= (8 if label in EIGHT else 12):
        return "limit"
    reads = [(t, o) for t, o in zip(trace, outs) if t.get("tool") in ("query", "compare") and not t.get("isError")]
    figures = [o for t, o in reads if (t.get("input") or {}).get("aggregation") != "count" and (o.get("rows_matched") or 0) > 0]
    return "read" if figures else "lacks"


def refusals():
    rows = []
    for name, graded, label in R.RUNS:
        grades = {g["id"]: g for g in R.load(graded[0])["questions"]} if graded else None
        for q in R.load(name)["questions"]:
            if q.get("status") not in REFUSED or not R.trace_of(q) and calls_of(q):
                continue
            rows.append({"run": label, "id": q["id"], "status": q["status"], "calls": calls_of(q), "class": classify(q, label),
                         "right": R.right_of(q, grades, graded[1] if graded else None)})
    return rows


def text(rows):
    lines = ["# Ask's refusals, classed from their tool records", "",
             "Energy Research Warehouse (ERW). Written by `python warehouse/chat/eval/refusals.py` (session 1304) from the stored runs of `warehouse/chat/eval/` alone, with no model; a test holds this file to what they give. Each refusal is put in the first class its record shows: MISO's pause, a license hold, the call limit of its day (8 until session 1111, then 12), the warehouse lacking the figure (only lists, notes or counts were asked, or no read matched a row), or rows read and still refused. Session 320's first run has no tool record and is not here.", "",
             "| Class | Refusals | Graded right |", "|---|---|---|"]
    for key, words in CLASSES:
        rs = [r for r in rows if r["class"] == key]
        if rs:
            lines.append(f"| {words} | {len(rs)} | {sum(1 for r in rs if r['right'])} of {sum(1 for r in rs if r['right'] is not None)} graded |")
    lines += ["", f"In all: {len(rows)} refusals.", "", "| Run | Id | Calls | Class | Graded |", "|---|---|---|---|---|"]
    words = dict(CLASSES)
    for r in rows:
        lines.append(f"| {r['run']} | {r['id']} | {r['calls']} | {words[r['class']]} | {'right' if r['right'] else 'wrong' if r['right'] is False else 'not graded'} |")
    return "\n".join(lines) + "\n"


def main(argv):
    body = text(refusals())
    if "--check" in argv:
        with open(OUT, encoding="utf-8") as f:
            return 0 if f.read().replace("\r\n", "\n") == body else 1
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(body)
    print(body)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
