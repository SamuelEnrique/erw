#!/usr/bin/env python3
"""Run the second ERCOT evaluation set through Ask ERCOT, before and after (session 121).

Energy Research Warehouse (ERW).

    python warehouse/chat/eval/ercot_eval_s121.py --arm before --cap 3      # Ask ERCOT as it stood when the session began
    python warehouse/chat/eval/ercot_eval_s121.py --arm after --cap 8       # with the session's changes
    python warehouse/chat/eval/ercot_eval_s121.py --arm after --cap 8 --only p18 j20
    python warehouse/chat/eval/ercot_eval_s121.py --rescore results/ercot_s121_before_<run>.jsonl   # no model call

The set is questions_ercot_s121.yaml (built by ercot_expected_s121.py): 100 questions of five kinds. The two arms ask
the same questions of the same class (ercot.ErcotAsker) at two states of the code; the arm changes one thing only:

  followup  "before" asks the follow-up bare, as the page did (it kept nothing of the answer before it). "after" asks
            the first question, then the follow-up with that answer as the conversation so far. The cost and the time
            of a follow-up in "after" are its own; the first question's are recorded beside them.

How a question is scored (score()). A question is correct when every check that applies passes:

  status    an answer where one is due; a refusal ("not in the warehouse") for the kind outside; either where the
            question says so (status_any)
  number    every expected number is in the answer, each within its own tolerance (half a percent, or to the unit for
            a count); or every number of one of the alternatives (any_of)
  text      every word of `text`, and one word of `text_any`
  citation  a cited table of those accepted; for a join, one of each group (tables_all); every citation complete
  nearest   (outside) the refusal names a table of the guide, in its text or in the field the session added; where the
            question names the nearest tables, one of those

Recorded for every question, never scored: seconds to the full answer; seconds to the first thing a reader is shown
(in "before" that is the full answer: nothing was shown before it); the cost; whether a series came with the answer
and whether its rows are the rows the tool returned.

Every model call goes through warehouse/llm.py and its ledger (a data write: take the data lock). --cap is the
session's total (ERW_SPEND_CAP_USD, session 121): llm refuses a call once the ledger's total for the session has
reached it. A question the cap stops is recorded as not run, never as wrong, and the run ends.
"""

import argparse
import datetime as dt
import json
import os
import statistics
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, ".."))
SESSION = "121"
KINDS = ["join", "vague", "followup", "premise", "outside"]
QUESTIONS = os.path.join(HERE, "questions_ercot_s121.yaml")


def guide_tables():
    """The tables of Ask ERCOT's guide: a refusal that names one of them has named something that is held."""
    import ercot
    return [t for t, _ in ercot.CARDS]


def has_all(got, values, tols):
    return all(any(abs(abs(g) - abs(e)) <= t for g in got) for e, t in zip(values, tols))


def score(q, rec, tables=None):
    import ask
    tables = tables or guide_tables()
    answer = rec.get("answer") or ""
    low = answer.lower()
    status = rec.get("status")
    s = {}
    if q["refuse"]:
        s["status"] = status == "not_in_warehouse"
    elif q.get("status_any"):
        s["status"] = status in ("answered", "not_in_warehouse")
    else:
        s["status"] = status == "answered"
    got = [v for v, _ in ask.numbers(answer)]
    if q["expected"] or q.get("any_of"):
        groups = ([(q["expected"], q["tolerances"])] if q["expected"] else []) + [(g, [max(0.011, 0.005 * abs(v)) for v in g]) for g in q.get("any_of", [])]
        s["number"] = any(has_all(got, vals, tols) for vals, tols in groups)
    if q["text"]:
        s["text"] = all(t.lower() in low for t in q["text"])
    if q.get("text_any"):
        s["text_any"] = any(t.lower() in low for t in q["text_any"])
    cites = rec.get("citations") or []
    cited = {c["table"] for c in cites}
    if q["refuse"]:
        field = [x.get("table") if isinstance(x, dict) else x for x in (rec.get("nearest") or [])]   # the record's: [{table, holds}]
        named = [t for t in tables if t in answer] + [t for t in field if t in tables]
        s["nearest"] = bool(named) and (not q.get("nearest") or any(t in q["nearest"] for t in named))
    elif not (q.get("status_any") and status == "not_in_warehouse"):
        complete = bool(cites) and all(c.get("source_report") and c.get("data_version") for c in cites)
        ok = any(t in cited for t in q["tables"]) if q["tables"] else True
        if q.get("tables_all"):
            ok = all(any(t in cited for t in g) for g in q["tables_all"])
        s["citation"] = ok and complete
    s["correct"] = all(s.values())
    return s


