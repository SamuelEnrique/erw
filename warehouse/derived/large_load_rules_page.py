#!/usr/bin/env python3
"""The large-load rules page file (chain 302, session 7200).

Energy Research Warehouse (ERW). Writes `site/data/siting/large_load_rules.json`, which the All grids tab of
/cost-of-power and the monitor of /policy read, from three warehouse tables as the connector
`warehouse/connectors/large_load_research.py` wrote them (docs/methods/large_load_research.md):

    utility_large_load_rules          one row a utility's (or a state commission's) large-load rule (100 public, 22 held)
    utility_large_load_rule_changes   one row a filing, order or event, 15 August to 13 November 2026 (94 public, 4 held)
    state_large_load_laws             one row a state law or bill of the 2025 and 2026 sessions (27 public, 1 held)

What it writes, and what it does not:

- Every public row, each field as the table prints it with its cite. Nothing is shortened, summed or converted.
- A row held for a license (the tables' headers name them) is written as its id, its utility or bill and its state only,
  so the page can draw the row with "license needed" in every cell. Its state and ISO or region are read from the
  research file as committed (`docs/research/large_load/utilities_2026-11-13.csv`): a classification, not a cited value.
  No other column of a held row is read.
- A public row's withheld field (`x_withheld`) is written as withheld, no value and no cite.
- A field the ERW's own registry holds (`x_held`, a pointer to `warehouse/sources/large_load_tariffs/<file>.yaml`) is
  written as the registry's own words and page where the registry file is public and prints them, else as the pointer;
  a registry file whose license is not public is written as withheld.
- A queue field that points to another row of the same utility (`see row: <rule>`) is written as that row's id.
- Which tab rows a rule belongs to: RULE_EIA below maps each rule (public or held) to the EIA utility numbers the tab's
  rows name (site/data/siting/utility.json); STATEWIDE maps a rule that binds every utility of a state (or of a state
  inside one grid). A utility the research read and found no rule for is in NO_RULE, with the research note's own
  words (docs/research/large_load/notes/<slug>.md, its "No large-load rule found" line).

- What the research records for a state with no law in the table (session 7204): the two files of
  docs/research/large_load/legislation/ list, by state, what was searched where no law was found (`none_found`) and a
  bill that was read and is withheld (`withheld`: Texas S.B. 6, whose copy sits on a path the legislature's robots
  file disallows). They are written as `law_searches`, one a state that has no row in the laws table, so the page can
  say "none found", "not read" or "read and not shown" in place of nothing. The research's own words are carried
  except where they hold a lead from the news, which is not verified: there the page names the file.

No request is made to anyone and no model is called. It writes nothing but the one site file.

    python warehouse/derived/large_load_rules_page.py                 # tables from warehouse/output
    python warehouse/derived/large_load_rules_page.py --in-dir DIR    # tables from DIR
    python warehouse/derived/large_load_rules_page.py --check         # build in memory and compare with the file
"""

import argparse
import csv
import datetime as dt
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUTPUT = os.path.join(ROOT, "warehouse", "output")
SITE_FILE = os.path.join(ROOT, "site", "data", "siting", "large_load_rules.json")
RESEARCH = os.path.join(ROOT, "docs", "research", "large_load")
REGISTRY = os.path.join(ROOT, "warehouse", "sources")

RULES, CHANGES, LAWS = "utility_large_load_rules", "utility_large_load_rule_changes", "state_large_load_laws"
FIELDS = ["threshold_mw", "min_demand", "contract_term", "collateral", "exit_fee", "study_timeline", "connection_timeline", "queue_size"]
RULE_STATUSES = ["in effect", "approved", "proposed", "ordered", "denied", "withdrawn"]
LAW_STATUSES = ["in effect", "enacted", "passed", "passed one chamber", "introduced", "vetoed", "died"]
NOT_PUBLISHED = "not published"

# The grid a rule's x_iso_region names, as the tab's filter words it. The column is the ERW's classification.
ISOS = [("ERCOT", "ercot"), ("PJM", "pjm"), ("MISO", "miso"), ("SPP", "spp"), ("NYISO", "nyiso"), ("CAISO", "caiso"), ("ISO-NE", "isone"), ("ISO New England", "isone")]

