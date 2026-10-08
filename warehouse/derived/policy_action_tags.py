#!/usr/bin/env python3
"""Tags of the policy actions held: large loads, interconnection, transmission cost, tax credits (session 154).

Energy Research Warehouse (ERW). Reads policy_actions (every row held) and writes policy_action_tags: one row for
each action and tag, with the term that matched and the field it matched in, so that a person can redo it. The rule
is written down in warehouse/config/policy_tag_rules.json, which this code reads and applies; no model reads a row
and no request is made. Method: docs/methods/policy_action_tags.md.

    python warehouse/derived/policy_action_tags.py                       # reads and writes warehouse/output
    python warehouse/derived/policy_action_tags.py --in-dir DIR --out-dir DIR2   # a trial: nothing in warehouse/output
    python warehouse/derived/policy_action_tags.py --sample 40 --seed 154 --in-dir DIR --out-dir DIR2
                                                                         # also writes the two samples a person reads

Dockets listed by number (the rule file's "dockets"): a notice whose title holds only the parties' names takes the
tags of a proceeding whose own order was read, when its docket field holds that docket number; the matched field is
then "docket". The municipal rule, the agencies in scope and each tag's exclusions hold for these rows too.

How a row is read (the rule file says the same): the title, the abstract and (session 157, rule version 3) the first
paragraph of the action's printed text in the Federal Register, each on its own, lower case, every hyphen and dash a
space, white space collapsed, the stripped phrases (a company's name) taken out. A table from before session 157
has no first_paragraph: the field is then empty and the rule reads the other two. A term matches as
whole words in order. An action with a municipal phrase in its title or abstract is never tagged. A tag's own
exclusions (a phrase in the title or abstract, a docket prefix) keep an action out of that tag only.

The table is a snapshot: a later rule replaces the rows (an action a corrected rule no longer tags must leave).
"""

import argparse
import datetime as dt
import json
import os
import random
import re
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import iso_prices as ip  # noqa: E402

NAME, ACTIONS = "policy_action_tags", "policy_actions"
RULES = os.path.join(ROOT, "warehouse", "config", "policy_tag_rules.json")
SOURCE = "erw:policy_action_tags"
METHOD = "docs/methods/policy_action_tags.md"
METHOD_URL = "https://github.com/SamuelEnrique/erw/blob/main/" + METHOD
COLS = ["event_id", "event_date", "event_type", "parties", "entity_ids", "mw", "price", "currency", "status", "source",
        "source_url", "action_event_id", "tag", "matched_term", "matched_field", "agency", "action_type", "title",
        "action_url", "rule_version", "retrieved_at"]
DASHES = "-" + chr(0x2010) + chr(0x2011) + chr(0x2012) + chr(0x2013) + chr(0x2014)


def load_rules(path=RULES):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def norm(s):
    """Lower case, every hyphen and dash a space, white space collapsed."""
    s = (s or "").lower()
    for d in DASHES:
        s = s.replace(d, " ")
    return re.sub(r"\s+", " ", s).strip()


def has(term, text):
    """The term's words stand in the text as whole words, in order."""
    return re.search(r"(?<![a-z0-9])" + re.escape(norm(term)) + r"(?![a-z0-9])", text) is not None


def docket_prefixes(docket):
    """The letters that begin each docket number of the row (FERC writes 'Docket No. CP13-499-006;Docket No. ...')."""
    out = []
    for part in re.split(r"[;,]", docket or ""):
        m = re.search(r"\b([A-Z]{2})\d{2}-\d", part)
        if m:
            out.append(m.group(1))
    return out


