#!/usr/bin/env python3
"""The large-load statements, public where it is safe (session 255).

Energy Research Warehouse (ERW). Two tables, both flagged INTERNAL until the owner rules:

    large_load_document_verdicts   events, one row a source document behind large_load_statements and
                                   large_load_waits: what kind of document it is, read from its address and the
                                   table's own columns, and a license verdict in session 205's words
    large_load_public              events, one row a statement whose document's verdict is "public": the entity,
                                   megawatts or a duration, the stage as one of the ERW's five classes, the date, the
                                   document's title, page and link. NO QUOTED TEXT: no sentence of a document, and not
                                   the stage or the load's kind in the document's own words

The rule (the owner's, in the prompt of session 255): a public regulatory filing and an SEC filing state facts that
may be republished as facts with a link; long quotation may not. So a statement is "public" when its document is

    an SEC filing             the address is on EDGAR (www.sec.gov)
    a regulatory filing       the address is a regulator's own docket or site (REGULATORS below)
    a read publisher's        the address is the site of a publisher whose terms session 205 read and found "may be
                              public" both as the ERW is today and if it sells anything
                              (warehouse/metadata/license_verdicts.csv: ERCOT, CAISO), kept apart by its basis. SPP's
                              terms allow copying today and ask for written consent for any commercial use, and its
                              tables are held by the ruling of 12 October 2026: its documents are not public here

and no other. A filed document read from the filer's own site, a company's presentation, an operator's report under
terms that ask for permission, a federal body's document and a third party's copy are each given their verdict and
are not in large_load_public. Two more things keep a public document's row out: an address that holds a filer's
e-mail address (48 rows: the commission's own public address, and still a person's e-mail), and an address that is
not https.

No request is made to anyone: the verdicts rest on the address, the document's type as the table holds it, and the
terms session 205 read. Nothing of large_load_waits is public: its four publishers are a grid operator whose notice
reserves all rights, a Canadian operator whose terms allow non-commercial use, a federal agency and a public utility
district whose sites state no terms.

    python warehouse/derived/large_load_public.py            # writes the two tables (under the data lock)
    python warehouse/derived/large_load_public.py --summary  # prints the counts as JSON; writes nothing
"""

import argparse
import datetime as dt
import hashlib
import json
import os
import sys
import traceback
import urllib.parse

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "connectors"))
import iso_prices as ip  # noqa: E402

PUBLIC, VERDICTS = "large_load_public", "large_load_document_verdicts"
SOURCE_PUBLIC, SOURCE_VERDICTS = "erw:large_load_public", "erw:large_load_document_verdicts"
METHOD_URL = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/large_load_public.md"
RULE = "a fact it states may be republished as a fact, with a link to it; no long quotation"
V_PUBLIC, V_PERMISSION, V_UNSETTLED, V_NOT = "public", "needs written permission", "not settled", "not public"
MAY = "may be public"

