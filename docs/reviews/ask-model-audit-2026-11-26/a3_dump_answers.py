"""Session 10234: print, for the trader's twenty asked through the site's loop (session 5275), each question, its key,
the answer, the stored grade, and every number of the tool results that lies within the key's tolerance, with the
field it sat in, so each answer can be re-scored by hand. Reads saved files only; no model, no network."""
import json
import os
import sys

EVAL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "warehouse", "chat", "eval")
run_name = sys.argv[1] if len(sys.argv) > 1 else "eval_s5275_site_trader_run.json"
keys_name = sys.argv[2] if len(sys.argv) > 2 else "keys_trader.json"
grades_name = sys.argv[3] if len(sys.argv) > 3 else "eval_s5275_site_trader_grades.json"
run = json.load(open(os.path.join(EVAL, run_name), encoding="utf-8"))
keys = json.load(open(os.path.join(EVAL, keys_name), encoding="utf-8"))["keys"]
grades = {g["id"]: g for g in json.load(open(os.path.join(EVAL, grades_name), encoding="utf-8"))["questions"]}


def walk(x, path, out):
    if isinstance(x, bool) or x is None:
        return
    if isinstance(x, (int, float)):
        out.append((path, float(x)))
    elif isinstance(x, dict):
        for k, v in x.items():
            walk(v, f"{path}.{k}", out)
    elif isinstance(x, list):
        for i, v in enumerate(x):
            walk(v, f"{path}[{i}]", out)


only = set(sys.argv[4].split(",")) if len(sys.argv) > 4 else None
for q in run["questions"]:
    if only and q["id"] not in only:
        continue
    k = keys.get(q["id"], {})
    g = grades.get(q["id"], {})
    print("=" * 100)
    print(q["id"], "|", q.get("question"))
    print("KEY expected", k.get("expected"), "tol", k.get("tolerance"), "text", k.get("text"), "refuse", k.get("refuse"), "hold", k.get("hold"))
    print("KEY note:", k.get("note"))
    print("STATUS", q.get("status"), "| retried", q.get("retried"), "| calls", q.get("tool_calls"), "| stored ok", g.get("ok"), g.get("grade"))
    print("ANSWER:", q.get("answer"))
    print("CITES:", [c.get("table") for c in q.get("citations") or []])
    trace = q.get("trace") or []
    for i, t in enumerate(trace):
        inp = json.dumps(t.get("input"), default=str)
        print(f"  call {i + 1} {t.get('tool')} {inp[:300]}")
        nums = []
        walk(t.get("out"), "out", nums)
        for e in k.get("expected") or []:
            tol = max(float(k.get("tolerance") or 0.01), 1e-9)
            hits = [(p, v) for p, v in nums if abs(abs(v) - abs(e)) <= tol * max(1.0, abs(e)) and abs(abs(v) - abs(e)) <= 0.51]
            for p, v in hits[:4]:
                print(f"     key {e} found at {p} = {v}")
