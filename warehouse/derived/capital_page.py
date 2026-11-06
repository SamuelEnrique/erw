#!/usr/bin/env python3
"""The file /capital reads (platform tool 11, capital flows: its first view; session 3306, chain 200).

Energy Research Warehouse (ERW). Reads energy_deals (the deal tracker's project finance, M&A, debt and equity raise rows)
and the company database (company_links, company_directory: the kind of each deal's counterparties); writes
site/data/capital.json. No request, no model call, no data lock. Method: docs/methods/companies.md, "Capital".

    python warehouse/derived/capital_page.py                 # from this repository's warehouse/output
    python warehouse/derived/capital_page.py --in-dir DIR    # read the tables from DIR
    python warehouse/derived/capital_page.py --out FILE      # write elsewhere

While energy_deals is held for a license (warehouse/metadata/license_status.csv, from its day, with no permission
recorded), the file holds the hold and the table's row count only: no deal, no figure, no count by kind (the deals
page's rule, site/app/deals/Held.tsx). Otherwise it holds, for the capital rows (deal_type project_finance, m_and_a,
debt, equity_raise): by quarter and type the rows, the USD disclosed summed, the rows with no USD and the MW stated; the
same by segment (the deal's technology) and by the kind of the counterparty that brings the money (the buyer: the
acquirer of an M&A, the lender or investor of a financing; its kind from company_directory, "not named" when the row
names no buyer); the disclosed share; and the twenty largest by USD with their sources. Nothing is filled in: a row
with no USD adds to the count of rows without one, never a figure.
"""

import argparse
import datetime as dt
import json
import os
import sys
from collections import defaultdict

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
import companies as C  # noqa: E402

OUT = os.path.join(ROOT, "site", "data", "capital.json")
TYPES = ["project_finance", "m_and_a", "debt", "equity_raise"]
TYPE_WORDS = {"project_finance": "Project finance", "m_and_a": "M&A", "debt": "Debt", "equity_raise": "Equity raise"}


def quarter(date):
    if not date or len(date) < 7:
        return ""
    return f"{date[:4]}Q{(int(date[5:7]) - 1) // 3 + 1}"


def cell():
    return dict(rows=0, usd=0.0, usd_rows=0, no_usd=0, mw=0.0)


def add(c, usd, mw):
    c["rows"] += 1
    if usd is not None:
        c["usd"] += usd
        c["usd_rows"] += 1
    else:
        c["no_usd"] += 1
    c["mw"] += mw or 0.0


def compute(deals, links, directory):
    """The figures of the capital rows (pure, on DataFrames of the three tables)."""
    kind = dict(zip(directory["entity_id"], directory["kind"]))
    buyers = defaultdict(set)
    for r in links[(links["input_table"] == "energy_deals") & (links["role"] == "buyer")].itertuples(index=False):
        buyers[r.input_row].add(kind.get(r.company_id, "other"))
    cap = deals[deals["deal_type"].isin(TYPES)].copy()
    by_q = defaultdict(lambda: defaultdict(cell))
    by_seg = defaultdict(cell)
    by_kind = defaultdict(cell)
    total = cell()
    rows = []
    for r in cap.to_dict("records"):
        usd, mw = C.num(r.get("dollars")), C.num(r.get("mw"))
        q = quarter(r.get("event_date", ""))
        add(by_q[q][r["deal_type"]], usd, mw)
        add(by_seg[C.fuel_of_text(r.get("technology")) or "not stated"], usd, mw)
        ks = sorted(buyers.get(r["event_id"], set())) or ["not named"]
        for k in ks:                       # a deal with two kinds of buyer counts once in each
            add(by_kind[k], usd, mw)
        add(total, usd, mw)
        rows.append(dict(event_id=r["event_id"], date=r.get("event_date", "")[:10], quarter=q, type=r["deal_type"],
                         buyer=r.get("buyer", ""), seller=r.get("seller", ""), asset=r.get("asset", ""),
                         technology=r.get("technology", ""), usd=usd, mw=mw, sources=[u for u in str(r.get("story_urls", "")).split(";") if u],
                         buyer_kinds=ks))
    r1 = lambda c: {**c, "usd": round(c["usd"]), "mw": round(c["mw"], 1)}
    largest = sorted([x for x in rows if x["usd"] is not None], key=lambda x: (-x["usd"], x["event_id"]))[:20]
    return dict(
        types=TYPES, type_words=TYPE_WORDS,
        quarters=[dict(quarter=q, **{t: r1(v[t]) for t in TYPES if t in v}) for q, v in sorted(by_q.items()) if q],
        segments=[dict(segment=k, **r1(v)) for k, v in sorted(by_seg.items(), key=lambda kv: -kv[1]["usd"])],
        kinds=[dict(kind=k, **r1(v)) for k, v in sorted(by_kind.items(), key=lambda kv: -kv[1]["usd"])],
        total=r1(total), disclosed_share=round(total["usd_rows"] / total["rows"], 4) if total["rows"] else None,
        largest=[{**x, "usd": round(x["usd"]), "mw": x["mw"]} for x in largest])


def build(in_dir, out, lic=None, now=None):
    deals = C.read_table(os.path.join(in_dir, "energy_deals.csv"))
    lic = lic or C.licenses(["energy_deals"])
    built = (now or dt.datetime.now(dt.timezone.utc)).strftime("%Y-%m-%dT%H:%M:%SZ")
    head = dict(built=built, table="energy_deals", n_rows=len(deals), method="docs/methods/companies.md")
    if lic.get("energy_deals") != "public":
        doc = dict(head, held=True)
    else:
        links = C.read_table(os.path.join(in_dir, "company_links.csv"))
        directory = C.read_table(os.path.join(in_dir, "company_directory.csv"))
        doc = dict(head, held=False, **compute(deals, links, directory))
    text = json.dumps(doc, ensure_ascii=False, indent=1)
    text = text.replace(chr(0x2014), "-").replace(chr(0x2013), "-")      # CLAUDE.md rule 2
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text + "\n")
    return doc


def main(argv=None):
    ap = argparse.ArgumentParser(description="The file /capital reads")
    ap.add_argument("--in-dir", default=os.path.join(ROOT, "warehouse", "output"))
    ap.add_argument("--out", default=OUT)
    args = ap.parse_args(argv)
    doc = build(args.in_dir, args.out)
    if doc["held"]:
        print(f"capital: energy_deals is held for a license; {args.out} holds the hold and its {doc['n_rows']} rows' count only")
    else:
        print(f"capital: {doc['total']['rows']} capital rows, {doc['total']['usd_rows']} with USD; {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
