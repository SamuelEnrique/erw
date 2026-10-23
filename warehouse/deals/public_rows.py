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


def sort_deals(deals, evidence, registry, verdicts, id_col="event_id", ev_col="deal_id"):
    """{deal_id: {"sort", "public": [publishers], "held": [publishers], "unsettled": [publishers], "evidence": [...]}}.

    The rule in the module's docstring. Publishers are listed once each, in the order met. Session 827: the same sort
    serves datacenter_projects (an entities table: id_col entity_id) and its evidence rows (ev_col facility_id)."""
    by_deal = {}
    for e in evidence:
        by_deal.setdefault(e[ev_col], []).append(e)
    out = {}
    for d in deals:
        pubs, public, held, unsettled, ev = [], [], [], [], []
        for e in by_deal.get(d[id_col], []):
            p = publisher_of(e["source"], registry)
            v = verdict_of(p, verdicts)
            kind = SHOWN if v == PUBLIC else (UNSETTLED if v is None else HELD)
            ev.append({"story_id": e["story_id"], "source": e["source"], "publisher": p, "verdict": v or "none", "kind": kind,
                       "url": e["source_url"], "date": e["event_date"]})
            if p not in pubs:
                pubs.append(p)
                {SHOWN: public, HELD: held, UNSETTLED: unsettled}[kind].append(p)
        sort = SHOWN if public else (UNSETTLED if unsettled else HELD)
        out[d[id_col]] = {"sort": sort, "public": public, "held": held, "unsettled": unsettled, "evidence": ev}
    return out


def datacenters_json(projects_path=None, evidence_path=None):
    """Session 827: the counts of datacenter_projects by the same sort (site/data/datacenters_public.json): the shown
    rows with their power-side fields only (name, state, MW, utility, power source; the queue's fields are the queue
    tables' own), the held and the unsettled counted. Today every evidence row rests on a publisher who asks for
    permission, so the file holds counts and no row."""
    projects = rows(projects_path or os.path.join(OUT, "datacenter_projects.csv"))
    evidence = rows(evidence_path or os.path.join(OUT, "datacenter_projects_evidence.csv"))
    registry = {r["source"]: r["publisher"] for r in rows(os.path.join(META, "sources.csv"))}
    verdicts = {r["key"]: r["verdict"] for r in rows(os.path.join(META, "license_verdicts.csv"))}
    s = sort_deals(projects, evidence, registry, verdicts, id_col="entity_id", ev_col="facility_id")
    shown = []
    for p in projects:
        v = s[p["entity_id"]]
        if v["sort"] != SHOWN:
            continue
        pub = [e for e in v["evidence"] if e["kind"] == SHOWN]
        shown.append({"entity_id": p["entity_id"], "name": p["name"], "state": p["state"], "county": p["county"], "city": p["city"], "mw": p["mw"] or None,
                      "utility": p["utility"], "power_source": p["power_source"], "project_status": p["project_status"], "planned_year": p["planned_year"],
                      "public_evidence": [{"publisher": e["publisher"], "url": e["url"], "date": e["date"]} for e in pub],
                      "other_publishers": len(v["held"]) + len(v["unsettled"])})
    return {"written_by": "warehouse/deals/public_rows.py --datacenters (session 827)", "retrieved": retrieved_of(projects_path or os.path.join(OUT, "datacenter_projects.csv")),
            "rule": "the same sort as the deals' (shown: an evidence row from a publisher whose verdict is 'may be public'; unsettled: none, and one not read; held: every row asks)",
            "counts": counts(s), "held_publishers": [list(x) for x in held_publishers(s)], "shown": shown}


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


# The events shape's own columns (warehouse/supabase/load.py EVENT_COLS): every other column of the CSV is `extra`
EVENT_COLS = ["event_id", "event_date", "event_type", "parties", "entity_ids", "mw", "price", "currency", "status", "source", "source_url"]
# Session 822: the columns of a shown row that would carry a held outlet's address or name: each is set from the public
# evidence alone (source and source_url are the first story's in the table, which may be a held outlet's)
TRACED = ("source", "source_url", "story_ids", "story_urls")


