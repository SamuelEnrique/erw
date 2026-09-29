#!/usr/bin/env python3
"""Ask the Energy Research Warehouse a question (session 12, platform tool 20, v0).

Energy Research Warehouse (ERW). A question-answering layer that never states a
number it did not fetch:

1. The model (the newest Sonnet-class model in the API's models list, chosen at run
   time, never hardcoded) gets a system prompt built from package/llms.txt and the
   rules below, and the four tools of warehouse/chat/tools.py. No SQL, no code.
2. It may call tools at most MAX_TOOL_CALLS (8) times, then must answer.
3. Its answer is JSON: the answer text, a citation per table used (table, source
   report, data version), and whether the answer is "not in the warehouse".
4. Post-check: every number in the answer must appear in some tool result (or in
   the question, or as a tool argument such as a percentile), allowing rounding to
   the precision the answer states; and every cited table must be one a tool read.
   If the check fails, the model gets one retry with the violations named. If the
   retry fails too, the answer is replaced by a refusal.

    python warehouse/chat/ask.py "What was the latest Henry Hub spot price?"
    python warehouse/chat/ask.py --json "..."          # the full record as JSON
    python warehouse/chat/ask.py --export-spec site/lib/chat/spec.json

Token usage and cost are printed for every question; dollars use PRICES (from the
claude-api skill's model table, cached 2026-06-24); a model not in PRICES is
reported as cost unknown, never guessed. The key is ANTHROPIC_API_KEY (environment
or .env) and is never printed. The backend is erw's: ERW_BACKEND=local (default),
supabase or redivis.
"""

import argparse
import datetime as dt
import json
import os
import re
import sys
import time

import anthropic

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tools  # noqa: E402
sys.path.insert(0, os.path.join(ROOT, "warehouse"))
import llm  # noqa: E402  session 30: every Anthropic call goes through the cost ledger

MAX_TOOL_CALLS = 8
MAX_TOKENS = 16000
EFFORT = "high"
# USD per million tokens (input, output), from the claude-api skill model table, cached 2026-06-24
PRICES = {m: (p["input"], p["output"]) for m, p in llm.prices()["models"].items()}  # session 30: warehouse/config/model_prices.yaml
REFUSAL = ("I cannot give an answer I can verify: the numbers in my draft could not all be traced "
           "to a warehouse query. Try asking for one value, one table and one period at a time.")

BRIEFING = open(os.path.join(ROOT, "package", "llms.txt"), encoding="utf-8").read().strip()

RULES = """You answer questions about the US energy system from the Energy Research Warehouse (ERW), using only its four tools: list_tables, describe_table, query and compare.

Rules:
1. Answer only from tool results. Every number you write (prices, counts, capacities, percentiles, differences, dates and years) must appear in a tool result, written at the same or a coarser precision (a result of 25.1834 may be written 25.18 or 25.2). Do not compute any number yourself: no sums, averages, differences, ratios, percentages or unit conversions. If you need a difference or ratio, call compare; if you need an average, call query with that aggregation.
2. Cite every number. In the answer text, give the table each number came from, for example "25.18 USD/MWh (iso_rtm_hub_prices)". In citations, list every table you used, with its source_report and data_version copied exactly from the tool result.
3. If the warehouse does not hold what the question asks (a market, node, period, variable or kind of data it does not have), answer "not in the warehouse", say in one sentence what is missing, set not_in_warehouse to true, and state no numbers. Never use outside knowledge, never estimate.
4. Prefer public tables. If you use a table whose license is internal, say in the answer that it is internal (licensed for internal use only).
5. Times: series times are interval starts in UTC. Say which time zone you report. For an ISO's operating day, group or filter in its local time zone (tz), as the briefing says.
6. You have at most 8 tool calls. Call list_tables (with a filter) to find the table, describe_table only when you need entity, variable or column names, then query or compare.
7. Keep the answer short: the number or numbers with units, the time or period, and the table. Say what the number is (for example "mean of 96 fifteen-minute intervals").
8. Provenance tier: every tool result gives the table's tier: source (as the publisher published it), derived (computed by the ERW from other tables) or model_extracted (at least one field written by a model reading news, filings or the web, not published by a source). When a number comes from a model_extracted table, say so next to it in the answer, for example "USD 1.2 billion (energy_deals, model-extracted from news)".

Your final message is JSON with: answer (plain text), citations (one per table used: table, source_report, data_version, tier), not_in_warehouse (true or false)."""

