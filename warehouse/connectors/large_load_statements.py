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
PER_GROUP = 5
# the ten entities, and the names the two passes filed their rows under
GROUPS = {
    "Dominion Energy Virginia": ["Dominion Energy Virginia"],
    "Georgia Power (Southern Company)": ["Georgia Power", "Southern Company traditional electric operating companies"],
    "Duke Energy": ["Duke Energy Carolinas and Duke Energy Progress", "Duke Energy (enterprise"],
    "Entergy": ["Entergy utility operating companies"],
    "PJM Interconnection": ["PJM Interconnection", "PPL Electric Utilities (submission to PJM)", "FirstEnergy (submission to PJM)"],
    "Oncor Electric Delivery": ["Oncor Electric Delivery"],
    "CenterPoint Energy Houston Electric": ["CenterPoint Energy Houston Electric"],
    "American Electric Power": ["American Electric Power"],
    "Exelon": ["Exelon"],
    "ERCOT": ["ERCOT"],
}
EVENTS = ["event_id", "event_date", "event_type", "parties", "entity_ids", "mw", "price", "currency", "status", "source", "source_url"]
EXTRA = ["entity_group", "entity", "entity_type", "parent_company", "document_title", "document_type", "document_date_as_stated", "page_or_slide",
         "quantity_as_written", "mw_low", "mw_high", "stage_as_worded", "load_type_as_worded", "place_as_worded", "time_horizon_as_worded",
         "wait_or_lead_time_as_worded", "sentence", "collected_in", "retrieved_at", "notes"]
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
    """Whether the row's own figure stands in its sentence: each number of quantity_as_written is in the sentence."""
    s = norm(row["sentence"]).replace(",", "")
    nums = [n.replace(",", "") for n in NUMBER.findall(row["quantity_as_written"])]
    return bool(nums) and all(n in s for n in nums)


