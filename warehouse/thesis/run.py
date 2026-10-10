#!/usr/bin/env python3
"""Thesis Builder as a tool of the site (session 135): one run, from a niche to the report /thesis draws.

Energy Research Warehouse (ERW), platform tool 27. warehouse/thesis/build.py (session 25) writes a workbook from the
command line. This module is the server side of the page /thesis: a person types a niche there, a row is queued in
the internal table public.thesis_runs (migration 024), and this runs it and writes the report back into that row.
Runs and their results stay in that table: nothing is merged into energy_companies or any public table, nothing goes
to Redivis, and no file under site/ or docs/ is written.

    python warehouse/thesis/run.py --run-id <id>            # the workflow: one queued run
    python warehouse/thesis/run.py --queue                  # every queued run, oldest first
    python warehouse/thesis/run.py --niche "..." [--stage ...] [--geography ...] --store      # a run started here
    python warehouse/thesis/run.py --niche "..." --landscape-from <state.json> --store        # the landscape stage again
                                                                                               # on a saved run's trends
    python warehouse/thesis/run.py --niche "..." --landscape-from bucket:<name> --store       # session 158: the same, from
                                                                                               # a state kept in the private
                                                                                               # bucket (the runner holds no
                                                                                               # file of an earlier run)

The order of work (the full method is internal: docs/methods/thesis_builder.md; what a reader may know is in
docs/methods/thesis.md):

  1. Research the niche's scope, definitions and trends (web search and the warehouse's read-only tools).
  2. Write the scope and exactly five trends as data; each trend names its own search phrases.
  3. The company landscape, from three kinds of source:
       a. the warehouse: energy_companies and energy_deals, rows matching the niche's own words (no model);
       b. web search by a STATED QUERY PLAN: fixed niche-level queries and two queries per trend, built here in code
          from the niche and the trends' phrases, run once each, in order. The plan is saved with the run's state;
       c. the PitchBook stage: a request this run writes for the user's own Claude connector (the ERW cannot sign in
          to PitchBook). Its answer arrives later and is kept beside the report, every figure labeled PitchBook's.
  4. Every organisation found is a row of the deal funnel. The SELECTION RULE is code, not the model's opinion:
       found -> a private company -> fits the stage and geography asked for -> tied to at least one of the five
       trends by a fetched source that the row cites -> on the landscape -> on the pipeline map when its
       confidence is 60 or more (at most ten, most trends served first).
     A row states the stage it reached and why it stopped.
     Session 142: "tied to a trend" is no longer the model's opinion. It is decided by warehouse/thesis/tie.py from
     saved evidence: a fixed order of evidence (the warehouse's tables, then the text of the sources fetched, then
     sentences reported from the web), a scoring a person can redo by hand, and a fixed tie-break. The evidence of a
     niche is kept in a store (--evidence-dir) that every later run of the niche reads, and each run's state records
     what changed since the run before (state["tie"]). None of it is sent to a reader.
  5. Capital, incumbents, risks, policy (the warehouse's policy_actions, as build.py does).
  6. Every number is checked against the fetched passages its row cites (build.check_numbers): one that is not
     there is not written.

Costs: every model call is logged (api_cost_ledger, step thesis). A run stops at --max-usd; --spent-file and
--session-cap hold several runs under one ceiling.
"""

import argparse
import datetime as dt
import json
import os
import re
import secrets
import sys
import time
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)


def _load(name, path):
    """A neighbouring module by its path, under a name of its own: "build" and "run" are names other folders use too."""
    import importlib.util
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


tb = _load("erw_thesis_build", os.path.join(HERE, "build.py"))      # also puts the warehouse's folders on the path
tie = _load("erw_thesis_tie", os.path.join(HERE, "tie.py"))         # session 142: the tie of a company to a trend, in code
pg = _load("erw_thesis_pages", os.path.join(HERE, "pages.py"))      # session 147: the pages a run cites, fetched in code
es = _load("erw_thesis_store", os.path.join(HERE, "store.py"))      # session 147: where the evidence store is kept
pv = _load("erw_thesis_providers", os.path.join(HERE, "providers.py"))   # session 150: the data providers of the fetch stage
sr = _load("erw_thesis_series", os.path.join(HERE, "series.py"))     # session 169: the real series a trend is drawn with
import iso_prices as ip  # noqa: E402

TABLE_DIR = None                # --in-dir: read the warehouse's tables from another folder (a working copy has few of them)

FORMAT = pv.PITCHBOOK.format     # "erw-pitchbook-1": the request a run writes is PitchBook's, as before session 150
RUN_USD = 1.0                   # one run's hard stop unless --max-usd says less (session 169: the owner lowered it from 2.00)
DAY_USD = 8.0                   # the tool's spend in a UTC day, counted from thesis_runs, for runs the page starts
PIPELINE_MIN, PIPELINE_MAX = 60, 10
STATE_DIR = os.path.join(ip.OUT_DIR, "thesis_state")
STOP = {"the", "and", "for", "with", "from", "that", "this", "into", "their", "new", "not", "general", "only", "based", "using",
        "technologies", "technology", "companies", "company", "startups", "startup", "market", "markets", "energy", "power"}
RULE = "A company is on this map when it is a private company that fits the stage and geography asked for and a fetched source ties it to at least one of the five trends."
VENDOR_MARK = "vendor page"      # session 158: shown beside a "Why it is here" sentence that comes from a data vendor's public page
VENDOR_NOTE = "This sentence is from a public page of a data vendor ({vendor}), not from the company or the press."
# Session 160: shown beside a "Why it is here" sentence read from a page's last good text, kept because the page did
# not give its text when it was asked again. The mark is the day the text was retrieved; the hover says why.
KEPT_MARK = "retrieved {day}"
KEPT_NOTE = "This sentence is from the page as it was read on {day}. The page did not give its text when it was asked again on {again}."
MONTHS = ("January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December")


def day_words(day):
    """A day (YYYY-MM-DD) as a reader sees it: 7 October 2026. A value that is not a day is returned as it is."""
    m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", str(day or "")[:10])
    return f"{int(m.group(3))} {MONTHS[int(m.group(2)) - 1]} {m.group(1)}" if m and 1 <= int(m.group(2)) <= 12 else str(day or "")
NOTE = {
    "not_disclosed": "No fetched source gives this.",
    "not_confirmed": "A figure was offered but does not appear in a fetched source, so it is not shown.",
    "tam": "No fetched source sizes this company's market.",
    "access": "Asked of PitchBook: the company's lead investors, the usual route to its founders. Shown when the PitchBook answer is submitted.",
}

S, IDS, obj = tb.S_STR, tb.S_IDS, tb.obj
INT = {"type": "integer"}
BOOL = {"type": "boolean"}
SCHEMA_A = obj({
    "scope": obj({"definition": S, "definition_sources": IDS,
                  "value_chain": {"type": "array", "items": obj({"stage": S, "what_happens": S, "sources": IDS})},
                  "excluded": {"type": "array", "items": obj({"niche": S, "why_excluded": S})},
                  "definitions": {"type": "array", "items": obj({"term": S, "meaning": S, "sources": IDS})}}),
    "trends": {"type": "array", "items": obj({
        "title": S, "fact": S, "table": tb.TABLE, "chart": tb.CHART, "unit": S,
        "search_phrases": {"type": "array", "items": S}, "sources": IDS})},
    "market_size": obj({"value": S, "what_it_measures": S, "sources": IDS}),
})
SCHEMA_L = obj({
    "fact": S, "fact_sources": IDS,
    "organisations": {"type": "array", "items": obj({
        "name": S, "website": S, "description": S,
        "kind": {"type": "string", "enum": ["private company", "public company", "subsidiary of a public company", "acquired",
                                            "university or national laboratory", "government or nonprofit", "investor", "other"]},
        "country": S, "location": S, "founders": S, "stage": S, "raised": S, "signal": S,
        "fits_stage": {"type": "string", "enum": ["yes", "no", "not stated"]},
        "trends": {"type": "array", "items": INT}, "trend_reason": S,
        "tam": S, "sources": IDS, "found_by": {"type": "array", "items": S},
        "independent_sources": INT, "latest_source_year": S, "stage_primary": BOOL, "raised_primary": BOOL,
        "evidence": {"type": "array", "items": obj({"quote": S, "source": S})}})},
})


# ---------------------------------------------------------------------------------------------
# the plan and the warehouse's own candidates (no model)
# ---------------------------------------------------------------------------------------------

def head_of(niche):
    """The niche's own name: the words before its first comma, colon or bracket."""
    return re.split(r"[,:;(]", niche, maxsplit=1)[0].strip()


# Session 169: the short words of the domain. words_of kept only words of four letters or more, so "oil" and "gas" (and
# "EV", "AI", "LNG") were never looked for: a niche named with them matched on its other words alone. A short word is
# kept when it is one of these and stands as a whole word; every longer word is read exactly as before.
SHORT = tb.SHORT
_WORD = re.compile(r"[a-z][a-z-]{3,}|(?<![a-z0-9-])(?:" + "|".join(SHORT) + r")(?![a-z0-9-])")


def words_of(text):
    return [w for w in _WORD.findall(text.lower()) if w not in STOP]


def has_word(text, w):
    """Is the word in the (lower case) text? A long word anywhere, as before; a short domain word only as a whole
    word ("oil" is not in "soil", "ev" is not in "development")."""
    return tb.short_in(text, w) if w in SHORT else w in text


def query_plan(niche, geography, trends):
    """The stated query plan: six niche-level queries and two per trend. [(id, query, what it is for)]."""
    head = head_of(niche)
    geo = f" {geography}" if geography else ""
    year = dt.date.today().year
    plan = [
        (f"{head} startups{geo}", "the niche by name"),
        (f"{head} startup funding round {year - 1} OR {year}", "recent rounds"),
        (f"{head} seed OR \"Series A\" company{geo}", "early-stage companies"),
        (f"{head} DOE OR ARPA-E OR SBIR OR NSF award company", "federal awards"),
        (f"{head} accelerator OR incubator cohort startup", "accelerators and incubators"),
        (f"{head} university OR national laboratory spinout company", "spinouts"),
    ]
    for i, t in enumerate(trends, 1):
        phrases = [p.strip() for p in (t.get("search_phrases") or []) if p.strip()][:2] or [t["title"]]
        plan.append((f"{phrases[0]} startup{geo}", f"trend {i}"))
        plan.append((f"{phrases[-1] if len(phrases) > 1 else phrases[0]} company raises funding", f"trend {i}"))
    return [(f"Q{n}", q, why) for n, (q, why) in enumerate(plan, 1)]


def read_table(name):
    import pandas as pd
    path = os.path.join(TABLE_DIR or ip.OUT_DIR, name + ".csv")
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        skip = sum(1 for ln in f if ln.startswith("#"))
    return pd.read_csv(path, skiprows=skip, dtype=str, keep_default_na=False)


def warehouse_candidates(niche, r, log, cap=40):
    """Rows of energy_companies and energy_deals that carry the niche's own words: the longest word of its name must
    be there, and a row with more of the name's words comes first. Each becomes a numbered ERW source the model may cite."""
    head = words_of(head_of(niche))
    if not head:
        return []
    anchor = max(head, key=len)
    out = []
    comp = read_table("energy_companies")
    if comp is not None:
        for x in comp.to_dict("records"):
            text = f"{x.get('description', '')} {x.get('niche_tags', '')} {x.get('sector', '')} {x.get('name', '')}".lower()
            if has_word(text, anchor):
                out.append((sum(has_word(text, w) for w in head), "energy_companies",
                            {k: x.get(k, "") for k in ("name", "description", "niche_tags", "stage", "raised", "location", "founders", "website", "source_url")}))
    deals = read_table("energy_deals")
    if deals is not None:
        for x in deals.to_dict("records"):
            text = f"{x.get('technology', '')} {x.get('asset', '')} {x.get('parties', '')} {x.get('deal_type', '')}".lower()
            if has_word(text, anchor):
                out.append((sum(has_word(text, w) for w in head), "energy_deals",
                            {k: x.get(k, "") for k in ("event_id", "event_date", "deal_type", "parties", "asset", "technology", "state", "country", "dollars", "status", "source", "source_url")}))
    out.sort(key=lambda t: -t[0])
    rows = []
    for _, table, row in out[:cap]:
        eid = f"E{len(r.erw) + 1}"
        r.erw.append({"id": eid, "tool": "query", "args": {"table": table}, "result": row, "error": False})
        rows.append((eid, table, row))
    log(f"  warehouse candidates: {len(rows)} rows carrying {anchor!r} (energy_companies and energy_deals), of {len(out)} matching")
    return rows


