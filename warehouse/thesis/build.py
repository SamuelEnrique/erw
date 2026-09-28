#!/usr/bin/env python3
"""Thesis Builder v0 (platform tool 27): a niche market map for investors, as one workbook.

Energy Research Warehouse (ERW), session 25. Internal CLI.

    python warehouse/thesis/build.py "subsurface heat mapping for geothermal"
    python warehouse/thesis/build.py "grid-scale battery storage software for merchant operators" --stage seed --geography US
    python warehouse/thesis/build.py "..." --max-usd 6 --out docs/thesis/my-niche.xlsx

The fixed research plan (docs/methods/thesis_builder.md):
  1. Research, three agentic passes with the Claude API (the newest Sonnet-class model the models list offers, as the
     news scorer picks it) with the API's web search tool and the ERW's four read-only warehouse tools
     (warehouse/chat/tools.py: list_tables, describe_table, query, compare), the warehouse first:
       a. scope, fundamentals and trends;  b. companies, capital and incumbents;  c. risks.
     Every web search result is kept as a numbered source (S1, S2, ...) with its URL, title and the date of the run,
     and every passage the model cites from it (the API's web citations, cited_text) is kept with it. Every warehouse
     tool result is kept as a numbered ERW source (E1, E2, ...) with its table and citation.
  2. Structure, one call per sheet with a JSON schema, from the research notes and the numbered sources only.
  3. Check. A number is written only if it appears in the cited text of a source the row names (the chat's
     literal-number check, warehouse/chat/ask.py); a number that fails is replaced by "not confirmed" and logged. A row
     with no source is not written. "not disclosed" is written where the sources say nothing. An estimate must be
     labelled as one and show its arithmetic, and its inputs pass the same check.
  4. Write the workbook (the Stanford format, below) and merge every company found into the entities table
     energy_companies (public: the model's fields, links and a confidence score), tool 10's seed, merged on name plus
     website.
  Licensed connectors (warehouse/thesis/connectors/): any connector whose credential is set is called, and its rows
  are marked "licensed, user's own account, not stored in the ERW"; they go to the workbook only, never to a table.

The workbook: Georgia titles in cardinal #8C1515, cardinal header bars with white text, body text #2E2D29, fog beige
#F7F3EA highlight rows, column A a narrow margin, gridlines off, numbered "(1) SECTION" bars each followed by a
"Fact:" paragraph, a table and a chart where there is data, and a grey "Source(s):" line under each section. Sheets:
Scope, Fundamentals, Trends, Landscape, Capital, Incumbents, Policy, Risks, Sources.

Every model call is logged with its tokens, web searches and cost; the run's total is logged and written on the Scope
sheet. Cost: the model's token prices (warehouse/news/score.py PRICES) plus USD 10 per 1,000 web searches.
"""

import argparse
import datetime as dt
import json
import os
import re
import sys
import time
import traceback

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
for p in ("warehouse/connectors", "warehouse/news", "warehouse/chat", "warehouse", "warehouse/analysis",
          "warehouse/analysis/templates", "warehouse/thesis"):
    sys.path.insert(0, os.path.join(ROOT, p))
import iso_prices as ip  # noqa: E402
from voice import VOICE_NOTE  # noqa: E402

SEARCH_USD = 10 / 1000
NAME = "energy_companies"
EM = chr(0x2014)
CARDINAL, INK, FOG, GREY, WHITE = "8C1515", "2E2D29", "F7F3EA", "808080", "FFFFFF"


class Budget(RuntimeError):
    pass


# ---------------------------------------------------------------------------------------------
# the model, with web search and the warehouse's tools
# ---------------------------------------------------------------------------------------------

