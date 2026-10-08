#!/usr/bin/env python3
"""Session 157: rerun the model's reads and scores of the policy actions held against their source text, under a cap.

Energy Research Warehouse (ERW). The audit of 100 policy actions against their source documents
(docs/methods/policy_monitor.md) found the model's fields weakest where the model had been given least: 1,086 of 1,843
actions were scored on a title alone, and the impact reads carried states, sectors and price directions their text
did not support. With each Federal Register document's printed text now held (policy_sources.py reads it once), this
script gives the same models the text and asks again, in the owner's order of priority:

    reads    the impact reads held in policy_reads (234), newest first: the reader of warehouse/policy/reads.py with
             its three corrections, on the printed text from the store (a Register document) or on the release itself,
             fetched once by a plain request (a news release of a regulator's or a commission's own site);
    title    the Register actions that were scored on a title alone (no abstract in the Register's record), newest
             first: the scorer of warehouse/policy/score.py, given the first paragraph of the printed text;
    rest     the other Register actions, newest first: the same scorer, on the same summary as before with the one
             line session 154 proposed.

Every answer is saved the moment it is paid for (WORK/answers/), before anything is checked: a paid answer is never
discarded, and a row with a saved answer for the same text is not asked again. The stop sits BEFORE each call: a call
starts only if the session's spend so far, plus the worst-case reserves of the calls in flight, plus this call's own
worst-case reserve (its prompt at CHARS_PER_TOKEN characters a token and max_tokens of output, at the configured
prices), fits under --stop-usd. Spend goes through the cost ledger (warehouse/llm.py) as the session in ERW_SESSION;
ERW_SPEND_CAP_USD is the ledger's own second stop.

Every row is marked. policy_reads.recheck and policy_actions.model_recheck hold one of:
    rechecked               the model field(s) were made again from the source text in this session (rechecked_at)
    not rechecked           the money or the scope did not reach the row; its fields are as they were
    source not reachable    the source text could not be fetched; its fields are as they were
A row whose rating, sector, why or read changes keeps its old value in warehouse/policy/eval/recheck_s157_changes.csv.

    python warehouse/policy/recheck.py --actions TRIAL/policy_actions.csv --reads MAIN/policy_reads.csv \\
        --evidence MAIN/policy_reads_evidence.csv --text-dir STORE --work WORK --ledger-dir LEDGER --plan
    ... --step reads --limit 3         # measure a few
    ... --step title --limit 1         # one batch of 40
    ... --step reads | title | rest    # the batch, until the stop
    ... --build                        # no call: the tables, the scores file and the before-and-after from the answers
"""

import argparse
import concurrent.futures as cf
import csv
import datetime as dt
import hashlib
import io
import json
import os
import re
import sys
import threading
import time
from urllib.parse import urlparse

import pandas as pd
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
for p in (os.path.join(ROOT, "warehouse", "connectors"), os.path.join(ROOT, "warehouse", "news"),
          os.path.join(ROOT, "warehouse", "chat"), os.path.join(ROOT, "warehouse"), HERE):
    if p not in sys.path:
        sys.path.insert(0, p)
import iso_prices as ip  # noqa: E402

SESSION = "157"
CHARS_PER_TOKEN = 2.5        # a low figure on purpose: the reserve must be a worst case
READ_MAX_TOKENS = 8000       # as reads.py (session 26)
SCORE_MAX_TOKENS = 6000      # 40 items a batch; an answer is about 70 tokens an item
BATCH = 40
WORKERS = 4
CHANGES = os.path.join(HERE, "eval", "recheck_s157_changes.csv")
SUMMARY = os.path.join(HERE, "eval", "recheck_s157_summary.json")
SCORES = os.path.join(HERE, "scores.csv")
# A release is fetched only from the site of a federal regulator or agency, or of a state commission (the scope of
# the monitor: nothing municipal, and no office that is neither). A release on another host is not requested.
RELEASE_HOSTS = {"www.nrc.gov": "the NRC", "www.energy.gov": "the Department of Energy",
                 "ftp.puc.texas.gov": "the Public Utility Commission of Texas",
                 "www.puc.texas.gov": "the Public Utility Commission of Texas",
                 "www.cpuc.ca.gov": "the California Public Utilities Commission"}