# ---------------------------------------------------------------------------------------------
# the selection rule (code)
# ---------------------------------------------------------------------------------------------

STAGES = [("found", "Found"), ("private", "A private company"), ("fits", "Fits the stage and geography asked for"),
          ("trend", "Tied to a trend: on the landscape"), ("pipeline", "On the pipeline map")]
US = {"us", "usa", "u.s.", "u.s.a.", "united states", "united states of america", "america"}
US_STATES = ["alabama", "alaska", "arizona", "arkansas", "california", "colorado", "connecticut", "delaware", "florida", "georgia", "hawaii",
             "idaho", "illinois", "indiana", "iowa", "kansas", "kentucky", "louisiana", "maine", "maryland", "massachusetts", "michigan",
             "minnesota", "mississippi", "missouri", "montana", "nebraska", "nevada", "new hampshire", "new jersey", "new mexico", "new york",
             "north carolina", "north dakota", "ohio", "oklahoma", "oregon", "pennsylvania", "rhode island", "south carolina", "south dakota",
             "tennessee", "texas", "utah", "vermont", "virginia", "washington", "west virginia", "wisconsin", "wyoming", "district of columbia"]


def geo_fits(asked, country, location):
    """True, False or None (the sources do not say) for a company against the geography asked for."""
    a = (asked or "").strip().lower()
    if not a:
        return True
    c, loc = (country or "").strip().lower(), (location or "").strip().lower()
    blank = ("not disclosed", "not stated", "unknown", "n/a")
    c, loc = ("" if c in blank else c), ("" if loc in blank else loc)
    if not c and not loc:
        return None
    if a in US or a.startswith("us ") or a.startswith("united states"):
        if c:
            return c in US
        if re.search(r"\b(usa|u\.s\.a?\.?|united states)\b", loc) or any(re.search(rf"\b{re.escape(s)}\b", loc) for s in US_STATES):
            return True
        return None           # a city alone does not say which country
    return (a in c or c in a) if c else (True if a in loc else None)


def select(orgs, stage_asked, geo_asked, n_trends, known_ids):
    """Every organisation with the funnel stage it reached and why it stopped. Returns the rows in the order found."""
    rows, seen = [], {}
    for o in orgs:
        key = tb.name_key(o.get("name", ""))
        if not key:
            continue
        if key in seen:                                   # the same company twice: the row with more sources stays
            if len(o.get("sources") or []) <= len(seen[key].get("sources") or []):
                continue
            rows.remove(seen[key])
        o = dict(o)
        o["sources"] = [i for i in (o.get("sources") or []) if i in known_ids]
        o["trends"] = sorted({int(t) for t in (o.get("trends") or []) if isinstance(t, int) and 1 <= t <= n_trends})
        reached, stopped = "found", ""
        if o.get("kind") != "private company" or tb.is_public(o):
            stopped = f"not a private company ({o.get('kind') or 'kind not stated'})"
        else:
            reached = "private"
            g = geo_fits(geo_asked, o.get("country"), o.get("location"))
            if g is None:
                stopped = "no fetched source gives its location"
            elif not g:
                stopped = f"outside the geography asked for ({o.get('country') or o.get('location')})"
            elif stage_asked and o.get("fits_stage") == "no":
                stopped = "outside the stage asked for"
            else:
                reached = "fits"
                if not o["sources"]:
                    stopped = "no fetched source is cited for it"
                elif not o["trends"] or not (o.get("trend_reason") or "").strip():
                    stopped = "no fetched source ties it to one of the five trends"
                else:
                    reached = "trend"
        o["reached"], o["stopped"] = reached, stopped
        o["score"], o["clause"] = tb.confidence(o)
        seen[key] = o
        rows.append(o)
    on_map = sorted((o for o in rows if o["reached"] == "trend" and o["score"] >= PIPELINE_MIN), key=rank)
    for o in on_map[:PIPELINE_MAX]:
        o["reached"] = "pipeline"
    for o in rows:
        if o["reached"] == "trend" and not o["stopped"]:      # session 142: a reader is told why, never the threshold or the cap
            o["stopped"] = "its confidence is too low for the pipeline map" if o["score"] < PIPELINE_MIN else "the pipeline map is full"
    return rows


def rank(o):
    """Session 142, the tie-break (tie.py, rule 4): the total score of its ties, then its best evidence tier, then its
    normalized name. The same evidence gives the same order every time."""
    return (-(o.get("tie") or 0), o.get("tier_rank", len(tie.TIER_ORDER)), tb.name_key(o.get("name", "")))


# ---------------------------------------------------------------------------------------------
# session 142: who is tied to a trend is decided by tie.py from saved evidence, never by the model
# ---------------------------------------------------------------------------------------------

def store_path(evidence_dir, niche, stage, geography):
    """The local file of a niche's store (session 147: the same name is the object's name in the bucket, store.py)."""
    return os.path.join(evidence_dir, es.store_name(niche, stage, geography) + ".json")


def cited_addresses(orgs, store):
    """Session 147: the web addresses a run asks for, in order: those its own rows cite (a row's sources and the
    pages of its quoted sentences), a to z; then those the rows already in the niche's store cite, a to z. An address
    the store holds from the run's day is not asked for again (pages.fetch_run)."""
    web = lambda a: bool(a) and re.match(r"https?://", str(a), re.I) is not None
    own = sorted({a for o in orgs for a in list(o.get("source_urls") or []) + [q.get("address") for q in (o.get("evidence") or [])] if web(a)})
    kept = sorted({a for x in store.get("rows") or [] for a in x["row"].get("source_urls") or [] if web(a)} | {q["address"] for q in store.get("quotes") or [] if web(q["address"])})
    return own + [a for a in kept if a not in set(own)]


def warehouse_rows():
    """The warehouse tier of the evidence, read whole from the tables as they are now (no model)."""
    out = {}
    for name in ("energy_companies", "energy_deals"):
        t = read_table(name)
        out[name] = t.to_dict("records") if t is not None else []
    return out


def address_book(r):
    """{source id of this run: its address}. A web source's address is its URL; a warehouse row's is erw:<table>/<row>."""
    book = {s["id"]: s["url"] for s in r.sources.values()}
    for e in r.erw:
        row, table = e.get("result"), (e.get("args") or {}).get("table")
        if e.get("tool") != "query" or not isinstance(row, dict):
            continue
        if table == "energy_companies" and row.get("name"):
            book[e["id"]] = f"erw:energy_companies/{row['name']}"
        elif table == "energy_deals" and row.get("event_id"):
            book[e["id"]] = f"erw:energy_deals/{row['event_id']}"
    return book


def run_day(run_id):
    """The run's day (UTC): the day in its id (YYYYMMDDTHHMMSSZ-...), else today's."""
    m = re.match(r"(\d{4})(\d{2})(\d{2})T", run_id or "")
    return f"{m.group(1)}-{m.group(2)}-{m.group(3)}" if m else dt.datetime.now(dt.timezone.utc).date().isoformat()


def tied_rows(r, run_id, niche, stage, geography, trends, land, evidence_path, log, fetch=None, read="pages"):
    """The landscape's rows from the evidence store and the rule. Returns (rows for select(), context for tie_done()).

    This run's fetched sources and the rows the model structured are added to the niche's store; the rule (tie.judge)
    then reads the whole store and the warehouse's tables. The model's own opinion of which trends a company serves
    (its "trends" and "trend_reason") is kept in the state for comparison and decides nothing.

    Session 147. evidence_path: a path (the local file), a store handle (store.py: the bucket or the file), or None.
    fetch: None (no page is asked for: the rule reads the pages the store already holds), or the keyword arguments of
    pages.fetch_run (count, raw_dir, get, the ceilings): the run then asks, in code, for every web address its rows
    cite, and the page texts are saved in the store before the rule reads them. No model call is made here.
    read: "pages", always, for a run; "quotes" is session 142's reading, for a comparison on saved answers only."""
    today = dt.date.today().isoformat()
    book = address_book(r)
    handle = es.handle_of(evidence_path)
    store = handle.load(niche, stage, geography) if handle is not None else tie.empty_store(niche, stage, geography)
    before = store.get("last")
    restored = pg.restore_kept(store)                    # session 160: a store written before it holds a refused page's good text in its history
    if restored:
        log(f"  pages: {len(restored)} pages whose last good text was in their history are kept pages again: " + "; ".join(restored))
    orgs = []
    for o in land["organisations"]:
        o = dict(o)
        o["source_urls"] = [book[i] for i in (o.get("sources") or []) if i in book]
        # a sentence the model attributes to a warehouse row is not evidence: the rule reads the warehouse itself
        o["evidence"] = [{"quote": q.get("quote", ""), "address": book.get((q.get("source") or "").strip(), "")} for q in (o.get("evidence") or [])
                         if not book.get((q.get("source") or "").strip(), "erw:").startswith("erw:")]
        orgs.append(o)
    changed = tie.add_run(store, run_id, today, [dict(s) for s in r.sources.values()], orgs)
    pull = None
    if fetch is not None:                                # session 147: the pages, asked for in code; a failure here never costs the run its paid answers
        try:
            pull = pg.fetch_run(store, cited_addresses(orgs, store), run_id, run_day(run_id), log, **fetch)
        except Exception as exc:
            pull = {"error": f"{type(exc).__name__}: {str(exc)[:300]}"}
            log(f"  pages: THE PULL FAILED ({pull['error']}); the rule reads the pages already saved")
    wh = warehouse_rows()
    judged = tie.judge(store, wh, niche, trends, read=read, vendors=pg.labeled_vendors())      # session 158: a data vendor's page is labeled
    ids = {addr: i for i, addr in sorted(book.items(), key=lambda kv: (kv[0][0], int(kv[0][1:]) if kv[0][1:].isdigit() else 0), reverse=True)}
    by_name = {x.get("name", ""): x for x in wh["energy_companies"]}
    by_event = {x.get("event_id", ""): x for x in wh["energy_deals"]}

    def id_of(addr):
        if addr in ids:
            return ids[addr]
        if addr.startswith("erw:"):
            table, _, rest = addr[4:].partition("/")
            row = by_name.get(rest) if table == "energy_companies" else by_event.get(rest)
            if row is None:
                return None
            keep = (("name", "description", "niche_tags", "stage", "raised", "location", "founders", "website", "source_url") if table == "energy_companies"
                    else ("event_id", "event_date", "deal_type", "parties", "asset", "technology", "state", "country", "dollars", "status", "source", "source_url"))
            ids[addr] = f"E{len(r.erw) + 1}"
            r.erw.append({"id": ids[addr], "tool": "query", "args": {"table": table}, "result": {k: row.get(k, "") for k in keep}, "error": False})
            return ids[addr]
        s = store["sources"].get(addr)
        if s is None:
            return None
        ids[addr] = r.source(addr, s.get("title", ""), s.get("page_age", ""))
        r.sources[addr]["retrieved"] = s.get("fetched") or r.sources[addr]["retrieved"]      # the day it was fetched, not today
        for c in s.get("cited") or []:
            if c not in r.sources[addr]["cited"]:
                r.sources[addr]["cited"].append(c)
        return ids[addr]

    model = {}
    for o in land["organisations"]:                      # the model's own opinion, for the state only
        model.setdefault(tie.name_key(o.get("name", "")), sorted({t for t in (o.get("trends") or []) if isinstance(t, int)}))
    rows = []
    for c in judged:
        o = dict(c["row"], name=c["name"])
        tying = [x["address"] for n in c["trends"] for x in c["ties"][n]["lines"]]
        addresses = list(dict.fromkeys(tying + c["row"]["source_urls"]))
        o["sources"] = [i for i in (id_of(a) for a in addresses) if i]
        o["independent_sources"] = len({tie.domain(a) for a in addresses if not a.startswith("erw:") and tie.domain(a)}) + (1 if any(a.startswith("erw:") for a in addresses) else 0)
        o["trends"], o["tie"] = list(c["trends"]), c["tie"]
        o["tier_rank"] = tie.TIER_ORDER.index(c["tier"]) if c["tier"] else len(tie.TIER_ORDER)
        best = c["reason"]
        o["trend_reason"] = "" if not best else (f"\"{best['text'].strip().rstrip('.')}\" " + ("(ERW companies and deals tables)" if best["address"].startswith("erw:") else f"({tie.domain(best['address']) or 'web'})"))
        o["model_trends"] = sorted({t for k in c["aliases"] for t in model.get(k, [])})
        if best and best.get("vendor"):                  # session 158: the sentence a reader is shown comes from a data vendor's public page
            o["reason_vendor"] = best["vendor"]
        if best and best.get("kept"):                    # session 160: the sentence a reader is shown is from a page's last good text
            o["reason_kept"] = best["kept"]
        # session 160: the company's other names, as written. A name that differs from the one shown only by its legal
        # form or its punctuation ("Thermofilic" beside "Thermofilic, LLC") is the same name and is not repeated
        also = [n for n in c.get("also") or [] if tie.name_key(n) != c["key"]]
        if also:
            o["also_written"] = also
        rows.append(o)
    held = sum(1 for p in (store.get("pages") or {}).values() if tie.page_holds(p))
    log(f"  the rule: {len(judged)} companies in the store of this niche ({len(store['rows'])} rows of {len(store['runs'])} runs, {len(store['sources'])} fetched sources, "
        f"{len(store.get('pages') or {})} pages asked for, {held} holding text, {len(store['quotes'])} reported sentences that decide nothing); "
        f"tied to a trend {sum(1 for c in judged if c['trends'])}; fetched sources whose text changed {len(changed)}; "
        f"warehouse rows read: energy_companies {len(wh['energy_companies'])}, energy_deals {len(wh['energy_deals'])}")
    return rows, {"store": store, "handle": handle, "before": before, "judged": judged, "changed": changed, "run_id": run_id, "pull": pull, "restored": restored,
                  "warehouse": {k: len(v) for k, v in wh.items()}}