# A regulator's own docket or site: host -> (the body, its state). www.in.gov is the State of Indiana's site: only its
# /iurc/ folder is the commission's.
REGULATORS = {
    "psc.ky.gov": ("Kentucky Public Service Commission", "KY"),
    "interchange.puc.texas.gov": ("Public Utility Commission of Texas", "TX"),
    "www.scc.virginia.gov": ("Virginia State Corporation Commission", "VA"),
    "docs.cpuc.ca.gov": ("California Public Utilities Commission", "CA"),
    "www.cpuc.ca.gov": ("California Public Utilities Commission", "CA"),
    "efiling.energy.ca.gov": ("California Energy Commission", "CA"),
    "www.energy.ca.gov": ("California Energy Commission", "CA"),
    "services.psc.ga.gov": ("Georgia Public Service Commission", "GA"),
    "www.puc.pa.gov": ("Pennsylvania Public Utility Commission", "PA"),
    "www.in.gov": ("Indiana Utility Regulatory Commission", "IN"),
    "documents.dps.ny.gov": ("New York State Department of Public Service", "NY"),
    "dms.psc.sc.gov": ("Public Service Commission of South Carolina", "SC"),
    "www.floridapsc.com": ("Florida Public Service Commission", "FL"),
    "floridapsc.com": ("Florida Public Service Commission", "FL"),
    "efis.psc.mo.gov": ("Missouri Public Service Commission", "MO"),
    "psc.mo.gov": ("Missouri Public Service Commission", "MO"),
    "www.dora.state.co.us": ("Colorado Public Utilities Commission", "CO"),
    "lpscpubvalence.lpsc.louisiana.gov": ("Louisiana Public Service Commission", "LA"),
    "www.lpsc.louisiana.gov": ("Louisiana Public Service Commission", "LA"),
    "psc.maryland.gov": ("Maryland Public Service Commission", "MD"),
    "mi-psc.my.site.com": ("Michigan Public Service Commission", "MI"),
    "apps.psc.wi.gov": ("Public Service Commission of Wisconsin", "WI"),
    "pscdocs.utah.gov": ("Public Service Commission of Utah", "UT"),
    "puc.sd.gov": ("South Dakota Public Utilities Commission", "SD"),
    "powerreview.nebraska.gov": ("Nebraska Power Review Board", "NE"),
    "www.ferc.gov": ("Federal Energy Regulatory Commission", "US"),
}
# A publisher whose terms session 205 read: host -> its key in warehouse/metadata/license_verdicts.csv.
READ_PUBLISHERS = {"www.ercot.com": "ERCOT", "www.caiso.com": "CAISO", "stakeholdercenter.caiso.com": "CAISO", "www.pjm.com": "PJM", "www.nyiso.com": "NYISO",
                   "www.iso-ne.com": "ISO-NE", "isonewswire.com": "ISO-NE", "www.spp.org": "SPP", "spp.org": "SPP"}
