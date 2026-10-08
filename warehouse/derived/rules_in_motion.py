#!/usr/bin/env python3
"""Rules in motion for large loads: the site's file for the block in "How soon" on /cost-of-power (session 154).

Energy Research Warehouse (ERW). No warehouse table is written, no request is made and nothing is loaded: this reads
tables already built and writes one file, site/data/datacenter/rules.json, whole, by rename. Method:
docs/methods/datacenter_cost.md, section "Rules in motion".

    python warehouse/derived/rules_in_motion.py --in-dir TRIAL --in-dir C:/.../warehouse/output
    python warehouse/derived/rules_in_motion.py --in-dir TRIAL --in-dir MAIN --out-dir DIR      # a trial: DIR/rules.json
    python warehouse/derived/rules_in_motion.py --ten DIR                # also the ten rules of the month (ten.json)

Tables read (the first --in-dir that holds a table wins; a table none holds is left out and named in the file):
    policy_actions, policy_action_tags, policy_reads      the federal actions held, their tags and their reads
    large_load_rules, large_load_rules_internal           the proceedings and orders of FERC and ten state commissions
                                                          (warehouse/connectors/large_load_rules.py)
    large_load_rule_reads                                 the model's one-line reads (warehouse/policy/rule_reads.py)

What is "in motion": a proceeding whose status class is open; an order or rule dated in the last 12 months; a tagged
federal action held of the last 12 months.

Which grid sees which action. A state commission's row about one named utility is under that utility's own operator
and no other, as warehouse/config/large_load_rule_grids.json states it with its source (FERC's orders of 18 June 2026
name each operator's transmission owners in their captions), and under no grid where the file says the utility is in
no organized market on the page (El Paso Electric) or does not list it and the docket's documents name no operator. A
statewide rule is under the operator its own documents name, else the state's operators (STATE_GRIDS below). A federal
action is under the operator its own words name, else in a group of its own, "Federal, all grids". MISO's block holds
the words "paused while terms are reviewed" and no row. Georgia, Arizona and Oregon have no grid on the page: their
actions are in the table and not in the file.

Two tables, by the regulator's own terms (warehouse/config/large_load_rule_terms.json): a row of large_load_rules
(public) is in the file with its sentence and its worded status; a row of large_load_rules_internal is in the file
with its facts, its link and the model's read only ("sentence" and "status_as_worded" null, "sentence_withheld" says
why). OFF_PAGE_REGULATORS and SHOW_SENTENCE_REGULATORS below are the owner's two switches.

Never in the file: the sentence or the worded status of a row of the internal table; anything municipal (a row whose
shown title, sentence, read or status holds one of MUNICIPAL_WORDS is kept out and counted); a read line a model did
not write; a filled field.
"""

import argparse
import datetime as dt
import json
import os
import re
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
SITE_FILE = os.path.join(ROOT, "site", "data", "datacenter", "rules.json")
TERMS_FILE = os.path.join(ROOT, "warehouse", "config", "large_load_rule_terms.json")
WINDOW_MONTHS = 12
GRIDS = ["ercot", "pjm", "miso", "caiso", "nyiso", "isone", "spp"]
MISO_WORDS = "paused while terms are reviewed"
# The names by which a document's own words name a grid operator (whole words, any case).
OPERATOR_WORDS = {
    "ercot": ["ERCOT", "Electric Reliability Council of Texas"],
    "pjm": ["PJM"],
    "miso": ["MISO", "Midcontinent Independent System Operator"],
    "caiso": ["CAISO", "California Independent System Operator", "California ISO"],
    "nyiso": ["NYISO", "New York Independent System Operator", "New York ISO"],
    "isone": ["ISO-NE", "ISO New England"],
    "spp": ["SPP", "Southwest Power Pool"],
}
GRID_NAMES = {"ercot": "ERCOT", "pjm": "PJM", "miso": "MISO", "caiso": "CAISO", "nyiso": "NYISO", "isone": "ISO-NE",
              "spp": "SPP"}