def tie_done(ctx, orgs, log):
    """After select(): what this run rested on, what changed since the run before, and the store saved."""
    placed = {tie.name_key(o["name"]): (o["reached"], o["score"]) for o in orgs}
    snap = tie.snapshot(ctx["run_id"], ctx["judged"], placed)
    d = tie.diff(ctx["before"], snap)
    ctx["store"]["last"] = snap
    handle, where, kind = ctx.get("handle"), "", ""
    if handle is not None:
        try:
            where = handle.save(ctx["store"])            # the bucket, or the local file; a refused bucket write falls back to the file and says so
            kind = handle.kind
            log(f"  evidence store saved ({kind}): {where}")
        except Exception as exc:                         # the run's report and state are still written: nothing paid for is lost
            where, kind = f"NOT SAVED ({type(exc).__name__}: {str(exc)[:200]})", "none"
            log(f"  EVIDENCE STORE {where}")
    checks = tie.quote_check(ctx["store"])
    quotes = {"reported": len(checks), "page_held": sum(1 for q in checks if q["page"] == "held"), "found_on_the_saved_page": sum(1 for q in checks if q["found"]),
              "not_found_on_the_saved_page": sum(1 for q in checks if q["page"] == "held" and not q["found"]),
              "page_not_held": sum(1 for q in checks if q["page"] != "held")}
    pages = ctx["store"].get("pages") or {}
    page_states = {}
    for p in pages.values():
        k = "fetched" if tie.page_holds(p) else (p.get("reason") or p.get("state") or "not held")
        page_states[k] = page_states.get(k, 0) + 1
    if ctx["before"]:
        log(f"  against run {d['from_run']}: {len(d['new_companies'])} new companies, {len(d['moved'])} moved, {d['evidence_changes']} evidence lines added or removed; "
            f"moved without an explanation: {sum(1 for m in d['moved'] if not m['explained'])}")
    trace = [{"name": c["name"], "key": c["key"], "aliases": c["aliases"], "trends": c["trends"], "tie": c["tie"], "tier": c["tier"],
              "reached": placed.get(c["key"], ("", None))[0], "confidence": placed.get(c["key"], ("", None))[1], "facts": {f: c["row"].get(f) for f in tie.FACTS},
              "ties": {str(n): t for n, t in c["ties"].items() if t["lines"]}, "evidence": c["evidence"],
              "name_rule": c.get("name_rule"), "near_duplicates": c.get("near_duplicates") or [],
              "also": c.get("also") or [], "merged_by_domain": c.get("merged_by_domain")} for c in ctx["judged"]]
    disagreements = [dict(x, name=c["name"]) for c in ctx["judged"] for x in c["row"].get("disagreements") or []]
    # session 158, for the run's record: the names matched as proper nouns only, the remarks counted once, the vendor pages
    proper = [dict(c["name_rule"], name=c["name"], reached=placed.get(c["key"], ("", None))[0]) for c in ctx["judged"] if c.get("name_rule")]
    merged = [dict(m, name=c["name"]) for c in ctx["judged"] for m in c.get("near_duplicates") or []]
    vendor_lines = [{"name": c["name"], "trend": n, "address": x["address"], "vendor": x["vendor"], "points": x["points"], "tied": t["tied"]}
                    for c in ctx["judged"] for n, t in c["ties"].items() for x in t["lines"] if x.get("vendor")]
    names = pg.labeled_vendors()
    vendors = {"pages": {u: {"vendor": tie.vendor_of(u, names), "holds_text": tie.page_holds(p), "state": p.get("reason") or p.get("state")}
                         for u, p in sorted(pages.items()) if tie.vendor_of(u, names)},
               "sentences_labeled": sum(1 for c in ctx["judged"] for e in c["evidence"] if e.get("vendor")), "lines": vendor_lines,
               "reasons_shown": [c["name"] for c in ctx["judged"] if (c.get("reason") or {}).get("vendor") and placed.get(c["key"], ("", None))[0] in ("trend", "pipeline")]}
    # session 160, for the run's record: the kept pages and their age, the titles not counted, the names merged by domain
    kept_pages = {u: dict(tie.page_kept(p), retrieved_at=p.get("retrieved_at"), refused_at=(p.get("refusal") or {}).get("at"), refusals=len(p.get("refusals") or []))
                  for u, p in sorted(pages.items()) if p.get("state") == tie.KEPT}
    kept_lines = [{"name": c["name"], "trend": n, "address": x["address"], "points": x["points"], "tied": t["tied"], "retrieved": x["kept"]["retrieved"], "age_days": x["kept"]["age_days"]}
                  for c in ctx["judged"] for n, t in c["ties"].items() for x in t["lines"] if x.get("kept")]
    kept = {"pages": kept_pages, "restored_from_history": list(ctx.get("restored") or []), "age_limit": None,
            "sentences": sum(1 for c in ctx["judged"] for e in c["evidence"] if e.get("kept")), "lines": kept_lines,
            "reasons_shown": [c["name"] for c in ctx["judged"] if (c.get("reason") or {}).get("kept") and placed.get(c["key"], ("", None))[0] in ("trend", "pipeline")]}
    titles = [dict(x, name=c["name"]) for c in ctx["judged"] for x in c.get("titles_not_counted") or []]
    by_domain = [dict(c["merged_by_domain"], name=c["name"], reached=placed.get(c["key"], ("", None))[0], kind=c["row"].get("kind"), read_by=c["row"].get("read_by") or {})
                 for c in ctx["judged"] if c.get("merged_by_domain")]
    log(f"  session 160: pages kept with their last good text {len(kept_pages)}"
        + ("" if not kept_pages else " (" + "; ".join(f"{u}: retrieved {k['retrieved']}, refused {k['refused']} ({k['reason']}), {k['age_days']} days" for u, k in kept_pages.items()) + ")")
        + f", {kept['sentences']} sentences read from them, {len(kept_lines)} scoring lines, {len(kept['reasons_shown'])} shown as a reason; "
        f"search results' titles that name a company and are not counted: {len(titles)}; companies merged by domain: {len(by_domain)}"
        + ("" if not by_domain else " (" + "; ".join(f"{x['name']} = {', '.join(x['names'][1:])} [{', '.join(x['domains'])}]" for x in by_domain) + ")"))
    log(f"  the name rule (session 158): {len(proper)} companies whose name is made of the niche's own words"
        + ("" if not proper else ": " + "; ".join(f"{x['name']} (counted {x['counted']}, not counted {x['not_counted']})" for x in proper))
        + f"; remarks printed twice and counted once: {len(merged)} pairs; sentences from data vendors' pages: {vendors['sentences_labeled']} labeled, "
        f"{len(vendor_lines)} scoring lines, {len(vendors['reasons_shown'])} shown as a reason")
    return {"store": where, "store_kind": kind, "diff": d, "changed_sources": ctx["changed"], "disagreements": disagreements, "trace": trace,
            "pull": ctx.get("pull"), "pages": page_states, "quotes": quotes, "quote_checks": checks, "warehouse": ctx.get("warehouse"),
            "name_rule": {"companies": proper, "sentences_not_counted": sum(x["not_counted"] for x in proper)},
            "near_duplicates": {"pairs": len(merged), "list": merged, "same_share": tie.NEAR_SAME, "least_words": tie.NEAR_MIN_WORDS},
            "vendor_pages": vendors,
            "kept_pages": kept, "titles_not_counted": {"count": len(titles), "list": titles}, "merged_by_domain": by_domain}


def confidence_note(o):
    n = max(0, min(3, int(o.get("independent_sources") or len(o.get("sources") or []))))
    year = str(o.get("latest_source_year") or "").strip()[:4]
    parts = [f"{n} independent source{'s' if n != 1 else ''}" + (f", the latest from {year}" if year.isdigit() else ", undated")]
    sp, rp = bool(o.get("stage_primary")), bool(o.get("raised_primary"))
    if sp and rp:
        parts.append("its stage and funding are confirmed by the company or an investor")
    elif sp or rp:
        parts.append(f"its {'stage' if sp else 'funding'} is confirmed by the company or an investor")
    else:
        parts.append("nothing is confirmed by the company or an investor")
    return "; ".join(parts) + "."


# ---------------------------------------------------------------------------------------------
# the report
# ---------------------------------------------------------------------------------------------

def cell(text, r, ids, log, where):
    """A cell as the page draws it: the checked text, or a placeholder with the reason on hover."""
    t = (text or "").strip()
    if not t or t.lower() in ("not disclosed", "n/a", "unknown", "none", "not stated", "undisclosed"):
        return {"missing": "not_disclosed", "note": NOTE["not_disclosed"]}
    t = tb.check_numbers(r, t, ids, log, where)
    if t == "not confirmed":
        return {"missing": "not_confirmed", "note": NOTE["not_confirmed"]}
    return clean(t)


def clean(t):
    return re.sub(r"\s+", " ", (t or "").replace(tb.EM, ", ")).strip()


def text(t, r, ids, log, where):
    ids = [i for i in (ids or [])]
    return {"text": clean(tb.check_numbers(r, t or "", ids, log, where)), "sources": ids}


def sourcing_of(o, plan):
    """Where a company was found, in words a reader may see: never the queries themselves."""
    out = []
    why = {q[0]: q[2] for q in plan}
    for f in o.get("found_by") or []:
        f = f.strip()
        if f.upper().startswith("E") or "erw" in f.lower() or "warehouse" in f.lower():
            label = "ERW companies and deals tables"
        elif f.upper() in why:
            label = "Web search: " + why[f.upper()]
        else:
            label = "Web search"
        if label not in out:
            out.append(label)
    if any(i.startswith("E") for i in o.get("sources") or []) and "ERW companies and deals tables" not in out:
        out.append("ERW companies and deals tables")
    return out or ["Web search"]


