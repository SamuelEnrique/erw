#!/usr/bin/env python3
"""Session 1301 (chain 093): every stored answer replayed through today's checks, with no model.

Energy Research Warehouse (ERW). Each answer of a stored run that carries its tool record (the runs of sessions 267,
302, 1113, 1114 and 1149's asking again; session 320's first run has none) and that the loop let through (answered, or
not in the warehouse) is run again through the checks of warehouse/chat/ask.py as they now stand: the number check
(`unverified`, with the name check inside it), the unit check (`unit_mismatches`) and the citations (a table cited and
never read; an answer that cites nothing). The sources are what the loop gave the check when the answer was written:
the question, the day's line, and every tool call's input and result. An answer the checks would now send back is
listed, with its grade, so a change to a check that would send back a right answer is seen before it lands.

    python warehouse/chat/eval/replay.py            writes docs/reviews/ask-replay.md
    python warehouse/chat/eval/replay.py --check    exit 1 when the file on disk is not what the runs give, or a right
                                                    answer would now be sent back
No network, no model.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.dirname(HERE))
import ask  # noqa: E402

OUT = os.path.join(ROOT, "docs", "reviews", "ask-replay.md")
# each run that carries a tool record, with the file of its grades and how a grade says right (session 1315: from
# runs.json, the one list of the stored runs)
with open(os.path.join(HERE, "runs.json"), encoding="utf-8") as _f:
    RUN_LIST = json.load(_f)["runs"]
RUNS = [(e["file"], (e["grades"], e["right"]) if e["grades"] else None, e["label"]) for e in RUN_LIST if e["replay"]]


def load(name):
    with open(os.path.join(HERE, name), encoding="utf-8") as f:
        return json.load(f)


def trace_of(q):
    for k in ("trace", "tool_calls"):
        t = q.get(k)
        if isinstance(t, list) and t and isinstance(t[0], dict) and "out" in t[0]:
            return t
    return None


def right_of(q, grades, key):
    if grades is not None:
        g = grades.get(q["id"])
        return None if g is None else bool(g.get(key))
    if "right" in q:
        return bool(q["right"])
    g = q.get("grade")
    return bool(g.get("ok")) if isinstance(g, dict) and "ok" in g else None


def tables_read(trace):
    read = set()
    for t in trace:
        if t.get("isError") or t.get("is_error"):
            continue
        inp, out = t.get("input") or {}, t.get("out") or {}
        for a in (inp, inp.get("a"), inp.get("b")):
            if isinstance(a, dict) and isinstance(a.get("table"), str):
                read.add(a["table"])
        if isinstance(out, dict):
            if isinstance(out.get("table"), str):
                read.add(out["table"])
            for r in out.get("tables") or []:
                if isinstance(r, dict) and isinstance(r.get("table"), str):
                    read.add(r["table"])
    return read


def check(q):
    """One stored answer through today's checks, its own tool record as the sources."""
    trace = trace_of(q) or []
    today = (q.get("asked_at_utc") or "")[:10]
    sources = [q.get("question") or "", f"Today is {today} (UTC)."] + [json.dumps(t.get("out"), default=str) for t in trace] \
        + [json.dumps(t.get("input"), default=str) for t in trace]
    cited = [c.get("table") for c in q.get("citations") or [] if isinstance(c, dict)]
    read = tables_read(trace)
    return {"numbers": ask.unverified(q["answer"], sources), "units": ask.unit_mismatches(q["answer"], sources),
            "uncited": [t for t in cited if t not in read and not str(t).startswith(("docs/", "site/"))],
            "no_cite": not q.get("not_in_warehouse") and not cited}


def replay():
    rows = []
    for name, graded, label in RUNS:
        grades = None
        if graded:
            grades = {g["id"]: g for g in load(graded[0])["questions"]}
        for q in load(name)["questions"]:
            if not trace_of(q) or not q.get("answer") or q.get("status") not in ("answered", "not_in_warehouse"):
                continue
            rows.append({"run": label, "id": q["id"], "status": q["status"], "right": right_of(q, grades, graded[1] if graded else None), **check(q)})
    return rows


def sent_back(r):
    return bool(r["numbers"] or r["units"] or r["uncited"] or r["no_cite"])


def text(rows):
    back = [r for r in rows if sent_back(r)]
    by_run = {}
    for r in rows:
        by_run.setdefault(r["run"], []).append(r)
    lines = ["# Ask's stored answers through today's checks", "",
             "Energy Research Warehouse (ERW). Written by `python warehouse/chat/eval/replay.py` (session 1301) from the stored runs of `warehouse/chat/eval/` alone, with no model: every answer the loop let through, with its tool record, run again through the number check, the unit check and the citations of `warehouse/chat/ask.py` as they now stand. A test holds this file to what the runs give and holds that no answer graded right would now be sent back.", "",
             "| Run | Answers let through | Graded right | Would now be sent back | Of them graded right |", "|---|---|---|---|---|"]
    for run, rs in by_run.items():
        b = [r for r in rs if sent_back(r)]
        lines.append(f"| {run} | {len(rs)} | {sum(1 for r in rs if r['right'])} | {len(b)} | {sum(1 for r in b if r['right'])} |")
    lines += ["", f"In all: {len(rows)} answers, {len(back)} would now be sent back."]
    if back:
        lines += ["", "| Run | Id | Graded | Why |", "|---|---|---|---|"]
        for r in back:
            why = "; ".join([f"figures in no result: {', '.join(r['numbers'])}" if r["numbers"] else "",
                             f"units: {', '.join(r['units'])}" if r["units"] else "",
                             f"cited, not read: {', '.join(r['uncited'])}" if r["uncited"] else "",
                             "cites nothing" if r["no_cite"] else ""]).strip("; ").replace("; ; ", "; ")
            lines.append(f"| {r['run']} | {r['id']} | {'right' if r['right'] else 'wrong' if r['right'] is False else 'not graded'} | {why} |")
    return "\n".join(lines) + "\n"


def main(argv):
    rows = replay()
    body = text(rows)
    if "--check" in argv:
        with open(OUT, encoding="utf-8") as f:
            same = f.read().replace("\r\n", "\n") == body
        return 0 if same and not any(sent_back(r) and r["right"] for r in rows) else 1
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(body)
    print(body)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
