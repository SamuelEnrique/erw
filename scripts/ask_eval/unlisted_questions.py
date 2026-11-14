#!/usr/bin/env python3
"""Session 6162 (chain 282): twelve questions about tables of the ERW's record that a visitor's chat cannot read, other
than the six of the week of 9 November 2026 (those are questions_newtables_live.yaml).

Energy Research Warehouse (ERW). No model call. Reads only: the license record's verdicts (site/data/table_verdicts.json)
and the live catalogue with a visitor's key (lab_questions.py's reader). Writes warehouse/chat/eval/questions_unlisted.yaml.

    python scripts/ask_eval/unlisted_questions.py            writes the file
    python scripts/ask_eval/unlisted_questions.py --check    exit 1 when a table named here can now be read by a visitor's chat

Why: the record holds 537 tables and the catalogue a visitor's chat lists 140. Asked on 14 November 2026 about six tables
out of its reach, the chat hunted through other tables and three times answered from a neighbour (chain 281). The loop
now refuses such a question by the table's name. That was measured on six tables; these twelve name others: public
tables of the record that are not loaded (most of the 397 are of this kind: the world tables), tables whose license is
not settled, and two whose names have two words, which the loop's word match does not look for by design (a short name
would be found by chance): for those the tools' own words must do.

Every key is a refusal: kind not_readable (eval_s1113.py not_readable_grade), no figure, nothing withheld (this machine
holds none of these tables, and none is needed: any figure at all is wrong).
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
EVAL = os.path.join(ROOT, "warehouse", "chat", "eval")
OUT = os.path.join(EVAL, "questions_unlisted.yaml")
TODAY = "2026-11-14"
OUT_OF_REACH = "not in the warehouse|license needed|live set|Redivis|not loaded"

# (id, the table, the question in a reader's words that hold every word of the table's name, whether the name has
# three words or more so that the loop's word match finds it)
ASKED = [
    ("ul01", "aeso_alberta_load_hourly", "What was Alberta's highest hourly load in 2025, by the AESO's figures?"),
    ("ul02", "boem_offshore_platforms", "How many offshore platforms does BOEM list in the Gulf of Mexico?"),
    ("ul03", "census_metro_population", "What is the population of the Houston metro area in the Census figures the warehouse holds?"),
    ("ul04", "boem_renewable_leases", "How many renewable energy leases has BOEM issued off the Atlantic coast?"),
    ("ul05", "caiso_curtailment_intervals", "In how many intervals did CAISO report wind and solar curtailment in May 2026?"),
    ("ul06", "afdc_station_counts_annual", "What do the AFDC's annual station counts give for electric vehicle charging stations in Texas in 2025?"),
    ("ul07", "usace_nid_dams", "How many dams does the USACE's NID list in California?"),
    ("ul08", "large_load_connection_rules", "How many large-load connection rules does the warehouse hold for utilities in PJM?"),
    ("ul09", "utility_large_load_tariffs", "How many utility large-load tariffs does the warehouse hold?"),
    ("ul10", "nyiso_load_queue", "How many MW of load are in NYISO's load queue?"),
    ("ul11", "eia860_boilers", "How many boilers does EIA-860 list at power plants in Texas?"),
    ("ul12", "wfigs_wildfires", "How many wildfires does WFIGS record in California in 2025?"),
]


def verdicts():
    with open(os.path.join(ROOT, "site", "data", "table_verdicts.json"), encoding="utf-8") as f:
        return json.load(f)


def readable():
    """The tables a visitor's chat can read today: the live catalogue's in_live_set yes or review."""
    sys.path.insert(0, HERE)
    import lab_questions as L
    return {t for t, c in L.catalogue().items() if c.get("in_live_set") in ("yes", "review")}, set(L.catalogue())


def build():
    v = verdicts()
    can, listed = readable()
    qs, moved = [], []
    for qid, table, question in ASKED:
        if table not in v:
            raise SystemExit(f"{table} is not a table of the record (site/data/table_verdicts.json)")
        if table in can:
            moved.append(table)
        words = len([w for w in table.split("_") if w])
        qs.append({"id": qid, "sector": "unlisted", "kind": "not_readable", "grid": "none", "via": "general", "question": question, "expected": [], "tolerance": 0.01,
                   "text": [OUT_OF_REACH], "tables": [], "refuse": True, "hold": False, "count": False, "withheld": [], "withheld_text": [],
                   "note": (f"{table} is a table of the ERW's record (verdict {v[table][0]}) that a visitor's chat cannot read"
                            f" ({'the catalogue lists it, not loaded' if table in listed else 'not in the live catalogue'}): a refusal and no figure. "
                            + ("Its name has three words or more: the loop names it." if words >= 3 else "Its name has two words: the loop's word match does not look for it, and the tools' words must do."))})
    return qs, moved


def yaml_text(qs):
    lines = [f"# Energy Research Warehouse (ERW): {len(qs)} questions about tables of the record that a visitor's chat cannot read, other than the week's six",
             "# (session 6162, chain 282), written by scripts/ask_eval/unlisted_questions.py. Every key is a refusal with no figure (kind not_readable).",
             f"today: '{TODAY}'", "questions:"]
    for x in qs:
        lines += [f"- id: {x['id']}", f"  sector: {x['sector']}", f"  kind: {x['kind']}", f"  grid: {x['grid']}", f"  via: {x['via']}",
                  f"  question: {json.dumps(x['question'])}", f"  expected: {json.dumps(x['expected'])}", f"  tolerance: {x['tolerance']}",
                  f"  text: {json.dumps(x['text'])}", f"  tables: {json.dumps(x['tables'])}", "  refuse: true", "  hold: false", "  count: false",
                  f"  withheld: {json.dumps(x['withheld'])}", f"  withheld_text: {json.dumps(x['withheld_text'])}", f"  note: {json.dumps(x['note'])}"]
    text = "\n".join(lines) + "\n"
    if chr(0x2014) in text or chr(0x2013) in text:
        raise SystemExit("a dash in the output")
    return text


def main(argv):
    qs, moved = build()
    if "--check" in argv:
        print("a visitor's chat can now read: " + ", ".join(moved) if moved else "none of the twelve tables can be read by a visitor's chat today")
        return 1 if moved else 0
    if moved:
        raise SystemExit("a visitor's chat can read " + ", ".join(moved) + ": its question is no refusal; take it out of ASKED")
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(yaml_text(qs))
    print(f"wrote {os.path.relpath(OUT, ROOT)}: {len(qs)} questions")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
