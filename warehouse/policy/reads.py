#!/usr/bin/env python3
"""Impact reads of significant policy actions (platform tool 12, session 24).

Energy Research Warehouse (ERW). For every policy action scored 5 or more (warehouse/policy/score.py, the news
rubric), the model reads the action's own text and returns a JSON object:

  what_changes    what the action changes, in plain words
  who_affected    the sectors, ISOs and states it affects
  direction       its direction of effect on supply, demand, prices and buildout (up, down, none, unclear)
  timeline        when it takes effect or what comes next
  plain_read      a two-sentence plain-language read

each with the exact spans of the source text that support it. A field is kept only if it has at least one span, every
span is found word for word in the stored source text (whitespace and quote marks normalized), and every number in the
field is in its spans (the chat's literal-number check). Otherwise it is dropped and the reason recorded.

The source text: for a Federal Register document, the Register's plain text of the document (its raw_text_url), from
the SUMMARY on, at most 9,000 characters; for a news release, the text of its page (or PDF). Every fetch is stored raw
under warehouse/raw/policy_reads/<run_id>/, and the text read is saved beside it.

Writes policy_reads (public: the model's kept fields and the links) and policy_reads_evidence (internal: the spans,
per field). Actions already read are not read again (warehouse/policy/read_done.csv, in git).

    python warehouse/policy/reads.py                  # every unread action scored 5 or more
    python warehouse/policy/reads.py --max-usd 3
"""

import argparse
import concurrent.futures as cf
import datetime as dt
import html as H
import io
import json
import os
import re
import sys
import traceback

import pandas as pd
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "news"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "chat"))
import iso_prices as ip  # noqa: E402
sys.path.insert(0, os.path.join(ROOT, "warehouse"))
from voice import VOICE_NOTE  # noqa: E402  session 25: docs/voice.md

ACTIONS, NAME, EVID = "policy_actions", "policy_reads", "policy_reads_evidence"
DONE = os.path.join(HERE, "read_done.csv")
UA = {"User-Agent": "Mozilla/5.0 (ERW energy research warehouse; https://github.com/SamuelEnrique/erw)"}
MAX_TEXT = 9000
ISOS = ["ERCOT", "CAISO", "PJM", "MISO", "SPP", "NYISO", "ISO-NE"]
SECTORS = ["power", "transmission", "gas", "oil", "nuclear", "renewables", "storage", "coal", "efficiency", "emissions",
           "datacenters", "leasing", "hydrogen", "minerals"]
DIRS = ["up", "down", "none", "unclear"]
FIELDS = ["what_changes", "who_affected", "direction", "timeline", "plain_read"]
EM = chr(0x2014)

SYSTEM = """You read one US energy policy action (a Federal Register document or an agency news release) for the Energy
Research Warehouse (ERW) and return a JSON object with five fields. Use only the source text given.
- what_changes: text, one or two plain sentences on what the action changes.
- who_affected: sectors (from the list given), isos (US grid operators named or clearly covered by the text; empty if
  none), states (two-letter codes of states the text names), and why in text.
- direction: the direction of the action's effect on supply, demand, prices and buildout, each one of up, down, none,
  unclear; unclear unless the text supports a direction.
- timeline: text: when it takes effect, comment deadlines, or what comes next, as the text states.
- plain_read: text, exactly two plain-language sentences for a non-specialist.
Every field has spans: one to three exact quotes copied character for character from the source text (each at most 300
characters) that support it. A field the text does not support gets empty text and empty spans. No numbers that are not
in its spans. No em dashes, no hype, no advice.""" + VOICE_NOTE
SPANS = {"type": "array", "items": {"type": "string"}}
SCHEMA = {"type": "object", "additionalProperties": False, "required": FIELDS, "properties": {
    "what_changes": {"type": "object", "additionalProperties": False, "required": ["text", "spans"],
                     "properties": {"text": {"type": "string"}, "spans": SPANS}},
    "who_affected": {"type": "object", "additionalProperties": False, "required": ["sectors", "isos", "states", "text", "spans"],
                     "properties": {"sectors": {"type": "array", "items": {"type": "string", "enum": SECTORS}},
                                    "isos": {"type": "array", "items": {"type": "string", "enum": ISOS}},
                                    "states": {"type": "array", "items": {"type": "string"}},
                                    "text": {"type": "string"}, "spans": SPANS}},
    "direction": {"type": "object", "additionalProperties": False,
                  "required": ["supply", "demand", "prices", "buildout", "spans"],
                  "properties": {k: {"type": "string", "enum": DIRS} for k in ("supply", "demand", "prices", "buildout")}
                  | {"spans": SPANS}},
    "timeline": {"type": "object", "additionalProperties": False, "required": ["text", "spans"],
                 "properties": {"text": {"type": "string"}, "spans": SPANS}},
    "plain_read": {"type": "object", "additionalProperties": False, "required": ["text", "spans"],
                   "properties": {"text": {"type": "string"}, "spans": SPANS}}}}