UA = {"User-Agent": "Mozilla/5.0 (ERW energy research warehouse; https://github.com/SamuelEnrique/erw)"}
assert "@" not in UA["User-Agent"]
READ_FIELDS = ["what_changes", "affected_sectors", "affected_isos", "affected_states", "direction_supply",
               "direction_demand", "direction_prices", "direction_buildout", "timeline", "plain_read", "fields_kept",
               "fields_dropped"]


def now_iso():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_events(path):
    return pd.read_csv(path, skiprows=ip.header_rows(path), dtype=str, keep_default_na=False)


def head_lines(path):
    with open(path, encoding="utf-8") as f:
        return [next(f) for _ in range(ip.header_rows(path))]


def safe(i):
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", i)


class Budget:
    """The stop, BEFORE a call. spent is what the session's ledger held when the run began plus every call since;
    held is the worst-case reserve of the calls in flight."""

    def __init__(self, stop, spent):
        self.stop, self.spent, self.held, self.lock = stop, spent, 0.0, threading.Lock()

    def take(self, reserve):
        with self.lock:
            if not may_call(self.spent + self.held, reserve, self.stop):
                return False
            self.held += reserve
            return True

    def done(self, reserve, cost):
        with self.lock:
            self.held -= reserve
            self.spent += cost


def may_call(spent, reserve, stop):
    """A call may start only if what is spent (with the reserves in flight) plus its own reserve fits under the stop."""
    return spent + reserve <= stop


def reserve_usd(model, prompt_chars, max_tokens, llm):
    """The worst case of one call: every character of its prompt at CHARS_PER_TOKEN a token, written to the cache at
    the 5-minute price where that is dearer than plain input, and max_tokens of output."""
    p = llm.prices()["models"][model]
    return (prompt_chars / CHARS_PER_TOKEN * max(p["input"], p.get("cache_write_5m", 0)) + max_tokens * p["output"]) / 1e6


def session_spent(llm, extra=()):
    total = llm.session_total(SESSION)
    mine = os.path.normcase(os.path.abspath(llm.ledger_path()))
    for path in extra:
        if os.path.exists(path) and os.path.normcase(os.path.abspath(path)) != mine:
            d = ip.read_series(path, llm.COLS)
            total += float(pd.to_numeric(d[d["session"] == SESSION]["usd"], errors="coerce").fillna(0).sum())
    return total


# ---------------------------------------------------------------- the source text of a read
def release_text(r, work, state, log):
    """(text, why not) of a news release, fetched once by a plain request and saved raw. One request a second a host."""
    import reads as R
    url = r["source_url"]
    host = urlparse(url).netloc.lower()
    raw_dir = os.path.join(work, "raw")
    os.makedirs(raw_dir, exist_ok=True)
    saved = os.path.join(raw_dir, safe(r["event_id"]) + (".pdf" if url.lower().endswith(".pdf") else ".html"))
    man = os.path.join(work, "release_manifest.csv")
    if host not in RELEASE_HOSTS:
        return None, f"not requested: {host} is not the site of a federal regulator, a state commission or a grid operator"
    if "@" in url:
        return None, "not requested: the address holds an e-mail address"
    content = None
    if os.path.exists(saved):
        with open(saved, "rb") as f:
            content = f.read()
    else:
        with state["lock"]:
            wait = 1.0 - (time.time() - state["last"].get(host, 0))
            if wait > 0:
                time.sleep(wait)
            state["last"][host] = time.time()
            state["requests"] += 1
        status, err, body = "", "", b""
        try:
            resp = requests.get(url, headers=UA, timeout=90)
            status, body = resp.status_code, resp.content
        except Exception as exc:
            err = ip.redact(repr(exc))[:200]
        with state["lock"]:
            new = not os.path.exists(man)
            with open(man, "a", encoding="utf-8", newline="") as f:
                w = csv.writer(f)
                if new:
                    w.writerow(["event_id", "url", "status", "bytes", "sha256", "retrieved_at", "error"])
                w.writerow([r["event_id"], url, status, len(body), hashlib.sha256(body).hexdigest() if body else "",
                            now_iso(), err])
            state["bytes"] += len(body)
        if status != 200:
            return None, f"source not reachable: {'HTTP ' + str(status) if status else err}"
        with open(saved, "wb") as f:
            f.write(body)
        content = body
    if saved.endswith(".pdf") or content[:5] == b"%PDF-":
        import pdfplumber
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            body = re.sub(r"\s+", " ", " ".join((p.extract_text() or "") for p in pdf.pages[:6]))
    else:
        body = R.html_text(content.decode("utf-8", "replace"))
        k = body.find(r["title"][:40])
        body = body[k:] if k >= 0 else body
    if len(body.strip()) < 200:
        return None, "source not reachable: the page holds no text a plain request can read"
    return (r["title"] + ". " + body)[:R.MAX_TEXT], ""