def read_pass(letter):
    path = os.path.join(RAW, letter, "statements.csv")
    with open(path, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r["collected_in"] = f"pass {letter}"
    return rows


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
        if not re.match(r"^\d{4}-\d{2}(-\d{2})?$", r.get("document_date", "")):
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


def choose(rows):
    """At most PER_GROUP rows an entity, by the rule in the docstring. Returns (taken, not_taken)."""
    taken, left = [], []
    by = {}
    for r in rows:
        g = group_of(r["entity"])
        if g is None or "CAUTION" in r.get("notes", ""):
            r["why_not_taken"] = "not one of the ten entities" if g is None else "marked CAUTION by its collector (a third party's copy)"
            left.append(r)
            continue
        r["entity_group"] = g
        by.setdefault(g, []).append(r)
    for g in GROUPS:
        cand = sorted(by.get(g, []), key=lambda r: (r["document_date"], size_of(r), r["document_url"], r["sentence"], r["quantity_as_written"]), reverse=True)
        picked, stages = [], set()
        for r in cand:  # a stage not yet taken first
            if len(picked) < PER_GROUP and norm(r["stage_as_worded"]).lower() not in stages:
                picked.append(r)
                stages.add(norm(r["stage_as_worded"]).lower())
        for r in cand:
            if len(picked) < PER_GROUP and r not in picked:
                picked.append(r)
        taken += picked
        for r in cand:
            if r not in picked:
                r["why_not_taken"] = f"the entity's {PER_GROUP} statements were already taken (newer, or a stage not yet held)"
                left.append(r)
    return taken, left


def to_row(r, retrieved):
    mw_text = r["mw"].strip()
    rng = re.match(r"^(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)$", mw_text)
    date = r["document_date"]
    key = "|".join([r["entity"], r["document_url"], norm(r["sentence"]), r["quantity_as_written"], r["stage_as_worded"]])
    return {
        "event_id": "llstmt:" + hashlib.sha1(key.encode("utf-8")).hexdigest()[:16],
        "event_date": date if len(date) == 10 else f"{date}-01", "event_type": "large_load_statement",
        "parties": r["entity"], "entity_ids": "", "mw": "" if rng or not mw_text else float(mw_text), "price": "", "currency": "",
        "status": norm(r["stage_as_worded"]), "source": SOURCE, "source_url": r["document_url"],
        "entity_group": r["entity_group"], "entity": r["entity"], "entity_type": r["entity_type"], "parent_company": r["parent_company"],
        "document_title": norm(r["document_title"]), "document_type": r["document_type"], "document_date_as_stated": date,
        "page_or_slide": r["page_or_slide"], "quantity_as_written": r["quantity_as_written"],
        "mw_low": float(rng.group(1)) if rng else "", "mw_high": float(rng.group(2)) if rng else "",
        "stage_as_worded": norm(r["stage_as_worded"]), "load_type_as_worded": norm(r["load_type_as_worded"]), "place_as_worded": norm(r["place_as_worded"]),
        "time_horizon_as_worded": norm(r["time_horizon_as_worded"]), "wait_or_lead_time_as_worded": norm(r["wait_or_lead_time_as_worded"]),
        "sentence": norm(r["sentence"]), "collected_in": r["collected_in"], "retrieved_at": r["retrieved_at"] or retrieved, "notes": norm(r["notes"]),
    }


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
    collected = read_pass("A") + read_pass("B")
    rows, failed = checked(collected, log)
    taken, left = choose(rows)
    out = pd.DataFrame([to_row(r, retrieved) for r in taken], columns=COLS)
    if out["event_id"].duplicated().any():
        raise SystemExit("two statements share an id: " + ", ".join(out.loc[out["event_id"].duplicated(), "event_id"]))
    with open(os.path.join(a.out_dir or RAW, "not_taken.csv"), "w", encoding="utf-8", newline="") as f:
        cols = [c for c in collected[0] if c != "entity_group"] + ["why_not_taken"]
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n", extrasaction="ignore")
        w.writeheader()
        w.writerows(left)
    per = out.groupby("entity_group").size().to_dict()
    log(f"  collected {len(collected)}, of which {failed} failed the row check; taken {len(out)} ({per}); not taken {len(left)} (not_taken.csv)")
    header = [
        "Energy Research Warehouse (ERW): public statements of large load waiting for power, each with the exact sentence it was read from: a pilot (session 139)",
        "Shape: events (docs/datastandard.md v0), event_type large_load_statement; one row per figure as a document states it. event_date: the document's date "
        "(a document dated to a month only: that month's first day; document_date_as_stated holds what it states). status: the stage in the document's own words.",
        f"Retrieved: {run_id} (UTC) by warehouse/connectors/large_load_statements.py from the two research passes of 7 October 2026 "
        "(warehouse/raw/large_load_pilot/A and B: statements, rejects, documents opened, timing, notes, the documents as downloaded and the checking scripts)",
        f"Run log: warehouse/output/logs/large_load_statements_{run_id}.log",
        f"Source: {SOURCE}: each row's source_url is the utility's or operator's own document (or the copy a commission, the SEC or an operator posts); "
        "document_title, document_type and page_or_slide say which and where",
        f"This run: {len(collected)} statements collected and verified by the passes, {len(out)} taken (at most {PER_GROUP} for each of the ten entities, "
        f"by the rule in the connector's docstring), {len(left)} kept beside the passes' files and not in this table.",
        "No number without its sentence: sentence is a literal substring of the document's extracted text, checked by code in each pass, and the figure as "
        "written stands in it. mw is quantity_as_written in MW; a range is in mw_low and mw_high with mw empty.",
        "DO NOT SUM across rows or entities: the entities count differently (requests, studies, letters, contracts, forecasts), a document often states a total "
        "and its parts, and two documents may state one quantity. The stage is each document's own wording.",
        "License: internal. Quoted from public documents under each publisher's own terms, not read one by one in the pilot; held internal until a person rules. "
        "Not on the site, not in the public Redivis dataset, not in the live set.",
    ]
    ip.write_csv(out, NAME, header, lambda m: log(m.strip()), cols=COLS, key=["event_id"], time_col="event_date")
    if not a.out_dir:
        ip.update_sources([{"source": SOURCE, "publisher": "Energy Research Warehouse (ERW), collected from utilities' and grid operators' public documents by an AI research agent, each sentence checked by code",
                            "report": "Large load statements pilot, 7 October 2026: ten utilities and operators, each statement with its sentence "
                                      "(docs/accelerator/large_load_pilot.md). The publishers' own terms were not read one by one: held internal",
                            "report_url": "https://github.com/SamuelEnrique/erw/blob/main/docs/accelerator/large_load_pilot.md", "document_list": "",
                            "license": "internal", "tables": [NAME]}])
    return 0


if __name__ == "__main__":
    sys.exit(main())