class Researcher:
    def __init__(self, log, max_usd):
        import anthropic
        from score import PRICES, pick_model
        self.client = anthropic.Anthropic(api_key=ip.load_key("ANTHROPIC_API_KEY", log))
        self.model = pick_model(self.client, log)
        self.price = PRICES[self.model]
        self.log, self.max_usd = log, max_usd
        self.cost, self.calls, self.searches = 0.0, 0, 0
        self.sources = {}      # url -> {id, url, title, page_age, cited: [texts]}
        self.erw = []          # [{id, tool, args, result}]

    def charge(self, resp, what):
        u = resp.usage
        stu = getattr(u, "server_tool_use", None)
        n_search = (getattr(stu, "web_search_requests", 0) or 0) if stu else 0
        cache_r = getattr(u, "cache_read_input_tokens", 0) or 0
        cache_w = getattr(u, "cache_creation_input_tokens", 0) or 0
        c = ((u.input_tokens + cache_w * 1.25 + cache_r * 0.1) * self.price[0] + u.output_tokens * self.price[1]) / 1e6 \
            + n_search * SEARCH_USD
        self.cost += c
        self.calls += 1
        self.searches += n_search
        self.log(f"  call {self.calls} ({what}): {self.model}, in {u.input_tokens} (cache read {cache_r}, write {cache_w}), "
                 f"out {u.output_tokens}, web searches {n_search}; USD {c:.4f}; run total USD {self.cost:.4f}")
        if self.cost > self.max_usd:
            raise Budget(f"the run passed USD {self.max_usd} (USD {self.cost:.4f}); stopping")

    def source(self, url, title="", page_age="", cited=None):
        if not url:
            return None
        s = self.sources.get(url)
        if s is None:
            s = self.sources[url] = {"id": f"S{len(self.sources) + 1}", "url": url, "title": title or "",
                                     "page_age": page_age or "", "cited": [], "retrieved": dt.date.today().isoformat()}
        if cited and cited not in s["cited"]:
            s["cited"].append(cited)
        return s["id"]

    def research(self, what, system, prompt, max_searches, erw_tools=True, max_turns=24):
        """One agentic pass: web search and the warehouse's tools, until the model ends its turn. Returns the notes
        (text, with each cited passage marked with its source id)."""
        import tools as erw_tools_mod
        tools = [{"type": "web_search_20260209", "name": "web_search", "max_uses": max_searches}]
        if erw_tools:
            tools = [dict(t) for t in erw_tools_mod.TOOLS] + tools
        msgs = [{"role": "user", "content": prompt}]
        notes = []
        for turn in range(max_turns):
            # the history grows every turn: cache it (the last block), so a turn pays for its new tokens only
            resp = self.client.messages.create(model=self.model, max_tokens=16000, system=system + VOICE_NOTE, tools=tools,
                                               messages=msgs, output_config={"effort": "medium"},
                                               cache_control={"type": "ephemeral"})
            self.charge(resp, what)
            results = []
            for b in resp.content:
                if b.type == "web_search_tool_result":
                    if isinstance(b.content, list):
                        for r in b.content:
                            self.source(getattr(r, "url", ""), getattr(r, "title", ""), getattr(r, "page_age", "") or "")
                elif b.type == "text":
                    tags = []
                    for c in (getattr(b, "citations", None) or []):
                        if getattr(c, "type", "") == "web_search_result_location":
                            sid = self.source(c.url, getattr(c, "title", ""), cited=getattr(c, "cited_text", ""))
                            tags.append(sid)
                    notes.append(b.text + (f" [{', '.join(dict.fromkeys(tags))}]" if tags else ""))
                elif b.type == "tool_use":
                    try:
                        res, err = erw_tools_mod.run(b.name, b.input)
                    except Exception as exc:  # a warehouse tool that fails is an error result, not a failed run
                        res, err = {"error": f"{type(exc).__name__}: {str(exc)[:300]}"}, True
                    eid = f"E{len(self.erw) + 1}"
                    self.erw.append({"id": eid, "tool": b.name, "args": b.input, "result": res, "error": err})
                    body = json.dumps(res, default=str)[:12000]
                    results.append({"type": "tool_result", "tool_use_id": b.id, "is_error": err,
                                    "content": f"[ERW source {eid}] {body}"})
            msgs.append({"role": "assistant", "content": resp.content})
            if resp.stop_reason == "tool_use" and results:
                msgs.append({"role": "user", "content": results})
                continue
            if resp.stop_reason == "pause_turn":
                continue
            break
        return "".join(notes)

    def structure(self, what, system, notes, schema):
        """One JSON call per sheet, from the notes and the numbered sources only."""
        src = self.source_list()
        msg = (f"Research notes (bracketed ids are the sources each passage cites):\n{notes}\n\nNumbered web sources "
               f"(id, title, URL, the passages cited from each):\n{src}\n\nWarehouse sources (id, tool, table, result):\n"
               f"{self.erw_list()}")
        # not cached: each sheet's JSON schema is part of the prompt's prefix, so a cache written for one sheet never
        # matches the next (session 25, run 1: every structure call wrote the cache and read none)
        resp = self.client.messages.create(
            model=self.model, max_tokens=16000, system=STRUCT_SYSTEM + VOICE_NOTE,
            messages=[{"role": "user", "content": [{"type": "text", "text": msg}, {"type": "text", "text": system}]}],
            output_config={"effort": "medium", "format": {"type": "json_schema", "schema": schema}})
        self.charge(resp, what)
        if resp.stop_reason != "end_turn":
            raise RuntimeError(f"{what}: stop_reason {resp.stop_reason}")
        return json.loads(next(b.text for b in resp.content if b.type == "text"))

    def source_list(self):
        out = []
        for s in self.sources.values():
            cited = " | ".join(c[:400] for c in s["cited"][:6])
            out.append(f"{s['id']} | {s['title'][:120]} | {s['url']}" + (f" | cited: {cited}" if cited else ""))
        return "\n".join(out)

    def erw_list(self):
        out = []
        for e in self.erw:
            table = e["args"].get("table") or ""
            out.append(f"{e['id']} | {e['tool']} | {table} | {json.dumps(e['result'], default=str)[:1500]}")
        return "\n".join(out)

    def texts_of(self, ids):
        """The text a row's numbers must appear in: the cited passages of its web sources, the results of its ERW sources."""
        by_id = {s["id"]: s for s in self.sources.values()}
        erw = {e["id"]: e for e in self.erw}
        out = []
        for i in ids or []:
            if i in by_id:
                out += by_id[i]["cited"] + [by_id[i]["title"]]
            elif i in erw:
                out.append(json.dumps(erw[i]["result"], default=str))
        return out


# ---------------------------------------------------------------------------------------------
# the plan: prompts and schemas
# ---------------------------------------------------------------------------------------------

def base_system(niche, stage, geo):
    return f"""You research one niche for an investor's market map, for the Energy Research Warehouse (ERW).
Niche: {niche}. Stage of interest: {stage or 'any'}. Geography: {geo or 'any, US first'}.
Rules: use the ERW warehouse tools first for any energy number they can give (list_tables, then describe_table, then
query), then web search for the rest. State facts with their numbers exactly as the source gives them, and cite them.
Write "not disclosed" where a company or source does not disclose a figure. Label any estimate as an estimate and show
its arithmetic from cited numbers. Never invent a company, a number, a founder, a round or an investor."""


S_STR = {"type": "string"}
S_IDS = {"type": "array", "items": {"type": "string"}}


def obj(props, req=None):
    return {"type": "object", "additionalProperties": False, "properties": props, "required": req or list(props)}


TABLE = obj({"columns": {"type": "array", "items": S_STR},
             "rows": {"type": "array", "items": {"type": "array", "items": S_STR}}})
CHART = obj({"kind": {"type": "string", "enum": ["none", "bar", "line"]}, "title": S_STR, "category_column": {"type": "integer"},
             "value_columns": {"type": "array", "items": {"type": "integer"}}})
