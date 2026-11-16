#!/usr/bin/env python3
"""ERW, the policy monitor (/policy?view=monitor): an independent replication of the page file's figures (session 7006,
chain 301, goal 4).

Written from docs/methods/policy_monitor.md (section 16, "The record") and the table policy_actions alone, not from
warehouse/policy/records.py or monitor_site.py. It groups the documents into records by the method's words:

  - the proceeding ids a document's docket field names join it to every document that names one of them: a FERC
    docket without its sub-number (CP25-539-000 and -001), a hydro project's numbered proceeding (a bare 15249-002, in
    a FERC document only), an NRC docket ID (NRC-2026-0265), an EPA, DOE, EERE, BOEM, OSM, BSEE, IRS, TTB, BLM, FWS or
    DOI docket, an IRS REG number, a RIN, a DOE LNG docket (15-190-LNG), an OSMRE program amendment (WV-124-FOR);
  - a docket whose documents of one day carry different RINs is two records, one a RIN (session 7002);
  - a document that names no proceeding joins only a repeat of its own title from its own body within 45 days;

and recomputes, for every record of site/data/policy/monitor.json: its documents (the file's history), the count,
the newest and the oldest date, the body, title, instrument and status of the newest document, the highest
significance and the sector of the document that has it, every dated step of every document, the next step (the
first on or after the newest document's date, in the method's order of kinds), the first figure, the sources, and the
plain read's and the significance's documents. Prints N of N and each difference.

    python replication/policy/replicate.py [--tables DIR] [--site DIR]

Exit 0 when every figure is equal, 1 when one is not, 2 when the inputs cannot be read. Standard library only.
"""
import argparse
import csv
import datetime as dt
import json
import os
import re
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
csv.field_size_limit(10 ** 9)

IDS = [
    (r"\b((?:CP|RP|ER|EL|RM|AD|PL|PF|RD|DI|EC|EG|ES|PR|OR|IS|QF|TS|NJ|EP|PP|IN|EF|ID|PA|CD)\d{2}-\d{1,5})-\d{3}\b", "ferc"),
    (r"\bP-(\d{1,5}-\d{3})\b|(?<![\w-])(\d{1,5}-\d{3})(?![\w-])", "project"),
    (r"\b(NRC-\d{4}-\d{4})\b", "nrc"),
    (r"\b((?:EPA|DOE|EERE|BOEM|OSM|BSEE|IRS|TTB|BLM|FWS|DOI)-[A-Z0-9-]*\d{4}-\d{4})\b", "docket"),
    (r"\b(REG-\d{6}-\d{2})\b", "irs"),
    (r"\b(\d{2}-\d{1,4}-(?:LNG|NG|CNG))\b", "doe"),
    (r"\b([A-Z]{2}-\d{3}-FOR)\b", "osmre"),
    (r"\b(\d{4}-[A-Z]{2}\d{2})\b", "rin"),
]
ORDER = ["comments_due", "intervention_due", "filing_due", "review_petition_due", "meeting", "review_due",
         "decision_due", "effective", "expires"]
# the page's words for each kind of step (the monitor's "Next step" column, as the file writes them)
WORDS = {"comments_due": "comments due", "intervention_due": "interventions or hearing requests due",
         "filing_due": "filings due", "review_petition_due": "petitions for judicial review due",
         "meeting": "meeting or session", "review_due": "environmental document due", "decision_due": "decision due",
         "effective": "takes effect", "expires": "ends"}


def rows(path):
    with open(path, encoding="utf-8", newline="") as f:
        yield from csv.DictReader(ln for ln in f if not ln.startswith("#"))


def proceedings(docket, body):
    out = []
    for pat, kind in IDS:
        if kind == "project" and body != "FERC":
            continue
        for m in re.finditer(pat, docket or ""):
            k = f"{kind}:{next(g for g in m.groups() if g)}"
            if k not in out:
                out.append(k)
    return out


