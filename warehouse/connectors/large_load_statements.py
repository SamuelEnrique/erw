#!/usr/bin/env python3
"""Public statements of large load waiting for power, each with its exact sentence: a pilot table (session 139).

Energy Research Warehouse (ERW). Writes warehouse/output/large_load_statements.csv (events shape, one row per figure
as a utility's or grid operator's own document states it). INTERNAL: nothing here is published, on the site, in the
public Redivis dataset or in the live set.

What it is. No public dataset says how much large load (datacenters above all) is waiting for power by place, or how
long a new large load waits; the pieces sit in utility planning filings, rate cases, load forecast reports and
earnings materials. On 7 October 2026 two research passes, each an AI research agent with web search, collected the most recent
public statements of ten utilities and operators (Dominion Energy Virginia, Georgia Power, Duke Energy, Entergy, PJM,
Oncor, CenterPoint Energy Houston Electric, American Electric Power, Exelon, ERCOT). Each document was downloaded,
its text extracted, and each statement's sentence checked by code to be a literal substring of that text with its
megawatt or gigawatt figure in it. The passes' own files (statements, rejects, documents opened, timing, notes, the
raw documents and the checking scripts) are under warehouse/raw/large_load_pilot/A and B (not in git).

What this script does. It makes no request and no model call. It reads the two passes' verified statements, checks
each again as far as the row itself allows (a sentence, an address, a figure that stands in the sentence), and writes
at most PER_GROUP statements for each of the ten entities: the owner asked for 30 to 50 statements, and the passes
verified more. The choice is by rule, not by hand:
    1. a row its collector marked CAUTION (a third party's copy of a filing) is not taken;
    2. within an entity, newest document first and, among a document's figures, the largest first (a total before
       its parts); a row whose stage, as worded, is not yet among those taken comes before one that repeats a stage;
    3. the first PER_GROUP rows are taken.
Every verified row not taken is written beside the passes' files (not_taken.csv), so nothing collected is lost.

No number without its sentence. Nothing is summed, netted, converted or annualized across statements: each entity
counts differently (requests, studies, letters, contracts, forecasts), and the stage is kept in the document's own
words (column status, and stage_as_worded). mw is the quantity of quantity_as_written in MW (a figure in gigawatts
times 1,000); where the document gives a range, mw is empty and mw_low and mw_high hold its ends.

event_date is the document's date. A document dated to a month only is filed on that month's first day, and
document_date_as_stated holds what the document states.

Session 141: from ten entities to forty. Six more research passes on 7 October 2026 (warehouse/raw/large_load_statements/C
to H, the same files as the pilot's passes and five more columns: page, row_kind, stage_class_proposed,
stage_class_reason, terms_url; each pass also wrote stages.csv, the stage words each entity uses, in its own order, with
the document's own definition where it gives one). Five passes read thirty more utilities and operators; the sixth went
back to the pilot's ten for the planning filings, testimony and forecasts the pilot did not reach. What changed here:
    - GROUPS names forty entities (ENTITIES_141 says how they were chosen). A row is filed under its entity group by
      the name its collector gave it. PPL's and FirstEnergy's submissions that PJM posts, which the pilot filed under
      PJM, are now under PPL and FirstEnergy, which are entities of their own.
    - The pilot took at most five statements an entity because the owner asked for 30 to 50 statements. That cap is
      gone: every verified statement that passes the row check is taken, once (the same entity, address, figure and
      sentence collected twice is one row; the newest pass's copy is kept). A row its collector marked CAUTION (a third
      party's words or copy) is still not taken, and neither is a row whose document sits on a third party's host
      (THIRD_PARTY_HOSTS). Nothing collected is lost: not_taken.csv holds every such row with its reason.
    - row_kind: "mw" (a megawatt figure, as before) or "wait" (a stated duration of waiting, studying or connecting,
      which may hold no megawatt figure: mw is then empty and quantity_as_written is the duration as written). The
      row check for a wait row is that the duration as written stands in the sentence.
    - page: the PDF page the sentence is on, found by code in the pass (empty for a web page).
    - event_date_basis: "document" when the document states its date; "undated page: the day it was read" for a web
      page that prints no date (event_date is then the retrieval day, and document_date_as_stated is empty).
    - stage_class and stage_class_basis: one of the five STAGES, or "none" (a total across stages, a forecast, a
      figure that is not a stage), or "not classed" (a pilot row whose stage words no pass placed). The class is the
      collecting pass's proposal from the document's own words (stage_class_reason), never a person's review, and it
      is ALWAYS beside the original words (stage_as_worded), never in place of them. stage_vocabulary() writes every
      entity's stage words with their class beside the passes' files (stage_vocabulary.csv), and funnels() says which
      entities' funnels can be placed on the five stages.

Session 151: from forty entities to eighty, and the waits. Eleven more research passes on 8 October 2026 (UTC): eight
(I to P) read forty more utilities and operators, five each, and three (W1 operators and federal bodies, W2 state
regulators, W3 the first forty's own filings) hunted for every public statement of how long a large load waited or
will wait. What changed here:
    - GROUPS names eighty entities (ENTITIES_151 says how the second forty were chosen). OUTSIDE names the bodies that
      state a figure and are not among the eighty (regulators, federal bodies, an association, a joint filing, two
      customers speaking about a utility): their rows are taken, each under the body that states it, and entity_list
      says "outside the eighty", so that no count of the eighty holds them.
    - Every row of the eleven passes is proved again here against the pass's saved text before it is taken (proved():
      the sentence a literal substring of the text of the saved document, on the page the row gives). A row that does
      not prove is not taken and is listed in not_taken.csv.
    - A statement collected by two passes is one row. The same sentence from the same document under two names of one
      entity is taken from the later pass, as before; a sentence that an earlier session already holds (the same
      document, page and figure, the words the same once digits are set aside) stays as held, so no row of the table
      changes its id.
    - A PDF that prints no date is filed on the day it was read, as session 141 filed an undated web page, and
      event_date_basis says "undated document: the day it was read" (a process guide or a one-page timetable often
      prints none, and those hold the waits).
    - A document read from a third party's copy (COPY_HOSTS: a city's copy of a utility's letter, a conference host's
      copy of a deck, a university's) is kept and flagged in source_flag. Session 141's rule for its own rows stands
      (THIRD_PARTY_HOSTS and rows marked CAUTION are not taken) until a person rules on them.
    - Seven columns (NEW_151). entity_list. source_flag: a third party's copy; a statement about another entity; an
      address that holds a filer's e-mail address as a folder name (the Kentucky commission's own public addresses).
      For wait rows: wait_basis (measured, what happened with no duration written, general statement, expected);
      load_scope (large loads, or "all distribution projects, not large loads" for the California energization
      reports); wait_counted (yes, or "no: " and why, for a generation or equipment lead time, a regulator's approval
      time, a rate or a difference: such a row is kept as written, classed none, and never counted as a load's wait);
      wait_figure and wait_figure_holder (below).
    - A distinct wait figure is one duration as written, about one entity, on one stage class, for one kind of load
      (duration_key() says what "as written" sets aside: letter case, "approximately", a number in words); a duration
      that is not a load's wait is a figure of its own. The same figure in two documents, two passes or two bodies'
      words counts once; it is counted under the row that held it first (wait_figure_holder yes). The count is on
      the low side by its rule: an entity that gives the same duration for two steps of one stage class (thirty days
      to apply and thirty to scope) states one figure. wait_counts() counts them; wait_figures.csv lists them beside
      the passes' files.

License: internal. The sentences are quoted from public filings, releases, presentations and operator reports, each
under its publisher's own terms, which were not read one by one in the pilot; the table is a research instrument and
is held internal until a person rules on each publisher.

    python warehouse/connectors/large_load_statements.py                 # writes the table: needs the data lock
    python warehouse/connectors/large_load_statements.py --out-dir DIR   # a trial run: the table under DIR
    python warehouse/connectors/large_load_statements.py --out-dir DIR --raw-root RAW   # the passes' files under RAW
"""

