#!/usr/bin/env python3
"""Who is buying: the buyer names of ferc_eqr_contracts brought to one spelling by rule, and the largest buyers and
sellers of energy, capacity and tolling (session 99).

Energy Research Warehouse (ERW). Three derived tables, all INTERNAL as their input is (ferc_eqr_contracts, session 83's
ruling), none of them in git:
    ferc_eqr_buyer_names      entities: one row per buyer name as filed, with the name it is counted under, the rules
                              that changed it, and how many names share that one. Every merge is here, for a person to check.
    ferc_eqr_buyer_doubtful   events: pairs of names that look like one buyer and were NOT merged, each with the reason
                              for the doubt. Nothing is merged on a guess.
    ferc_eqr_party_totals     entities: for energy, capacity and tolling, each buyer (by its merged name) and each seller
                              (by FERC's company identifier): contracts in force, rows, counterparties and the MW filed.
Method: docs/methods/eqr_buyers.md. Page: /contracts?view=largest (in review, internal view).

    python warehouse/derived/eqr_buyers.py                 # the three tables, under the data lock
    python warehouse/derived/eqr_buyers.py --out-dir DIR   # a trial run: the tables under DIR, nothing in warehouse/output

No request is made, and no model: every merge is a rule a person can read.

THE RULES, in order. Two names are one buyer only when all of them leave the two names identical.
    case_space            capitals; runs of spaces closed up
    punctuation           "&" read as AND; periods, commas, apostrophes, quotation marks and brackets taken out; a hyphen
                          or a slash read as a space
    leading_the           a leading THE taken off
    abbreviation          a whole word from a short list written out or shortened one way: CORPORATION as CORP,
                          INCORPORATED as INC, COMPANY as CO, LIMITED as LTD, COOP as COOPERATIVE, ASSN and ASSOC as
                          ASSOCIATION, ELEC as ELECTRIC, DEPT as DEPARTMENT, AUTH as AUTHORITY, MGMT as MANAGEMENT,
                          SVC and SVCS as SERVICE and SERVICES, INTL as INTERNATIONAL, NATL as NATIONAL, PWR as POWER,
                          MKTG as MARKETING, TRANSM as TRANSMISSION. CO is left alone as the last word of a name that
                          begins CITY, TOWN, VILLAGE, COUNTY or BOROUGH or holds OF: there it may be Colorado.
    legal_suffix          the legal form at the end of a name written one way: L L C as LLC, L P as LP, L L P as LLP,
                          LIMITED LIABILITY COMPANY as LLC, LIMITED PARTNERSHIP as LP, N A as NA
    suffix_left_off       a name with no legal form at its end, when the same name is also filed with exactly one legal
                          form, is counted with it ("Versant Power" with "Versant Power, Inc."). When the same name is
                          filed with two different legal forms nothing is merged and the pair is doubtful.

DOUBTFUL, never merged:
    different_legal_form  the same name with two different legal forms (LLC and INC): they may be two companies
    extra_clause          a name that is another name plus a d/b/a, f/k/a, "as agent for" or bracketed clause
    near_spelling         two names at least 94 percent alike letter by letter, of 12 letters or more, that do not differ
                          by a number (a project's I and II, 1 and 2 are two companies, not a doubt)
"""

import argparse
import difflib
import os
import re
import sys
from collections import defaultdict

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import iso_prices as ip  # noqa: E402

INPUT = "ferc_eqr_contracts"
NAMES, DOUBTFUL, TOTALS = "ferc_eqr_buyer_names", "ferc_eqr_buyer_doubtful", "ferc_eqr_party_totals"
SOURCE = "erw:eqr_buyers"
METHOD_URL = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/eqr_buyers.md"
ENTITY_COLS = ["entity_id", "entity_type", "name", "geo", "lat", "lon", "capacity_mw", "status", "status_date", "operator", "source", "source_url", "retrieved_at", "vintage"]
EVENT_COLS = ["event_id", "event_date", "event_type", "parties", "entity_ids", "mw", "price", "currency", "status", "source", "source_url"]
PRODUCTS = {"ENERGY": "energy", "CAPACITY": "capacity", "TOLLING ENERGY": "tolling"}
ABBREVIATIONS = {"CORPORATION": "CORP", "INCORPORATED": "INC", "COMPANY": "CO", "LIMITED": "LTD", "COOP": "COOPERATIVE", "ASSN": "ASSOCIATION", "ASSOC": "ASSOCIATION",
                 "ELEC": "ELECTRIC", "DEPT": "DEPARTMENT", "AUTH": "AUTHORITY", "MGMT": "MANAGEMENT", "SVC": "SERVICE", "SVCS": "SERVICES", "INTL": "INTERNATIONAL",
                 "NATL": "NATIONAL", "PWR": "POWER", "MKTG": "MARKETING", "TRANSM": "TRANSMISSION"}
