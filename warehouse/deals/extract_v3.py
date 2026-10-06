#!/usr/bin/env python3
"""The deals tracker, re-aimed at power deals: version 3 of the extraction (platform tool 6).

Energy Research Warehouse (ERW), session 130.

    python warehouse/deals/extract_v3.py plan                  # what would be read, by tier; no model call
    python warehouse/deals/extract_v3.py run --cap-usd 8       # read stories not yet read, to the cap
    python warehouse/deals/extract_v3.py confirm --cap-usd 8   # the second read of every deal not yet read twice
    python warehouse/deals/extract_v3.py build                 # the two tables and the site's copy, from the answers

What is read: the title and summary of every story held in warehouse/output/news_stories.csv. The ERW holds no
article body, so a figure a story keeps for its body is not here. Stories are read by cluster (stories about the same
event), in this order, until the cap:
  tier 1  the stories version 2 read (warehouse/deals/checked.csv), so the two versions can be compared like for like
  tier 2  other scored stories in a power sector, or whose words name a size, a term, storage or a transaction
  tier 3  stories never scored whose words do the same
  tier 4  the other scored stories; tier 5 the other stories never scored
A stop at the cap leaves the later tiers unread; `plan` says how many stories remain.

What is asked for, per power deal: the parties, the kind (power_purchase, tolling, offtake, project_finance,
acquisition, other), the technology, MW and MWh, the price and its unit, the term, the value in US dollars, the place,
the status, and for every number the words and the sentence it was read from.

No number without its sentence. For every number the model returns the exact words (mw_text, ...) and the sentence
(mw_sentence, ...). The code keeps the number only if
  1. the sentence is in one story's own title or summary,
  2. the words are in that sentence,
  3. the words hold the number with its unit (MW, GW; MWh, GWh; a dollar sign; "year"; a price per MWh or kWh), and
     parse to the same value, and
  4. the words are one number, not a range.
Otherwise the number is left blank and the run log says why. The sentence stored is the story's whole title, or the
whole sentence of its summary. A party, an asset and a place are kept only if the story's words hold them; a state, a
country and a status by version 2's rule (the story names them). A deal whose evidence sentence is not in a story, or
that names no party the story's words hold, is not kept at all. The kind, the technology and the datacenter flag are the model's reading of the story, not a copy of
its words: the hand check in the session report measures them.

The second read. The first read is made at low effort over many stories at once, and it lets through things that are not
deals (a plant starting up, a plan, a datacenter lease). So every deal it returns is read again at medium effort, with
its own stories only, and the model answers one question: is this a specific power transaction (power_deal), a
transaction that is not about power (not_power), or no transaction at all (not_a_transaction), and of what kind. Only a
power_deal enters the table, with the second read's kind and its datacenter flag. The second read also says whether
the story states who buys and who sells; where it does not (partners, a joint venture), the names are kept as parties
with no side. And it names any figure that is not the deal's own (a programme's total, "first deal in a $5 billion
push") and any name that is not a party to the deal (the backer in "Blackstone-backed X"); those are left blank. A deal not yet read a second time is not in the table.

Duplicates: stories of one cluster make one deal. Deals from different clusters are folded into one when the kind is
the same, their dates are within 60 days, no figure both state differs, and either their named parties are the same
(two or more), or they share a party and a figure, or within 3 days they share a party, one of them names no other, and
both state the same technology (same_deal(), below); the earliest is kept with every story linked, and a number the kept one lacks is filled from the other with its sentence.

Outputs (the events shape, docs/datastandard.md):
  warehouse/output/power_deals.csv            license public: structured fields and story links, no outlet text
  warehouse/output/power_deals_evidence.csv   license internal: one row per deal, field and story, with the sentence
  warehouse/deals/answers_v3.jsonl            every model answer as returned, so `build` needs no model
  warehouse/deals/second_read_v3.jsonl        every second read as returned
  warehouse/deals/checked_v3.csv              every story read, with its tier
  site/data/deals_v3.json                     the review page's copy (public fields only) and the comparison with version 2
Every call is priced and recorded in the cost ledger (warehouse/llm.py); the key is ANTHROPIC_API_KEY.
"""

import argparse
import datetime as dt
import hashlib
import json
import math
import os
import re
import sys
import threading
import traceback
from concurrent.futures import ThreadPoolExecutor

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "news"))
sys.path.insert(0, os.path.join(ROOT, "warehouse"))
import iso_prices as ip  # noqa: E402
from ingest import NAME as NEWS, NEWS_COLS  # noqa: E402
from extract import DEAL_COLS as V2_COLS, FOREIGN, SCALE, STATUSES, clean, norm, pick_model, stated_words  # noqa: E402  version 2's own checks
import llm  # noqa: E402

DEALS = "power_deals"
EVIDENCE = "power_deals_evidence"
V2 = "energy_deals"
ANSWERS = os.path.join(HERE, "answers_v3.jsonl")
SECOND = os.path.join(HERE, "second_read_v3.jsonl")
CHECKED = os.path.join(HERE, "checked_v3.csv")
CHECKED_V2 = os.path.join(HERE, "checked.csv")
SITE_COPY = os.path.join(ROOT, "site", "data", "deals_v3.json")
STEP = "deals_extract_v3"
VERDICTS = ["power_deal", "not_power", "not_a_transaction"]

KINDS = ["power_purchase", "tolling", "offtake", "project_finance", "acquisition", "other"]
TECHNOLOGIES = ["solar", "wind", "storage", "nuclear", "gas", "coal", "hydro", "geothermal", "hydrogen", "fuel_cell",
                "transmission", "other"]
NUMBERS = ["mw", "mwh", "price_value", "term_years", "dollars"]
TEXT_OF = {"mw": "mw_text", "mwh": "mwh_text", "price_value": "price_text", "term_years": "term_text", "dollars": "dollars_text"}
SENTENCE_OF = {"mw": "mw_sentence", "mwh": "mwh_sentence", "price_value": "price_sentence", "term_years": "term_sentence",
               "dollars": "dollars_sentence"}
POWER_SECTORS = ["deal", "ppa", "capital", "nuclear", "generation", "datacenter_power", "renewables", "storage",
                 "power_prices", "transmission", "interconnection", "hydrogen", "grid_conditions", "company"]
# words that name a size, a term, storage or a transaction (tiers 2 and 3)
WORDS = re.compile(
    r"\d\s?-?(?:mw|gw|kw|mwh|gwh|twh|megawatts?|gigawatts?)(?![a-z])|megawatt|gigawatt|batter|energy storage|\bbess\b"
    r"|\bppa\b|power purchase|offtake|off-take|tolling|\btoll\b|acqui|to buy|\bbuys\b|\bbought\b|\bsells\b|sale of|financ"
    r"|\bloan|agreement|contract|\bsigns?\b|signed|\binks?\b|\bdeal\b|\d+\s?-?\s?years?\b")
TIER_WORDS = {1: "read by version 2", 2: "scored, a power sector or the words of a deal", 3: "not scored, the words of a deal",
              4: "scored, the rest", 5: "not scored, the rest"}
BATCH = {1: 20, 2: 25, 3: 25, 4: 40, 5: 40}   # clusters per call
WORKERS = 8
FOLD_DAYS = 60
NEAR_DAYS = 3
PER_CALL_RESERVE = 0.08   # USD held back for each call in flight, so the cap is not passed

