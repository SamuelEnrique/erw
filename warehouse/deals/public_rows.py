#!/usr/bin/env python3
"""The deal rows sorted by who stands behind them: shown, held or unsettled (session 821).

Energy Research Warehouse (ERW). `energy_deals` is "license needed" as a whole (session 465) because every deal was
extracted from news stories whose publishers ask for permission. Chain 080 (23 October 2026) sorts the deals by the
publishers of their evidence rows (`energy_deals_evidence`, one row a deal and story, the `source` column) so that the
tracker can show the rows a public source stands behind and count the rest in place:

    shown       at least one evidence row comes from a publisher whose verdict in warehouse/metadata/license_verdicts.csv
                is "may be public" (a government page such as the DOE newsroom, a regulator's or an ISO's filing, a
                company's own announcement, or an outlet whose terms allow it, such as World Nuclear News);
    unsettled   no such row, and at least one evidence row comes from a publisher with no verdict (its page not read);
    held        every evidence row comes from a publisher whose verdict asks for permission (or a paid license).

A source's name goes through warehouse/metadata/sources.csv (source to publisher) and then canon() of scripts/licenses.py,
the function docs/licenses.md is written from, so "Bloomberg.com" is Bloomberg and "jpt.spe.org" is JPT. A deal with no
evidence row is held (nothing stands behind it that the rule can read). This is a reader: it writes nothing under
warehouse/output and makes no request. The deals' and the evidence's files are read from warehouse/output (the archive's
restore, `scripts/sync.py --check` current) or from the paths given.

    python warehouse/deals/public_rows.py                       # the counts and the lists, as text
    python warehouse/deals/public_rows.py --json site/data/deals_public_rows.json   # the sort, one entry a deal, for the site
    python warehouse/deals/public_rows.py --markdown            # the tables of docs/reviews/deals-public-rows-2026-10-23.md
"""

import argparse
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import licenses  # noqa: E402  (scripts/licenses.py: canon())

OUT = os.path.join(ROOT, "warehouse", "output")
META = os.path.join(ROOT, "warehouse", "metadata")
PUBLIC = "may be public"
SHOWN, HELD, UNSETTLED = "shown", "held", "unsettled"


def rows(path):
    """The rows of an ERW CSV, its # header skipped."""
    with open(path, encoding="utf-8", newline="") as f:
        lines = [ln for ln in f if not ln.startswith("#")]
    return list(csv.DictReader(lines))


def publisher_of(source, registry):
    """A source column's value to the publisher docs/licenses.md names."""
    return licenses.canon(registry.get(source, source))


def verdict_of(publisher, verdicts):
    """"may be public", "needs written permission", "needs a paid license", or None when the publisher was not read."""
    return verdicts.get(publisher)


def sort_deals(deals, evidence, registry, verdicts):
    """{deal_id: {"sort", "public": [publishers], "held": [publishers], "unsettled": [publishers], "evidence": [...]}}.

    The rule in the module's docstring. Publishers are listed once each, in the order met."""
    by_deal = {}
    for e in evidence:
        by_deal.setdefault(e["deal_id"], []).append(e)
    out = {}
    for d in deals:
        pubs, public, held, unsettled, ev = [], [], [], [], []
        for e in by_deal.get(d["event_id"], []):
            p = publisher_of(e["source"], registry)
            v = verdict_of(p, verdicts)
            kind = SHOWN if v == PUBLIC else (UNSETTLED if v is None else HELD)
            ev.append({"story_id": e["story_id"], "source": e["source"], "publisher": p, "verdict": v or "none", "kind": kind,
                       "url": e["source_url"], "date": e["event_date"]})
            if p not in pubs:
                pubs.append(p)
                {SHOWN: public, HELD: held, UNSETTLED: unsettled}[kind].append(p)
        sort = SHOWN if public else (UNSETTLED if unsettled else HELD)
        out[d["event_id"]] = {"sort": sort, "public": public, "held": held, "unsettled": unsettled, "evidence": ev}
    return out


def load(deals_path=None, evidence_path=None):
    deals = rows(deals_path or os.path.join(OUT, "energy_deals.csv"))
    evidence = rows(evidence_path or os.path.join(OUT, "energy_deals_evidence.csv"))
    registry = {r["source"]: r["publisher"] for r in rows(os.path.join(META, "sources.csv"))}
    verdicts = {r["key"]: r["verdict"] for r in rows(os.path.join(META, "license_verdicts.csv"))}
    return deals, evidence, registry, verdicts


