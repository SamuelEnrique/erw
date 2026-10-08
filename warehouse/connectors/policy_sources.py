#!/usr/bin/env python3
"""Policy sources (platform tool 12): the Federal Register and agency news, as one events table, policy_actions.

Energy Research Warehouse (ERW) connector, session 24. All sources are free and public; every response is stored
raw under warehouse/raw/policy_sources/<run_id>/ (manifest.csv names each URL and time).

    python warehouse/connectors/policy_sources.py                       # from 2025-10-01 to today
    python warehouse/connectors/policy_sources.py --since 2026-09-01

Sources:
  federalregister   The Federal Register API (federalregister.gov/api/v1, no key): rules, proposed rules and notices of
                    DOE (with FERC, which the Register files under it), FERC, EPA, NRC, BLM and Interior, published
                    since --since. DOE, FERC and NRC documents are all energy; EPA, BLM and Interior documents are kept
                    only when their title, abstract or Federal Register topics name an energy subject (ENERGY below).
                    Routine paperwork (information collections, meeting and Sunshine Act notices, Privacy Act systems,
                    FERC's combined notices of filings) is left out (ROUTINE below).
  nrc               NRC news releases (www.nrc.gov RSS, the feed's window only).
  doe               DOE newsroom (www.energy.gov RSS, the feed's window only).
  puct              Public Utility Commission of Texas news page (puc.texas.gov, every dated item on the page).
  cpuc              California Public Utilities Commission news (cpuc.ca.gov/news-and-updates/all-news, pages until
                    --since), the items whose title names an energy subject (the CPUC also regulates rail, water and
                    telecommunications).
  Session 157: each Federal Register document's printed text (its raw_text_url, plain text as the Register serves
  it) is read ONCE and kept by document number under warehouse/raw/policy_sources/fr_text/, so it is never asked
  twice; a run asks only for documents it does not hold (in that store, or already read in the table held: the
  runner has no raw store, the table carries what was read). From it come first_paragraph, the full title where the
  Register's record cuts it short, and the place (PLACE RULE below). One request every two seconds (--text-pause),
  a ceiling a run (--max-texts, --max-text-bytes) it stops before, and the Register's own limit honoured: on an
  HTTP 429 the run waits, slows, asks once more, and at a second 429 asks for no more texts (read_texts).
  Treasury and the IRS joined the listing in session 157.
  FERC's own news and eLibrary pages answer a Cloudflare JavaScript challenge (checked 2026-09-28), so FERC's actions
  come from the Federal Register and FERC news items reach the ERW through news_stories (the Google News feed).

The table (events shape, docs/datastandard.md; public: every source is a US or state government publication):
  event_id     federalregister:<document number>, or <source>:<sha1 of the link, 12 hex>
  event_date   the publication date (Register) or the release date (news), YYYY-MM-DD
  event_type   filing (a Register document) or announcement (a news release)
  parties      the agencies, as named
  status       the Register's action line ("Final rule.", "Notice of availability.") or "news release"
  source, source_url
  then: agency (the short name: DOE, FERC, EPA, NRC, BLM, Interior, PUCT, CPUC), action_type (rule, proposed_rule,
  notice, press_release), title, abstract (the Register's own summary; blank for news), docket (docket ids and RINs,
  ";"-separated), rin, fr_document_number, sector_tags (keyword rules, SECTOR_TAGS), states (US states named in the
  title or abstract, or the commission's state), related_urls (a news release that reports a Register document is
  folded into it: its link is here and it gets no row of its own), news_story_ids and news_story_urls (the scored news
  stories that report the same action: a docket, RIN or document number in the story, or a title of the same content
  words within 21 days), then (session 157) first_paragraph (the first paragraph of the printed text, at most 1,500
  characters; its SUMMARY where it has one), place_words (only where the title, the abstract and the first paragraph
  name no state: the first sentence of the printed text that places something in a county, parish or borough of a
  state, which the place is then read from), title_register (the Register's record title, only where the printed
  title goes on and was taken), text_status ("read", "not reachable: <why>", or blank: not asked yet or no printed
  text) and text_read_at, and the scores warehouse/policy/score.py writes (significance, sector, why, model_id,
  scored_at; blank until scored) with model_recheck ("rechecked", "not rechecked", "source not reachable", or
  "scored on the source text" for an action first scored after session 157) and model_rechecked_at.
"""

import argparse
import datetime as dt
import hashlib
import html as H
import json
import os
import re
import sys
import traceback
import xml.etree.ElementTree as ET

import pandas as pd
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "policy_actions"
ROOT = ip.ROOT
SCORES = os.path.join(ROOT, "warehouse", "policy", "scores.csv")
FR = "https://www.federalregister.gov/api/v1/documents.json"
UA = {"User-Agent": "Mozilla/5.0 (ERW energy research warehouse; https://github.com/SamuelEnrique/erw)"}
AGENCIES = {"energy-department": "DOE", "federal-energy-regulatory-commission": "FERC",
            "environmental-protection-agency": "EPA", "nuclear-regulatory-commission": "NRC",
            "land-management-bureau": "BLM", "interior-department": "Interior",
            # session 157: the tax credits. The IRS is a bureau of the Treasury: its documents carry both names.
            "treasury-department": "Treasury", "internal-revenue-service": "IRS"}
ALWAYS_ENERGY = {"DOE", "FERC", "NRC"}
TYPES = {"Rule": "rule", "Proposed Rule": "proposed_rule", "Notice": "notice"}
ENERGY = re.compile(r"\b(energy|electric\w*|power plant|power sector|utilit(y|ies)|oil|natural gas|gas|coal|pipeline|"
                    r"methane|petroleum|crude|refiner\w*|nuclear|uranium|renewable|solar|wind|geothermal|hydro\w*|"
                    r"transmission|offshore|lease sale|leasing|fuel|emission guidelines|greenhouse gas|carbon capture|"
                    r"battery|batteries|lithium|critical mineral\w*|LNG|biofuel|ethanol|hydrogen|mining claim)\b", re.I)
ROUTINE = re.compile(r"(Combined Notice of Filings|Information Collection|Paperwork Reduction|Sunshine Act|"
                     r"Privacy Act of 1974|Meeting\b|Advisory (Committee|Board)|Environmental Impact Statements; Notice of "
                     r"Availability|Notice of Filing\b|Notice of Institution of Section 206|Records Governing Off-the-Record|"
                     r"Self-Certification|Change in Status|Market-Based Rate|Filing of Revised Rate|Supplemental Notice)",
                     re.I)