def tag_action(row, rules):
    """[{tag, matched_term, matched_field}] for one action; [] when none or when the action is municipal."""
    fields = {}
    for f in rules["fields_matched"]:
        t = norm(row.get(f, ""))
        for s in rules["strip"]:
            t = t.replace(norm(s), " ")
        fields[f] = re.sub(r"\s+", " ", t).strip()
    both = " || ".join(fields.values())
    scope = rules["agencies_in_scope"]
    if row.get("agency", "") not in scope["federal"] + scope["state"]:
        return []
    if row.get("action_type", "") not in rules["action_types_in_scope"]:
        return []
    if any(has(t, both) for t in rules["municipal"]["terms"]):
        return []
    prefixes = docket_prefixes(row.get("docket", ""))
    out = []
    for tag, spec in rules["tags"].items():
        if any(has(t, both) for t in spec.get("exclude_any", [])):
            continue
        if any(p in spec.get("exclude_docket_prefix", []) for p in prefixes):
            continue
        if any(c.lower() in (row.get("docket", "") or "").lower() for c in spec.get("exclude_docket_contains", [])):
            continue
        hit = None
        for f in rules["fields_matched"]:
            for t in spec["terms"]:
                if has(t["term"], fields[f]) and (not t.get("needs_any") or any(has(n, both) for n in t["needs_any"])):
                    hit = {"tag": tag, "matched_term": t["term"], "matched_field": f}
                    break
            if hit:
                break
        if not hit:   # the dockets listed by number: a notice whose title is only the parties' names
            many = len([x for x in re.split(r"[;,]", row.get("docket", "") or "") if re.search(r"\d", x)]) > rules.get("dockets", {}).get("max_dockets_in_a_notice", 3)
            for d in ([] if many else rules.get("dockets", {}).get("list", [])):
                if tag in d["tags"] and docket_holds(row.get("docket", ""), d["docket"]):
                    hit = {"tag": tag, "matched_term": d["docket"], "matched_field": "docket"}
                    break
        if hit:
            out.append(hit)
    return out


def docket_holds(docket, number):
    """The row's docket field holds the docket number as a whole number (EL26-67 stands in 'Docket No. EL26-67-000',
    not in 'EL26-670-000')."""
    return re.search(r"(?<![A-Za-z0-9])" + re.escape(number) + r"(?![0-9])", docket or "") is not None


def read_events(path):
    with open(path, encoding="utf-8") as f:
        n = 0
        for ln in f:
            if not ln.startswith("#"):
                break
            n += 1
    return pd.read_csv(path, skiprows=n, dtype=str, keep_default_na=False)


def build(actions, rules, now):
    rows = []
    for r in actions.to_dict("records"):
        for h in tag_action(r, rules):
            rows.append({"event_id": f"{r['event_id']}#{h['tag']}", "event_date": r["event_date"][:10],
                         "event_type": "policy_tag", "parties": r.get("parties", ""), "entity_ids": "", "mw": "",
                         "price": "", "currency": "", "status": "", "source": SOURCE, "source_url": METHOD_URL,
                         "action_event_id": r["event_id"], "tag": h["tag"], "matched_term": h["matched_term"],
                         "matched_field": h["matched_field"], "agency": r["agency"], "action_type": r["action_type"],
                         "title": r["title"], "action_url": r["source_url"], "rule_version": str(rules["version"]),
                         "retrieved_at": now})
    return pd.DataFrame(rows, columns=COLS).sort_values(["event_date", "event_id"], ascending=[False, True]).reset_index(drop=True)