# Which operator serves which state's utilities, for the ten states whose commissions were read. Stated plainly as
# common knowledge of the US power system, the states listed (no federal table of it is cited in this repository):
# the operators' own membership is public (each names its transmission owners), and the method note repeats this list.
# A state with no organized market operator on the page has an empty list: its actions are in the table, not the file.
STATE_GRIDS = {
    "TX": (["ercot"], "The Texas commission regulates the ERCOT region, where most of the state's load is served; the "
                      "parts of Texas in SPP and MISO see a Texas action only when its own words name them."),
    "VA": (["pjm"], "Virginia's investor-owned utilities (Dominion Energy Virginia, Appalachian Power) are in PJM."),
    "OH": (["pjm"], "Ohio's utilities (AEP Ohio, FirstEnergy's Ohio companies, AES Ohio, Duke Energy Ohio) are in PJM."),
    "PA": (["pjm"], "Pennsylvania's utilities (PECO, PPL Electric, FirstEnergy's Pennsylvania company, Duquesne Light) are in PJM."),
    "IL": (["pjm", "miso"], "Illinois is served by PJM in the north (Commonwealth Edison) and MISO elsewhere (Ameren Illinois)."),
    "IN": (["pjm", "miso"], "Indiana is served by PJM (Indiana Michigan Power) and by MISO (the state's other utilities)."),
    "CA": (["caiso"], "California's investor-owned utilities (PG&E, Southern California Edison, SDG&E) are in CAISO."),
    "GA": ([], "Georgia's utilities are in no organized market: no grid on the page."),
    "AZ": ([], "Arizona's utilities are in no organized market operator's footprint: no grid on the page."),
    "OR": ([], "Oregon's utilities are in no organized market operator's footprint: no grid on the page."),
}
# The block never shows these words (session 154: nothing municipal). A row holding one is kept out and counted.
MUNICIPAL_WORDS = ["zoning", "permit", "city council", "county board"]
AGENCY_NAMES = {"FERC": "Federal Energy Regulatory Commission", "DOE": "Department of Energy",
                "EPA": "Environmental Protection Agency", "NRC": "Nuclear Regulatory Commission",
                "BLM": "Bureau of Land Management", "Interior": "Department of the Interior"}
FEDERAL = list(AGENCY_NAMES)
TAG_TOPICS = {"large_load": "large loads", "interconnection": "interconnection",
              "transmission_cost": "transmission cost", "tax_credit": "tax credits"}
# The status class of a held federal action, from its type alone (the Register gives no docket status).
ACTION_CLASS = {"rule": "decided", "proposed_rule": "open", "notice": "not stated", "press_release": "not stated"}
TABLES = ["large_load_rules", "large_load_rules_internal"]
# Two switches for the owner, one line each (session 154). A regulator whose terms restrict copying, or whose terms no
# pass read, has its rows in large_load_rules_internal: the file then holds such a row's facts, its link and the
# model's read, and neither its sentence nor its worded status.
#   OFF_PAGE_REGULATORS: name a regulator here and none of its rows is in the file at all.
#   SHOW_SENTENCE_REGULATORS: name a regulator here and its rows carry their sentence and worded status although the
#   table is internal (the owner's ruling that its text may be shown; its class in large_load_rule_terms.json should
#   then change too, which moves its rows to the public table at the next build of the connector).
SINGLE_FLAG = "single-customer contract"   # the connector's flag (large_load_rules.FLAG_SINGLE begins with it)
OFF_PAGE_REGULATORS = ()
SHOW_SENTENCE_REGULATORS = ()
READ_FROM_HELD = ("the action's own text in the Federal Register or the agency's release; kept only where its "
                  "supporting quotations were found word for word in that text (policy_reads)")


def read_events(path):
    with open(path, encoding="utf-8") as f:
        head = []
        for ln in f:
            if not ln.startswith("#"):
                break
            head.append(ln[1:].strip())
    return pd.read_csv(path, skiprows=len(head), dtype=str, keep_default_na=False), head


def find(name, dirs):
    for d in dirs:
        p = os.path.join(d, name + ".csv")
        if os.path.exists(p):
            return p
    return None


def license_of(head):
    """'public' or 'internal', from the table's header (the line that states its License)."""
    for h in head:
        m = re.search(r"License:\s*(public|internal)", h)
        if m:
            return m.group(1)
    return "internal"  # a table that does not say is not shown


def operators_named(text):
    """The grids whose operator the text names, in GRIDS order."""
    out = []
    for g in GRIDS:
        for w in OPERATOR_WORDS[g]:
            if re.search(r"(?<![A-Za-z0-9])" + re.escape(w) + r"(?![A-Za-z0-9])", text or "", flags=re.I if " " in w else 0):
                out.append(g)
                break
    return out


