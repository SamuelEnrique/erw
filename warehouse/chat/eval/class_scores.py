#!/usr/bin/env python3
"""Session 6101 (chain 280): a set's answers scored in four classes, from the stored runs alone, with no model.

Energy Research Warehouse (ERW). The owner's four classes for the chat's evaluation (the chain's prompt of 14 November
2026), read from the runs eval_site.py stored and the grades it wrote:

  correct            the key holds a figure (or, for a window held in part, the answer gave the figure of what is held
                     and said so), and the answer is graded right
  correctly refused  the key is a refusal (a hold, the pause, a table not in the live set, nothing in the warehouse, a
                     missing day; or a window held in part that the answer refused) and the answer is graded right
  unsupported number the answer the reader got holds a number that today's number check finds in no tool result, in
                     the question or in a tool argument (replay.py's check, the loop's own, run again on the record),
                     or a figure in a unit no result gave it in; or the loop gave its fixed refusal because two drafts
                     in a row held such a number (the reader then gets no figure, and no answer either). Counted
                     whatever the grade: the rule the chat stands on is that it never states a number it did not fetch
  wrong              everything else: graded not right, or ended in an error

    python warehouse/chat/eval/class_scores.py --set platform --sessions 6101,6102 [--json]

A question asked more than once in the sessions named counts once, its newest answer standing (the later session's).
A draft sent back once and answered right is counted where its answer falls, and listed under "sent back once".
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CLASSES = ("correct", "correctly refused", "unsupported number", "wrong")
REFUSAL_KINDS = ("hold", "pause", "not_live", "outside", "gap")


def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def key_refuses(q):
    """Whether a question's key is a refusal: its kind (the platform set), or its marks (the sets with no kind)."""
    kind = q.get("kind")
    if kind:
        return kind in REFUSAL_KINDS
    yes = (True, "true", "True")
    return q.get("refuse") in yes or q.get("hold") in yes


def class_of(q, answer, ok, check=None):
    """The class of one stored answer. `q` the question with its key, `answer` its record, `ok` its grade, `check` the
    record through today's checks (replay.check: {"numbers": [...], "units": [...], ...}) or None when it could not be
    made (no answer text: an error)."""
    status = answer.get("status")
    if status == "refused_unverified" or answer.get("refused"):
        return "unsupported number"
    if check and (check.get("numbers") or check.get("units")):
        return "unsupported number"
    if not ok or status == "error" or not answer.get("answer"):
        return "wrong"
    if q.get("kind") == "partial":
        return "correctly refused" if status == "not_in_warehouse" else "correct"
    return "correctly refused" if key_refuses(q) else "correct"


def newest(which, sessions, here=HERE):
    """{id: (session, record, grade row)} over the sessions named, the later session's answer standing."""
    out = {}
    for s in sorted(sessions, key=int):
        run = os.path.join(here, f"eval_s{s}_site_{which}_run.json")
        grades = os.path.join(here, f"eval_s{s}_site_{which}_grades.json")
        if not os.path.exists(run):
            continue
        g = {r["id"]: r for r in read_json(grades)["questions"]} if os.path.exists(grades) else {}
        for a in read_json(run).get("questions") or []:
            out[a["id"]] = (str(s), a, g.get(a["id"]))
    return out


def score(qs, answers, check):
    """The rows and the counts. `qs` the set's questions in order, `answers` newest()'s, `check` a function of a record."""
    rows = []
    for q in qs:
        if q["id"] not in answers:
            continue
        s, a, g = answers[q["id"]]
        c = check(a) if a.get("answer") and a.get("status") in ("answered", "not_in_warehouse") else None
        rows.append({"id": q["id"], "session": s, "kind": q.get("kind"), "sector": q.get("sector"), "status": a.get("status"),
                     "ok": bool(g and g.get("ok")), "class": class_of(q, a, bool(g and g.get("ok")), c),
                     "retried": bool(a.get("retried")), "tool_calls": a.get("tool_calls"), "cost_usd": float(a.get("cost_usd") or 0),
                     "untraced": (c or {}).get("numbers") or [], "units": (c or {}).get("units") or []})
    counts = {c: sum(1 for r in rows if r["class"] == c) for c in CLASSES}
    return rows, counts


def text(which, n_set, rows, counts):
    asked = len(rows)
    lines = [f"| Class | {which}: {asked} asked of {n_set} |", "|---|---:|"]
    lines += [f"| {c} | {counts[c]} |" for c in CLASSES]
    lines += ["", f"- Cost: USD {sum(r['cost_usd'] for r in rows):.4f}. Sent back once by the number check and then let through: "
              f"{sum(1 for r in rows if r['retried'])}."]
    for c in ("unsupported number", "wrong"):
        ids = [f"{r['id']} ({r['status']}" + (f"; in no result: {', '.join(map(str, r['untraced']))}" if r["untraced"] else "") + ")" for r in rows if r["class"] == c]
        lines.append(f"- {c.capitalize()}: {', '.join(ids) if ids else 'none'}.")
    return "\n".join(lines) + "\n"


def main(argv):
    def val(name, default=None):
        return argv[argv.index(name) + 1] if name in argv else default
    which = val("--set", "platform")
    sessions = [s for s in (val("--sessions") or "").split(",") if s]
    if not sessions:
        raise SystemExit("--sessions <N,N,...> is required")
    sys.path.insert(0, HERE)
    import eval_s1113 as E   # the sets and their questions
    import replay            # today's checks on a stored record
    qs = E.questions(E.SETS[which]["questions"])
    rows, counts = score(qs, newest(which, sessions), replay.check)
    if "--json" in argv:
        print(json.dumps({"set": which, "sessions": sessions, "in_set": len(qs), "asked": len(rows), "counts": counts, "rows": rows}, indent=1))
    else:
        print(text(which, len(qs), rows, counts), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