BASE = ["event_id", "event_date", "event_type", "parties", "entity_ids", "mw", "price", "currency", "status", "source",
        "source_url"]
DEAL_COLS = BASE + ["kind", "buyer", "seller", "other_parties", "asset", "technology", "storage", "datacenter", "place",
                    "state", "country", "mwh", "dollars", "price_value", "price_unit", "term_years", "qualifiers",
                    "number_stories", "date_basis", "read_by_v2", "n_stories", "story_ids", "story_urls", "folded_ids",
                    "model_id", "extracted_at"]
EVIDENCE_COLS = BASE + ["deal_id", "story_id", "field", "value", "text", "sentence"]
CHECKED_COLS = ["story_id", "cluster", "tier", "checked_at", "model_id", "n_deals"]

SYSTEM = f"""You read news stories for the Energy Research Warehouse (ERW) and extract power deals.

Each item is one cluster: one or more stories (a title, and a summary when the story has one) about the same event, numbered c. Decide whether the cluster reports a power deal: a specific transaction between named parties whose subject is electricity, or an asset that generates, stores or transmits it. Kinds:
- power_purchase: a power purchase agreement, physical or virtual, or a contract to supply electricity to a named buyer (a utility, a company, a datacenter)
- tolling: a tolling agreement, the buyer pays for the right to dispatch a plant or a battery
- offtake: an offtake of capacity, of storage, or of clean-energy attributes that is not a power purchase agreement
- project_finance: debt, a loan, tax equity or equity raised for named power, storage or transmission projects, or by a power company
- acquisition: a power plant, a portfolio, a developer, a power company or a utility bought, sold or merged
- other: another power transaction (an equipment supply order for a plant, a lease, a joint venture, a fuel supply contract for a power plant, a grid service or interconnection contract)

Not power deals, return them under none: oil, upstream gas, LNG, pipelines, refining, mining and shipping transactions; a datacenter, chip or cloud deal with no power transaction in it; policy, regulation, rate cases, court rulings; earnings, forecasts, market commentary, prices; a plan or a project with no named counterparty and no financing.

For each power deal return:
- c: the cluster's number
- kind: one of {", ".join(KINDS)}
- buyer, seller: the parties as the story names them, copied character for character (the offtaker, acquirer, lender or investor is the buyer; the generator, the company sold, or the company raising money is the seller); empty when not named. other_parties: any other named parties
- asset: the plant, project, portfolio or company the deal is about, copied from the story; empty when not named
- technology: every technology the story states for the asset, from {", ".join(TECHNOLOGIES)}; a battery is storage; an empty list when the story does not say
- mw (capacity in MW), mwh (energy in MWh), price_value with price_unit exactly as stated (for example 50 and "USD/MWh"), term_years (the length of the contract or the loan in years), dollars (the value of the deal in US dollars)
- for every number, two more fields: the exact words you read it from, as short as they can be while holding the number and its unit (mw_text "250 MW", dollars_text "$1.2 billion", term_text "15-year"), and the whole sentence those words are in (mw_sentence, ...), both copied character for character from the title or the summary. A title counts as a sentence
- place: where the asset or the delivery is, in the story's own words; state (US two-letter code) and country only when the story names that state or that country, each with the exact words (state_text, country_text). Never infer a state or a country from a city, a region, a grid operator, a project or a company
- status: one of {", ".join(STATUSES)}, read only from the stated words, with the exact words (status_text): signed for signed, agreed, secured, awarded, inked; closed for completed, closed, finalized, or money raised; announced for announces, plans, will acquire, to buy; cancelled for cancelled, terminated, scrapped; rumored for in talks, considering, reportedly. Empty when the words do not say
- datacenter: true only if the power, the plant or the money serves datacenters or AI, as the story says
- evidence: the one sentence (or the title) that shows the transaction, copied character for character

Rules for numbers. Never infer, estimate, add up or convert a number: if the title and summary do not state it, the number, its words and its sentence are all empty strings, and that is the correct answer. A range ("200 to 300 MW") is not one number: leave it empty. Write a number as plain digits in the unit named (mw in MW, so 1.2 GW is 1200; dollars in US dollars, so $1.2 billion is 1200000000), with no commas. Do not convert another currency to dollars. Only numbers of this deal: not a company's total fleet, not a market forecast.

Return every cluster number exactly once: in a deal, or in the list none."""

S = {"type": "string"}
SCHEMA = {
    "type": "object",
    "properties": {
        "deals": {"type": "array", "items": {
            "type": "object",
            "properties": {
                "c": {"type": "integer"},
                "kind": {"type": "string", "enum": KINDS},
                "buyer": S, "seller": S, "other_parties": {"type": "array", "items": S},
                "asset": S, "technology": {"type": "array", "items": {"type": "string", "enum": TECHNOLOGIES}},
                "mw": S, "mw_text": S, "mw_sentence": S, "mwh": S, "mwh_text": S, "mwh_sentence": S,
                "price_value": S, "price_unit": S, "price_text": S, "price_sentence": S,
                "term_years": S, "term_text": S, "term_sentence": S,
                "dollars": S, "dollars_text": S, "dollars_sentence": S,
                "place": S, "state": S, "state_text": S, "country": S, "country_text": S,
                "status": {"type": "string", "enum": STATUSES + [""]}, "status_text": S,
                "datacenter": {"type": "boolean"},
                "evidence": S,
            },
            "required": ["c", "kind", "buyer", "seller", "other_parties", "asset", "technology", "mw", "mw_text",
                         "mw_sentence", "mwh", "mwh_text", "mwh_sentence", "price_value", "price_unit", "price_text",
                         "price_sentence", "term_years", "term_text", "term_sentence", "dollars", "dollars_text",
                         "dollars_sentence", "place", "state", "state_text", "country", "country_text", "status",
                         "status_text", "datacenter", "evidence"],
            "additionalProperties": False}},
        "none": {"type": "array", "items": {"type": "integer"}},
    },
    "required": ["deals", "none"],
    "additionalProperties": False,
}