def build_report(niche, stage, geography, r, a, land, rest, pol, plan, log):
    known = {s["id"] for s in r.sources.values()} | {e["id"] for e in r.erw}
    keep = lambda ids: [i for i in (ids or []) if i in known]
    used = set()

    def T(t, ids, where):
        ids = keep(ids); used.update(ids)
        return text(t, r, ids, log, where)

    def C(t, ids, where):
        ids = keep(ids); used.update(ids)
        return cell(t, r, ids, log, where)

    sc = a["scope"]
    scope = {"definition": T(sc["definition"], sc["definition_sources"], "scope definition"),
             "value_chain": [{"stage": clean(v["stage"]), "what": T(v["what_happens"], v["sources"], "value chain")} for v in sc["value_chain"] if keep(v["sources"])],
             "excluded": [{"niche": clean(x["niche"]), "why": clean(x["why_excluded"])} for x in sc["excluded"]],
             "definitions": [{"term": clean(d["term"]), "meaning": T(d["meaning"], d["sources"], "definition")} for d in sc.get("definitions", []) if keep(d["sources"])]}
    trends = []
    for n, t in enumerate(a["trends"][:5], 1):
        ids = keep(t["sources"])
        if not ids:
            log(f"    trend {n} {t['title']!r}: no source, not written")
            continue
        used.update(ids)
        rows = [[cell(c, r, ids, log, f"trend {n} table") for c in row] for row in t["table"]["rows"]]
        ch = t["chart"]
        trends.append({"n": n, "title": clean(t["title"]), "fact": text(t["fact"], r, ids, log, f"trend {n} fact"),
                       "table": {"columns": [clean(c) for c in t["table"]["columns"]], "rows": rows},
                       "chart": {"kind": ch["kind"], "title": clean(ch["title"]), "category": ch["category_column"], "values": ch["value_columns"], "unit": clean(t.get("unit", ""))},
                       "sources": ids})
    orgs = select(land["organisations"], stage, geography, len(a["trends"][:5]), known)
    place = {clean(o["name"]): n for n, o in enumerate(sorted(orgs, key=rank))}      # session 142: the rule's order (tie.py, rule 4)
    kept_n = {t["n"] for t in trends}
    companies, funnel, pipeline = [], [], []
    for o in orgs:
        ids = o["sources"]; used.update(ids)
        srcg = sourcing_of(o, plan)
        funnel.append({"name": clean(o["name"]), "reached": dict(STAGES)[o["reached"]], "stopped": o["stopped"],
                       "score": o["score"] if o["reached"] != "found" else None, "sourcing": srcg, "sources": ids})
        if o["reached"] not in ("trend", "pipeline"):
            continue
        row = {"name": clean(o["name"]), "website": (o.get("website") or "").strip(), "description": clean(tb.check_numbers(r, o.get("description", ""), ids, log, f"landscape {o['name']}")),
               "founders": C(o.get("founders"), ids, f"founders {o['name']}"), "stage": C(o.get("stage"), ids, f"stage {o['name']}"),
               "raised": C(o.get("raised"), ids, f"raised {o['name']}"), "location": C(o.get("location"), ids, f"location {o['name']}"),
               "signal": clean(tb.check_numbers(r, o.get("signal", ""), ids, log, f"signal {o['name']}")),
               "trends": [t for t in o["trends"] if t in kept_n], "reason": clean(tb.check_numbers(r, o.get("trend_reason", ""), ids, log, f"reason {o['name']}")),
               "sources": ids, "confidence": o["score"], "confidence_note": confidence_note(o), "sourcing": srcg}
        if o.get("reason_vendor"):                       # session 158: a short mark with a hover, drawn beside the sentence
            row["reason_vendor"] = {"mark": VENDOR_MARK, "note": VENDOR_NOTE.format(vendor=clean(o["reason_vendor"]))}
        if o.get("reason_kept"):                         # session 160: the day the kept text was retrieved, a short mark with a hover
            k = o["reason_kept"]
            row["reason_kept"] = {"mark": KEPT_MARK.format(day=day_words(k.get("retrieved"))), "retrieved": str(k.get("retrieved") or ""),
                                  "note": KEPT_NOTE.format(day=day_words(k.get("retrieved")), again=day_words(k.get("refused")))}
        if o.get("also_written"):                        # session 160: one company under several names is one row
            row["also"] = [clean(n) for n in o["also_written"]]
        companies.append(row)
        if o["reached"] == "pipeline":
            tam = C(o.get("tam"), ids, f"tam {o['name']}")
            if isinstance(tam, dict):
                tam = {"missing": "not_held", "note": NOTE["tam"]}
            pipeline.append({"name": row["name"], "founders": row["founders"], "signal": row["signal"],
                             "access": {"missing": "pitchbook_pending", "note": NOTE["access"]}, "tam": tam,
                             "trends": row["trends"], "confidence": o["score"], "sources": ids})
    companies.sort(key=lambda c: place.get(c["name"], len(place)))
    pipeline.sort(key=lambda c: place.get(c["name"], len(place)))
    order = [s for s, _ in STAGES]
    counts = [{"id": sid, "label": label, "n": sum(1 for o in orgs if order.index(o["reached"]) >= i)} for i, (sid, label) in enumerate(STAGES)]

    cap = rest.get("capital", {"fact": "", "fact_sources": [], "rounds": []})
    rounds = []
    for x in cap["rounds"]:
        ids = keep(x["sources"])
        if not ids:
            continue
        used.update(ids)
        x = dict(x, sources=ids)
        date, investors = tb.capital_checked(r, x, log)
        rounds.append({"date": cell(date, r, ids, log, "capital date"), "company": clean(x["company"]), "kind": clean(x["kind"]),
                       "amount": cell(f"{x['amount']} {x['currency']}".strip() if x["amount"] else "", r, ids, log, f"capital {x['company']}"),
                       "investors": cell(investors, r, ids, log, "capital investors"), "sources": ids})
    inc = rest.get("incumbents", {"fact": "", "fact_sources": [], "players": []})
    players = [{"name": clean(p["name"]), "kind": clean(p["kind"]), "ticker": clean(p["ticker"]), "metric": clean(p["metric"]),
                "value": C(p["value"], p["sources"], f"incumbent {p['name']}"), "as_of": clean(p["as_of"]), "sources": keep(p["sources"])}
               for p in inc["players"] if keep(p["sources"])]
    risks = [{"risk": clean(x["risk"]), "how": clean(tb.check_numbers(r, x["how_it_breaks_the_thesis"], keep(x["sources"]), log, "risk")),
              "not_known": clean(x["not_known"]), "sources": keep(x["sources"])} for x in rest.get("risks", {}).get("risks", []) if keep(x["sources"])]
    for x in risks + players:
        used.update(x["sources"])
    policy = {"fact": clean(rest.get("policy", {}).get("fact", "")), "actions": []}
    if pol is not None and len(pol):
        by = {x["event_id"]: x for x in pol.to_dict("records")}
        reads = read_table("policy_reads")
        read_by = {x["event_id"]: x for x in reads.to_dict("records")} if reads is not None and "event_id" in reads.columns else {}
        for x in rest.get("policy", {}).get("actions", []):
            p = by.get(x["event_id"])
            if p:
                rd = read_by.get(x["event_id"], {})
                policy["actions"].append({"date": p.get("event_date", "")[:10], "agency": p.get("agency", ""), "title": clean(p.get("title", "")),
                                          "why": clean(x["why_it_matters"]), "url": p.get("source_url", ""), "read": clean(rd.get("read", "") or rd.get("plain_read", ""))})
    report = {"version": 1, "niche": niche, "stage": stage, "geography": geography, "built": ip.utc_iso(dt.datetime.now(dt.timezone.utc)),
              "sources": [], "scope": scope, "trends": trends,
              "landscape": {"fact": T(land.get("fact", ""), land.get("fact_sources"), "landscape fact"), "rule": RULE, "companies": companies},
              "funnel": {"stages": counts, "companies": funnel}, "pipeline": {"companies": pipeline},
              "capital": {"fact": T(cap["fact"], cap["fact_sources"], "capital fact"), "rounds": rounds},
              "incumbents": {"fact": T(inc["fact"], inc["fact_sources"], "incumbents fact"), "players": players},
              "risks": risks, "policy": policy}
    # the sources the report cites, and only those, once every part has named its own
    by_id = {s["id"]: s for s in r.sources.values()}
    erw = {e["id"]: e for e in r.erw}
    for i in sorted(used, key=lambda s: (s[0], int(s[1:]) if s[1:].isdigit() else 0)):
        if i in by_id:
            s = by_id[i]
            report["sources"].append({"id": i, "kind": "web", "title": clean(s["title"])[:200], "url": s["url"], "retrieved": s.get("retrieved", "")})
        elif i in erw:
            report["sources"].append({"id": i, "kind": "erw", "title": f"ERW table {erw[i]['args'].get('table') or 'query'}", "url": "", "retrieved": dt.date.today().isoformat()})
    return report, orgs


# ---------------------------------------------------------------------------------------------
# the PitchBook stage: the request, and the text a person pastes into a Claude chat
# ---------------------------------------------------------------------------------------------

LOOKUPS = ["company profile: legal name, headquarters, year founded, one-line description, employees",
           "financing status and the last financing: date, type, size, post-money valuation where PitchBook shows one",
           "total raised to date", "investors, with the lead investors named", "founders and the chief executive"]


def pitchbook_request(run_id, niche, geography, orgs, trends, key):
    asked = [o for o in orgs if o["reached"] != "found"][:60]
    companies = [{"name": tb_clean_name(o["name"]), "website": (o.get("website") or "").strip(), "lookups": LOOKUPS} for o in asked]
    kw = [head_of(niche)] + [p for t in trends for p in (t.get("search_phrases") or [])[:1]]
    discover = {"keywords": list(dict.fromkeys(k.strip() for k in kw if k.strip()))[:8], "hq": geography or "any"}
    names = "\n".join(f"{i}. {c['name']}" + (f" ({c['website']})" if c["website"] else "") for i, c in enumerate(companies, 1))
    if not companies:          # session 169: the ERW does not search for companies; the list is PitchBook's own (part B)
        names = "(This run names no company: the ERW does not search for companies. Return \"companies\": [] and put every company in \"additional_companies\".)"
    paste = f"""You have a PitchBook connector. Please pull the following from PitchBook for an ERW Thesis Builder run and answer with ONE JSON code block in the exact format below, and nothing else after it.

Run: {run_id}
Key: {key}
Niche: {niche}

A. For each company in this list, look it up in PitchBook by name (use the website to pick the right one) and return:
   - {LOOKUPS[0]}
   - {LOOKUPS[1]}
   - {LOOKUPS[2]}
   - {LOOKUPS[3]}
   - {LOOKUPS[4]}

{names}

B. Then search PitchBook for companies this list is missing: keywords {", ".join(repr(k) for k in discover["keywords"])}; headquarters: {discover["hq"]}; private, venture-backed or grant-backed, founded 2012 or later. Return up to {25 if companies else 60} that are not in the list above, as "additional_companies", each with "why": the keyword or PitchBook industry that matched.

Rules: report only what PitchBook shows. If PitchBook has no record of a company, return it with "found": false and nothing else. Leave out any field PitchBook does not show; do not estimate, and do not fill a field from memory or from the web. Money is in millions of US dollars as numbers (12.5, not "$12.5M"). Dates are YYYY-MM-DD, or YYYY-MM, or YYYY.

Format:
```json
{{
  "format": "{FORMAT}",
  "run_id": "{run_id}",
  "key": "{key}",
  "pulled_on": "YYYY-MM-DD",
  "companies": [
    {{
      "name": "the name exactly as in the list above",
      "found": true,
      "pitchbook_name": "the name PitchBook uses",
      "hq": "City, State, Country",
      "founded_year": 2019,
      "description": "one line",
      "employees": 25,
      "financing_status": "Venture Capital-Backed",
      "last_round": {{ "date": "2025-03-01", "type": "Series A", "size_usd_m": 12.5, "post_valuation_usd_m": 60.0 }},
      "total_raised_usd_m": 20.1,
      "investors": ["Investor One", "Investor Two"],
      "lead_investors": ["Investor One"],
      "founders": ["First Founder", "Second Founder"]
    }},
    {{ "name": "a company PitchBook does not hold", "found": false }}
  ],
  "additional_companies": [
    {{ "name": "A company not in the list", "found": true, "why": "keyword: ...", "hq": "City, State, Country", "total_raised_usd_m": 3.0 }}
  ]
}}
```"""
    return {"format": FORMAT, "run_id": run_id, "companies": companies, "discover": discover, "paste_text": paste}


def tb_clean_name(name):
    return clean(re.sub(r"\s*\(.*?\)\s*", " ", name or ""))[:120]


# ---------------------------------------------------------------------------------------------
# one run
# ---------------------------------------------------------------------------------------------

# What each stage has cost at most in the runs of 6 October 2026, rounded up: the spend a stage must find under the
# run's ceiling BEFORE it starts. Session 135's last run was stopped by the old rule, which looked only after a call was
# paid: it paid for every stage, then threw the finished landscape away and passed the session's ceiling by USD 0.12.
# Session 142: the structure call of the landscape also copies each organisation's quoted sentences, so its reserve is
# raised from 0.26; and the research of the landscape now copies whole source sentences into its notes, so its reserve
# is raised from 0.66: the first run of 7 October 2026 paid USD 0.7262 for it (and 0.2199 for the structure call).
STAGE_USD = {"research a": 0.45, "structure a": 0.16, "landscape": 0.85, "risks": 0.12, "structure landscape": 0.34, "structure rest": 0.16}


