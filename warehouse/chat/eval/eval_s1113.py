#!/usr/bin/env python3
"""Session 1113 (chain 075): session 320's thirty questions asked again through the site's /api/ask as it now stands,
with every tool call recorded, and graded on keys computed the same hour from the live set.

Energy Research Warehouse (ERW). Three steps, each its own command:

    python warehouse/chat/eval/eval_s1113.py --keys                       the keys from the live set (the anon key, reads
                                                                          only, no model): eval_s1113_keys.json
    python warehouse/chat/eval/eval_s1113.py --ask --base URL --cap 6     the thirty asked as an evaluation (the header
                                                                          x-erw-ask-eval with the server's ASK_EVAL_TOKEN,
                                                                          read from site/.env.local; the ledger step
                                                                          site_ask_eval); eval_s1113_run.json, written
                                                                          after every question; --only b01,g02 for some
    python warehouse/chat/eval/eval_s1113.py --grade                      the grades, no model, no network:
                                                                          eval_s1113_grades.json

The spend cap is enforced before each question: the step's spend of the UTC day, read back from the ledger
(site_api_calls, the service key from .env) or, when the ledger cannot be read, the run's own costs, plus a reserve
(USD 0.50 for the first ten questions, then two and a half times the dearest so far, at least USD 0.30), must stay
under --cap. The route holds its own ceiling (ASK_EVAL_DAILY_USD) too.

The grades, four for each question (session 539's, with one more):
  now        eval_s267.py's grader on the keys of this hour
  held       for a key whose rows the site holds for a license (ISO-NE, NYISO, MISO since 21 October 2026): right when
             the answer says "license needed", names the grid, and states no figure of it (session 1112's answer); the
             others as now
  if_ruled   as now, with session 320's three open rulings taken the answers' way (informative; nothing is ruled):
             a per-kW key accepted in the table's USD per MW, a figure of 1,000 or more accepted rounded to the unit, a
             key accepting every table that holds the figure, and a refusal not graded on a table
  per_kw     as held, with a per-kW key accepted only in USD per kW (what ASK_PER_KW=on would need)
"""
import datetime as dt
import importlib.util
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
KEYS = os.path.join(HERE, "eval_s1113_keys.json")
RUN = os.path.join(HERE, "eval_s1113_run.json")
GRADES = os.path.join(HERE, "eval_s1113_grades.json")
# session 1114: the second set (questions_s1114.yaml, keys computed by expected_s1114.py the same hour) through the same
# asking, with --set s1114: its own run and grades files
SETS = {"s320": {"questions": None, "run": RUN, "grades": GRADES},
        "s1114": {"questions": os.path.join(HERE, "questions_s1114.yaml"), "run": os.path.join(HERE, "eval_s1114_run.json"),
                  "grades": os.path.join(HERE, "eval_s1114_grades.json")}}
ENV_ROOT = ROOT if os.path.exists(os.path.join(ROOT, ".env")) else os.path.join(os.path.dirname(ROOT), "erw")   # a worktree reads the main checkout's
STEP = "site_ask_eval"
GRID_SLUG = {"ERCOT": "ercot", "CAISO": "caiso", "NYISO": "nyiso", "SPP": "spp", "ISO-NE": "isone", "MISO": "miso", "PJM": "pjm"}
GRID_OF_PREFIX = {v: k for k, v in GRID_SLUG.items()}
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36 erw-eval-1113"


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


R = module("regrade_s539_for_s1113", os.path.join(HERE, "regrade_s539.py"))
G = module("eval_s267_for_s1113", os.path.join(HERE, "eval_s267.py"))


def env_file(path, name):
    if not os.path.exists(path):
        return ""
    with open(path, encoding="utf-8") as f:
        for line in f:
            m = re.match(rf"^{name}=(.*)$", line.strip())
            if m:
                return m.group(1).strip().strip('"')
    return ""


def questions(path=None):
    return R.load_yaml(path or R.QUESTIONS)


# ------------------------------------------------------------------ keys