SCHEMAS = {
    "scope": obj({"definition": S_STR, "definition_sources": S_IDS,
                  "value_chain": {"type": "array", "items": obj({"stage": S_STR, "what_happens": S_STR, "sources": S_IDS})},
                  "excluded": {"type": "array", "items": obj({"niche": S_STR, "why_excluded": S_STR})}}),
    "fundamentals": obj({"fact": S_STR, "fact_sources": S_IDS, "numbers": {"type": "array", "items": obj(
        {"metric": S_STR, "value": S_STR, "unit": S_STR, "as_of": S_STR, "estimate_arithmetic": S_STR, "sources": S_IDS})}}),
    "trends": obj({"trends": {"type": "array", "items": obj(
        {"title": S_STR, "fact": S_STR, "table": TABLE, "chart": CHART,
         "analysis_template": {"type": "string", "enum": ["none", "peak_premium_block", "da_rt_spread_by_hour", "forecast_error",
                                                            "curtailment_midday", "implied_heat_rate", "storage_evening_peak",
                                                            "negative_price_hours", "deals_by_month", "datacenters_by_state"]},
         "sources": S_IDS})}}),
    "landscape": obj({"fact": S_STR, "fact_sources": S_IDS, "companies": {"type": "array", "items": obj(
        {"name": S_STR, "website": S_STR, "description": S_STR, "founders": S_STR, "stage": S_STR, "raised": S_STR,
         "location": S_STR, "signal": S_STR, "sources": S_IDS, "independent_sources": {"type": "integer"},
         "latest_source_year": S_STR, "stage_primary": {"type": "boolean"}, "raised_primary": {"type": "boolean"}})}}),
    "capital": obj({"fact": S_STR, "fact_sources": S_IDS, "rounds": {"type": "array", "items": obj(
        {"date": S_STR, "company": S_STR, "kind": S_STR, "amount": S_STR, "currency": S_STR, "investors": S_STR,
         "sources": S_IDS, "investors_spans": {"type": "array", "items": S_STR}, "date_span": S_STR})}}),
    "incumbents": obj({"fact": S_STR, "fact_sources": S_IDS, "players": {"type": "array", "items": obj(
        {"name": S_STR, "kind": S_STR, "ticker": S_STR, "metric": S_STR, "value": S_STR, "as_of": S_STR, "sources": S_IDS})}}),
    "policy": obj({"fact": S_STR, "actions": {"type": "array", "items": obj({"event_id": S_STR, "why_it_matters": S_STR})}}),
    "risks": obj({"risks": {"type": "array", "items": obj(
        {"risk": S_STR, "how_it_breaks_the_thesis": S_STR, "not_known": S_STR, "sources": S_IDS})}}),
}
STRUCT_SYSTEM = """You turn research notes into one sheet of an investor's market map, as JSON. Use only facts in the
notes and the numbered sources; cite each row with the ids of the sources (S#, E#) it rests on, and only ids that
support it. Every number must be written exactly as the cited source gives it. Where a source does not give a figure,
write "not disclosed". An estimate is written as "estimate: <value>" with its arithmetic in estimate_arithmetic. Leave out
any row you cannot source. Plain, precise, no hype.
Capital rows: investors_spans are exact quotes, copied from the cited passages, that name each investor; date_span is the
exact quote that gives the date. A field without its quote is left empty.
Landscape: public companies (listed on an exchange) belong on Incumbents, not Landscape."""


# ---------------------------------------------------------------------------------------------
# checks
# ---------------------------------------------------------------------------------------------

def check_numbers(r, text, ids, log, where):
    """The text with every number not found in the cited sources replaced by "not confirmed"."""
    import ask as chat_ask
    if not text or not re.search(r"\d", text):
        return text
    pool = r.texts_of(ids)
    bad = chat_ask.unverified(text, pool) if pool else re.findall(r"\d[\d,.]*", text)
    if bad:
        log(f"    {where}: numbers not in the cited sources {bad[:6]}; written as not confirmed")
        return "not confirmed" if len(text) < 40 or not pool else text + f" (not confirmed: {', '.join(bad[:4])})"
    return text


PUBLIC = re.compile(r"\b(public(ly)? (company|listed|traded)|public\b|NASDAQ|NYSE|Nasdaq|TSX|LSE|IPO)\b")
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November",
          "December"]


def is_public(c):
    """Session 26 ruling: a company listed on an exchange is an incumbent. Read from its stage and raised cells."""
    return bool(PUBLIC.search(f"{c.get('stage', '')} {c.get('raised', '')}"))


def ticker_of(c):
    m = re.search(r"\b(NASDAQ|Nasdaq|NYSE|TSX|LSE)\s*:\s*([A-Z.]{1,6})", f"{c.get('stage', '')} {c.get('raised', '')}")
    return f"{m.group(1).upper()}: {m.group(2)}" if m else ""


def _norm(t):
    return re.sub(r"\s+", " ", (t or "").replace("\u2019", "'")).strip().casefold()


def date_forms(date):
    """The ways a source may write a date given as YYYY, YYYY-MM or YYYY-MM-DD (session 26: a date restated in another
    format is accepted when the date appears in the source)."""
    m = re.fullmatch(r"(\d{4})(?:-(\d{2}))?(?:-(\d{2}))?", (date or "").strip())
    if not m:
        return [date] if date else []
    y, mo, d = m.group(1), m.group(2), m.group(3)
    if not mo:
        return [y]
    name = MONTHS[int(mo) - 1]
    short = name[:3]
    if not d:
        return [f"{name} {y}", f"{short} {y}", f"{short}. {y}", f"{y}-{mo}", f"{int(mo)}/{y}"]
    di = int(d)
    return [f"{y}-{mo}-{d}", f"{name} {di}, {y}", f"{short} {di}, {y}", f"{short}. {di}, {y}", f"{di} {name} {y}",
            f"{int(mo)}/{di}/{y}", f"{name} {di}"]


def capital_checked(r, x, log):
    """Session 26 ruling: investor names and dates in a Capital row need a quoted span from a cited source, like the
    policy reads; else the field is blank. A run that asked for spans (investors_spans, date_span) keeps a field only
    when its spans are in the sources' cited passages; a saved state from before the ruling has no spans, and there a name
    counts only if it appears verbatim in those passages (the name is its own quote), and a date only if the passages
    write it in one of its forms (date_forms)."""
    texts = r.texts_of(x["sources"])
    pool = _norm(" ".join(texts))
    spans = [sp for sp in (x.get("investors_spans") or []) if sp.strip()]
    if spans:
        investors = x["investors"] if all(_norm(sp) in pool for sp in spans) else ""
    else:
        names = [n.strip(" .") for n in re.split(r",|;| and |\bwith\b|\bled by\b|\bco-led by\b|\(|\)", x["investors"] or "")]
        names = [n for n in names if len(n) > 2 and n.lower() not in ("not disclosed", "others", "existing investors", "lead",
                                                                           "anchor", "strategic investments from")]
        # a phrase before a name ("strategic investments from JERA") is not part of it; a name starts with a capital
        names = [re.sub(r"^[a-z0-9$ .,%-]*from\s+", "", n).strip() for n in names]
        kept = [n for n in names if n[:1].isupper() and _norm(n) in pool]
        investors = "; ".join(dict.fromkeys(kept))
    if (x["investors"] or "").strip().lower().startswith(("not disclosed", "not named")):
        investors = "not disclosed"  # a statement that none is named, not a name: kept as the builder's standard phrase
    if x.get("date_span"):
        date = x["date"] if _norm(x["date_span"]) in pool else ""
    else:
        date = x["date"] if any(_norm(f) in pool for f in date_forms(x["date"])) else ""
    if investors != (x["investors"] or "") or date != x["date"]:
        log(f"    capital {x['company']}: date {x['date']!r} -> {date!r}; investors {x['investors']!r} -> {investors!r}")
    return date, investors