class Careful(tb.Researcher):
    """A Researcher that asks before a stage whether the stage fits under the ceiling, and never discards a paid answer."""

    def charge(self, resp, what, model=None):
        try:
            super().charge(resp, what, model) if model else super().charge(resp, what)
        except tb.Budget:
            self.log(f"  the ceiling of USD {self.max_usd:.2f} is passed at USD {self.cost:.4f}: the answer is kept, and no further stage starts")

    def guard(self, stage):
        need = STAGE_USD[stage] if stage in STAGE_USD else MARKET_USD[stage]      # session 169: the market run's stages
        if self.cost + need > self.max_usd:
            raise tb.Budget(f"{stage} needs up to USD {need:.2f} and USD {self.max_usd - self.cost:.4f} is left under the ceiling of USD {self.max_usd:.2f}; not started")


TREND_RULE = ("Each of the five trends must be about how the niche's own work is changing: a technology, a method, a data "
              "source, a kind of buyer, a business model or a source of money that is rising or falling, such that one can "
              "say of a company that it serves the trend or does not. A general fact about the wider industry (its total "
              "capacity, its geography, its age) is background for the scope, never a trend.")


def execute(r, run_id, niche, stage, geography, log, searches=8, landscape_from=None, retrend=False, landscape_only=False, evidence_path=None, fetch=None):
    """The whole run, on a Researcher the caller made (so its spend is known even when the run fails).
    Returns (report, pitchbook_request, key, state)."""
    log(f"run {run_id}: niche {niche!r}; stage {stage or 'any'}; geography {geography or 'any'}; model {r.model}; stop at USD {r.max_usd:.2f}")
    sysm = tb.base_system(niche, stage, geography)
    structure_a = (
        f"Niche: {niche}. Write the scope (the definition, the value chain, the adjacent niches kept out, and the "
        "terms a newcomer needs with their meanings), exactly five trends, and the market size if a source gives one. "
        + TREND_RULE + " Each trend: a short title; a Fact paragraph of two to four sentences; a table whose rows are years or "
        "categories and whose value columns hold numbers exactly as the sources give them; the chart that fits it "
        "(bar for categories, line for years) with its unit; and two search_phrases of two to five words that name "
        "the technology or business the trend favours, the words a company in it would use about itself.")
    if landscape_from:
        st = json.load(open(landscape_from, encoding="utf-8"))
        r.sources, r.erw, notes_a, a = st["sources"], st["erw"], st["notes_a"], st["a"]
        if retrend:
            r.guard("structure a")
            a = r.structure("structure (scope, trends)", structure_a, notes_a + "\n\n" + st.get("notes_b", ""), SCHEMA_A)
            a["trends"] = a["trends"][:5]
            log(f"  the research is taken from {os.path.basename(landscape_from)}; the scope and trends are written again from it")
        else:
            log(f"  scope and trends taken from {os.path.basename(landscape_from)} (no new call for them)")
    else:
        r.guard("research a")
        notes_a = r.research("research: scope, definitions, trends", sysm, (
            "Research (1) what this niche is exactly, the terms a newcomer needs defined, its value chain from input to "
            "customer, and the adjacent niches an investor should keep out of scope. (2) Its market size, with the "
            "warehouse first for any energy number it holds. (3) The five trends that most shape where a new company can "
            "win in this niche over the next five years, each with the numbers behind it over time (a small table of "
            "years or categories against values). " + TREND_RULE + " Write notes: one fact per sentence, cited."), searches)
        r.guard("structure a")
        a = r.structure("structure (scope, trends)", structure_a, notes_a, SCHEMA_A)
        a["trends"] = a["trends"][:5]
    plan = query_plan(niche, geography, a["trends"])
    cands = warehouse_candidates(niche, r, log)
    for qid, q, why in plan:
        log(f"  plan {qid} ({why}): {q}")
    trend_lines = "\n".join(f"{i}. {t['title']}" for i, t in enumerate(a["trends"], 1))
    cand_lines = "\n".join(f"[ERW source {eid}] {table}: {json.dumps(row, default=str)[:500]}" for eid, table, row in cands) or "(none)"
    capital_too = not landscape_from and not landscape_only
    lookups = 6 if geography else 0          # a location matters to the rule only when a geography was asked for
    r.guard("landscape")
    notes_b = r.research("research: landscape" + (", capital, incumbents" if capital_too else ""), sysm, (
        "Find every company working in this niche. Run each of these web searches once, in this order. For every "
        "organisation a result names as working in the niche write ONE compact note line of at most 60 words: its name; "
        "website; what it does; whether it is a private company (or public, a subsidiary, acquired, a university or "
        "laboratory, a nonprofit); the country and city of its headquarters; founders; stage; amount raised; the signal "
        "that surfaced it (a round, a grant, a pilot, a customer, a patent); and the id of the search that found it (Q1, "
        "Q2, ...). Then, for that organisation, go through the five trends below one by one and name each trend it serves "
        "with the source's own sentence that shows it, whole and word for word in quotation marks, and the page it is on. "
        "Do not skip a company because little is disclosed about it. Then "
        "judge each warehouse candidate below the same way (cite it by its ERW source id). "
        + ("Then, for up to six private companies whose headquarters country no result gave, run one search each to find it. " if lookups else "")
        + ("Then, with up to three more searches, the capital in the niche (rounds, grants, project finance, M&A with dates, "
           "amounts and investors) and the incumbents and public comparables with the one metric that matters for each. " if capital_too else "")
        + "Prefer primary sources. Cite every line.\n\nThe five trends:\n" + trend_lines +
        "\n\nThe searches:\n" + "\n".join(f"{qid}: {q}" for qid, q, _ in plan) + "\n\nWarehouse candidates:\n" + cand_lines),
        len(plan) + lookups + (3 if capital_too else 0), erw_tools=False)
    r.partial = {"run_id": run_id, "niche": niche, "notes_b": notes_b, "sources": r.sources, "erw": r.erw}      # session 142: a paid answer is kept even when a later stage is refused
    if not (landscape_from or landscape_only):
        r.guard("risks")
    notes_c = "" if (landscape_from or landscape_only) else r.research("research: risks", sysm, (
        "Research what could break an investment thesis in this niche: technical, market, regulatory and financing "
        "risks, and what is not known yet. Cite each. Write notes: one fact per sentence, cited."), 3, erw_tools=False)
    r.guard("structure landscape")
    land = r.structure("structure (landscape)", (
        f"Niche: {niche}. Stage asked for: {stage or 'any'}. Geography asked for: {geography or 'any'}. Write one row for EVERY "
        "organisation the notes name as working in or next to the niche, including those that will turn out public, "
        "foreign, acquired or out of scope: none is left out here. Keep each description to one line of at most 25 "
        "words. kind: what the sources say it is. country: the country of its headquarters as the sources give it, or "
        "\"not stated\". fits_stage: whether it fits the stage asked for, from the sources. trends: go through the five "
        "trends below one by one for each organisation and give the numbers (1 to 5) of every trend that a cited source "
        "shows it serving; trend_reason: one sentence, from that source, saying how. Leave both empty only when no "
        "source shows it serving any of the five. tam: the size of the company's own addressable market only if a cited "
        "source states it, else empty. found_by: the ids of the searches (Q1, Q2, ...) or ERW sources (E1, ...) that "
        "surfaced it. evidence: up to six sentences about this organisation that the notes give in quotation marks as a "
        "source's own words (what it does, builds, sells, was awarded or raised), each copied whole and word for word, "
        "never a sentence of your own and never a fragment of two or three words, each with the id of the one web "
        "source (S#) whose page it is from; leave it empty when the notes quote nothing. Public companies stay in this "
        "list with their kind.\n\nThe five trends:\n"
        + "\n".join(f"{i}. {t['title']}: {t['fact'][:240]}" for i, t in enumerate(a["trends"], 1))), notes_b, SCHEMA_L)
    r.partial["land"] = land                             # session 147: the structured rows are paid for too, and what follows now reaches the network
    words = tb.policy_words(head_of(niche), {"merchant", "operators", "software", "mapping", "sensing"})      # session 169: the short domain words too
    pol = tb.policy_candidates(words or [niche])
    keys = ["capital", "incumbents", "risks"]
    extra = f"Niche: {niche}."
    if len(pol):
        keys.append("policy")
        extra += (" For the policy sheet, pick from these candidate policy actions (the ERW table policy_actions) only those "
                  "that bear on the niche, by event_id.\n\nCandidate policy actions:\n" +
                  "\n".join(f"{x['event_id']} | {x['agency']} {x['action_type']} {x['event_date']} | {x['title'][:200]} | significance {x['significance']}" for x in pol.to_dict("records")))
    if landscape_only:
        rest = {}          # the landscape's run: capital, incumbents, risks and policy are not researched
    elif landscape_from:
        rest = st["rest"]
    else:
        r.guard("structure rest")
        rest = r.structure_groups("structure", keys, extra, f"{notes_b}\n\n{notes_c}")
    # session 142: who is tied to a trend is the rule's (tie.py), read from the niche's saved evidence and this run's
    # session 147: the pages the rows cite are asked for in code (fetch) and the web tier is read from their saved text
    rows, ctx = tied_rows(r, run_id, niche, stage, geography, a["trends"][:5], land, evidence_path, log, fetch=fetch)
    report, orgs = build_report(niche, stage, geography, r, a, dict(land, organisations=rows), rest, pol, plan, log)
    tied = tie_done(ctx, orgs, log)
    key = secrets.token_urlsafe(32)
    request = pitchbook_request(run_id, niche, geography, orgs, a["trends"], key)
    state = {"run_id": run_id, "niche": niche, "stage": stage, "geography": geography, "model": r.model, "cost": r.cost, "calls": r.calls,
             "searches": r.searches, "sources": r.sources, "erw": r.erw, "notes_a": notes_a, "notes_b": notes_b, "notes_c": notes_c,
             "a": a, "land": land, "rest": rest, "plan": plan, "tie": tied,
             "funnel": [{k: o.get(k) for k in ("name", "kind", "country", "reached", "stopped", "score", "trends", "found_by", "tie", "model_trends")} for o in sorted(orgs, key=rank)]}
    return report, request, key, state


# ---------------------------------------------------------------------------------------------
# session 169: the market research is the ERW's work; companies come from a connector
# ---------------------------------------------------------------------------------------------
#
# The owner's ruling of 8 October 2026: "The ERW does not search for companies. Companies, the deal funnel, the
# pipeline, success stories and investors come from PitchBook or Harmonic once a connector works." The report keeps
# scope and definitions, five trends each drawn with a real series, where capital goes (public sources only), policy
# (the policy monitor's tables first), risks, the incumbents the sources name, timing and the references. No point of
# view: it never argues who the winners are. Classification and extraction on the small model, writing on the run's
# Sonnet-class model with the literal-number check (build.check_numbers), RUN_USD 1.00.
#
# COMPANY_SEARCH is the one switch. False (the ruling): no web search for companies, no tie checks, no page fetch;
# the five connector tabs are placeholders until a provider's answer is pasted. True: the run as it was before this
# session (execute above, kept whole), reversible by this one line.

COMPANY_SEARCH = False
SMALL = "claude-haiku-4-5"         # the small model the site's gate and the Ask planner already use
REPORT_VERSION = 2
# What each stage of the market run may cost at most, rounded up from the small call measured on 9 October 2026 (the
# session's spend plan, runs/session169/spend_plan.md): the spend a stage must find under the run's ceiling before it starts
MARKET_USD = {"market research": 0.45, "market structure": 0.12, "market structure rest": 0.12, "series pick": 0.06, "market write": 0.12, "policy pick": 0.04}
MARKET_STAGES = ("market research", "market structure", "market structure rest", "series pick", "market write", "policy pick")
CONNECTOR_NOTE = "Connect PitchBook or Harmonic to fill this"
COMPANY_COLUMNS = ["Company", "What it sells", "Founders", "Stage", "Raised", "Investors", "Founded", "Location", "Signal", "Source"]
# The owner: "for the funnel: the MCJ workbook's columns". The workbook is not on this machine (session 169 looked);
# these stand in for its columns until it is, and the session's report says so.
FUNNEL_COLUMNS = ["Company", "What it sells", "Stage", "Funnel stage", "Date sourced", "Sourced by", "Next step", "Status", "Notes", "Source"]
CONNECTOR_TABS = {
    "landscape": COMPANY_COLUMNS, "funnel": FUNNEL_COLUMNS, "pipeline": COMPANY_COLUMNS,
    "success": ["Company", "What it sells", "Outcome", "Date", "Raised before", "Investors", "Source"],
    "investors": ["Investor", "Companies backed in this niche", "Lead in", "Latest round seen", "Source"],
}
NO_SERIES = "No real series that measures this trend was found in the warehouse or at the EIA, so it is not drawn."