import argparse
import csv
import hashlib
import os
import re
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import iso_prices as ip  # noqa: E402

NAME = "large_load_statements"
SOURCE = "erw:large_load_pilot"
RAW = os.path.join(ROOT, "warehouse", "raw", "large_load_pilot")
RAW141 = os.path.join(ROOT, "warehouse", "raw", "large_load_statements")
# the passes: the pilot's two (session 139) and the six of session 141, oldest first (a later pass's copy of a row wins)
PASSES = [("A", RAW), ("B", RAW), ("C", RAW141), ("D", RAW141), ("E", RAW141), ("F", RAW141), ("G", RAW141), ("H", RAW141)]
PASSES_151 = ["I", "J", "K", "L", "M", "N", "O", "P", "W1", "W2", "W3"]   # session 151: eight entity passes, three wait hunts
PASSES += [(p, RAW141) for p in PASSES_151]
HELD_BEFORE_151 = ["A", "B", "C", "D", "E", "F", "G", "H"]
PER_GROUP = None   # session 139 took at most five an entity (the owner asked for 30 to 50 statements); session 141 takes all
PILOT_TEN = ["Dominion Energy Virginia", "Georgia Power (Southern Company)", "Duke Energy", "Entergy", "PJM Interconnection", "Oncor Electric Delivery",
             "CenterPoint Energy Houston Electric", "American Electric Power", "Exelon", "ERCOT"]
ENTITIES_141 = ("Forty, chosen before the search by the pilot's method: the utilities and grid operators believed to report the most datacenter load in public "
                "documents, not a ranking from data (no ranking can be made across stages). The pilot's ten; four more operators and federal or public power "
                "systems with a load queue or large-load process (SPP, California ISO with the California Energy Commission's forecast it relies on, New York ISO, "
                "Bonneville Power Administration); two public power systems with large datacenter load (Tennessee Valley Authority, Omaha Public Power District); "
                "and twenty-four utility groups. MISO is not among them: its own site is never requested while its terms are under review.")
ENTITIES_151 = ("Forty more, chosen before the search by the same method and listed in the session's brief: the next utilities, public power systems, "
                "cooperatives and operators believed to report large load in public documents, five to a pass by region (California and the Northwest; the "
                "Mountain West; the Southwest and Texas; the upper Midwest; the central states and Kentucky; Virginia, Pennsylvania and South Carolina; New "
                "England and New York; Georgia, Florida and Indiana). Not a ranking. MISO is not among them: utilities in its footprint were read from their "
                "own sites and their commissions.")