# Each rule (public or held) to the EIA utility numbers of site/data/siting/utility.json it is that utility's rule for.
# Matched by hand on the utility's name and state (session 7200); a test holds every id to the tables and every number
# to the tab's utility file. A rule whose utility no tab row names is not here: it is in the table under the tab.
RULE_EIA = {
    "entergy-05": ["814"], "entergy-06": ["814"], "entergy-07": ["814"],                 # Entergy Arkansas
    "southwest_california-01": ["14328"],                                                 # PG&E (Electric Rule 30)
    "entergy-01": ["11241"], "entergy-02": ["11241"],                                     # Entergy Louisiana
    "great_lakes-05": ["4254"],                                                           # Consumers Energy (held)
    "xcel_plains-01": ["13781"],                                                          # Northern States Power, Minnesota
    "northeast-03": ["4226"], "northeast-05": ["4226"],                                   # Con Edison
    "northeast-09": ["11171"],                                                            # LIPA
    "northeast-04": ["3249"],                                                             # Central Hudson
    "northeast-07": ["13573"],                                                            # Niagara Mohawk (National Grid)
    "northeast-08": ["13511", "16183"],                                                   # NYSEG and RG&E
    "ameren_evergy_spp-10": ["14063"],                                                    # OG&E
    "texas-02": ["44372"],                                                                # Oncor
    "texas-03": ["8901"],                                                                 # CenterPoint Houston (held)
    "texas-05": ["16604"],                                                                # CPS Energy, City of San Antonio (held)
    "texas-06": ["1015"],                                                                 # Austin Energy
    "northeast-10": ["54913", "11804"],                                                   # NSTAR and Massachusetts Electric (held)
}
# A rule that binds every utility of a state, or of a state inside one grid (the rule's own words name them).
STATEWIDE = {
    "texas-01": {"state": "TX", "grid": "ercot"},     # 16 TAC 25.194: TSPs and DSPs in ERCOT
    "xcel_plains-02": {"state": "MN", "grid": None},  # Minn. Stat. 216B.1622: all Minnesota public utilities
    "entergy-03": {"state": "LA", "grid": None},      # the Louisiana PSC's Lightning Amendment
    "entergy-04": {"state": "LA", "grid": None},      # the Louisiana PSC's large-load guidelines
}
# Utilities the tab's rows name that the research read and found no rule for: EIA number to the note's slug.
NO_RULE = {
    "12685": "entergy_mississippi", "9273": "aes_indiana", "15470": "duke_energy_indiana", "5487": "duquesne_light",
    "66101": "firstenergy_pennsylvania", "7601": "green_mountain_power", "17609": "southern_california_edison",
    "11208": "ladwp", "14626": "pedernales_electric", "55937": "entergy_texas",
}


def header_of(path):
    with open(path, encoding="utf-8") as fh:
        return [ln[2:].rstrip("\n") for ln in fh if ln.startswith("# ")]


def rows_of(path):
    with open(path, encoding="utf-8", newline="") as fh:
        body = "".join(ln for ln in fh if not ln.startswith("#"))
    return list(csv.DictReader(io.StringIO(body)))


def held_of(head):
    """The rows a table's header names as held for a license: [(id, name)]."""
    line = next((ln for ln in head if ln.startswith("Rows:")), "")
    m = re.search(r"held for a license and not written \(\d+\): (.*)$", line)
    if not m:
        return []
    out, text = [], m.group(1).rstrip(".")
    # each entry is "<id> (<name>)", entries separated by "; " outside the parentheses
    depth, cur = 0, ""
    for ch in text:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == ";" and depth == 0:
            out.append(cur.strip())
            cur = ""
            continue
        cur += ch
    if cur.strip():
        out.append(cur.strip())
    pairs = []
    for e in out:
        mm = re.match(r"^(\S+) \((.*)\)$", e)
        if mm:
            pairs.append((mm.group(1), mm.group(2)))
    return pairs


def retrieved_of(head):
    line = next((ln for ln in head if ln.startswith("Retrieved:")), "")
    m = re.search(r"Retrieved: (\S+)", line)
    return m.group(1) if m else ""


def grid_of(region):
    for word, key in ISOS:
        if region.startswith(word):
            return key
    return "other"