ARR = lambda items: {"type": "array", "items": items}      # noqa: E731
SCHEMA_M1 = obj({
    "scope": obj({"definition": S, "definition_sources": IDS,
                  "in_scope": ARR(obj({"item": S, "sources": IDS})),
                  "out_of_scope": ARR(obj({"item": S, "why": S})),
                  "sub_segments": ARR(obj({"name": S, "what": S, "sources": IDS})),
                  "definitions": ARR(obj({"term": S, "meaning": S, "sources": IDS}))}),
    "trends": ARR(obj({"title": S, "claim": S, "sources": IDS, "measure": S})),
    "timing": obj({"stage": {"type": "string", "enum": ["being installed", "deploying", "not clear from the sources"]},
                   "evidence": ARR(obj({"text": S, "sources": IDS}))}),
    "policy_fact": S,
})
SCHEMA_M2 = obj({"capital": tb.SCHEMAS["capital"], "incumbents": tb.SCHEMAS["incumbents"], "risks": tb.SCHEMAS["risks"]})
SCHEMA_PICK = obj({"picks": ARR(obj({"trend": INT, "series_id": S, "why": S}))})
SCHEMA_WRITE = obj({"trends": ARR(obj({"n": INT, "fact": S})), "timing": S, "capital": S, "incumbents": S})
SCHEMA_POLICY = obj({"fact": S, "actions": ARR(obj({"event_id": S, "why_it_matters": S}))})

NEUTRAL = ("The report is neutral: it describes the market and never argues which company or approach will win, never "
           "ranks companies and never recommends an investment.")
MARKET_RESEARCH = (
    "Research this niche for an investor who is new to it, with web search. Find and cite: (1) what the niche is exactly: "
    "its definition, what is in scope and what is out, its sub-segments, and the terms a newcomer needs; (2) the five "
    "trends that most shape it now, each with the measurable statistic that shows it (what is measured, by whom, the "
    "numbers over time), preferring trends that a public US statistic tracks over the years (the EIA, the BLS, the Census "
    "Bureau, FRED) and naming that statistic; (3) where capital goes, from public sources only: federal and state programs, grants, loans, "
    "project finance, and funding rounds the press or the companies announced, with dates, amounts and who gave them; "
    "(4) the established companies (incumbents) the sources name as active in it; (5) the policy that bears on it; "
    "(6) the risks; (7) timing: whether the market is still being installed (research, pilots, first demonstrations) or "
    "already deploying at scale, with the evidence. " + NEUTRAL + " Do not search for lists of startups. Write notes: "
    "one fact per sentence, each cited, numbers exactly as the source gives them.")


def ask_json(r, what, system, user, schema, model=None, max_tokens=8000):
    """One call that answers JSON in the schema given, charged to the run (the cost ledger records it too)."""
    m = model or r.model
    resp = r.client.messages.create(
        model=m, max_tokens=max_tokens, system=system, messages=[{"role": "user", "content": user}],
        output_config={**({} if "haiku" in m else {"effort": "medium"}), "format": {"type": "json_schema", "schema": schema}})
    r.charge(resp, what, model)
    if resp.stop_reason != "end_turn":
        raise RuntimeError(f"{what}: stop_reason {resp.stop_reason}")
    return json.loads(next(b.text for b in resp.content if b.type == "text"))


def plain_num(v):
    """A value as the table holds it: never in exponent form, never rounded."""
    return str(int(v)) if float(v).is_integer() else f"{v:.6f}".rstrip("0").rstrip(".")


def browse_url(s):
    """The address a reader may open for a series: the publisher's own browser page (the API needs a key)."""
    if s["source"] == "EIA" and s["url"].startswith("https://api.eia.gov/v2/"):
        route = s["url"].split("?", 1)[0][len("https://api.eia.gov/v2/"):].rstrip("/")
        route = route[:-len("/data")] if route.endswith("/data") else route
        return "https://www.eia.gov/opendata/browser/" + route
    return s["url"]


def pick_series(r, trends, cat, log):
    """The classification call: one catalog id a trend, or none. Ids not in the catalog are none."""
    ids = {e["id"] for e in cat}
    trend_lines = "\n".join(f"{n}. {t['title']}: {t['claim'][:300]} (what would measure it: {t.get('measure', '')[:200]})" for n, t in enumerate(trends, 1))
    got = ask_json(r, "classify: a series for each trend", (
        "You match each trend of a market report to at most one statistical series from a catalog. Pick the series that "
        "measures the trend itself, or else the activity in the niche's own market that the trend is about (for example US "
        "geothermal generation for a trend about geothermal deployment, or US natural gas vented and flared for a trend "
        "about methane emissions from oil and gas), in the United States or for the whole market. Answer \"none\" when no "
        "series in the catalog is about the same activity: a series about something else is never picked to fill a gap. "
        "When an ERW series and an outside series fit equally, pick the ERW one. Use each series for one trend at most."),
        f"Trends:\n{trend_lines}\n\nCatalog (id | publisher | title | unit | frequency; span):\n{sr.lines(cat)}", SCHEMA_PICK, model=SMALL, max_tokens=2000)
    out, used = {}, set()
    for p in got.get("picks") or []:
        n, sid = p.get("trend"), (p.get("series_id") or "").strip()
        if isinstance(n, int) and 1 <= n <= len(trends) and sid in ids and sid not in used:
            out[n] = {"id": sid, "why": clean(p.get("why", ""))[:300]}
            used.add(sid)
    log(f"  series picked: {', '.join(f'trend {n}: {v['id']}' for n, v in sorted(out.items())) or 'none'}")
    return out


def execute_market(r, run_id, niche, stage, geography, log, series_count=None, raw_dir=None):
    """The run since session 169. Returns (report, pitchbook_request, key, state)."""
    log(f"run {run_id}: niche {niche!r}; stage {stage or 'any'}; geography {geography or 'any'}; the market research (no company search); "
        f"writer {r.model}, small model {SMALL}; stop at USD {r.max_usd:.2f}")
    sysm = (f"You research one niche for an investor's market report, for the Energy Research Warehouse (ERW). Niche: {niche}. "
            f"Stage of interest: {stage or 'any'}. Geography: {geography or 'any, US first'}. Rules: state facts with their numbers "
            "exactly as the source gives them, and cite them. Write \"not disclosed\" where a source does not give a figure. Never "
            "invent a company, a number, a round or an investor.")
    r.guard("market research")
    notes = r.research("research: the market", sysm, MARKET_RESEARCH, 8, erw_tools=False, model=SMALL)
    r.partial = {"run_id": run_id, "niche": niche, "notes": notes, "sources": r.sources, "erw": r.erw}      # a paid answer is kept
    r.guard("market structure")
    m1 = r.structure("structure (scope, trends, timing)", (
        f"Niche: {niche}. Write the scope (definition; what is in scope and out; the sub-segments; the terms a newcomer needs "
        "with their meanings), exactly five trends (a short title; the claim in one or two sentences as the sources state it; "
        "what statistic would measure it), the timing (is the market still being installed or already deploying, and the "
        "evidence sentences from the notes), and one sentence on the policy that bears on it. " + NEUTRAL), notes, SCHEMA_M1, model=SMALL)
    m1["trends"] = m1["trends"][:5]
    r.partial["m1"] = m1
    r.guard("market structure rest")
    m2 = r.structure("structure (capital, incumbents, risks)", (
        f"Niche: {niche}. Capital: where money goes in this niche, from public sources only (programs, grants, loans, project "
        "finance, announced rounds), each row dated and cited. Incumbents: the established companies the notes name as "
        "active in the niche; metric is \"Role in the niche\" and value is one line from the sources on what it does there. "
        "Risks: what could go wrong for the market, each cited. " + NEUTRAL), notes, SCHEMA_M2, model=SMALL)
    r.partial["m2"] = m2
    # the series: the warehouse's first, then the EIA's; one classification call, then the pulls in code
    cat = sr.catalog(TABLE_DIR or ip.OUT_DIR, log)
    r.guard("series pick")
    picks = pick_series(r, m1["trends"], cat, log)
    by_id = {e["id"]: e for e in cat}
    count = series_count or sr.Count(None)
    series, pulls = {}, []
    for n, p in sorted(picks.items()):
        try:
            s = sr.pull(by_id[p["id"]], count, TABLE_DIR or ip.OUT_DIR, log, raw_dir)
            series[n] = dict(s, why=p["why"])
            pulls.append({"trend": n, "id": p["id"], "ok": True, "points": len(s["points"])})
        except Exception as exc:
            pulls.append({"trend": n, "id": p["id"], "ok": False, "error": f"{type(exc).__name__}: {str(exc)[:200]}"})
            log(f"  trend {n}: the series {p['id']} could not be pulled ({type(exc).__name__}: {str(exc)[:160]}); the trend is not drawn")
    # each series is a source of the run: its numbers are the text its sentence is checked against
    series_ids = {}
    for n, s in series.items():
        if s["source"] == "ERW":
            eid = f"E{len(r.erw) + 1}"
            r.erw.append({"id": eid, "tool": "series", "args": {"table": s["url"][4:]}, "result": sr.describe(s), "error": False})
            series_ids[n] = eid
        else:
            series_ids[n] = r.source(browse_url(s), f"{s['note']}: {s['title']}", cited=sr.describe(s))
            r.sources[browse_url(s)]["retrieved"] = s["retrieved"]
    # the writing: one call on the run's model, every number from the material given
    blocks = []
    for n, t in enumerate(m1["trends"], 1):
        passages = " | ".join(x[:400] for x in r.texts_of(t["sources"])[:6])
        blocks.append(f"Trend {n}: {t['title']}\nClaim (cited): {t['claim']}\nCited passages: {passages or 'none'}\n"
                      f"Series: {sr.describe(series[n]) if n in series else 'none'}")
    cap_lines = "\n".join(f"- {x['date']} {x['company']} {x['kind']} {x['amount']} {x['currency']} ({', '.join(x['sources'])})" for x in m2["capital"]["rounds"][:20])
    inc_lines = "\n".join(f"- {x['name']} ({x['kind']}): {x['value']}" for x in m2["incumbents"]["players"][:20])
    tim = m1["timing"]
    r.guard("market write")
    w = ask_json(r, "write: facts, timing, capital, incumbents", (
        "You write short, plain sentences for an investor's market report. Use only the numbers given in the material, "
        "copied exactly as written there (you may round a value to fewer digits, never change it). Never invent a number, "
        "a company or a date. " + NEUTRAL + " No em dashes."),
        f"Niche: {niche}\n\nFor each trend write ONE sentence, the trend's Fact, that states the trend with its number: from "
        "the series when one is given (its latest value and the change over the years shown), else from the cited passages. "
        "Take every number from the series or the cited passages only, never from the claim alone: a number that is not "
        "in them is not written. "
        f"Then: timing, two sentences on whether the market is still being installed or already deploying ({tim['stage']}), "
        "from the evidence; capital, two sentences on where money goes, from the rows; incumbents, one sentence on who they are.\n\n"
        + "\n\n".join(blocks) + "\n\nTiming evidence:\n" + "\n".join(f"- {e['text']}" for e in tim["evidence"][:8])
        + f"\n\nCapital rows:\n{cap_lines or 'none'}\n\nIncumbents:\n{inc_lines or 'none'}", SCHEMA_WRITE, max_tokens=4000)
    facts = {x["n"]: x["fact"] for x in w.get("trends") or [] if isinstance(x.get("n"), int)}
    # policy: the policy monitor's tables first (policy_actions), the small model picks those that bear on the niche
    words = tb.policy_words(head_of(niche), {"merchant", "operators", "software", "mapping", "sensing"})
    pol = tb.policy_candidates(words or [niche])
    chosen = {"fact": m1.get("policy_fact", ""), "actions": []}
    if len(pol):
        r.guard("policy pick")
        chosen = ask_json(r, "classify: policy actions", "You pick, from a list of policy actions, those that bear directly on a niche, by event_id. " + NEUTRAL,
                          f"Niche: {niche}\n\nCandidate policy actions (the ERW table policy_actions):\n" + "\n".join(
                              f"{x['event_id']} | {x['agency']} {x['action_type']} {x['event_date']} | {x['title'][:200]}" for x in pol.to_dict("records")),
                          SCHEMA_POLICY, model=SMALL, max_tokens=2000)
    report = market_report(niche, stage, geography, r, m1, m2, series, series_ids, facts, w, chosen, pol, log)
    key = secrets.token_urlsafe(32)
    request = pitchbook_request(run_id, niche, geography, [], [{"search_phrases": [t["title"]]} for t in m1["trends"]], key)
    state = {"run_id": run_id, "niche": niche, "stage": stage, "geography": geography, "model": r.model, "small_model": SMALL, "cost": r.cost, "calls": r.calls,
             "searches": r.searches, "sources": r.sources, "erw": r.erw, "notes": notes, "m1": m1, "m2": m2, "picks": picks, "pulls": pulls,
             "series_requests": count.n, "write": w, "policy": chosen, "company_search": COMPANY_SEARCH}
    return report, request, key, state


