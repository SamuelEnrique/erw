"""Session 10234, evidence a2: how much of the number line the number check lets through, measured on the stored answers.

For every stored answer that replay.py replays (the runs of runs.json with a tool record, status answered or
not_in_warehouse), the sources are built exactly as replay.check builds them (the question, the day line, every tool
result and every tool argument). Then, against that answer's own pool:
  ints    the share of the whole numbers 1 to 100 that ask.unverified lets through, each written alone
  dec1    the share of 400 numbers with one decimal, spread evenly over 0.0 to 99.9, let through
  dec2    the share of 400 numbers with two decimals, spread evenly over 0.00 to 99.99, let through
  moved   of the answer's own figures with decimals, each moved by +7.13 at its own precision, the share let through
And, of the answers sent back once (retried), how many first violations held no untraced number (so "a number could not
be traced" was not the reason). Reads saved files only; no model, no network.
"""
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


def share(values, fmt, sources):
    ok = 0
    for v in values:
        if not ask.unverified(fmt.format(v), sources):
            ok += 1
    return ok / len(values)


rows = []
retried = {"all": 0, "no_number": 0, "examples": []}
for name, graded, label in R.RUNS:
    for q in R.load(name)["questions"]:
        if q.get("retried"):
            retried["all"] += 1
            fv = q.get("first_violations") or []
            nums = [x for x in fv if isinstance(x, str) and re.fullmatch(r"-?[\d.]+", x.strip())]
            if fv and not nums:
                retried["no_number"] += 1
                if len(retried["examples"]) < 8:
                    retried["examples"].append({"run": label, "id": q.get("id"), "first_violations": [str(x)[:120] for x in fv]})
        trace = R.trace_of(q)
        if not trace or not q.get("answer") or q.get("status") not in ("answered", "not_in_warehouse"):
            continue
        today = (q.get("asked_at_utc") or "")[:10]
        sources = [q.get("question") or "", f"Today is {today} (UTC)."] + [json.dumps(t.get("out"), default=str) for t in trace] \
            + [json.dumps(t.get("input"), default=str) for t in trace]
        figs = [m.group() for m in re.finditer(r"(?<![\w.])\d+\.\d+", q["answer"])]
        moved = [f"{float(f) + 7.13:.{len(f.split('.')[1])}f}" for f in figs]
        mv = sum(1 for m in moved if not ask.unverified(m, sources)) / len(moved) if moved else None
        rows.append({"run": label, "id": q.get("id"), "listed": any(t.get("tool") == "list_tables" for t in trace),
                     "ints": share(range(1, 101), "{}", sources), "dec1": share(DEC1, "{:.1f}", sources),
                     "dec2": share(DEC2, "{:.2f}", sources), "moved": mv, "n_moved": len(moved)})


def summ(key, sub):
    vals = [r[key] for r in sub if r[key] is not None]
    if not vals:
        return None
    return {"n": len(vals), "mean": round(statistics.mean(vals), 4), "median": round(statistics.median(vals), 4),
            "min": round(min(vals), 4), "max": round(max(vals), 4)}


out = {"answers": len(rows),
       "all": {k: summ(k, rows) for k in ("ints", "dec1", "dec2", "moved")},
       "with_list_tables": {k: summ(k, [r for r in rows if r["listed"]]) for k in ("ints", "dec1", "dec2", "moved")},
       "without_list_tables": {k: summ(k, [r for r in rows if not r["listed"]]) for k in ("ints", "dec1", "dec2", "moved")},
       "moved_figures": sum(r["n_moved"] for r in rows),
       "moved_let_through": round(sum((r["moved"] or 0) * r["n_moved"] for r in rows)),
       "retried": retried}
print(json.dumps(out, indent=1))