def registry_value(pointer, field):
    """A held field's value from the ERW's registry file it points to: (value, cite, withheld)."""
    rel = pointer.strip()
    path = os.path.join(REGISTRY, *rel.split("/"))
    if not os.path.exists(path):
        return None, f"held in the ERW's registry: {rel}", False
    import yaml
    with open(path, encoding="utf-8") as fh:
        y = yaml.safe_load(fh) or {}
    if str(y.get("license", "")).strip() != "public":
        return None, "", True
    terms = y.get("terms") or {}
    key = {"min_demand": "min_bill", "contract_term": "term", "collateral": "collateral", "exit_fee": "exit_fee"}.get(field)
    where = f"the ERW's registry, {rel} ({y.get('document', '')}, {y.get('document_url', '')})"
    if key and isinstance(terms.get(key), dict) and terms[key].get("text"):
        t = terms[key]
        return t["text"], f"p. {t.get('page', '')}: \"{t['text']}\" ({where})", False
    if field == "threshold_mw":
        fig = next((f for f in (y.get("figures") or []) if f.get("variable") == "min_demand_mw" and f.get("printed")), None)
        if fig:
            return fig["printed"], f"p. {fig.get('page', '')}: \"{fig['printed']}\" ({where})", False
        if y.get("sector"):
            return str(y["sector"]), f"the registry's sector line ({where})", False
    return None, f"held in the ERW's registry: {rel}", False


def held_pointers(text):
    """x_held: 'field: registry/file.yaml; field: ...' to {field: path}."""
    out = {}
    for part in (text or "").split(";"):
        if ":" in part:
            k, v = part.split(":", 1)
            out[k.strip()] = v.strip()
    return out


def field_of(r, f, rows_by_name, withheld, held):
    v, cite = r.get(f"x_{f}", ""), r.get(f"x_{f}_cite", "")
    if f in withheld:
        return {"kind": "withheld"}
    if f in held:
        val, c, wh = registry_value(held[f], f)
        if wh:
            return {"kind": "withheld", "registry": held[f]}
        if val is None:
            return {"kind": "registry", "registry": held[f], "cite": c}
        return {"kind": "value", "v": val, "cite": c, "registry": held[f]}
    if v == NOT_PUBLISHED:
        return {"kind": "not published", "cite": cite}
    if v.startswith("see row:"):
        name = v[len("see row:"):].strip()
        # the row whose rule name the pointer prints: the same utility's first, then the same group's, then any
        cands = [x for x in rows_by_name["*"] if x["x_row_id"] != r["x_row_id"] and (x["x_rule_name"].startswith(name[:60]) or name.startswith(x["x_rule_name"][:60]))]
        cands.sort(key=lambda x: (x["x_utility"] != r["x_utility"], x["x_group"] != r["x_group"]))
        target = cands[0] if cands else None
        if target is None:
            # the row it names may be one held for a license: its id only, which the page draws as "license needed"
            held_row = next((x for x in rows_by_name["held"] if x["rule_name"].startswith(name[:60])), None)
            if held_row:
                return {"kind": "see", "row": held_row["row_id"], "held": True}
        return {"kind": "see", "row": target["x_row_id"] if target else None, "name": name}
    if not v:
        return {"kind": "empty"}
    return {"kind": "value", "v": v, "cite": cite}


def note_line(slug):
    path = os.path.join(RESEARCH, "notes", f"{slug}.md")
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    m = re.search(r"^- (No large-load rule found\..*)$", text, re.M)
    if not m:
        raise ValueError(f"{path}: no 'No large-load rule found' line")
    line = m.group(1)
    # the note's leads from the news are not verified: they are not carried to the page
    line = re.split(r"\s*Leads only", line)[0].strip()
    return line


LEAD = re.compile(r"\bnews\b|\blead\b|unconfirmed|described in", re.I)
LEGISLATION = ("midwest_northeast.json", "south_west.json")


