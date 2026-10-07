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

License: internal. The sentences are quoted from public filings, releases, presentations and operator reports, each
under its publisher's own terms, which were not read one by one in the pilot; the table is a research instrument and
is held internal until a person rules on each publisher.

    python warehouse/connectors/large_load_statements.py                 # writes the table: needs the data lock
    python warehouse/connectors/large_load_statements.py --out-dir DIR   # a trial run: the table under DIR
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
PER_GROUP = None   # session 139 took at most five an entity (the owner asked for 30 to 50 statements); session 141 takes all
PILOT_TEN = ["Dominion Energy Virginia", "Georgia Power (Southern Company)", "Duke Energy", "Entergy", "PJM Interconnection", "Oncor Electric Delivery",
             "CenterPoint Energy Houston Electric", "American Electric Power", "Exelon", "ERCOT"]
ENTITIES_141 = ("Forty, chosen before the search by the pilot's method: the utilities and grid operators believed to report the most datacenter load in public "
                "documents, not a ranking from data (no ranking can be made across stages). The pilot's ten; four more operators and federal or public power "
                "systems with a load queue or large-load process (SPP, California ISO with the California Energy Commission's forecast it relies on, New York ISO, "
                "Bonneville Power Administration); two public power systems with large datacenter load (Tennessee Valley Authority, Omaha Public Power District); "
                "and twenty-four utility groups. MISO is not among them: its own site is never requested while its terms are under review.")
# the forty entities, and the names the passes filed their rows under (a row belongs to the first group one of whose
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
}
# a document on one of these hosts is a third party's copy of a publisher's document: its rows are not taken
THIRD_PARTY_HOSTS = {"protectpwc.org", "www.protectpwc.org", "ceae.ku.edu"}
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
         "page", "row_kind", "stage_class", "stage_class_basis", "event_date_basis", "terms_url"]   # session 141
COLS = EVENTS + EXTRA
NUMBER = re.compile(r"\d[\d,]*(?:\.\d+)?")


def group_of(entity):
    for g, names in GROUPS.items():
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
        undated_page = not r.get("document_date", "").strip() and not r.get("page", "").strip() and re.match(r"^\d{4}-\d{2}-\d{2}", r.get("retrieved_at", ""))
        if not dated and not undated_page:
            why.append("no document date")   # a web page that prints no date is filed on the day it was read (to_row); a PDF must state its date
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
    by, seen = {}, {}
    for r in rows:
        g = group_of(r["entity"])
        why = ("not one of the entities" if g is None else "marked CAUTION by its collector (a third party's words or copy)" if "CAUTION" in r.get("notes", "")
               else "the document sits on a third party's host" if host_of(r.get("document_url", "")) in THIRD_PARTY_HOSTS else "")
        if why:
            r["why_not_taken"] = why
            left.append(r)
            continue
        r["entity_group"] = g
        key = (r["entity"], r["document_url"], norm(r["quantity_as_written"]), norm(r["sentence"]))
        if key in seen:
            seen[key]["why_not_taken"] = f"collected again in {r['collected_in']}: that copy is taken"
            left.append(seen[key])
            by[g].remove(seen[key])
        seen[key] = r
        by.setdefault(g, []).append(r)
    for g in GROUPS:
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
    out.sort(key=lambda r: (list(GROUPS).index(r["entity_group"]), r["entity"], r["funnel_order"], r["stage_as_worded"]))
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
        for e in {r["entity"] for r in staged}:
            seq = [int(r["stage_class"][0]) for r in sorted((r for r in staged if r["entity"] == e), key=lambda r: r["funnel_order"]) if r["funnel_order"]]
            against = against or any(b < a for a, b in zip(seq, seq[1:]))
        verdict = ("not placed" if not staged or against else "one stage only" if len(classes) < 2 else "placed" if len(staged) == len(rows) else "placed in part")
        out[g] = dict(stage_words=len(rows), on_a_stage=len(staged), stages=[c[0] for c in classes], against_order=against, verdict=verdict)
    return out


def to_row(r, retrieved, vocab_class=None):
    mw_text = r["mw"].strip()
    rng = re.match(r"^(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)$", mw_text)
    date = r["document_date"].strip()
    basis = "document"
    if not date:   # a web page that prints no date: filed on the day it was read, and said so
        date, basis = (r.get("retrieved_at") or retrieved)[:10], "undated page: the day it was read"
    stated = r["document_date"].strip()
    cls = class_of(r.get("stage_class_proposed", ""))
    cls_basis = "the collecting pass's reading of the document's words: " + norm(r.get("stage_class_reason", "")) if cls else ""
    if not cls and vocab_class:   # a pilot row: placed by its entity's stage words where a later pass placed them
        cls = vocab_class.get((r.get("entity_group"), norm(r["stage_as_worded"]).lower()), "")
        cls_basis = "the same stage words of this entity, placed by a later pass" if cls else ""
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
    }