def months_back(day, months):
    y, m = day.year, day.month - months
    while m <= 0:
        y, m = y - 1, m + 12
    d = min(day.day, [31, 29 if y % 4 == 0 and (y % 100 or y % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1])
    return dt.date(y, m, d)


def municipal(row):
    text = " ".join(str(row.get(k) or "") for k in ("title", "sentence", "read", "status_as_worded")).lower()
    return [w for w in MUNICIPAL_WORDS if w in text]


def sentence_of(text, term):
    """The sentence of an abstract that holds the term (the abstract's own words), else ''."""
    for s in re.split(r"(?<=[.;])\s+(?=[A-Z])", text or ""):
        if re.search(re.escape(term).replace(r"\ ", r"[\s-]+"), s, flags=re.I):
            return s.strip()
    return ""


def docket_words(row):
    d = re.sub(r"\bDocket Nos?\.\s*", "", row.get("docket", "") or "").strip()
    d = d.split(";")[0].strip()
    if d:
        return d
    if row.get("fr_document_number"):
        return "FR Doc. " + row["fr_document_number"]
    return ""


def held_rows(dirs, cutoff, notes):
    """The tagged federal actions held of the last 12 months, as ROWs; (rows, counted-out reasons)."""
    pa, pt = find("policy_actions", dirs), find("policy_action_tags", dirs)
    if not pa or not pt:
        notes.append("policy_actions or policy_action_tags is not held: no federal action held is in the file")
        return [], {}
    acts, head = read_events(pa)
    tags, thead = read_events(pt)
    out, off = [], {}
    if license_of(head) != "public" or license_of(thead) != "public":
        notes.append("policy_actions or policy_action_tags is internal: none of its rows is in the file")
        return [], {"internal table": int(tags["action_event_id"].nunique())}
    reads = {}
    pr = find("policy_reads", dirs)
    if pr:
        r, rhead = read_events(pr)
        if license_of(rhead) == "public":
            reads = {x["action_event_id"]: x for x in r.to_dict("records") if x["plain_read"].strip()}
    extra = {}
    er = find("large_load_rule_reads", dirs)
    if er:
        r, rhead = read_events(er)
        if license_of(rhead) == "public":
            extra = {x["rule_event_id"]: x for x in r.to_dict("records") if x["read"].strip()}
    by = acts.set_index("event_id")
    docket_ops = {}
    rules_file = os.path.join(ROOT, "warehouse", "config", "policy_tag_rules.json")
    if os.path.exists(rules_file):
        with open(rules_file, encoding="utf-8") as f:
            docket_ops = {d["docket"]: d.get("grids", []) for d in json.load(f).get("dockets", {}).get("list", [])}

    def g_tags(aid, tags):
        return tags[(tags["action_event_id"] == aid) & (tags["matched_field"] == "docket")]

    def g_terms(g_rows):
        return list(g_rows["matched_term"])

    for aid, g in tags.groupby("action_event_id", sort=False):
        a = by.loc[aid].to_dict()
        a["event_id"] = aid
        if a["agency"] in ("Treasury", "IRS"):   # session 157: the tax credits are in the policy monitor's view, not here
            k = "a Treasury or IRS action held (tax credits: shown in the policy monitor, not in this block)"
            off[k] = off.get(k, 0) + 1
            continue
        if a["agency"] not in FEDERAL:
            off["a state commission's news release held (in the tags table; the block shows a state's dockets, not its releases)"] = \
                off.get("a state commission's news release held (in the tags table; the block shows a state's dockets, not its releases)", 0) + 1
            continue
        if a["event_date"][:10] < cutoff.isoformat():
            off["older than 12 months"] = off.get("older than 12 months", 0) + 1
            continue
        first = g.iloc[0]
        sent, sfrom = "", "title"
        if first["matched_field"] == "abstract":
            sent, sfrom = sentence_of(a["abstract"], first["matched_term"]), "abstract"
        if not sent:
            sent, sfrom = a["title"], "title"
        rd = reads.get(aid)
        ex = extra.get(aid)
        row = {
            "id": aid, "date": a["event_date"][:10], "regulator": AGENCY_NAMES[a["agency"]], "jurisdiction": "federal",
            "state": "", "docket": docket_words(a), "title": a["title"], "row_kind": "federal action",
            "topic": "; ".join(TAG_TOPICS[t] for t in g["tag"]), "tags": list(g["tag"]),
            "status_as_worded": a["status"] if a["status"] not in ("", "news release") else "",
            "status_class": ACTION_CLASS.get(a["action_type"], "not stated"), "url": a["source_url"], "page": None,
            "sentence": sent, "sentence_withheld": None, "sentence_from": "the action's " + sfrom, "sentence_kind": "document",
            "flags": [], "terms_class": "",
            "read": rd["plain_read"] if rd else (ex["read"] if ex else None),
            "read_by": "model" if (rd or ex) else None,
            "read_model": rd["model_id"] if rd else (ex["model_id"] if ex else None),
            "read_from": READ_FROM_HELD if rd else (ex["read_from"] if ex else None),
            "named": operators_named(a["title"] + " " + a["abstract"]),
        }
        for g in GRIDS:   # a notice tagged by its docket number is under the operator that docket is about
            if any(GRID_NAMES[g] in docket_ops.get(t, []) for t in g_terms(g_rows=g_tags(aid, tags))) and g not in row["named"]:
                row["named"].append(g)
        out.append(row)
    return out, off


def load_terms(path=None):
    path = path or TERMS_FILE
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        return {t["regulator"]: t for t in json.load(f)["regulators"]}


def withheld_words(regulator, terms):
    t = terms.get(regulator) or {}
    return t.get("withheld_words") or f"The {regulator}'s terms on copying its text were not read; open the document"


GRIDS_FILE = os.path.join(ROOT, "warehouse", "config", "large_load_rule_grids.json")
# A caption that holds one of these words names a company: the row is about one utility, not a statewide rule.
COMPANY_WORDS = re.compile(r"\b(Company|Cooperative|Corporation|Inc\.|LLC|L\.L\.C\.|d/b/a|dba|Electric Power|Power & Light|PG&E)\b|PG&E")
KEY_OF = {v: k for k, v in GRID_NAMES.items()}


def load_utilities(path=None):
    path = path or GRIDS_FILE
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return json.load(f)["utilities"]


def utility_of(state, caption, utilities):
    """(scope, the listed utility or None) of a state commission's docket, from its caption (the proceeding's title,
    with the docket number where the commission prints the utility there). 'one utility': the caption holds a name
    the mapping file lists for the state. 'one utility, not listed': it names a company the file does not list.
    'statewide': it names no company (a rulemaking, an investigation, a conference)."""
    low = caption.lower()
    for u in utilities:
        if u["state"] == state and any(n.lower() in low for n in u["names"]):
            return "one utility", u
    if COMPANY_WORDS.search(caption):
        return "one utility, not listed", None
    return "statewide", None


def docket_base(number):
    """A docket number without its sub-docket (EL26-67-000 and EL26-67-001 are one docket)."""
    return re.sub(r"-\d{3}$", "", number or "")


def in_motion(a, cutoff):
    kind, cls, day = a["row_kind"], a["status_class"], a["event_date"][:10]
    return (kind == "proceeding" and cls == "open") or (kind == "order" and day >= cutoff.isoformat())


def table_rows(dirs, cutoff, notes, every=False):
    """The proceedings and orders in motion, as ROWs, from the public table and the internal one; (rows, counted-out
    reasons). every (session 157, the policy monitor's file): every row held, in motion or not, each with the key
    "in_motion"; the block's own file is built with every False and is unchanged. A row of the public table carries its sentence and its worded status. A row of the internal table
    carries its facts only (date, regulator, docket number, status class, topic, the link) and the model's read:
    "sentence" and "status_as_worded" are null, the title is empty and "sentence_withheld" says why, unless its
    regulator is in SHOW_SENTENCE_REGULATORS; a regulator in OFF_PAGE_REGULATORS has no row in the file at all."""
    terms = load_terms()
    reads = {}
    rp = find("large_load_rule_reads", dirs)
    if rp:
        r, rhead = read_events(rp)
        if license_of(rhead) == "public":
            reads = {x["rule_event_id"]: x for x in r.to_dict("records") if x["read"].strip()}
    out, off, found = [], {}, False
    loaded = []
    utilities = load_utilities()
    captions = {}       # a docket's caption: every title its rows give it, and its number
    docket_grids = {}   # the operators any document of a docket names: its other rows, which name none, take them
    for name in TABLES:
        p = find(name, dirs)
        if p:
            t, head = read_events(p)
            loaded.append((name, t, head))
            for a in t.to_dict("records"):
                key = (a["regulator"], docket_base(a["docket_number"]))
                captions.setdefault(key, set()).update([a["proceeding_title"], a["docket_number"]])
                for x in a["grids"].split(";"):
                    if x.strip():
                        docket_grids.setdefault(key, set()).add(x.strip())
    for name, t, head in loaded:
        found = True
        public = license_of(head) == "public"
        if public != (name == "large_load_rules"):
            raise RuntimeError(f"{name}: its header's license is not the one its name says; nothing is written")
        for a in t.to_dict("records"):
            moving = in_motion(a, cutoff)
            if not moving and not every:
                why = "a proceeding whose status class is not open" if a["row_kind"] == "proceeding" else "an order older than 12 months"
                off[why] = off.get(why, 0) + 1
                continue
            if a["regulator"] in OFF_PAGE_REGULATORS:
                k = f"{a['regulator']}: turned off the page (OFF_PAGE_REGULATORS)"
                off[k] = off.get(k, 0) + 1
                continue
            show = public or a["regulator"] in SHOW_SENTENCE_REGULATORS
            rd = reads.get(a["event_id"])
            # the operators the document's own words name, as the collecting pass recorded them (grids): a pass leaves
            # out an operator named only in passing (a capacity auction mentioned once), which a word search would not
            own = [x.strip() for x in a["grids"].split(";") if x.strip()] or sorted(docket_grids.get((a["regulator"], docket_base(a["docket_number"])), []))
            named = [g for g in GRIDS if GRID_NAMES[g] in own]
            out.append({
                "id": a["event_id"], "date": a["event_date"][:10], "regulator": a["regulator"],
                "jurisdiction": a["jurisdiction"], "state": a["state"], "docket": a["docket_number"],
                "title": (a["document_title"] or a["proceeding_title"]) if show else "",
                "row_kind": a["row_kind"], "topic": a["topic"].replace(";", "; "), "tags": [],
                "status_as_worded": a["status_as_worded"] if show else None, "status_class": a["status_class"],
                "url": a["source_url"], "page": int(a["page"]) if a["page"].strip().isdigit() else None,
                "sentence": a["sentence"] if show else None,
                "sentence_withheld": None if show else withheld_words(a["regulator"], terms),
                "sentence_from": a.get("sentence_from", "") or "document text", "sentence_kind": a.get("sentence_kind", ""),
                "flags": [x for x in a.get("row_flag", "").split("; ") if x],
                "terms_class": (terms.get(a["regulator"]) or {}).get("class", "not quoted"),
                "read": rd["read"] if rd else None, "read_by": "model" if rd else None,
                "read_model": rd["model_id"] if rd else None, "read_from": rd["read_from"] if rd else None,
                "named": named,
                "placing": utility_of(a["state"], " | ".join(sorted(captions[(a["regulator"], docket_base(a["docket_number"]))])), utilities)
                if a["jurisdiction"] == "state" else ("federal", None),
            })
            if every:
                out[-1]["in_motion"] = moving
    if not found:
        notes.append("large_load_rules is not built yet: the file holds the federal actions held only")
    return out, off


def place(rows):
    """{grid: [rows]}, the federal group, and the rows with no grid on the page [(row, reason)], by the mapping.

    A state commission's row (session 154, the mapping corrected):
      - about one utility the mapping file lists: under that utility's operator and no other; under no grid where the
        file says the utility is in no organized market on the page;
      - about one utility the file does not list: under the operator the docket's own documents name, else no grid;
      - a statewide rule: under the operator the docket's own documents name, else the state's operators.
    A federal action: under the operator its own words name, else in the group Federal, all grids."""
    grids = {g: [] for g in GRIDS}
    federal, nowhere = [], []
    for r in rows:
        named = r.pop("named")
        scope, u = r.pop("placing", ("statewide", None))
        if r["jurisdiction"] == "state":
            base, why = STATE_GRIDS.get(r["state"], ([], f"{r['state']}: no mapping written for this state"))
            r = dict(r, scope="one utility" if scope.startswith("one utility") else "statewide", utility=u["utility"] if u else None)
            if u is not None:
                if not u["operator"]:
                    nowhere.append((r, f"{u['utility']}: in no organized market on the page"))
                elif not base and KEY_OF[u["operator"]] not in base and r["state"] in ("GA", "AZ", "OR"):
                    nowhere.append((r, f"{r['state']}: no grid on the page"))
                else:
                    g = KEY_OF[u["operator"]]
                    grids[g].append(dict(r, why_here=f"A case of {u['utility']}: {u['why']}."))
                continue
            if scope == "one utility, not listed":
                if named:
                    for g in named:
                        grids[g].append(dict(r, why_here=f"The document's own words name {GRID_NAMES[g]}."))
                elif not base:
                    nowhere.append((r, f"{r['state']}: no grid on the page"))
                else:
                    nowhere.append((r, f"{r['state']}: names a utility whose operator the mapping file does not state"))
                continue
            if named:   # a statewide rule whose own documents name the operator
                for g in named:
                    grids[g].append(dict(r, why_here=f"A statewide rule; the document's own words name {GRID_NAMES[g]}."))
            elif not base:
                nowhere.append((r, f"{r['state']}: no grid on the page"))
            else:
                for g in base:
                    grids[g].append(dict(r, why_here="A statewide rule. " + why))
        elif named:
            for g in named:
                grids[g].append(dict(r, why_here=f"A federal action whose own words name {GRID_NAMES[g]}."))
        else:
            federal.append(dict(r, why_here="A federal action that names no grid operator: it is under every grid."))
    return grids, federal, nowhere


def order(rows):
    return sorted(rows, key=lambda r: (r["date"], r["id"]), reverse=True)


def build(dirs, today):
    cutoff = months_back(today, WINDOW_MONTHS)
    notes, off = [], {}
    rows = []
    for fn in (table_rows, held_rows):
        got, out = fn(dirs, cutoff, notes)
        rows += got
        for k, v in out.items():
            off[k] = off.get(k, 0) + v
    seen, kept = set(), []
    for r in rows:
        words = municipal(r)
        if words:
            k = "a row that holds a word the block never shows (" + ", ".join(MUNICIPAL_WORDS) + "): in the table, not in the file"
            off[k] = off.get(k, 0) + 1
            continue
        if any(chr(0x2014) in str(r.get(k) or "") for k in ("title", "sentence", "status_as_worded", "read", "docket")):
            k = "a row whose own words hold an em dash, which no file of this repository holds: in the table, not in the file"
            off[k] = off.get(k, 0) + 1
            continue
        if r["id"] in seen:
            continue
        seen.add(r["id"])
        kept.append(r)
    grids, federal, nowhere = place(kept)
    for r, why in nowhere:
        off[why] = off.get(why, 0) + 1
    elsewhere = {r["id"] for g in GRIDS if g != "miso" for r in grids[g]}
    miso_only = sum(1 for r in grids["miso"] if r["id"] not in elsewhere)
    if miso_only:
        off["under MISO alone (MISO is paused and shows no row)"] = miso_only
    out_grids = {}
    for g in GRIDS:
        if g == "miso":
            out_grids[g] = {"state": "paused", "words": MISO_WORDS, "rows": []}
        elif grids[g]:
            out_grids[g] = {"state": "shown", "rows": order(grids[g])}
        else:
            out_grids[g] = {"state": "none", "rows": [],
                            "why": "No proceeding or order held names this grid or comes from a state it serves; "
                                   "the federal actions that name no grid are in the group Federal, all grids."}
    sources = []
    shown = {r["regulator"] for g in out_grids.values() for r in g["rows"]} | {r["regulator"] for r in federal}
    for t in load_terms().values():
        if t["regulator"] in shown and t.get("terms_quote"):
            sources.append({"regulator": t["regulator"], "terms_url": t["terms_url"], "terms_quote": t["terms_quote"],
                            "terms_class": t["class"]})
    n_off = sum(off.values())
    why = "; ".join(f"{v} {k}" for k, v in sorted(off.items())) if off else "Every row in motion held is in the file."
    return {
        "built_at_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "as_of": today.isoformat(), "window_months": WINDOW_MONTHS, "window_from": cutoff.isoformat(),
        "sources": sources, "grids": out_grids, "federal_all_grids": order(federal),
        "not_on_page": {"count": n_off, "why": why, "by_reason": dict(sorted(off.items()))},
        "notes": notes,
    }


# ---------------------------------------------------------------- the ten rules of the month (session 154, part e)
TEN = 10
TEN_PER_REGULATOR = 2   # 3 at first: see the note in ten_rules
MONTH_DAYS = 31
DIRECTNESS = {"large-load interconnection": 3, "large-load tariff": 3, "transmission cost allocation": 2,
              "interconnection reform": 1}
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November",
          "December"]