def law_searches(have):
    """What the research's legislation files record for each state with no row in the laws table: [{state, kind, bill,
    words, source}], kind "none found", "not read" or "withheld". `have` is the states the table holds a row for."""
    out = []
    for name in LEGISLATION:
        rel = f"docs/research/large_load/legislation/{name}"
        with open(os.path.join(RESEARCH, "legislation", name), encoding="utf-8") as fh:
            d = json.load(fh)
        for x in d.get("withheld", []):
            if x["state"] in have:
                raise ValueError(f"{rel}: {x['state']} {x['bill']} is withheld by the research and the table holds a row for the state")
            out.append({"state": x["state"], "kind": "withheld", "bill": x["bill"], "words": " ".join(x["reason"].split()), "source": rel})
        for x in d.get("none_found", []):
            if x["state"] in have:
                continue   # the state has a law in the table: what else was searched there is the research's own note
            words = " ".join(x["searched"].split())
            # "not read": the research says so in its first words, or that it read nothing (a site that answered 404)
            kind = "not read" if words.lower().startswith("not read") or "nothing read" in words.lower() else "none found"
            # a lead from the news is not verified: its words stay in the research file, and the page names the file
            out.append({"state": x["state"], "kind": kind, "bill": "", "words": "" if LEAD.search(words) else words, "source": rel})
    states = [x["state"] for x in out]
    if len(states) != len(set(states)):
        raise ValueError(f"the legislation files name a state twice: {sorted(s for s in set(states) if states.count(s) > 1)}")
    return sorted(out, key=lambda x: x["state"])