def counts(sorted_deals):
    c = {SHOWN: 0, HELD: 0, UNSETTLED: 0}
    for v in sorted_deals.values():
        c[v["sort"]] += 1
    return c


def held_publishers(sorted_deals, top=10):
    """[(publisher, deals held that rest on it, evidence rows)] for the held deals, most deals first."""
    deals, ev = {}, {}
    for v in sorted_deals.values():
        if v["sort"] != HELD:
            continue
        seen = set()
        for e in v["evidence"]:
            ev[e["publisher"]] = ev.get(e["publisher"], 0) + 1
            if e["publisher"] not in seen:
                seen.add(e["publisher"])
                deals[e["publisher"]] = deals.get(e["publisher"], 0) + 1
    ranked = sorted(deals.items(), key=lambda kv: (-kv[1], kv[0]))
    return [(p, n, ev[p]) for p, n in ranked[:top]]


def unsettled_publishers(sorted_deals):
    out = {}
    for v in sorted_deals.values():
        if v["sort"] == UNSETTLED:
            for p in v["unsettled"]:
                out[p] = out.get(p, 0) + 1
    return sorted(out.items(), key=lambda kv: (-kv[1], kv[0]))


def shown_table(deals, sorted_deals):
    """One line a shown deal, for the review: the deal, its date, parties, MW and the public evidence."""
    by_id = {d["event_id"]: d for d in deals}
    lines = []
    for did, v in sorted_deals.items():
        if v["sort"] != SHOWN:
            continue
        d = by_id[did]
        pub = "; ".join(f"{e['publisher']} ({e['date'][:10]})" for e in v["evidence"] if e["kind"] == SHOWN)
        other = ", ".join(v["held"] + v["unsettled"]) or "none"
        parties = " / ".join(x for x in (d["buyer"], d["seller"]) if x) or d["parties"]
        lines.append((d["event_date"][:10], did, d["deal_type"], parties, d["asset"], d["mw"] or "", d["dollars"] or "", pub, other))
    return sorted(lines, reverse=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--deals")
    ap.add_argument("--evidence")
    ap.add_argument("--json", help="write the sort, one entry a deal, to this path")
    ap.add_argument("--markdown", action="store_true", help="print the review's tables")
    a = ap.parse_args(argv)
    deals, evidence, registry, verdicts = load(a.deals, a.evidence)
    s = sort_deals(deals, evidence, registry, verdicts)
    c = counts(s)
    if a.json:
        out = {"retrieved": next((ln.split("Retrieved:")[1].split("(")[0].strip() for ln in open(a.deals or os.path.join(OUT, "energy_deals.csv"), encoding="utf-8") if ln.startswith("# Retrieved:")), ""),
               "rule": "shown: an evidence row from a publisher whose verdict is 'may be public'; unsettled: none, and one from a publisher not read; held: every row asks for permission",
               "counts": c,
               "deals": {k: {"sort": v["sort"], "public": v["public"], "held": v["held"], "unsettled": v["unsettled"],
                             "public_evidence": [{"publisher": e["publisher"], "url": e["url"], "date": e["date"]} for e in v["evidence"] if e["kind"] == SHOWN]}
                         for k, v in s.items()}}
        os.makedirs(os.path.dirname(os.path.abspath(a.json)), exist_ok=True)
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=1, sort_keys=True)
            f.write("\n")
        print(f"wrote {a.json}: {len(out['deals'])} deals, {c}")
        return 0
    print(f"{len(deals)} deals, {len(evidence)} evidence rows: shown {c[SHOWN]}, held {c[HELD]}, unsettled {c[UNSETTLED]}")
    if a.markdown:
        print("\n| Date | Deal | Type | Parties | Asset | MW | USD | Public evidence (publisher, story date) | Other publishers behind it |")
        print("|---|---|---|---|---|---|---|---|---|")
        for ln in shown_table(deals, s):
            print("| " + " | ".join(str(x).replace("|", "/") for x in ln) + " |")
        print("\n| Publisher | Verdict | Held deals resting on it | Evidence rows |")
        print("|---|---|---|---|")
        for p, n, e in held_publishers(s):
            print(f"| {p} | {verdicts.get(p, 'none')} | {n} | {e} |")
        print("\n| Publisher not read | Unsettled deals resting on it |")
        print("|---|---|")
        for p, n in unsettled_publishers(s):
            print(f"| {p} | {n} |")
    else:
        for ln in shown_table(deals, s):
            print("  ", *ln[:5], ln[7])
        print("held, top publishers:", held_publishers(s))
        print("unsettled publishers:", unsettled_publishers(s))
    return 0


if __name__ == "__main__":
    sys.exit(main())