# the eighty entities (the forty of session 141 first), and the names the passes filed their rows under (a row belongs to the first group one of whose
# names its entity equals or begins with)
GROUPS = {
    "PPL": ["PPL Electric Utilities", "Louisville Gas and Electric Company and Kentucky Utilities Company", "PPL"],
    "FirstEnergy": ["FirstEnergy"],
    "Dominion Energy Virginia": ["Dominion Energy Virginia"],
    "Georgia Power (Southern Company)": ["Georgia Power", "Southern Company traditional electric operating companies"],
    "Duke Energy": ["Duke Energy Carolinas and Duke Energy Progress", "Duke Energy (enterprise", "Duke Energy Florida", "Duke Energy"],
    "Entergy": ["Entergy utility operating companies", "Entergy Arkansas", "Entergy"],
    "PJM Interconnection": ["PJM Interconnection"],
    "Oncor Electric Delivery": ["Oncor Electric Delivery"],
    "CenterPoint Energy Houston Electric": ["CenterPoint Energy Houston Electric"],
    "American Electric Power": ["American Electric Power", "Appalachian Power (AEP)", "Indiana Michigan Power (AEP)", "AEP Ohio", "Kentucky Power (AEP)"],
    "Exelon": ["Exelon", "ComEd (Exelon)", "PECO (Exelon)"],
    "ERCOT": ["ERCOT"],
    "Southwest Power Pool": ["Southwest Power Pool"],
    "California ISO": ["California ISO", "California Energy Commission"],
    "New York ISO": ["New York ISO"],
    "Bonneville Power Administration": ["Bonneville Power Administration"],
    "Tennessee Valley Authority": ["Tennessee Valley Authority"],
    "Omaha Public Power District": ["Omaha Public Power District"],
    "Public Service Enterprise Group": ["Public Service Electric and Gas Company", "PSEG"],
    "AES": ["AES Ohio", "AES Indiana", "AES"],
    "NiSource": ["Northern Indiana Public Service Company", "NiSource"],
    "DTE Energy": ["DTE Electric Company", "DTE Energy"],
    "Xcel Energy": ["Xcel Energy", "Public Service Company of Colorado"],
    "Ameren": ["Ameren Missouri", "Ameren Illinois", "Ameren"],
    "Evergy": ["Evergy"],
    "WEC Energy Group": ["WEC Energy Group"],
    "Alliant Energy": ["Alliant Energy", "Interstate Power and Light", "Wisconsin Power and Light"],
    "CMS Energy": ["Consumers Energy", "CMS Energy"],
    "Arizona Public Service": ["Arizona Public Service"],
    "Salt River Project": ["Salt River Project"],
    "Tucson Electric Power": ["Tucson Electric Power"],
    "NV Energy": ["NV Energy"],
    "PacifiCorp": ["PacifiCorp"],
    "Idaho Power": ["Idaho Power"],
    "Portland General Electric": ["Portland General Electric"],
    "Pacific Gas and Electric": ["Pacific Gas and Electric"],
    "NextEra Energy (Florida Power & Light)": ["Florida Power & Light", "NextEra Energy"],
    "CPS Energy": ["CPS Energy"],
    "OGE Energy": ["OGE Energy", "Oklahoma Gas and Electric"],
    "Black Hills Corporation": ["Black Hills Corporation"],
    # session 151, pass I
    "Southern California Edison": ["Southern California Edison"],
    "San Diego Gas & Electric": ["San Diego Gas & Electric"],
    "Los Angeles Department of Water and Power": ["Los Angeles Department of Water and Power"],
    "Sacramento Municipal Utility District": ["Sacramento Municipal Utility District"],
    "Grant County Public Utility District": ["Grant County Public Utility District"],
    # pass J
    "Puget Sound Energy": ["Puget Sound Energy"],
    "Avista": ["Avista"],
    "NorthWestern Energy": ["NorthWestern Energy"],
    "Tri-State Generation and Transmission Association": ["Tri-State Generation and Transmission Association"],
    "Colorado Springs Utilities": ["Colorado Springs Utilities"],
    # pass K
    "El Paso Electric": ["El Paso Electric"],
    "TXNM Energy": ["Public Service Company of New Mexico", "Texas-New Mexico Power", "TXNM Energy"],
    "Austin Energy": ["Austin Energy"],
    "Lower Colorado River Authority": ["LCRA Transmission Services Corporation", "Lower Colorado River Authority"],
    "Western Farmers Electric Cooperative": ["Western Farmers Electric Cooperative"],
    # pass L
    "Basin Electric Power Cooperative": ["Basin Electric Power Cooperative"],
    "Great River Energy": ["Great River Energy"],
    "Otter Tail Power": ["Otter Tail Power"],
    "Minnesota Power (ALLETE)": ["Minnesota Power"],
    "MidAmerican Energy": ["MidAmerican Energy"],
    # pass M
    "Associated Electric Cooperative": ["Associated Electric Cooperative"],
    "Nebraska Public Power District": ["Nebraska Public Power District"],
    "Cleco": ["Cleco"],
    "East Kentucky Power Cooperative": ["East Kentucky Power Cooperative"],
    "Big Rivers Electric Corporation": ["Big Rivers Electric Corporation"],
    # pass N
    "Northern Virginia Electric Cooperative": ["Northern Virginia Electric Cooperative"],
    "Rappahannock Electric Cooperative": ["Rappahannock Electric Cooperative"],
    "Old Dominion Electric Cooperative": ["Old Dominion Electric Cooperative"],
    "Duquesne Light": ["Duquesne Light"],
    "Santee Cooper": ["Santee Cooper"],
    # pass O
    "ISO New England": ["ISO New England"],
    "Eversource Energy": ["Eversource Energy"],
    "National Grid": ["National Grid"],
    "Consolidated Edison": ["Consolidated Edison"],
    "Avangrid": ["Avangrid"],
    # pass P
    "Oglethorpe Power Corporation": ["Oglethorpe Power Corporation"],
    "Tampa Electric": ["Tampa Electric"],
    "JEA": ["JEA"],
    "Hoosier Energy": ["Hoosier Energy"],
    "Wabash Valley Power Alliance": ["Wabash Valley Power Alliance"],
}
FORTY_141 = list(GROUPS)[:40]
# session 151: bodies that state a figure and are not among the eighty. A row of theirs is taken under the body that
# states it; entity_list says "outside the eighty" and no count of the eighty holds it.
OUTSIDE = {
    "Federal Energy Regulatory Commission": ["Federal Energy Regulatory Commission"],
    "National Laboratory of the Rockies": ["National Laboratory of the Rockies"],
    "Pacific Northwest National Laboratory": ["Pacific Northwest National Laboratory"],
    "Congressional Research Service": ["Congressional Research Service"],
    "California Public Utilities Commission": ["California Public Utilities Commission"],
    "Public Utility Commission of Texas": ["Public Utility Commission of Texas"],
    "Pennsylvania Public Utility Commission": ["Pennsylvania Public Utility Commission"],
    "Maryland Public Service Commission": ["Maryland Public Service Commission"],
    "Louisiana Public Service Commission": ["Louisiana Public Service Commission"],
    "Nebraska Power Association": ["Nebraska Power Association"],
    "Joint Utilities of New York": ["Joint Utilities of New York"],
    "Google LLC (about Dominion Energy Virginia)": ["Google LLC"],
    "Amazon Data Services (about Dominion Energy Virginia)": ["Amazon Data Services"],
}
ALL_GROUPS = list(GROUPS) + list(OUTSIDE)
# a document on one of these hosts is a third party's copy of a publisher's document: its rows are not taken
THIRD_PARTY_HOSTS = {"protectpwc.org", "www.protectpwc.org", "ceae.ku.edu"}
# session 151: a third party's copy that is kept and flagged (source_flag), by the session's ruling for its own passes
COPY_HOSTS = {
    "hermantownmn.com": "the addressee's copy (a city) of the utility's letter",
    "mrec.org": "a conference host's copy of the utility's presentation",
    "wp.ece.uw.edu": "a university's copy of the utility's presentation",
    "www.spotsylvania.va.us": "a county's copy of the cooperative's form",
}
# the California utilities' reports under the commission's energization rulemaking (R.24-01-018) and the commission's own
# targets for it: every distribution line and service extension of any size, not large loads (address endings)
ALL_DISTRIBUTION_DOCS = ("604030059.pdf", "sdge%20biannual%20energization%20report.pdf", "604023792.pdf", "618-energization-timelines-workshop-slides.pdf")
ALL_DISTRIBUTION = "all distribution projects, not large loads"
LARGE_LOADS = "large loads (or every load at transmission voltage: the notes say which)"
# wait rows that are not a load's wait: (the entity's name begins with, the duration as written or None for any, words
# in the stage as worded, the kind). Such a row is kept as written, classed none, and never counted as a load's wait.
LEAD_TIME = "a generation or equipment lead time"
APPROVAL = "a regulator's approval time"
RATE = "a rate, an interval or a difference, not a duration"
NOT_A_LOADS_WAIT = [
    ("El Paso Electric", "exceeding 2 to 3 years", "phase 3", LEAD_TIME),
    ("El Paso Electric", "over two to three years", "generation to serve", LEAD_TIME),
    ("El Paso Electric", "within 18 months", "commissioning of generation", LEAD_TIME),
    ("Austin Energy", "3-5 years", "building generation", LEAD_TIME),
    ("Basin Electric Power Cooperative", "7 years", "power plants", LEAD_TIME),
    ("NV Energy", "four years", "", LEAD_TIME),
    ("Public Service Company of New Mexico", "up to 15 months", "ccn approval", APPROVAL),
    ("California Public Utilities Commission", None, "exceptional case", APPROVAL),
    ("California Public Utilities Commission", None, "electric rule 30", APPROVAL),
    ("Pacific Gas and Electric", None, "exceptional case", APPROVAL),
    ("Pacific Gas and Electric", None, "tier 3 advice", APPROVAL),
    ("Pacific Gas and Electric", None, "post-pes report", APPROVAL),
    ("Louisiana Public Service Commission", None, "", APPROVAL),
    ("FirstEnergy", "12-18 months", "siting application", APPROVAL),
    ("Rappahannock Electric Cooperative", "one batch per year", "", RATE),
    ("Rappahannock Electric Cooperative", "every 3 years", "", RATE),
    ("Dominion Energy Virginia", "approximately three years", "campus-style", RATE),
    ("Congressional Research Service", "several years longer", "", RATE),
]
# a body's row that states another entity's figure: (the stating entity's name begins with, the duration as written or
# None for any, the entity group the figure is about). The figure is joined with that entity's own where it holds it.
ABOUT = [
    ("Federal Energy Regulatory Commission", "approximately nine months", "New York ISO"),
    ("Federal Energy Regulatory Commission", "90 calendar days", "Southwest Power Pool"),
    ("National Grid", "approximately nine months", "New York ISO"),
    ("California Public Utilities Commission", "18-22 months", "Pacific Gas and Electric"),
    ("California Public Utilities Commission", "2-5 months", "Pacific Gas and Electric"),
    ("Google LLC", None, "Dominion Energy Virginia"),
    ("Amazon Data Services", None, "Dominion Energy Virginia"),
]
# wait rows that say what happened and write no duration (a date, "for years")
NO_DURATION = [("Texas-New Mexico Power", "years"), ("Bonneville Power Administration", "since August 2024"), ("Pacific Gas and Electric", "filed ")]
# wait rows whose basis the notes' first words do not settle, read here (the reason is in the session's report)
BASIS_READ = [
    ("California Public Utilities Commission", "18-22 months", "general statement"),   # "PG&E states has historically taken": the utility's own filing gives it as the total of a table of estimates
    ("Duquesne Light", "six-month", "general statement"),                              # "in some cases": no count
    ("PECO", "approximately eighteen months", "general statement"),                    # "PECO's own experience and that of its affiliates": no count
]
BASES = ["measured", "what happened, no duration written", "general statement", "expected"]
# the five stages a statement's own stage words are placed on, beside those words and never in place of them
STAGES = {
    "1 request or inquiry": "the customer has asked or inquired; nothing has been studied and no money is committed",
    "2 study or engineering": "a study is under way or done (feasibility, system impact, facilities), or an engineering letter or study agreement is signed",
    "3 financial commitment": "the customer has committed money short of a service agreement: a construction letter, a deposit or collateral, a reimbursement "
                              "or procurement agreement, an equipment reservation",
    "4 signed service agreement": "an electric service agreement or contract for service is signed",
    "5 under construction or energized": "construction has started, or the load is in service or ramping",
}
NOT_A_STAGE = "none"
EVENTS = ["event_id", "event_date", "event_type", "parties", "entity_ids", "mw", "price", "currency", "status", "source", "source_url"]
EXTRA = ["entity_group", "entity", "entity_type", "parent_company", "document_title", "document_type", "document_date_as_stated", "page_or_slide",
         "quantity_as_written", "mw_low", "mw_high", "stage_as_worded", "load_type_as_worded", "place_as_worded", "time_horizon_as_worded",
         "wait_or_lead_time_as_worded", "sentence", "collected_in", "retrieved_at", "notes",
         "page", "row_kind", "stage_class", "stage_class_basis", "event_date_basis", "terms_url",   # session 141
         "entity_list", "source_flag", "wait_basis", "load_scope", "wait_counted", "wait_figure", "wait_figure_holder"]   # session 151