DATE_WORDS = re.compile(r"\b(" + "|".join(MONTHS) + r")\s+(\d{1,2}),?\s+(\d{4})\b|\b(\d{4})-(\d{2})-(\d{2})\b")


def dates_in(text):
    """The dates a text writes ('October 20, 2026' or '2026-10-20'), as dates."""
    out = []
    for m in DATE_WORDS.finditer(text or ""):
        try:
            if m.group(1):
                out.append(dt.date(int(m.group(3)), MONTHS.index(m.group(1)) + 1, int(m.group(2))))
            else:
                out.append(dt.date(int(m.group(4)), int(m.group(5)), int(m.group(6))))
        except ValueError:
            pass
    return out


def ten_rules(dirs, today):
    """The ten rules a datacenter buyer most needs to know this month, by a stated rule (docs/accelerator/
    rules_in_motion.md says it in words). The pool: every row in motion of large_load_rules, whichever the state (a
    state with no grid on the page is in the pool). One row a docket: its newest row in motion. Ordered by
        1. this month first: the document is dated in the MONTH_DAYS days up to today, or its row states a date
           (a comment deadline, a hearing, an effective date, in notes or status_as_worded) in the MONTH_DAYS days
           from today;
        2. how directly it sets when or at what cost a large load is served: its topic's DIRECTNESS (interconnection
           standards and tariffs with minimum terms and collateral, then who pays for transmission, then
           interconnection reform at large); a document on two topics counts by its more direct one (as first written the
           two were added and three rows a regulator allowed: that left FERC's show cause orders, the broadest
           actions held, out of the ten behind two-topic state orders; corrected once, on 8 October 2026);
        3. breadth: a federal action before a state's; more grids named before fewer;
        4. the newest document first.
    At most TEN_PER_REGULATOR rows a regulator, so that ten rows are not one commission's docket list. Ten rows, no
    more. Returns (the rows, the size of the pool)."""
    terms = load_terms()
    reads = {}
    rp = find("large_load_rule_reads", dirs)
    if rp:
        r, _ = read_events(rp)
        reads = {x["rule_event_id"]: x for x in r.to_dict("records") if x["read"].strip()}
    cutoff = months_back(today, WINDOW_MONTHS)
    month_from, month_to = today - dt.timedelta(days=MONTH_DAYS), today + dt.timedelta(days=MONTH_DAYS)
    pool, single = {}, 0
    for name in TABLES:
        p = find(name, dirs)
        if not p:
            continue
        t, head = read_events(p)
        lic = license_of(head)
        for a in t.to_dict("records"):
            if not in_motion(a, cutoff):
                continue
            if SINGLE_FLAG in a.get("row_flag", ""):
                single += 1   # a contract with one customer sets no rule for others: never among the ten
                continue
            a["table_license"] = lic
            day = a["event_date"][:10]
            key = (a["regulator"], re.sub(r"-\d{3}$", "", a["docket_number"]))
            if key not in pool or (day, a["event_id"]) > (pool[key]["event_date"][:10], pool[key]["event_id"]):
                pool[key] = a
    scored = []
    for a in pool.values():
        day = dt.date.fromisoformat(a["event_date"][:10])
        ahead = [d for d in dates_in(a["notes"] + " " + a["status_as_worded"]) if today <= d <= month_to]
        this_month = day >= month_from or bool(ahead)
        direct = max([DIRECTNESS.get(x.strip(), 0) for x in a["topic"].split(";")] or [0])
        named = [g for g in a["grids"].split(";") if g.strip()]
        breadth = (2 if a["jurisdiction"] == "federal" else 0) + min(len(named), 3)
        scored.append(((1 if this_month else 0, direct, breadth, a["event_date"][:10], a["event_id"]), a, ahead))
    scored.sort(key=lambda x: x[0], reverse=True)
    out, per = [], {}
    for score, a, ahead in scored:
        if per.get(a["regulator"], 0) >= TEN_PER_REGULATOR:
            continue
        per[a["regulator"]] = per.get(a["regulator"], 0) + 1
        rd = reads.get(a["event_id"])
        show = a["table_license"] == "public" or a["regulator"] in SHOW_SENTENCE_REGULATORS
        out.append({"rank": len(out) + 1, "regulator": a["regulator"], "state": a["state"], "docket": a["docket_number"],
                    "date": a["event_date"][:10], "row_kind": a["row_kind"], "topic": a["topic"].replace(";", "; "),
                    "status_as_worded": a["status_as_worded"], "status_class": a["status_class"],
                    "title": a["document_title"] or a["proceeding_title"], "sentence": a["sentence"], "url": a["source_url"],
                    "page": a["page"], "grids": a["grids"], "read": rd["read"] if rd else None,
                    "read_model": rd["model_id"] if rd else None,
                    "sentence_from": a.get("sentence_from", ""), "row_flag": a.get("row_flag", ""),
                    "this_month": bool(score[0]), "date_ahead": ahead[0].isoformat() if ahead else "",
                    "directness": score[1], "breadth": score[2], "table_license": a["table_license"],
                    "show_sentence": show, "sentence_withheld": "" if show else withheld_words(a["regulator"], terms),
                    "id": a["event_id"]})
        if len(out) == TEN:
            break
    return out, len(pool)


