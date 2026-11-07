#!/usr/bin/env python3
"""One record an action (session 3057, chain 166): the documents of one proceeding grouped, with every source and
a status history.

Energy Research Warehouse (ERW), platform tool 12. A row of policy_actions is one document (a Register notice, rule
or proposed rule, or an agency's release). An action runs through several: a FERC pipeline's application, its
scoping notice, its environmental assessment and its order; the NRC's four weekly notices of one application; a
direct final rule, its parallel proposal and its withdrawal. This module groups the documents that name the same
proceeding into one record. It reads policy_actions and writes nothing but its own table, and only when asked.

    python warehouse/policy/records.py --out runs/policy_action_records.csv    # a trial: any path, no lock
    python warehouse/policy/records.py                                          # the data machine: the warehouse table

What makes two documents one record: the same proceeding id in their docket field (PROCEEDING below, the forms a
proceeding's id takes: a FERC docket, an amendment's -001 with its -000; a hydro project's numbered proceeding; an
NRC docket ID; an EPA, DOE, BOEM, OSM or IRS rulemaking or program docket; a RIN; a DOE LNG docket; an OSMRE program
amendment), joined across rows (a document that names two ids joins their records). What does not: a bureau's
billing code (BLM's A2407-014-004-065516 stood on 52 rows of unrelated matters), an NRC plant's license docket
(50-261 spans exemptions, renewals and transfers), a document number (EPA's FRL- numbers). A document with no
proceeding id is its own record, unless an earlier document of the same body has the same title within 45 days (a
repeated notice). Tested on 30 stored rows whose records were written from their own words
(tests/fixtures/policy/records_3057.json).

The table policy_action_records (events shape, one row a record): event_id (the record's key: its first proceeding
id, "ferc:CP25-539", "nrc:NRC-2026-0265", or "doc:<event_id>" of a document that names none), event_date (the newest
document's), event_type "policy_record", parties (the body), entity_ids, mw, price, currency (empty), status (the
newest document's action_status), source ("erw:policy_actions"), source_url (the newest document's), body, title
(the newest document's), first_date, last_date, n_documents, event_ids, proceeding_ids, instruments, history (one
entry a distinct step:
"date instrument status event_id", a repeated notice once with every date), next_step, next_step_date,
next_step_evidence (the first dated step on or after the newest document's date, of any document), figure_value,
figure_unit, figure_evidence, figure_event_id (the first document that states one), significance (the highest),
sector (of the most significant document), source_urls, related_urls, news_story_ids, news_story_urls (every
source of every document, once each).
"""

import argparse
import os
import re
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import policy_fields as pf  # noqa: E402  session 3233: its own name, beside the deals tracker's fields

NAME = "policy_action_records"
SOURCE = "policy_actions"
REPEAT_DAYS = 45

# The forms a proceeding's id takes, each with the key it is grouped by (a FERC docket's sub-number dropped: an
# amendment, -001, is filed in the proceeding of its -000).
PROCEEDING = [
    (re.compile(r"\b((?:CP|RP|ER|EL|RM|AD|PL|PF|RD|DI|EC|EG|ES|PR|OR|IS|QF|TS|NJ|EP|PP|IN|EF|ID|PA|CD)\d{2}-\d{1,5})-\d{3}\b"), "ferc:{}"),
    (re.compile(r"\bP-(\d{1,5}-\d{3})\b|(?<![\w-])(\d{1,5}-\d{3})(?![\w-])"), "project:{}"),
    (re.compile(r"\b(NRC-\d{4}-\d{4})\b"), "nrc:{}"),
    (re.compile(r"\b((?:EPA|DOE|EERE|BOEM|OSM|BSEE|IRS|TTB|BLM|FWS|DOI)-[A-Z0-9-]*\d{4}-\d{4})\b"), "docket:{}"),
    (re.compile(r"\b(REG-\d{6}-\d{2})\b"), "irs:{}"),
    (re.compile(r"\b(\d{2}-\d{1,4}-(?:LNG|NG|CNG))\b"), "doe:{}"),
    (re.compile(r"\b([A-Z]{2}-\d{3}-FOR)\b"), "osmre:{}"),
    (re.compile(r"\b(\d{4}-[A-Z]{2}\d{2})\b"), "rin:{}"),
]