COLS = EVENTS + EXTRA
NUMBER = re.compile(r"\d[\d,]*(?:\.\d+)?")


def group_of(entity):
    for g, names in list(GROUPS.items()) + list(OUTSIDE.items()):
        if any(entity == n or entity.startswith(n) for n in names):
            return g
    return None


def norm(s):
    return " ".join(str(s).split())


def figure_in_sentence(row):
    """Whether the row's own figure stands in its sentence: each number of quantity_as_written is in the sentence. A
    wait row (session 141) states a duration, which may be in words ("several years"): its test is that the duration
    as written stands in the sentence, letter case and line-break hyphens aside."""
    if row.get("row_kind") == "wait":
        q = norm(row["quantity_as_written"]).lower()
        s = norm(row["sentence"]).lower()
        return bool(q) and (q in s or q.replace("-", "") in s.replace("-", ""))
    s = norm(row["sentence"]).replace(",", "")
    nums = [n.replace(",", "") for n in NUMBER.findall(row["quantity_as_written"])]
    return bool(nums) and all(n in s for n in nums)


def read_pass(letter, base=RAW):
    path = os.path.join(base, letter, "statements.csv")
    with open(path, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r["collected_in"] = f"pass {letter}"
        r.setdefault("row_kind", "mw")
        for k in ("page", "stage_class_proposed", "stage_class_reason", "terms_url"):
            r.setdefault(k, "")
    return rows


def read_stages(letter, base=RAW141):
    """A pass's stages.csv: the stage words each entity uses, in its own order, with the document's definition where
    it gives one. [] for a pass that wrote none (the pilot's)."""
    path = os.path.join(base, letter, "stages.csv")
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r["collected_in"] = f"pass {letter}"
    return rows


def host_of(url):
    m = re.match(r"^https?://([^/]+)", url or "")
    return m.group(1).lower() if m else ""


def url_key(url):
    """An address for comparing: lower case, and without the braces some sites print round an identifier."""
    return re.sub(r"[{}]|%7b|%7d", "", (url or "").strip().lower())


EMAIL_IN_URL = re.compile(r"[\w.+-]+(?:%40|@)[\w-]+(?:\.[\w-]+)+", re.I)
FF = chr(12)
LINE_NUMBER = re.compile(r"^\s*\d{1,2}(\s+|$)")


def texts_of(base, letter, row):
    """The saved text files of a row's document, under the pass's text/: the one its notes name first, then every
    file whose name begins with the local file's folder and name (a pass keeps more than one extraction)."""
    tdir = os.path.join(base, letter, "text")
    out = []
    for m in re.finditer(r"warehouse/raw/[^\s()]*?/text/([^\s()]+)", row.get("notes", "")):
        n = m.group(1).rstrip(".")
        if os.path.exists(os.path.join(tdir, n)) and n not in out:
            out.append(n)
    m2 = re.search(r".*/%s/raw/(.+)$" % re.escape(letter), row.get("local_file", "").replace("\\", "/"))
    if m2 and os.path.isdir(tdir):
        stem = m2.group(1).replace("/", "__")
        out += [n for n in sorted(os.listdir(tdir)) if n.startswith(stem) and n not in out]
    return [os.path.join(tdir, n) for n in out]


def proved(row, base, letter, cache):
    """Session 151: a pass's row checked again against the pass's saved text, apart from the pass's own script. The
    sentence, white space normalized, is a literal substring of the text of the saved document; where the row gives a
    page, that page of the text (pages split at form feeds) holds it; where testimony prints a line number at the
    start of each line and the pass saved no copy without them, the same page with those numbers removed. Returns
    (the reasons it does not prove, [] when it does; how it was proved)."""
    sent = norm(row.get("sentence", ""))
    if not sent:
        return ["no sentence"], ""
    files = texts_of(base, letter, row)
    if not files:
        return ["no saved text for the row's document"], ""
    pg = row.get("page", "").strip()
    found = False
    for path in files:
        if path not in cache:
            with open(path, encoding="utf-8", errors="replace") as f:
                raw = f.read()
            cache[path] = (norm(raw), raw.split(FF) if FF in raw else None)
        whole, pages = cache[path]
        if sent in whole:
            found = True
            if not pg or (pages is not None and pg.isdigit() and 1 <= int(pg) <= len(pages) and sent in norm(pages[int(pg) - 1])):
                return [], "the saved text"
    if found:
        return ["the sentence is not on the page the row gives (page %s)" % pg], ""
    for path in files:   # line-numbered testimony: the page with the numbers at the start of each line removed
        pages = cache[path][1]
        if pages is not None and pg.isdigit() and 1 <= int(pg) <= len(pages):
            if sent in norm("\n".join(LINE_NUMBER.sub("", ln) for ln in pages[int(pg) - 1].split("\n"))):
                return [], "the page with the line numbers at the start of each line removed"
    return ["the sentence is not a literal substring of the saved text"], ""


def checked(rows, log):
    """The rows that hold what a row must: a sentence, an http address, a document date, verified yes, a figure that
    stands in the sentence. A row that fails is counted and named, never mended."""
    good, bad = [], []
    for r in rows:
        why = []
        if r.get("verified", "").strip().lower() != "yes":
            why.append("not marked verified")
        if not norm(r.get("sentence", "")):
            why.append("no sentence")
        if not r.get("document_url", "").startswith("http"):
            why.append("no address")
        dated = re.match(r"^\d{4}(-\d{2}(-\d{2})?)?$", r.get("document_date", ""))
        # a document that prints no date is filed on the day it was read, and the row says so (to_row). Session 141 allowed that for a web page
        # only; session 151 allows it for a PDF too (a utility's process guide or one-page timetable often prints no date, and those hold the waits)
        undated = not r.get("document_date", "").strip() and re.match(r"^\d{4}-\d{2}-\d{2}", r.get("retrieved_at", ""))
        if not dated and not undated:
            why.append("no document date")
        if not why and not figure_in_sentence(r):
            why.append("the figure as written is not in the sentence")
        (bad if why else good).append((r, why))
    for r, why in bad:
        log(f"  not taken, {'; '.join(why)}: {r.get('entity')}, {r.get('quantity_as_written')}, {r.get('document_title', '')[:60]}")
    return [r for r, _ in good], len(bad)


def size_of(r):
    """A row's megawatts as a number, for ordering only (a range by its upper end)."""
    m = NUMBER.findall(r["mw"].replace(",", ""))
    return float(m[-1]) if m else 0.0


def choose(rows, per_group=PER_GROUP):
    """The rows taken, by the rule in the docstring, and those not taken with the reason. A row of no entity group, a
    row marked CAUTION by its collector and a row whose document sits on a third party's host are not taken. Within an
    entity: newest document first and, among a document's figures, the largest first; a row whose stage, as worded, is
    not yet among those taken before one that repeats a stage. With per_group (session 139: five) only that many an
    entity are taken; without it (session 141) all are, once: a row collected twice (the same entity, address, figure
    and sentence) is taken from the later pass. Returns (taken, not_taken)."""
    taken, left = [], []
    by, seen, nearby = {}, {}, {}
    for r in rows:
        g = group_of(r["entity"])
        why = ("not one of the entities" if g is None else "marked CAUTION by its collector (a third party's words or copy)" if "CAUTION" in r.get("notes", "")
               else "the document sits on a third party's host" if host_of(r.get("document_url", "")) in THIRD_PARTY_HOSTS else "")
        if why:
            r["why_not_taken"] = why
            left.append(r)
            continue
        r["entity_group"] = g
        # session 151: the same sentence of the same document under two names of one entity is one row (the group, not the name, is the key)
        key = (g, url_key(r["document_url"]), norm(r["quantity_as_written"]), norm(r["sentence"]))
        if key in seen and seen[key]["collected_in"] == r["collected_in"] and norm(seen[key]["stage_as_worded"]) != norm(r["stage_as_worded"]):
            key += (norm(r["stage_as_worded"]),)   # one pass, one table row, two lines of it (the same words and figure for two steps): two statements
        if key in seen:
            seen[key]["why_not_taken"] = (f"collected again in {r['collected_in']}: that copy is taken" if seen[key]["collected_in"] != r["collected_in"] else
                                          f"the same sentence, figure and stage words as another row of {r['collected_in']} (one table row quoted for two of its lines): held once")
            left.append(seen[key])
            by[g].remove(seen[key])
        # session 151: a statement an earlier pass holds (the same document, page and figure; the words the same once digits are
        # set aside, or one cut holding the other) stays as held, so that a row of the table keeps its id
        near = (url_key(r["document_url"]), r.get("page", "").strip(), norm(r["quantity_as_written"]).lower())
        bare = re.sub(r"[\d\s]", "", norm(r["sentence"]).lower())
        held = next((o for o, b in nearby.get(near, []) if o["collected_in"] != r["collected_in"] and key not in seen and (bare in b or b in bare)), None)
        if held is not None:
            r["why_not_taken"] = f"held already from {held['collected_in']} (the same document, page and figure)"
            left.append(r)
            continue
        nearby.setdefault(near, []).append((r, bare))
        seen[key] = r
        by.setdefault(g, []).append(r)
    for g in ALL_GROUPS:
        cand = sorted(by.get(g, []), key=lambda r: (r["document_date"], size_of(r), r["document_url"], r["sentence"], r["quantity_as_written"]), reverse=True)
        if per_group is None:
            taken += cand
            continue
        picked, stages = [], set()
        for r in cand:  # a stage not yet taken first
            if len(picked) < per_group and norm(r["stage_as_worded"]).lower() not in stages:
                picked.append(r)
                stages.add(norm(r["stage_as_worded"]).lower())
        for r in cand:
            if len(picked) < per_group and r not in picked:
                picked.append(r)
        taken += picked
        for r in cand:
            if r not in picked:
                r["why_not_taken"] = f"the entity's {per_group} statements were already taken (newer, or a stage not yet held)"
                left.append(r)
    return taken, left


def class_of(text):
    """A proposed class as one of STAGES, NOT_A_STAGE, or "" when nothing was proposed."""
    t = norm(text).lower()
    for k in STAGES:
        if t == k or t.startswith(k[:1] + " "):
            return k
    return NOT_A_STAGE if t.startswith("none") else ""


def stage_vocabulary(stage_rows):
    """Every entity's stage words with the class they are placed on, the original words kept: one row per (entity
    group, entity, stage as worded). basis: "the document defines the stage" when the pass recorded the document's own
    definition, else "the stage's own words"."""
    out, seen = [], set()
    for r in stage_rows:
        g = group_of(r["entity"])
        key = (g, r["entity"], norm(r["stage_as_worded"]).lower())
        if g is None or key in seen:
            continue
        seen.add(key)
        cls = class_of(r.get("stage_class_proposed", "")) or NOT_A_STAGE
        try:
            order = int(float(r.get("funnel_order") or 0))
        except ValueError:
            order = 0
        out.append(dict(entity_group=g, entity=r["entity"], funnel_order=order, stage_as_worded=norm(r["stage_as_worded"]), stage_class=cls,
                        stage_class_basis="the document defines the stage" if norm(r.get("definition_as_worded", "")) else "the stage's own words",
                        stage_class_reason=norm(r.get("stage_class_reason", "")), definition_as_worded=norm(r.get("definition_as_worded", "")),
                        definition_document_url=r.get("definition_document_url", ""), definition_page=r.get("definition_page", ""), collected_in=r["collected_in"]))
    out.sort(key=lambda r: (ALL_GROUPS.index(r["entity_group"]), r["entity"], r["funnel_order"], r["stage_as_worded"]))
    return out


def funnels(vocab):
    """Which entity groups' funnels can be placed on the five stages. For each group, over its stage words in each
    entity's own order: placed = the words on one of the five stages; a funnel is "placed" when at least two different
    stages are held and no entity's own order runs against the stages' order, "placed in part" when that holds but
    some of its stage words are on none, "one stage only" with a single stage, "not placed" otherwise (no stage words,
    none on a stage, or an order that runs against the stages)."""
    out = {}
    for g in GROUPS:
        rows = [r for r in vocab if r["entity_group"] == g]
        staged = [r for r in rows if r["stage_class"] in STAGES]
        classes = sorted({r["stage_class"] for r in staged})
        against = False
        for e in {(r["entity"], r["collected_in"]) for r in staged}:   # session 151: an order is one pass's reading of one entity's documents
            seq = [int(r["stage_class"][0]) for r in sorted((r for r in staged if (r["entity"], r["collected_in"]) == e), key=lambda r: r["funnel_order"]) if r["funnel_order"]]
            against = against or any(b < a for a, b in zip(seq, seq[1:]))
        verdict = ("not placed" if not staged or against else "one stage only" if len(classes) < 2 else "placed" if len(staged) == len(rows) else "placed in part")
        out[g] = dict(stage_words=len(rows), on_a_stage=len(staged), stages=[c[0] for c in classes], against_order=against, verdict=verdict)
    return out


NUMBER_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
                "fifteen": 15, "eighteen": 18, "twenty": 20, "thirty": 30}