def ten_markdown(rows, pool, today, full=False):
    """The one page of the ten rules, written by code so that every sentence is the table's, character for character.
    full=False (docs/accelerator/rules_in_motion.md, in the public repository): a row of a regulator whose terms
    restrict copying, or were not read, shows its facts, its link and the model's read, not its sentence or its worded
    status. full=True (the session's report, not in the repository): every row with its sentence."""
    out = [
        "# Rules in motion: the ten a datacenter buyer most needs to know this month",
        "",
        f"As of {today.isoformat()} (UTC). Written by `warehouse/derived/rules_in_motion.py --ten --ten-doc` from the tables "
        "`large_load_rules` (public) and `large_load_rules_internal` and the model's one-line reads in "
        "`large_load_rule_reads`; nothing here is typed by hand. Method: "
        "[`docs/methods/datacenter_cost.md`](../methods/datacenter_cost.md), section \"Rules in motion\".",
        "",
        "**Not legal advice, and not complete**: a docket system cannot be proved complete from outside. Federal "
        "regulators and state utility commissions only; nothing municipal. A row's sentence is the regulator's own, "
        "proved by code as a literal substring of the saved document; where it is cut from the regulator's own record "
        "of an order (a docket card, meeting minutes, a news release) and not from the order's text, the row says so. "
        "Each \"read\" line is **a model's read**, not the regulator's words."
        + ("" if full else " Where a regulator's own terms restrict copying, or no terms of it were read, this page gives "
           "the row's facts, the link to the regulator's document and the model's read, and not the sentence."),
        "",
        f"**How the ten were chosen**, by rule, from the {pool} dockets with a row in motion (an open proceeding, or an order "
        "of the last 12 months), one row a docket (its newest): (1) this month first: the document is dated in the "
        f"{MONTH_DAYS} days up to {today.isoformat()}, or the row states a deadline, hearing or effective date in the {MONTH_DAYS} days "
        "after it; (2) then how directly it sets when or at what cost a large load is served: large-load "
        "interconnection and large-load tariffs (minimum terms, collateral) before who pays for transmission, before "
        "interconnection reform at large; (3) then breadth: a federal action before a state's, more grids named before "
        f"fewer; (4) then the newest. At most {TEN_PER_REGULATOR} rows a regulator. A contract or agreement with one customer "
        "is never among the ten: it sets no rule for others.",
        "",
    ]
    if len(rows) < TEN:
        out += [f"**Fewer than ten qualify: {len(rows)}.**", ""]
    for r in rows:
        show = full or r["show_sentence"]
        if show:
            status = (f"\"{r['status_as_worded']}\" ({r['status_class']})" if r["status_as_worded"] else f"{r['status_class']} (the regulator words no status)")
        else:
            status = r["status_class"]
        where = f", page {r['page']}" if r["page"] else ""
        why = "this month" if r["this_month"] else "not this month"
        if r["date_ahead"]:
            why += f" (the row states {r['date_ahead']})"
        out += [f"## {r['rank']}. {r['regulator']}, {r['docket']}", ""]
        out += [f"- **What**: {r['title']} ({r['row_kind']}; {r['topic']})" if show else f"- **What**: {r['row_kind']}; {r['topic']}"]
        out += [f"- **Date**: {r['date']}. **Status**: {status}."]
        if show:
            out += [f"- **The sentence** (cut from: {r['sentence_from']}): \"{r['sentence']}\""]
        else:
            out += [f"- **The sentence**: not shown here. {r['sentence_withheld']}."]
        out += [f"- **Source**: <{r['url']}>{where}",
                ("- **A model's read** (" + r["read_model"] + "): " + r["read"]) if r["read"] else "- **A model's read**: no read yet"]
        if r["row_flag"]:
            out += [f"- Flag: {r['row_flag']}."]
        out += [f"- Why here: {why}; directness {r['directness']}; breadth {r['breadth']}" + (f"; grids named: {r['grids']}" if r["grids"] else "") + ".", ""]
    return "\n".join(out)