SECTOR_TAGS = [  # (tag, pattern) on title + abstract + Register topics
    ("power", r"\b(electric\w*|power plant|power sector|generat\w+|grid|reliability|capacity market|RTO|ISO)\b"),
    ("transmission", r"\b(transmission|interconnection|transmission line)\b"),
    ("gas", r"\b(natural gas|gas pipeline|interstate pipeline|LNG|liquefied natural gas|methane)\b"),
    ("oil", r"\b(oil|petroleum|crude|refiner\w*|gasoline|diesel)\b"),
    ("nuclear", r"\b(nuclear|reactor|uranium|spent fuel|radioactive)\b"),
    ("renewables", r"\b(renewable|solar|wind|geothermal|hydroelectric|hydropower|biofuel)\b"),
    ("storage", r"\b(storage|batter(y|ies))\b"),
    ("coal", r"\b(coal)\b"),
    ("efficiency", r"\b(energy conservation|efficiency standard\w*|appliance)\b"),
    ("emissions", r"\b(emission\w*|greenhouse gas|carbon|air quality)\b"),
    ("datacenters", r"\b(data ?cent(er|re)s?|large load\w*)\b"),
    ("leasing", r"\b(lease\w*|leasing|right-of-way|public lands)\b"),
    # session 157 (the audit's draw 48): "hydrogen chloride" in an air rule is not the hydrogen sector
    ("hydrogen", r"\b(hydrogen)\b(?!\s+(?:chloride|sulfide|fluoride|cyanide|peroxide|bromide))"),
    ("minerals", r"\b(critical mineral\w*|lithium|mining)\b"),
]
STATES = {"Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA", "Colorado": "CO",
          "Connecticut": "CT", "Delaware": "DE", "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID",
          "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA",
          "Maine": "ME", "Maryland": "MD", "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN",
          "Mississippi": "MS", "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV",
          "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY", "North Carolina": "NC",
          "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA",
          "Rhode Island": "RI", "South Carolina": "SC", "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX",
          "Utah": "UT", "Vermont": "VT", "Virginia": "VA", "Washington": "WA", "West Virginia": "WV",
          "Wisconsin": "WI", "Wyoming": "WY"}
SCORE_COLS = ["significance", "sector", "why", "model_id", "scored_at", "model_recheck", "model_rechecked_at"]
TEXT_COLS = ["first_paragraph", "place_words", "title_register", "text_status", "text_read_at"]  # session 157: from the printed text
COLS = ["event_id", "event_date", "event_type", "parties", "entity_ids", "mw", "price", "currency", "status", "source",
        "source_url", "agency", "action_type", "title", "abstract", "docket", "rin", "fr_document_number",
        "sector_tags", "states", "related_urls", "news_story_ids", "news_story_urls"] + TEXT_COLS + SCORE_COLS + ["retrieved_at"]
COLS_S154 = [c for c in COLS if c not in TEXT_COLS + ["model_recheck", "model_rechecked_at"]]  # the table before session 157
STOP = set("the and for of to in on a an by with from at as is are be or its that this under final notice rule "
           "proposed commission department agency federal u.s. us announces approves".split())


# Session 154 (the audit of 50 rows against their source documents, runs/session154/agent_report_audit.md): five
# rules below were wrong for a class of documents. Each is tested on the real documents in tests/fixtures/session154/.
INLINE = re.compile(r"</?(?:INF|SUB|SUP|E|I|B|EM|STRONG|SMALL)\b[^>]*>", re.I)  # the Register's inline markup
NOT_A_STATE = re.compile(r"\bWashington,? D\.? ?C\b\.?|\bDistrict of Columbia\b")
GAS_DOCKET = re.compile(r"\b(?:CP|PF)\d{2}-\d+")  # FERC: a natural gas certificate docket, or its pre-filing
HYDRO_DOCKET = re.compile(r"\bProject Nos?\. ?\d|\bDI\d{2}-\d+")  # FERC: a hydropower project, or a declaration of intention
NRC_STORAGE = re.compile(r"\b(batter(y|ies)|energy storage)\b", re.I)
EASTERN = "America/New_York"  # NRC and DOE date a release by the day in Washington, not by the UTC day of the feed


def clean(s):
    # NO<INF>X</INF> is "NOX": inline markup goes without a space (it left "NO X " in 2026-13027's abstract)
    s = H.unescape(re.sub(r"<[^>]+>", " ", INLINE.sub("", s or "")))
    s = s.replace(chr(0x2014), ", ").replace(chr(0x2013), "-")
    return re.sub(r"\s+", " ", s).strip()


def tags(text, agency="", docket=""):
    """The sector tags: the keyword rules on the text, and (session 154) what the agency and the docket say where the
    text cannot. A FERC notice has no abstract in the Register's API, so its tags rested on a title that is often only
    the applicant's name: a CP docket is a natural gas certificate (and "Transmission" in a pipeline company's name is
    not the electric transmission sector), a Project No. or DI docket is a hydropower project. Every NRC document is
    nuclear; "storage" in one is spent fuel or waste storage unless it speaks of batteries or energy storage."""
    got = {t for t, p in SECTOR_TAGS if re.search(p, text, re.I)}
    if agency == "FERC" and GAS_DOCKET.search(docket or ""):
        got = (got | {"gas"}) - {"transmission"}
    if agency == "FERC" and HYDRO_DOCKET.search(docket or ""):
        got |= {"power", "renewables"}
    if agency == "NRC":
        got.add("nuclear")
        if not NRC_STORAGE.search(text):
            got.discard("storage")
    return ";".join(t for t, _ in SECTOR_TAGS if t in got)


def states(text):
    """US states named in the text. Session 154: the longest name is read first and taken out, so "West Virginia" is
    not also Virginia (2026-02830 held VA;WV), and "Washington, DC" is not the state of Washington."""
    t = NOT_A_STATE.sub(" ", text or "")
    out = set()
    for n, c in sorted(STATES.items(), key=lambda kv: -len(kv[0])):
        t, k = re.subn(rf"\b{n}\b", " ", t)
        if k:
            out.add(c)
    return ";".join(sorted(out))


