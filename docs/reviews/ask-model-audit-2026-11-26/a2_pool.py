"""Session 10234, evidence a2: how much of the number line the number check lets through, measured on the stored answers.

For every stored answer that replay.py replays (the runs of runs.json with a tool record, status answered or
not_in_warehouse), the sources are built exactly as replay.check builds them (the question, the day line, every tool
result and every tool argument), and the pool is every number ask.numbers reads in them. A figure written alone with d
decimals passes ask.unverified when some pool number's magnitude lies within 0.5 * 10**-d of it (the same rule; the
percentile names and list markers of unverified do not arise for a figure written alone). Against each answer's pool:
  ints    the share of the whole numbers 1 to 100 let through
  dec1    the share of 400 numbers with one decimal, evenly over 0.0 to 99.9, let through
  dec2    the share of 400 numbers with two decimals, evenly over 0.00 to 99.99, let through
  big     the share of 400 whole numbers evenly over 1,000 to 100,000 let through
  moved   of the answer's own figures with decimals, each moved by +7.13 at its own precision, the share let through
The rule is checked against ask.unverified itself on the first 30 answers (every candidate of ints). Reads saved files
only; no model, no network.
"""
import bisect
import json
import os
import re
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "chat", "eval"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "chat"))
import replay as R  # noqa: E402
import ask  # noqa: E402

DEC1 = [round(i * 0.25, 1) for i in range(400)]
DEC2 = [round(i * 0.2497, 2) for i in range(400)]
BIG = [1000 + i * 247 for i in range(400)]


def passes(sorted_pool, v, d):
    tol = 0.5 * 10 ** (-d) + 1e-9
    i = bisect.bisect_left(sorted_pool, v - tol)
    return i < len(sorted_pool) and sorted_pool[i] <= v + tol


rows, checked, disagree = [], 0, 0
for name, graded, label in R.RUNS:
    for q in R.load(name)["questions"]:
        trace = R.trace_of(q)
        if not trace or not q.get("answer") or q.get("status") not in ("answered", "not_in_warehouse"):
            continue
        today = (q.get("asked_at_utc") or "")[:10]
        sources = [q.get("question") or "", f"Today is {today} (UTC)."] + [json.dumps(t.get("out"), default=str) for t in trace] \
            + [json.dumps(t.get("input"), default=str) for t in trace]
        pool = sorted({abs(v) for s in sources for v, _ in ask.numbers(s)})
        if checked < 30:
            for k in range(1, 101):
                if passes(pool, k, 0) != (not ask.unverified(str(k), sources)):
                    disagree += 1
            checked += 1
        figs = [m.group() for m in re.finditer(r"(?<![\w.])\d+\.\d+", q["answer"])]
        moved = [float(f) + 7.13 for f in figs]
        decs = [len(f.split(".")[1]) for f in figs]
        mv = sum(1 for v, d in zip(moved, decs) if passes(pool, round(v, d), d)) / len(moved) if moved else None
        rows.append({"run": label, "id": q.get("id"), "listed": any(t.get("tool") == "list_tables" for t in trace), "pool": len(pool),
                     "ints": sum(passes(pool, k, 0) for k in range(1, 101)) / 100,
                     "dec1": sum(passes(pool, v, 1) for v in DEC1) / len(DEC1),
                     "dec2": sum(passes(pool, v, 2) for v in DEC2) / len(DEC2),
                     "big": sum(passes(pool, v, 0) for v in BIG) / len(BIG),
                     "moved": mv, "n_moved": len(moved)})


def summ(key, sub):
    vals = [r[key] for r in sub if r[key] is not None]
    if not vals:
        return None
    return {"n": len(vals), "mean": round(statistics.mean(vals), 4), "median": round(statistics.median(vals), 4),
            "min": round(min(vals), 4), "max": round(max(vals), 4)}


keys = ("pool", "ints", "dec1", "dec2", "big", "moved")
out = {"answers": len(rows), "rule_checked_on": checked, "rule_disagreements_with_unverified": disagree,
       "all": {k: summ(k, rows) for k in keys},
       "with_list_tables": {k: summ(k, [r for r in rows if r["listed"]]) for k in keys},
       "without_list_tables": {k: summ(k, [r for r in rows if not r["listed"]]) for k in keys},
       "moved_figures": sum(r["n_moved"] for r in rows),
       "moved_let_through": round(sum((r["moved"] or 0) * r["n_moved"] for r in rows))}
print(json.dumps(out, indent=1))
