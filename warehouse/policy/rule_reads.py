#!/usr/bin/env python3
"""One-line reads of the rules in motion for large loads, written by a model and marked as a model's (session 154).

Energy Research Warehouse (ERW). For each proceeding or order in motion of large_load_rules (and each tagged federal
action held that has an abstract and no read in policy_reads), a model writes ONE line: what the action would change
for a large load seeking power. The line is a model's read and is marked so in the data (read_by is always "model"
on a page; model_id here) and on the page.

What the model is given, and nothing else: the row's own sentence and the saved text of the document around it
(BEFORE characters before the sentence and AFTER after it, white space normalized), under one heading line made of
the row's own fields (regulator, docket number, kind, document date, title). For a federal action held: its title
and abstract as the Federal Register prints them.

What code checks before a line is kept (check_read):
    - one line, at most MAX_CHARS characters, not empty, no em dash;
    - every number in the line stands in the text given (the same digits, commas aside), and every number written as
      a word (two, ten, hundred ...) stands in that text as the same word or as its digits;
    - none of the words the block never shows (zoning, permit, city council, county board).
A line that fails is not kept: the row has no read ("no read yet" on the page), the answer paid for is kept beside
the table (answers/<id>.json) with the reason, and it is not asked again unless --again names it.

Spend. Every call goes through the cost ledger (warehouse/llm.py) as the session in ERW_SESSION. The stop sits BEFORE
each call: a call starts only if the session's ledger total, plus a worst-case reserve for it (its prompt at
CHARS_PER_TOKEN characters a token and max_tokens of output, at the model's configured prices), fits under
--stop-usd. ERW_SPEND_CAP_USD in the environment is the ledger's own second stop. A paid answer is never discarded.

    python warehouse/policy/rule_reads.py --in-dir TRIAL --in-dir MAIN --out-dir TRIAL --raw-base C:/.../erw --plan
    python warehouse/policy/rule_reads.py ... --limit 1            # measure one
    python warehouse/policy/rule_reads.py ... --stop-usd 3.70      # the batch, newest first
    --ledger-dir DIR   keep the cost ledger under DIR (a working copy's own warehouse/output) instead of --out-dir
    python warehouse/policy/rule_reads.py --no-call                # the table from the saved answers; nothing is spent

Writes large_load_rule_reads (events shape, event_type rule_read; one row a kept line). License: public: the lines
are the ERW's own. A line about a row of large_load_rules_internal (a regulator whose terms restrict copying or were
not read) must not quote the document: code rejects a line that holds a run of more than QUOTE_WORDS consecutive words
of the text the model was given.
"""

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
sys.path.insert(0, os.path.join(ROOT, "warehouse"))
import iso_prices as ip  # noqa: E402
import rules_in_motion as rim  # noqa: E402

NAME, RULES, TAGS, ACTIONS = "large_load_rule_reads", "large_load_rules", "policy_action_tags", "policy_actions"
SOURCE = "erw:large_load_rule_reads"
METHOD = "docs/methods/datacenter_cost.md"
METHOD_URL = "https://github.com/SamuelEnrique/erw/blob/main/" + METHOD
BEFORE, AFTER = 2500, 3500
MAX_CHARS = 320   # 240 at first; raised after the first 27 answers: an order with several conditions ran past it. The other checks are unchanged
MAX_TOKENS = 700
QUOTE_WORDS = 5   # a line about a regulator that restricts copying holds no run of more than this many of its words
CHARS_PER_TOKEN = 2.5   # a low figure on purpose: the reserve must be a worst case
SYSTEM_TOKENS = 700
EM = chr(0x2014)
EVENTS = ["event_id", "event_date", "event_type", "parties", "entity_ids", "mw", "price", "currency", "status", "source",
          "source_url"]
COLS = EVENTS + ["rule_event_id", "regulator", "docket_number", "row_kind", "read", "read_from", "text_chars",
                 "text_sha256", "answer_file", "model_id", "read_at"]
