#!/usr/bin/env python3
"""Session 2221 (chain 152): session 320's thirty asked through the Python loop (warehouse/chat/ask.py), with every
tool call recorded, graded on keys computed the same hour from the live set, under a spend cap.

Energy Research Warehouse (ERW). One command, three steps, each into files of its own so that no stored run is touched:

    python warehouse/chat/eval/eval_loop.py --session 2221 --cap 3 [--only b01,b02] [--set s320] [--no-ask]

  keys     eval_s1113.py's --keys (session 539's code: the keys from the live set, the anon key, no model), written to
           eval_s<N>_loop_keys.json
  ask      each question through ask.Asker: a grid question through the grid's scoped chat (Asker(grid=<slug>)), the
           general chat otherwise; the hold on as the site's (ASK_HOLD=on, warehouse/chat/license_hold.py); the Supabase
           live set as the backend (ERW_BACKEND=supabase), so the tools read what the site reads; every tool call and
           its result recorded (record_tools); eval_s<N>_loop_run.json written after every question, and read first, so
           a run asked again goes on where it stopped. The model calls go through the repository's client under the
           ledger step chat_eval, with the ledger file not written (ERW_LEDGER=0: a code machine holds no data lock) and each
           call's cost kept in the run file from the response's usage block. The cap is checked before each question: the run's own costs plus a reserve (USD 0.50
           for the first ten questions, then the dearest so far, at least USD 0.30) must stay
           under --cap (the reserve one question at the dearest cost seen, the costs being exact here).
  grade    eval_s1113.py's grade (now, under the hold, if ruled), written to eval_s<N>_loop_grades.json.

The run file has the shape of eval_s1113_run.json (so replay.py, refusals.py and history.py read it through runs.json),
with "loop": "python" on every record and each trace entry carrying isError beside is_error (the site's key, which
refusals.py reads). Nothing of the warehouse is written; nothing is sent but the model calls and the live set's reads.
"""
import datetime as dt
import importlib.util
import json
import os
import sys
import time
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ENV_ROOT = ROOT if os.path.exists(os.path.join(ROOT, ".env")) else os.path.join(os.path.dirname(ROOT), "erw")   # a worktree reads the main checkout's
sys.path.insert(0, os.path.dirname(HERE))


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def load_env():
    """The keys from .env into the environment where they are not set: the live set's address and anon key, the model's
    key. Values are never printed."""
    try:
        from dotenv import dotenv_values
    except ImportError:  # pragma: no cover
        return
    for k, v in (dotenv_values(os.path.join(ENV_ROOT, ".env")) or {}).items():
        if v is not None and not os.environ.get(k):
            os.environ[k] = v


def files(session, which):
    tag = f"eval_s{session}_loop" + ("" if which == "s320" else f"_{which}")
    return {k: os.path.join(HERE, f"{tag}_{k}.json") for k in ("keys", "run", "grades")}


def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def write_json(path, doc):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, indent=1, ensure_ascii=False)
        f.write("\n")


def trace_of(rec):
    out = []
    for t in rec.get("trace") or []:
        if isinstance(t, dict):
            t = dict(t)
            if "is_error" in t and "isError" not in t:
                t["isError"] = bool(t["is_error"])
            out.append(t)
    return out