def ask_one(asker, q, today, arm):
    if q["kind"] == "followup" and arm == "after":
        first = asker.ask(q["first"], today=today)
        rec = asker.ask(q["question"], today=today, history=[first])
        rec["first"] = {k: first.get(k) for k in ("question", "answer", "status", "cost_usd", "seconds", "seconds_first", "tool_calls")}
        return rec
    return asker.ask(q["question"], today=today)


def summarize(rows, arm, model, n_asked, today, extra=()):
    n = len(rows)
    correct = sum(r["score"]["correct"] for r in rows)
    costs = [r["cost_usd"] for r in rows if r.get("cost_usd") is not None]
    full = [r["seconds"] for r in rows if r.get("seconds") is not None]
    first = [r.get("seconds_first", r.get("seconds")) for r in rows if r.get("seconds") is not None]
    med = lambda v: f"{statistics.median(v):.1f}" if v else ""  # noqa: E731
    p90 = lambda v: f"{sorted(v)[max(0, int(round(0.9 * len(v))) - 1)]:.1f}" if v else ""  # noqa: E731
    lines = [f"# ERCOT evaluation, second set (session 121), {arm}", "",
             f"Ask ERCOT (warehouse/chat/ercot.py), {'as it stood when the session began' if arm == 'before' else 'with the session changes'}; model {model}; "
             f"{n} of {n_asked} questions run; today = {today}; backend {os.environ.get('ERW_BACKEND', 'local')}.", "",
             "| Kind | Correct | Median seconds to the first thing shown | Median seconds to the full answer | Mean cost (USD) |", "|---|---|---|---|---|"]
    for k in KINDS + ["all"]:
        g = [r for r in rows if k == "all" or r["kind"] == k]
        if not g:
            continue
        c = [r["cost_usd"] for r in g if r.get("cost_usd") is not None]
        lines.append(f"| {k} | {sum(r['score']['correct'] for r in g)} of {len(g)} | {med([r.get('seconds_first', r.get('seconds')) for r in g if r.get('seconds') is not None])} | "
                     f"{med([r['seconds'] for r in g if r.get('seconds') is not None])} | {sum(c) / max(len(c), 1):.4f} |")
    lines += ["", "| Measure | Result |", "|---|---|", f"| Correct | {correct} of {n} |"]
    for k in ("status", "number", "text", "text_any", "citation", "nearest"):
        vals = [r["score"][k] for r in rows if k in r["score"]]
        if vals:
            lines.append(f"| {k} | {sum(vals)} of {len(vals)} |")
    with_series = [r for r in rows if r.get("series")]
    checked = [r for r in with_series if all(x.get("check", {}).get("same") for x in r["series"])]
    lines += [f"| Retried after the check | {sum(bool(r.get('retried')) for r in rows)} |",
              f"| Answers that came with a series | {len(with_series)} ({len(checked)} with every series checked against the rows the tool returned) |",
              f"| Seconds to the first thing shown: median, 90th percentile | {med(first)}, {p90(first)} |",
              f"| Seconds to the full answer: median, 90th percentile, longest | {med(full)}, {p90(full)}, {max(full) if full else ''} |",
              f"| Cost of the questions | USD {sum(costs):.4f} (mean {sum(costs) / max(len(costs), 1):.4f}, highest {max(costs) if costs else 0:.4f}) |",
              f"| Cost of the first questions of the follow-ups | USD {sum((r.get('first') or {}).get('cost_usd') or 0 for r in rows):.4f} |",
              f"| Mean tool calls | {sum(r.get('tool_calls', 0) for r in rows) / max(n, 1):.2f} |"]
    lines += list(extra)
    lines += ["", "| Id | Kind | Correct | Status | Calls | Seconds, first | Seconds, full | Cost (USD) | Checks |", "|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        c = r.get("cost_usd")
        checks = ", ".join(f"{k} {'ok' if v else 'FAIL'}" for k, v in r["score"].items() if k != "correct")
        lines.append(f"| {r['id']} | {r['kind']} | {'yes' if r['score']['correct'] else 'no'} | {r.get('status')} | {r.get('tool_calls')} | {r.get('seconds_first', r.get('seconds'))} | "
                     f"{r.get('seconds')} | {'' if c is None else f'{c:.4f}'} | {checks} |")
    return lines


def rescore(path, questions):
    spec = yaml.safe_load(open(questions, encoding="utf-8"))
    by = {q["id"]: q for q in spec["questions"]}
    rows = [json.loads(line) for line in open(path, encoding="utf-8") if line.strip()]
    tables = guide_tables()
    for r in rows:
        r["score"] = score(by[r["id"]], r, tables)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r, default=str) + "\n")
    arm = rows[0]["arm"] if rows else "?"
    lines = summarize(rows, arm, rows[0].get("model") if rows else "", len(rows), spec["today"], ["| Rescored | from the saved answers; no model call |"])
    with open(path[:-6] + ".md", "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines[:26]))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="The second ERCOT evaluation of Ask ERCOT, before and after (session 121)")
    ap.add_argument("--arm", choices=["before", "after"])
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--kinds", nargs="*", choices=KINDS)
    ap.add_argument("--skip", nargs="*", default=[], help="question ids already answered in another file of this arm (a smoke run): not asked again")
    ap.add_argument("--cap", type=float, help="USD: the session's total spend cap (ERW_SPEND_CAP_USD)")
    ap.add_argument("--questions", default=QUESTIONS)
    ap.add_argument("--rescore", metavar="JSONL", help="score saved answers again and rewrite the summary; no model call")
    ap.add_argument("--tag", default="", help="a word added to the result file's name (a partial run)")
    a = ap.parse_args(argv)
    if a.rescore:
        return rescore(a.rescore, a.questions)
    if not a.arm or a.cap is None:
        ap.error("--arm and --cap are required")
    os.environ["ERW_SESSION"] = SESSION
    os.environ["ERW_SPEND_CAP_USD"] = str(a.cap)
    os.environ.setdefault("ERW_STEP", f"chat_ercot_eval_s121_{a.arm}")
    import ercot
    import llm
    spec = yaml.safe_load(open(a.questions, encoding="utf-8"))
    qs = [q for q in spec["questions"] if (not a.only or q["id"] in a.only) and (not a.kinds or q["kind"] in a.kinds) and q["id"] not in a.skip]
    spent0 = llm.session_total(SESSION)
    asker = ercot.ErcotAsker()
    tables = guide_tables()
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    stem = os.path.join(HERE, "results", f"ercot_s121_{a.arm}{'_' + a.tag if a.tag else ''}_{run_id}")
    rows, stopped = [], None
    with open(stem + ".jsonl", "w", encoding="utf-8", newline="\n") as f:
        for q in qs:
            try:
                rec = ask_one(asker, q, spec["today"], a.arm)
            except llm.SpendCapReached as exc:
                stopped = f"{q['id']}: {exc}"
                break
            except Exception as exc:  # a failed question is scored wrong and recorded, never skipped
                rec = {"question": q["question"], "answer": "", "citations": [], "status": "error", "error": f"{type(exc).__name__}: {exc}",
                       "tool_calls": 0, "cost_usd": 0.0, "usage": {}, "retried": False}
            s = score(q, rec, tables)
            rec.update({"id": q["id"], "kind": q["kind"], "arm": a.arm, "score": s, "expected": q["expected"]})
            f.write(json.dumps(rec, default=str) + "\n")
            f.flush()
            rows.append(rec)
            c = rec.get("cost_usd")
            print(f"{q['id']} {q['kind']:8s} {'ok  ' if s['correct'] else 'FAIL'} {rec.get('status')} calls {rec.get('tool_calls')} {rec.get('seconds')} s cost {c if c is None else round(c, 4)} "
                  f"{json.dumps({k: v for k, v in s.items() if k != 'correct'})}", flush=True)
    spent = llm.session_total(SESSION)
    extra = [f"| Session {SESSION} in the ledger | USD {spent0:.4f} before this run, USD {spent:.4f} after; cap USD {a.cap:.2f} |"]
    if stopped:
        extra.append(f"| Stopped by the cap | {stopped} |")
    lines = summarize(rows, a.arm, asker.model, len(qs), spec["today"], extra)
    with open(stem + ".md", "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines[:28]))
    print(f"records: {stem}.jsonl\nsummary: {stem}.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
