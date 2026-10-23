#!/usr/bin/env python3
"""The FERC EQR contract rows beside the deals (session 825): a read-only join by the parties' names and the quarter.

Energy Research Warehouse (ERW). For each deal the tracker shows (warehouse/deals/public_rows.py, the shown sort), the
rows of ferc_eqr_contracts whose seller and buyer are the deal's parties, filed in the deal's quarter (and, for the
record, in any quarter held). ferc_eqr_contracts is internal by the ERW's own record (docs/licenses.md: FERC's page
not read for the EQR), so what the site may carry is a count a deal and the words "license needed" where the filed
terms would be; the terms themselves stay in runs/ (never committed).

The names. A party of a deal is the model's words from a story ("Constellation", "Amazon"); an EQR name is the filer's
("Constellation Energy Generation, LLC"). Both go through key(): upper case, punctuation dropped, the corporate words
(LLC, INC, CORP, CORPORATION, CO, COMPANY, LP, LTD, PLC, HOLDINGS, ENERGY where it is not the whole name) dropped, spaces
folded; the buyer's filed name is first read through ferc_eqr_buyer_names (name to x_key, the group's key after
session 99's rules) where it is listed. A party matches a filed name when the keys are equal, or one key is a whole
word (or words) of the other and at least four characters long. A row matches a deal when one party matches the
seller and another the buyer (either way round); a deal with one named party matches on that party as seller or
buyer, said so. Nothing is matched on a guess: a party of fewer than four letters ("US") matches only as a whole key.

    python warehouse/deals/eqr_join.py                              # the counts, one line a shown deal
    python warehouse/deals/eqr_join.py --json site/data/deals_eqr.json   # the counts for the site (no filed term in it)
    python warehouse/deals/eqr_join.py --terms runs/s825/eqr_terms.json  # the matched rows' terms, for the review (runs/ only)
    python warehouse/deals/eqr_join.py --contracts runs/archive_restore/ferc_eqr_contracts.csv --names runs/archive_restore/ferc_eqr_buyer_names.csv
"""

import argparse
import csv
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import public_rows as P  # noqa: E402

RESTORE = os.path.join(ROOT, "runs", "archive_restore")
CORPORATE = {"LLC", "INC", "CORP", "CORPORATION", "CO", "COMPANY", "LP", "LTD", "PLC", "HOLDINGS", "THE", "L", "P", "LIMITED", "PARTNERSHIP", "ENERGY"}
MIN = 4


def key(name):
    """A name's key: upper case, punctuation to spaces, the corporate words dropped (unless nothing would be left)."""
    words = re.sub(r"[^A-Z0-9 ]+", " ", (name or "").upper()).split()
    kept = [w for w in words if w not in CORPORATE]
    return " ".join(kept or words)


def matches(party_key, filed_key):
    """True when the keys are equal, or one is whole words of the other and at least MIN characters long."""
    if not party_key or not filed_key:
        return False
    if party_key == filed_key:
        return True
    short, long_ = (party_key, filed_key) if len(party_key) <= len(filed_key) else (filed_key, party_key)
    if len(short) < MIN:
        return False
    return re.search(r"(?<![A-Z0-9])" + re.escape(short) + r"(?![A-Z0-9])", long_) is not None


def quarter_of(date):
    y, m = int(date[:4]), int(date[5:7])
    return f"{y}_Q{(m - 1) // 3 + 1}"


def rows(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader([ln for ln in f if not ln.startswith("#")]))


def load_contracts(path):
    """The EQR rows with the fields the join and the review use."""
    out = []
    for r in rows(path):
        x = {k[2:] if k.startswith("x_") else k: v for k, v in r.items()}
        out.append({"id": r["event_id"], "date": r["event_date"][:10], "seller": x.get("seller_company_name", ""), "buyer": x.get("customer_company_name", ""),
                    "product": x.get("product_name", ""), "class": x.get("class_name", ""), "term": x.get("term_name", ""),
                    "commencement": x.get("commencement_date_of_contract_term", ""), "termination": x.get("contract_termination_date", ""),
                    "quantity": x.get("quantity", ""), "units": x.get("units", ""), "rate": x.get("rate", ""), "rate_units": x.get("rate_units", ""),
                    "rate_description": x.get("rate_description", ""), "pod_ba": x.get("point_of_delivery_balancing_authority", ""),
                    "pod": x.get("point_of_delivery_specific_location", ""), "quarter": x.get("quarter", "") or quarter_of(r["event_date"]),
                    "mw": r.get("mw", "")})
    return out