# ---------------------------------------------------------------- session 157: the printed text, read once
# PLACE RULE (the three faults session 154 left: a state the document names in its first paragraph, a title the
# Register's record cuts short, a state read off an applicant's name). The place of an action is read from its title,
# its abstract with the Register's topics, and the first paragraph of its printed text, after taking out what is not
# a place:
#   1. a company's name: a run of capitalised words that ends in a company word (LLC, Inc., Company, Corporation,
#      L.P., Cooperative, Partners, Association, Co.), with "of <State>" after it, and the short name the document
#      gives it in brackets ("Texas Eastern Transmission, LP (Texas Eastern)");
#   2. the parties named in the title before "; Notice ..." (the applicant), wherever the text repeats them, unless
#      the party is a public body, whose name states its place ("City of Chignik, Alaska");
#   3. a postal address: a state followed by a ZIP code, a state in a street's name ("1001 Louisiana Street"),
#      Washington, DC, and Rockville, Maryland (the NRC's seat);
#   4. a river, county, city, falls, lake or valley that carries a state's name ("the Colorado River", "Kansas City",
#      "Delaware County", "Lake Michigan", "Tennessee Valley Authority").
# Where the title, the abstract and the first paragraph name no state, the place is read from place_words: the first
# sentence in the opening PLACE_REACH characters of the printed text (footnotes apart) that places something in a
# county, parish or borough of a state ("42 miles of pipeline in Rowan, Fleming, and Mason Counties, Kentucky").
# What is left is read with states(). A state agency's name ("the New Hampshire Department of Environmental
# Services") still counts: the audits counted it as the document naming the state.
CO_WORD = (r"(?:L\.?L\.?C\.?|Inc\.?|Incorporated|Company|Corporation|Corp\.?|L\.P\.|LP|Cooperative|Partners|Partnership|"
           r"Co\.|Association)")
CAP = r"[A-Z0-9][\w&'-]*\.?"   # a capitalised word, or a number inside a name ("FFP Missouri 5, LLC")
COMPANY = re.compile(r"\b" + CAP + r"(?:\s+(?:of|and|the|&)\s+" + CAP + r"|\s+" + CAP + r"){0,7}?,?\s+" + CO_WORD
                     + r"(?![\w.])(?:\s+of\s+(?:New |North |South |West )?[A-Z][a-z]+)?(?:,?\s+" + CO_WORD + r"(?![\w.]))?"
                     + r"(?:\s*\(([^()]{2,40})\))?")
STATE_NAMES = "|".join(sorted(STATES, key=len, reverse=True))
ADDRESS = re.compile(r"\b(?:" + STATE_NAMES + r"),?\s+\d{5}(?:-\d{4})?\b|\b(?:" + STATE_NAMES + r")\s+(?:Street|St\.|Avenue|Ave\.|"
                     r"Boulevard|Blvd\.|Road|Drive|Way|Highway|Parkway|Plaza)\b|\bRockville,? Maryland\b")
NAMED_AFTER = re.compile(r"\b(?:" + STATE_NAMES + r")\s+(?:River|County|Parish|City|Valley|Beach|Basin|Lake|Canyon|Falls|Springs|Rapids|Harbor)\b"
                         r"|\bLake\s+(?:" + STATE_NAMES + r")\b")
TITLE_WORD = re.compile(r"^(Notice|Order|Errata|Supplemental|Revised|Amended|Application|Petition|Technical|Request|"
                        r"Environmental|Combined)\b")
FOOTNOTE = re.compile(r"\\\d+\\")
PARA_MAX = 1500
PLACE_REACH = 8000
IN_A_COUNTY = re.compile(r"\b(?:Count(?:y|ies)|Parish(?:es)?|Borough|Township)s?,?\s+(?:" + STATE_NAMES + r")\b"
                         r"|\b(?:is|are|be|facility|facilities|project) located\b[^.;]{0,160}?\b(?:" + STATE_NAMES + r")\b")
# A party of a title that is a public body keeps its state ("City of Chignik, Alaska", "New Hampshire Department of
# Environmental Services"); any other party is an applicant's name and is taken out whole.
PUBLIC_BODY = re.compile(r"\b(City|Town|Village|County|Borough|State|Commonwealth|Department|Commission|District|"
                         r"Authority|Tribe|Tribes|Nation|Board|Agency|Bureau|University)\b")
DATE_LINE = re.compile(r"(?:Issued:? )?[A-Z][a-z]+ \d{1,2}, \d{4}\.?")


def title_parties(title):
    """The parties a notice's title names before its own words ("A, LLC; B Inc.; Notice of ..."): the segments,
    cut at ";", that come before the first one beginning with a title word."""
    out = []
    for seg in [x.strip() for x in (title or "").split(";")]:
        if not seg or TITLE_WORD.match(seg):
            break
        out.append(seg)
    return out if len(out) < len([x for x in (title or "").split(";") if x.strip()]) or (title or "").rstrip().endswith(";") else []


def not_a_place(text, parties=()):
    """The text with what is not a place taken out (PLACE RULE 1 to 4)."""
    t = text or ""
    shorts = []
    for m in COMPANY.finditer(t):                      # 1. the short name a company is given in brackets
        if m.group(1):
            shorts.append(m.group(1).strip())
    for p in sorted(parties, key=len, reverse=True):   # 2. the applicant, as the title names it
        if len(p) >= 4 and not PUBLIC_BODY.search(p):
            t = re.sub(re.escape(p), " ", t, flags=re.I)
            bare = re.sub(r",?\s+" + CO_WORD + r"$", "", p).strip()
            if len(bare) >= 4 and bare != p:
                shorts.append(bare)

    def company(m):                                    # 1. a company's name; "Hamilton, Ohio and X, Inc." keeps Ohio
        lead = re.match(r"(" + STATE_NAMES + r") and ", m.group(0))
        return lead.group(1) + " " if lead and t[max(0, m.start() - 2):m.start()] == ", " else " "
    t = COMPANY.sub(company, t)
    for sname in sorted(set(shorts), key=len, reverse=True):
        if re.search(r"\b(?:" + STATE_NAMES + r")\b", sname):
            t = re.sub(r"\b" + re.escape(sname) + r"\b", " ", t)
    t = ADDRESS.sub(" ", t)                            # 3. a postal address
    return NAMED_AFTER.sub(" ", t)                     # 4. a river, county or city with a state's name


def place_states(title, abstract, first_paragraph, place_words=""):
    """The states an action's own words name as its place (PLACE RULE). place_words is read only when the title, the
    abstract and the first paragraph name none."""
    parties = title_parties(title)
    got = states(" . ".join(not_a_place(x, parties) for x in (title, abstract, first_paragraph)))
    return got or states(not_a_place(place_words, parties))