READ_COLS = ["event_id", "event_date", "event_type", "parties", "entity_ids", "mw", "price", "currency", "status",
             "source", "source_url", "action_event_id", "agency", "action_type", "title", "significance",
             "what_changes", "affected_sectors", "affected_isos", "affected_states", "direction_supply",
             "direction_demand", "direction_prices", "direction_buildout", "timeline", "plain_read", "fields_kept",
             "fields_dropped", "news_story_urls", "model_id", "read_at"]
EVID_COLS = ["event_id", "event_date", "event_type", "parties", "entity_ids", "mw", "price", "currency", "status",
             "source", "source_url", "read_id", "field", "span", "source_text_file"]


def norm(s):
    s = (s or "").replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    s = s.replace("–", "-").replace(EM, "-").replace(" ", " ").replace("­", "")
    return re.sub(r"\s+", " ", s).strip().casefold()


def read_events(path):
    with open(path, encoding="utf-8") as f:
        head = [ln for ln in f if ln.startswith("#")]
    return pd.read_csv(path, skiprows=len(head), dtype=str, keep_default_na=False)


def html_text(s):
    s = re.sub(r"(?is)<(script|style|nav|header|footer)[^>]*>.*?</\1>", " ", s)
    return re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", " ", s))).strip()


def source_text(r, log):
    """(text, url) of the action's own text, fetched now (stored raw by the ERW's request hook)."""
    if r["fr_document_number"]:
        meta = requests.get(f"https://www.federalregister.gov/api/v1/documents/{r['fr_document_number']}.json",
                            params={"fields[]": ["raw_text_url", "abstract", "title"]}, headers=UA, timeout=60)
        meta.raise_for_status()
        url = meta.json()["raw_text_url"]
        t = requests.get(url, headers=UA, timeout=90)
        t.raise_for_status()
        body = html_text(t.text) if "<" in t.text[:200] else re.sub(r"\s+", " ", t.text)
        i = body.find("SUMMARY:")
        return (r["title"] + ". " + body[i if i >= 0 else 0:][:MAX_TEXT]), url
    url = r["source_url"]
    t = requests.get(url, headers=UA, timeout=90)
    t.raise_for_status()
    if url.lower().endswith(".pdf") or t.headers.get("content-type", "").startswith("application/pdf"):
        import pdfplumber
        with pdfplumber.open(io.BytesIO(t.content)) as pdf:
            body = " ".join((p.extract_text() or "") for p in pdf.pages[:6])
        body = re.sub(r"\s+", " ", body)
    else:
        body = html_text(t.text)
        k = body.find(r["title"][:40])
        body = body[k:] if k >= 0 else body
    return (r["title"] + ". " + body)[:MAX_TEXT], url


def check_field(name, val, text):
    """The reasons a field fails, [] if it is kept."""
    import ask as chat_ask
    spans = [s for s in val.get("spans", []) if s.strip()]
    if not spans:
        return ["no span"]
    nt = norm(text)
    bad = [s[:60] for s in spans if norm(s) not in nt]
    if bad:
        return [f"span not in the source: {bad}"]
    words = val.get("text", "")
    if name in ("what_changes", "timeline", "plain_read") and not words.strip():
        return ["empty"]
    nums = chat_ask.unverified(words, spans)
    if nums:
        return [f"numbers not in the spans: {nums}"]
    return []


