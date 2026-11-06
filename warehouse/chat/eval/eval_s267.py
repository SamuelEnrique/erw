#!/usr/bin/env python3
"""Grade an answer of Ask against a question of questions_s267.yaml (session 267). No model, no network.

Energy Research Warehouse (ERW). The grades, as the brief of session 267 names them:
  number   every expected number appears in the answer, within the tolerance, or written at a coarser precision
           (139.6 for 139.6044); thousands separators are read
  text     every required word appears in the answer (a year, a month, "paused")
  table    a cited table is one of the acceptable tables
  cited    every citation names a source report and a data version (an answered question only)
  refusal  "not in the warehouse" exactly when the question expects it
A question is right when every grade that applies passes.

    python warehouse/chat/eval/eval_s267.py      # replays eval_s267_fixtures.json and prints the grades
"""

import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
FIXTURES = os.path.join(HERE, "eval_s267_fixtures.json")
QUESTIONS = os.path.join(HERE, "questions_s267.yaml")


def numbers(text):
    """The numbers written in a text, as (value, decimals): "1,361,345.63" is (1361345.63, 2)."""
    out = []
    for m in re.findall(r"-?\d[\d,]*(?:\.\d+)?", text or ""):
        m = m.rstrip(",")
        if not m or m == "-":
            continue
        dec = len(m.split(".")[1]) if "." in m else 0
        try:
            out.append((float(m.replace(",", "")), dec))
        except ValueError:
            continue
    return out


def matches(expected, written, tolerance):
    for v, dec in written:
        if abs(v - expected) <= tolerance:
            return True
        if dec >= 1 and abs(v - round(expected, dec)) < 10 ** -(dec + 3):
            return True
    return False


# Session 2223 (chain 152): the rules a grading may be made under, session 320's open ruling 3 as recommended in
# docs/reviews/ask-board-rulings-2026-10-23.md (item 3). A grading made with none is what it was; the stored gradings of
# 20 to 23 October 2026 were made with none, and eval_s1113.py regrades them so.
#   refusal_no_table    a key that expects a refusal (refuse: true) is graded on refusing and stating no figure, never on
#                       a cited table (d10: PJM's right refusal cited no table, or a table it read, and was graded wrong)
#   table_by_evidence   a key's table is also met when every expected figure is in a tool result of a cited table in the
#                       answer's own record (trace): the table holds the figure, as the record shows (t06, f05, f06, f07
#                       of session 1114's thirty stated the right figure from another table that holds it)
RULES_2223 = ("refusal_no_table", "table_by_evidence")


NOT_FIGURES = {"rows_matched", "n", "n_groups", "rows_in_live_set", "n_tables", "limit", "rows", "months", "days", "hours", "n_hours"}


def figures_in(out):
    """The figures a tool result holds: every numeric leaf of it (not a count of rows or groups, not the filters or the
    arguments echoed back, never a number inside a string such as a date or an id)."""
    found = []

    def walk(x, key=None):
        if isinstance(x, bool) or x is None:
            return
        if isinstance(x, (int, float)):
            if key not in NOT_FIGURES:
                found.append((float(x), 6))
        elif isinstance(x, dict):
            for k, v in x.items():
                if k in ("filters", "input", "where", "provenance"):
                    continue
                walk(v, k)
        elif isinstance(x, list):
            for v in x:
                walk(v, key)

    walk(out)
    return found


def results_of(body, table):
    """The tool results of an answer's record that read `table`: a query's own, and a compare's whole result when one
    side read it (the difference and the ratio are the compare's own figures)."""
    outs = []
    for t in body.get("trace") or []:
        if not isinstance(t, dict) or t.get("is_error") or t.get("isError"):
            continue
        inp, out = t.get("input") or {}, t.get("out")
        if not isinstance(inp, dict) or not isinstance(out, dict):
            continue
        if inp.get("table") == table or out.get("table") == table:
            outs.append(out)
            continue
        for side in ("a", "b"):
            s_in, s_out = inp.get(side), out.get(side)
            if (isinstance(s_in, dict) and s_in.get("table") == table) or (isinstance(s_out, dict) and s_out.get("table") == table):
                outs.append(out)
                break
    return outs


def table_holds(q, body, table):
    """Session 2223: every expected figure of the key is a figure of a tool result that read `table`, in the answer's own
    record (within the key's tolerance, or equal once rounded as the result writes it)."""
    if not q["expected"]:
        return False
    found = []
    for out in results_of(body, table):
        found += figures_in(out)
    return bool(found) and all(matches(e, found, q["tolerance"]) or any(abs(round(e, 2) - v) < 1e-9 for v, _ in found) for e in q["expected"])


def grade(q, body, rules=()):
    ans = body.get("answer") or ""
    cits = body.get("citations") or []
    cited = [c.get("table") for c in cits]
    written = numbers(ans)
    table = bool(set(cited) & set(q["tables"])) if q["tables"] else None
    if q["tables"] and not table and "table_by_evidence" in rules:
        table = any(table_holds(q, body, t) for t in cited if t)
    if q["refuse"] and "refusal_no_table" in rules:
        table = None
    g = {
        "number": all(matches(e, written, q["tolerance"]) for e in q["expected"]) if q["expected"] else None,
        "text": all(t.lower() in ans.lower() for t in q["text"]) if q["text"] else None,
        "table": table,
        "cited": (bool(cits) and all(c.get("source_report") and c.get("data_version") for c in cits)) if not q["refuse"] else None,
    }
    refused = bool(body.get("not_in_warehouse")) or body.get("status") in ("not_in_warehouse", "refused_unverified")
    g["refusal"] = refused == bool(q["refuse"])
    if q["refuse"] and "refusal_no_table" in rules:
        # a refusal states no figure: no number with decimals, and no whole number of 1,000 or more that is not a year
        g["no_figure"] = not any(dec >= 1 or (abs(v) >= 1000 and not 1900 <= v <= 2100) for v, dec in written)
    g["ok"] = all(v for v in g.values() if v is not None)
    return g


def load():
    with open(FIXTURES, encoding="utf-8") as f:
        return json.load(f)["questions"]


if __name__ == "__main__":
    fx = load()
    for q in fx:
        g = grade(q, q)
        print(q["id"], "right" if g["ok"] else "WRONG", q["verdict"], {k: v for k, v in g.items() if k != "ok"})
    print(sum(1 for q in fx if grade(q, q)["ok"]), "of", len(fx), "right")