# A body of the United States government (its own work is in the public domain, 17 U.S.C. 105; the ruling names two
# kinds of document and this is neither, so it waits for the owner).
FEDERAL = {"www.bpa.gov": "Bonneville Power Administration", "www.congress.gov": "Congressional Research Service"}
FILED_TYPES = {"commission filing", "large load tariff filing", "rate case testimony", "integrated resource plan", "sec filing"}
# large_load_waits: its four publishers by the table's `source`, each with the verdict the table's own header records.
WAIT_PUBLISHERS = {
    "nyiso:interconnection_queue_dated_copies": ("New York ISO", V_PERMISSION, "session 205's read of NYISO's legal notice (license_verdicts.csv, NYISO): no license is conferred and all rights are reserved"),
    "aeso:connection_project_list_dated_copies": ("Alberta Electric System Operator", V_PERMISSION, "its terms allow use for non-commercial, personal or educational purposes and no other without written permission (session 165)"),
    "bpa:interconnection_queue_dated_copies": ("Bonneville Power Administration", V_UNSETTLED, "a body of the United States government, whose own work is in the public domain (17 U.S.C. 105); its site states no terms, and it is neither of the two kinds of document the ruling names"),
    "grantpud:interconnection_queue_dated_copies": ("Grant County Public Utility District", V_UNSETTLED, "its site states no terms of use for its documents (session 155)"),
}
# Where an entity is, for the report's counts by grid and state: entity -> (the states it serves, the grid of the page
# it is in: one of the seven, "more than one", or "none of the seven"). Written by hand in session 255 for the
# entities that hold a public row, from each entity's own service territory; an entity not here is counted under "not
# placed". Words about places, not numbers. A row of a regulatory filing takes its state from the regulator instead.
NONE, SEVERAL = "none of the seven", "more than one"
PLACE = {
    "AES Indiana": ("IN", "miso"),
    "Interstate Power and Light": ("IA", "miso"),
    "Wisconsin Power and Light": ("WI", "miso"),
    "Amazon Data Services, Inc. (about Dominion Energy Virginia)": ("VA", "pjm"),
    "Ameren Missouri (Union Electric Company)": ("MO", "miso"),
    "American Electric Power": ("AR, IN, KY, LA, MI, OH, OK, TN, TX, VA, WV", SEVERAL),
    "Appalachian Power (AEP)": ("VA, WV", "pjm"),
    "Indiana Michigan Power (AEP)": ("IN, MI", "pjm"),
    "Arizona Public Service": ("AZ", NONE),
    "Big Rivers Electric Corporation": ("KY", "miso"),
    "Consumers Energy": ("MI", "miso"),
    "California Energy Commission (the data center forecast California ISO relies on)": ("CA", "caiso"),
    "California ISO": ("CA", "caiso"),
    "California Public Utilities Commission": ("CA", "caiso"),
    "CenterPoint Energy Houston Electric": ("TX", "ercot"),
    "DTE Electric Company": ("MI", "miso"),
    "Dominion Energy Virginia (Virginia Electric and Power Company)": ("NC, VA", "pjm"),
    "Duke Energy Carolinas and Duke Energy Progress": ("NC, SC", NONE),
    "Duquesne Light": ("PA", "pjm"),
    "ERCOT": ("TX", "ercot"),
    "East Kentucky Power Cooperative": ("KY", "pjm"),
    "El Paso Electric": ("NM, TX", NONE),
    "Entergy Louisiana": ("LA", "miso"),
    "Evergy Metro (Evergy Missouri Metro and Evergy Kansas Metro)": ("KS, MO", "spp"),
    "Evergy Missouri Metro": ("MO", "spp"),
    "Evergy Missouri West": ("MO", "spp"),
    "Exelon": ("DC, DE, IL, MD, NJ, PA", "pjm"),
    "PECO (Exelon)": ("PA", "pjm"),
    "Federal Energy Regulatory Commission": ("US", SEVERAL),
    "FirstEnergy (Ohio, Pennsylvania, Maryland, West Virginia and New Jersey utilities)": ("MD, NJ, OH, PA, WV", "pjm"),
    "FirstEnergy Pennsylvania Electric Company (with FirstEnergy's transmission companies)": ("PA", "pjm"),
    "Georgia Power": ("GA", NONE),
    "Southern Company traditional electric operating companies (Alabama Power, Georgia Power, Mississippi Power)": ("AL, GA, MS", NONE),
    "Google LLC (about Dominion Energy Virginia)": ("VA", "pjm"),
    "Hoosier Energy": ("IL, IN", "miso"),
    "JEA": ("FL", NONE),
    "Joint Utilities of New York (Central Hudson, Con Edison, NYSEG, National Grid, Orange & Rockland, RG&E)": ("NY", "nyiso"),
    "Louisiana Public Service Commission": ("LA", "miso"),
    "Louisiana Public Service Commission (on Cleco Power's docket U-38035)": ("LA", "miso"),
    "Maryland Public Service Commission": ("MD", "pjm"),
    "National Grid (Niagara Mohawk Power Corporation)": ("NY", "nyiso"),
    "National Grid (United States utilities)": ("MA, NY", SEVERAL),
    "Nebraska Power Association (statewide: NPPD, OPPD, LES and others)": ("NE", "spp"),
    "Nebraska Public Power District": ("NE", "spp"),
    "Omaha Public Power District": ("NE", "spp"),
    "Florida Power & Light": ("FL", NONE),
    "Northern Indiana Public Service Company (NIPSCO)": ("IN", "miso"),
    "Northern Virginia Electric Cooperative (NOVEC)": ("VA", "pjm"),
    "Old Dominion Electric Cooperative": ("DE, MD, VA", "pjm"),
    "Oncor Electric Delivery": ("TX", "ercot"),
    "Otter Tail Power": ("MN, ND, SD", "miso"),
    "Louisville Gas and Electric Company and Kentucky Utilities Company": ("KY", NONE),
    "PPL Electric Utilities": ("PA", "pjm"),
    "PacifiCorp (Rocky Mountain Power and Pacific Power)": ("CA, ID, OR, UT, WA, WY", NONE),
    "Pacific Gas and Electric": ("CA", "caiso"),
    "Pennsylvania Public Utility Commission": ("PA", "pjm"),
    "Public Utility Commission of Texas": ("TX", "ercot"),
    "Rappahannock Electric Cooperative": ("VA", "pjm"),
    "San Diego Gas & Electric": ("CA", "caiso"),
    "Southern California Edison": ("CA", "caiso"),
    "Southwest Power Pool": ("AR, IA, KS, LA, MN, MO, MT, ND, NE, NM, OK, SD, TX, WY", "spp"),
    "Texas-New Mexico Power": ("TX", "ercot"),
    "Tampa Electric": ("FL", NONE),
    "Tucson Electric Power": ("AZ", NONE),
    "WEC Energy Group (Wisconsin utilities; the data center load is in We Energies' territory)": ("WI", "miso"),
    "Wabash Valley Power Alliance": ("IL, IN, MO", SEVERAL),
    "Public Service Company of Colorado": ("CO", NONE),
}
FIGURE_MAX = 48                   # a duration as stated is a figure: a number, its unit and its bound. Longer is a clause of the document
IN_WORDS = "stated in words, not as a figure: see the document"
STAGES = {"1 request or inquiry", "2 study or engineering", "3 financial commitment", "4 signed service agreement", "5 under construction or energized"}
PUBLIC_COLS = ["event_id", "event_date", "event_type", "parties", "entity_ids", "mw", "price", "currency", "status", "source", "source_url",
               "entity_group", "entity_type", "row_kind", "mw_low", "mw_high", "duration_as_stated", "wait_basis", "wait_counted", "load_scope", "stage_class",
               "document_title", "document_type", "page", "event_date_basis", "document_class", "public_basis", "regulator", "state", "grid", "source_flag",
               "statement_id", "retrieved_at"]