def read_text(r, text_dir, work, state, log):
    """(text, why not): the text an impact read is made from."""
    import reads as R
    if r["fr_document_number"]:
        path = os.path.join(text_dir, safe(r["fr_document_number"]) + ".txt")
        if not os.path.exists(path):
            return None, "source not reachable: the printed text is not held (" + (r.get("text_status") or "not read") + ")"
        with open(path, "rb") as f:
            return R.register_text(r["title"], f.read().decode("utf-8", "replace")), ""
    return release_text(r, work, state, log)


# ---------------------------------------------------------------- the calls
def call_read(client, model, r, text, llm):
    import reads as R
    msg = (f"Action: {r['agency']} {r['action_type'].replace('_', ' ')}, {r['event_date']}: {r['title']}\n"
           f"Sectors to choose from: {', '.join(R.SECTORS)}\n\nSource text:\n{text}")
    resp = client.messages.create(
        model=model, max_tokens=READ_MAX_TOKENS, messages=[{"role": "user", "content": msg}],
        system=[{"type": "text", "text": R.SYSTEM, "cache_control": {"type": "ephemeral"}}],
        output_config={"effort": "low", "format": {"type": "json_schema", "schema": R.SCHEMA}})
    n = llm.usage_numbers(resp.usage)
    return {"stop_reason": resp.stop_reason, "usage": n, "usd": llm.usd(model, n) or 0.0,
            "answer": next((b.text for b in resp.content if b.type == "text"), "")}


def call_score(client, model, items, llm):
    resp = client.messages.create(
        model=model, max_tokens=SCORE_MAX_TOKENS,
        system=[{"type": "text", "text": NEWS["SYSTEM"] + NEWS["POLICY_NOTE"], "cache_control": {"type": "ephemeral"}}],
        output_config={"effort": "low", "format": {"type": "json_schema", "schema": NEWS["SCHEMA"]}},
        messages=[{"role": "user", "content": json.dumps({"stories": items}, ensure_ascii=False)}])
    n = llm.usage_numbers(resp.usage)
    return {"stop_reason": resp.stop_reason, "usage": n, "usd": llm.usd(model, n) or 0.0,
            "answer": next((b.text for b in resp.content if b.type == "text"), "")}


NEWS = {}


def load_modules():
    """The policy scorer (warehouse/policy/score.py) and the news scorer it borrows from (warehouse/news/score.py)
    are both named score: each is loaded from its own file."""
    import importlib.util
    out = {}
    for name, path in (("policy_score", os.path.join(HERE, "score.py")),
                       ("news_score", os.path.join(ROOT, "warehouse", "news", "score.py"))):
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        out[name] = mod
    NEWS["SYSTEM"], NEWS["SCHEMA"], NEWS["nodash"] = out["news_score"].SYSTEM, out["news_score"].SCHEMA, out["news_score"].nodash
    NEWS["pick_model"] = out["news_score"].pick_model
    NEWS["POLICY_NOTE"] = out["policy_score"].POLICY_NOTE
    return out["policy_score"]