SYSTEM = RULES + "\n\n# Briefing: package/llms.txt\n\n" + BRIEFING

ANSWER_SCHEMA = {
    "type": "object",
    "properties": {
        "answer": {"type": "string"},
        "citations": {"type": "array", "items": {
            "type": "object",
            "properties": {"table": {"type": "string"}, "source_report": {"type": "string"},
                           "data_version": {"type": "string"}, "tier": {"type": "string"}},
            "required": ["table", "source_report", "data_version", "tier"],
            "additionalProperties": False}},
        "not_in_warehouse": {"type": "boolean"},
    },
    "required": ["answer", "citations", "not_in_warehouse"],
    "additionalProperties": False,
}

RETRY = ("Your answer failed the check that every number comes from a tool result: {problems}. Every "
         "number must appear in a tool result, at the same or a coarser precision, and every cited table "
         "must be one a tool read. Call a tool for any number you need (compare gives differences and "
         "ratios), or remove the number, or answer \"not in the warehouse\". Answer again in the same "
         "JSON format.")


# ------------------------------------------------------------------ post-check

# A number: not glued to a letter, digit, underscore or dot before it (so table names such as
# eia930_ciso and codes such as P99.9 or HB_2015 are not read as numbers); thousands commas allowed.
NUM = re.compile(r"(?<![A-Za-z_\d.])(-?)(\d{1,3}(?:,\d{3})+|\d+)(\.\d+)?(?!\d)")


def numbers(text):
    """(value, decimals) for every number in a text. A minus sign counts only after a space,
    an opening bracket, a colon, a comma or an equals sign (so 2026-09-22 is one number, 2026)."""
    text = text.replace("−", "-")
    out = []
    for m in NUM.finditer(text):
        sign, whole, frac = m.group(1), m.group(2), m.group(3) or ""
        if sign:
            before = text[m.start() - 1] if m.start() > 0 else " "
            if not (before.isspace() or before in "([:,=" or m.start() == 0):
                sign = ""
        out.append((float(sign + whole.replace(",", "") + frac), len(frac) - 1 if frac else 0))
    return out


def list_markers(text):
    """Numbers that are list markers ("1. ", "2) ") at the start of a line: not facts."""
    return {float(m.group(1)) for m in re.finditer(r"(?m)^\s*(\d+)[.)]\s", text)}


def unverified(answer, sources):
    """Numbers in the answer that no source text contains at the answer's precision."""
    pool = []
    for s in sources:
        pool.extend(v for v, _ in numbers(s))
    markers = list_markers(answer)
    bad = []
    for v, d in numbers(answer):
        if d == 0 and v in markers:
            continue
        tol = 0.5 * 10 ** (-d) + 1e-9
        # the magnitude must match: a sign may be stated in words ("fell by 3.2" for a result of -3.2)
        if not any(abs(abs(p) - abs(v)) <= tol for p in pool):
            s = f"{v:.{d}f}"
            if s not in bad:
                bad.append(s)
    return bad


# ------------------------------------------------------------------ the loop

def nodash(text):
    return text.replace(chr(0x2014), " - ").replace("  -  ", " - ")


def pick_model(client):
    models = list(client.models.list())
    sonnets = [m for m in models if "sonnet" in m.id.lower()]
    if not sonnets:
        raise RuntimeError("the models list has no Sonnet-class model")
    return max(sonnets, key=lambda m: m.created_at).id


def api_key():
    k = os.environ.get("ANTHROPIC_API_KEY")
    if not k:
        from dotenv import dotenv_values
        k = dotenv_values(os.path.join(ROOT, ".env")).get("ANTHROPIC_API_KEY")
    if not k:
        raise SystemExit("ANTHROPIC_API_KEY is not set (environment or .env)")
    return k.strip()