def group(docs):
    """{event_id: record id} by the method's rules (a union of the documents that share a proceeding id)."""
    docs = sorted(docs, key=lambda d: (d["event_date"][:10], d["event_id"]))
    ids = {d["event_id"]: proceedings(d["docket"], d["body"] or d["agency"]) for d in docs}
    day = {d["event_id"]: d["event_date"][:10] for d in docs}
    rins_by_key, same_day = defaultdict(set), defaultdict(set)
    for e, ks in ids.items():
        rins = [k[4:] for k in ks if k.startswith("rin:")]
        for k in ks:
            if not k.startswith("rin:"):
                rins_by_key[k].update(rins)
                same_day[(k, day[e])].update(rins)
    split = {k for (k, _), v in same_day.items() if len(v) > 1}
    last = {}
    for d in docs:
        e, rins = d["event_id"], [k[4:] for k in ids[d["event_id"]] if k.startswith("rin:")]
        new = []
        for k in ids[e]:
            if k in split:
                r = rins[0] if rins else last.get(k, sorted(rins_by_key[k])[0])
                last[k] = r
                k = f"{k}.{r}"
            new.append(k)
        ids[e] = new
    parent = {}

    def find(x):
        while parent.setdefault(x, x) != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for d in docs:
        for k in ids[d["event_id"]]:
            ra, rb = find(d["event_id"]), find("k=" + k)
            if ra != rb:
                parent[rb] = ra
    seen = {}
    for d in docs:
        e = d["event_id"]
        if ids[e]:
            continue
        key = (d["body"] or d["agency"], re.sub(r"[^a-z0-9]+", " ", d["title"].lower()).strip())
        when = dt.date.fromisoformat(day[e])
        if key in seen and (when - seen[key][1]).days <= 45:
            ra, rb = find(e), find(seen[key][0])
            if ra != rb:
                parent[rb] = ra
        seen[key] = (e, when)
    name, first = {}, {}
    for d in docs:
        r = find(d["event_id"])
        if ids[d["event_id"]] and r not in name:
            name[r] = ids[d["event_id"]][0]
        first.setdefault(r, d["event_id"])
    return {d["event_id"]: name.get(find(d["event_id"])) or f"doc:{first[find(d['event_id'])]}" for d in docs}


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def record(docs, reads):
    """The record's fields from its documents (oldest first)."""
    newest = docs[-1]
    sig = [num(d["significance"]) for d in docs]
    top = max((s for s in sig if s is not None), default=None)
    top_doc = next((d for d, s in zip(docs, sig) if s == top), None) if top is not None else None
    steps, seen = [], set()
    for d in docs:
        pairs = [p for p in d["dates"].split("; ") if p]
        for p in pairs:
            k, day = p.split("=")
            if (k, day) not in seen:
                seen.add((k, day))
                steps.append((k, day))
    ahead = sorted((day, ORDER.index(k), k) for k, day in [(k, day) for d in docs for k, day in
                                                          (p.split("=") for p in d["dates"].split("; ") if p)]
                   if day >= newest["event_date"][:10])
    fig = next((d for d in docs if d["figure_value"]), None)
    plain = None
    for d in docs:
        if (reads.get(d["event_id"]) or {}).get("plain_read"):
            plain = d["event_id"]
    return dict(n=len(docs), date=newest["event_date"][:10], first=docs[0]["event_date"][:10],
                body=newest["body"] or newest["agency"], title=newest["title"], instrument=newest["instrument"],
                status=newest["action_status"], significance=None if top is None else int(top),
                sector=top_doc["sector"] if top_doc else "", steps=sorted(steps),
                next=(WORDS[ahead[0][2]], ahead[0][0]) if ahead else None,
                figure=(float(fig["figure_value"]), fig["figure_unit"], fig["event_id"]) if fig else None,
                sources=sorted({u for d in docs for u in d["source_url"].split(";") if u}),
                plain_doc=plain, significance_doc=top_doc["event_id"] if top_doc else None)


def main(argv=None):
    ap = argparse.ArgumentParser(description="The policy monitor's replication")
    ap.add_argument("--tables", default=os.path.join(ROOT, "warehouse", "output"))
    ap.add_argument("--site", default=os.path.join(ROOT, "site"))
    a = ap.parse_args(argv)
    try:
        with open(os.path.join(a.site, "data", "policy", "monitor.json"), encoding="utf-8") as f:
            mon = json.load(f)
        docs = list(rows(os.path.join(a.tables, "policy_actions.csv")))
        rp = os.path.join(a.tables, "policy_reads.csv")
        reads = {r["action_event_id"]: r for r in rows(rp)} if os.path.exists(rp) else {}
    except (OSError, ValueError, KeyError) as exc:
        print(f"the inputs could not be read: {exc}")
        return 2
    by_id = {d["event_id"]: d for d in docs}
    rid = group(docs)
    recs = defaultdict(list)
    for d in sorted(docs, key=lambda d: (d["event_date"][:10], d["event_id"])):
        recs[rid[d["event_id"]]].append(d)
    n, misses = 0, []

    def check(what, mine, theirs):
        nonlocal n
        n += 1
        if mine != theirs:
            misses.append(f"{what}: replication {mine!r}, file {theirs!r}")

    check("documents", len(docs), mon["documents"])
    check("records", len(recs), mon["records"])
    file_ids = {r["id"] for r in mon["rows"]}
    check("record ids", sorted(set(recs) ^ file_ids)[:5], [])
    for r in mon["rows"]:
        mine_docs = recs.get(r["id"])
        if not mine_docs:
            continue
        got = record(mine_docs, reads)
        hist = [e for h in r.get("history", []) for e in h.rsplit(" ", 1)[-1].split(",")]
        check(f"{r['id']} documents", sorted(d["event_id"] for d in mine_docs), sorted(hist))
        for k in ("n", "date", "first", "body", "title", "instrument", "status", "significance", "sector"):
            check(f"{r['id']} {k}", got[k], r.get(k, "" if k != "significance" else None) if k != "sector" else r.get("sector", ""))
        check(f"{r['id']} steps", got["steps"], sorted((s["kind"], s["date"]) for s in r.get("steps", [])))
        nx = r.get("next")
        check(f"{r['id']} next", got["next"], (nx["step"], nx["date"]) if nx else None)
        fg = r.get("figure")
        check(f"{r['id']} figure", got["figure"], (fg["value"], fg["unit"], fg["event_id"]) if fg else None)
        check(f"{r['id']} sources", got["sources"], sorted(r.get("sources", [])))
        if "plain_doc" in r or got["plain_doc"]:
            check(f"{r['id']} plain_doc", got["plain_doc"], (r.get("plain_doc") or {}).get("event_id"))
        if "significance_doc" in r or got["significance_doc"]:
            check(f"{r['id']} significance_doc", got["significance_doc"], (r.get("significance_doc") or {}).get("event_id"))
    print(f"The policy monitor, from {a.tables} and monitor.json (built {mon['built']}): {mon['records']:,} records "
          f"of {mon['documents']:,} documents")
    for m in misses[:60]:
        print("  " + m)
    print(f"{n - len(misses):,} of {n:,} figures equal")
    return 0 if not misses else 1


if __name__ == "__main__":
    sys.exit(main())