def county_sentence(text):
    """The first sentence of the text that places something in a county, parish or borough of a state; '' if none."""
    m = IN_A_COUNTY.search(text or "")
    if not m:
        return ""
    cut = max(text.rfind(". ", 0, m.start()), text.rfind("; ", 0, m.start()), text.rfind(": ", 0, m.start()))
    a = cut + 2 if cut >= 0 else 0
    ends = [x for x in (text.find(". ", m.end()), text.find("; ", m.end())) if x >= 0]
    b = min(ends) + 1 if ends else len(text)
    return text[max(a, m.start() - 250):min(b, m.end() + 200)].strip()


def printed(raw, record_title=""):
    """What the connector takes from a Federal Register document's printed text (the Register's plain text, HTML
    around a <pre>): {"title": the printed title, with the paragraph that carries on a title ending in ";",
    "first_paragraph": its SUMMARY where it has one, else the first paragraph after the title (with the lettered
    items that follow a paragraph ending in ":"), at most PARA_MAX characters}. Empty strings where the text has no
    such part. Page marks, rule lines and footnotes are not paragraphs."""
    text = H.unescape(re.sub(r"<[^>]+>", "", raw or "")).replace(chr(13) + chr(10), chr(10))
    m = re.search(r"\[FR Doc No: [^\]]+\]", text)
    body = text[m.end():] if m else text
    end = re.search(r"\n\[FR Doc\. [^\]]*Filed[^\]]*\]", body)   # the document's own last line
    body = body[:end.start()] if end else body
    body = re.sub(r"\n[ \t]*\n+\[\[Page \d+\]\][ \t]*\n[ \t]*\n+", "\n", body)   # a page break inside a paragraph
    nl = chr(10)
    lines = []
    for ln in body.split(nl):
        if re.fullmatch(r"\s*-{20,}\s*", ln):          # a rule line (round the heading, round footnotes) parts paragraphs
            lines.append("")
            continue
        if re.fullmatch(r"\s*(\[\[Page \d+\]\]|={20,}|_{20,})\s*", ln):
            continue
        lines.append(ln)
    blocks = [b for b in re.split(r"\n[ \t]*\n", nl.join(lines)) if b.strip()]
    one = lambda b: re.sub(r"\s+", " ", FOOTNOTE.sub("", b)).strip()
    key = re.sub(r"[^a-z0-9]+", " ", (record_title or "").lower()).strip()[:40]
    at = None
    for i, b in enumerate(blocks[:40]):
        k = re.sub(r"[^a-z0-9]+", " ", one(b).lower()).strip()
        if key and k and (k.startswith(key) or key.startswith(k[:40]) and len(k) >= 12):
            at = i
            break
    if at is None:
        return {"title": "", "first_paragraph": "", "place_words": ""}
    title = one(blocks[at])
    paras = [p for p in re.split(r"\n(?= {4}\S)|\n[ \t]*\n", nl + nl.join(b + nl for b in blocks[at + 1:at + 60]))
             if p.strip() and not re.match(r"\s*\\\d+\\", p) and not p.strip().startswith("[")]
    paras = [x for x in (one(p) for p in paras) if not DATE_LINE.fullmatch(x)]   # a notice's own date line is no paragraph
    if title.endswith(";") and paras and TITLE_WORD.match(paras[0]) and not re.search(r"\.\s+[A-Z]", paras[0]):
        title, paras = f"{title} {paras[0]}", paras[1:]
    m = re.search(r"(?:^|\n)SUMMARY:\s*(.*?)(?:\n[ \t]*\n|\Z)", (nl + nl).join(blocks[at + 1:at + 14]), re.S)
    if m:
        first = one(m.group(1))
    else:
        paras = [p for p in paras if not re.match(r"(AGENCY|ACTION|DATES|ADDRESSES):", p)]
        first = paras[0] if paras else ""
        if first.endswith(":"):
            for p in paras[1:]:
                if not re.match(r"[a-z]\. ", p) or len(first) + len(p) > PARA_MAX:
                    break
                first = f"{first} {p}"
    return {"title": clean(title), "first_paragraph": clean(first)[:PARA_MAX],
            "place_words": clean(county_sentence(" ".join(paras)[:PLACE_REACH]))[:450]}


def cut_short(record_title, printed_title):
    """TITLE RULE: the Register's record cuts a title short when it ends at a semicolon ("Gulf South Pipeline Company,
    LLC;") and the printed document's title begins with the same words and goes on. Only then is the printed title
    taken (title_register keeps the record's). A printed heading that merely adds a line ("...; Final Rule") is left."""
    a, b = (record_title or "").strip(), (printed_title or "").strip()
    return a.endswith(";") and len(b) > len(a) + 3 and b.lower().startswith(a.lower())


def text_dir(args=None):
    return os.path.abspath(args.text_dir) if args is not None and getattr(args, "text_dir", None) else \
        os.path.join(ip.RAW_DIR, "policy_sources", "fr_text")


LIMIT_WAIT, LIMIT_WAIT_MAX = 120, 300   # seconds to wait on an HTTP 429 that names no Retry-After, and the most waited