def cost_usd(model, usage):
    """Session 30: at the prices of warehouse/config/model_prices.yaml, cache reads at their own price."""
    return llm.usd(model, {"input": usage["input"], "output": usage["output"], "cache_read": usage["cache_read"],
                           "cache_write": usage["cache_write"], "cache_write_1h": 0, "web_searches": 0})


class Asker:
    def __init__(self, model=None, client=None):
        self.client = client or llm.client(os.environ.get("ERW_STEP") or "chat", api_key=api_key())
        self.model = model or pick_model(self.client)

    def _create(self, messages, allow_tools):
        return self.client.messages.create(
            model=self.model, max_tokens=MAX_TOKENS,
            system=[{"type": "text", "text": SYSTEM, "cache_control": {"type": "ephemeral"}}],
            tools=tools.TOOLS,
            tool_choice={"type": "auto"} if allow_tools else {"type": "none"},
            output_config={"effort": EFFORT, "format": {"type": "json_schema", "schema": ANSWER_SCHEMA}},
            messages=messages)

    def ask(self, question, today=None):
        t0 = time.time()
        today = today or dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")
        messages = [{"role": "user", "content": f"Today is {today} (UTC).\n\nQuestion: {question}"}]
        usage = {"input": 0, "output": 0, "cache_write": 0, "cache_read": 0, "requests": 0}
        calls, sources, tables_read = [], [question], set()
        record = {"question": question, "model": self.model, "today": today, "retried": False,
                  "first_violations": [], "request_ids": []}
        final, attempts = None, 0
        while True:
            resp = self._create(messages, allow_tools=len(calls) < MAX_TOOL_CALLS)
            u = resp.usage
            usage["input"] += u.input_tokens
            usage["output"] += u.output_tokens
            usage["cache_write"] += u.cache_creation_input_tokens or 0
            usage["cache_read"] += u.cache_read_input_tokens or 0
            usage["requests"] += 1
            record["request_ids"].append(resp._request_id)
            messages.append({"role": "assistant", "content": resp.content})
            if resp.stop_reason == "tool_use":
                results = []
                for b in resp.content:
                    if b.type != "tool_use":
                        continue
                    if len(calls) >= MAX_TOOL_CALLS:
                        out, err = {"error": f"tool call limit ({MAX_TOOL_CALLS}) reached; answer now"}, True
                    else:
                        out, err = tools.run(b.name, b.input)
                        text = json.dumps(out, default=str)
                        calls.append({"tool": b.name, "input": b.input, "is_error": err,
                                      "result_chars": len(text)})
                        sources += [text, json.dumps(b.input)]
                        for key in ("table",):
                            if isinstance(out, dict) and out.get(key):
                                tables_read.add(out[key])
                        if isinstance(out, dict):
                            for sub in ("a", "b"):
                                if isinstance(out.get(sub), dict) and out[sub].get("table"):
                                    tables_read.add(out[sub]["table"])
                            if b.name == "list_tables":
                                tables_read.update(r["table"] for r in out.get("tables", []))
                    results.append({"type": "tool_result", "tool_use_id": b.id,
                                    "content": json.dumps(out, default=str), "is_error": err})
                messages.append({"role": "user", "content": results})
                continue
            if resp.stop_reason == "refusal":
                final = {"answer": REFUSAL, "citations": [], "not_in_warehouse": False}
                record["status"] = "model_refusal"
                break
            if resp.stop_reason != "end_turn":
                raise RuntimeError(f"stop_reason {resp.stop_reason} (request {resp._request_id})")
            text = "".join(b.text for b in resp.content if b.type == "text")
            try:
                draft = json.loads(text)
            except json.JSONDecodeError:
                raise RuntimeError(f"final message is not JSON: {text[:200]}")
            bad = unverified(draft["answer"], sources)
            cited = [c["table"] for c in draft.get("citations", [])]
            uncited_tables = [t for t in cited if t not in tables_read]
            no_cite = bool(numbers(draft["answer"])) and not cited and not draft.get("not_in_warehouse")
            if not bad and not uncited_tables and not no_cite:
                final = draft
                record["status"] = "not_in_warehouse" if draft.get("not_in_warehouse") else "answered"
                break
            attempts += 1
            if attempts == 1:
                record["retried"] = True
                record["first_violations"] = bad + [f"cited table not read: {t}" for t in uncited_tables] \
                    + (["numbers without a citation"] if no_cite else [])
                record["first_answer"] = draft["answer"]
                problems = []
                if bad:
                    problems.append("numbers in no tool result: " + ", ".join(bad))
                if uncited_tables:
                    problems.append("cited tables no tool read: " + ", ".join(uncited_tables))
                if no_cite:
                    problems.append("numbers but no citations")
                messages.append({"role": "user", "content": RETRY.format(problems="; ".join(problems))})
                continue
            final = {"answer": REFUSAL, "citations": [], "not_in_warehouse": False}
            record["status"] = "refused_unverified"
            record["second_violations"] = bad + [f"cited table not read: {t}" for t in uncited_tables]
            record["second_answer"] = draft["answer"]
            break
        # session 28: each citation's tier is the warehouse's, whatever the model copied
        for c in final.get("citations", []):
            c["tier"] = tools.provenance(c["table"]).get("tier") or c.get("tier") or ""
        record.update(final)
        # the ERW writes no em dashes in any file (CLAUDE.md): model text is normalised, as in
        # warehouse/news/score.py; the numbers and every other character are unchanged
        for k in ("answer", "first_answer", "second_answer"):
            if isinstance(record.get(k), str):
                record[k] = nodash(record[k])
        record.update({"tool_calls": len(calls), "calls": calls, "usage": usage,
                       "cost_usd": cost_usd(self.model, usage), "seconds": round(time.time() - t0, 1)})
        return record


