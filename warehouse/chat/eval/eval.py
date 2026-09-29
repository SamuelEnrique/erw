#!/usr/bin/env python3
"""Run the evaluation set through warehouse/chat/ask.py and score it (session 12, Task 3).

Energy Research Warehouse (ERW).

    python warehouse/chat/eval/eval.py                 # every question
    python warehouse/chat/eval/eval.py --only q01 q29  # some

For each question in questions.yaml (built by expected.py), asks the model with the
set's fixed date, then scores:
  number    every expected number appears in the answer within its tolerance
  text      every required word appears in the answer (for example the winning ISO)
  citation  at least one cited table is one of the acceptable tables, every citation
            names a source report and a data version, and for an internal table the
            answer says it is internal
  refusal   "not in the warehouse" exactly when the question expects it
A question is correct when all that apply pass. Writes every record to
results/<run>.jsonl and a summary to results/<run>.md, and prints accuracy, cost and
mean tool calls.
"""

import argparse
import datetime as dt
import json
import os
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import ask  # noqa: E402


def accepted(tables):
    """Session 30: the acceptable tables, and the consolidated table each old name moved into in session 29
    (warehouse/metadata/table_migrations.csv), so an answer citing iso_dam_hub_prices where the set names
    ercot_dam_hub_prices is not marked wrong for the rename."""
    import erw
    moved = erw.migrations()
    return set(tables) | {moved[t][0] for t in tables if t in moved}


def expected(q):
    """Session 33: the expected numbers. A question on a table that keeps growing (q27: stories dated one day in
    news_index, which later runs add to as they score more stories of that day) names the count it asks for in
    count_on_day, {table, column, day}; the count is taken from the table when the eval scores, the day fixed. Every
    other question keeps the numbers expected.py wrote."""
    c = q.get("count_on_day")
    if not c:
        return q["expected"]
    import erw
    import pandas as pd
    df = erw.fetch(c["table"])
    t = pd.to_datetime(df[c["column"]], utc=True)
    day = pd.Timestamp(c["day"], tz="UTC")
    return [float(((t >= day) & (t < day + pd.Timedelta(days=1))).sum())]


def score(q, rec):
    got = [v for v, _ in ask.numbers(rec["answer"])]
    s = {}
    status = rec.get("status")
    if q["refuse"]:
        s["refusal"] = status == "not_in_warehouse"
    else:
        s["refusal"] = status == "answered"
        s["number"] = all(any(abs(abs(g) - abs(e)) <= q["tolerance"] for g in got) for e in expected(q))
        low = rec["answer"].lower()
        s["text"] = all(t.lower() in low for t in q["text"])
        cites = rec.get("citations") or []
        ok_table = any(c["table"] in accepted(q["tables"]) for c in cites)
        complete = bool(cites) and all(c.get("source_report") and c.get("data_version") for c in cites)
        s["citation"] = ok_table and complete and (not q["internal"] or "internal" in low)
    s["correct"] = all(s.values())
    return s


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW question-answering evaluation")
    ap.add_argument("--only", nargs="*", help="question ids to run")
    ap.add_argument("--questions", default=os.path.join(HERE, "questions.yaml"),
                    help="the question set to run (default questions.yaml)")
    args = ap.parse_args(argv)
    spec = yaml.safe_load(open(args.questions, encoding="utf-8"))
    qs = [q for q in spec["questions"] if not args.only or q["id"] in args.only]
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    jl = os.path.join(HERE, "results", f"{run_id}.jsonl")
    asker = ask.Asker()
    rows = []
    with open(jl, "w", encoding="utf-8", newline="\n") as f:
        for q in qs:
            try:
                rec = asker.ask(q["question"], today=spec["today"])
            except Exception as exc:  # a failed question is scored wrong and recorded, never skipped
                rec = {"question": q["question"], "answer": "", "citations": [], "status": "error",
                       "error": f"{type(exc).__name__}: {exc}", "tool_calls": 0, "cost_usd": 0.0,
                       "usage": {}, "retried": False}
            s = score(q, rec)
            rec.update({"id": q["id"], "score": s, "expected": q["expected"], "expected_text": q["text"],
                        "expected_tables": q["tables"], "expected_refuse": q["refuse"]})
            f.write(json.dumps(rec, default=str) + "\n")
            f.flush()
            rows.append(rec)
            cost = rec.get("cost_usd")
            print(f"{q['id']} {'ok  ' if s['correct'] else 'FAIL'} {rec.get('status')} calls {rec.get('tool_calls')} "
                  f"cost {cost if cost is None else round(cost, 4)} {json.dumps({k: v for k, v in s.items() if k != 'correct'})}",
                  flush=True)
    n = len(rows)
    correct = sum(r["score"]["correct"] for r in rows)
    parts = {}
    for k in ("number", "text", "citation", "refusal"):
        vals = [r["score"][k] for r in rows if k in r["score"]]
        parts[k] = (sum(vals), len(vals))
    costs = [r["cost_usd"] for r in rows if r.get("cost_usd") is not None]
    calls = [r.get("tool_calls", 0) for r in rows]
    retried = sum(bool(r.get("retried")) for r in rows)
    lines = [f"# Evaluation run {run_id}", "",
             f"Model {asker.model}; {n} questions; today = {spec['today']}; backend {os.environ.get('ERW_BACKEND', 'local')}.", "",
             "| Measure | Result |", "|---|---|",
             f"| Correct | {correct} of {n} ({100 * correct / n:.0f}%) |"]
    for k, (a, b) in parts.items():
        lines.append(f"| {k} | {a} of {b} |")
    lines += [f"| Retried after the number check | {retried} |",
              f"| Total cost | USD {sum(costs):.4f} |",
              f"| Mean cost per question | USD {sum(costs) / len(costs):.4f} |" if costs else "| Mean cost | unknown |",
              f"| Mean tool calls | {sum(calls) / n:.2f} |", "",
              "| Id | Correct | Status | Calls | Cost (USD) | Checks |", "|---|---|---|---|---|---|"]
    for r in rows:
        c = r.get("cost_usd")
        checks = ", ".join(f"{k} {'ok' if v else 'FAIL'}" for k, v in r["score"].items() if k != "correct")
        lines.append(f"| {r['id']} | {'yes' if r['score']['correct'] else 'no'} | {r.get('status')} | "
                     f"{r.get('tool_calls')} | {'' if c is None else f'{c:.4f}'} | {checks} |")
    md = os.path.join(HERE, "results", f"{run_id}.md")
    with open(md, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines[:14]))
    print(f"records: {jl}\nsummary: {md}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