SYSTEM2 = f"""You check power deals that an earlier reading extracted from news stories, for the Energy Research Warehouse (ERW).

Each item is numbered i and holds the stories (a title, and a summary when the story has one) and the deal as extracted: its kind, buyer, seller, other parties and asset, and the figures extracted with the sentence each was read from. Read the stories and give a verdict:
- power_deal: the stories report a specific transaction, and its subject is electricity or an asset that generates, stores or transmits it. A transaction is a contract, a purchase, a sale, a merger, an order, a lease, a joint venture or a financing between parties the story names, or money raised by a named company or project (the investors need not be named). It may be signed, closed, announced, or in talks. Examples: a power purchase agreement; a tolling agreement; an order for turbines, fuel cells, batteries or reactors; a contract to supply electricity to a datacenter; a loan for a named power plant; a power company or a power plant bought; a power company raising money
- not_power: a transaction, but the stories' words do not show it is about power. Examples: a datacenter built, leased, sold or financed with no power contract in the story; chips; oil, LNG or gas that is not fuel for a named power plant; a gas distribution business; mining; electric vehicles; "energy assets" or "infrastructure" that the story does not say are power assets; an investment firm raising or closing its own fund (money raised from investors for a fund, not for a named power company or project)
- not_a_transaction: no contract and no financing, or none that the story reports. Examples: a deal mentioned only in passing in a story about something else; a plant starting up or finishing construction; a company's own plan or target; a project announced by one company with no counterparty and no financing; a government programme or a total of loans to many; regulation, approvals, court rulings; commentary and forecasts

Then five more answers, for a power_deal (for the other verdicts answer other, not_stated, false and two empty lists):

not_the_deals: the figures, by name (mw, mwh, price_value, term_years, dollars), that are not this deal's own: a programme's or a company's total ("first deal in a $5 billion push"), a market figure, another deal's figure. A figure of the asset the deal is about (the plant's megawatts, the portfolio's size) is the deal's own. An empty list when every figure is the deal's own.

not_parties: the names among the buyer, the seller and the other parties that the stories do not present as a party to this transaction: an earlier backer or owner named only in a description ("Blackstone-backed X" does not make Blackstone a party), an adviser, a company only mentioned. An empty list when every name is a party.

roles: stated when the stories' words say which party buys, takes the power, lends or invests, and which sells, supplies or receives the money ("X to buy Y", "X signs a power deal with utility Y to supply its datacenter", "X raises money from Y"); not_stated when the parties are partners (a joint venture, a partnership, co-investors, "X and Y to develop") or the words do not say who is on which side.

datacenter: true only when the stories' words say the power, the plant, the equipment or the money serves datacenters or AI.

kind:
{chr(10).join("- " + k for k in KINDS)}
power_purchase is a contract to buy or supply electricity; tolling a tolling agreement; offtake an offtake of capacity, storage or attributes that is not a power purchase; project_finance debt, a loan, tax equity or equity raised; acquisition a plant, portfolio or company bought, sold or merged; other any other power transaction (an equipment order, a lease, a joint venture, a fuel supply contract for a power plant, a grid connection contract).

Return every item number exactly once."""
SCHEMA2 = {
    "type": "object",
    "properties": {"checks": {"type": "array", "items": {
        "type": "object",
        "properties": {"i": {"type": "integer"}, "verdict": {"type": "string", "enum": VERDICTS},
                       "not_the_deals": {"type": "array", "items": {"type": "string", "enum": NUMBERS}},
                       "not_parties": {"type": "array", "items": {"type": "string"}},
                       "roles": {"type": "string", "enum": ["stated", "not_stated"]}, "datacenter": {"type": "boolean"},
                       "kind": {"type": "string", "enum": KINDS}},
        "required": ["i", "verdict", "not_the_deals", "not_parties", "roles", "datacenter", "kind"], "additionalProperties": False}}},
    "required": ["checks"], "additionalProperties": False,
}
BATCH2 = 20

# ------------------------------------------------------------------ the checks (pure; tests/test_session130.py)

NUMBER_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
                "ten": 10, "eleven": 11, "twelve": 12, "fifteen": 15, "twenty": 20, "thirty": 30}
RANGE = re.compile(r"\d\s*(?:-|to|and)\s*\$?\d|between")
UNIT_PRICE = re.compile(r"(?:/|\bper\b|\ba\b)\s*-?\s*(?:mwh|kwh|megawatt.?hours?|kilowatt.?hours?|kw.?month|kw.?year|mw.?day|mw.?year)")
FIRST_NUMBER = re.compile(r"(?:us)?\$?\s*\d|\b(?:" + "|".join(NUMBER_WORDS) + r")\b")
# "over" limits a number only after worth, of, for, raises or raised; "in talks over $7 billion plant" is not a limit
QUALIFIER = re.compile(r"(up to|as much as|at least|more than|(?:(?<=worth )|(?<=of )|(?<=for )|(?<=raises )|(?<=raised ))over|nearly|about|"
                       r"around|roughly|approximately|almost|an estimated|estimated)\s*(?:us)?\$?\s*$")


def split_sentences(text):
    """A summary's sentences, as written (a summary cut short ends in its last fragment)."""
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\"'(\[])", " ".join(str(text).split()))
    return [p for p in parts if p]


def find_sentence(wanted, stories):
    """(story_id, the story's own whole sentence) holding the words `wanted`, or None. A title is one sentence."""
    w = norm(wanted)
    if not w:
        return None
    for s in stories:
        if w in norm(s["title"]):
            return s["event_id"], " ".join(s["title"].split())
    for s in stories:
        if w not in norm(s["summary"]):
            continue
        sents = split_sentences(s["summary"])
        for n in range(1, len(sents) + 1):          # the fewest whole sentences that hold the words
            for i in range(0, len(sents) - n + 1):
                run = " ".join(sents[i:i + n])
                if w in norm(run):
                    return s["event_id"], run
    return None


def span_numbers(span):
    """Every number the words hold: digits, and the number words to twelve (and fifteen, twenty, thirty)."""
    nums = [float(m.replace(",", "")) for m in re.findall(r"\d[\d,]*(?:\.\d+)?", span)]
    nums += [float(NUMBER_WORDS[w]) for w in re.findall(r"[a-z]+", span.lower()) if w in NUMBER_WORDS]
    return nums


def number_ok(field, value, span):
    """None when the words state this number with its unit; else the reason it is not kept."""
    s = norm(span)
    nums = span_numbers(s)
    if not nums:
        return f"no number in {span!r}"
    if RANGE.search(s):
        return f"{span!r} is a range, not one number"
    scales = [1.0]
    if field in ("mw", "mwh"):
        scales = [m for pat, m in SCALE[field] if re.search(pat, s)]
        if not scales:
            return f"{span!r} names no {field.upper()} unit"
    elif field == "dollars":
        if FOREIGN.search(s):
            return f"{span!r} is not in US dollars"
        if not re.search(r"\$|\busd\b|dollars?", s):
            return f"{span!r} names no dollars"
        scales = [m for pat, m in SCALE["dollars"] if re.search(pat, s)] or [1.0]
    elif field == "term_years":
        if re.search(r"month", s):
            return f"{span!r} is in months"
        if not re.search(r"years?\b|\byrs?\b", s):
            return f"{span!r} names no years"
    elif field == "price_value":
        if not UNIT_PRICE.search(s):
            return f"{span!r} is not a price per unit of power or energy"
    for n in nums:
        for m in scales:
            if math.isclose(n * m, float(value), rel_tol=1e-9, abs_tol=1e-9):
                return None
    return f"{value:g} is not what {span!r} says"


def qualifier(sentence, span):
    """The word before the number that limits it ("up to", "about", "more than"), or ""."""
    s, w = norm(sentence), norm(span)
    i = s.find(w)
    if i < 0:
        return ""
    first = FIRST_NUMBER.search(w)          # the words may begin with the limit themselves ("about $1 billion")
    m = QUALIFIER.search(s[:i + (first.start() if first else 0)])
    return m.group(1) if m else ""


def check_number(field, d, stories):
    """(value, story_id, sentence, words, qualifier) for one number of a model answer, or (None, reason)."""
    raw = str(d.get(field) or "").strip()
    if raw == "":
        return None, None
    try:
        value = float(raw.replace(",", "").replace("$", ""))
    except ValueError:
        return None, f"{field} {raw!r} is not a number"
    span, sentence = d.get(TEXT_OF[field]) or "", d.get(SENTENCE_OF[field]) or ""
    if not span.strip() or not sentence.strip():
        return None, f"{field} {raw}: no words or no sentence given"
    found = find_sentence(sentence, stories)
    if found is None:
        return None, f"{field} {raw}: its sentence is not in a story: {sentence[:80]!r}"
    story_id, whole = found
    if norm(span) not in norm(whole):
        return None, f"{field} {raw}: the words {span!r} are not in its sentence"
    why = number_ok(field, value, span)
    if why:
        return None, f"{field} {raw}: {why}"
    if field == "price_value" and not str(d.get("price_unit") or "").strip():
        return None, f"{field} {raw}: no unit given"
    return (value, story_id, whole, " ".join(span.split()), qualifier(whole, span)), None