def proceeding_ids(docket, body="FERC"):
    """The proceeding keys a docket field names, in order, each once. A bare "2538-106" is a hydro project's
    proceeding only in a FERC document: elsewhere the same shape is an NRC plant's docket (50-261)."""
    out = []
    for pat, form in PROCEEDING:
        if form == "project:{}" and body != "FERC":
            continue
        for m in pat.finditer(docket or ""):
            key = form.format(next(g for g in m.groups() if g))
            if key not in out:
                out.append(key)
    return out


def norm_title(t):
    return re.sub(r"[^a-z0-9]+", " ", (t or "").lower()).strip()


def group(rows):
    """{event_id: record_id} over the rows (dicts with event_id, event_date, agency or body, title, docket). The
    record_id is the record's first proceeding key, or "doc:<event_id>" of its first document."""
    parent = {}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    rows = sorted(rows, key=lambda r: (r["event_date"][:10], r["event_id"]))
    keys_of = {}
    for r in rows:
        e = r["event_id"]
        parent.setdefault(e, e)
        keys = proceeding_ids(r.get("docket", ""), r.get("body") or r.get("agency", ""))
        keys_of[e] = keys
        for k in keys:
            parent.setdefault("key=" + k, "key=" + k)
            union(e, "key=" + k)
    # a document with no proceeding id: one record with an earlier document of its body and title within 45 days
    last = {}
    for r in rows:
        e = r["event_id"]
        if keys_of[e]:
            continue
        t = (r.get("body") or r.get("agency", ""), norm_title(r.get("title")))
        d = pd.Timestamp(r["event_date"][:10])
        if t in last and (d - last[t][1]).days <= REPEAT_DAYS:
            union(e, last[t][0])
        last[t] = (e, d)
    # each record's id: its first proceeding key (the first named by its oldest document), else its oldest document
    name = {}
    for r in rows:
        root = find(r["event_id"])
        if keys_of[r["event_id"]] and not name.get(root):
            name[root] = keys_of[r["event_id"]][0]
        name.setdefault(root, None)
    first_doc = {}
    for r in rows:
        first_doc.setdefault(find(r["event_id"]), r["event_id"])
    return {r["event_id"]: name[find(r["event_id"])] or f"doc:{first_doc[find(r['event_id'])]}" for r in rows}


def _join(values):
    seen = []
    for v in values:
        for x in str(v or "").split(";"):
            x = x.strip()
            if x and x not in seen:
                seen.append(x)
    return ";".join(seen)