def read_texts(rows, held, store, log, max_requests=300, max_bytes=300_000_000, pause=2.0, fetch=None, sleep=None):
    """Each Federal Register row's printed text, read once. In this order: the store (a file by document number),
    else what the table held already took from it (text_status "read", or "not reachable": never asked twice), else
    one request, newest document first, until BEFORE a ceiling (requests, bytes). Sets first_paragraph,
    title_register, title, states, text_status and text_read_at on the rows; returns the counts. fetch(url) is the
    request, returning (status, bytes, Retry-After) (a test replaces it, and sleep); a response that is not HTTP 200
    is recorded and left.

    The Register's own limit is honoured (session 157: its trial ran at one request a second, and after about 450
    requests the Register answered HTTP 429 to 170 in a row while the first version of this loop kept asking). An
    HTTP 429 is the Register saying slow down, not an answer about the document: nothing is written to the row; the
    run waits as Retry-After says (LIMIT_WAIT seconds where it names none, LIMIT_WAIT_MAX at most), doubles its
    pause and asks for that one document once more; a second 429 ends the asking for this run, and every document
    not yet asked waits for a later run. pause is the seconds between two requests (2: one request every two
    seconds, under the two a second the session allowed)."""
    import time
    sleep = sleep or time.sleep
    os.makedirs(store, exist_ok=True)
    n = {"store": 0, "table": 0, "asked": 0, "bytes": 0, "not_reachable": 0, "left": 0, "titles": 0, "limited": 0}
    held = held or {}
    last, gap, ended = [0.0], [pause], [False]

    def ask(url):
        wait = gap[0] - (time.time() - last[0])
        if wait > 0:
            sleep(wait)
        last[0] = time.time()
        r = requests.get(url, headers=UA, timeout=90, allow_redirects=False)   # a redirect is never followed (below)
        return r.status_code, r.content, r.headers.get("Retry-After", "") or r.headers.get("Location", "")

    fetch = fetch or ask

    def ask_politely(url, num):
        """(status, bytes) of one document, honouring a 429 as the docstring says; (None, b"") when the run's asking
        has ended."""
        got = tuple(fetch(url)) + ("",)
        n["asked"] += 1
        if got[0] in (301, 302, 303, 307, 308) or (got[0] == 200 and b"[FR Doc No" not in got[1]):
            # The Register sends automated requests it does not want to a check of its own (session 157: its
            # developers page answered HTTP 302 to unblock.federalregister.gov). A redirect is not followed and an
            # answer that is not a printed document is not kept: the asking ends for this run, nothing is written.
            n["refused"] = n.get("refused", 0) + 1
            ended[0] = True
            log(f"  printed text {num}: HTTP {got[0]}" + (f" to {str(got[2])[:120]}" if got[0] != 200 else
                                                        ", not a printed document") + "; not followed, not kept; "
                "no more printed texts are asked for in this run")
            return None, b""
        if got[0] != 429:
            return got[0], got[1]
        n["limited"] += 1
        after = str(got[2] or "").strip()
        wait = min(int(after) if after.isdigit() else LIMIT_WAIT, LIMIT_WAIT_MAX)
        gap[0] = gap[0] * 2
        log(f"  printed text {num}: HTTP 429 (Retry-After: {after or 'none given'}); waiting {wait} seconds, then one "
            f"request every {gap[0]:g} seconds")
        sleep(wait)
        if n["asked"] >= max_requests:
            ended[0] = True
            return None, b""
        got = tuple(fetch(url)) + ("",)
        n["asked"] += 1
        if got[0] == 429:
            n["limited"] += 1
            ended[0] = True
            log(f"  printed text {num}: HTTP 429 again; no more printed texts are asked for in this run")
            return None, b""
        if got[0] in (301, 302, 303, 307, 308) or (got[0] == 200 and b"[FR Doc No" not in got[1]):
            n["refused"] = n.get("refused", 0) + 1
            ended[0] = True
            log(f"  printed text {num}: HTTP {got[0]} after the wait, not a printed document; not followed, not kept; "
                "no more printed texts are asked for in this run")
            return None, b""
        return got[0], got[1]
    for r in sorted((x for x in rows if x.get("fr_document_number")), key=lambda x: x["event_date"], reverse=True):
        num, old = r["fr_document_number"], held.get(r["event_id"], {})
        path = os.path.join(store, re.sub(r"[^A-Za-z0-9_.-]", "_", num) + ".txt")
        raw = None
        if os.path.exists(path):
            with open(path, "rb") as f:
                raw = f.read().decode("utf-8", "replace")
            r["text_status"] = "read"
            r["text_read_at"] = old.get("text_read_at") or ip.utc_iso(pd.Timestamp(os.path.getmtime(path), unit="s", tz="UTC"))
            n["store"] += 1
        elif old.get("text_status"):
            for c in TEXT_COLS:
                r[c] = old.get(c, "")
            if old["text_status"] == "read":
                if old.get("title_register"):
                    r["title"] = old["title"]
                r["states"] = place_states(r["title"], f"{r['abstract']} {r.get('_topics', '')}", r["first_paragraph"],
                                           r.get("place_words", ""))
            n["table"] += 1
            continue
        else:
            url = r.get("_text_url") or ""
            if not url or "@" in url:
                continue   # no printed text address in the record (or one that holds an e-mail address: not requested)
            if ended[0] or n["asked"] >= max_requests or n["bytes"] + 5_000_000 > max_bytes:
                n["left"] += 1
                continue
            try:
                status, content = ask_politely(url, num)
            except Exception as exc:   # a network fault is not an answer: the next run asks again
                n["asked"] += 1
                log(f"  printed text {num}: {ip.redact(repr(exc))[:160]}")
                continue
            if status is None:         # the Register's limit ended this run's asking: the document waits
                n["left"] += 1
                continue
            n["bytes"] += len(content)
            now = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
            if status != 200:
                r["text_status"], r["text_read_at"] = f"not reachable: HTTP {status}", now
                n["not_reachable"] += 1
                log(f"  printed text {num}: HTTP {status} for {url}")
                continue
            with open(path + ".tmp", "wb") as f:
                f.write(content)
            os.replace(path + ".tmp", path)
            raw, r["text_status"], r["text_read_at"] = content.decode("utf-8", "replace"), "read", now
        got = printed(raw, r["title"])
        r["first_paragraph"] = got["first_paragraph"]
        full = got["title"]
        if cut_short(r["title"], full):
            r["title_register"], r["title"] = r["title"], full   # the Register's record cuts the title short
            n["titles"] += 1
        first = place_states(r["title"], f"{r['abstract']} {r.get('_topics', '')}", r["first_paragraph"])
        r["place_words"] = "" if first else got["place_words"]
        r["states"] = first or place_states(r["title"], "", "", r["place_words"])
    log(f"  printed texts: {n['store']} from the store, {n['table']} already read in the table held, {n['asked']} asked "
        f"({n['bytes']} bytes), {n['not_reachable']} not reachable, {n['limited']} answered HTTP 429 (the Register's "
        f"limit), {n['left']} left for a later run (a ceiling or that limit), {n['titles']} titles the record cuts short")
    return n


def get(url, log, **kw):
    def call():
        r = requests.get(url, headers=UA, timeout=90, **kw)
        if r.status_code != 200:
            raise RuntimeError(f"HTTP {r.status_code} for {r.url}")
        return r
    return ip.with_retries(url, call, log)