def read_deal(d, stories):
    """One model answer for one cluster, checked against the cluster's stories: (deal or None, [reasons])."""
    why = []
    text = norm(" | ".join(f"{s['title']} | {s['summary']}" for s in stories))
    ev = find_sentence(d.get("evidence") or "", stories)
    if ev is None:
        return None, [f"deal not kept: its evidence sentence is not in a story: {str(d.get('evidence'))[:80]!r}"]

    def held(label, v):
        v = " ".join(str(v or "").split())
        if v and norm(v) not in text:
            why.append(f"{label} {v!r}: not in the story's words")
            return ""
        return v

    buyer, seller = held("buyer", d.get("buyer")), held("seller", d.get("seller"))
    others = [p for p in (held("party", p) for p in d.get("other_parties") or []) if p and p not in (buyer, seller)]
    if not buyer and not seller and not others:
        return None, why + ["deal not kept: the story's words name no party"]
    numbers = {}
    for f in NUMBERS:
        got, reason = check_number(f, d, stories)
        if reason:
            why.append(reason)
        if got:
            numbers[f] = dict(value=got[0], story_id=got[1], sentence=got[2], text=got[3], qualifier=got[4])
    state, country, status, words_why = stated_words(d, text)
    why.extend(words_why)
    tech = [t for t in dict.fromkeys(d.get("technology") or []) if t in TECHNOLOGIES]
    kind = d.get("kind") if d.get("kind") in KINDS else "other"
    return dict(kind=kind, buyer=buyer, seller=seller, others=others, asset=held("asset", d.get("asset")), technology=tech,
                place=held("place", d.get("place")), state=state, country=country, status=status,
                datacenter=bool(d.get("datacenter")), numbers=numbers,
                price_unit=" ".join(str(d.get("price_unit") or "").split()) if "price_value" in numbers else "",
                evidence=dict(story_id=ev[0], sentence=ev[1])), why


def party_key(name):
    """A party's name for matching across stories: lower case, without a company's legal ending."""
    n = re.sub(r"[.,']", "", norm(name))
    n = re.sub(r"\b(inc|corp|corporation|llc|ltd|plc|co|company|group|holdings|lp|sa|ag|nv)\b", "", n)
    return " ".join(n.split())


def party_keys(d):
    return {k for k in (party_key(p) for p in [d["buyer"], d["seller"]] + d["others"]) if k}


def same_deal(a, b):
    """Two reports of one deal (the rule of fold): the same kind, within FOLD_DAYS, no figure both state that differs
    (MW, MWh, US dollars), and one of: the same named parties, two or more; a party in common and a figure in common; or,
    within NEAR_DAYS, a party in common, one report naming no other party, and the same technology stated by both."""
    if a["kind"] != b["kind"] or abs((pd.Timestamp(a["date"]) - pd.Timestamp(b["date"])).days) > FOLD_DAYS:
        return False
    both = [f for f in ("mw", "mwh", "dollars") if f in a["numbers"] and f in b["numbers"]]
    if any(not math.isclose(a["numbers"][f]["value"], b["numbers"][f]["value"]) for f in both):
        return False
    pa, pb = party_keys(a), party_keys(b)
    if (len(pa) >= 2 and pa == pb) or (pa & pb and both):
        return True
    # one report names both parties and the other only one of them, within NEAR_DAYS, with the same technology stated
    near = abs((pd.Timestamp(a["date"]) - pd.Timestamp(b["date"])).days) <= NEAR_DAYS
    return bool(near and pa & pb and (len(pa) == 1 or len(pb) == 1) and a["technology"] and set(a["technology"]) == set(b["technology"]))


def fold(deals):
    """Deals from different clusters that are one deal (same_deal), folded. The earliest is kept, with every story linked;
    returns (kept deals, [(folded id, kept id)])."""
    out, pairs = [], []
    for d in sorted(deals, key=lambda d: (d["date"], d["id"])):
        k = next((k for k in out if same_deal(k, d)), None)
        if k is None:
            out.append(d)
            continue
        for sid in d["story_ids"]:
            if sid not in k["story_ids"]:
                k["story_ids"].append(sid)
        for f, v in d["numbers"].items():          # a gap is filled, with the sentence it was read from; nothing is replaced
            k["numbers"].setdefault(f, v)
            if f == "price_value" and not k["price_unit"]:
                k["price_unit"] = d["price_unit"]
        for f in ("asset", "place", "state", "country", "status"):
            k[f] = k[f] or d[f]
        k["technology"] = list(dict.fromkeys(k["technology"] + d["technology"]))
        k["datacenter"] = k["datacenter"] or d["datacenter"]
        sided = {party_key(k["buyer"]), party_key(k["seller"])}
        k["others"] = [p for p in dict.fromkeys(k["others"] + [d["buyer"], d["seller"]] + d["others"]) if p and party_key(p) not in sided]
        k["others"] = list({party_key(p): p for p in reversed(k["others"])}.values())[::-1]
        k["evidences"] += d["evidences"]
        k["folded"] += [d["id"]] + d["folded"]
        pairs.append((d["id"], k["id"]))
    return out, pairs


def deal_id(first_story, n):
    return "pdeal:" + hashlib.sha1(f"{first_story}#{n}".encode()).hexdigest()[:16]


# ------------------------------------------------------------------ what is read, and in what order

def cluster_key(row):
    return row["cluster_id"] if row["cluster_id"] else "story:" + row["event_id"]


def plan(news, v2_read):
    """Every story with its cluster and tier (a cluster takes the first tier any of its stories has)."""
    n = news.copy()
    text = (n["title"] + " . " + n["summary"]).str.lower()
    scored = n["scored_at"] != ""
    words = text.str.contains(WORDS, regex=True)
    tier = pd.Series(5, index=n.index)
    tier[scored] = 4
    tier[~scored & words] = 3
    tier[scored & (n["sector"].isin(POWER_SECTORS) | words)] = 2
    tier[n["event_id"].isin(v2_read)] = 1
    n["cluster"] = [cluster_key(r) for r in n[["cluster_id", "event_id"]].to_dict("records")]
    n["tier"] = tier.groupby(n["cluster"]).transform("min")
    return n