def records(actions):
    """The records of a frame of policy_actions (with the fields of session 3056, derived here where absent)."""
    a = actions.copy().fillna("")
    for c in pf.FIELD_COLS:
        if c not in a.columns:
            a[c] = ""
    need = a["fields_from"] == ""
    for i in a.index[need]:
        a.loc[i, pf.FIELD_COLS] = pd.Series(pf.derive(a.loc[i].to_dict(), "", None))
    rid = group(a.to_dict("records"))
    a["record_id"] = a["event_id"].map(rid)
    a["_d"] = a["event_date"].str[:10]
    a["_sig"] = pd.to_numeric(a.get("significance", ""), errors="coerce")
    out = []
    for r_id, g in a.sort_values(["_d", "event_id"]).groupby("record_id", sort=False):
        newest = g.iloc[-1]
        hist, seen = [], {}
        for _, x in g.iterrows():
            step = (x["instrument"], x["action_status"], norm_title(x["title"]))
            if step in seen:
                hist[seen[step]][0].append(x["_d"])
                hist[seen[step]][3].append(x["event_id"])
                continue
            seen[step] = len(hist)
            hist.append(([x["_d"]], x["instrument"], x["action_status"], [x["event_id"]]))
        history = " | ".join(f"{','.join(d)} {i} {s} {','.join(e)}" for d, i, s, e in hist)
        steps = []
        for _, x in g.iterrows():
            for pair, ev in zip([p for p in x["dates"].split("; ") if p], (x["dates_evidence"] or "").split(" | ")):
                k, d = pair.split("=")
                steps.append((k, d, ev))
        nxt = pf.next_step(steps, newest["_d"])
        fig = g[g["figure_value"] != ""]
        f0 = fig.iloc[0] if len(fig) else None
        top = g.sort_values("_sig", ascending=False, na_position="last").iloc[0]
        out.append({
            "event_id": r_id, "event_date": newest["_d"], "event_type": "policy_record",
            "parties": newest["body"] or newest.get("agency", ""), "entity_ids": "", "mw": "", "price": "", "currency": "",
            "status": newest["action_status"], "source": "erw:" + SOURCE, "source_url": newest["source_url"],
            "body": newest["body"] or newest.get("agency", ""), "title": newest["title"],
            "first_date": g["_d"].min(), "last_date": g["_d"].max(), "n_documents": str(len(g)),
            "event_ids": ";".join(g["event_id"]), "proceeding_ids": _join(";".join(proceeding_ids(x, b)) for x, b in zip(g["docket"], g["body"])),
            "instruments": _join(g["instrument"]), "history": history,
            "next_step": nxt[0], "next_step_date": nxt[1], "next_step_evidence": nxt[2],
            "figure_value": "" if f0 is None else f0["figure_value"], "figure_unit": "" if f0 is None else f0["figure_unit"],
            "figure_evidence": "" if f0 is None else f0["figure_evidence"], "figure_event_id": "" if f0 is None else f0["event_id"],
            "significance": "" if pd.isna(top["_sig"]) else str(int(top["_sig"])), "sector": top.get("sector", ""),
            "source_urls": _join(g["source_url"]), "related_urls": _join(g.get("related_urls", [])),
            "news_story_ids": _join(g.get("news_story_ids", [])), "news_story_urls": _join(g.get("news_story_urls", []))})
    return pd.DataFrame(out, columns=COLS)


COLS = ["event_id", "event_date", "event_type", "parties", "entity_ids", "mw", "price", "currency", "status", "source",
        "source_url", "body", "title", "first_date", "last_date", "n_documents", "event_ids", "proceeding_ids", "instruments",
        "history", "next_step", "next_step_date", "next_step_evidence", "figure_value", "figure_unit", "figure_evidence",
        "figure_event_id", "significance", "sector", "source_urls", "related_urls", "news_story_ids", "news_story_urls"]


def read_actions(path):
    with open(path, encoding="utf-8") as f:
        skip = sum(1 for ln in f if ln.startswith("#"))
    return pd.read_csv(path, skiprows=skip, dtype=str, keep_default_na=False)


def main(argv=None):
    sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
    import iso_prices as ip
    ap = argparse.ArgumentParser(description="ERW policy action records (session 3057)")
    ap.add_argument("--actions", default=os.path.join(ip.OUT_DIR, SOURCE + ".csv"))
    ap.add_argument("--out", help="a trial: write here (any path, no data lock), not to the warehouse table")
    args = ap.parse_args(argv)
    a = read_actions(args.actions)
    r = records(a)
    run = pd.Timestamp.now(tz="UTC").strftime("%Y%m%dT%H%M%SZ")
    header = [
        "Energy Research Warehouse (ERW): policy action records: the documents of policy_actions that name one "
        "proceeding, grouped, with every source and a status history",
        "Shape: events (docs/datastandard.md v0), event_type policy_record; one row a record; event_date is its newest "
        "document's date; the columns are described in warehouse/policy/records.py.",
        f"Retrieved: {run} (UTC) by warehouse/policy/records.py, from erw:{SOURCE} ({len(a)} documents, {len(r)} records)",
        f"Source: erw:{SOURCE} (the Federal Register and agency news releases).",
        "License: public (US and state government publications)."]
    if args.out:
        os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
        with open(args.out, "w", encoding="utf-8", newline="") as f:
            for h in header:
                f.write(f"# {h}\n")
            r.to_csv(f, index=False, lineterminator="\n")
        print(f"{NAME}: {len(a)} documents, {len(r)} records, written to {args.out}")
        return 0
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{NAME}_{run}.log"))
    ip.write_csv(r, NAME, header, log, cols=COLS, key=["event_id"], time_col="event_date")
    return 0


if __name__ == "__main__":
    sys.exit(main())