NEW_141 = ["page", "row_kind", "stage_class", "stage_class_basis", "event_date_basis", "terms_url"]


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
    if list(old.columns) != [c for c in COLS if c not in NEW_141]:
        return False
    for c in NEW_141:
        old[c] = ""
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        f.writelines(head)
        old[COLS].to_csv(f, index=False, lineterminator="\n")
    os.replace(tmp, path)
    log(f"  {os.path.basename(path)}: {len(old)} rows of session 139's shape rewritten with the six columns of session 141, empty")
    return True


def main(argv=None):
    ap = argparse.ArgumentParser(description="Public statements of large load waiting for power, each with its sentence (internal pilot table)")
    ap.add_argument("--out-dir", help="a trial run: the table and its log under this directory; nothing in warehouse/output")
    a = ap.parse_args(argv)
    run_id = pd.Timestamp.now(tz="UTC").strftime("%Y%m%dT%H%M%SZ")
    retrieved = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
    if a.out_dir:
        os.makedirs(a.out_dir, exist_ok=True)
        ip.set_out_dir(a.out_dir)
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    log_path = os.path.join(ip.LOG_DIR, f"large_load_statements_{run_id}.log")
    log = ip.Log(log_path)
    collected, stage_rows = [], []
    for letter, base in PASSES:
        if not os.path.exists(os.path.join(base, letter, "statements.csv")):
            log(f"  pass {letter}: no statements.csv under {base}")
            continue
        collected += read_pass(letter, base)
        stage_rows += read_stages(letter, base)
    rows, failed = checked(collected, log)
    taken, left = choose(rows)
    vocab = stage_vocabulary(stage_rows)
    vocab_class = {(v["entity_group"], v["stage_as_worded"].lower()): v["stage_class"] for v in vocab}
    out = pd.DataFrame([to_row(r, retrieved, vocab_class) for r in taken], columns=COLS)
    if out["event_id"].duplicated().any():
        raise SystemExit("two statements share an id: " + ", ".join(out.loc[out["event_id"].duplicated(), "event_id"]))
    beside = a.out_dir or RAW141
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
    log(f"  collected {len(collected)}, of which {failed} failed the row check; taken {len(out)} from {len(per)} of the {len(GROUPS)} entities "
        f"({int((out['row_kind'] == 'wait').sum())} wait rows); not taken {len(left)} (not_taken.csv)")
    log(f"  stage vocabulary: {len(vocab)} stage words of {len({v['entity_group'] for v in vocab})} entities (stage_vocabulary.csv); funnels: {verdicts} (funnels.csv)")
    log(f"  by entity: {per}")
    header = [
        "Energy Research Warehouse (ERW): public statements of large load waiting for power, each with the exact sentence it was read from (session 139's pilot of "
        "ten entities, extended to forty in session 141)",
        "Shape: events (docs/datastandard.md v0), event_type large_load_statement; one row per figure as a document states it. event_date: the document's date "
        "(a document dated to a month or a year only: its first day; document_date_as_stated holds what it states; a web page that prints no date: the day it "
        "was read, and event_date_basis says so). status: the stage in the document's own words.",
        f"Retrieved: {run_id} (UTC) by warehouse/connectors/large_load_statements.py from the research passes of 7 October 2026 "
        "(warehouse/raw/large_load_pilot/A and B, warehouse/raw/large_load_statements/C to H: statements, rejects, documents opened, timing, stage words, notes, "
        "the documents as downloaded and the checking scripts)",
        f"Run log: warehouse/output/logs/large_load_statements_{run_id}.log",
        f"Source: {SOURCE}: each row's source_url is the utility's or operator's own document (or the copy a commission, the SEC or an operator posts); "
        "document_title, document_type, page_or_slide and page say which and where",
        f"This run: {len(collected)} statements collected and verified by the passes, {len(out)} taken from {len(per)} of the {len(GROUPS)} entities "
        f"({int((out['row_kind'] == 'wait').sum())} of them state a duration, row_kind wait), {len(left)} kept beside the passes' files and not in this table.",
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
                            "report": "Large load statements, 7 October 2026: forty utilities and operators (the pilot's ten, session 139, and thirty more, "
                                      "session 141), each statement with its sentence (docs/accelerator/large_load_pilot.md, "
                                      "docs/accelerator/large_load_forty.md). The publishers' own terms were not read one by one: held internal",
                            "report_url": "https://github.com/SamuelEnrique/erw/blob/main/docs/accelerator/large_load_pilot.md", "document_list": "",
                            "license": "internal", "tables": [NAME]}])
    return 0


if __name__ == "__main__":
    sys.exit(main())
