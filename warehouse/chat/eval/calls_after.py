#!/usr/bin/env python3
"""Session 5266 (chain 256): what the calls made after the figure was in hand are, by class.

Energy Research Warehouse (ERW). The platform set's scores (platform_scores.py, "Calls past the figure") count, for a
figure question answered right, the tool calls made after the first result that held the key's figure: 37 of 80 made
three or more on 13 November 2026. This says what those calls were, from the stored runs alone (no model, no network):

    python warehouse/chat/eval/calls_after.py [--json] [--ids pw09,tx01] [--sessions 5266,5267]

Each recorded call after the figure is put in one class, the first it fits:

  refused         the tool answered with an error (a held table, a table not in the live set, a bad argument)
  list            list_tables
  describe        describe_table
  count_window    a query of the figure's table with aggregation "count" (the figure's own call was not a count): the rows
                  of the window counted, which is how the chat finds out whether a day, a week or a month is whole
  regroup         a query of the figure's table with a group_by the figure's call did not have (the same rows by day, by
                  hour, by entity): the window looked at step by step
  same_table      another query of the figure's table (other filters, another aggregation)
  other_table     a query of another table
  compare         compare
  other           any other tool (board_rank, grid_notes, a page tool)

and the calls the loop counted and did not make (a repeated call, answered with a note and not recorded: session 2222)
are `not_made`. --sessions limits the answers read to those sessions' runs (a question's newest answer among them),
so a later asking can be set beside an earlier one.
"""
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SET = "platform"
CLASSES = ("count_window", "regroup", "same_table", "other_table", "compare", "describe", "list", "refused", "other", "not_made")


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def table_of(call):
    a = call.get("input") if isinstance(call.get("input"), dict) else {}
    return a.get("table") if isinstance(a.get("table"), str) else None


def class_of(call, figure_call):
    """The class of one recorded call made after `figure_call`, the call whose result first held the figure."""
    if call.get("isError") or call.get("is_error"):
        return "refused"
    tool = call.get("tool")
    if tool == "list_tables":
        return "list"
    if tool == "describe_table":
        return "describe"
    if tool == "compare":
        return "compare"
    if tool != "query":
        return "other"
    a = call.get("input") if isinstance(call.get("input"), dict) else {}
    f = figure_call.get("input") if isinstance(figure_call.get("input"), dict) else {}
    if table_of(call) != table_of(figure_call) or figure_call.get("tool") != "query":
        return "other_table"
    if a.get("aggregation") == "count" and f.get("aggregation") != "count":
        return "count_window"
    if a.get("group_by") and a.get("group_by") != f.get("group_by"):
        return "regroup"
    return "same_table"


def after(q, rec, in_hand):
    """{"at": the call the figure was in hand at, "calls": the loop's count, "after": [class, ...]} for a figure question
    answered with the figure in a result, else None. `in_hand` is platform_scores.py's reading of the trace."""
    n = in_hand(q, rec)
    if n is None:
        return None
    trace = rec.get("trace") or []
    later = [class_of(t, trace[n - 1]) for t in trace[n:] if isinstance(t, dict)]
    not_made = max(0, int(rec.get("tool_calls") or 0) - len(trace))
    return {"at": n, "calls": int(rec.get("tool_calls") or 0), "after": later + ["not_made"] * not_made}


def measure(qs, runs, in_hand, ids=None, sessions=None):
    """The measure over the figure questions answered: per question, and the totals by class."""
    by = {q["id"]: q for q in qs}
    newest = {}
    for s, run, *_ in runs:
        if sessions and str(s) not in sessions:
            continue
        for rec in run:
            newest[rec["id"]] = (s, rec)
    rows = []
    for i, (s, rec) in newest.items():
        q = by.get(i)
        if not q or q.get("kind") != "figure" or rec.get("status") != "answered" or (ids and i not in ids):
            continue
        m = after(q, rec, in_hand)
        if m is not None:
            rows.append({"id": i, "session": str(s), "cost_usd": float(rec.get("cost_usd") or 0), **m})
    rows.sort(key=lambda r: [q["id"] for q in qs].index(r["id"]))
    totals = {c: sum(r["after"].count(c) for r in rows) for c in CLASSES}
    return {"questions": len(rows), "calls": sum(r["calls"] for r in rows), "calls_after": sum(len(r["after"]) for r in rows),
            "with_three_or_more_after": sum(1 for r in rows if len(r["after"]) >= 3),
            "cost_usd": round(sum(r["cost_usd"] for r in rows), 4), "by_class": totals,
            "questions_with": {c: sum(1 for r in rows if c in r["after"]) for c in CLASSES}, "rows": rows}


def lines(m):
    out = [f"figure questions answered with the figure in a result: {m['questions']}; calls {m['calls']}, of them after the figure {m['calls_after']}; "
           f"with three or more after: {m['with_three_or_more_after']}; cost USD {m['cost_usd']:.4f}", "",
           "| Class | Calls after the figure | Questions with one |", "|---|---:|---:|"]
    out += [f"| {c} | {m['by_class'][c]} | {m['questions_with'][c]} |" for c in CLASSES if m["by_class"][c]]
    return out


def main(argv):
    def val(name):
        return argv[argv.index(name) + 1] if name in argv else None
    S = module("eval_site_for_calls_after", os.path.join(HERE, "eval_site.py"))
    E = module("eval_s1113_for_calls_after", os.path.join(HERE, "eval_s1113.py"))
    P = module("platform_scores_for_calls_after", os.path.join(HERE, "platform_scores.py"))
    qs, runs = P.load(S, E)
    ids = set(val("--ids").split(",")) if val("--ids") else None
    sessions = set(val("--sessions").split(",")) if val("--sessions") else None
    m = measure(qs, runs, lambda q, rec: P.in_hand(q, rec, E.G), ids, sessions)
    if "--json" in argv:
        print(json.dumps(m, indent=1))
    else:
        print("\n".join(lines(m)))
        if "--rows" in argv:
            for r in m["rows"]:
                print(f"{r['id']} (session {r['session']}): in hand at call {r['at']} of {r['calls']}; after: {', '.join(r['after']) or 'none'}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