MUNICIPAL = {"CITY", "TOWN", "VILLAGE", "COUNTY", "BOROUGH"}
LEGAL = ("LLC", "LLP", "LP", "INC", "CORP", "CO", "LTD", "PLC", "NA")
SUFFIX_FORMS = [(("LIMITED", "LIABILITY", "COMPANY"), "LLC"), (("LTD", "LIABILITY", "CO"), "LLC"), (("LIMITED", "PARTNERSHIP"), "LP"), (("LTD", "PARTNERSHIP"), "LP"),
                (("L", "L", "C"), "LLC"), (("L", "L", "P"), "LLP"), (("L", "P"), "LP"), (("P", "L", "C"), "PLC"), (("N", "A"), "NA")]
CLAUSE = re.compile(r"\s+(D/B/A|DBA|F/K/A|FKA|AS AGENT FOR|AS AGNT FOR|A/K/A)\s+.*$|\s*\([^)]*\)\s*$", re.I)
NUMERAL = re.compile(r"^(\d+|[IVX]+|[A-H])$")
NEAR = 0.94
NEAR_MIN = 12


def normalized(name):
    """A name's key and the rules that changed it, in order."""
    rules = []
    s = " ".join(str(name).upper().split())
    if s != str(name):
        rules.append("case_space")
    p = s.replace("&", " AND ")
    p = re.sub(r"[.,'\"`()\[\]]", "", p)
    p = " ".join(re.sub(r"[-/]", " ", p).split())
    if p != s:
        rules.append("punctuation")
    t = p.split()
    if len(t) > 1 and t[0] == "THE":
        t = t[1:]
        rules.append("leading_the")
    out, changed = [], False
    for i, w in enumerate(t):
        if w == "CO" and i == len(t) - 1 and (t[0] in MUNICIPAL or "OF" in t):
            out.append(w)  # it may be Colorado
            continue
        v = ABBREVIATIONS.get(w, w)
        changed = changed or v != w
        out.append(v)
    if changed:
        rules.append("abbreviation")
    for form, short in SUFFIX_FORMS:
        if len(out) > len(form) and tuple(out[-len(form):]) == form:
            out = out[:-len(form)] + [short]
            rules.append("legal_suffix")
            break
    return " ".join(out), rules


def stem_and_form(key):
    """A key without its legal form, and the form ('' when it has none). CO counts as a form only after another word."""
    t = key.split()
    if len(t) > 1 and t[-1] in LEGAL and not (t[-1] == "CO" and (t[0] in MUNICIPAL or "OF" in t)):
        return " ".join(t[:-1]), t[-1]
    return key, ""