def ask_all(E, ask, qs, run_path, cap, only, session, which):
    run = {"_about": f"Session {session} (chain 152, {which}): the questions asked through the Python loop (warehouse/chat/ask.py Asker; a grid "
                     "question through the grid's scoped chat), the hold on as the site's (ASK_HOLD=on), the Supabase live set as the backend, "
                     "every tool call recorded (trace), by eval_loop.py under the ledger step chat_eval.",
           "base": "python loop", "questions": []}
    if os.path.exists(run_path):
        run = read_json(run_path)
    done = {x["id"]: x for x in run["questions"]}
    dearest = max([float(x.get("cost_usd") or 0) for x in run["questions"]] + [0.0])
    for q in qs:
        if (only and q["id"] not in only) or (not only and q["id"] in done):
            continue
        spent = sum(float(x.get("cost_usd") or 0) for x in run["questions"])
        # the costs here are exact (each response's usage block, no ledger lag), so the reserve is one more question at the
        # dearest cost seen (USD 0.50 until ten are asked), where eval_s1113.py keeps two and a half times it
        reserve = 0.50 if len(done) < 10 else max(0.30, dearest)
        if spent + reserve > cap:
            print(f"{q['id']}: STOPPED before the call: spent {spent:.4f} + reserve {reserve:.2f} > cap {cap:.2f}")
            break
        at = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        t0 = time.time()
        rec, error = {}, None
        try:
            asker = ask.Asker(grid=E.GRID_SLUG[q["grid"]] if q["via"] == "grid" else None, record_tools=True)
            rec = asker.ask(q["question"])
        except Exception as exc:  # noqa: BLE001: the question is recorded as an error and the run goes on
            error = f"{type(exc).__name__}: {exc}"
            traceback.print_exc()
        cost = float(rec.get("cost_usd") or 0)
        dearest = max(dearest, cost)
        status = rec.get("status") or ("error" if error else None)
        done[q["id"]] = {**{k: q.get(k) for k in ("id", "grid", "via", "question")}, "asked_at_utc": at, "http": None, "loop": "python",
                         "model": rec.get("model"), "status": status, "answer": rec.get("answer"), "why": rec.get("why"),
                         "citations": rec.get("citations"), "not_in_warehouse": status == "not_in_warehouse",
                         "tool_calls": rec.get("tool_calls"), "retried": bool(rec.get("retried")), "cost_usd": cost,
                         "seconds": rec.get("seconds", round(time.time() - t0, 1)), "error": error, "refused": status == "refused_unverified",
                         "first_violations": rec.get("first_violations"), "second_violations": rec.get("second_violations"),
                         "reads": rec.get("reads"), "nearest": rec.get("nearest"), "trace": trace_of(rec)}
        run["questions"] = [done[x["id"]] for x in qs if x["id"] in done]
        write_json(run_path, run)
        print(f"{q['id']} {q['via']:7} {status} calls {rec.get('tool_calls')} cost {cost:.4f} {done[q['id']]['seconds']}s"
              + (f" ERROR {error[:160]}" if error else ""))
    spent = sum(float(x.get("cost_usd") or 0) for x in run["questions"])
    print(f"asked {len(run['questions'])} of {len(qs)}; the run's cost USD {spent:.4f}")
    return run


def main(argv):
    if "--session" not in argv:
        raise SystemExit("--session <N> is required (the files are named by it)")
    session = argv[argv.index("--session") + 1]
    which = argv[argv.index("--set") + 1] if "--set" in argv else "s320"
    cap = float(argv[argv.index("--cap") + 1]) if "--cap" in argv else 3.0
    only = set(argv[argv.index("--only") + 1].split(",")) if "--only" in argv else None
    load_env()
    os.environ["ERW_BACKEND"] = "supabase"
    os.environ["ASK_HOLD"] = "on"
    os.environ.setdefault("ERW_STEP", "chat_eval")
    # the cost ledger is a table of warehouse/output, which only a machine holding the data lock writes (docs/machines.md,
    # "The data lock"); this runner runs on a code machine, so the ledger file is not written (ERW_LEDGER=0: the calls go
    # through as before) and every call's cost stands in the run file instead, from the usage block of each response
    os.environ.setdefault("ERW_LEDGER", "0")
    E = module("eval_s1113_for_loop", os.path.join(HERE, "eval_s1113.py"))
    if which not in E.SETS:
        raise SystemExit(f"--set must be one of {sorted(E.SETS)}")
    import ask  # noqa: E402  the Python loop, after the environment is set
    F = files(session, which)
    if which == "s320":
        if os.path.exists(F["keys"]):
            keys_doc = read_json(F["keys"])
            print(f"keys: {F['keys']} (computed {keys_doc.get('computed_at_utc')})")
        else:
            E.KEYS = F["keys"]
            keys_doc = E.keys()
            print(f"keys: {F['keys']} written at {keys_doc.get('computed_at_utc')}")
    qs = E.questions(E.SETS[which]["questions"])
    if "--no-ask" not in argv:
        run = ask_all(E, ask, qs, F["run"], cap, only, session, which)
    else:
        run = read_json(F["run"])
    if which == "s320":
        E.GRADES = F["grades"]
        doc = E.grade(run, keys_doc)
        doc["_about"] = (f"Session {session} (chain 152): {os.path.basename(F['run'])} graded on {os.path.basename(F['keys'])} by "
                         "eval_loop.py with eval_s1113.py's grade (no model, no network).")
        doc["loop"] = "python"
        write_json(F["grades"], doc)
    else:
        E.SETS[which]["run"], E.SETS[which]["grades"] = F["run"], F["grades"]
        E.grade_s1114()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