def samples(actions, table, n, seed):
    """n tagged and n untagged actions, drawn by the seed from the actions in event_id order (a person reads them)."""
    ids = sorted(actions["event_id"])
    tagged = sorted(set(table["action_event_id"]))
    untagged = [i for i in ids if i not in set(tagged)]
    rnd = random.Random(seed)
    return rnd.sample(tagged, min(n, len(tagged))), rnd.sample(untagged, min(n, len(untagged)))


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW: tags of the policy actions held")
    ap.add_argument("--in-dir", help="read policy_actions from this directory instead of warehouse/output")
    ap.add_argument("--out-dir", help="a trial run: every output under this directory; nothing in warehouse/output")
    ap.add_argument("--rules", default=RULES)
    ap.add_argument("--sample", type=int, default=0, help="also write this many tagged and untagged actions to read")
    ap.add_argument("--seed", type=int, default=154)
    args = ap.parse_args(argv)
    in_dir = os.path.abspath(args.in_dir) if args.in_dir else ip.OUT_DIR
    if args.out_dir:
        ip.set_out_dir(args.out_dir)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{NAME}_{run_id}.log"))
    try:
        rules = load_rules(args.rules)
        actions = read_events(os.path.join(in_dir, ACTIONS + ".csv"))
        now = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
        table = build(actions, rules, now)
        counts = table["tag"].value_counts().to_dict()
        by_tag = ", ".join(f"{t} {counts.get(t, 0)}" for t in rules["tags"])
        n_actions = table["action_event_id"].nunique()
        header = [
            "Energy Research Warehouse (ERW): tags of the policy actions held: large loads, interconnection, "
            "transmission cost, tax credits (session 154)",
            "Shape: events (docs/datastandard.md v0), event_type policy_tag; one row for each action and tag; a snapshot "
            "(a later rule replaces the rows). event_date is the action's. matched_term is the rule's term that "
            "matched and matched_field the field it matched in (title, abstract, first_paragraph: the first paragraph of "
            "the printed text, or docket: a docket the rule lists by number); action_url is the action's own document.",
            f"Rule: warehouse/config/policy_tag_rules.json, version {rules['version']}, applied by code; no model "
            f"reads a row. Method: {METHOD}.",
            f"Retrieved: {run_id} (UTC) by warehouse/derived/policy_action_tags.py",
            f"Run log: warehouse/output/logs/{NAME}_{run_id}.log",
            f"Derived from: {ACTIONS}",
            f"Actions read: {len(actions)}; actions tagged: {n_actions}; rows: {len(table)} ({by_tag}).",
            "Source: erw:policy_action_tags. License: public (US and state government publications; the tags are "
            "the ERW's own).",
        ]
        if len(table):
            ip.write_snapshot(table, NAME, header, log, COLS)
        else:
            raise RuntimeError("the rule tagged no action: no table is written")
        ip.update_sources([dict(source=SOURCE, publisher="Energy Research Warehouse (ERW)",
                                report="Tags of the policy actions held, by a written rule (large loads, "
                                       "interconnection, transmission cost, tax credits)",
                                report_url=METHOD_URL, document_list="", license="public", tables=[NAME])])
        detail = f"{len(actions)} actions read, {n_actions} tagged, {len(table)} rows ({by_tag}); rule version {rules['version']}"
        log(detail)
        print(f"{NAME}: {detail}")
        if args.sample:
            tg, un = samples(actions, table, args.sample, args.seed)
            by = actions.set_index("event_id")
            tags_of = table.groupby("action_event_id")[["tag", "matched_term", "matched_field"]].apply(
                lambda g: "; ".join(f"{a} [{b} in {c}]" for a, b, c in zip(g["tag"], g["matched_term"], g["matched_field"])))
            for label, ids in (("tagged", tg), ("untagged", un)):
                path = os.path.join(ip.OUT_DIR, f"{NAME}_sample_{label}_seed{args.seed}_v{rules['version']}.txt")
                with open(path, "w", encoding="utf-8", newline="\n") as f:
                    f.write(f"# {len(ids)} {label} actions, random.Random({args.seed}).sample over the sorted event ids "
                            f"(tagged drawn first), rule version {rules['version']}\n")
                    for k, i in enumerate(ids, 1):
                        r = by.loc[i]
                        f.write(f"\n[{k}] {i} | {r['agency']} | {r['action_type']} | {r['event_date'][:10]} | docket: {r['docket']}\n"
                                f"    TAGS: {tags_of.get(i, '(none)')}\n    TITLE: {r['title']}\n    ABSTRACT: {r['abstract']}\n")
                print(f"sample written: {path}")
        ip.write_status(NAME, run_id, [dict(table=NAME, market="all", status="ok", detail=detail)])
    except Exception as exc:
        log(f"FAILED: {exc!r}")
        ip.write_status(NAME, run_id, [dict(table=NAME, market="all", status="failed", detail=repr(exc)[:300])])
        log.close()
        raise
    log.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