def federal_register(since, log):
    fields = ["document_number", "type", "title", "abstract", "action", "publication_date", "agencies", "docket_ids",
              "regulation_id_numbers", "html_url", "topics", "significant", "raw_text_url"]
    rows, got = [], ip.utc_iso(pd.Timestamp.now(tz="UTC"))
    for slug, short in AGENCIES.items():
        for t in TYPES:
            page = 1
            while True:
                r = get(FR, log, params={"conditions[agencies][]": slug, "conditions[type][]": {"Rule": "RULE",
                        "Proposed Rule": "PRORULE", "Notice": "NOTICE"}[t], "conditions[publication_date][gte]": since,
                        "per_page": 1000, "page": page, "order": "oldest", "fields[]": fields})
                d = r.json()
                for x in d.get("results", []):
                    x["_short"], x["_url"], x["_got"] = short, r.url, got
                    rows.append(x)
                log(f"  Federal Register {short} {t} page {page}: {len(d.get('results', []))} (of {d.get('count')})")
                if page >= (d.get("total_pages") or 1):
                    break
                page += 1
    out, seen = [], set()
    for x in rows:
        if x["document_number"] in seen:
            continue
        seen.add(x["document_number"])
        names = [a.get("name") or a.get("raw_name", "") for a in x.get("agencies") or []]
        shorts = [AGENCIES.get((a.get("url") or "").rstrip("/").split("/")[-1], "") for a in x.get("agencies") or []]
        agency = "FERC" if "FERC" in shorts else next((s for s in ["NRC", "BLM", "EPA", "DOE", "Interior", "IRS", "Treasury"] if s in shorts),
                                                       x["_short"])
        title, abstract = clean(x.get("title")), clean(x.get("abstract"))
        text = f"{title} {abstract} {' '.join(x.get('topics') or [])}"
        if agency not in ALWAYS_ENERGY and not ENERGY.search(text):
            continue
        if ROUTINE.search(title):
            continue
        rins = [r_ for r_ in x.get("regulation_id_numbers") or [] if r_]
        docket = ";".join([d_ for d_ in x.get("docket_ids") or [] if d_] + rins)
        out.append({"event_id": f"federalregister:{x['document_number']}", "event_date": x["publication_date"],
                    "event_type": "filing", "parties": ";".join(n for n in names if n), "status": clean(x.get("action")),
                    "source": "federalregister:api", "source_url": x["html_url"], "agency": agency,
                    "action_type": TYPES.get(x["type"], "notice"), "title": title, "abstract": abstract[:1500],
                    "docket": docket, "rin": ";".join(rins),
                    "fr_document_number": x["document_number"], "sector_tags": tags(text, agency, docket),
                    "states": place_states(title, f"{abstract} {' '.join(x.get('topics') or [])}", ""),
                    "_text_url": x.get("raw_text_url") or "", "_topics": " ".join(x.get("topics") or []),
                    "retrieved_at": x["_got"]})
    log(f"  Federal Register: {len(seen)} documents, {len(out)} kept (energy, not routine)")
    return out


def rss(name, agency, url, since, log):
    r = get(url, log)
    got = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
    out = rss_rows(name, agency, r.content, since, got)
    log(f"  {name}: {len(out)} items since {since} (the feed's window)")
    return out


def release_day(pub_date):
    """The day a feed item was released, as the agency dates it (session 154). The NRC's feed gives GMT times, so a
    release of the evening in Washington carried the next day's date: 24 of the feed's 167 items on 8 October 2026,
    and each of the 7 releases opened states the Eastern day. None when the feed's date cannot be read."""
    when = pd.to_datetime(pub_date, utc=True, errors="coerce")
    return None if pd.isna(when) else when.tz_convert(EASTERN).strftime("%Y-%m-%d")


def rss_rows(name, agency, content, since, got):
    """The rows of one feed (its bytes), apart from the request so that a saved feed can be read again."""
    out = []
    for it in ET.fromstring(content).iter("item"):
        title, link = clean(it.findtext("title")), (it.findtext("link") or "").strip()
        day = release_day(it.findtext("pubDate"))
        if not link or day is None or day < since:
            continue
        desc = clean(it.findtext("description"))
        text = f"{title} {desc}"
        out.append(press(name, agency, link, day, title, text, got,
                         "TX" if agency == "PUCT" else "CA" if agency == "CPUC" else states(text)))
    return out


def press(name, agency, link, date, title, text, got, st):
    # session 154: the PUCT's news page also lists releases of the Governor's office (gov.texas.gov); the row stays
    # under the commission that lists it, and parties names who issued it
    parties = f"Office of the Texas Governor;{agency}" if "gov.texas.gov" in link.lower() else agency
    return {"event_id": f"{name}:{hashlib.sha1(link.encode()).hexdigest()[:12]}", "event_date": date,
            "event_type": "announcement", "parties": parties, "status": "news release", "source": f"{name}:news",
            "source_url": link, "agency": agency, "action_type": "press_release", "title": title, "abstract": "",
            "docket": "", "rin": "", "fr_document_number": "", "sector_tags": tags(text, agency), "states": st,
            "retrieved_at": got}


def puct(since, log):
    url = "https://www.puc.texas.gov/agency/resources/pubs/news/"
    t = get(url, log).text
    got = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
    out = []
    for link, title, date in re.findall(r'<a href="([^"]+)"[^>]*>([^<]{10,300})</a><br\s*/?>\s*<span[^>]*>([A-Z][a-z]+ \d{1,2}, \d{4})',
                                        t):
        d = pd.to_datetime(date, errors="coerce")
        if pd.isna(d) or d.strftime("%Y-%m-%d") < since:
            continue
        # the page also lists the Governor's releases about the PUCT's programs: kept, with their own link
        out.append(press("puct", "PUCT", link, d.strftime("%Y-%m-%d"), clean(title), clean(title), got, "TX"))
    log(f"  PUCT news page: {len(out)} dated items since {since}")
    return out


def cpuc(since, log):
    out, got = [], ip.utc_iso(pd.Timestamp.now(tz="UTC"))
    for page in range(0, 80):
        t = get("https://www.cpuc.ca.gov/news-and-updates/all-news" + (f"?page={page}" if page else ""), log).text
        items = re.findall(r'<a href="(https://www\.cpuc\.ca\.gov/news-and-updates/all-news/[^"]+)">.*?'
                           r'<span class="heading__main">(.*?)</span>.*?news__date[^>]*>([A-Z][a-z]+ \d{1,2}, \d{4})', t, re.S)
        if not items:
            break
        older = False
        for link, title, date in items:
            d = pd.to_datetime(date, errors="coerce")
            if pd.isna(d):
                continue
            if d.strftime("%Y-%m-%d") < since:
                older = True
                continue
            if not ENERGY.search(clean(title)):  # the CPUC also regulates rail, water and telecommunications
                continue
            out.append(press("cpuc", "CPUC", link, d.strftime("%Y-%m-%d"), clean(title), clean(title), got, "CA"))
        if older:
            break
    log(f"  CPUC news: {len(out)} items since {since} ({page + 1} pages read)")
    return out