SYSTEM = """You read one excerpt of a US energy regulator's own document (an order, a notice, a rule or a docket's opening
document) for the Energy Research Warehouse (ERW) and write ONE line saying what it would change for a large load,
such as a datacenter, that is seeking power from the grid: when it can be connected, on what terms, or at what cost.

Rules:
- Use only the excerpt given. The sentence marked SENTENCE is the one that states what the document does; the text
  around it is the same document. Write nothing the excerpt does not support.
- One plain sentence, at most 30 words, present tense, for a reader who is not a lawyer. Say what changes and for
  whom. If the action is a proposal or an open proceeding, say it would or may, not that it does.
- No number, date, amount, threshold or percentage that is not written in the excerpt, and write each exactly as the
  excerpt writes it.
- Write in your own words: never copy more than five consecutive words from the excerpt.
- No advice, no opinion, no hype, no em dashes. Do not use the words zoning, permit, city council or county board.
- If the excerpt does not support any line about large loads seeking power, return an empty string.
Return a JSON object with one field, "read"."""
SCHEMA = {"type": "object", "additionalProperties": False, "required": ["read"],
          "properties": {"read": {"type": "string"}}}
NUM = re.compile(r"\d[\d,]*(?:\.\d+)?")
WORD_NUMBERS = {"two": "2", "three": "3", "four": "4", "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9",
                "ten": "10", "eleven": "11", "twelve": "12", "thirteen": "13", "fourteen": "14", "fifteen": "15",
                "sixteen": "16", "seventeen": "17", "eighteen": "18", "nineteen": "19", "twenty": "20", "thirty": "30",
                "forty": "40", "fifty": "50", "sixty": "60", "seventy": "70", "eighty": "80", "ninety": "90",
                "hundred": "100", "thousand": "1000", "million": "1000000", "billion": "1000000000",
                "half": None, "double": None, "triple": None, "twice": None, "dozen": None}
BLOCK_WORDS = rim.MUNICIPAL_WORDS


def norm(s):
    return " ".join(str(s).split())


def num_tokens(text):
    return {m.group(0).replace(",", "").rstrip(".") for m in NUM.finditer(text)}


def words_of(text):
    return re.findall(r"[a-z0-9]+(?:'[a-z]+)?", text.lower().replace(chr(0x2019), "'"))


def copied_run(line, given, n=None):
    """The first run of more than QUOTE_WORDS consecutive words of the line that stands in the text given, or ''."""
    n = (QUOTE_WORDS + 1) if n is None else n
    lw = words_of(line)
    hay = " " + " ".join(words_of(given)) + " "
    for i in range(len(lw) - n + 1):
        run = " ".join(lw[i:i + n])
        if " " + run + " " in hay:
            return run
    return ""


def check_read(line, given, no_quote=False):
    """The reasons a line is not kept; [] when it is. given is the whole text the model was shown. no_quote: the row's
    regulator restricts copying (or its terms were not read), so the line must not quote the document: no run of more
    than QUOTE_WORDS consecutive words of the text given."""
    why = []
    if not line.strip():
        return ["the model returned no line (the excerpt supports none)"]
    if "\n" in line.strip():
        why.append("more than one line")
    if len(line.strip()) > MAX_CHARS:
        why.append(f"longer than {MAX_CHARS} characters")
    if EM in line:
        why.append("an em dash")
    pool = num_tokens(given)
    bad = sorted(n for n in num_tokens(line) if n not in pool)
    if bad:
        why.append(f"numbers not in the text given: {bad}")
    low = given.lower()
    for m in re.finditer(r"[A-Za-z]+", line):
        w = m.group(0).lower()
        if w in WORD_NUMBERS:
            digits = WORD_NUMBERS[w]
            if not re.search(r"(?<![a-z])" + w + r"(?![a-z])", low) and not (digits and digits in pool):
                why.append(f"a number in words not in the text given: {w}")
    hit = [w for w in BLOCK_WORDS if w in line.lower()]
    if hit:
        why.append(f"a word the block never shows: {hit}")
    if no_quote:
        run = copied_run(line, given)
        if run:
            why.append(f"quotes the document (more than {QUOTE_WORDS} consecutive words of it): '{run}'")
    return why


def excerpt(whole, sentence):
    """(the text given around the sentence, or None when the sentence is not in the text)."""
    at = whole.find(sentence)
    if at < 0:
        return None
    a, b = max(0, at - BEFORE), min(len(whole), at + len(sentence) + AFTER)
    return whole[a:at] + "\n\nSENTENCE: " + sentence + "\n\n" + whole[at + len(sentence):b]