VERDICT_COLS = ["event_id", "event_date", "event_type", "parties", "entity_ids", "mw", "price", "currency", "status", "source", "source_url",
                "of_table", "host", "document_title", "document_type", "document_class", "verdict_basis", "regulator_state", "rows", "rows_public",
                "address_holds_email", "retrieved_at"]


def read(name, in_dir=None):
    path = os.path.join(in_dir or ip.OUT_DIR, name + ".csv")
    return pd.read_csv(path, skiprows=ip.header_rows(path), dtype=str, keep_default_na=False)


def publisher_verdicts(path=None):
    """{key: (verdict as the ERW is today, verdict if it sells anything, read number)} of the publishers session 205 read."""
    path = path or os.path.join(HERE, "..", "metadata", "license_verdicts.csv")
    d = pd.read_csv(path, dtype=str, keep_default_na=False)
    return {k: (v, c, r) for k, v, c, r in zip(d["key"], d["verdict"], d["if_commercial"], d["read"])}


def holds_email(url):
    return "@" in url or "%40" in url.lower()


def classify(url, document_type, source_flag, read_publishers):
    """(document_class, verdict, basis, publisher or body, the regulator's state or "") for one statement's document."""
    u = urllib.parse.urlparse(url)
    host, kind = u.netloc.lower(), document_type.strip().lower()
    if source_flag.startswith("a third party's copy"):
        return "third party's copy", V_NOT, "the address is a third party's copy of the document, not its publisher's or a regulator's", host, ""
    if host == "www.sec.gov":
        return "SEC filing", V_PUBLIC, f"filed with or furnished to the Securities and Exchange Commission, read from EDGAR: {RULE}", "Securities and Exchange Commission (EDGAR)", ""
    if host in REGULATORS and (host != "www.in.gov" or u.path.startswith("/iurc/")):
        body, state = REGULATORS[host]
        return "regulatory filing", V_PUBLIC, f"a public regulatory filing, read from the regulator's own docket or site: {RULE}", body, state
    if host in READ_PUBLISHERS:
        key = READ_PUBLISHERS[host]
        verdict, sold, n = read_publishers.get(key, ("", "", ""))
        if verdict == MAY and sold == MAY:
            return "read publisher's document", V_PUBLIC, (f"session 205 read {key}'s terms (license_verdicts.csv, read {n}): may be public, today and if the ERW sells anything. "
                                                           "Not one of the two kinds the ruling names: kept apart by this basis"), key, ""
        if verdict == MAY:
            return "read publisher's document", V_PERMISSION, (f"session 205 read {key}'s terms (license_verdicts.csv, read {n}): may be public as the ERW is today, {sold} if it "
                                                               "sells anything; held with the publisher's tables"), key, ""
        if verdict:
            return "read publisher's document", verdict, f"session 205 read {key}'s terms (license_verdicts.csv, read {n}): {verdict}", key, ""
        return "read publisher's document", V_UNSETTLED, f"{key} is not in license_verdicts.csv", key, ""
    if host in FEDERAL:
        return "federal body's document", V_UNSETTLED, ("a body of the United States government, whose own work is in the public domain (17 U.S.C. 105); "
                                                         "neither of the two kinds of document the ruling names, so it waits for the owner"), FEDERAL[host], ""
    if kind in FILED_TYPES:
        return "filed document, the filer's own copy", V_UNSETTLED, ("a filed document read from the filer's own site, whose terms were not read; the regulator's or the SEC's "
                                                                     "copy of it would be public"), host, ""
    return "publisher's own document", V_UNSETTLED, "the publisher's terms were not read (a company's, a public power body's or a laboratory's own site)", host, ""