def words(s):
    return {w for w in re.findall(r"[a-z0-9]+", (s or "").lower()) if w not in STOP and len(w) > 2}


def similar(a, b):
    wa, wb = words(a), words(b)
    return len(wa & wb) / max(1, len(wa | wb))


def fold_press(frame, log):
    """A news release that reports a Register document (the same docket in its text, or a title of the same content
    words, similarity 0.5 or more, within 30 days) is folded into it: its link goes to related_urls."""
    fr = frame[frame["action_type"] != "press_release"]
    pr = frame[frame["action_type"] == "press_release"]
    drop = []
    frd = pd.to_datetime(fr["event_date"])
    for i, p in pr.iterrows():
        near = fr[(abs(frd - pd.Timestamp(p["event_date"])) <= pd.Timedelta(days=30)) & (fr["agency"] == p["agency"])]
        best = max(((similar(p["title"], r["title"]), j) for j, r in near.iterrows()), default=(0, None))
        if best[0] >= 0.5:
            j = best[1]
            frame.at[j, "related_urls"] = ";".join(x for x in [frame.at[j, "related_urls"], p["source_url"]] if x)
            drop.append(i)
    log(f"  {len(drop)} news releases folded into the Register documents they report")
    return frame.drop(index=drop)


def link_news(frame, log):
    """The scored news stories that report the same action (deduplication against news_stories)."""
    path = os.path.join(ip.OUT_DIR, "news_stories.csv")
    if not os.path.exists(path):
        log("  news_stories.csv not on this machine: no links to news")
        return frame
    with open(path, encoding="utf-8") as fh:
        skip = sum(1 for line in fh if line.startswith("#"))
    n = pd.read_csv(path, skiprows=skip, dtype=str, keep_default_na=False)
    n = n[n.get("scored_at", "") != ""] if "scored_at" in n.columns else n
    n = n.assign(d=pd.to_datetime(n["event_date"], utc=True, errors="coerce").dt.tz_localize(None).dt.normalize(),
                 text=(n["title"].fillna("") + " " + n["summary"].fillna("")))
    n = n[n["d"] >= pd.Timestamp(frame["event_date"].min()) - pd.Timedelta(days=21)]
    nwords = [words(t) for t in n["title"]]
    linked = 0
    for i, r in frame.iterrows():
        d = pd.Timestamp(r["event_date"])
        ids = [x for x in (r["docket"].split(";") + [r["fr_document_number"]]) if len(x) >= 6]
        hit = set()
        if ids:
            m = n["text"].str.contains("|".join(re.escape(x) for x in ids), regex=True)
            hit |= set(n.index[m])
        rw = words(r["title"])
        win = n.index[(n["d"] >= d - pd.Timedelta(days=2)) & (n["d"] <= d + pd.Timedelta(days=21))]
        for j in win:
            k = n.index.get_loc(j)
            if rw and len(rw & nwords[k]) / max(1, len(rw | nwords[k])) >= 0.5:
                hit.add(j)
        if r["action_type"] == "press_release":  # the agency's own feed item, already in news_stories
            hit |= set(n.index[n["source_url"] == r["source_url"]])
        if hit:
            frame.at[i, "news_story_ids"] = ";".join(sorted(n.loc[list(hit), "event_id"]))
            frame.at[i, "news_story_urls"] = ";".join(sorted(n.loc[list(hit), "source_url"]))
            linked += 1
    log(f"  {linked} actions linked to the news stories that report them")
    return frame


def held_table():
    """{event_id: row} of the table held (any columns it has), {} when there is none."""
    path = os.path.join(ip.OUT_DIR, NAME + ".csv")
    if not os.path.exists(path):
        return {}
    old = pd.read_csv(path, skiprows=ip.header_rows(path), dtype=str, keep_default_na=False)
    return {r["event_id"]: r for r in old.to_dict("records")}