def duration_key(q):
    """A duration as written, for telling whether two rows state the same figure. Set aside: letter case; the words
    approximately, about, around, roughly, typically, within, estimated and calendar; a number in words up to twelve
    (and fifteen, eighteen, twenty, thirty) against the same number in digits, and a number in words followed by its
    digits in brackets; "to" or a short dash between two numbers; singular against plural of the unit. Kept: the
    numbers, the unit, "business", and every bound (up to, at least, over, more than, +). Nothing is converted: 180
    days and six months are two figures."""
    t = norm(q).lower().replace(chr(0x2013), "-").replace("~", "")
    t = re.sub(r"\b(?:(?:%s|hundred|eighty|and)[ -]?)+\((\d+)\)" % "|".join(NUMBER_WORDS), r"\1", t)
    t = re.sub(r"\((?:estimated)\)", "", t)
    t = re.sub(r"\b(approximately|about|around|roughly|typically|within|estimated|calendar)\b", " ", t)
    t = re.sub(r"\b(%s)\b" % "|".join(NUMBER_WORDS), lambda m: str(NUMBER_WORDS[m.group(1)]), t)
    t = re.sub(r"(\d)\s*(?:-|\bto\b)\s*(\d)", r"\1-\2", t)
    t = re.sub(r"(\d)-(day|week|month|year)", r"\1 \2", t)
    t = re.sub(r"\b(day|week|month|year)s\b", r"\1", t)
    return norm(t)


