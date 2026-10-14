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


def grade(q, body):
    ans = body.get("answer") or ""
    cits = body.get("citations") or []
    cited = [c.get("table") for c in cits]
    written = numbers(ans)
    g = {
        "number": all(matches(e, written, q["tolerance"]) for e in q["expected"]) if q["expected"] else None,
        "text": all(t.lower() in ans.lower() for t in q["text"]) if q["text"] else None,
        "table": bool(set(cited) & set(q["tables"])) if q["tables"] else None,
        "cited": (bool(cits) and all(c.get("source_report") and c.get("data_version") for c in cits)) if not q["refuse"] else None,
    }
    refused = bool(body.get("not_in_warehouse")) or body.get("status") in ("not_in_warehouse", "refused_unverified")
    g["refusal"] = refused == bool(q["refuse"])
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