def confidence(c):
    """0 to 100 from the evidence, with the clause that explains it: independent sources (up to 3 count, 20 each),
    recency of the latest source (20 if this year or last, 10 if two to three years, else 0), and a primary source
    confirming the stage (10) and the amount raised (10)."""
    n = max(0, min(3, int(c.get("independent_sources") or len(c.get("sources") or []))))
    try:
        age = dt.date.today().year - int(str(c.get("latest_source_year") or "")[:4])
    except ValueError:
        age = 99
    rec = 20 if age <= 1 else 10 if age <= 3 else 0
    sp, rp = bool(c.get("stage_primary")), bool(c.get("raised_primary"))
    score = 20 * n + rec + 10 * sp + 10 * rp
    clause = (f"{n} independent source{'s' if n != 1 else ''}, latest {c.get('latest_source_year') or 'undated'}; "
              f"stage {'confirmed' if sp else 'not confirmed'} and raised {'confirmed' if rp else 'not confirmed'} by a primary source")
    return score, clause


# ---------------------------------------------------------------------------------------------
# the workbook
# ---------------------------------------------------------------------------------------------

class Book:
    def __init__(self, title):
        from openpyxl import Workbook
        self.wb = Workbook()
        self.wb.remove(self.wb.active)
        self.title = title
        self.cells = {}  # source id -> [cell refs]

    def sheet(self, name, heading):
        from openpyxl.styles import Font
        ws = self.wb.create_sheet(name)
        ws.sheet_view.showGridLines = False
        ws.column_dimensions["A"].width = 2
        for col, w in zip("BCDEFGHIJ", (28, 26, 22, 18, 18, 18, 18, 18, 18)):
            ws.column_dimensions[col].width = w
        ws["B1"] = heading
        ws["B1"].font = Font(name="Georgia", size=16, bold=True, color=CARDINAL)
        ws["B2"] = self.title
        ws["B2"].font = Font(name="Georgia", size=11, italic=True, color=INK)
        ws._erw_row, ws._erw_n = 4, 0
        return ws

    def bar(self, ws, text, width=8):
        from openpyxl.styles import Alignment, Font, PatternFill
        ws._erw_n += 1
        r = ws._erw_row
        ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=1 + width)
        c = ws.cell(r, 2, f"({ws._erw_n}) {text.upper()}")
        c.font = Font(name="Georgia", size=11, bold=True, color=WHITE)
        c.fill = PatternFill("solid", fgColor=CARDINAL)
        c.alignment = Alignment(vertical="center")
        ws.row_dimensions[r].height = 20
        ws._erw_row += 1

    def para(self, ws, label, text, width=8, color=INK, italic=False):
        from openpyxl.cell.rich_text import CellRichText, TextBlock
        from openpyxl.cell.text import InlineFont
        from openpyxl.styles import Alignment
        r = ws._erw_row
        ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=1 + width)
        c = ws.cell(r, 2)
        body = InlineFont(rFont="Calibri", sz=10, color=color, i=italic)
        c.value = CellRichText([TextBlock(InlineFont(rFont="Calibri", sz=10, b=True, color=color, i=italic), label + " "),
                                TextBlock(body, text)]) if label else CellRichText([TextBlock(body, text)])
        c.alignment = Alignment(wrap_text=True, vertical="top")
        ws.row_dimensions[r].height = max(15, 15 * (len(text) // 120 + 1))
        ws._erw_row += 1
        return f"'{ws.title}'!B{r}"

    def table(self, ws, columns, rows, row_sources=None):
        from openpyxl.styles import Alignment, Font, PatternFill
        r0 = ws._erw_row
        for j, h in enumerate(columns):
            c = ws.cell(r0, 2 + j, h)
            c.font = Font(name="Calibri", size=10, bold=True, color=WHITE)
            c.fill = PatternFill("solid", fgColor=CARDINAL)
            c.alignment = Alignment(wrap_text=True, vertical="center")
        for i, row in enumerate(rows, 1):
            for j, v in enumerate(row):
                c = ws.cell(r0 + i, 2 + j, v)
                c.font = Font(name="Calibri", size=10, color=INK)
                c.alignment = Alignment(wrap_text=True, vertical="top")
                if i % 2 == 0:
                    c.fill = PatternFill("solid", fgColor=FOG)
            ref = f"'{ws.title}'!B{r0 + i}:{chr(65 + len(columns))}{r0 + i}"
            for sid in (row_sources[i - 1] if row_sources else []):
                self.cells.setdefault(sid, []).append(ref)
        ws._erw_row = r0 + len(rows) + 1
        return r0

    def chart(self, ws, r0, n_rows, spec):
        from openpyxl.chart import BarChart, LineChart, Reference
        if not spec or spec.get("kind") in (None, "none") or n_rows < 2:
            return
        ch = BarChart() if spec["kind"] == "bar" else LineChart()
        ch.title = spec.get("title") or ""
        ch.style = 2
        ch.height, ch.width = 7, 16
        cat = 2 + int(spec.get("category_column") or 0)
        for vc in spec.get("value_columns") or []:
            col = 2 + int(vc)
            ch.add_data(Reference(ws, min_col=col, min_row=r0, max_row=r0 + n_rows), titles_from_data=True)
        ch.set_categories(Reference(ws, min_col=cat, min_row=r0 + 1, max_row=r0 + n_rows))
        for i, s in enumerate(ch.series):
            color = [CARDINAL, "007C92", "E98300", "175E54"][i % 4]
            s.graphicalProperties.solidFill = color
            s.graphicalProperties.line.solidFill = color
        ws.add_chart(ch, f"B{ws._erw_row}")
        ws._erw_row += 15

    def image(self, ws, path):
        from openpyxl.drawing.image import Image
        img = Image(path)
        img.width, img.height = 720, 450
        ws.add_image(img, f"B{ws._erw_row}")
        ws._erw_row += 24

    def sources_line(self, ws, ids, r):
        by = {s["id"]: s for s in r.sources.values()}
        erw = {e["id"]: e for e in r.erw}
        names = []
        for i in dict.fromkeys(ids or []):
            if i in by:
                names.append(f"{i} {by[i]['title'][:60] or by[i]['url']}")
            elif i in erw:
                names.append(f"{i} ERW table {erw[i]['args'].get('table', erw[i]['tool'])}")
        ref = self.para(ws, "Source(s):", "; ".join(names) if names else "none", color=GREY, italic=True)
        for i in ids or []:
            self.cells.setdefault(i, []).append(ref)
        ws._erw_row += 1


# ---------------------------------------------------------------------------------------------
# energy_companies
# ---------------------------------------------------------------------------------------------

ENT_COLS = ["entity_id", "entity_type", "name", "geo", "lat", "lon", "capacity_mw", "status", "status_date", "operator",
            "source", "source_url", "retrieved_at", "vintage", "description", "sector", "niche_tags", "stage", "raised",
            "location", "founders", "website", "sources", "confidence", "confidence_note", "first_seen"]


def domain(url):
    m = re.match(r"https?://(?:www\.)?([^/]+)", (url or "").strip().lower())
    return m.group(1) if m else ""


def company_id(name, website):
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return f"erwco:{slug}" + (f"@{domain(website)}" if domain(website) else "")


def merge_companies(rows, niche, run_id, log):
    path = os.path.join(ip.OUT_DIR, NAME + ".csv")
    old = None
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            skip = sum(1 for ln in f if ln.startswith("#"))
        old = pd.read_csv(path, skiprows=skip, dtype=str, keep_default_na=False)
    new = pd.DataFrame(rows, columns=ENT_COLS)
    if old is not None and len(old):
        merged = []
        oldk = {(o["name"].lower(), domain(o["website"])): o for o in old.to_dict("records")}
        seen = set()
        for n_ in new.to_dict("records"):
            k = (n_["name"].lower(), domain(n_["website"]))
            o = oldk.get(k)
            if o:
                seen.add(k)
                n_["niche_tags"] = ";".join(sorted(set(filter(None, o["niche_tags"].split(";") + n_["niche_tags"].split(";")))))
                n_["sources"] = ";".join(dict.fromkeys(filter(None, o["sources"].split(";") + n_["sources"].split(";"))))
                n_["first_seen"] = min(o["first_seen"], n_["first_seen"])
                if int(o["confidence"] or 0) > int(n_["confidence"] or 0):
                    for c in ("description", "stage", "raised", "location", "founders", "confidence", "confidence_note"):
                        n_[c] = o[c]
            merged.append(n_)
        merged += [o for k, o in oldk.items() if k not in seen]
        new = pd.DataFrame(merged, columns=ENT_COLS)
    new = new.drop_duplicates("entity_id", keep="first").sort_values("entity_id")
    header = [
        "Energy Research Warehouse (ERW): energy companies found by the Thesis Builder (tool 27), the seed of the company "
        "database (tool 10)",
        "Shape: entities (docs/datastandard.md v0), entity_type company; one row per company, merged on name plus website. "
        "The fields are the model's, from public web sources it cites (sources); a number that did not appear in a cited "
        "source is written as not confirmed. confidence 0 to 100 by the rule in warehouse/thesis/build.py, explained in "
        "confidence_note. No licensed data (warehouse/thesis/connectors/ rows never enter this table).",
        f"Retrieved: {run_id} (UTC) by warehouse/thesis/build.py for the niche \"{niche}\"",
        f"Run log: warehouse/output/logs/thesis_{run_id}.log",
        "Source: erw:thesis_builder (public web sources, each row's sources column).",
        "License: public (names, one-line descriptions written by the ERW, and links).",
    ]
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        for ln in header:
            f.write("# " + ln + "\n")
        new.to_csv(f, index=False, lineterminator="\n")
    os.replace(tmp, path)
    ip.update_sources([dict(source="erw:thesis_builder", publisher="Energy Research Warehouse (ERW)",
                            report="Thesis Builder company finds (warehouse/thesis/build.py), from public web sources",
                            report_url="https://github.com/SamuelEnrique/erw/blob/main/docs/methods/thesis_builder.md",
                            document_list="", license="public", tables=[NAME])])
    log(f"  {NAME}: {len(rows)} companies from this run, {len(new)} in the table")


# ---------------------------------------------------------------------------------------------
# the run
# ---------------------------------------------------------------------------------------------

def policy_candidates(niche_words):
    path = os.path.join(ip.OUT_DIR, "policy_actions.csv")
    if not os.path.exists(path):
        return pd.DataFrame()
    with open(path, encoding="utf-8") as f:
        skip = sum(1 for ln in f if ln.startswith("#"))
    a = pd.read_csv(path, skiprows=skip, dtype=str, keep_default_na=False)
    pat = "|".join(re.escape(w) for w in niche_words)
    m = a[(a["title"] + " " + a["abstract"] + " " + a["sector_tags"]).str.contains(pat, case=False, regex=True)]
    m = m.assign(sig=pd.to_numeric(m["significance"], errors="coerce").fillna(0)).sort_values("sig", ascending=False)
    return m.head(40)


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW Thesis Builder v0 (tool 27)")
    ap.add_argument("niche")
    ap.add_argument("--stage", default="")
    ap.add_argument("--geography", default="")
    ap.add_argument("--out")
    ap.add_argument("--max-usd", type=float, default=6.0)
    ap.add_argument("--searches", type=int, default=12, help="web searches per research pass (at most)")
    ap.add_argument("--resume", help="a saved state (warehouse/output/thesis_state/*.json): write the workbook without new calls")
    args = ap.parse_args(argv)
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"thesis_{run_id}.log"))
    t0 = time.time()
    slug = re.sub(r"[^a-z0-9]+", "-", args.niche.lower()).strip("-")[:60]
    out = args.out or os.path.join(ROOT, "docs", "thesis", f"{slug}.xlsx")
    status = dict(table=NAME, market="thesis", status="ok", detail="")
    try:
        state_path = os.path.join(ip.OUT_DIR, "thesis_state", f"{slug}_{run_id}.json")
        if args.resume:  # rebuild the workbook from a saved state: no model call
            st = json.load(open(args.resume, encoding="utf-8"))
            r = Researcher.__new__(Researcher)
            r.log, r.max_usd, r.model, r.cost, r.calls, r.searches = log, args.max_usd, st["model"], st["cost"], st["calls"], st["searches"]
            r.sources, r.erw, sheets, notes = st["sources"], st["erw"], st["sheets"], st["notes"]
            pol = pd.DataFrame(st["pol"])
            log(f"resumed from {args.resume}: {r.calls} calls, USD {r.cost:.4f} (no new call)")
        else:
            r = Researcher(log, args.max_usd)
            log(f"niche {args.niche!r}; stage {args.stage or 'any'}; geography {args.geography or 'any'}; model {r.model}")
            sysm = base_system(args.niche, args.stage, args.geography)
            notes_a = r.research("research: scope, fundamentals, trends", sysm, (
                "Research (1) what this niche is exactly, its value chain from input to customer, and the adjacent niches an "
                "investor should keep out of scope; (2) the framing numbers: market size, installed base, costs, prices, "
                "volumes, with the warehouse first (its tables: prices, generation by fuel and state, the generator inventory, "
                "interconnection queues, curtailment, batteries, deals, policy actions); (3) three to five trends, each with "
                "the numbers behind it, preferring a warehouse table where one exists. Write notes: one fact per sentence, "
                "cited."), args.searches)
            notes_b = r.research("research: companies, capital, incumbents", sysm, (
                "Research every company working in this niche (startups and scale-ups first): name, website, what it does in "
                "one line, founders, stage, amount raised, location, and the signal that surfaced it (a round, a grant, a "
                "pilot, a customer, a patent). Then the capital: venture rounds, grants, project finance and M&A in the "
                "niche with dates, amounts and investors (check the warehouse table energy_deals too). Then the incumbents "
                "and public comparables, with the one metric that matters for each. Prefer primary sources (the company, "
                "the investor, a filing). Write notes: one fact per sentence, cited."), args.searches + 6)
            notes_c = r.research("research: risks", sysm, (
                "Research what could break an investment thesis in this niche: technical, market, regulatory and financing "
                "risks, and what is not known yet. Cite each. Write notes: one fact per sentence, cited."),
                max(4, args.searches // 2), erw_tools=False)
            notes = f"{notes_a}\n\n{notes_b}\n\n{notes_c}"
            words = [w for w in re.findall(r"[a-z]{5,}", args.niche.lower()) if w not in {"merchant", "operators", "software", "mapping"}]
            pol = policy_candidates(words or [args.niche])
            sheets = {}
            for key in ("scope", "fundamentals", "trends", "landscape", "capital", "incumbents", "risks"):
                sheets[key] = r.structure(f"structure: {key}", f"Write the sheet: {key}. Niche: {args.niche}.", notes,
                                          SCHEMAS[key])
                log(f"  {key}: structured")
            if len(pol):
                cand = "\n".join(f"{x['event_id']} | {x['agency']} {x['action_type']} {x['event_date']} | {x['title'][:200]} | "
                                 f"significance {x['significance']}" for x in pol.to_dict("records"))
                sheets["policy"] = r.structure("structure: policy", "Write the sheet: policy. Pick from these candidate policy "
                                               "actions (the ERW table policy_actions) only those that bear on the niche, by "
                                               f"event_id. Niche: {args.niche}.\n\nCandidate policy actions:\n" + cand, notes,
                                               SCHEMAS["policy"])
            else:
                sheets["policy"] = {"fact": "", "actions": []}

            # the state, so the workbook can be rebuilt without calling the model again (--resume)
            os.makedirs(os.path.dirname(state_path), exist_ok=True)
            json.dump({"niche": args.niche, "model": r.model, "cost": r.cost, "calls": r.calls, "searches": r.searches,
                       "sources": r.sources, "erw": r.erw, "sheets": sheets, "notes": notes,
                       "pol": pol.to_dict("records") if len(pol) else []},
                      open(state_path, "w", encoding="utf-8"), default=str)
            log(f"state saved: {os.path.relpath(state_path, ROOT)}")
        # licensed connectors, if a credential is present: workbook only
        try:
            from connectors import available as licensed_connectors
        except ImportError:
            licensed_connectors = list
        licensed = {"landscape": [], "capital": []}
        for conn in licensed_connectors():
            try:
                licensed["landscape"] += conn.landscape(args.niche)
                licensed["capital"] += conn.capital(args.niche)
                log(f"  licensed connector {conn.NAME}: rows added to the workbook only")
            except Exception as exc:
                log(f"  licensed connector {conn.NAME} FAILED: {ip.redact(repr(exc))[:200]}")

        book = Book(f"{args.niche}" + (f", {args.stage}" if args.stage else "") + (f", {args.geography}" if args.geography else ""))
        write_book(book, r, sheets, pol, licensed, args, log)
        companies = company_rows(r, sheets["landscape"], args.niche, run_id)
        merge_companies(companies, args.niche, run_id, log)
        secs = time.time() - t0
        ws = book.wb["Scope"]
        book.para(ws, "Built:", f"{dt.datetime.now(dt.timezone.utc):%Y-%m-%d %H:%M} UTC by warehouse/thesis/build.py, run "
                  f"{run_id}; {r.calls} model calls ({r.model}), {r.searches} web searches, USD {r.cost:.4f}, {secs / 60:.1f} "
                  "minutes. Numbers not found in a cited source are written as not confirmed.", color=GREY, italic=True)
        write_sources(book, r)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        book.wb.save(out)
        n_sec = {s.title: s._erw_n for s in book.wb.worksheets}
        status["detail"] = (f"{os.path.relpath(out, ROOT)}: {r.calls} calls, {r.searches} searches, USD {r.cost:.4f}, "
                            f"{secs / 60:.1f} min; sections {n_sec}; companies {len(companies)}")
        log(status["detail"])
        print(f"thesis: {status['detail']}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED:\n{tb}")
        print(f"thesis FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        status.update(status="failed", detail=tb.strip().splitlines()[-1][:300])
    ip.write_status("thesis", run_id, [status])
    log.close()
    return 0 if status["status"] == "ok" else 1


def company_rows(r, land, niche, run_id):
    rows, today = [], dt.date.today().isoformat()
    by = {s["id"]: s for s in r.sources.values()}
    for c in land.get("companies", []):
        if not c.get("sources"):
            continue
        score, clause = confidence(c)
        if is_public(c):  # session 26 ruling: a public company's raised cell is blank, noted
            c["_raised"], clause = "", "public company; " + clause
        urls = [by[i]["url"] for i in c["sources"] if i in by]
        rows.append({"entity_id": company_id(c["name"], c["website"]), "entity_type": "company", "name": c["name"].strip(),
                     "geo": "", "lat": "", "lon": "", "capacity_mw": "", "status": "", "status_date": "", "operator": "",
                     "source": "erw:thesis_builder", "source_url": urls[0] if urls else (c["website"] or ""),
                     "retrieved_at": ip.utc_iso(pd.Timestamp.now(tz="UTC")), "vintage": run_id,
                     "description": c["description"].replace(EM, ","), "sector": "energy technology",
                     "niche_tags": niche, "stage": c["_stage"], "raised": c["_raised"], "location": c["location"],
                     "founders": c["founders"], "website": c["website"], "sources": ";".join(urls), "confidence": str(score),
                     "confidence_note": clause, "first_seen": today})
    return [x for x in rows if x["source_url"]]


def write_book(book, r, sheets, pol, licensed, args, log):
    import templates as tpl
    # Scope
    ws = book.sheet("Scope", "Scope")
    s = sheets["scope"]
    book.bar(ws, "Definition")
    book.para(ws, "Fact:", check_numbers(r, s["definition"], s["definition_sources"], log, "scope definition"))
    book.sources_line(ws, s["definition_sources"], r)
    book.bar(ws, "Value chain")
    book.table(ws, ["Stage", "What happens"], [[v["stage"], v["what_happens"]] for v in s["value_chain"]],
               [v["sources"] for v in s["value_chain"]])
    book.sources_line(ws, [i for v in s["value_chain"] for i in v["sources"]], r)
    book.bar(ws, "Adjacent niches excluded")
    book.table(ws, ["Niche", "Why it is out of scope"], [[e["niche"], e["why_excluded"]] for e in s["excluded"]])
    # Fundamentals
    ws = book.sheet("Fundamentals", "Fundamentals")
    f = sheets["fundamentals"]
    book.bar(ws, "The framing numbers")
    book.para(ws, "Fact:", check_numbers(r, f["fact"], f["fact_sources"], log, "fundamentals fact"))
    rows, srcs = [], []
    for n in f["numbers"]:
        if not n["sources"]:
            continue
        val = check_numbers(r, n["value"], n["sources"], log, f"fundamentals {n['metric']}")
        if n["estimate_arithmetic"]:
            val = f"{val} (estimate: {check_numbers(r, n['estimate_arithmetic'], n['sources'], log, 'estimate')})"
        erw_first = any(i.startswith("E") for i in n["sources"])
        rows.append([n["metric"], val, n["unit"], n["as_of"], ", ".join(n["sources"]) + (" (ERW)" if erw_first else "")])
        srcs.append(n["sources"])
    rows.sort(key=lambda x: 0 if x[4].endswith("(ERW)") else 1)  # the warehouse's numbers first
    book.table(ws, ["Metric", "Value", "Unit", "As of", "Source"], rows, srcs)
    book.sources_line(ws, [i for x in srcs for i in x] + f["fact_sources"], r)
    # Trends
    ws = book.sheet("Trends", "Trends")
    mods = {m.NAME: m for m in tpl.load_all()}
    for t in sheets["trends"]["trends"][:5]:
        book.bar(ws, t["title"])
        book.para(ws, "Fact:", check_numbers(r, t["fact"], t["sources"], log, f"trend {t['title'][:40]}"))
        tab = t["table"]
        if tab["columns"] and tab["rows"]:
            rows = [[check_numbers(r, v, t["sources"], log, "trend table") for v in row[:len(tab["columns"])]]
                    for row in tab["rows"]]
            r0 = book.table(ws, tab["columns"], rows, [t["sources"]] * len(rows))
            # a chart only from rows whose values survived the check as numbers
            if all(re.fullmatch(r"-?[\d,.]+%?", str(row[c]).strip() or "x") for row in rows
                   for c in (t["chart"].get("value_columns") or [])):
                for row_i, row in enumerate(rows, 1):
                    for c in t["chart"].get("value_columns") or []:
                        cell = ws.cell(r0 + row_i, 2 + c)
                        try:
                            cell.value = float(str(row[c]).replace(",", "").rstrip("%"))
                        except ValueError:
                            pass
                book.chart(ws, r0, len(rows), t["chart"])
        name = t.get("analysis_template")
        if name and name != "none" and name in mods and mods[name].PUBLIC:
            try:
                res = mods[name].compute()
                png = os.path.join(ROOT, "warehouse", "output", "thesis_charts", f"{name}.png")
                mods[name].render(res, "email", png)
                book.image(ws, png)
                book.para(ws, "Chart:", f"ERW Automated Analysis template {name}. {res['source_line']}", color=GREY, italic=True)
            except Exception as exc:
                log(f"    template {name}: not drawn ({ip.redact(repr(exc))[:150]})")
        book.sources_line(ws, t["sources"], r)
    # Landscape
    ws = book.sheet("Landscape", "Landscape")
    land = sheets["landscape"]
    book.bar(ws, "Companies")
    book.para(ws, "Fact:", check_numbers(r, land["fact"], land["fact_sources"], log, "landscape fact"))
    rows, srcs = [], []
    moved = []  # session 26 ruling: public companies stay on Incumbents and off Landscape
    for c in land["companies"]:
        if not c["sources"]:
            continue
        if is_public(c):
            c["_stage"] = check_numbers(r, c["stage"], c["sources"], log, f"{c['name']} stage") or "not disclosed"
            c["_raised"] = ""
            moved.append(c)
            log(f"    {c['name']}: public company, moved from Landscape to Incumbents")
            continue
        c["_stage"] = check_numbers(r, c["stage"], c["sources"], log, f"{c['name']} stage") or "not disclosed"
        c["_raised"] = check_numbers(r, c["raised"], c["sources"], log, f"{c['name']} raised") or "not disclosed"
        score, clause = confidence(c)
        rows.append([c["name"], c["description"], c["founders"] or "not disclosed", c["_stage"], c["_raised"], c["location"],
                     c["signal"], ", ".join(c["sources"]), f"{score}: {clause}"])
        srcs.append(c["sources"])
    for x in licensed["landscape"]:
        rows.append([x.get("name", ""), x.get("description", ""), x.get("founders", ""), x.get("stage", ""),
                     x.get("raised", ""), x.get("location", ""), "licensed", "licensed, user's own account, not stored in the ERW",
                     ""])
        srcs.append([])
    book.table(ws, ["Company", "What it does", "Founders", "Stage", "Raised", "Location", "Signal", "Sources",
                    "Confidence (0 to 100)"], rows, srcs)
    book.sources_line(ws, [i for x in srcs for i in x], r)
    # Capital
    ws = book.sheet("Capital", "Capital")
    cap = sheets["capital"]
    book.bar(ws, "Rounds, project finance and M&A")
    book.para(ws, "Fact:", check_numbers(r, cap["fact"], cap["fact_sources"], log, "capital fact"))
    rows, srcs = [], []
    for x in cap["rounds"]:
        if not x["sources"]:
            continue
        date, investors = capital_checked(r, x, log)
        rows.append([date, x["company"], x["kind"], check_numbers(r, x["amount"], x["sources"], log, f"{x['company']} amount")
                     or "not disclosed", x["currency"], investors, ", ".join(x["sources"])])
        srcs.append(x["sources"])
    for x in licensed["capital"]:
        rows.append([x.get("date", ""), x.get("company", ""), x.get("kind", ""), x.get("amount", ""), x.get("currency", ""),
                     x.get("investors", ""), "licensed, user's own account, not stored in the ERW"])
        srcs.append([])
    book.table(ws, ["Date", "Company", "Kind", "Amount", "Currency", "Investors", "Sources"], rows, srcs)
    book.sources_line(ws, [i for x in srcs for i in x], r)
    # Incumbents
    ws = book.sheet("Incumbents", "Incumbents")
    inc = sheets["incumbents"]
    book.bar(ws, "Large players and public comparables")
    book.para(ws, "Fact:", check_numbers(r, inc["fact"], inc["fact_sources"], log, "incumbents fact"))
    rows, srcs = [], []
    for x in inc["players"]:
        if not x["sources"]:
            continue
        rows.append([x["name"], x["kind"], x["ticker"] or "", x["metric"],
                     check_numbers(r, x["value"], x["sources"], log, f"{x['name']} metric") or "not disclosed", x["as_of"],
                     ", ".join(x["sources"])])
        srcs.append(x["sources"])
    have = {x["name"].split(" (")[0].split(",")[0].strip().lower() for x in inc["players"]}
    for c in moved:
        key = c["name"].split(" (")[0].split(",")[0].strip().lower()
        if key in have or any(key.split()[0] == h.split()[0] for h in have if h):
            continue
        rows.append([c["name"], "public company (from Landscape)", ticker_of(c), "not stated", "not disclosed", "",
                     ", ".join(c["sources"])])
        srcs.append(c["sources"])
    book.table(ws, ["Name", "Kind", "Ticker", "Metric that matters", "Value", "As of", "Sources"], rows, srcs)
    book.sources_line(ws, [i for x in srcs for i in x], r)
    # Policy
    ws = book.sheet("Policy", "Policy")
    book.bar(ws, "Policy actions (ERW tables policy_actions and policy_reads)")
    p = sheets["policy"]
    if p["fact"]:
        book.para(ws, "Fact:", p["fact"])
    reads = {}
    rp = os.path.join(ip.OUT_DIR, "policy_reads.csv")
    if os.path.exists(rp):
        with open(rp, encoding="utf-8") as fh:
            skip = sum(1 for ln in fh if ln.startswith("#"))
        reads = {x["action_event_id"]: x for x in pd.read_csv(rp, skiprows=skip, dtype=str, keep_default_na=False).to_dict("records")}
    polmap = {x["event_id"]: x for x in pol.to_dict("records")} if len(pol) else {}
    rows = []
    for a in p["actions"]:
        x = polmap.get(a["event_id"])
        if not x:
            continue
        rd = reads.get(x["event_id"], {})
        rows.append([x["event_date"], x["agency"], x["action_type"].replace("_", " "), x["title"][:200],
                     rd.get("plain_read") or a["why_it_matters"], x["source_url"]])
    book.table(ws, ["Date", "Agency", "Type", "Title", "Read (policy_reads) or why it matters", "Link"], rows)
    book.para(ws, "Source(s):", "ERW tables policy_actions (Federal Register and agency news) and policy_reads (impact reads, "
              "fields kept only when their words are in the action's own text).", color=GREY, italic=True)
    # Risks
    ws = book.sheet("Risks", "Risks")
    for x in sheets["risks"]["risks"]:
        if not x["sources"]:
            continue
        book.bar(ws, x["risk"])
        book.para(ws, "Fact:", check_numbers(r, x["how_it_breaks_the_thesis"], x["sources"], log, "risk"))
        book.para(ws, "Not known:", x["not_known"] or "not stated")
        book.sources_line(ws, x["sources"], r)


def write_sources(book, r):
    ws = book.sheet("Sources", "Sources")
    book.bar(ws, "Every source, its retrieval date and the cells it supports")
    rows = []
    for s in r.sources.values():
        rows.append([s["id"], s["title"][:150], s["url"], s["retrieved"], s["page_age"],
                     "; ".join(dict.fromkeys(book.cells.get(s["id"], []))) or "searched, not cited in a cell"])
    for e in r.erw:
        rows.append([e["id"], f"ERW {e['tool']} {e['args'].get('table', '')}".strip(),
                     "https://github.com/SamuelEnrique/erw (" + (e["args"].get("table") or e["tool"]) + ")",
                     dt.date.today().isoformat(), "", "; ".join(dict.fromkeys(book.cells.get(e["id"], []))) or "queried, not cited in a cell"])
    book.table(ws, ["Id", "Title", "URL", "Retrieved", "Page age", "Cells it supports"], rows)


if __name__ == "__main__":
    sys.exit(main())