def basis_of(r):
    """A wait row's basis, one of BASES. BASIS_READ and NO_DURATION first; then the collecting pass's own word:
    measured when the row's notes begin with it (and do not take it back: "measured only loosely", "in words", "in
    the sense"); a general statement when the notes call it one; otherwise expected (a target, a deadline, a
    plan, an estimate, an assumption)."""
    ent, q = r["entity"], norm(r["quantity_as_written"])
    for e, d, b in BASIS_READ:
        if ent.startswith(e) and q.startswith(d):
            return b
    for e, d in NO_DURATION:
        if ent.startswith(e) and q.startswith(d):
            return BASES[1]
    low = norm(r.get("notes", "")).lower()
    if re.match(r"measured\b(?! only| in words| in the sense)", low):
        return BASES[0]
    if any(w in low for w in ("general statement", "general experience", "statement of experience", "stated as experience", "measured only loosely", "measured in words")):
        return BASES[2]
    return BASES[3]


def not_a_loads_wait(r):
    """The kind (LEAD_TIME, APPROVAL, RATE) of a wait row that is not a load's wait, or ""."""
    ent, q, stage = r["entity"], norm(r["quantity_as_written"]), norm(r["stage_as_worded"]).lower()
    for e, d, words, kind in NOT_A_LOADS_WAIT:
        if ent.startswith(e) and (d is None or q == d) and words in stage:
            return kind
    return ""


def about_of(r):
    """The entity group a row's figure is about: its own, unless ABOUT names another."""
    q = norm(r["quantity_as_written"])
    for e, d, g in ABOUT:
        if r["entity"].startswith(e) and (d is None or q == d):
            return g
    return r["entity_group"]


def source_flags(r):
    host = host_of(r.get("document_url", ""))
    flags = []
    if host in COPY_HOSTS:
        flags.append(f"a third party's copy: {COPY_HOSTS[host]} ({host})")
    if about_of(r) != r["entity_group"]:
        flags.append(f"a statement about another entity: {about_of(r)}")
    if norm(r.get("notes", "")).startswith("The words are those of a site profile"):
        flags.append("another body's words, filed by the entity as its exhibit")
    if EMAIL_IN_URL.search(r.get("document_url", "")):
        flags.append("the address holds a filer's e-mail address as a folder name (the commission's own public address)")
    return "; ".join(flags)


def to_row(r, retrieved, vocab_class=None):
    mw_text = r["mw"].strip()
    rng = re.match(r"^(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)$", mw_text)
    date = r["document_date"].strip()
    basis = "document"
    if not date:   # a web page that prints no date: filed on the day it was read, and said so
        date, basis = (r.get("retrieved_at") or retrieved)[:10], ("undated document" if r.get("page", "").strip() else "undated page") + ": the day it was read"
    stated = r["document_date"].strip()
    cls = class_of(r.get("stage_class_proposed", ""))
    cls_basis = "the collecting pass's reading of the document's words: " + norm(r.get("stage_class_reason", "")) if cls else ""
    if not cls and vocab_class:   # a pilot row: placed by its entity's stage words where a later pass placed them
        cls = vocab_class.get((r.get("entity_group"), norm(r["stage_as_worded"]).lower()), "")
        cls_basis = "the same stage words of this entity, placed by a later pass" if cls else ""
    wait = (r.get("row_kind") or "mw") == "wait"
    kind = not_a_loads_wait(r) if wait else ""
    if kind:   # kept as written, classed none, never counted as a load's wait
        cls_basis = f"session 151: {kind}, not a step of a load's wait (the collecting pass proposed: {cls or 'nothing'})"
        cls = NOT_A_STAGE
    scope = "" if not wait else ALL_DISTRIBUTION if url_key(r["document_url"]).endswith(ALL_DISTRIBUTION_DOCS) else LARGE_LOADS
    figure = "" if not wait else " | ".join([about_of(r), duration_key(r["quantity_as_written"]), (cls or "not classed")[:1] if cls in STAGES else (cls or "not classed"),
                                             "all distribution" if scope == ALL_DISTRIBUTION else "large loads"] + (["not a load's wait"] if kind else []))
    key = "|".join([r["entity"], r["document_url"], norm(r["sentence"]), r["quantity_as_written"], r["stage_as_worded"]])
    return {
        "event_id": "llstmt:" + hashlib.sha1(key.encode("utf-8")).hexdigest()[:16],
        "event_date": date if len(date) == 10 else f"{date}-01" if len(date) == 7 else f"{date}-01-01", "event_type": "large_load_statement",
        "parties": r["entity"], "entity_ids": "", "mw": "" if rng or not mw_text else float(mw_text), "price": "", "currency": "",
        "status": norm(r["stage_as_worded"]), "source": SOURCE, "source_url": r["document_url"],
        "entity_group": r["entity_group"], "entity": r["entity"], "entity_type": r["entity_type"], "parent_company": r["parent_company"],
        "document_title": norm(r["document_title"]), "document_type": r["document_type"], "document_date_as_stated": stated,
        "page_or_slide": r["page_or_slide"], "quantity_as_written": r["quantity_as_written"],
        "mw_low": float(rng.group(1)) if rng else "", "mw_high": float(rng.group(2)) if rng else "",
        "stage_as_worded": norm(r["stage_as_worded"]), "load_type_as_worded": norm(r["load_type_as_worded"]), "place_as_worded": norm(r["place_as_worded"]),
        "time_horizon_as_worded": norm(r["time_horizon_as_worded"]), "wait_or_lead_time_as_worded": norm(r["wait_or_lead_time_as_worded"]),
        "sentence": norm(r["sentence"]), "collected_in": r["collected_in"], "retrieved_at": r["retrieved_at"] or retrieved, "notes": norm(r["notes"]),
        "page": r.get("page", ""), "row_kind": r.get("row_kind") or "mw", "stage_class": cls or "not classed", "stage_class_basis": cls_basis,
        "event_date_basis": basis, "terms_url": r.get("terms_url", ""),
        "entity_list": "the eighty" if r["entity_group"] in GROUPS else "outside the eighty", "source_flag": source_flags(r),
        "wait_basis": basis_of(r) if wait else "", "load_scope": scope, "wait_counted": "" if not wait else f"no: {kind}" if kind else "yes",
        "wait_figure": figure, "wait_figure_holder": "",
    }


def pass_order(collected_in):
    letters = [p for p, _ in PASSES]
    letter = str(collected_in).replace("pass ", "")
    return letters.index(letter) if letter in letters else len(letters)


def mark_holders(out):
    """Each distinct wait figure is counted under one row, the holder: the row of the earliest pass (a figure held
    before stays under the row that held it), and among rows of one pass the entity the figure is about."""
    wait = out[out["row_kind"] == "wait"]
    for fig, rows in wait.groupby("wait_figure"):
        about = fig.split(" | ")[0]
        order = sorted(rows.index, key=lambda i: (pass_order(out.at[i, "collected_in"]), out.at[i, "entity_group"] != about, out.at[i, "event_date"], out.at[i, "event_id"]))
        out.at[order[0], "wait_figure_holder"] = "yes"
    return out


