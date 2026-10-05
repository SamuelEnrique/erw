#!/usr/bin/env python3
"""Run the ERCOT evaluation set through Ask, before and after (session 92).

Energy Research Warehouse (ERW).

    python warehouse/chat/eval/ercot_eval.py --arm before --cap 5    # the grid page's chat as it is (ask.py --grid ercot)
    python warehouse/chat/eval/ercot_eval.py --arm after --cap 5     # Ask ERCOT, the reference version (ercot.py)
    python warehouse/chat/eval/ercot_eval.py --arm after --only e03 e41
    python warehouse/chat/eval/ercot_eval.py --arm after --cap 3 --session 114   # a later session's run, under its own cap

Each question of questions_ercot.yaml (built by ercot_expected.py) is asked with the set's fixed date and scored as
eval.py scores: number, text, citation, refusal; a question is correct when all that apply pass. The reference
version is also scored on what it adds: two or three follow-up questions on every answer, and a series (the rows a
chart and a table are drawn from) where the question asks for one, cut from a table the question accepts. "before"
cannot do either and cannot be told the page a reader came from: its context questions are asked bare.

Every model call goes through warehouse/llm.py and its ledger (so the run is a data write: take the data lock). The
cap is the session's: --cap sets ERW_SPEND_CAP_USD for session 92, and llm refuses a call once the ledger's total for
the session has reached it. A question the cap stops is recorded as not run, never as wrong, and the run ends.

Writes results/ercot_<arm>_<run>.jsonl and .md.
"""

import argparse
import datetime as dt
import json
import os
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, ".."))
SESSION = "92"


def extras(q, rec):
    """What the reference version adds, scored: follow-ups, and a series where the question asks for one."""
    import eval as base
    ups = rec.get("followups") or []
    s = {"followups": 2 <= len(ups) <= 3 and all(u.strip().endswith("?") for u in ups)}
    if q.get("series"):
        ser = rec.get("series") or []
        s["series"] = bool(ser) and any(len(x["rows"]) >= 3 and x["table"] in base.accepted(q["tables"]) and x.get("source_report") for x in ser)
    return s