def widen_held(log):
    """Session 157: the table held from before has no columns for the printed text and the recheck marks, and the
    merge refuses a file of another shape. A file that has exactly the earlier columns gains the new ones, empty, in
    their place; no value changes. Any other shape is left for the merge to refuse."""
    path = os.path.join(ip.OUT_DIR, NAME + ".csv")
    if not os.path.exists(path):
        return False
    n = ip.header_rows(path)
    old = pd.read_csv(path, skiprows=n, dtype=str, keep_default_na=False)
    if list(old.columns) != COLS_S154:
        return False
    ip._require_lock(path, f"widening {NAME}")
    with open(path, encoding="utf-8") as fh:
        head = [next(fh) for _ in range(n)]
    for c in COLS:
        if c not in old.columns:
            old[c] = ""
    with open(path + ".tmp", "w", encoding="utf-8", newline="") as fh:
        fh.writelines(head)
        old[COLS].to_csv(fh, index=False, lineterminator=chr(10))
    os.replace(path + ".tmp", path)
    log(f"  {NAME}: the table held gained the columns of session 157, empty ({len(old)} rows, no value changed)")
    return True


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW policy sources")
    ap.add_argument("--since", default="2025-10-01")
    ap.add_argument("--out-dir", help="session 154: a trial run, every output (the table, logs, raw files, registry, "
                                      "status) under this directory and nothing under warehouse/output")
    ap.add_argument("--sources", default="federalregister,nrc,doe,puct,cpuc",
                    help="session 157: the sources to ask, comma separated (a trial may ask the Register alone; the "
                         "rows of a source not asked stay as the table holds them)")
    ap.add_argument("--text-dir", help="session 157: the store of printed texts by document number (default: "
                                       "warehouse/raw/policy_sources/fr_text)")
    ap.add_argument("--max-texts", type=int, default=300,
                    help="session 157: at most this many requests for printed texts in one run; the rest wait for "
                         "the next run")
    ap.add_argument("--text-pause", type=float, default=2.0,
                    help="session 157: seconds between two requests for a printed text (never under 0.5: two a second)")
    ap.add_argument("--max-text-bytes", type=int, default=300_000_000)
    args = ap.parse_args(argv)
    if args.out_dir:
        ip.set_out_dir(args.out_dir)
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"policy_sources_{run_id}.log"))
    ip.RAW.open("policy_sources", run_id)
    results, rows, absent = [], [], []
    asked = [x.strip() for x in args.sources.split(",") if x.strip()]
    try:
        for name, fn in (("federalregister", lambda: federal_register(args.since, log)),
                         ("nrc", lambda: rss("nrc", "NRC", "https://www.nrc.gov/public-involve/rss?feed=news", args.since, log)),
                         ("doe", lambda: rss("doe", "DOE", "https://www.energy.gov/rss/newsroom.xml", args.since, log)),
                         ("puct", lambda: puct(args.since, log)), ("cpuc", lambda: cpuc(args.since, log))):
            if name not in asked:
                log(f"{name}: not asked this run (--sources {args.sources}); its rows stay as the table holds them")
                continue
            try:
                got = fn()
                rows += got
                results.append(dict(table=NAME, market=name, status="ok", detail=f"{len(got)} rows"))
            except Exception as exc:
                last = ip.redact(repr(exc))[:300]
                log(f"{name} FAILED: {last}")
                print(f"policy_sources {name} FAILED: {last}", file=sys.stderr)
                absent.append(name)
                results.append(dict(table=NAME, market=name, status="failed", detail=last))
        if not rows:
            raise RuntimeError("no source returned rows")
        held = held_table()
        counts = read_texts(rows, held, text_dir(args), log, max_requests=args.max_texts, max_bytes=args.max_text_bytes,
                            pause=max(0.5, args.text_pause))
        results.append(dict(table=NAME, market="printed_text", status="ok",
                            detail=f"{counts['asked']} asked ({counts['bytes']} bytes), {counts['store']} from the store, "
                                   f"{counts['table']} read before, {counts['not_reachable']} not reachable, "
                                   f"{counts['limited']} answered HTTP 429, {counts['left']} left for a later run"))
        f = pd.DataFrame(rows)
        for c in COLS:
            if c not in f.columns:
                f[c] = ""
        f = f.drop_duplicates("event_id").reset_index(drop=True).fillna("")
        if set(asked) >= {"federalregister", "nrc", "doe", "puct", "cpuc"}:
            f = fold_press(f, log)
        else:   # a run that did not ask every source cannot fold the releases again: the links held are kept
            f["related_urls"] = [held.get(i, {}).get("related_urls", "") for i in f["event_id"]]
        f = link_news(f, log)
        if os.path.exists(SCORES):  # the scores warehouse/policy/score.py wrote, kept across runs
            s = pd.read_csv(SCORES, dtype=str, keep_default_na=False).drop_duplicates("event_id", keep="last")
            for c in SCORE_COLS:
                if c not in s.columns:
                    s[c] = ""
            f = f.drop(columns=SCORE_COLS).merge(s[["event_id"] + SCORE_COLS], on="event_id", how="left").fillna("")
        f = f[COLS].sort_values(["event_date", "event_id"])
        header = [
            "Energy Research Warehouse (ERW): policy actions: Federal Register rules, proposed rules and notices of DOE, "
            "FERC, EPA, NRC, BLM and Interior on energy, and news releases of NRC, DOE, the PUCT and the CPUC",
            "Shape: events (docs/datastandard.md v0). event_date is the publication or release date; the columns after "
            "source_url are described in warehouse/connectors/policy_sources.py.",
            f"Window: {args.since} to the run; every run reads the Register window again and merges news releases.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/policy_sources.py",
            f"Run log: warehouse/output/logs/policy_sources_{run_id}.log",
            f"Raw files: warehouse/raw/policy_sources/{run_id}/ (not in git)",
            "Sources: federalregister:api (https://www.federalregister.gov/developers/documentation/api/v1); nrc:news "
            "(https://www.nrc.gov/public-involve/rss?feed=news); doe:news (https://www.energy.gov/rss/newsroom.xml); "
            "puct:news (https://www.puc.texas.gov/agency/resources/pubs/news/); cpuc:news "
            "(https://www.cpuc.ca.gov/news-and-updates/all-news). FERC's own pages answer a Cloudflare challenge: not read.",
            "Scores (significance, sector, why) from warehouse/policy/score.py with the news rubric; blank = not scored.",
            "Session 157: first_paragraph, title_register, text_status and text_read_at come from each Register "
            "document's printed text, read once (the place in states is read from it too); model_recheck says whether "
            "the model's fields were rechecked against that text, and model_rechecked_at when.",
        ] + ([f"Absent inputs: {', '.join(absent)} (failed this run; their rows from earlier runs are kept)"] if absent else []) + [
            "License: public (US and state government publications)."]
        widen_held(log)
        ip.write_csv(f, NAME, header, log, cols=COLS, key=["event_id"], time_col="event_date")
        ip.update_sources([
            dict(source="federalregister:api", publisher="Office of the Federal Register (NARA)",
                 report="Federal Register documents API", report_url="https://www.federalregister.gov/developers/documentation/api/v1",
                 document_list=FR, license="public", tables=[NAME]),
            dict(source="nrc:news", publisher="U.S. Nuclear Regulatory Commission (NRC)", report="NRC news releases (RSS)",
                 report_url="https://www.nrc.gov/reading-rm/doc-collections/news/", document_list="https://www.nrc.gov/public-involve/rss?feed=news",
                 license="public", tables=[NAME]),
            dict(source="doe:news", publisher="U.S. Department of Energy (DOE)", report="DOE newsroom (RSS)",
                 report_url="https://www.energy.gov/newsroom", document_list="https://www.energy.gov/rss/newsroom.xml",
                 license="public", tables=[NAME]),
            dict(source="puct:news", publisher="Public Utility Commission of Texas (PUCT)", report="PUCT news releases",
                 report_url="https://www.puc.texas.gov/agency/resources/pubs/news/", document_list="https://www.puc.texas.gov/agency/resources/pubs/news/",
                 license="public", tables=[NAME]),
            dict(source="cpuc:news", publisher="California Public Utilities Commission (CPUC)", report="CPUC news",
                 report_url="https://www.cpuc.ca.gov/news-and-updates/all-news", document_list="https://www.cpuc.ca.gov/news-and-updates/all-news",
                 license="public", tables=[NAME])])
        by = f.groupby(["agency", "action_type"]).size()
        log("rows by agency and type: " + "; ".join(f"{a} {t} {n}" for (a, t), n in by.items()))
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{NAME} FAILED, no output file written:\n{tb}")
        print(f"policy_sources {NAME} FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    ip.write_status("policy_sources", run_id, results)
    log.close()
    print(f"policy_sources run log: {os.path.relpath(log.path, ip.ROOT)}")
    return 1 if any(r["status"] == "failed" and r["market"] == "all" for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