def retrieved_of(path):
    with open(path, encoding="utf-8") as f:
        for ln in f:
            if ln.startswith("# Retrieved:"):
                return ln.split("Retrieved:")[1].split("(")[0].strip()
            if not ln.startswith("#"):
                break
    return ""


def site_json(deals, sorted_deals, deals_path):
    """The file site/data/deals_public.json (session 822): the counts, and each shown deal as the live set would serve
    its row (the events columns, then `extra` with the table's other columns, a blank left out as the loader leaves it),
    with source, source_url, story_ids and story_urls set from the public evidence rows alone, so that no held outlet's
    address or name is in the file. Held and unsettled deals are counted and not listed: nothing of a held row is here."""
    rows = []
    for d in deals:
        v = sorted_deals.get(d["event_id"])
        if not v or v["sort"] != SHOWN:
            continue
        pub = [e for e in v["evidence"] if e["kind"] == SHOWN]
        r = {c: (None if c in ("mw", "price") and d[c] == "" else (float(d[c]) if c in ("mw", "price") else d[c])) for c in EVENT_COLS}
        r["source"], r["source_url"] = pub[0]["publisher"], pub[0]["url"]
        extra = {c: d[c] for c in d if c not in EVENT_COLS and d[c] != "" and c not in TRACED}
        extra["story_ids"] = ";".join(e["story_id"] for e in pub)
        extra["story_urls"] = ";".join(e["url"] for e in pub)
        r["extra"] = extra
        r["public_evidence"] = [{"publisher": e["publisher"], "url": e["url"], "date": e["date"]} for e in pub]
        r["other_publishers"] = len(v["held"]) + len(v["unsettled"])  # a count, never a name
        rows.append(r)
    rows.sort(key=lambda r: (r["event_date"], r["event_id"]), reverse=True)
    # session 823: the held and unsettled deals counted by the month of their date (a count a month, nothing of a row),
    # so the tracker's chart can hatch the months whose deals are not drawn
    held_by_month = {}
    for d in deals:
        v = sorted_deals.get(d["event_id"])
        if v and v["sort"] != SHOWN:
            m = d["event_date"][:7]
            held_by_month[m] = held_by_month.get(m, 0) + 1
    return {"written_by": "warehouse/deals/public_rows.py --json (session 822)",
            "held_by_month": held_by_month,
            "retrieved": retrieved_of(deals_path),
            "rule": "shown: at least one evidence row from a publisher whose verdict is 'may be public'; unsettled: none, and one from a publisher not read; held: every evidence row asks for permission",
            "counts": counts(sorted_deals),
            "shown": rows}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--deals")
    ap.add_argument("--evidence")
    ap.add_argument("--json", help="write the sort, one entry a deal, to this path")
    ap.add_argument("--markdown", action="store_true", help="print the review's tables")
    ap.add_argument("--datacenters", help="session 827: write datacenter_projects' sort to this path (site/data/datacenters_public.json)")
    a = ap.parse_args(argv)
    if a.datacenters:
        out = datacenters_json(a.deals, a.evidence)
        with open(a.datacenters, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=1, sort_keys=True, ensure_ascii=False)
            f.write("\n")
        print(f"wrote {a.datacenters}: {len(out['shown'])} shown rows, {out['counts']}; held publishers {out['held_publishers'][:5]}")
        return 0
    deals, evidence, registry, verdicts = load(a.deals, a.evidence)
    s = sort_deals(deals, evidence, registry, verdicts)
    c = counts(s)
    if a.json:
        out = site_json(deals, s, a.deals or os.path.join(OUT, "energy_deals.csv"))
        os.makedirs(os.path.dirname(os.path.abspath(a.json)), exist_ok=True)
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=1, sort_keys=True, ensure_ascii=False)
            f.write("\n")
        print(f"wrote {a.json}: {len(out['shown'])} shown rows, {c}")
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