def build(in_dir=OUTPUT):
    paths = {t: os.path.join(in_dir, f"{t}.csv") for t in (RULES, CHANGES, LAWS)}
    for t, p in paths.items():
        if not os.path.exists(p):
            raise FileNotFoundError(f"{t}: {p}")
    rh, ch, lh = (header_of(paths[t]) for t in (RULES, CHANGES, LAWS))
    rules_raw, changes_raw, laws_raw = (rows_of(paths[t]) for t in (RULES, CHANGES, LAWS))
    for r in rules_raw:
        if r["status"] not in RULE_STATUSES:
            raise ValueError(f"{RULES}: status {r['status']!r} of {r['x_row_id']}")
    for r in laws_raw:
        if r["status"] not in LAW_STATUSES:
            raise ValueError(f"{LAWS}: status {r['status']!r} of {r['x_law_id']}")

    research = {r["row_id"]: r for r in rows_of(os.path.join(RESEARCH, "utilities_2026-11-13.csv"))}
    by_name = {"*": rules_raw, "held": [r for r in research.values() if r.get("license") == "internal"]}

    rules = []
    for r in rules_raw:
        withheld = {x for x in (r.get("x_withheld") or "").split(";") if x}
        held = held_pointers(r.get("x_held"))
        rules.append({
            "id": r["x_row_id"], "utility": r["x_utility"], "state": r["x_state"], "region": r["x_iso_region"], "grid": grid_of(r["x_iso_region"]),
            "name": r["x_rule_name"], "status": r["status"], "status_date": r["x_status_date"], "status_cite": r["x_status_cite"],
            "date_kind": r["x_date_kind"], "docket": r["x_docket"], "docket_cite": r["x_docket_cite"],
            "fields": {f: field_of(r, f, by_name, withheld, held) for f in FIELDS},
            "url": r["source_url"], "title": r["x_source_title"], "read": r["x_date_read"], "clause": r["x_quoted_clause"],
            "basis": r["x_license_basis"], "notes": r["x_notes"], "withheld": sorted(withheld),
        })
    rules.sort(key=lambda x: x["id"])  # a fixed order: the page sorts for the reader; the table's own order is its writer's
    held_rules = []
    for rid, name in held_of(rh):
        src = research.get(rid, {})
        if src and src.get("license") != "internal":
            raise ValueError(f"{RULES}: {rid} is named held but the research file reads {src.get('license')!r}")
        held_rules.append({"id": rid, "utility": name, "state": src.get("state", ""), "region": src.get("iso_region", ""), "grid": grid_of(src.get("iso_region", ""))})

    changes = [{
        "id": r["x_change_id"], "date": r["event_date"], "date_printed": r["x_date"], "date_kind": r["x_date_kind"], "group": r["x_group"],
        "utility": r["x_utility"], "state": r["x_state"], "rule": r["x_rule_name"], "affects": r["x_affects"], "docket": r["x_docket"],
        "kind": r["status"], "what": r["x_what"], "cite": r["x_cite"], "url": r["source_url"], "title": r["x_source_title"], "read": r["x_date_read"],
    } for r in changes_raw]
    changes.sort(key=lambda c: (c["date"], c["id"]), reverse=True)
    held_changes = [{"id": i, "utility": n} for i, n in held_of(ch)]

    laws = [{
        "id": r["x_law_id"], "state": r["x_state"], "bill": r["x_bill"], "session": r["x_session"], "title": r["x_title"], "status": r["status"],
        "status_date": r["x_status_date"], "date_kind": r["x_date_kind"], "effective": r["x_effective_date"], "status_cite": r["x_status_cite"],
        "threshold": r["x_threshold_mw"], "threshold_cite": r["x_threshold_mw_cite"], "requirements": r["x_requirements"],
        "url": r["source_url"], "doc": r["x_source_title"], "read": r["x_date_read"], "notes": r["x_notes"],
    } for r in laws_raw]
    laws.sort(key=lambda x: (x["state"], x["bill"]))
    held_laws = [{"id": i, "bill": n, "state": (n.split(" ")[0] if re.match(r"^[A-Z]{2} ", n) else "")} for i, n in held_of(lh)]

    ids = {r["id"] for r in rules} | {r["id"] for r in held_rules}
    for rid in list(RULE_EIA) + list(STATEWIDE):
        if rid not in ids:
            raise ValueError(f"RULE_EIA or STATEWIDE names {rid}, which neither {RULES} nor its held list holds")
    eia = {}
    for rid, nums in RULE_EIA.items():
        for n in nums:
            eia.setdefault(n, {"rules": []})["rules"].append(rid)
    for n, slug in NO_RULE.items():
        if n in eia:
            raise ValueError(f"EIA {n} has a rule and a no-rule note")
        eia[n] = {"rules": [], "none": note_line(slug), "note": f"docs/research/large_load/notes/{slug}.md"}

    count = lambda xs, key, order: {s: sum(1 for x in xs if x[key] == s) for s in order if any(x[key] == s for x in xs)}
    return {
        "tables": [RULES, CHANGES, LAWS],
        "built": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "retrieved": {RULES: retrieved_of(rh), CHANGES: retrieved_of(ch), LAWS: retrieved_of(lh)},
        "method": "docs/methods/large_load_research.md",
        "fields": FIELDS,
        "rules": rules, "held_rules": held_rules,
        "changes": changes, "held_changes": held_changes,
        "laws": laws, "held_laws": held_laws,
        "law_searches": law_searches({x["state"] for x in laws} | {x["state"] for x in held_laws}),
        "eia": eia, "statewide": STATEWIDE,
        "counts": {"rules": count(rules, "status", RULE_STATUSES), "laws": count(laws, "status", LAW_STATUSES),
                   "changes": len(changes), "held": {"rules": len(held_rules), "changes": len(held_changes), "laws": len(held_laws)}},
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--in-dir", default=OUTPUT)
    ap.add_argument("--out", default=SITE_FILE)
    ap.add_argument("--check", action="store_true", help="build in memory; exit 1 when the file differs (the built time aside)")
    a = ap.parse_args(argv)
    try:
        d = build(a.in_dir)
    except Exception as e:  # fail loudly, write nothing
        print(f"large_load_rules_page: {type(e).__name__}: {e}", file=sys.stderr)
        return 1
    if a.check:
        if not os.path.exists(a.out):
            print(f"{a.out} does not exist", file=sys.stderr)
            return 1
        with open(a.out, encoding="utf-8") as fh:
            old = json.load(fh)
        same = {k: v for k, v in old.items() if k != "built"} == {k: v for k, v in d.items() if k != "built"}
        print("same" if same else "differs")
        return 0 if same else 1
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(d, fh, ensure_ascii=False, indent=0, separators=(",", ":"))
        fh.write("\n")
    c = d["counts"]
    print(f"wrote {a.out}: {len(d['rules'])} rules ({c['rules']}), {len(d['held_rules'])} held; {len(d['changes'])} changes, "
          f"{len(d['held_changes'])} held; {len(d['laws'])} laws ({c['laws']}), {len(d['held_laws'])} held")
    return 0


if __name__ == "__main__":
    sys.exit(main())