def save_answer(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path + ".tmp", "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    os.replace(path + ".tmp", path)


def load_answers(folder):
    out = {}
    if os.path.isdir(folder):
        for fn in sorted(os.listdir(folder)):
            if fn.endswith(".json"):
                with open(os.path.join(folder, fn), encoding="utf-8") as f:
                    a = json.load(f)
                out[a["key"]] = a
    return out


# ---------------------------------------------------------------- what is to do
def score_groups(actions):
    """(title-only Register actions, the other Register actions), each newest first. A news release has no printed
    text held: it is in neither (its score is marked not rechecked)."""
    fr = actions[(actions["fr_document_number"] != "") & (actions["significance"] != "")]
    fr = fr.sort_values(["event_date", "event_id"], ascending=[False, True])
    return fr[fr["abstract"] == ""], fr[fr["abstract"] != ""]


def batches_of(frame, S):
    """Batches of BATCH actions whose printed text is read, in the frame's order: [(key, [items], [ids])]."""
    rows = [r for r in frame.to_dict("records") if r.get("text_status") == "read"]
    out = []
    for i in range(0, len(rows), BATCH):
        part = rows[i:i + BATCH]
        items = [S.item_of(r) for r in part]
        key = hashlib.sha256(json.dumps(items, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()[:16]
        out.append((key, items, [r["event_id"] for r in part]))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW session 157: recheck the model's reads and scores against the source text")
    ap.add_argument("--actions", required=True, help="policy_actions.csv with the printed text's columns (a trial's)")
    ap.add_argument("--reads", required=True, help="policy_reads.csv as held")
    ap.add_argument("--evidence", help="policy_reads_evidence.csv as held (for --build)")
    ap.add_argument("--text-dir", required=True, help="the store of printed texts by document number")
    ap.add_argument("--work", required=True, help="answers, texts, fetched releases and the built tables go here")
    ap.add_argument("--ledger-dir", required=True, help="the cost ledger's directory (a working copy's own)")
    ap.add_argument("--also-ledger", action="append", default=[], help="another ledger whose session rows count as spent")
    ap.add_argument("--stop-usd", type=float, default=5.50)
    ap.add_argument("--step", choices=["reads", "title", "rest"])
    ap.add_argument("--limit", type=int, help="at most this many calls")
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--build", action="store_true")
    args = ap.parse_args(argv)
    work = os.path.abspath(args.work)
    os.makedirs(work, exist_ok=True)
    os.environ["ERW_SESSION"] = SESSION
    ip.set_out_dir(os.path.abspath(args.ledger_dir))   # the ledger, its registry line and this run's log: not warehouse/output
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"policy_recheck_{run_id}.log"))
    import llm
    S = load_modules()
    actions = read_events(args.actions)
    reads = read_events(args.reads)
    by = actions.set_index("event_id")
    if args.build:
        return build(args, actions, reads, work, S, log)
    title, rest = score_groups(actions)
    read_rows = [dict(by.loc[i].to_dict(), event_id=i) for i in
                 reads.sort_values(["event_date", "action_event_id"], ascending=[False, True])["action_event_id"] if i in by.index]
    a_reads, a_scores = load_answers(os.path.join(work, "answers", "reads")), load_answers(os.path.join(work, "answers", "scores"))
    spent0 = session_spent(llm, args.also_ledger)
    model = "claude-sonnet-5-5"
    if args.plan or not args.step:
        import reads as R
        p = llm.prices()["models"][model]
        r_res = [reserve_usd(model, len(R.SYSTEM) + len(json.dumps(R.SCHEMA)) + R.MAX_TEXT + 400, READ_MAX_TOKENS, llm)
                 for r in read_rows if r["event_id"] not in a_reads]
        tb, rb = batches_of(title, S), batches_of(rest, S)
        s_res = lambda bs: [reserve_usd(model, len(NEWS["SYSTEM"]) + len(S.POLICY_NOTE) + len(json.dumps(NEWS["SCHEMA"]))
                                        + len(json.dumps(items)), SCORE_MAX_TOKENS, llm) for k, items, _ in bs if k not in a_scores]
        print(f"plan at {now_iso()}: model {model} (USD {p['input']} a million input tokens, {p['output']} output); "
              f"session {SESSION} spent so far USD {spent0:.4f}; stop USD {args.stop_usd:.2f}")
        print(f"  reads: {len(read_rows)} held with their action in the table, {len(a_reads)} answered; "
              f"worst-case reserve of the rest USD {sum(r_res):.2f} ({max(r_res) if r_res else 0:.4f} a call)")
        for name, frame, bs in (("title", title, tb), ("rest", rest, rb)):
            res = s_res(bs)
            n_text = sum(len(ids) for _, _, ids in bs)
            print(f"  {name}: {len(frame)} Register actions, {n_text} with their printed text read, in {len(bs)} batches of "
                  f"{BATCH}; {sum(1 for k, _, _ in bs if k in a_scores)} batches answered; worst-case reserve of the rest "
                  f"USD {sum(res):.2f} ({max(res) if res else 0:.4f} a call)")
        log.close()
        return 0
    os.environ.setdefault("ERW_SPEND_CAP_USD", f"{args.stop_usd:.2f}")
    client = llm.client("policy_recheck_" + args.step, log)
    model = NEWS["pick_model"](client, log)
    budget = Budget(args.stop_usd, spent0)
    done = {"calls": 0, "usd": 0.0, "stopped": "", "skipped": 0}
    state = {"lock": threading.Lock(), "last": {}, "requests": 0, "bytes": 0}
    text_dir = os.path.abspath(args.text_dir)

    def one_read(r):
        import reads as R
        text, why = read_text(r, text_dir, work, state, log)
        if text is None:
            save_answer(os.path.join(work, "no_text", safe(r["event_id"]) + ".json"), {"key": r["event_id"], "why": why, "at": now_iso()})
            return 0.0, f"{r['event_id']}: {why}"
        tfile = os.path.join(work, "texts", safe(r["event_id"]) + ".txt")
        os.makedirs(os.path.dirname(tfile), exist_ok=True)
        with open(tfile, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        res = reserve_usd(model, len(R.SYSTEM) + len(json.dumps(R.SCHEMA)) + len(text) + 400, READ_MAX_TOKENS, llm)
        if not budget.take(res):
            return None, f"stopped before {r['event_id']}: spent USD {budget.spent:.4f} with USD {budget.held:.4f} in flight; a reserve of USD {res:.4f} would pass the stop USD {args.stop_usd:.2f}"
        cost = 0.0
        try:
            a = call_read(client, model, r, text, llm)
            cost = a["usd"]
            a.update(key=r["event_id"], at=now_iso(), model=model, text_file=tfile,
                     text_sha256=hashlib.sha256(text.encode("utf-8")).hexdigest())
            save_answer(os.path.join(work, "answers", "reads", safe(r["event_id"]) + ".json"), a)   # paid: saved first
        finally:
            budget.done(res, cost)
        return cost, f"{r['event_id']}: USD {cost:.4f} (in {a['usage']['input']}, cache read {a['usage']['cache_read']}, written {a['usage']['cache_write']}, out {a['usage']['output']})"

    def one_batch(b):
        key, items, ids = b
        res = reserve_usd(model, len(NEWS["SYSTEM"]) + len(S.POLICY_NOTE) + len(json.dumps(NEWS["SCHEMA"])) + len(json.dumps(items)),
                          SCORE_MAX_TOKENS, llm)
        if not budget.take(res):
            return None, f"stopped before batch {key}: spent USD {budget.spent:.4f} with USD {budget.held:.4f} in flight; a reserve of USD {res:.4f} would pass the stop USD {args.stop_usd:.2f}"
        cost = 0.0
        try:
            a = call_score(client, model, items, llm)
            cost = a["usd"]
            a.update(key=key, at=now_iso(), model=model, ids=ids, items=items, kind=args.step)
            save_answer(os.path.join(work, "answers", "scores", key + ".json"), a)   # paid: saved first
        finally:
            budget.done(res, cost)
        return cost, f"batch {key} ({len(ids)} actions): USD {cost:.4f} (in {a['usage']['input']}, cache read {a['usage']['cache_read']}, written {a['usage']['cache_write']}, out {a['usage']['output']})"

    if args.step == "reads":
        todo = [r for r in read_rows if r["event_id"] not in a_reads
                and not os.path.exists(os.path.join(work, "no_text", safe(r["event_id"]) + ".json"))]
        fn = one_read
    else:
        todo = [b for b in batches_of(title if args.step == "title" else rest, S) if b[0] not in a_scores]
        fn = one_batch
    if args.limit:
        todo = todo[:args.limit]
    log(f"{args.step}: {len(todo)} to do; session spent so far USD {spent0:.4f}; stop USD {args.stop_usd:.2f}; model {model}")
    # the first call alone (it writes the prompt cache), then WORKERS at a time
    first, others = todo[:1], todo[1:]
    for group, workers in ((first, 1), (others, WORKERS)):
        if done["stopped"] or not group:
            continue
        with cf.ThreadPoolExecutor(workers) as pool:
            for cost, line in pool.map(lambda x: guarded(fn, x, log), group):
                if cost is None:
                    done["stopped"] = done["stopped"] or line
                    continue
                done["calls"] += 1 if cost else 0
                done["usd"] += cost
                log("  " + line)
    total = session_spent(llm, args.also_ledger)
    line = (f"{args.step}: {done['calls']} calls, USD {done['usd']:.4f} this run; session {SESSION} in the ledger USD {total:.4f}; "
            f"releases requested {state['requests']} ({state['bytes']} bytes)" + (f"; {done['stopped']}" if done["stopped"] else ""))
    log(line)
    print(line)
    log.close()
    return 0


def guarded(fn, x, log):
    try:
        return fn(x)
    except Exception as exc:   # a failed call is logged and the batch goes on; what was paid is in the ledger
        return 0.0, f"FAILED: {ip.redact(repr(exc))[:300]}"


# ---------------------------------------------------------------- the tables, from the saved answers (no call)
def build(args, actions, reads, work, S, log):
    import reads as R
    by = actions.set_index("event_id")
    a_reads, a_scores = load_answers(os.path.join(work, "answers", "reads")), load_answers(os.path.join(work, "answers", "scores"))
    no_text = load_answers(os.path.join(work, "no_text"))
    out_dir = os.path.join(work, "out")
    os.makedirs(out_dir, exist_ok=True)
    changes, summary = [], {"built_at_utc": now_iso(), "session": SESSION}

    # ---- the reads
    new_rows, evid, kinds = [], [], {"rechecked": 0, "not rechecked": 0, "source not reachable": 0}
    unread = []
    for old in reads.to_dict("records"):
        aid = old["action_event_id"]
        row = dict(old)
        a = a_reads.get(aid)
        out = None
        if a and a.get("stop_reason") == "end_turn":
            try:
                out = json.loads(a["answer"])
            except ValueError:
                unread.append(aid)
        elif a:
            unread.append(aid)
        if out is not None and aid in by.index:
            r = by.loc[aid]
            with open(a["text_file"], encoding="utf-8") as f:
                text = f.read()
            fixed = R.enforce(out, text)
            kept, dropped = [], []
            for name in R.FIELDS:
                why = R.check_field(name, out[name], text, fixed)
                (dropped if why else kept).append(name if not why else f"{name} ({'; '.join(why)})")
            k = set(kept)
            wa, dr = out["who_affected"], out["direction"]
            row.update({
                "title": r["title"], "event_date": r["event_date"],
                "what_changes": out["what_changes"]["text"].replace(R.EM, ",") if "what_changes" in k else "",
                "affected_sectors": ";".join(wa["sectors"]) if "who_affected" in k else "",
                "affected_isos": ";".join(wa["isos"]) if "who_affected" in k else "",
                "affected_states": ";".join(s for s in wa["states"] if re.fullmatch(r"[A-Z]{2}", s)) if "who_affected" in k else "",
                **{f"direction_{d}": dr[d] if "direction" in k else "" for d in ("supply", "demand", "prices", "buildout")},
                "timeline": out["timeline"]["text"].replace(R.EM, ",") if "timeline" in k else "",
                "plain_read": out["plain_read"]["text"].replace(R.EM, ",") if "plain_read" in k else "",
                "fields_kept": ";".join(sorted(k)), "fields_dropped": " | ".join(dropped + fixed),
                "model_id": a["model"], "read_at": a["at"], "recheck": "rechecked", "rechecked_at": a["at"]})
            rid = old["event_id"]
            for name in sorted(k):
                for s_ in out[name]["spans"]:
                    evid.append({"event_id": f"{rid}#{name}#{len(evid)}", "event_date": row["event_date"],
                                 "event_type": "policy_read_evidence", "parties": "", "entity_ids": "", "mw": "", "price": "",
                                 "currency": "", "status": "", "source": "erw:policy_reads", "source_url": old["source_url"],
                                 "read_id": rid, "field": name, "span": s_.replace(R.EM, "-"),
                                 "source_text_file": "runs/session157/recheck/texts/" + os.path.basename(a["text_file"])})
            kinds["rechecked"] += 1
            for f_ in READ_FIELDS:
                if old.get(f_, "") != row[f_]:
                    changes.append({"kind": "read", "event_id": aid, "field": f_, "before": old.get(f_, ""), "after": row[f_],
                                    "rechecked_at": a["at"]})
        else:
            why = (no_text.get(aid) or {}).get("why", "")
            mark = "source not reachable" if why.startswith("source not reachable") else "not rechecked"
            row.update({"recheck": mark, "rechecked_at": ""})
            kinds[mark] += 1
        new_rows.append(row)
    table = pd.DataFrame(new_rows)[R.READ_COLS]
    rp = os.path.join(out_dir, "policy_reads.csv")
    with open(rp, "w", encoding="utf-8", newline="") as f:
        for ln in head_lines(args.reads):
            if not ln.startswith("# Session 157"):
                f.write(ln)
        f.write(f"# Session 157: {kinds['rechecked']} of {len(table)} reads made again from the source text by "
                f"warehouse/policy/recheck.py (recheck, rechecked_at); {kinds['not rechecked']} not rechecked, "
                f"{kinds['source not reachable']} whose source was not reachable: those rows are as they were.\n")
        table.to_csv(f, index=False, lineterminator="\n")
    summary["reads"] = dict(kinds, rows=len(table), answers_not_readable=unread,
                            what_changes_blank_before=int((reads["what_changes"] == "").sum()),
                            what_changes_blank_after=int((table["what_changes"] == "").sum()),
                            plain_read_blank_before=int((reads["plain_read"] == "").sum()),
                            plain_read_blank_after=int((table["plain_read"] == "").sum()),
                            why_not=sorted({(v.get("why") or "")[:120] for v in no_text.values()}))
    if args.evidence and os.path.exists(args.evidence):
        ev_old = read_events(args.evidence)
        redone = {r["event_id"] for r in new_rows if r["recheck"] == "rechecked"}
        ev_new = pd.concat([ev_old[~ev_old["read_id"].isin(redone)], pd.DataFrame(evid, columns=R.EVID_COLS)], ignore_index=True)
        ev_new = ev_new.drop_duplicates("event_id", keep="last")
        with open(os.path.join(out_dir, "policy_reads_evidence.csv"), "w", encoding="utf-8", newline="") as f:
            f.writelines(head_lines(args.evidence))
            ev_new[R.EVID_COLS].to_csv(f, index=False, lineterminator="\n")
        summary["reads"]["evidence_rows"] = len(ev_new)

    # ---- the scores
    old_scores = pd.read_csv(SCORES, dtype=str, keep_default_na=False).drop_duplicates("event_id", keep="last")
    for c in S.SCORE_COLS:
        if c not in old_scores.columns:
            old_scores[c] = ""
    sc = {r["event_id"]: r for r in old_scores.to_dict("records")}
    got, bad_batches = {}, []
    for key, a in sorted(a_scores.items(), key=lambda kv: kv[1]["at"]):
        if a.get("stop_reason") != "end_turn":
            bad_batches.append(key)
            continue
        try:
            res = S.first_list(json.loads(a["answer"]))
        except (ValueError, RuntimeError):
            bad_batches.append(key)
            continue
        for x in res:
            if x.get("id") in a["ids"]:
                got[x["id"]] = (str(int(x["significance"])), x["sector"], NEWS["nodash"](x.get("one_line_why") or ""),
                                a["model"], a["at"], a.get("kind", ""))
    title, rest = score_groups(actions)
    kind_of = {i: "title" for i in title["event_id"]}
    kind_of.update({i: "rest" for i in rest["event_id"]})
    marks = {"rechecked": 0, "not rechecked": 0, "source not reachable": 0}
    by_kind = {"title": {"rechecked": 0, "not rechecked": 0, "source not reachable": 0, "changed": 0},
               "rest": {"rechecked": 0, "not rechecked": 0, "source not reachable": 0, "changed": 0},
               "news release": {"rechecked": 0, "not rechecked": 0, "source not reachable": 0, "changed": 0}}
    moved = {"significance": 0, "sector": 0, "why": 0, "to_5_or_more": 0, "below_5": 0}
    for r in actions.to_dict("records"):
        i = r["event_id"]
        old = sc.get(i)
        if old is None or old.get("significance", "") == "":
            continue   # never scored: the daily scorer scores it, on the source text
        kind = kind_of.get(i, "news release")
        if i in got:
            sig, sector, why, model, at, _ = got[i]
            row = dict(old, significance=sig, sector=sector, why=why, model_id=model, scored_at=at, model_recheck="rechecked",
                       model_rechecked_at=at)
            changed = False
            for f_ in ("significance", "sector", "why"):
                if old.get(f_, "") != row[f_]:
                    changes.append({"kind": "score", "event_id": i, "field": f_, "before": old.get(f_, ""), "after": row[f_],
                                    "rechecked_at": at})
                    moved[f_] += 1
                    changed = changed or f_ != "why"
            try:
                a_, b_ = int(old["significance"]), int(sig)
                moved["to_5_or_more"] += a_ < 5 <= b_
                moved["below_5"] += b_ < 5 <= a_
            except ValueError:
                pass
            by_kind[kind]["changed"] += changed
            mark = "rechecked"
        else:
            mark = "source not reachable" if (r.get("text_status") or "").startswith("not reachable") else "not rechecked"
            row = dict(old, model_recheck=mark, model_rechecked_at="")
        marks[mark] += 1
        by_kind[kind][mark] += 1
        sc[i] = row
    allsc = pd.DataFrame(list(sc.values()))[["event_id"] + S.SCORE_COLS]
    allsc.to_csv(os.path.join(out_dir, "scores.csv"), index=False, lineterminator="\n")
    summary["scores"] = dict(marks, by_kind=by_kind, moved=moved, batches=len(a_scores), batches_not_readable=bad_batches,
                             scores_file_rows=len(allsc))
    pd.DataFrame(changes, columns=["kind", "event_id", "field", "before", "after", "rechecked_at"]).to_csv(
        os.path.join(out_dir, "recheck_s157_changes.csv"), index=False, lineterminator="\n")
    summary["changes_rows"] = len(changes)
    with open(os.path.join(out_dir, "recheck_s157_summary.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(summary, f, indent=1, ensure_ascii=False)
    print(json.dumps(summary, indent=1, ensure_ascii=False))
    log.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