class Reader:
    def __init__(self, log):
        import anthropic
        from score import PRICES, pick_model
        self.client = anthropic.Anthropic(api_key=ip.load_key("ANTHROPIC_API_KEY", log))
        self.model = pick_model(self.client, log)
        self.price = PRICES.get(self.model)

    def read(self, r, text):
        msg = (f"Action: {r['agency']} {r['action_type'].replace('_', ' ')}, {r['event_date']}: {r['title']}\n"
               f"Sectors to choose from: {', '.join(SECTORS)}\n\nSource text:\n{text}")
        resp = self.client.messages.create(
            model=self.model, max_tokens=4000, system=SYSTEM, messages=[{"role": "user", "content": msg}],
            output_config={"effort": "low", "format": {"type": "json_schema", "schema": SCHEMA}})
        u = resp.usage
        cost = (u.input_tokens * self.price[0] + u.output_tokens * self.price[1]) / 1e6 if self.price else 0
        return json.loads(next(b.text for b in resp.content if b.type == "text")), cost


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW policy impact reads")
    ap.add_argument("--max-usd", type=float, default=3.0)
    ap.add_argument("--min-significance", type=int, default=5)
    args = ap.parse_args(argv)
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"policy_reads_{run_id}.log"))
    ip.RAW.open("policy_reads", run_id)
    text_dir = os.path.join(ip.RAW_DIR, "policy_reads", run_id, "texts")
    os.makedirs(text_dir, exist_ok=True)
    status = dict(table=NAME, market="reads", status="ok", detail="")
    try:
        acts = read_events(os.path.join(ip.OUT_DIR, ACTIONS + ".csv"))
        sig = pd.to_numeric(acts["significance"], errors="coerce")
        want = acts[sig >= args.min_significance]
        done = pd.read_csv(DONE, dtype=str, keep_default_na=False) if os.path.exists(DONE) else pd.DataFrame(columns=["action_event_id", "read_at", "outcome"])
        todo = want[~want["event_id"].isin(set(done["action_event_id"]))]
        log(f"{len(want)} actions scored {args.min_significance} or more; {len(todo)} not read yet")
        reads, evid, marks, cost = [], [], [], 0.0
        if len(todo):
            reader = Reader(log)

            def one(r):
                text, url = source_text(r, log)
                fn = os.path.join(text_dir, re.sub(r"[^A-Za-z0-9_.-]+", "_", r["event_id"]) + ".txt")
                with open(fn, "w", encoding="utf-8", newline="\n") as f:
                    f.write(f"# {url}\n{text}")
                out, c = reader.read(r, text)
                return r, text, url, fn, out, c

            rows = todo.to_dict("records")
            with cf.ThreadPoolExecutor(4) as pool:
                for g in range(0, len(rows), 4):
                    if cost + 0.03 * 4 > args.max_usd:
                        log(f"  stopping before action {g + 1} of {len(rows)}: the spend would pass USD {args.max_usd}")
                        break
                    futs = [pool.submit(one, r) for r in rows[g:g + 4]]
                    for f in futs:
                        try:
                            r, text, url, fn, out, c = f.result()
                        except Exception as exc:
                            log(f"  a read FAILED: {ip.redact(repr(exc))[:250]}")
                            continue
                        cost += c
                        kept, dropped = [], []
                        for name in FIELDS:
                            why = check_field(name, out[name], text)
                            (dropped if why else kept).append(name if not why else f"{name} ({'; '.join(why)})")
                        k = {x.split(" ")[0] for x in kept}
                        rid = "policyread:" + r["event_id"]
                        now = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
                        wa, dr = out["who_affected"], out["direction"]
                        reads.append({
                            "event_id": rid, "event_date": r["event_date"], "event_type": "policy_read",
                            "parties": r["parties"], "entity_ids": "", "mw": "", "price": "", "currency": "", "status": "",
                            "source": "erw:policy_reads", "source_url": r["source_url"], "action_event_id": r["event_id"],
                            "agency": r["agency"], "action_type": r["action_type"], "title": r["title"],
                            "significance": r["significance"],
                            "what_changes": out["what_changes"]["text"].replace(EM, ",") if "what_changes" in k else "",
                            "affected_sectors": ";".join(wa["sectors"]) if "who_affected" in k else "",
                            "affected_isos": ";".join(wa["isos"]) if "who_affected" in k else "",
                            "affected_states": ";".join(s for s in wa["states"] if re.fullmatch(r"[A-Z]{2}", s)) if "who_affected" in k else "",
                            **{f"direction_{d}": dr[d] if "direction" in k else "" for d in ("supply", "demand", "prices", "buildout")},
                            "timeline": out["timeline"]["text"].replace(EM, ",") if "timeline" in k else "",
                            "plain_read": out["plain_read"]["text"].replace(EM, ",") if "plain_read" in k else "",
                            "fields_kept": ";".join(sorted(k)), "fields_dropped": " | ".join(dropped),
                            "news_story_urls": r["news_story_urls"], "model_id": reader.model, "read_at": now})
                        for name in k:
                            for s in out[name]["spans"]:
                                evid.append({"event_id": f"{rid}#{name}#{len(evid)}", "event_date": r["event_date"],
                                             "event_type": "policy_read_evidence", "parties": "", "entity_ids": "", "mw": "",
                                             "price": "", "currency": "", "status": "", "source": "erw:policy_reads",
                                             "source_url": url, "read_id": rid, "field": name, "span": s.replace(EM, "-"),
                                             "source_text_file": os.path.relpath(fn, ROOT).replace(os.sep, "/")})
                        marks.append({"action_event_id": r["event_id"], "read_at": now, "outcome": f"{len(k)} of 5 kept"})
                        log(f"  {r['event_id']}: kept {sorted(k)}; dropped {dropped}; USD {c:.4f}")
        if reads:
            hdr = ["Energy Research Warehouse (ERW): impact reads of policy actions scored 5 or more",
                   "Shape: events (docs/datastandard.md v0), event_type policy_read; one row per action read. The model's "
                   "fields as kept by warehouse/policy/reads.py: a field is blank when its spans were not found word for "
                   "word in the action's own text or a number in it was not in its spans (fields_dropped says why).",
                   f"Retrieved: {run_id} (UTC) by warehouse/policy/reads.py; model {reads[0]['model_id']}",
                   f"Run log: warehouse/output/logs/policy_reads_{run_id}.log",
                   f"Raw files: warehouse/raw/policy_reads/{run_id}/ (not in git; texts/ holds the text each read used)",
                   "Source: erw:policy_reads, from policy_actions (the Federal Register and agency news releases).",
                   "License: public (the model's fields and links; the evidence spans are in policy_reads_evidence, internal)."]
            ip.write_csv(pd.DataFrame(reads)[READ_COLS], NAME, hdr, log, cols=READ_COLS, key=["event_id"], time_col="event_date")
            ehdr = ["Energy Research Warehouse (ERW): the evidence spans of each kept field of policy_reads",
                    "Shape: events (docs/datastandard.md v0), event_type policy_read_evidence; one row per span.",
                    f"Retrieved: {run_id} (UTC) by warehouse/policy/reads.py",
                    f"Run log: warehouse/output/logs/policy_reads_{run_id}.log",
                    "Source: erw:policy_reads.", "License: internal (kept for checking the reads, not shown on the site)."]
            ip.write_csv(pd.DataFrame(evid)[EVID_COLS], EVID, ehdr, log, cols=EVID_COLS, key=["event_id"], time_col="event_date")
            pd.concat([done, pd.DataFrame(marks)], ignore_index=True).to_csv(DONE, index=False, lineterminator="\n")
            ip.update_sources([dict(source="erw:policy_reads", publisher="Energy Research Warehouse (ERW)",
                                    report="Impact reads of policy actions (warehouse/policy/reads.py)",
                                    report_url="https://github.com/SamuelEnrique/erw/blob/main/warehouse/policy/reads.py",
                                    document_list="", license="public", tables=[NAME, EVID])])
        full = sum(1 for r in reads if r["fields_kept"].count(";") == 4)
        status["detail"] = f"{len(reads)} actions read ({full} with all 5 fields kept); cost USD {cost:.4f}"
        log(status["detail"])
        print(f"policy_reads: {status['detail']}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED:\n{tb}")
        print(f"policy_reads FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        status.update(status="failed", detail=tb.strip().splitlines()[-1][:300])
    ip.write_status("policy_reads", run_id, [status])
    log.close()
    return 0 if status["status"] == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