def load_names(path):
    return {r["name"]: r["x_key"] for r in rows(path)} if path and os.path.exists(path) else {}


def parties_of(deal):
    ps = [deal.get("buyer", ""), deal.get("seller", "")] + [p for p in (deal.get("other_parties") or "").split(";")]
    return [p.strip() for p in ps if p and p.strip()]


def join(deals, contracts, names):
    """{deal_id: {"parties", "quarter", "in_quarter": [rows], "any_quarter": [rows], "how"}} for the deals given."""
    ckeys = [(c, key(c["seller"]), key(names.get(c["buyer"], c["buyer"]))) for c in contracts]
    out = {}
    for d in deals:
        parties = parties_of(d)
        pkeys = [(p, key(p)) for p in parties]
        q = quarter_of(d["event_date"])
        hits, how = [], "two parties" if len(pkeys) >= 2 else "one party"
        for c, sk, bk in ckeys:
            s_hit = [p for p, k in pkeys if matches(k, sk)]
            b_hit = [p for p, k in pkeys if matches(k, bk)]
            if len(pkeys) >= 2:
                ok = any(s != b for s in s_hit for b in b_hit)
            else:
                ok = bool(s_hit or b_hit)
            if ok:
                hits.append(dict(c, matched_seller="; ".join(s_hit), matched_buyer="; ".join(b_hit)))
        out[d["event_id"]] = {"parties": parties, "quarter": q, "how": how,
                              "in_quarter": [h for h in hits if h["quarter"] == q], "any_quarter": hits}
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--contracts", default=os.path.join(RESTORE, "ferc_eqr_contracts.csv"))
    ap.add_argument("--names", default=os.path.join(RESTORE, "ferc_eqr_buyer_names.csv"))
    ap.add_argument("--deals")
    ap.add_argument("--evidence")
    ap.add_argument("--json", help="the site's file: counts a shown deal, no filed term")
    ap.add_argument("--terms", help="the matched rows' terms, under runs/ only")
    ap.add_argument("--all", action="store_true", help="join every deal, not the shown ones only (for the rule's precision; with --terms under runs/)")
    a = ap.parse_args(argv)
    if a.terms and not os.path.abspath(a.terms).startswith(os.path.join(ROOT, "runs")):
        print("--terms writes under runs/ only (the EQR tables are internal)", file=sys.stderr)
        return 2
    deals, evidence, registry, verdicts = P.load(a.deals, a.evidence)
    s = P.sort_deals(deals, evidence, registry, verdicts)
    shown = [d for d in deals if a.all or s[d["event_id"]]["sort"] == P.SHOWN]
    contracts = load_contracts(a.contracts)
    quarters = sorted({c["quarter"] for c in contracts})
    j = join(shown, contracts, load_names(a.names))
    if a.json:
        out = {"written_by": "warehouse/deals/eqr_join.py --json (session 825)", "contracts_rows": len(contracts), "quarters_held": quarters,
               "rule": "a row matches a deal when one party matches the filed seller and another the filed buyer (either way round) by name key; in the deal's quarter",
               "deals": {k: {"quarter": v["quarter"], "how": v["how"], "in_quarter": len(v["in_quarter"]), "any_quarter": len(v["any_quarter"]),
                             "products": sorted({h["product"] for h in v["any_quarter"] if h["product"]}),
                             "quarters": sorted({h["quarter"] for h in v["any_quarter"]})} for k, v in j.items()}}
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=1, sort_keys=True)
            f.write("\n")
        print(f"wrote {a.json}: {len(out['deals'])} shown deals, {sum(v['in_quarter'] for v in out['deals'].values())} rows in quarter, {sum(v['any_quarter'] for v in out['deals'].values())} in any")
    if a.terms:
        os.makedirs(os.path.dirname(os.path.abspath(a.terms)), exist_ok=True)
        with open(a.terms, "w", encoding="utf-8") as f:
            json.dump(j, f, indent=1, sort_keys=True)
        print(f"wrote {a.terms}")
    if not a.json and not a.terms:
        print(f"{len(contracts)} contract rows, quarters {quarters}; {len(shown)} shown deals")
        for k, v in j.items():
            print(f"  {k} {v['quarter']} {v['how']}: {len(v['in_quarter'])} in quarter, {len(v['any_quarter'])} in any | {' / '.join(v['parties'])[:80]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