def write_whole(path, obj):
    """The file written whole beside itself, then renamed over the old one (a reader never sees half a file)."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1, allow_nan=False)
        f.write("\n")
    os.replace(tmp, path)


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW: the site's file of rules in motion for large loads")
    ap.add_argument("--in-dir", action="append", default=[], help="a directory of tables; may be given more than "
                    "once, the first that holds a table wins (default: warehouse/output)")
    ap.add_argument("--out-dir", help="a trial run: rules.json under this directory; nothing in site/data")
    ap.add_argument("--ten", help="also write the ten rules of the month to this file (JSON); no site file changes for it")
    ap.add_argument("--ten-full", action="store_true", help="with --ten-doc: every row with its sentence (for a report that is "
                    "not in the repository); without it, a restricted regulator's sentence is not written")
    ap.add_argument("--ten-doc", help="with --ten: also write the one page (docs/accelerator/rules_in_motion.md)")
    ap.add_argument("--today", help="YYYY-MM-DD (default: today, UTC): the day the 12 months are counted back from")
    args = ap.parse_args(argv)
    dirs = [os.path.abspath(d) for d in args.in_dir] or [os.path.join(ROOT, "warehouse", "output")]
    today = dt.date.fromisoformat(args.today) if args.today else dt.datetime.now(dt.timezone.utc).date()
    obj = build(dirs, today)
    text = json.dumps(obj, ensure_ascii=False)
    if chr(0x2014) in text:
        raise RuntimeError("an em dash in the file: a row's own words hold one; it is not written")
    path = os.path.join(os.path.abspath(args.out_dir), "rules.json") if args.out_dir else SITE_FILE
    write_whole(path, obj)
    shown = {g: len(v["rows"]) for g, v in obj["grids"].items()}
    reads = sum(1 for v in obj["grids"].values() for r in v["rows"] if r["read"]) + sum(1 for r in obj["federal_all_grids"] if r["read"])
    print(f"rules.json: {path}")
    print(f"  rows by grid {shown}; Federal, all grids {len(obj['federal_all_grids'])}; row places with a read {reads}; "
          f"not on the page {obj['not_on_page']['count']}")
    for n in obj["notes"]:
        print(f"  note: {n}")
    if args.ten:
        rows, pool = ten_rules(dirs, today)
        write_whole(os.path.abspath(args.ten), {"as_of": today.isoformat(), "pool": pool, "rows": rows})
        print(f"  the ten: {len(rows)} rows from a pool of {pool} dockets in motion: {os.path.abspath(args.ten)}")
        if args.ten_doc:
            text = ten_markdown(rows, pool, today, full=args.ten_full)
            if chr(0x2014) in text:
                raise RuntimeError("an em dash in the ten rules' page: a sentence holds one; the page is not written")
            with open(os.path.abspath(args.ten_doc) + ".tmp", "w", encoding="utf-8", newline="\n") as f:
                f.write(text)
            os.replace(os.path.abspath(args.ten_doc) + ".tmp", os.path.abspath(args.ten_doc))
            print(f"  the ten, one page: {os.path.abspath(args.ten_doc)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