def groups_of(counts):
    """{raw name: rows} to: {raw: (group key, rules)}, and the doubtful pairs of group keys [(a, b, reason, similarity)]."""
    keyed = {raw: normalized(raw) for raw in counts}
    keys = defaultdict(int)
    for raw, (k, _) in keyed.items():
        keys[k] += counts[raw]
    by_stem = defaultdict(set)
    for k in keys:
        stem, form = stem_and_form(k)
        by_stem[stem].add(form)
    final, doubtful = {}, []
    for stem, forms in by_stem.items():
        real = sorted(f for f in forms if f)
        if "" in forms and len(real) == 1:
            final[stem] = f"{stem} {real[0]}"  # suffix_left_off
        if len(real) > 1:
            names = [f"{stem} {f}" for f in real] + ([stem] if "" in forms else [])
            for i in range(len(names)):
                for j in range(i + 1, len(names)):
                    doubtful.append((names[i], names[j], "different_legal_form", 1.0))
    out = {}
    for raw, (k, rules) in keyed.items():
        if k in final:
            out[raw] = (final[k], rules + ["suffix_left_off"])
        else:
            out[raw] = (k, rules)
    group_keys = sorted({g for g, _ in out.values()})
    seen = {tuple(sorted((a, b))) for a, b, _, _ in doubtful}
    # extra_clause: a raw name that is another group's name plus a d/b/a or a bracketed clause
    key_set = set(group_keys)
    for raw, (g, _) in out.items():
        base = CLAUSE.sub("", str(raw))
        if base != str(raw) and base.strip():
            bk, _ = normalized(base)
            bk = final.get(bk, bk)
            if bk in key_set and bk != g and tuple(sorted((g, bk))) not in seen:
                doubtful.append((g, bk, "extra_clause", 1.0))
                seen.add(tuple(sorted((g, bk))))
    # near_spelling: within names that begin with the same four letters
    blocks = defaultdict(list)
    for g in group_keys:
        if len(g) >= NEAR_MIN:
            blocks[g[:4]].append(g)
    for block in blocks.values():
        for i in range(len(block)):
            a = block[i]
            for j in range(i + 1, len(block)):
                b = block[j]
                if abs(len(a) - len(b)) > 3 or tuple(sorted((a, b))) in seen:
                    continue
                m = difflib.SequenceMatcher(None, a, b, autojunk=False)
                if m.real_quick_ratio() < NEAR or m.quick_ratio() < NEAR:
                    continue
                r = m.ratio()
                if r < NEAR:
                    continue
                ta, tb = a.split(), b.split()
                diff = set(ta) ^ set(tb)
                if diff and all(NUMERAL.match(w) for w in diff):
                    continue  # a project's I and II are two companies, not a doubt
                if stem_and_form(a)[0] == stem_and_form(b)[0]:
                    continue  # already listed as a different legal form
                doubtful.append((a, b, "near_spelling", round(r, 4)))
                seen.add(tuple(sorted((a, b))))
    return out, doubtful


def read_input(in_dir):
    path = os.path.join(in_dir, f"{INPUT}.csv")
    n = 0
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.startswith("#"):
                break
            n += 1
    return pd.read_csv(path, skiprows=n, low_memory=False, dtype=str, keep_default_na=False), path


def display_names(mapping, counts):
    """The spelling a group is shown under: the one filed on the most rows (ties: the first in order)."""
    best = {}
    for raw, (g, _) in mapping.items():
        c = (counts[raw], raw)
        if g not in best or (c[0], ) > (best[g][0], ) or (c[0] == best[g][0] and raw < best[g][1]):
            best[g] = c
    return {g: raw for g, (_, raw) in best.items()}


def party_totals(d, mapping, shown):
    """Energy, capacity and tolling rows in force, by buyer (merged name) and by seller (FERC's company identifier)."""
    x = d[(d["status"] == "in_force") & d["x_product_name"].str.upper().isin(PRODUCTS)].copy()
    x["product"] = x["x_product_name"].str.upper().map(PRODUCTS)
    x["buyer"] = x["x_customer_company_name"].map(lambda r: shown[mapping[r][0]])
    x["contract"] = x["x_company_id"] + "|" + x["x_contract_unique_id"]
    x["mw_n"] = pd.to_numeric(x["mw"], errors="coerce")
    seller_name = x.groupby("x_company_id")["x_seller_company_name"].agg(lambda s: s.value_counts().index[0])
    x["seller"] = x["x_company_id"].map(seller_name)
    rows = []
    for role, key, other in (("buyer", "buyer", "x_company_id"), ("seller", "x_company_id", "buyer")):
        g = x.groupby(["product", key]).agg(contracts=("contract", "nunique"), rows=("contract", "size"), counterparties=(other, "nunique"),
                                            mw_filed=("mw_n", "sum"), rows_with_mw=("mw_n", "count")).reset_index()
        g["name"] = g[key] if role == "buyer" else g[key].map(seller_name)
        for product, p in g.groupby("product"):
            p = p.sort_values(["contracts", "rows", "name"], ascending=[False, False, True]).reset_index(drop=True)
            for i, r in enumerate(p.itertuples(), 1):
                rows.append(dict(role=role, product=product, rank=i, name=r.name, contracts=int(r.contracts), rows=int(r.rows), counterparties=int(r.counterparties),
                                 mw_filed=round(float(r.mw_filed), 1), rows_with_mw=int(r.rows_with_mw), company_id=getattr(r, key) if role == "seller" else ""))
    return rows, x


