"""Audit of Automated Analysis (session 10204): is "the week before" always the week before?

run.change pairs each held period with the previous HELD period; run.finding then writes "the week before" for any
weekly figure. Two checks:
1. on the engine: a weekly headline whose previous week is missing (too few rows) is compared with the week two back,
   and the caption still says "the week before";
2. on the files: every finding in docs/analysis/*/chart_of_the_week.json (the chosen one and the five also_moved),
   whose compared period does not end the day before its own begins.

Run: python runs/a10_week_before.py <repo root> > runs/a10.out
"""
import datetime as dt
import glob
import json
import os
import sys

ROOT = sys.argv[1]
sys.path.insert(0, os.path.join(ROOT, "warehouse", "analysis"))
sys.path.insert(0, os.path.join(ROOT, "warehouse"))
import run  # noqa: E402


def wk(monday):
    a = dt.date.fromisoformat(monday)
    return f"{a} to {a + dt.timedelta(days=6)}"


def engine():
    mondays = [dt.date(2026, 1, 5) + dt.timedelta(weeks=i) for i in range(20)]
    hist = [(wk(str(m)), 10.0 + (i % 3)) for i, m in enumerate(mondays) if i != 19]   # week 19, the one before the headline, not held
    head = {"label": "a weekly mean", "unit": "u", "period": wk(str(dt.date(2026, 1, 5) + dt.timedelta(weeks=20))), "value": 20.0, "history": hist}
    ch = run.change(head, "previous")
    one, two = run.finding(head, ch, "previous")
    print("engine: headline", head["period"], "compared with", ch["prev_period"])
    print("engine: caption:", one)


def files():
    bad = 0
    for path in sorted(glob.glob(os.path.join(ROOT, "docs", "analysis", "2026-W*", "chart_of_the_week.json"))):
        c = json.load(open(path, encoding="utf-8"))
        items = [c] + list(c.get("also_moved") or [])
        for it in items:
            ch = it.get("change") or {}
            h = it.get("headline") or {}
            p, q = str(h.get("period", "")), str(ch.get("prev_period", ""))
            if " to " not in p or " to " not in q:
                continue
            start = dt.date.fromisoformat(p.split(" to ")[0])
            prev_end = dt.date.fromisoformat(q.split(" to ")[1])
            gap = (start - prev_end).days
            words = it.get("finding") or ""
            if gap != 1:
                bad += 1
                print(f"{os.path.basename(os.path.dirname(path))}: {it.get('template')}: {p} against {q} (gap {gap} days); words: {words[:220]}")
    print("findings whose compared week is not the week before:", bad)


if __name__ == "__main__":
    engine()
    files()