def wait_counts(out):
    """The count of distinct wait figures, from the table alone. One figure is one duration as written, about one
    entity, on one stage class, for one kind of load; the holder row gives its entity, stage, basis and scope. A
    figure is held before when a row of it was collected before session 151. Nothing is added across figures: these
    are counts of statements, never of days."""
    wait = out[out["row_kind"] == "wait"]
    holders = wait[wait["wait_figure_holder"] == "yes"]
    before = set(wait.loc[wait["collected_in"].str.replace("pass ", "").isin(HELD_BEFORE_151), "wait_figure"])
    stage = holders["stage_class"].map(lambda c: c[:1] if c in STAGES else c)
    large = holders[holders["load_scope"] != ALL_DISTRIBUTION]
    counted = large[large["wait_counted"] == "yes"]
    cstage = counted["stage_class"].map(lambda c: c[:1] if c in STAGES else c)
    return {
        "wait_rows": int(len(wait)), "figures": int(len(holders)),
        "held_before": int(holders["wait_figure"].isin(before).sum()), "new": int((~holders["wait_figure"].isin(before)).sum()),
        "by_basis": {b: int((holders["wait_basis"] == b).sum()) for b in BASES},
        "by_stage": {k: int((stage == k).sum()) for k in ["1", "2", "3", "4", "5", NOT_A_STAGE]},
        "by_scope": {"large loads": int(len(large)), "all distribution": int(len(holders) - len(large))},
        "not_a_loads_wait": int((holders["wait_counted"] != "yes").sum()),
        "large_and_counted": int(len(counted)),
        "large_and_counted_by_basis": {b: int((counted["wait_basis"] == b).sum()) for b in BASES},
        "large_and_counted_by_stage": {k: int((cstage == k).sum()) for k in ["1", "2", "3", "4", "5", NOT_A_STAGE]},
        "measured_large": int(((large["wait_basis"] == BASES[0])).sum()), "measured_all_distribution": int(((holders["load_scope"] == ALL_DISTRIBUTION) & (holders["wait_basis"] == BASES[0])).sum()),
        "by_list": {k: int((holders["entity_list"] == k).sum()) for k in ("the eighty", "outside the eighty")},
        "entities_of_eighty_with_a_figure": int(holders.loc[holders["entity_list"] == "the eighty", "entity_group"].nunique()),
        "by_entity": holders.groupby("entity_group").size().to_dict(),
    }


NEW_141 = ["page", "row_kind", "stage_class", "stage_class_basis", "event_date_basis", "terms_url"]
NEW_151 = ["entity_list", "source_flag", "wait_basis", "load_scope", "wait_counted", "wait_figure", "wait_figure_holder"]


def migrate_shape(path, log):
    """Session 141 added six columns (NEW_141). The shared writer merges only into a file of the same shape, so the
    table as session 139 wrote it (the same columns without those six) is first rewritten with the six columns empty,
    its header lines and every row as they were; the run that follows then replaces each of its rows by event_id with
    the fuller row. A file of any other shape is left alone, and the writer refuses it as before."""
    if not os.path.exists(path):
        return False
    n = ip.header_rows(path)
    with open(path, encoding="utf-8") as f:
        head = [next(f) for _ in range(n)]
    old = pd.read_csv(path, skiprows=n, dtype=str, keep_default_na=False, na_values=[])
    shape_141 = [c for c in COLS if c not in NEW_151]            # session 151 added seven more: the table as session 141 wrote it
    shape_139 = [c for c in shape_141 if c not in NEW_141]
    if list(old.columns) not in (shape_141, shape_139):
        return False
    added = [c for c in COLS if c not in old.columns]
    for c in added:
        old[c] = ""
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        f.writelines(head)
        old[COLS].to_csv(f, index=False, lineterminator="\n")
    os.replace(tmp, path)
    log(f"  {os.path.basename(path)}: {len(old)} rows of an earlier session's shape rewritten with the {len(added)} columns added since, empty")
    return True


def passes_under(raw_root=None):
    """PASSES, with the passes' folders under raw_root (the directory that holds large_load_pilot and
    large_load_statements) where one is given."""
    return [(letter, os.path.join(raw_root, os.path.basename(base)) if raw_root else base) for letter, base in PASSES]