def main(argv=None):
    ap = argparse.ArgumentParser(description="Who is buying: buyer names by rule, and the largest buyers and sellers")
    ap.add_argument("--out-dir", help="a trial run: the tables and their log under this directory; nothing in warehouse/output")
    a = ap.parse_args(argv)
    inputs = ip.OUT_DIR
    if a.out_dir:
        os.makedirs(a.out_dir, exist_ok=True)
    run_id = pd.Timestamp.now(tz="UTC").strftime("%Y%m%dT%H%M%SZ")
    retrieved = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
    log_dir = os.path.join(a.out_dir, "logs") if a.out_dir else ip.LOG_DIR
    os.makedirs(log_dir, exist_ok=True)
    log = ip.Log(os.path.join(log_dir, f"eqr_buyers_{run_id}.log"))
    d, path = read_input(inputs)
    quarter = d["x_quarter"].iloc[0]
    y, q = int(quarter[:4]), int(quarter[-1])
    quarter_end = (pd.Timestamp(year=y, month=3 * q, day=1) + pd.offsets.MonthEnd(0)).strftime("%Y-%m-%d")
    counts = d["x_customer_company_name"].value_counts().to_dict()
    mapping, doubtful = groups_of(counts)
    shown = display_names(mapping, counts)
    size = defaultdict(int)
    grows = defaultdict(int)
    for raw, (g, _) in mapping.items():
        size[g] += 1
        grows[g] += counts[raw]
    by_rule = defaultdict(int)
    for raw, (g, rules) in mapping.items():
        for r in rules:
            by_rule[r] += 1
    merged = sum(1 for g in size if size[g] > 1)
    log(f"  {INPUT}: {len(d):,} rows, {len(counts):,} buyer names as filed, {len(size):,} after the rules; {merged:,} of those hold more than one name "
        f"({sum(size[g] for g in size if size[g] > 1):,} names); names a rule changed: {dict(by_rule)}; doubtful pairs, not merged: {len(doubtful):,} "
        f"({ {r: sum(1 for x in doubtful if x[2] == r) for r in ('different_legal_form', 'extra_clause', 'near_spelling')} })")
    common = dict(geo="US", lat="", lon="", capacity_mw="", status_date="", operator="", source=SOURCE, source_url=METHOD_URL, retrieved_at=retrieved, vintage="")
    names = pd.DataFrame([dict(entity_id=f"ferc_eqr_buyer_name:{i:05d}", entity_type="company", name=raw, status="active", **common,
                               x_merged="yes" if size[g] > 1 else "no", x_counted_as=shown[g], x_key=g, x_rules=";".join(rules), x_names_in_group=size[g], x_rows=counts[raw], x_group_rows=grows[g], x_quarter=quarter)
                          for i, (raw, (g, rules)) in enumerate(sorted(mapping.items(), key=lambda kv: (kv[1][0], kv[0])), 1)])
    pairs = pd.DataFrame([dict(event_id=f"ferc_eqr_doubtful:{quarter}:{i:05d}", event_date=quarter_end, event_type="doubtful_name_pair", parties=f"{shown[x]};{shown[z]}", entity_ids="",
                               mw="", price="", currency="", status="not_merged", source=SOURCE, source_url=METHOD_URL, x_reason=reason, x_similarity=sim,
                               x_rows_a=grows[x], x_rows_b=grows[z], x_key_a=x, x_key_b=z, x_quarter=quarter, retrieved_at=retrieved)
                          for i, (x, z, reason, sim) in enumerate(sorted(doubtful, key=lambda t: (-(grows[t[0]] + grows[t[1]]), t[0], t[1])), 1)])
    totals, scope = party_totals(d, mapping, shown)
    tot = pd.DataFrame([dict(entity_id=f"ferc_eqr_party:{r['role']}:{r['product']}:{r['rank']:05d}", entity_type="company", name=r["name"], status="active", **common,
                             x_role=r["role"], x_product=r["product"], x_rank=r["rank"], x_contracts=r["contracts"], x_rows=r["rows"], x_counterparties=r["counterparties"],
                             x_mw_filed=r["mw_filed"], x_rows_with_mw=r["rows_with_mw"], x_company_id=r["company_id"], x_quarter=quarter) for r in totals])
    log(f"  energy, capacity and tolling in force: {len(scope):,} rows; {scope['buyer'].nunique():,} buyers after the rules, {scope['x_company_id'].nunique():,} sellers; "
        f"rows with a MW quantity: {int(scope['mw_n'].notna().sum()):,}")
    if a.out_dir:
        ip.set_out_dir(a.out_dir)
    for name in (NAMES, DOUBTFUL, TOTALS):
        target = os.path.join(ip.OUT_DIR, name + ".csv")
        if os.path.exists(target):
            ip._require_lock(target, f"rebuilding {name}")
            os.remove(target)  # rebuilt whole from the quarter's file each run
    tail = [f"Retrieved: {run_id} (UTC) by warehouse/derived/eqr_buyers.py", f"Run log: warehouse/output/logs/eqr_buyers_{run_id}.log",
            f"Derived from: {INPUT} ({quarter}); read by this run from {os.path.relpath(path, ROOT).replace(os.sep, '/')}",
            f"Source: {SOURCE} from ferc:eqr, Federal Energy Regulatory Commission, Electric Quarterly Reports, {quarter}",
            "License: internal. A derived table inherits the license of its input: ferc_eqr_contracts is internal (session 83's ruling). Not in git, not public."]
    ip.write_csv(names, NAMES, [
        "Energy Research Warehouse (ERW): the buyer names of FERC's Electric Quarterly Reports as filed, and the name each is counted under, by rule (session 99)",
        "Shape: entities (docs/datastandard.md v0). One row per buyer name as filed (name). x_counted_as: the spelling its group is shown under (the one filed on "
        "the most rows). x_key: the group's key after the rules. x_rules: the rules that changed this name, in order. x_names_in_group, x_rows (this name), "
        "x_group_rows. x_merged yes: the group holds more than one name. The rules: docs/methods/eqr_buyers.md.",
        f"Counts: {len(counts):,} names as filed, {len(size):,} after the rules, {merged:,} groups of more than one name. Every merge is a row here; nothing is merged on a guess.",
    ] + tail, log, cols=ENTITY_COLS + ["x_merged", "x_counted_as", "x_key", "x_rules", "x_names_in_group", "x_rows", "x_group_rows", "x_quarter"], key=["entity_id"], time_col="retrieved_at")
    ip.write_csv(pairs, DOUBTFUL, [
        "Energy Research Warehouse (ERW): pairs of buyer names in FERC's Electric Quarterly Reports that look like one buyer and were NOT merged (session 99)",
        "Shape: events (docs/datastandard.md v0). One row per pair: parties, the two names as shown; x_reason: different_legal_form, extra_clause or near_spelling; "
        "x_similarity (near_spelling: the share of letters alike); x_rows_a, x_rows_b the rows each is filed on. event_date: the last day of the quarter filed for. "
        "A person decides each; the rules never merge these. docs/methods/eqr_buyers.md.",
        f"Counts: {len(pairs):,} pairs.",
    ] + tail, log, cols=EVENT_COLS + ["x_reason", "x_similarity", "x_rows_a", "x_rows_b", "x_key_a", "x_key_b", "x_quarter", "retrieved_at"], key=["event_id"], time_col="event_date")
    ip.write_csv(tot, TOTALS, [
        "Energy Research Warehouse (ERW): the buyers and sellers of energy, capacity and tolling in FERC's Electric Quarterly Reports, contracts in force (session 99)",
        "Shape: entities (docs/datastandard.md v0). One row per party, role (x_role: buyer by its merged name, seller by FERC's company identifier) and product "
        "(x_product: energy, capacity, tolling). x_rank within its role and product, by contracts then rows. x_contracts: distinct contracts (filer and contract "
        "identifier); x_rows: product rows; x_counterparties; x_mw_filed: the sum of the quantities filed in MW, over x_rows_with_mw rows (most rows file none).",
        f"Counts: {len(scope):,} rows in force of the three products.",
    ] + tail, log, cols=ENTITY_COLS + ["x_role", "x_product", "x_rank", "x_contracts", "x_rows", "x_counterparties", "x_mw_filed", "x_rows_with_mw", "x_company_id", "x_quarter"],
        key=["entity_id"], time_col="retrieved_at")
    ip.update_sources([dict(source=SOURCE, publisher="Energy Research Warehouse (ERW), derived",
                            report="FERC EQR buyer names by rule, the doubtful pairs, and the largest buyers and sellers (docs/methods/eqr_buyers.md)", report_url=METHOD_URL,
                            document_list="docs/methods/eqr_buyers.md", license="internal", tables=[NAMES, DOUBTFUL, TOTALS])])
    log.close()
    print(f"{NAMES}: {len(names):,} names, {len(size):,} after the rules, {merged:,} merged groups; {DOUBTFUL}: {len(pairs):,} pairs; {TOTALS}: {len(tot):,} rows"
          + (f" (trial, under {a.out_dir})" if a.out_dir else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