def market_report(niche, stage, geography, r, m1, m2, series, series_ids, facts, w, chosen, pol, log):
    """The report of a run since session 169 (version 2). It keeps every key of version 1, so a page that reads only
    those still draws it: the connector tabs' keys hold empty lists."""
    known = {s["id"] for s in r.sources.values()} | {e["id"] for e in r.erw}
    keep = lambda ids: [i for i in (ids or []) if i in known]      # noqa: E731
    used = set()

    def T(t, ids, where):
        ids = keep(ids)
        used.update(ids)
        return text(t, r, ids, log, where)

    sc = m1["scope"]
    scope = {"definition": T(sc["definition"], sc["definition_sources"], "scope definition"),
             "value_chain": [], "excluded": [{"niche": clean(x["item"]), "why": clean(x["why"])} for x in sc["out_of_scope"]],
             "definitions": [{"term": clean(d["term"]), "meaning": T(d["meaning"], d["sources"], "definition")} for d in sc["definitions"] if keep(d["sources"])],
             "in_scope": [T(x["item"], x["sources"], "in scope") for x in sc["in_scope"] if keep(x["sources"])],
             "sub_segments": [{"name": clean(x["name"]), "what": T(x["what"], x["sources"], "sub-segment")} for x in sc["sub_segments"] if keep(x["sources"])]}
    trends, checked = [], {"facts": 0, "unconfirmed": 0}
    for n, t in enumerate(m1["trends"], 1):
        s = series.get(n)
        ids = keep(t["sources"]) + ([series_ids[n]] if n in series_ids else [])
        used.update(ids)
        fact = text(facts.get(n) or t["claim"], r, ids, log, f"trend {n} fact")
        checked["facts"] += 1
        if facts.get(n) and "not confirmed" in fact["text"]:
            # a written Fact holding a number no source holds is not shown: the trend's cited claim stands in its place
            checked["unconfirmed"] += 1
            log(f"    trend {n}: the written Fact holds a number no source holds; the cited claim is shown instead")
            fact = text(t["claim"], r, ids, log, f"trend {n} claim")
        item = {"n": n, "title": clean(t["title"]), "fact": fact, "sources": ids, "table": {"columns": [], "rows": []},
                "chart": {"kind": "none", "title": "", "category": 0, "values": [1], "unit": ""}, "series": None, "no_series": NO_SERIES}
        if s:
            item["table"] = {"columns": ["Period", clean(s["title"])], "rows": [[p, plain_num(v)] for p, v in s["points"]]}
            item["chart"] = {"kind": "line", "title": clean(s["title"]), "category": 0, "values": [1], "unit": clean(s["unit"])}
            item["series"] = {"id": s["id"], "source": s["source"], "title": clean(s["title"]), "unit": clean(s["unit"]), "freq": s["freq"],
                              "url": browse_url(s) if s["source"] != "ERW" else "", "retrieved": s["retrieved"], "points": len(s["points"]), "cut": s["cut"],
                              "source_line": series_line(s), "source_id": series_ids.get(n, "")}
            item["no_series"] = ""
        trends.append(item)
    log(f"  the literal-number check: {checked['facts']} trend facts, {checked['unconfirmed']} written with a number no source holds (replaced by the cited claim)")
    r.checked = checked
    cap = m2["capital"]
    rounds = []
    for x in cap["rounds"]:
        ids = keep(x["sources"])
        if not ids:
            continue
        used.update(ids)
        x = dict(x, sources=ids)
        date, investors = tb.capital_checked(r, x, log)
        rounds.append({"date": cell(date, r, ids, log, "capital date"), "company": clean(x["company"]), "kind": clean(x["kind"]),
                       "amount": cell(f"{x['amount']} {x['currency']}".strip() if x["amount"] else "", r, ids, log, f"capital {x['company']}"),
                       "investors": cell(investors, r, ids, log, "capital investors"), "sources": ids})
    cap_ids = sorted({i for x in rounds for i in x["sources"]})
    players = [{"name": clean(p["name"]), "kind": clean(p["kind"]), "ticker": clean(p["ticker"]), "metric": clean(p["metric"]) or "Role in the niche",
                "value": cell(p["value"], r, keep(p["sources"]), log, f"incumbent {p['name']}"), "as_of": clean(p["as_of"]), "sources": keep(p["sources"])}
               for p in m2["incumbents"]["players"] if keep(p["sources"])]
    inc_ids = sorted({i for p in players for i in p["sources"]})
    risks = [{"risk": clean(x["risk"]), "how": clean(tb.check_numbers(r, x["how_it_breaks_the_thesis"], keep(x["sources"]), log, "risk")),
              "not_known": clean(x["not_known"]), "sources": keep(x["sources"])} for x in m2["risks"]["risks"] if keep(x["sources"])]
    for x in risks + players:
        used.update(x["sources"])
    policy = {"fact": clean(chosen.get("fact") or m1.get("policy_fact", "")), "actions": []}
    if pol is not None and len(pol):
        by = {x["event_id"]: x for x in pol.to_dict("records")}
        reads = read_table("policy_reads")
        read_by = {x["event_id"]: x for x in reads.to_dict("records")} if reads is not None and "event_id" in reads.columns else {}
        for x in chosen.get("actions") or []:
            p = by.get(x.get("event_id"))
            if p:
                rd = read_by.get(x["event_id"], {})
                policy["actions"].append({"date": p.get("event_date", "")[:10], "agency": p.get("agency", ""), "title": clean(p.get("title", "")),
                                          "why": clean(x.get("why_it_matters", "")), "url": p.get("source_url", ""), "read": clean(rd.get("read", "") or rd.get("plain_read", ""))})
    tim = m1["timing"]
    timing = {"stage": tim["stage"], "text": T(w.get("timing", ""), sorted({i for e in tim["evidence"] for i in e["sources"]}), "timing"),
              "evidence": [T(e["text"], e["sources"], "timing evidence") for e in tim["evidence"] if keep(e["sources"])]}
    report = {"version": REPORT_VERSION, "niche": niche, "stage": stage, "geography": geography, "built": ip.utc_iso(dt.datetime.now(dt.timezone.utc)),
              "sources": [], "scope": scope, "trends": trends,
              "landscape": {"fact": {"text": "", "sources": []}, "rule": "", "companies": []}, "funnel": {"stages": [], "companies": []}, "pipeline": {"companies": []},
              "capital": {"fact": T(w.get("capital", "") or cap["fact"], cap_ids or cap["fact_sources"], "capital fact"), "rounds": rounds},
              "incumbents": {"fact": T(w.get("incumbents", "") or m2["incumbents"]["fact"], inc_ids or m2["incumbents"]["fact_sources"], "incumbents fact"), "players": players},
              "risks": risks, "policy": policy, "timing": timing,
              "connector_tabs": {"note": CONNECTOR_NOTE, "columns": CONNECTOR_TABS}}
    by_id = {s["id"]: s for s in r.sources.values()}
    erw = {e["id"]: e for e in r.erw}
    for i in sorted(used, key=lambda s: (s[0], int(s[1:]) if s[1:].isdigit() else 0)):
        if i in by_id:
            s = by_id[i]
            report["sources"].append({"id": i, "kind": "web", "title": clean(s["title"])[:200], "url": s["url"], "retrieved": s.get("retrieved", "")})
        elif i in erw:
            report["sources"].append({"id": i, "kind": "erw", "title": f"ERW table {erw[i]['args'].get('table') or 'query'}", "url": "", "retrieved": dt.date.today().isoformat()})
    return report


def series_line(s):
    """The source line under a trend's chart, in the words each publisher's terms ask for."""
    if s["source"] == "ERW":
        return f"Source: ERW table {s['url'][4:]}" + (f", retrieved {day_words(s['retrieved'])}" if s.get("retrieved") else "") + "."
    if s["source"] == "EIA":
        return f"Source: U.S. Energy Information Administration ({day_words(s['retrieved'])}), {s['title']}."
    return f"Source: {s['source']}, {s['title']}, retrieved {day_words(s['retrieved'])}."


# ---------------------------------------------------------------------------------------------
# the internal table (service connection; never the site's public key)
# ---------------------------------------------------------------------------------------------

def db():
    import psycopg
    url = os.environ.get("SUPABASE_DB_URL")
    if not url:
        try:
            from dotenv import dotenv_values
            url = dotenv_values(os.path.join(ROOT, ".env")).get("SUPABASE_DB_URL")
        except ImportError:
            url = None
    if not url:
        raise RuntimeError("SUPABASE_DB_URL is not set: the run cannot be stored")
    return psycopg.connect(url, autocommit=True, connect_timeout=30)


def claim(conn, run_id):
    """Mark a queued run as running and return (niche, stage, geography), or None when it is not there or not queued."""
    row = conn.execute("update public.thesis_runs set status = 'running', started_at = now() where run_id = %s and status = 'queued' "
                       "returning niche, stage, geography", (run_id,)).fetchone()
    return row


def spent_today(conn):
    return float(conn.execute("select coalesce(sum(usd), 0) from public.thesis_runs where (requested_at at time zone 'utc')::date = (now() at time zone 'utc')::date").fetchone()[0])


GATE_WHY = ("few_words", "sector_only", "open", "command_line")


def gate_of(conn, run_id):
    """Session 169: what the gate on the niche stored with a run that was started with "Run anyway" (thesis_runs.gate,
    migration 026; site/lib/thesis/niche.ts), as the report carries it: {"forced": True, "why", "topic", "at"}, or
    None for a run that passed the gate. A database that does not hold the column yet answers with an error: the run
    then has no flag, as every run before the migration."""
    if conn is None:
        return None
    try:
        row = conn.execute("select gate from public.thesis_runs where run_id = %s", (run_id,)).fetchone()
    except Exception:
        return None
    return gate_flag(row[0] if row else None)


def gate_flag(g):
    """The stored gate as the report's flag, read as data: only a forced run has one, and only these four fields."""
    if isinstance(g, str):
        try:
            g = json.loads(g)
        except ValueError:
            return None
    if not isinstance(g, dict) or g.get("forced") is not True:
        return None
    why = g.get("why") if g.get("why") in GATE_WHY else "open"
    topic = g.get("topic") if isinstance(g.get("topic"), str) and re.fullmatch(r"[a-z_]{1,40}", g["topic"]) else None
    at = g.get("at") if isinstance(g.get("at"), str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}T[\d:.]{8,15}Z", g["at"]) else ""
    return {"forced": True, "why": why, "topic": topic, "at": at}


def finish(conn, run_id, report, request, key, usd):
    from psycopg.types.json import Jsonb
    conn.execute("update public.thesis_runs set status = 'done', finished_at = now(), usd = %s, report = %s, pitchbook_request = %s, "
                 "pitchbook_key = %s, note = '' where run_id = %s", (usd, Jsonb(report), Jsonb(request), key, run_id))


def fail(conn, run_id, note, usd):
    conn.execute("update public.thesis_runs set status = 'failed', finished_at = now(), usd = %s, note = %s where run_id = %s", (usd, note[:300], run_id))


BUCKET_STATE = "bucket:"        # --landscape-from bucket:<name>: a saved state kept in the private bucket (store.py, states/<name>.json.gz)