def duration_of(written):
    """A wait row's figure as written, when it is a figure; a clause of the document is not copied."""
    t = " ".join(written.split())
    return t if len(t) <= FIGURE_MAX else IN_WORDS


def doc_id(table, url):
    return "lldoc:" + hashlib.sha1(f"{table}|{url}".encode("utf-8")).hexdigest()[:16]


def build(statements, waits, read_publishers, today):
    """(the public rows, the verdict rows) as two DataFrames."""
    s = statements.copy()
    got = [classify(u, t, f, read_publishers) for u, t, f in zip(s["source_url"], s["document_type"], s["source_flag"])]
    s["document_class"], s["verdict"], s["verdict_basis"], s["body"], s["reg_state"] = zip(*got) if len(s) else ([], [], [], [], [])
    s["email"] = s["source_url"].map(holds_email)
    s["is_public"] = (s["verdict"] == V_PUBLIC) & ~s["email"] & s["source_url"].str.startswith("https://")
    # the verdicts, one row a document
    v = []
    for url, g in s.groupby("source_url", sort=True):
        r = g.iloc[0]
        v.append(dict(event_id=doc_id("large_load_statements", url), event_date=today, event_type="license_verdict", parties=r["body"], entity_ids="", mw="", price="", currency="",
                      status=r["verdict"], source=SOURCE_VERDICTS, source_url=url, of_table="large_load_statements", host=urllib.parse.urlparse(url).netloc.lower(),
                      document_title=r["document_title"], document_type=r["document_type"], document_class=r["document_class"], verdict_basis=r["verdict_basis"],
                      regulator_state=r["reg_state"], rows=len(g), rows_public=int(g["is_public"].sum()), address_holds_email="yes" if r["email"] else "no"))
    for url, g in waits.groupby("source_url", sort=True):
        r = g.iloc[0]
        body, verdict, basis = WAIT_PUBLISHERS.get(r["source"], (r["source"], V_UNSETTLED, "the publisher is not one this builder knows"))
        host = urllib.parse.urlparse(url).netloc.lower()
        v.append(dict(event_id=doc_id("large_load_waits", url), event_date=today, event_type="license_verdict", parties=body, entity_ids="", mw="", price="", currency="",
                      status=verdict, source=SOURCE_VERDICTS, source_url=url, of_table="large_load_waits", host=host,
                      document_title="", document_type="a dated copy of a public queue" + (" (the Internet Archive's copy)" if host == "web.archive.org" else ""),
                      document_class="queue copy", verdict_basis=basis, regulator_state="", rows=len(g), rows_public=0, address_holds_email="yes" if holds_email(url) else "no"))
    verdicts = pd.DataFrame(v, columns=[c for c in VERDICT_COLS if c != "retrieved_at"])
    # the public rows: a figure, a class, a date, a title and a link; no words of the document
    p = s[s["is_public"]]
    rows = []
    for _, r in p.iterrows():
        states, grid = PLACE.get(r["entity"], ("", "not placed"))
        rows.append(dict(event_id="llpub:" + r["event_id"].split(":", 1)[1], event_date=r["event_date"], event_type="large_load_statement", parties=r["entity"], entity_ids="",
                         mw=r["mw"] if r["row_kind"] == "mw" else "", price="", currency="",
                         status=r["stage_class"] if r["stage_class"] in STAGES else "not classed", source=SOURCE_PUBLIC, source_url=r["source_url"],
                         entity_group=r["entity_group"], entity_type=r["entity_type"], row_kind=r["row_kind"], mw_low=r["mw_low"], mw_high=r["mw_high"],
                         duration_as_stated=duration_of(r["quantity_as_written"]) if r["row_kind"] == "wait" else "", wait_basis=r["wait_basis"], wait_counted=r["wait_counted"],
                         load_scope=r["load_scope"], stage_class=r["stage_class"], document_title=r["document_title"].strip(), document_type=r["document_type"],
                         page=r["page"], event_date_basis=r["event_date_basis"], document_class=r["document_class"],
                         public_basis={"SEC filing": "SEC filing", "regulatory filing": "public regulatory filing"}.get(r["document_class"], "publisher's terms read in session 205"),
                         regulator=r["body"] if r["document_class"] == "regulatory filing" else "", state=r["reg_state"] or states, grid=grid, source_flag=r["source_flag"],
                         statement_id=r["event_id"]))
    public = pd.DataFrame(rows, columns=[c for c in PUBLIC_COLS if c != "retrieved_at"])
    return public, verdicts, s