def candidates(dirs, raw_base, today, log):
    """The rows to read, newest first: [{id, date, url, regulator, docket, kind, heading, given, read_from, sha}]."""
    cutoff = rim.months_back(today, rim.WINDOW_MONTHS)
    out = []
    for name in rim.TABLES:
        p = rim.find(name, dirs)
        if not p:
            continue
        t, head = rim.read_events(p)
        internal = rim.license_of(head) != "public"
        for a in t.to_dict("records"):
            kind, cls, day = a["row_kind"], a["status_class"], a["event_date"][:10]
            if not rim.in_motion(a, cutoff):
                continue
            path = os.path.join(raw_base, a["text_file"])
            if not os.path.exists(path):
                log(f"  {a['event_id']}: its saved text is not there ({path}): no read")
                continue
            with open(path, encoding="utf-8", errors="replace") as f:
                raw = f.read()
            if re.search(r"(?i)<html|<body|<div", raw[:4000]):
                import large_load_rules as llr
                raw = llr.html_text(raw)
            body = excerpt(norm(raw), a["sentence"])
            if body is None:
                log(f"  {a['event_id']}: its sentence is not in its saved text: no read")
                continue
            heading = (f"{a['regulator']}, docket {a['docket_number']}, {kind}, document dated {day}: "
                       f"{a['document_title'] or a['proceeding_title']}")
            out.append({"id": a["event_id"], "date": day, "url": a["source_url"], "regulator": a["regulator"],
                        "docket": a["docket_number"], "kind": kind, "heading": heading, "given": body,
                        "status_class": cls, "table": name,
                        "no_quote": internal and a["regulator"] not in rim.SHOW_SENTENCE_REGULATORS,
                        "read_from": f"the document's own sentence and the saved text around it "
                                     f"({len(body):,} characters of the document), nothing else"})
    pa, pt = rim.find(ACTIONS, dirs), rim.find(TAGS, dirs)
    if pa and pt:
        acts, _ = rim.read_events(pa)
        tags, _ = rim.read_events(pt)
        have = set()
        pr = rim.find("policy_reads", dirs)
        if pr:
            r, _ = rim.read_events(pr)
            have = set(r.loc[r["plain_read"].str.strip() != "", "action_event_id"])
        by = acts.set_index("event_id")
        for aid in dict.fromkeys(tags["action_event_id"]):
            a = by.loc[aid]
            if a["agency"] not in rim.FEDERAL or aid in have or not a["abstract"].strip():
                continue
            if a["event_date"][:10] < cutoff.isoformat():
                continue
            body = "SENTENCE: " + norm(a["title"]) + "\n\n" + norm(a["abstract"])
            out.append({"id": aid, "date": a["event_date"][:10], "url": a["source_url"],
                        "regulator": rim.AGENCY_NAMES[a["agency"]], "docket": rim.docket_words(a.to_dict()),
                        "kind": "federal action", "table": ACTIONS, "no_quote": False, "status_class": rim.ACTION_CLASS.get(a["action_type"], "not stated"),
                        "heading": f"{rim.AGENCY_NAMES[a['agency']]}, {a['action_type'].replace('_', ' ')}, published {a['event_date'][:10]}",
                        "given": body,
                        "read_from": "the action's title and abstract as the Federal Register prints them, nothing else"})
    for c in out:
        c["sha"] = hashlib.sha256(c["given"].encode("utf-8")).hexdigest()
    return sorted(out, key=lambda c: (c["date"], c["id"]), reverse=True)


def safe(i):
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", i)


def reserve_usd(model, prompt_chars, llm):
    p = llm.price_of(model)
    if p is None:
        raise RuntimeError(f"model {model} has no configured price: no call is made")
    return ((prompt_chars / CHARS_PER_TOKEN + SYSTEM_TOKENS) * p["input"] + MAX_TOKENS * p["output"]) / 1e6


def may_call(spent, reserve, stop):
    """The stop, BEFORE a call: a call may start only if what is spent plus its worst-case reserve fits under the stop."""
    return spent + reserve <= stop


def session_spent(llm, extra_ledgers):
    """The session's total in the ledger this run writes, plus the same session's rows in any other ledger named
    (the main copy's, read only), so that no spend recorded anywhere is missed."""
    total = llm.session_total()
    mine = os.path.normcase(os.path.abspath(llm.ledger_path()))
    for path in extra_ledgers:
        if path and os.path.exists(path) and os.path.normcase(os.path.abspath(path)) != mine:
            df = ip.read_series(path, llm.COLS)
            df = df[df["session"] == llm.session()]
            total += float(pd.to_numeric(df["usd"], errors="coerce").fillna(0).sum())
    return total