def build(passes, retrieved, log):
    """The table from the passes' files, with nothing written: each pass read, the passes of session 151 proved again
    against their saved text, the row check, the choice, the stage vocabulary, the rows and the holders of the wait
    figures. Returns the table (out), the rows not taken (left), the vocabulary and the counts a run reports."""
    collected, stage_rows, unproved, read = [], [], [], []
    for letter, base in passes:
        if not os.path.exists(os.path.join(base, letter, "statements.csv")):
            log(f"  pass {letter}: no statements.csv under {base}")
            continue
        mine = read_pass(letter, base)
        read.append(letter)
        if letter in PASSES_151:   # proved again against the pass's saved text before anything is taken
            cache, good, how = {}, [], {}
            for r in mine:
                why, by = proved(r, base, letter, cache)
                if why:
                    r["why_not_taken"] = "not proved again against the pass's saved text: " + "; ".join(why)
                    unproved.append(r)
                    log(f"  pass {letter}: NOT PROVED, {'; '.join(why)}: {r.get('entity')}, {r.get('quantity_as_written')}, {norm(r.get('sentence', ''))[:80]}")
                else:
                    good.append(r)
                    how[by] = how.get(by, 0) + 1
            log(f"  pass {letter}: {len(mine)} rows, {len(good)} proved again ({how}), {len(mine) - len(good)} not")
            mine = good
        collected += mine
        stage_rows += read_stages(letter, base)
    rows, failed = checked(collected, log)
    taken, left = choose(rows)
    left += unproved
    vocab = stage_vocabulary(stage_rows)
    vocab_class = {(v["entity_group"], v["stage_as_worded"].lower()): v["stage_class"] for v in vocab}
    out = pd.DataFrame([to_row(r, retrieved, vocab_class) for r in taken], columns=COLS)
    if out["event_id"].duplicated().any():
        raise SystemExit("two statements share an id: " + ", ".join(out.loc[out["event_id"].duplicated(), "event_id"]))
    out = mark_holders(out)
    return dict(out=out, left=left, vocab=vocab, collected=collected, unproved=unproved, failed=failed, read=read)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Public statements of large load waiting for power, each with its sentence (internal pilot table)")
    ap.add_argument("--out-dir", help="a trial run: the table and its log under this directory; nothing in warehouse/output")
    ap.add_argument("--raw-root", help="the directory that holds large_load_pilot and large_load_statements (default: this copy's warehouse/raw)")
    a = ap.parse_args(argv)
    passes = passes_under(a.raw_root)
    raw141 = os.path.join(a.raw_root, os.path.basename(RAW141)) if a.raw_root else RAW141
    run_id = pd.Timestamp.now(tz="UTC").strftime("%Y%m%dT%H%M%SZ")
    retrieved = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
    if a.out_dir:
        os.makedirs(a.out_dir, exist_ok=True)
        ip.set_out_dir(a.out_dir)
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    log_path = os.path.join(ip.LOG_DIR, f"large_load_statements_{run_id}.log")
    log = ip.Log(log_path)
    b = build(passes, retrieved, log)
    out, left, vocab, collected, unproved, failed, read = (b[k] for k in ("out", "left", "vocab", "collected", "unproved", "failed", "read"))
    counts = wait_counts(out)
    beside = a.out_dir or raw141
    os.makedirs(beside, exist_ok=True)
    with open(os.path.join(beside, "not_taken.csv"), "w", encoding="utf-8", newline="") as f:
        cols = [c for c in collected[0] if c != "entity_group"] + [c for c in ("page", "row_kind", "stage_class_proposed", "stage_class_reason", "terms_url") if c not in collected[0]] + ["why_not_taken"]
        w = csv.DictWriter(f, fieldnames=list(dict.fromkeys(cols)), lineterminator="\n", extrasaction="ignore")
        w.writeheader()
        w.writerows(left)
    with open(os.path.join(beside, "stage_vocabulary.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(vocab[0]) if vocab else ["entity_group"], lineterminator="\n")
        w.writeheader()
        w.writerows(vocab)
    with open(os.path.join(beside, "wait_figures.csv"), "w", encoding="utf-8", newline="") as f:   # session 151: each distinct wait figure, under its holder row
        cols = ["wait_figure", "entity_group", "entity", "entity_list", "quantity_as_written", "stage_class", "status", "wait_basis", "load_scope", "wait_counted",
                "rows", "held_before", "event_date", "document_type", "source_url", "page", "source_flag", "sentence", "collected_in", "event_id"]
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n", extrasaction="ignore")
        w.writeheader()
        waits = out[out["row_kind"] == "wait"]
        for _, h in waits[waits["wait_figure_holder"] == "yes"].iterrows():
            same = waits[waits["wait_figure"] == h["wait_figure"]]
            before = same["collected_in"].str.replace("pass ", "").isin(HELD_BEFORE_151).any()
            w.writerow(dict(h.to_dict(), rows=len(same), held_before="yes" if before else "no"))
    fun = funnels(vocab)
    with open(os.path.join(beside, "funnels.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["entity_group", "statements", "wait_rows", "stage_words", "on_a_stage", "stages", "against_order", "verdict"], lineterminator="\n")
        w.writeheader()
        for g, v in fun.items():
            mine = out[out["entity_group"] == g]
            w.writerow(dict(entity_group=g, statements=len(mine), wait_rows=int((mine["row_kind"] == "wait").sum()), stage_words=v["stage_words"], on_a_stage=v["on_a_stage"],
                            stages=" ".join(v["stages"]), against_order="yes" if v["against_order"] else "no", verdict=v["verdict"]))
    per = out.groupby("entity_group").size().to_dict()
    verdicts = {k: sum(1 for v in fun.values() if v["verdict"] == k) for k in ("placed", "placed in part", "one stage only", "not placed")}
    eighty = out[out["entity_list"] == "the eighty"]
    n_eighty = eighty["entity_group"].nunique()
    log(f"  passes read: {' '.join(read)}")
    log(f"  collected {len(collected) + len(unproved)}, of which {len(unproved)} did not prove again and {failed} failed the row check; taken {len(out)} "
        f"({int((out['row_kind'] == 'wait').sum())} wait rows): {len(eighty)} from {n_eighty} of the {len(GROUPS)} entities and {len(out) - len(eighty)} from "
        f"{out.loc[out['entity_list'] != 'the eighty', 'entity_group'].nunique()} bodies outside them; not taken {len(left)} (not_taken.csv)")
    log(f"  entities of the {len(GROUPS)} with no statement: {', '.join(g for g in GROUPS if g not in set(eighty['entity_group']))}")
    log(f"  distinct wait figures (wait_figures.csv): {counts}")
    flagged = out["source_flag"]
    log(f"  flagged: a third party's copy {int(flagged.str.contains('third party').sum())}; a statement about another entity {int(flagged.str.contains('about another entity').sum())}; "
        f"another body's words filed as an exhibit {int(flagged.str.contains('exhibit').sum())}; an address holding a filer's e-mail address "
        f"{int(flagged.str.contains('e-mail').sum())} ({int((flagged.str.contains('e-mail') & (out['row_kind'] == 'wait')).sum())} of them wait rows; by pass "
        f"{out[flagged.str.contains('e-mail')].groupby('collected_in').size().to_dict()})")
    log(f"  stage vocabulary: {len(vocab)} stage words of {len({v['entity_group'] for v in vocab})} entities (stage_vocabulary.csv); funnels: {verdicts} (funnels.csv)")
    log(f"  by entity: {per}")
    header = [
        "Energy Research Warehouse (ERW): public statements of large load waiting for power, each with the exact sentence it was read from (session 139's pilot of "
        "ten entities, extended to forty in session 141 and to eighty, with a hunt for statements of how long a load waits, in session 151)",
        "Shape: events (docs/datastandard.md v0), event_type large_load_statement; one row per figure as a document states it. event_date: the document's date "
        "(a document dated to a month or a year only: its first day; document_date_as_stated holds what it states; a web page that prints no date: the day it "
        "was read, and event_date_basis says so). status: the stage in the document's own words.",
        f"Retrieved: {run_id} (UTC) by warehouse/connectors/large_load_statements.py from the research passes of 7 and 8 October 2026 "
        f"(warehouse/raw/large_load_pilot/A and B, warehouse/raw/large_load_statements/C to P and W1 to W3; read in this run: {' '.join(read)}: statements, rejects, "
        "documents opened, timing, stage words, notes, the documents as downloaded and the checking scripts)",
        f"Run log: warehouse/output/logs/large_load_statements_{run_id}.log",
        f"Source: {SOURCE}: each row's source_url is the utility's or operator's own document (or the copy a commission, the SEC or an operator posts); "
        "document_title, document_type, page_or_slide and page say which and where",
        f"This run: {len(collected) + len(unproved)} statements collected and verified by the passes, {len(out)} taken: {len(eighty)} from {n_eighty} of the "
        f"{len(GROUPS)} entities and {len(out) - len(eighty)} from bodies outside them that state a figure (entity_list); {int((out['row_kind'] == 'wait').sum())} "
        f"of them state a duration (row_kind wait), {counts['figures']} distinct wait figures (wait_figure, counted under wait_figure_holder yes); {len(left)} kept "
        "beside the passes' files and not in this table.",
        "Wait rows: wait_basis says measured, what happened with no duration written, general statement, or expected; load_scope says where a figure covers every "
        "distribution project and not large loads; wait_counted says no where the duration is a generation or equipment lead time, a regulator's approval time, or a "
        "rate, which is never a load's wait. source_flag marks a third party's copy, a statement about another entity, and an address that holds a filer's e-mail "
        "address as a folder name. A count of wait figures is a count of statements: durations are never added or averaged across rows.",
        "No number without its sentence: sentence is a literal substring of the document's extracted text, checked by code in each pass, and the figure as "
        "written stands in it. mw is quantity_as_written in MW; a range is in mw_low and mw_high with mw empty; a wait row's mw is empty.",
        "DO NOT SUM across rows or entities: the entities count differently (requests, studies, letters, contracts, forecasts), a document often states a total "
        "and its parts, two documents may state one quantity, and an operator's figures hold its utilities'. The stage is each document's own wording; "
        "stage_class places it on one of five stages (or none) beside those words, by the collecting pass's reading, not a person's review.",
        "License: internal. Quoted from public documents under each publisher's own terms, not read one by one; held internal until a person rules. "
        "Not on the site, not in the public Redivis dataset, not in the live set.",
    ]
    migrate_shape(os.path.join(ip.OUT_DIR, f"{NAME}.csv"), log)
    ip.write_csv(out, NAME, header, lambda m: log(m.strip()), cols=COLS, key=["event_id"], time_col="event_date")
    if not a.out_dir:
        ip.update_sources([{"source": SOURCE, "publisher": "Energy Research Warehouse (ERW), collected from utilities' and grid operators' public documents by an AI research agent, each sentence checked by code",
                            "report": "Large load statements, 7 and 8 October 2026: eighty utilities and operators (the pilot's ten, session 139; thirty more, "
                                      "session 141; forty more and a hunt for statements of how long a load waits, session 151), each statement with its "
                                      "sentence (docs/accelerator/large_load_pilot.md, docs/accelerator/large_load_forty.md, "
                                      "docs/accelerator/large_load_eighty.md). The publishers' own terms were not read one by one: held internal",
                            "report_url": "https://github.com/SamuelEnrique/erw/blob/main/docs/accelerator/large_load_pilot.md", "document_list": "",
                            "license": "internal", "tables": [NAME]}])
    return 0


if __name__ == "__main__":
    sys.exit(main())