def summary(public, verdicts, s):
    """The counts the report prints: documents by class and verdict, rows and entities public by basis, grid and state."""
    def count(frame, by):
        return {str(k): int(v) for k, v in frame.groupby(by).size().items()}
    vs = verdicts[verdicts["of_table"] == "large_load_statements"]
    out = {"statements": int(len(s)), "documents": int(vs["source_url"].nunique()), "documents_of_waits": int((verdicts["of_table"] == "large_load_waits").sum()),
           "documents_by_class": count(vs, "document_class"), "documents_by_verdict": count(vs, "status"),
           "rows_by_class": {str(k): int(v) for k, v in s.groupby("document_class").size().items()}, "rows_by_verdict": {str(k): int(v) for k, v in s.groupby("verdict").size().items()},
           "waits_documents_by_verdict": count(verdicts[verdicts["of_table"] == "large_load_waits"], ["parties", "status"]),
           "waits_rows_by_publisher": {str(k): int(v) for k, v in verdicts[verdicts["of_table"] == "large_load_waits"].groupby("parties")["rows"].sum().items()},
           "public_verdict_rows": int((s["verdict"] == V_PUBLIC).sum()), "held_out_for_an_email_address": int(((s["verdict"] == V_PUBLIC) & s["email"]).sum()),
           "public_rows": int(len(public)), "public_entities": int(public["parties"].nunique()), "public_groups": int(public["entity_group"].nunique()),
           "public_documents": int(public["source_url"].nunique()),
           "public_by_basis": count(public, "public_basis"), "public_by_kind": count(public, "row_kind"), "public_by_stage": count(public, "status"),
           "public_by_grid": {}, "public_by_state": {}, "public_waits_counted": int(((public["row_kind"] == "wait") & (public["wait_counted"] == "yes")).sum()),
           "entities_all": int(s["entity"].nunique()), "groups_all": int(s["entity_group"].nunique())}
    for col in ("grid", "state"):
        for k, g in public.groupby(col):
            out[f"public_by_{col}"][str(k)] = {"statements": int(len(g)), "megawatt_rows": int((g["row_kind"] == "mw").sum()), "duration_rows": int((g["row_kind"] == "wait").sum()),
                                               "entities": int(g["parties"].nunique()), "groups": sorted(g["entity_group"].unique())}
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW: the large-load statements, public where it is safe (session 255)")
    ap.add_argument("--summary", action="store_true", help="print the counts as JSON and write nothing")
    a = ap.parse_args(argv)
    today = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")
    if a.summary:
        public, verdicts, s = build(read("large_load_statements"), read("large_load_waits"), publisher_verdicts(), today)
        print(json.dumps(summary(public, verdicts, s), indent=1))
        return 0
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    retrieved = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{PUBLIC}_{run_id}.log"))
    results = []
    try:
        public, verdicts, s = build(read("large_load_statements"), read("large_load_waits"), publisher_verdicts(), today)
        n = summary(public, verdicts, s)
        public, verdicts = public.assign(retrieved_at=retrieved)[PUBLIC_COLS], verdicts.assign(retrieved_at=retrieved)[VERDICT_COLS]
        common = [f"Retrieved: {run_id} (UTC) by warehouse/derived/large_load_public.py; no request to anyone",
                  f"Run log: warehouse/output/logs/{PUBLIC}_{run_id}.log"]
        head_v = [
            "Energy Research Warehouse (ERW): a license verdict for each source document behind large_load_statements and large_load_waits (session 255)",
            "Shape: events (docs/datastandard.md v0), event_type license_verdict; one row a document. source_url: the document's address. parties: the regulator, the publisher session 205 "
            "read, or the host. status: the verdict (public; needs written permission; not settled; not public). document_class and verdict_basis say why. rows: the table's rows that "
            "rest on the document; rows_public: those that are in large_load_public. event_date: the day of the verdict.",
            f"The rule: a public regulatory filing and an SEC filing state facts that may be republished as facts with a link; long quotation may not (the owner's, session 255). "
            f"This run: {n['documents']} documents of large_load_statements ({json.dumps(n['documents_by_verdict'])}) and {n['documents_of_waits']} of large_load_waits, none of them public.",
            *common,
            f"Source: {SOURCE_VERDICTS} ERW derived table, docs/methods/large_load_public.md, {METHOD_URL}",
            "Derived from: large_load_statements; large_load_waits",
            "License: internal. It lists the documents of two internal tables, 48 of them at addresses that hold a filer's e-mail address. Not on the site, not in a public Redivis dataset, not in the live set.",
        ]
        head_p = [
            "Energy Research Warehouse (ERW): the large-load statements whose source document is public, as facts with a link and no quoted text (session 255)",
            "Shape: events (docs/datastandard.md v0), event_type large_load_statement; one row a figure a public document states. parties: the entity. mw (row_kind mw; a range in mw_low "
            "and mw_high) or duration_as_stated (row_kind wait: the figure as written, a number and its unit). status and stage_class: the ERW's class of the stage, one of five, or not "
            "classed; not the document's words. source_url, document_title, page: where it stands. public_basis: SEC filing, public regulatory filing, or publisher's terms read in "
            "session 205. statement_id: the row of large_load_statements it comes from.",
            "NO QUOTED TEXT: no sentence of a document, and neither the stage nor the kind of load in the document's own words. A row whose address holds a filer's e-mail address is not here.",
            "DO NOT SUM across rows or entities: the entities count differently (requests, studies, letters, contracts, forecasts), a document often states a total and its parts, two "
            "documents may state one quantity, and an operator's figures hold its utilities'. wait_counted says no where a duration is not a load's wait; load_scope says where a figure "
            "covers every distribution project.",
            f"This run: {n['public_rows']} of {n['statements']} statements ({n['public_by_kind'].get('mw', 0)} of megawatts, {n['public_by_kind'].get('wait', 0)} of a duration), from "
            f"{n['public_documents']} documents, {n['public_entities']} entities in {n['public_groups']} groups; by basis {json.dumps(n['public_by_basis'])}. "
            f"{n['held_out_for_an_email_address']} more rest on a public document at an address that holds an e-mail address and are held out.",
            *common,
            f"Source: {SOURCE_PUBLIC} ERW derived table, docs/methods/large_load_public.md, {METHOD_URL}; each row's source_url is the regulator's, the SEC's or the publisher's own copy of the document",
            "Derived from: large_load_statements",
            "License: internal until the owner rules (session 255's prompt). Built so that it can be made public: facts with a link, no quotation. Not on the site, not in a public Redivis dataset, not in the live set.",
        ]
        for name, frame, head, cols in ((VERDICTS, verdicts, head_v, VERDICT_COLS), (PUBLIC, public, head_p, PUBLIC_COLS)):
            path = os.path.join(ip.OUT_DIR, name + ".csv")
            if os.path.exists(path):
                os.remove(path)  # rebuilt whole from its inputs each run
            ip.write_csv(frame, name, head, log, cols=cols, key=["event_id"], time_col="event_date")
        ip.update_sources([
            dict(source=SOURCE_PUBLIC, publisher="Energy Research Warehouse (ERW), derived", report="The large-load statements whose source document is public, as facts with a link (warehouse/derived/large_load_public.py)",
                 report_url=METHOD_URL, document_list="", license="internal", tables=[PUBLIC]),
            dict(source=SOURCE_VERDICTS, publisher="Energy Research Warehouse (ERW), derived", report="A license verdict for each source document of the large-load tables (warehouse/derived/large_load_public.py)",
                 report_url=METHOD_URL, document_list="", license="internal", tables=[VERDICTS])])
        msg = (f"{len(verdicts)} documents with a verdict; {len(public)} of {n['statements']} statements public ({n['public_entities']} entities), "
               f"{n['held_out_for_an_email_address']} held out for an e-mail address in the address")
        log(msg)
        print(f"{PUBLIC}: {msg}")
        results += [dict(table=PUBLIC, market="all", status="ok", detail=msg), dict(table=VERDICTS, market="all", status="ok", detail=msg)]
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED:\n{tb}")
        print(f"{PUBLIC} FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=PUBLIC, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    ip.write_status(PUBLIC, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