def table_from_answers(ans_dir, cands, lic, log):
    """The kept lines of every saved answer whose text is still the row's text (a changed document is read again).
    Each saved line is checked again here against the text the model was given (check_read), so the table always
    holds exactly the lines the code's checks pass today, and a saved answer is never asked for twice."""
    by = {c["id"]: c for c in cands}
    rows = []
    for n in sorted(os.listdir(ans_dir)) if os.path.isdir(ans_dir) else []:
        if not n.endswith(".json"):
            continue
        with open(os.path.join(ans_dir, n), encoding="utf-8") as f:
            a = json.load(f)
        c = by.get(a["id"])
        if not c or a["text_sha256"] != c["sha"]:
            continue
        why = check_read(a.get("read", ""), c["given"], c["no_quote"])
        if why:
            log(f"  {a['id']}: saved line NOT kept: {'; '.join(why)}")
            continue
        rows.append({"event_id": "ruleread:" + c["id"], "event_date": c["date"], "event_type": "rule_read",
                     "parties": c["regulator"], "entity_ids": "", "mw": "", "price": "", "currency": "", "status": "",
                     "source": SOURCE, "source_url": c["url"], "rule_event_id": c["id"], "regulator": c["regulator"],
                     "docket_number": c["docket"], "row_kind": c["kind"], "read": a["read"], "read_from": c["read_from"],
                     "text_chars": str(len(c["given"])), "text_sha256": c["sha"], "answer_file": "answers/" + n,
                     "model_id": a["model"], "read_at": a["read_at"]})
    return pd.DataFrame(rows, columns=COLS)


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW: one-line reads of the rules in motion, by a model")
    ap.add_argument("--in-dir", action="append", default=[], help="a directory of tables (first that holds one wins)")
    ap.add_argument("--out-dir", help="a trial run: the table, its log and the answers under this directory")
    ap.add_argument("--ledger-dir", help="keep the cost ledger under this directory instead of the output directory")
    ap.add_argument("--also-ledger", action="append", default=[], help="another ledger whose rows of this session count as spent (read only)")
    ap.add_argument("--raw-base", default=ROOT, help="the copy whose warehouse/raw holds the saved documents")
    ap.add_argument("--stop-usd", type=float, default=3.70)
    ap.add_argument("--limit", type=int, help="read at most this many rows (1: measure one)")
    ap.add_argument("--plan", action="store_true", help="no call: print the rows to read and the worst-case reserve")
    ap.add_argument("--no-call", action="store_true", help="no call and no spend: write the table from the answers already saved")
    ap.add_argument("--again-not-kept", action="store_true", help="ask once more for each row whose saved line fails "
                    "today's checks (the earlier answer is kept under answers/superseded/); never a third time")
    ap.add_argument("--max-asks", type=int, default=2, help="with --again-not-kept: a row is never asked more than this many times")
    ap.add_argument("--again", help="a file of ids to ask again although an answer is saved")
    ap.add_argument("--today")
    ap.add_argument("--model", help="the model id (default: the newest Sonnet-class model the API lists)")
    args = ap.parse_args(argv)
    dirs = [os.path.abspath(d) for d in args.in_dir] or [os.path.join(ROOT, "warehouse", "output")]
    today = dt.date.fromisoformat(args.today) if args.today else dt.datetime.now(dt.timezone.utc).date()
    out_dir = os.path.abspath(args.out_dir) if args.out_dir else ip.OUT_DIR
    ledger_dir = os.path.abspath(args.ledger_dir) if args.ledger_dir else out_dir
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    os.makedirs(os.path.join(out_dir, "logs"), exist_ok=True)
    log = ip.Log(os.path.join(out_dir, "logs", f"{NAME}_{run_id}.log"))
    # a trial keeps the answers under its own folder; the table of record keeps them in the raw store
    ans_dir = os.path.join(out_dir, "raw", NAME, "answers") if args.out_dir else os.path.join(ROOT, "warehouse", "raw", NAME, "answers")
    os.makedirs(ans_dir, exist_ok=True)
    cands = candidates(dirs, os.path.abspath(args.raw_base), today, log)
    again = {x.strip() for x in open(args.again, encoding="utf-8")} if args.again else set()
    done = {}
    for n in os.listdir(ans_dir):
        if n.endswith(".json"):
            with open(os.path.join(ans_dir, n), encoding="utf-8") as f:
                a = json.load(f)
            done[a["id"]] = a
    sup_dir = os.path.join(ans_dir, "superseded")
    if args.again_not_kept:   # one more ask, once only, for a row whose saved line fails today's checks
        earlier = {}   # how many answers of a row were set aside already
        for n in (os.listdir(sup_dir) if os.path.isdir(sup_dir) else []):
            earlier[n.rsplit(".", 2)[0]] = earlier.get(n.rsplit(".", 2)[0], 0) + 1
        for c in cands:
            a = done.get(c["id"])
            if a and a["text_sha256"] == c["sha"] and 1 + earlier.get(safe(c["id"]), 0) < args.max_asks and check_read(a.get("read", ""), c["given"], c["no_quote"]):
                again.add(c["id"])
                run = copied_run(a.get("read", ""), c["given"]) if c["no_quote"] else ""
                if run:   # the code's own finding about the earlier line, and nothing else, goes back to the model
                    c["feedback"] = ("\n\nAn earlier line was set aside because it copied this run of words from the excerpt: '" + run +
                                     "'. Write the line again wholly in your own words: no six consecutive words of it may stand in the excerpt.")
    todo = [c for c in cands if c["id"] in again or c["id"] not in done or done[c["id"]]["text_sha256"] != c["sha"]]
    if args.no_call:   # the table from the answers already saved, and nothing else: no client is built, nothing is spent
        log(f"--no-call: {len(todo)} rows have no saved answer for their text and are left without a line")
        todo = []
    log(f"{len(cands)} rows in motion with a saved text; {len(cands) - len(todo)} already answered; {len(todo)} to read")
    import llm
    if args.ledger_dir or args.out_dir:
        ip.set_out_dir(ledger_dir)   # the ledger (and its registry line) under the ledger directory, not warehouse/output
    spent0 = session_spent(llm, args.also_ledger)
    if args.plan:
        model = args.model or "claude-sonnet-5-5"
        res = [reserve_usd(model, len(c["given"]) + len(c["heading"]) + 40, llm) for c in todo]
        print(f"plan: {len(todo)} rows to read; worst-case reserve USD {sum(res):.4f} at {model} "
              f"(largest call {max(res) if res else 0:.4f}); session spent so far USD {spent0:.4f}; stop USD {args.stop_usd:.2f}")
        log.close()
        return 0
    cost = 0.0
    n_called = n_kept = 0
    stopped = ""
    if todo:
        client = llm.client("rule_reads", log, max_retries=1)
        if args.model:
            model = args.model
        else:
            sys.path.insert(0, os.path.join(ROOT, "warehouse", "news"))
            from score import pick_model
            model = pick_model(client, log)
        for c in todo[: args.limit] if args.limit else todo:
            msg = c["heading"] + "\n\nExcerpt of the document:\n" + c["given"] + c.get("feedback", "")
            res = reserve_usd(model, len(msg), llm)
            spent = session_spent(llm, args.also_ledger)
            if not may_call(spent, res, args.stop_usd):   # the stop, BEFORE the call
                stopped = (f"stopped before {c['id']}: spent USD {spent:.4f} plus a reserve of USD {res:.4f} would pass "
                           f"the stop USD {args.stop_usd:.2f}")
                log("  " + stopped)
                break
            try:
                resp = client.messages.create(
                    model=model, max_tokens=MAX_TOKENS, system=SYSTEM, messages=[{"role": "user", "content": msg}],
                    output_config={"effort": "low", "format": {"type": "json_schema", "schema": SCHEMA}})
            except llm.SpendCapReached as exc:
                stopped = str(exc)
                log("  " + stopped)
                break
            except Exception as exc:
                log(f"  {c['id']}: the call FAILED: {ip.redact(repr(exc))[:250]}")
                continue
            n_called += 1
            usd = llm.usd(model, llm.usage_numbers(resp.usage)) or 0.0
            cost += usd
            text = next((b.text for b in resp.content if b.type == "text"), "")
            try:
                line = norm(json.loads(text).get("read", "")) if resp.stop_reason == "end_turn" else ""
                why = check_read(line, c["given"], c["no_quote"]) if resp.stop_reason == "end_turn" else [f"stop_reason {resp.stop_reason}"]
            except (ValueError, AttributeError) as exc:
                line, why = "", [f"the answer is not the JSON asked for: {exc!r}"[:160]]
            now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            ans = {"id": c["id"], "read": line, "kept": not why, "why_not_kept": why, "model": model, "read_at": now,
                   "usd": round(usd, 6), "input_tokens": resp.usage.input_tokens, "output_tokens": resp.usage.output_tokens,
                   "text_sha256": c["sha"], "text_chars": len(c["given"]), "raw_answer": text,
                   "request_id": getattr(resp, "_request_id", None)}
            dest = os.path.join(ans_dir, safe(c["id"]) + ".json")
            if os.path.exists(dest):   # a paid answer is never discarded: the earlier one moves beside, numbered
                os.makedirs(sup_dir, exist_ok=True)
                k = 1
                while os.path.exists(os.path.join(sup_dir, f"{safe(c['id'])}.{k}.json")):
                    k += 1
                os.replace(dest, os.path.join(sup_dir, f"{safe(c['id'])}.{k}.json"))
            with open(dest, "w", encoding="utf-8", newline="\n") as f:
                json.dump(ans, f, ensure_ascii=False, indent=1)
            n_kept += 0 if why else 1
            log(f"  {c['id']}: {'kept' if not why else 'NOT kept: ' + '; '.join(why)}; USD {usd:.4f}; {line[:200]}")
    if args.ledger_dir or args.out_dir:
        ip.set_out_dir(out_dir)
    lic = "public"   # the lines are the ERW's own (a model's), and quote no restricted regulator's text
    table = table_from_answers(ans_dir, cands, lic, log)
    answered = len([n for n in os.listdir(ans_dir) if n.endswith(".json")])
    if len(table):
        model_ids = ", ".join(sorted(set(table["model_id"])))
        header = [
            "Energy Research Warehouse (ERW): one-line reads of the rules in motion for large loads: what each proceeding, "
            "order or federal action would change for a large load seeking power, written by a model (session 154)",
            "Shape: events (docs/datastandard.md v0), event_type rule_read; one row a line kept. A MODEL'S READ, not the "
            "regulator's words and not legal advice: the regulator's own sentence is in large_load_rules (sentence). "
            "rule_event_id is the row read (large_load_rules.event_id, or a policy_actions.event_id).",
            f"Retrieved: {run_id} (UTC) by warehouse/policy/rule_reads.py; model {model_ids}",
            f"Run log: warehouse/output/logs/{NAME}_{run_id}.log",
            "Raw files: warehouse/raw/large_load_rule_reads/answers/ (not in git: every answer paid for, kept or not, "
            "with the reason a line was not kept)",
            "What the model was given, and nothing else: the row's own sentence and the saved text of the document around "
            f"it ({BEFORE} characters before, {AFTER} after), or a federal action's title and abstract. A line is kept "
            "only if code finds every number in it in that text, it is one line with no em dash, and it holds none of "
            "the words zoning, permit, city council, county board. Method: " + METHOD + ".",
            f"Rows read: the rows in motion of {RULES} and {RULES}_internal, and the tagged federal actions of {ACTIONS} "
            "that have an abstract and no read in policy_reads. Each line is made from the saved document, not from a table.",
            f"Source: {SOURCE}. License: public. The lines are the ERW's own (a model's). A line about a row of "
            f"{RULES}_internal (a regulator whose terms restrict copying, or whose terms were not read) is kept only if it "
            f"holds no run of more than {QUOTE_WORDS} consecutive words of the document: it states facts and quotes nothing.",
        ]
        ip.write_snapshot(table, NAME, header, log, COLS)
        ip.update_sources([dict(source=SOURCE, publisher="Energy Research Warehouse (ERW)",
                                report="One-line reads of the rules in motion for large loads, by a model "
                                       "(warehouse/policy/rule_reads.py)",
                                report_url=METHOD_URL, document_list="", license=lic, tables=[NAME])])
    detail = (f"{len(cands)} rows in motion with a saved text; {n_called} calls this run, {n_kept} lines kept, USD {cost:.4f}; "
              f"answers saved {answered}; lines in the table {len(table)}" + (f"; {stopped}" if stopped else ""))
    log(detail)
    print(f"{NAME}: {detail}")
    log.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