def export_spec(path):
    """The loop's definition for the site's server route (site/app/api/ask): the same
    system prompt, tools, answer schema, limits and prices, from this file only."""
    spec = {"_about": "Generated by warehouse/chat/ask.py --export-spec; do not edit by hand.",
            "system": SYSTEM, "tools": tools.TOOLS, "answer_schema": ANSWER_SCHEMA,
            "max_tool_calls": MAX_TOOL_CALLS, "max_tokens": MAX_TOKENS, "effort": EFFORT,
            "prices": PRICES, "retry": RETRY, "refusal": REFUSAL,
            # session 30: the full price table (cache writes and reads) and its date, for the site's cost ledger
            "model_prices": llm.prices()["models"], "prices_as_of": llm.prices()["as_of"],
            "aggregations": tools.AGGREGATIONS, "time_groups": tools.TIME_GROUPS,
            "max_groups": tools.MAX_GROUPS, "digits": tools.DIGITS}
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(spec, f, indent=1, ensure_ascii=False)
        f.write("\n")
    print(f"wrote {path}")


def main(argv=None):
    ap = argparse.ArgumentParser(description="Ask the ERW a question")
    ap.add_argument("question", nargs="?")
    ap.add_argument("--json", action="store_true", help="print the full record as JSON")
    ap.add_argument("--export-spec", metavar="PATH", help="write the loop definition for the site and exit")
    args = ap.parse_args(argv)
    if args.export_spec:
        export_spec(args.export_spec)
        return 0
    if not args.question:
        ap.error("a question is required")
    rec = Asker().ask(args.question)
    if args.json:
        print(json.dumps(rec, indent=2, default=str))
        return 0
    print(rec["answer"])
    for c in rec["citations"]:
        print(f"  [{c['table']}] source {c['source_report']}; {c['data_version']}"
              + (f"; tier {c['tier']}" if c.get("tier") else ""))
    u = rec["usage"]
    cost = "unknown (model not in PRICES)" if rec["cost_usd"] is None else f"USD {rec['cost_usd']:.4f}"
    print(f"\nstatus {rec['status']}; model {rec['model']}; tool calls {rec['tool_calls']}; "
          f"requests {u['requests']}; tokens in {u['input']} out {u['output']} cache write "
          f"{u['cache_write']} cache read {u['cache_read']}; cost {cost}; {rec['seconds']} s"
          + ("; retried after: " + ", ".join(rec["first_violations"]) if rec["retried"] else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