def ledger_rows():
    """This process's rows of the cost ledger, as the ledger wrote them. On the runner the ledger's file is the runner's
    own and is discarded with it, so a run's rows travel in its state (session 158). [] when the ledger is off."""
    try:
        import llm
        rows = llm.read_ledger()
        mine = os.environ.get("ERW_RUN_ID", "").strip() or llm._START
        return rows[rows["run_id"] == mine].to_dict("records")
    except Exception:
        return []


def keep_in_bucket(handle, in_bucket, name, state, log):
    """Session 158: a run whose evidence store is the bucket (the runner) keeps its state there too. The runner's files
    are discarded with it; the state holds the answers the run paid for (the notes, the structured rows) and its rows
    of the cost ledger. A refusal is logged and never costs the run: the local file is already written."""
    if not in_bucket or handle is None or not hasattr(handle, "keep_state"):
        return ""
    try:
        where = handle.keep_state(name, dict(state, ledger=ledger_rows()))
        log(f"state kept (bucket): {where}")
        return where
    except Exception as exc:
        log(f"STATE NOT KEPT IN THE BUCKET ({type(exc).__name__}: {str(exc)[:200]}); it is in the local file only")
        return ""


def one(conn, run_id, niche, stage, geography, args, log):
    """Run one claimed run and store it. Returns the spend."""
    cap = min(args.max_usd, RUN_USD)
    if args.spent_file:
        spent = json.load(open(args.spent_file))["usd"] if os.path.exists(args.spent_file) else 0.0
        cap = min(cap, args.session_cap - spent)
    elif conn is not None:
        cap = min(cap, DAY_USD - spent_today(conn))
    market = not COMPANY_SEARCH and not args.landscape_from and not args.landscape_only      # session 169
    first = (sum(MARKET_USD[k] for k in MARKET_STAGES) if market else
             STAGE_USD["landscape"] + STAGE_USD["structure landscape"] + (0 if args.landscape_from else STAGE_USD["research a"] + STAGE_USD["structure a"]))
    if cap < first:          # a run that cannot reach its landscape is not started: nothing is spent on a report that cannot be written
        if conn is not None:
            fail(conn, run_id, "The spending limit for Thesis Builder is reached. The run did not start.", 0)
        log(f"run {run_id}: the spending limit is reached; not started")
        return 0.0
    t0, usd, r = time.time(), 0.0, None
    in_bucket, handle = False, None
    try:
        r = Careful(log, cap)
        state_dir = getattr(args, "state_dir", None) or STATE_DIR
        evidence_dir = getattr(args, "evidence_dir", None) or os.path.join(state_dir, "evidence")
        # session 147: the store is the private bucket when the service key is set (the runner has it), else the local file
        handle = None if (getattr(args, "no_evidence", False) or market) else es.open_store(evidence_dir, niche, stage, geography, mode=getattr(args, "evidence_store", "file"), log=log)
        if getattr(handle, "kind", "") == "bucket":
            handle.ensure_bucket()
            handle.load(niche, stage, geography)         # read once before anything is paid for: a store that cannot be read stops the run here
        if handle is not None:
            log(f"  evidence store ({handle.kind}): {handle.where}")
        in_bucket = getattr(handle, "kind", "") == "bucket"      # session 158: asked before the run, since a refused write turns the handle to the file
        landscape_from = args.landscape_from
        if landscape_from and str(landscape_from).startswith(BUCKET_STATE):
            # session 158: the saved state of an earlier run, read from the private bucket before anything is paid for
            name = str(landscape_from)[len(BUCKET_STATE):]
            os.makedirs(state_dir, exist_ok=True)
            landscape_from = os.path.join(state_dir, f"from_bucket_{name}.json")
            json.dump(es.read_state(name), open(landscape_from, "w", encoding="utf-8"), default=str)
            log(f"  the saved state {name} is read from the private bucket ({es.BUCKET}/{es.state_object(name)})")
        fetch = None if getattr(args, "no_fetch", True) else {"count": pg.Count(getattr(args, "fetch_count_file", None)), "raw_dir": getattr(args, "raw_dir", None),
                                                              "max_session": getattr(args, "fetch_session_cap", None) or pg.MAX_ADDRESSES_SESSION}
        if market:          # session 169: the market research; no company search, no tie checks, no page fetch
            report, request, key, state = execute_market(r, run_id, niche, stage, geography, log,
                                                         series_count=sr.Count(getattr(args, "series_count_file", None), getattr(args, "series_cap", None) or sr.MAX_REQUESTS_RUN),
                                                         raw_dir=getattr(args, "raw_dir", None))
        else:
            report, request, key, state = execute(r, run_id, niche, stage, geography, log, searches=args.searches, landscape_from=landscape_from, retrend=args.retrend, landscape_only=args.landscape_only,
                                                  evidence_path=handle, fetch=fetch)
        usd = r.cost
        # session 169: a run started with "Run anyway" on a niche the gate refused carries the flag on its report
        flag = gate_flag({"forced": True, "why": "command_line"}) if getattr(args, "run_anyway", False) else gate_of(conn, run_id)
        if flag:
            report["gate"] = flag
            log(f"  the gate: this run was started with Run anyway ({flag['why']}); its report is flagged")
        os.makedirs(state_dir, exist_ok=True)
        slug = re.sub(r"[^a-z0-9]+", "-", head_of(niche).lower()).strip("-")[:50]
        path = os.path.join(state_dir, f"{slug}_{run_id}.json")
        json.dump(dict(state, report=report), open(path, "w", encoding="utf-8"), default=str)
        log(f"state saved: {os.path.relpath(path, ROOT)}")
        keep_in_bucket(handle, in_bucket, f"{slug}_{run_id}", dict(state, report=report), log)
        if conn is not None:
            finish(conn, run_id, report, request, key, usd)
        f = report["funnel"]["stages"]
        drawn = sum(1 for t in report["trends"] if t.get("series"))
        line = (f"thesis run {run_id}: {r.calls} calls, {r.searches} searches, USD {usd:.4f}, {(time.time() - t0) / 60:.1f} min; trends {len(report['trends'])}"
                + (f" ({drawn} drawn with a real series)" if market else "") + f"; funnel {' > '.join(str(s['n']) for s in f) or 'a connector tab'}; state {os.path.relpath(path, ROOT)}")
        log(line); print(line)
    except tb.Budget as exc:
        usd = r.cost if r is not None else 0.0
        log(f"run {run_id} stopped at its spending limit: {exc}")
        if getattr(r, "partial", None):               # session 142: the research already paid for is saved, not thrown away
            keep_dir = getattr(args, "state_dir", None) or STATE_DIR
            os.makedirs(keep_dir, exist_ok=True)
            keep = os.path.join(keep_dir, f"partial_{run_id}.json")
            json.dump(r.partial, open(keep, "w", encoding="utf-8"), default=str)
            log(f"the research this run paid for is kept: {os.path.relpath(keep, ROOT)}")
            keep_in_bucket(handle, in_bucket, f"partial_{run_id}", r.partial, log)
        if conn is not None:
            fail(conn, run_id, "The run reached its spending limit before it finished. Nothing partial is shown.", usd)
        print(f"thesis run {run_id} STOPPED at its spending limit", file=sys.stderr)
    except (Exception, SystemExit):      # SystemExit: a guard that refuses to start (the data lock) exits; the row must not stay "running"
        usd = r.cost if r is not None else 0.0
        trace = ip.redact(traceback.format_exc())
        log(f"run {run_id} FAILED after USD {usd:.4f}:\n{trace}")
        if getattr(r, "partial", None):               # session 147: whatever was paid for before the failure is kept
            keep_dir = getattr(args, "state_dir", None) or STATE_DIR
            os.makedirs(keep_dir, exist_ok=True)
            keep = os.path.join(keep_dir, f"partial_{run_id}.json")
            json.dump(r.partial, open(keep, "w", encoding="utf-8"), default=str)
            log(f"the answers this run paid for are kept: {os.path.relpath(keep, ROOT)}")
            keep_in_bucket(handle, in_bucket, f"partial_{run_id}", r.partial, log)
        if conn is not None:
            fail(conn, run_id, "The run failed before it finished. Nothing partial is shown.", usd)
        print(f"thesis run {run_id} FAILED: {trace.strip().splitlines()[-1][:300]}", file=sys.stderr)
    if args.spent_file:
        spent = json.load(open(args.spent_file))["usd"] if os.path.exists(args.spent_file) else 0.0
        json.dump({"usd": round(spent + usd, 4)}, open(args.spent_file, "w"))
    return usd


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW Thesis Builder: one run for the page /thesis")
    ap.add_argument("--run-id")
    ap.add_argument("--queue", action="store_true")
    ap.add_argument("--niche")
    ap.add_argument("--stage", default="")
    ap.add_argument("--geography", default="")
    ap.add_argument("--store", action="store_true", help="with --niche: keep the run in the internal table")
    ap.add_argument("--landscape-from", help="a saved state: its scope and trends are reused and the landscape stage runs again "
                                             "(a file, or bucket:<name> for a state kept in the private bucket)")
    ap.add_argument("--retrend", action="store_true", help="with --landscape-from: write the scope and trends again from the saved research")
    ap.add_argument("--landscape-only", action="store_true", help="scope, trends and the landscape only: no capital, incumbents, risks or policy")
    ap.add_argument("--run-anyway", action="store_true", help="with --niche: flag the report as a run started with Run anyway (session 169)")
    ap.add_argument("--max-usd", type=float, default=RUN_USD)
    ap.add_argument("--searches", type=int, default=8)
    ap.add_argument("--spent-file", help="a file holding what a session has spent, raised by this run")
    ap.add_argument("--session-cap", type=float, default=6.0)
    ap.add_argument("--state-dir", help="where the run's state is saved (default: warehouse/output/thesis_state)")
    ap.add_argument("--evidence-dir", help="where the niche's evidence store is kept (default: <state dir>/evidence)")
    ap.add_argument("--no-evidence", action="store_true", help="read and save no evidence store: the rule sees this run's evidence only")
    ap.add_argument("--evidence-store", choices=["auto", "bucket", "file"], default="auto",
                    help="where the niche's evidence store is kept: the private storage bucket when SUPABASE_URL and SUPABASE_SERVICE_KEY are set (auto), else the local file")
    ap.add_argument("--no-fetch", action="store_true", help="ask for no page: the rule reads the pages the store already holds")
    ap.add_argument("--fetch-count-file", help="a file holding the addresses and requests a session has made, raised by this run")
    ap.add_argument("--fetch-session-cap", type=int, help=f"the session's ceiling of addresses with --fetch-count-file (default {pg.MAX_ADDRESSES_SESSION})")
    ap.add_argument("--raw-dir", help="keep each page as received (bytes) in this folder, named by its SHA-256")
    ap.add_argument("--in-dir", help="read the warehouse's tables from this folder instead of warehouse/output")
    ap.add_argument("--series-count-file", help="session 169: a file holding the series requests a session has made, raised by this run")
    ap.add_argument("--series-cap", type=int, help=f"session 169: the ceiling of series requests (default {sr.MAX_REQUESTS_RUN}, one run's)")
    args = ap.parse_args(argv)
    if args.in_dir:
        global TABLE_DIR
        TABLE_DIR = tb.TABLE_DIR = os.path.abspath(args.in_dir)
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"thesis_run_{stamp}.log"))
    rc = 0
    try:
        if args.niche:
            run_id = stamp + "-" + secrets.token_hex(3)
            conn = db() if args.store else None
            if conn is not None:
                conn.execute("insert into public.thesis_runs (run_id, niche, stage, geography, status, started_at) values (%s, %s, %s, %s, 'running', now())",
                             (run_id, args.niche, args.stage, args.geography))
            one(conn, run_id, args.niche, args.stage, args.geography, args, log)
        else:
            conn = db()
            if args.run_id:
                ids = [args.run_id]
            else:
                ids = [x[0] for x in conn.execute("select run_id from public.thesis_runs where status = 'queued' order by requested_at").fetchall()]
            if not ids:
                print("thesis: nothing is queued")
            for run_id in ids:
                row = claim(conn, run_id)
                if row is None:
                    print(f"thesis: run {run_id} is not queued (already taken, or unknown)")
                    continue
                one(conn, run_id, row[0], row[1], row[2], args, log)
    except Exception:
        trace = ip.redact(traceback.format_exc())
        log(f"FAILED:\n{trace}")
        print(f"thesis FAILED: {trace.strip().splitlines()[-1][:300]}", file=sys.stderr)
        rc = 1
    log.close()
    return rc


if __name__ == "__main__":
    sys.exit(main())