def keys():
    R.KEYS = KEYS          # the module writes its keys where it is told; session 539's file is left as it is
    for name in ("SUPABASE_URL", "SUPABASE_ANON_KEY"):   # the anon read's keys, from the main checkout's .env in a worktree
        if not os.environ.get(name):
            os.environ[name] = env_file(os.path.join(ENV_ROOT, ".env"), name)
    doc = R.build_keys()
    doc["_about"] = doc["_about"].replace("Session 539", "Session 1113 (with session 539's code)").replace("regrade_s539.py --keys", "eval_s1113.py --keys")
    with open(KEYS, "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, indent=1)
        f.write("\n")
    return doc


# ------------------------------------------------------------------ asking

def spent_today():
    url, key = env_file(os.path.join(ENV_ROOT, ".env"), "SUPABASE_URL").rstrip("/"), env_file(os.path.join(ENV_ROOT, ".env"), "SUPABASE_SERVICE_KEY")
    if not url or not key:
        return None
    u = urllib.parse.urlparse(url)
    day = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT00:00:00Z")
    q = urllib.parse.urlencode({"select": "usd", "step": f"eq.{STEP}", "ts_utc": f"gte.{day}", "limit": "5000"})
    req = urllib.request.Request(f"{u.scheme}://{u.netloc}/rest/v1/site_api_calls?{q}", headers={"apikey": key, "Authorization": f"Bearer {key}"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            rows = json.loads(r.read())
    except Exception as exc:  # noqa: BLE001: the run's own costs stand in, and the line says so
        print(f"ledger unreadable: {exc}")
        return None
    if any(r.get("usd") is None for r in rows):
        return None
    return sum(float(r["usd"]) for r in rows), len(rows)


def post(base, token, q, ip):
    body = {"question": q["question"], "grid": GRID_SLUG[q["grid"]]} if q["via"] == "grid" else {"question": q["question"]}
    req = urllib.request.Request(f"{base}/api/ask", data=json.dumps(body).encode("utf-8"), method="POST", headers={
        "Content-Type": "application/json", "Origin": base, "User-Agent": UA, "X-Forwarded-For": ip, "Sec-Fetch-Site": "same-origin", "x-erw-ask-eval": token})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            raw, status = r.read().decode("utf-8"), r.status
    except urllib.error.HTTPError as e:
        raw, status = e.read().decode("utf-8", "replace"), e.code
    try:
        out = json.loads(raw)
    except ValueError:
        out = {"error": raw[:300]}
    out["_http"], out["_seconds"] = status, round(time.time() - t0, 1)
    return out


def ask(base, cap, only=None, which="s320"):
    token = env_file(os.path.join(ROOT, "site", ".env.local"), "ASK_EVAL_TOKEN") or env_file(os.path.join(ENV_ROOT, "site", ".env.local"), "ASK_EVAL_TOKEN")
    if len(token) < 24:
        raise SystemExit("ASK_EVAL_TOKEN (24 characters at least) is not in site/.env.local")
    qs = questions(SETS[which]["questions"])
    RUN = SETS[which]["run"]
    run = {"_about": f"Session 1113 ({which}): the questions (questions_s320.yaml) asked through the site's /api/ask on a local production build of main, as an evaluation (x-erw-ask-eval; ledger step site_ask_eval), each as its page sends it; every answer carries its tool calls and their results (trace, session 1111).",
           "base": base, "questions": []}
    if os.path.exists(RUN):
        with open(RUN, encoding="utf-8") as f:
            run = json.load(f)
    done = {x["id"]: x for x in run["questions"]}
    dearest = max([float(x.get("cost_usd") or 0) for x in run["questions"]] + [0.0])
    for i, q in enumerate(qs):
        if (only and q["id"] not in only) or (not only and q["id"] in done):
            continue
        led = spent_today()
        spent = led[0] if led else sum(float(x.get("cost_usd") or 0) for x in run["questions"])
        reserve = 0.50 if len(done) < 10 else max(0.30, 2.5 * dearest)
        if spent + reserve > cap:
            print(f"{q['id']}: STOPPED before the call: spent {spent:.4f} (ledger {led}) + reserve {reserve:.2f} > cap {cap:.2f}")
            break
        ip = f"10.{(int(time.time()) // 60) % 200 + 20}.{(int(time.time()) // 3600) % 250}.{1 + i // 8}"
        at = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        r = post(base, token, q, ip)
        cost = float(r.get("cost_usd") or 0)
        dearest = max(dearest, cost)
        done[q["id"]] = {**{k: q.get(k) for k in ("id", "grid", "via", "question")}, "asked_at_utc": at, "http": r.get("_http"),
                         "model": r.get("model"), "status": r.get("status") or ("error" if r.get("error") else None), "answer": r.get("answer"),
                         "why": r.get("why"), "citations": r.get("citations"), "not_in_warehouse": r.get("not_in_warehouse"),
                         "tool_calls": r.get("tool_calls"), "retried": r.get("retried"), "cost_usd": cost, "seconds": r.get("seconds", r.get("_seconds")),
                         "error": r.get("error"), "refused": r.get("refused"), "trace": r.get("trace")}
        run["questions"] = [done[x["id"]] for x in qs if x["id"] in done]
        with open(RUN, "w", encoding="utf-8", newline="\n") as f:
            json.dump(run, f, indent=1, ensure_ascii=False)
            f.write("\n")
        print(f"{q['id']} {q['via']:7} http {r.get('_http')} {done[q['id']]['status']} calls {r.get('tool_calls')} cost {cost:.4f} {done[q['id']]['seconds']}s"
              + (f" ERROR {str(r.get('error'))[:160]}" if r.get("error") else ""))
    print(f"asked {len(run['questions'])} of {len(qs)}; the step's ledger today: {spent_today()}")


# ------------------------------------------------------------------ grading

def held_ok(answer, k):
    """Session 1112's answer to a held grid: "license needed", the grid named, and no figure of it."""
    grid = GRID_OF_PREFIX.get(k["entity"].split(":")[0], "")
    a = answer or ""
    figure = k["table_unit_value"]
    written = G.numbers(a)
    states = any(abs(v - figure) < 0.5 * 10 ** -max(d, 0) + 1e-9 and d >= 1 for v, d in written) or any(abs(v - figure) < 1e-6 for v, _ in written)
    return "license needed" in a.lower() and grid.lower() in a.lower() and not states


def grade_s1114():
    """The second set: each question graded by eval_s267.py's grader on its own key (questions_s1114.yaml), a date in
    its text accepted written either way ("September 3" or "3 September")."""
    with open(SETS["s1114"]["run"], encoding="utf-8") as f:
        run = {x["id"]: x for x in json.load(f)["questions"]}
    out = []
    for q in questions(SETS["s1114"]["questions"]):
        a = run.get(q["id"])
        if a is None:
            continue
        g = G.grade(q, a)
        if g.get("text") is False:
            ans = (a.get("answer") or "").lower()
            ok = True
            for t in q["text"]:
                m = re.fullmatch(r"([A-Za-z]+) (\d{1,2})", t)
                alts = [t.lower()] + ([f"{m.group(2)} {m.group(1)}".lower()] if m else [])
                ok = ok and any(x in ans for x in alts)
            g["text"] = ok
            g["ok"] = all(v for k, v in g.items() if k != "ok" and v is not None)
        out.append({"id": q["id"], "via": q["via"], "grid": q["grid"], "status": a.get("status"), "tool_calls": a.get("tool_calls"), "retried": a.get("retried"),
                    "cost_usd": a.get("cost_usd"), "seconds": a.get("seconds"), "expected": q["expected"], "ok": g["ok"], "grade": g, "trace_calls": len(a.get("trace") or [])})
    doc = {"_about": "Session 1114: eval_s1114_run.json graded on questions_s1114.yaml's keys by eval_s1113.py --grade --set s1114 (no model, no network).",
           "asked": len(out), "right": sum(r["ok"] for r in out), "cost_usd": round(sum(float(r["cost_usd"] or 0) for r in out), 4), "questions": out}
    with open(SETS["s1114"]["grades"], "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, indent=1)
        f.write("\n")
    print(f"right {doc['right']} of {doc['asked']}; cost USD {doc['cost_usd']}")
    return doc


def grade(run_doc=None, keys_doc=None):
    if run_doc is None:
        with open(RUN, encoding="utf-8") as f:
            run_doc = json.load(f)
    if keys_doc is None:
        with open(KEYS, encoding="utf-8") as f:
            keys_doc = json.load(f)
    run = {x["id"]: x for x in run_doc["questions"]}
    ks = keys_doc["keys"]
    day = (keys_doc.get("computed_at_utc") or "")[:10]
    out = []
    for q in questions():
        a = run.get(q["id"])
        if a is None:
            continue
        k = ks.get(q["id"])
        now_q = dict(q)
        if k:
            now_q["expected"] = k["expected"]
            if q["id"] in ("b07", "d08") and k.get("month_name"):
                now_q["text"] = ([k["month"][:4]] if q["id"] == "b07" else []) + [k["month_name"]]
        now = G.grade(now_q, a)
        held = bool(k) and not q["refuse"] and any(R.held_row(k["table"], e.strip(), day) for e in k["entity"].split(" less "))
        held_g = {"ok": held_ok(a.get("answer"), k)} if held else now
        if_q = dict(now_q)
        if k and R.SPEC.get(q["id"], (None,) * 6)[5] == 1000:
            if_q["expected"], if_q["tolerance"] = [k["table_unit_value"]], q["tolerance"] * 1000
        if any(abs(x) >= 1000 for x in if_q["expected"]):
            if_q["tolerance"] = max(if_q["tolerance"], 0.5)
        if q["id"] == "g08":
            if_q["tables"] = q["tables"] + [R.C]
        if q["refuse"]:
            if_q["tables"] = []
        if_ruled = {"ok": held_ok(a.get("answer"), k)} if held else G.grade(if_q, a)
        out.append({"id": q["id"], "via": q["via"], "grid": q["grid"], "status": a.get("status"), "tool_calls": a.get("tool_calls"),
                    "retried": a.get("retried"), "cost_usd": a.get("cost_usd"), "seconds": a.get("seconds"), "expected_now": now_q["expected"],
                    "held": held, "now_ok": now["ok"], "held_ok": held_g["ok"], "if_ruled_ok": if_ruled["ok"], "grade_now": now,
                    "trace_calls": len(a.get("trace") or [])})
    doc = {"_about": "Session 1113: eval_s1113_run.json graded on eval_s1113_keys.json by eval_s1113.py --grade (no model, no network).",
           "keys_computed_at_utc": keys_doc.get("computed_at_utc"), "asked": len(out),
           "right_now": sum(r["now_ok"] for r in out), "right_under_hold": sum(r["held_ok"] for r in out),
           "right_if_ruled": sum(r["if_ruled_ok"] for r in out), "held": [r["id"] for r in out if r["held"]],
           "cost_usd": round(sum(float(r["cost_usd"] or 0) for r in out), 4), "questions": out}
    with open(GRADES, "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, indent=1)
        f.write("\n")
    print(f"right now {doc['right_now']}, under the hold {doc['right_under_hold']}, if ruled {doc['right_if_ruled']} of {doc['asked']}; cost USD {doc['cost_usd']}")
    return doc


def main(argv):
    which = argv[argv.index("--set") + 1] if "--set" in argv else "s320"
    if which not in SETS:
        raise SystemExit(f"--set must be one of {sorted(SETS)}")
    if "--keys" in argv:
        keys()
    if "--ask" in argv:
        base = argv[argv.index("--base") + 1] if "--base" in argv else "http://localhost:3713"
        cap = float(argv[argv.index("--cap") + 1]) if "--cap" in argv else 6.0
        only = set(argv[argv.index("--only") + 1].split(",")) if "--only" in argv else None
        ask(base, cap, only, which)
    if "--grade" in argv:
        grade_s1114() if which == "s1114" else grade()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