def load_answers():
    if not os.path.exists(ANSWERS):
        return []
    with open(ANSWERS, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def read_news():
    return ip.read_series(os.path.join(ip.OUT_DIR, NEWS + ".csv"), NEWS_COLS)


def read_stories(answers):
    """story_id -> the call that read it last."""
    return {sid: a for a in answers for c in a["clusters"] if c["answered"] for sid in c["story_ids"]}


def items_of(batch):
    items = []
    for i, g in enumerate(batch):
        stories = []
        for r in g.itertuples():
            s = {"title": r.title}
            if not norm(r.summary).startswith(norm(r.title)):     # many summaries are the title and the outlet's name
                s["summary"] = r.summary
            stories.append(s)
        items.append({"c": i, "stories": stories})
    return items


def cmd_plan(args, log):
    news = read_news()
    v2 = set(pd.read_csv(CHECKED_V2, dtype=str, keep_default_na=False)["story_id"])
    p = plan(news, v2)
    done = set(read_stories(load_answers()))
    rows = []
    for t in sorted(TIER_WORDS):
        x = p[p["tier"] == t]
        rows.append(dict(tier=t, words=TIER_WORDS[t], stories=len(x), clusters=x["cluster"].nunique(),
                         read=int(x["event_id"].isin(done).sum()), remain=int((~x["event_id"].isin(done)).sum())))
        log(f"tier {t} ({TIER_WORDS[t]}): {len(x)} stories in {x['cluster'].nunique()} clusters; "
            f"{rows[-1]['read']} read, {rows[-1]['remain']} remain")
    log(f"all: {len(p)} stories; {int(p['event_id'].isin(done).sum())} read, {int((~p['event_id'].isin(done)).sum())} remain")
    return rows


def cmd_run(args, log):
    cap = float(args.cap_usd)
    key = ip.load_key("ANTHROPIC_API_KEY", log)
    if key is None:
        raise RuntimeError("ANTHROPIC_API_KEY is empty")
    news = read_news()
    v2 = set(pd.read_csv(CHECKED_V2, dtype=str, keep_default_na=False)["story_id"])
    p = plan(news, v2)
    done = set(read_stories(load_answers()))
    todo = p[~p["cluster"].isin(set(p[p["event_id"].isin(done)].groupby("cluster")["event_id"].count().index)
                               - set(p[~p["event_id"].isin(done)]["cluster"]))]
    batches = []
    for t in sorted(TIER_WORDS):
        if args.tiers and t not in args.tiers:
            continue
        cl = [g for _, g in todo[todo["tier"] == t].groupby("cluster", sort=False)]
        cl.sort(key=lambda g: g["event_date"].max(), reverse=True)        # newest first
        batches += [(t, cl[i:i + BATCH[t]]) for i in range(0, len(cl), BATCH[t])]
    batches = batches[:args.max_calls] if args.max_calls else batches
    log(f"{len(todo)} stories to read in {len(batches)} calls; cap USD {cap:.2f}; session {llm.session()} has spent "
        f"USD {llm.session_total():.4f}")
    if not batches:
        return
    client = llm.client(STEP, log, api_key=key)
    model = pick_model(client, log)
    if llm.price_of(model) is None:
        raise RuntimeError(f"model {model} has no price in warehouse/config/model_prices.yaml: the cap could not be kept")
    inner = client._client                      # the calls are recorded by llm.record below, one at a time
    lock = threading.Lock()
    state = dict(spent=llm.session_total(), flying=0, stopped=False, calls=0, failed=0)

    def one(job):
        k, (tier, batch) = job
        with lock:
            if state["stopped"] or state["spent"] + (state["flying"] + 1) * PER_CALL_RESERVE >= cap:
                if not state["stopped"]:
                    log(f"STOP at the cap: spent USD {state['spent']:.4f} with {state['flying']} calls in flight; cap USD {cap:.2f}")
                state["stopped"] = True
                return
            state["flying"] += 1
        answer, err, usage, rid = None, "", None, ""
        try:
            resp = inner.messages.create(
                model=model, max_tokens=16000,
                system=[{"type": "text", "text": SYSTEM, "cache_control": {"type": "ephemeral"}}],
                output_config={"effort": "low", "format": {"type": "json_schema", "schema": SCHEMA}},
                messages=[{"role": "user", "content": "Clusters (JSON):\n" + json.dumps(items_of(batch), ensure_ascii=False)}])
            usage, rid = resp.usage, getattr(resp, "_request_id", "") or ""
            if resp.stop_reason != "end_turn":
                raise RuntimeError(f"stop_reason {resp.stop_reason}")
            answer = json.loads("".join(b.text for b in resp.content if b.type == "text"))
        except Exception as exc:
            err = ip.redact(repr(exc))[:300]
        with lock:
            state["flying"] -= 1
            state["calls"] += 1
            cost = 0.0
            if usage is not None:
                row = llm.record(STEP, model, usage, rid, None)
                cost = float(row["usd"] or 0)
                state["spent"] += cost
            if answer is None:
                state["failed"] += 1
                log(f"  call {k} (tier {tier}) FAILED, {len(batch)} clusters stay unread: {err}")
                return
            said = {int(d["c"]) for d in answer["deals"]} | {int(c) for c in answer["none"]}
            line = dict(call=k, tier=tier, model=model, at=ip.utc_iso(pd.Timestamp.now(tz="UTC")), request_id=rid, usd=round(cost, 6),
                        clusters=[dict(c=i, cluster=g["cluster"].iloc[0], story_ids=list(g["event_id"]), answered=i in said)
                                  for i, g in enumerate(batch)],
                        answer=answer)
            with open(ANSWERS, "a", encoding="utf-8", newline="\n") as f:
                f.write(json.dumps(line, ensure_ascii=False) + "\n")
            missing = len(batch) - sum(1 for i in range(len(batch)) if i in said)
            log(f"  call {k} tier {tier}: {len(batch)} clusters, {len(answer['deals'])} deals"
                f"{f', {missing} clusters not answered (they stay unread)' if missing else ''}; USD {cost:.4f}, "
                f"session total {state['spent']:.4f}; request {rid}")

    jobs = list(enumerate(batches, 1))
    one(jobs[0])                                # alone, so the calls after it read the cached instructions
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        list(pool.map(one, jobs[1:]))
    log(f"run over: {state['calls']} calls ({state['failed']} failed), session {llm.session()} total USD {llm.session_total():.4f}"
        f"{'; stopped at the cap' if state['stopped'] else ''}")


def cmd_confirm(args, log):
    cap = float(args.cap_usd)
    key = ip.load_key("ANTHROPIC_API_KEY", log)
    if key is None:
        raise RuntimeError("ANTHROPIC_API_KEY is empty")
    news = read_news()
    by_id = {r["event_id"]: r for r in news.to_dict("records")}
    deals, _, _ = first_read(news, load_answers())
    second = load_second()
    todo = [d for d in deals if args.again or d["id"] not in second]
    batches = [todo[i:i + BATCH2] for i in range(0, len(todo), BATCH2)]
    batches = batches[:args.max_calls] if args.max_calls else batches
    log(f"second read: {len(deals)} deals from the first read, {len(todo)} not yet read twice, {len(batches)} calls; cap USD {cap:.2f}; "
        f"session {llm.session()} has spent USD {llm.session_total():.4f}")
    if not batches:
        return
    client = llm.client(STEP + "_second", log, api_key=key)
    model = pick_model(client, log)
    if llm.price_of(model) is None:
        raise RuntimeError(f"model {model} has no price in warehouse/config/model_prices.yaml: the cap could not be kept")
    for k, batch in enumerate(batches, 1):
        if llm.session_total() + PER_CALL_RESERVE >= cap:
            log(f"STOP at the cap: session total USD {llm.session_total():.4f}; {sum(len(b) for b in batches[k - 1:])} deals not read twice")
            break
        items = []
        for i, d in enumerate(batch):
            stories = []
            for sid in d["story_ids"]:
                r = by_id[sid]
                st = {"title": r["title"]}
                if not norm(r["summary"]).startswith(norm(r["title"])):
                    st["summary"] = r["summary"]
                stories.append(st)
            items.append({"i": i, "stories": stories,
                          "deal": {"kind": d["kind"], "buyer": d["buyer"], "seller": d["seller"], "other_parties": d["others"], "asset": d["asset"]},
                          "figures": {f: {"value": clean(v["value"]), "sentence": v["sentence"]} for f, v in d["numbers"].items()}})
        try:
            resp = client.messages.create(
                model=model, max_tokens=16000,
                system=[{"type": "text", "text": SYSTEM2, "cache_control": {"type": "ephemeral"}}],
                output_config={"effort": "medium", "format": {"type": "json_schema", "schema": SCHEMA2}},
                messages=[{"role": "user", "content": "Items (JSON):\n" + json.dumps(items, ensure_ascii=False)}])
            if resp.stop_reason != "end_turn":
                raise RuntimeError(f"stop_reason {resp.stop_reason}")
            got = {int(c["i"]): c for c in json.loads("".join(b.text for b in resp.content if b.type == "text"))["checks"]}
        except llm.SpendCapReached as exc:
            log(f"STOP at the cap: {exc}")
            break
        except Exception as exc:
            log(f"  second read call {k} FAILED, {len(batch)} deals stay unread: {ip.redact(repr(exc))[:300]}")
            continue
        checks = [dict(deal_id=d["id"], verdict=got[i]["verdict"], kind=got[i]["kind"], first_kind=d["kind"], roles=got[i]["roles"],
                       datacenter=got[i]["datacenter"], first_datacenter=d["datacenter"],
                       not_the_deals=[f for f in got[i]["not_the_deals"] if f in d["numbers"]], not_parties=got[i]["not_parties"])
                  for i, d in enumerate(batch) if i in got]
        with open(SECOND, "a", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(dict(call=k, model=model, at=ip.utc_iso(pd.Timestamp.now(tz="UTC")), request_id=getattr(resp, "_request_id", "") or "",
                                    checks=checks), ensure_ascii=False) + "\n")
        n = {v: sum(1 for c in checks if c["verdict"] == v) for v in VERDICTS}
        log(f"  second read call {k}: {len(batch)} deals, {n}; session total USD {llm.session_total():.4f}")
    log(f"second read over: session {llm.session()} total USD {llm.session_total():.4f}")


# ------------------------------------------------------------------ the tables, from the answers

def load_second():
    """deal id -> the second read's answer for it (the last one wins)."""
    if not os.path.exists(SECOND):
        return {}
    out = {}
    with open(SECOND, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                a = json.loads(line)
                for c in a["checks"]:
                    out[c["deal_id"]] = dict(c, model=a["model"], at=a["at"])
    return out


def confirmed(deals, second):
    """(the deals the second read calls a power deal, with its kind; counts of the others). A deal not yet read a second
    time is not kept, and is counted."""
    kept, counts = [], dict(second_power_deal=0, second_not_power=0, second_not_a_transaction=0, second_not_read=0, kind_changed=0,
                            roles_not_stated=0, datacenter_changed=0, numbers_not_the_deals=0, names_not_parties=0, no_party_left=0)
    for d in deals:
        c = second.get(d["id"])
        if c is None:
            counts["second_not_read"] += 1
            continue
        counts["second_" + c["verdict"]] += 1
        if c["verdict"] != "power_deal":
            continue
        if c["kind"] != d["kind"]:
            counts["kind_changed"] += 1
        d = dict(d, first_kind=d["kind"], kind=c["kind"], numbers=dict(d["numbers"]), others=list(d["others"]))
        for f in c.get("not_the_deals") or []:      # a figure the story states, but not this deal's own: left blank
            if d["numbers"].pop(f, None) is not None:
                counts["numbers_not_the_deals"] += 1
                if f == "price_value":
                    d["price_unit"] = ""
        gone = {party_key(p) for p in c.get("not_parties") or []} - {""}
        if gone:
            before = [d["buyer"], d["seller"]] + d["others"]
            d["buyer"] = "" if party_key(d["buyer"]) in gone else d["buyer"]
            d["seller"] = "" if party_key(d["seller"]) in gone else d["seller"]
            d["others"] = [p for p in d["others"] if party_key(p) not in gone]
            counts["names_not_parties"] += sum(1 for p in before if p) - sum(1 for p in [d["buyer"], d["seller"]] + d["others"] if p)
            if not d["buyer"] and not d["seller"] and not d["others"]:
                counts["no_party_left"] += 1
                continue
        if c.get("roles") == "not_stated" and (d["buyer"] or d["seller"]):
            # the story does not say who buys and who sells: the names are kept, as parties, with no side
            counts["roles_not_stated"] += 1
            d.update(buyer="", seller="", others=[p for p in [d["buyer"], d["seller"]] + d["others"] if p])
        if "datacenter" in c and bool(c["datacenter"]) != d["datacenter"]:
            counts["datacenter_changed"] += 1
            d["datacenter"] = bool(c["datacenter"])
        kept.append(d)
    return kept, counts


def first_read(news, answers):
    """(every deal of the first read that passes the checks, reasons not kept, counts); the last answer for a cluster wins."""
    by_id = {r["event_id"]: r for r in news.to_dict("records")}
    latest = {}
    for a in answers:
        for c in a["clusters"]:
            if c["answered"]:
                latest[c["cluster"]] = (a, c)
    deals, dropped, counts = [], [], dict(model_deals=0, deals_not_kept=0, numbers_given=0, numbers_kept=0)
    for cluster, (a, c) in latest.items():
        stories = sorted((by_id[s] for s in c["story_ids"] if s in by_id), key=lambda s: (s["event_date"], s["event_id"]))
        if not stories:
            continue
        n = 0
        for d in a["answer"]["deals"]:
            if int(d["c"]) != c["c"]:
                continue
            counts["model_deals"] += 1
            counts["numbers_given"] += sum(1 for f in NUMBERS if str(d.get(f) or "").strip())
            deal, why = read_deal(d, stories)
            dropped += [f"{cluster}: {w}" for w in why]
            if deal is None:
                counts["deals_not_kept"] += 1
                continue
            counts["numbers_kept"] += len(deal["numbers"])
            first = stories[0]
            deal.update(id=deal_id(first["event_id"], n), date=first["event_date"], story_ids=[s["event_id"] for s in stories],
                        model=a["model"], at=a["at"], folded=[], evidences=[deal.pop("evidence")])
            deals.append(deal)
            n += 1
    return deals, dropped, counts


def assemble(news, answers, v2_read, second, log=lambda m: None):
    """(deals after the second read and the fold, pairs folded, reasons not kept, counts) from every answer held."""
    deals, dropped, counts = first_read(news, answers)
    deals, c2 = confirmed(deals, second)
    counts.update(c2)
    kept, pairs = fold(deals)
    for d in kept:
        d["read_by_v2"] = any(s in v2_read for s in d["story_ids"])
    for w in dropped:
        log(f"  not kept: {w}")
    for a, b in pairs:
        log(f"  folded: {a} into {b}")
    return kept, pairs, dropped, counts


def tables(kept, news):
    by_id = {r["event_id"]: r for r in news.to_dict("records")}
    drows, erows = [], []
    for d in kept:
        first = by_id[d["story_ids"][0]]
        num = {f: d["numbers"][f]["value"] if f in d["numbers"] else None for f in NUMBERS}
        unit = d["price_unit"]
        usd_mwh = num["price_value"] is not None and re.fullmatch(r"(?i)(usd|\$|us\$)\s*/\s*mwh", unit)
        drows.append({
            "event_id": d["id"], "event_date": d["date"], "event_type": "power_deal",
            "parties": ";".join(clean(p) for p in [d["buyer"], d["seller"]] + d["others"] if p), "entity_ids": "",
            "mw": clean(num["mw"]), "price": clean(num["price_value"]) if usd_mwh else "", "currency": "USD" if usd_mwh else "",
            "status": d["status"], "source": first["source"], "source_url": first["source_url"],
            "kind": d["kind"], "buyer": clean(d["buyer"]), "seller": clean(d["seller"]),
            "other_parties": ";".join(clean(p) for p in d["others"]), "asset": clean(d["asset"]),
            "technology": ";".join(d["technology"]), "storage": "true" if "storage" in d["technology"] else "false",
            "datacenter": "true" if d["datacenter"] else "false", "place": clean(d["place"]), "state": d["state"],
            "country": d["country"], "mwh": clean(num["mwh"]), "dollars": clean(num["dollars"]),
            "price_value": clean(num["price_value"]), "price_unit": unit, "term_years": clean(num["term_years"]),
            "qualifiers": ";".join(f"{f}={d['numbers'][f]['qualifier']}" for f in NUMBERS if f in d["numbers"] and d["numbers"][f]["qualifier"]),
            "number_stories": ";".join(f"{f}={d['numbers'][f]['story_id']}" for f in NUMBERS if f in d["numbers"]),
            "date_basis": "first_story_published", "read_by_v2": "true" if d["read_by_v2"] else "false",
            "n_stories": str(len(d["story_ids"])), "story_ids": ";".join(d["story_ids"]),
            "story_urls": ";".join(by_id[s]["source_url"] for s in d["story_ids"]), "folded_ids": ";".join(d["folded"]),
            "model_id": d["model"], "extracted_at": d["at"]})

        def ev(field, story_id, value, text, sentence):
            s = by_id[story_id]
            return {"event_id": f"{d['id']}|{field}|{story_id}", "event_date": s["event_date"], "event_type": "power_deal_sentence",
                    "parties": "", "entity_ids": "", "mw": "", "price": "", "currency": "", "status": "",
                    "source": s["source"], "source_url": s["source_url"], "deal_id": d["id"], "story_id": story_id,
                    "field": field, "value": clean(value), "text": text, "sentence": sentence}
        for e in {e["story_id"]: e for e in d["evidences"]}.values():
            erows.append(ev("deal", e["story_id"], None, "", e["sentence"]))
        for f in NUMBERS:
            if f in d["numbers"]:
                x = d["numbers"][f]
                erows.append(ev(f, x["story_id"], x["value"], x["text"], x["sentence"]))
    return (pd.DataFrame(drows, columns=DEAL_COLS).fillna("").sort_values(["event_date", "event_id"]),
            pd.DataFrame(erows, columns=EVIDENCE_COLS).fillna("").sort_values(["event_date", "event_id"]))


def no_number_without_its_sentence(deals, evidence, news):
    """The rule, checked on the tables as written: raises on the first number that has no sentence in a story held."""
    by_id = {r["event_id"]: r for r in news.to_dict("records")}
    ev = {(r["deal_id"], r["field"]): r for r in evidence.to_dict("records")}
    n = 0
    for r in deals.to_dict("records"):
        for f in NUMBERS:
            if r[f] == "":
                continue
            e = ev.get((r["event_id"], f))
            if e is None or not e["sentence"]:
                raise RuntimeError(f"{r['event_id']}: {f} {r[f]} has no sentence")
            s = by_id[e["story_id"]]
            if norm(e["sentence"]) not in norm(s["title"]) and norm(e["sentence"]) not in norm(s["summary"]):
                raise RuntimeError(f"{r['event_id']}: the sentence of {f} is not in story {e['story_id']}")
            if float(e["value"]) != float(r[f]):
                raise RuntimeError(f"{r['event_id']}: {f} {r[f]} is not the value its sentence row holds ({e['value']})")
            n += 1
    return n


def stated(df, version):
    """How many deals of a table state a size, a price, a term: the comparison's one row."""
    has = lambda c: (df[c] != "") if c in df else pd.Series(False, index=df.index)   # noqa: E731
    size = has("mw") | has("mwh")
    return dict(version=version, deals=int(len(df)), size=int(size.sum()), mw=int(has("mw").sum()), mwh=int(has("mwh").sum()),
                price=int(has("price_value").sum()), price_usd_mwh=int(has("price").sum()), term=int(has("term_years").sum()),
                dollars=int(has("dollars").sum()), any_number=int((size | has("price_value") | has("term_years") | has("dollars")).sum()))


def v2_subsets(v2):
    """Version 2's table with the two subsets as its page defines them (site/lib/deals2.ts)."""
    storage = v2["technology"].str.contains(r"batter|storage|\bbess\b", case=False, regex=True) \
        | v2["asset"].str.contains(r"batter|energy storage|\bbess\b", case=False, regex=True)
    return storage, v2["ai_power"].str.lower() == "true"


def compare(deals, v2):
    st, ai = v2_subsets(v2)
    return dict(
        all=[stated(v2, "2"), stated(deals[deals["read_by_v2"] == "true"], "3, the stories version 2 read"), stated(deals, "3, every story read")],
        storage=[stated(v2[st], "2"), stated(deals[(deals["storage"] == "true") & (deals["read_by_v2"] == "true")], "3, the stories version 2 read"),
                 stated(deals[deals["storage"] == "true"], "3, every story read")],
        datacenter=[stated(v2[ai], "2"), stated(deals[(deals["datacenter"] == "true") & (deals["read_by_v2"] == "true")], "3, the stories version 2 read"),
                    stated(deals[deals["datacenter"] == "true"], "3, every story read")])


def cmd_build(args, log):
    news = read_news()
    v2_read = set(pd.read_csv(CHECKED_V2, dtype=str, keep_default_na=False)["story_id"])
    answers = load_answers()
    if not answers:
        raise RuntimeError("no model answer is held (warehouse/deals/answers_v3.jsonl): nothing to build")
    kept, pairs, dropped, counts = assemble(news, answers, v2_read, load_second(), log)
    deals, evidence = tables(kept, news)
    n_checked = no_number_without_its_sentence(deals, evidence, news)
    run_id = args.run_id
    common = [f"Retrieved: {run_id} (UTC) by warehouse/deals/extract_v3.py from warehouse/output/{NEWS}.csv (titles and "
              "summaries; the ERW holds no article body)",
              f"Run log: warehouse/output/logs/{STEP}_{run_id}.log"]
    models = sorted({d["model"] for d in kept})
    ip.write_snapshot(deals, DEALS, [
        "Energy Research Warehouse (ERW): Power deals read from the news, version 3 of the deals tracker (platform tool 6)",
        "Shape: events (docs/datastandard.md v0), event_type power_deal. event_date is the first story's publish time "
        "(date_basis first_story_published).",
        *common,
        f"Model: {', '.join(models)}, JSON schema output. No number without its sentence: mw, mwh, price_value, term_years and "
        "dollars are kept only when the sentence is in the story, the words are in the sentence, and the words state that "
        f"number with its unit; the sentence of every number is in {EVIDENCE} (field, story_id). A deal that states none "
        "keeps blanks. kind, technology and datacenter are the model's reading.",
        "Columns: mw in MW, mwh in MWh, dollars in US dollars, term_years in years, as stated; price and currency only for a "
        "price stated in USD/MWh, otherwise price_value with price_unit as stated. qualifiers holds the word before a number "
        "that limits it (mw=up to). number_stories names the story each number was read from. storage is true when "
        "technology names storage. read_by_v2 is true when version 2 read one of the deal's stories.",
        "License: public. Structured fields and story links only, no outlet text.",
        "Sources: the outlet named in each row's source column (the first story); story_urls lists every story.",
        "Method: docs/methods/power_deals.md",
    ], log, DEAL_COLS)
    ip.write_snapshot(evidence, EVIDENCE, [
        "Energy Research Warehouse (ERW): The sentences power_deals was read from, copied from the stories",
        "Shape: events (docs/datastandard.md v0), event_type power_deal_sentence; one row per deal, field and story. field is "
        "deal (the sentence that shows the transaction) or a number's column (mw, mwh, price_value, term_years, dollars), with "
        "value, the words (text) and the whole sentence. event_date is the story's publish time.",
        *common,
        "License: internal. Outlet text (a title, or a sentence of a summary); never shown publicly.",
        "Sources: the outlet named in each row's source column; source_url links the story.",
        "Method: docs/methods/power_deals.md",
    ], log, EVIDENCE_COLS)
    # every story read, with its tier
    p = plan(news, v2_read).set_index("event_id")
    read = read_stories(answers)
    n_deals = {}
    for d in kept:
        for s in d["story_ids"]:
            n_deals[s] = n_deals.get(s, 0) + 1
    chk = pd.DataFrame([dict(story_id=s, cluster=p.loc[s, "cluster"], tier=str(p.loc[s, "tier"]), checked_at=a["at"],
                             model_id=a["model"], n_deals=str(n_deals.get(s, 0))) for s, a in sorted(read.items()) if s in p.index],
                       columns=CHECKED_COLS)
    chk.to_csv(CHECKED, index=False, lineterminator="\n")
    reg = pd.read_csv(os.path.join(ip.METADATA_DIR, "sources.csv"), dtype=str, keep_default_na=False)
    srcs = set(deals["source"]) | set(evidence["source"])
    entries = [dict(r, tables=[t for t in r["tables"].split(";") if t] + [DEALS, EVIDENCE])
               for r in reg[reg["source"].isin(srcs)].to_dict("records")]
    if entries:
        ip.update_sources(entries)
    # the comparison with version 2, and the page's copy (public fields only)
    v2 = ip.read_series(os.path.join(ip.OUT_DIR, V2 + ".csv"), V2_COLS)
    tiers = []
    for t in sorted(TIER_WORDS):
        x = p[p["tier"] == t]
        tiers.append(dict(tier=t, words=TIER_WORDS[t], stories=int(len(x)), read=int(x.index.isin(list(read)).sum()),
                          remain=int((~x.index.isin(list(read))).sum())))
    ledger = llm.read_ledger()
    ledger = ledger[ledger["step"].isin([STEP, STEP + "_second"])]
    summary = dict(
        built_at=run_id, models=models, stories_held=int(len(news)), stories_read=int(sum(t["read"] for t in tiers)),
        stories_remaining=int(sum(t["remain"] for t in tiers)), tiers=tiers,
        calls=int(len(ledger)), usd=round(float(pd.to_numeric(ledger["usd"], errors="coerce").fillna(0).sum()), 4),
        model_deals=counts["model_deals"], deals_not_kept=counts["deals_not_kept"], folded=len(pairs), deals=int(len(deals)),
        second_read={k[len("second_"):]: v for k, v in counts.items() if k.startswith("second_")}, kind_changed=counts["kind_changed"],
        roles_not_stated=counts["roles_not_stated"], datacenter_changed=counts["datacenter_changed"],
        numbers_not_the_deals=counts["numbers_not_the_deals"], names_not_parties=counts["names_not_parties"], no_party_left=counts["no_party_left"],
        numbers_given=counts["numbers_given"], numbers_kept=counts["numbers_kept"], numbers_checked=n_checked,
        fields_not_kept=len(dropped), kinds=deals["kind"].value_counts().to_dict(),
        technologies={t: int(deals["technology"].str.split(";").apply(lambda v: t in v).sum()) for t in TECHNOLOGIES},
        v2_table=dict(rows=int(len(v2)), first=v2["event_date"].min()[:10], last=v2["event_date"].max()[:10]),
        compare=compare(deals, v2))
    public = [c for c in DEAL_COLS if c not in ("entity_ids", "model_id", "extracted_at")]
    os.makedirs(os.path.dirname(SITE_COPY), exist_ok=True)
    with open(SITE_COPY, "w", encoding="utf-8", newline="\n") as f:
        json.dump(dict(summary=summary, deals=deals[public].sort_values(["event_date", "event_id"], ascending=False).to_dict("records")),
                  f, ensure_ascii=False, indent=0)
        f.write("\n")
    log(f"second read: {summary['second_read']}; kind changed for {counts['kind_changed']}, sides not stated for {counts['roles_not_stated']}, "
        f"datacenter flag changed for {counts['datacenter_changed']}; figures not the deal's own {counts['numbers_not_the_deals']}, names not "
        f"parties {counts['names_not_parties']} ({counts['no_party_left']} deals left with no party, not kept)")
    log(f"built: {len(deals)} deals ({counts['model_deals']} from the model, {counts['deals_not_kept']} not kept, {len(pairs)} folded); "
        f"numbers {counts['numbers_kept']} kept of {counts['numbers_given']} given; {len(evidence)} sentence rows; "
        f"{summary['stories_read']} stories read, {summary['stories_remaining']} remain; USD {summary['usd']}")
    for k, rows in summary["compare"].items():
        for r in rows:
            log(f"  {k:10s} version {r['version']}: {r['deals']} deals; size {r['size']} (MW {r['mw']}, MWh {r['mwh']}); "
                f"price {r['price']}; term {r['term']}; dollars {r['dollars']}")


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW power deals, version 3")
    ap.add_argument("command", choices=["plan", "run", "confirm", "build"])
    ap.add_argument("--cap-usd", default=os.environ.get("ERW_SPEND_CAP_USD", ""), help="stop before the session's spend reaches this")
    ap.add_argument("--max-calls", type=int, default=0)
    ap.add_argument("--again", action="store_true", help="confirm: read every deal a second time again, not only the new ones")
    ap.add_argument("--tiers", type=lambda s: [int(x) for x in s.split(",")], default=None)
    args = ap.parse_args(argv)
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    args.run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{STEP}_{args.run_id}.log"))
    status = dict(table=DEALS, market=args.command, status="ok", detail="")
    try:
        if args.command in ("run", "confirm") and not args.cap_usd:
            raise RuntimeError(f"{args.command} needs a cap: --cap-usd, or ERW_SPEND_CAP_USD")
        {"plan": cmd_plan, "run": cmd_run, "confirm": cmd_confirm, "build": cmd_build}[args.command](args, log)
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED:\n{tb}")
        print(f"power deals {args.command} FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        status.update(status="failed", detail=tb.strip().splitlines()[-1][:300])
        if args.command != "plan":
            ip.write_status("power_deals", args.run_id, [status])
        log.close()
        return 1
    if args.command != "plan":
        ip.write_status("power_deals", args.run_id, [status])
    log.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