def main(argv=None):
    global SESSION
    ap = argparse.ArgumentParser(description="The ERCOT evaluation of Ask, before and after")
    ap.add_argument("--arm", required=True, choices=["before", "after"])
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--cap", type=float, required=True, help="USD: the session's spend cap (ERW_SPEND_CAP_USD)")
    ap.add_argument("--questions", default=os.path.join(HERE, "questions_ercot.yaml"))
    ap.add_argument("--session", default=SESSION, help="the session the calls are recorded under and the cap counts (session 114; default 92)")
    a = ap.parse_args(argv)
    SESSION = str(a.session)
    os.environ["ERW_SESSION"] = SESSION
    os.environ["ERW_SPEND_CAP_USD"] = str(a.cap)
    os.environ.setdefault("ERW_STEP", f"chat_ercot_eval_{a.arm}")
    import ask
    import eval as base
    import llm
    spec = yaml.safe_load(open(a.questions, encoding="utf-8"))
    qs = [q for q in spec["questions"] if not a.only or q["id"] in a.only]
    if a.only:  # in the order asked: when the cap may end a run early, the questions that matter most go first
        qs.sort(key=lambda q: a.only.index(q["id"]))
    spent0 = llm.session_total(SESSION)
    if a.arm == "after":
        import ercot
        asker = ercot.ErcotAsker()
    else:
        asker = ask.Asker(grid="ercot")
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    stem = os.path.join(HERE, "results", f"ercot_{a.arm}_{run_id}")
    rows, stopped = [], None
    with open(stem + ".jsonl", "w", encoding="utf-8", newline="\n") as f:
        for q in qs:
            try:
                rec = asker.ask(q["question"], today=spec["today"], context=q.get("context")) if a.arm == "after" \
                    else asker.ask(q["question"], today=spec["today"])
            except llm.SpendCapReached as exc:
                stopped = f"{q['id']}: {exc}"
                break
            except Exception as exc:  # a failed question is scored wrong and recorded, never skipped
                rec = {"question": q["question"], "answer": "", "citations": [], "status": "error", "error": f"{type(exc).__name__}: {exc}",
                       "tool_calls": 0, "cost_usd": 0.0, "usage": {}, "retried": False}
            s = base.score(q, rec)
            if a.arm == "after":
                x = extras(q, rec)
                s.update(x)
                s["full"] = s["correct"] and all(x.values())
            rec.update({"id": q["id"], "kind": q["kind"], "arm": a.arm, "score": s, "expected": q["expected"], "expected_text": q["text"],
                        "expected_tables": q["tables"], "expected_refuse": q["refuse"]})
            f.write(json.dumps(rec, default=str) + "\n")
            f.flush()
            rows.append(rec)
            c = rec.get("cost_usd")
            print(f"{q['id']} {q['kind']:7s} {'ok  ' if s['correct'] else 'FAIL'} {rec.get('status')} calls {rec.get('tool_calls')} cost {c if c is None else round(c, 4)} "
                  f"{json.dumps({k: v for k, v in s.items() if k != 'correct'})}", flush=True)
    n = len(rows)
    spent = llm.session_total(SESSION)
    correct = sum(r["score"]["correct"] for r in rows)
    kinds = sorted({r["kind"] for r in rows}, key=["lookup", "series", "join", "refuse", "context"].index)
    costs = [r["cost_usd"] for r in rows if r.get("cost_usd") is not None]
    lines = [f"# ERCOT evaluation, {a.arm}: run {run_id}", "",
             f"{'Ask ERCOT, the reference version (warehouse/chat/ercot.py)' if a.arm == 'after' else 'The grid page chat as it was (ask.py --grid ercot)'}; "
             f"model {asker.model}; {n} of {len(qs)} questions run; today = {spec['today']}; backend {os.environ.get('ERW_BACKEND', 'local')}.", "",
             "| Measure | Result |", "|---|---|",
             f"| Correct | {correct} of {n} ({100 * correct / max(n, 1):.0f}%) |"]
    for k in kinds:
        g = [r for r in rows if r["kind"] == k]
        lines.append(f"| Correct, {k} | {sum(r['score']['correct'] for r in g)} of {len(g)} |")
    for k in ("number", "text", "citation", "refusal") + (("followups", "series", "full") if a.arm == "after" else ()):
        vals = [r["score"][k] for r in rows if k in r["score"]]
        lines.append(f"| {k} | {sum(vals)} of {len(vals)} |")
    lines += [f"| Retried after the check | {sum(bool(r.get('retried')) for r in rows)} |",
              f"| Cost of this run | USD {sum(costs):.4f} |",
              f"| Mean cost per question | USD {sum(costs) / max(len(costs), 1):.4f} |",
              f"| Mean tool calls | {sum(r.get('tool_calls', 0) for r in rows) / max(n, 1):.2f} |",
              f"| Session {SESSION} in the ledger | USD {spent0:.4f} before this run, USD {spent:.4f} after; cap USD {a.cap:.2f} |"]
    if stopped:
        lines.append(f"| Stopped by the cap | {stopped} |")
    lines += ["", "| Id | Kind | Correct | Status | Calls | Cost (USD) | Checks |", "|---|---|---|---|---|---|---|"]
    for r in rows:
        c = r.get("cost_usd")
        checks = ", ".join(f"{k} {'ok' if v else 'FAIL'}" for k, v in r["score"].items() if k != "correct")
        lines.append(f"| {r['id']} | {r['kind']} | {'yes' if r['score']['correct'] else 'no'} | {r.get('status')} | {r.get('tool_calls')} | "
                     f"{'' if c is None else f'{c:.4f}'} | {checks} |")
    with open(stem + ".md", "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines[:22]))
    print(f"records: {stem}.jsonl\nsummary: {stem}.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
