#!/usr/bin/env python3
"""Proceedings and orders on large loads at FERC and ten state commissions, each with its exact sentence (session 154).

Energy Research Warehouse (ERW). Writes warehouse/output/large_load_rules.csv (events shape): one row a proceeding
(the docket itself: its opening order, notice or petition is the document) and one row for each order in it, on four
topics: large-load interconnection, large-load tariffs, transmission cost allocation and interconnection reform. The
regulators: the Federal Energy Regulatory Commission and the utility commissions of Texas, Virginia, Ohio, Georgia,
Indiana, Arizona, Pennsylvania, Illinois, Oregon and California. Federal regulators and state commissions only:
nothing municipal (permitting, zoning, a local hearing) is recorded.

What it is made from. On 8 October 2026 (UTC) three research passes, each an AI research agent, read the regulators'
public dockets (the owner's approved pull: USD 0, a ceiling of 20,000 rows) and wrote, under
warehouse/raw/large_load_rules/A, B and C (not in git): actions.csv (the rows), rejects.csv, documents.csv (every
document opened), requests.csv (every request), notes.md (what each docket system gives and refuses, and each
regulator's terms quoted) and the documents as downloaded with their extracted text.

What this script does. It makes no request and no model call. It reads the passes' rows and proves each again by its
own code before it is taken:
    - the sentence, white space normalized, is a literal substring of the text of the saved document;
    - for a PDF, the page is found here (the first page of the saved text that holds the sentence, or the page where
      it begins when it runs over a page break), and that page is what the table holds;
    - the row holds what a row must: a regulator of the eleven, a docket number, a document date that is a real date,
      a kind (proceeding or order), a topic of the four, a status class of the four, an http address on a regulator's
      or grid operator's own host.
A row that does not prove or fails a check is left out and listed with its reason (large_load_rules_not_taken.csv,
beside the table in a trial, beside the passes' files otherwise). Nothing is filled: a field the document does not
state is empty. status_as_worded is the regulator's own wording where its page or the document states one;
status_class (open, decided, closed, not stated) is the collecting pass's reading of it and always stands beside
those words, never in place of them.

Never taken: an address on misoenergy.org (MISO is paused) or on PJM's Data Miner or API; an address that holds a
filer's e-mail address (the owner has not ruled on such addresses); a document on a host that is not a regulator's or
a grid operator's (a news article, a law firm's note and a search summary are never the source of a row); a row whose
title or sentence is about municipal permitting, zoning or a local hearing.

License, by regulator (warehouse/config/large_load_rule_terms.json holds the sentence that decides each, word for
word as its pass saved it). A table has one license, so the rows are written to two tables, as session 140 wrote
ISO-NE's zone prices beside the public ones:
    large_load_rules            public: the regulators whose own quoted terms allow reuse (class "allowed") or are a
                                statement about public records (class "public record": about access, not reuse; flagged
                                for the owner);
    large_load_rules_internal   internal: the regulators whose terms restrict copying (class "restricted") or whose
                                terms no pass read (class "not quoted"). A page may show such a row's facts (date,
                                regulator, docket number, status class, topic, the link) and a model's read of it, never
                                its sentence or its worded status.

Three columns say what a row rests on. sentence_from: what the sentence is cut from (order text, docket card, meeting
minutes, meeting agenda, list of suspended cases, news release, docket page, draft resolution ...), by SENTENCE_FROM.
sentence_kind: "document" (the document's own text) or "record" (the regulator's own summary or record of it), counted
apart: Ohio's document viewer answers with a reCAPTCHA and Illinois's docket pages with a robot check, so those rows
are cut from the docket card and from the commission's minutes, agendas and suspension list; Arizona's decisions are
scans, so its rows are cut from the commission's own releases and docket record. row_flag: a docket number that is not
in the row's own document (kept where the commission's agenda or other minutes tie it; left out where only a match of
company, subject and date does: DOCKET_NOT_TIED); a single-customer contract (SINGLE_CUSTOMER); a draft (a California
draft resolution as posted for the agenda: its status class is "not stated" here, since no adopted text was read).

    python warehouse/connectors/large_load_rules.py                              # writes the table: needs the data lock
    python warehouse/connectors/large_load_rules.py --out-dir DIR                # a trial run: the table under DIR
    python warehouse/connectors/large_load_rules.py --out-dir DIR --raw-root RAW # the passes' folders under RAW
"""

import argparse
import csv
import datetime as dt
import hashlib
import html as H
import json
import os
import re
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import iso_prices as ip  # noqa: E402

NAME = "large_load_rules"
SOURCE = "erw:large_load_rules"
# The rows of a regulator whose own terms do not allow reuse, or whose terms no pass quoted, are held in a table of
# their own, internal, as session 140 held ISO-NE's zone prices beside the public ones: a table has one license.
NAME_HELD = "large_load_rules_internal"
SOURCE_HELD = "erw:large_load_rules_internal"
RAW = os.path.join(ROOT, "warehouse", "raw", "large_load_rules")
TERMS_FILE = os.path.join(ROOT, "warehouse", "config", "large_load_rule_terms.json")
METHOD = "docs/methods/datacenter_cost.md"
METHOD_URL = "https://github.com/SamuelEnrique/erw/blob/main/" + METHOD
PASSES = ["A", "B", "C"]
ROW_CEILING = 20000   # the owner's ceiling for the session's pull
PASS_COLS = ["regulator", "jurisdiction", "state", "grids", "docket_number", "proceeding_title", "row_kind", "topic",
             "document_title", "document_date", "status_as_worded", "status_class", "document_url", "docket_url", "page",
             "sentence", "local_file", "retrieved_at", "verified", "notes", "terms_url"]
EVENTS = ["event_id", "event_date", "event_type", "parties", "entity_ids", "mw", "price", "currency", "status", "source",
          "source_url"]
EXTRA = ["regulator", "jurisdiction", "state", "grids", "docket_number", "proceeding_title", "row_kind", "topic",
         "document_title", "status_as_worded", "status_class", "docket_url", "page", "sentence", "sentence_from",
         "sentence_kind", "row_flag", "text_file", "text_sha256", "proved_how", "collected_in", "notes", "terms_url",
         "retrieved_at"]
COLS = EVENTS + EXTRA
# What a sentence is cut from, by the saved file's name and the document's title, first match (session 154: twenty rows
# of pass B and several of pass C do not rest on an order's own text, because the documents sit behind a robot check or
# are scans). sentence_kind counts the two kinds apart: "document" (the document's own text) and "record" (the
# regulator's own summary or record of it: a docket card or page, minutes, an agenda, a list, a news release).
SENTENCE_FROM = [
    (r"/oh/card_", "", "docket card", "record"),
    (r"il_minutes", "", "meeting minutes", "record"),
    (r"il_agendas", "", "meeting agenda", "record"),
    (r"il/suspension", "", "list of suspended cases", "record"),
    (r"in_hearings", "", "hearings list", "record"),
    (r"az_news", "", "news release", "record"),
    (r"az_api_docket|_docket\.html|ca_proc_", "", "docket page", "record"),
    ("", r"^draft resolution", "draft resolution", "document"),
    ("", r"regulatory agenda", "regulatory agenda", "record"),
    ("", r"^notice of|^secretarial letter", "notice or letter", "document"),
    ("", r"^application|^request for approval|^control number request", "application or request", "document"),
    ("", r"^staff memo", "staff memo", "document"),
    ("", r"^proposal for publication", "proposed rule", "document"),
    ("", r"^motion of", "commissioner's motion", "document"),
    ("", r"ruling", "judge's ruling", "document"),
    ("", r"order|decision|opinion|resolution", "order text", "document"),
]
# Single-customer contracts and agreements placed under a topic as the nearest fit (the passes' notes say so): kept,
# flagged, and never among the ten rules of the month unless the order sets a rule for others too (none listed does).
SINGLE_CUSTOMER = {
    "Indiana Utility Regulatory Commission": ["46183", "46322", "46362", "46393", "46394", "46442"],   # pass B, notes point 9
    "California Public Utilities Commission": ["Resolution E-5420", "Resolution E-5439", "Resolution E-5433", "Resolution E-5455"],
    "Arizona Corporation Commission": ["E-01933A-25-0187"],   # one utility's supply agreement with one customer
}
# A row whose docket number the pass could tie to its document only by matching company, subject and date across two
# of the commission's lists, not by the regulator's own words: left out (session 154, the coordinator's ruling).
DOCKET_NOT_TIED = [("Illinois Commerce Commission", "26-0625", "order")]
FLAG_DOCKET = "docket number not in the row's own document (tied by another document of the commission: see notes)"
FLAG_SINGLE = "single-customer contract or agreement, not a rule for others"
FLAG_DRAFT = "draft as posted for the agenda: no adopted text was read"
# The eleven regulators: the words a pass may name each by, its two-letter state and the id's first part.
REGULATORS = {
    "ferc": ("Federal Energy Regulatory Commission", "", ["federal energy regulatory commission", "ferc"]),
    "txpuc": ("Public Utility Commission of Texas", "TX", ["public utility commission of texas", "puct"]),
    "vascc": ("Virginia State Corporation Commission", "VA", ["virginia state corporation commission", "state corporation commission"]),
    "puco": ("Public Utilities Commission of Ohio", "OH", ["public utilities commission of ohio", "puco"]),
    "gapsc": ("Georgia Public Service Commission", "GA", ["georgia public service commission"]),
    "iurc": ("Indiana Utility Regulatory Commission", "IN", ["indiana utility regulatory commission", "iurc"]),
    "azcc": ("Arizona Corporation Commission", "AZ", ["arizona corporation commission"]),
    "papuc": ("Pennsylvania Public Utility Commission", "PA", ["pennsylvania public utility commission"]),
    "ilcc": ("Illinois Commerce Commission", "IL", ["illinois commerce commission"]),
    "orpuc": ("Oregon Public Utility Commission", "OR", ["oregon public utility commission", "public utility commission of oregon"]),
    "cpuc": ("California Public Utilities Commission", "CA", ["california public utilities commission", "cpuc"]),
}
TOPICS = ["large-load interconnection", "large-load tariff", "transmission cost allocation", "interconnection reform"]
KINDS = ["proceeding", "order"]
CLASSES = ["open", "decided", "closed", "not stated"]
GRID_WORDS = ["ERCOT", "PJM", "CAISO", "NYISO", "ISO-NE", "SPP", "MISO"]
# A grid operator's own host may hold a regulator's filing (PJM's public committee documents). Never MISO's.
OPERATOR_HOSTS = ["pjm.com", "ercot.com", "caiso.com", "spp.org", "nyiso.com", "iso-ne.com"]
REFUSED_HOSTS = ["misoenergy.org", "dataminer2.pjm.com", "dataminer.pjm.com", "api.pjm.com"]
# Municipal permitting, zoning and local hearings are out of scope (session 154): a row about one is not taken.
MUNICIPAL = ["zoning", "rezoning", "city council", "county board", "county commission", "board of supervisors",
             "planning commission", "town board", "building permit", "conditional use permit", "special use permit",
             "local hearing"]
EMAIL_IN_URL = re.compile(r"[\w.+-]+(?:%40|@)[\w-]+(?:\.[\w-]+)+", re.I)
FF = chr(12)
DASH = chr(0x2014)


def norm(s):
    return " ".join(str(s).split())


def host_of(url):
    m = re.match(r"^https?://([^/:]+)", url or "", flags=re.I)
    return m.group(1).lower() if m else ""


def regulator_key(name):
    n = norm(name).lower()
    for k, (_, _, words) in REGULATORS.items():
        if any(n == w or n.startswith(w) or w in n for w in words if len(w) > 5) or n in words:
            return k
    return None


def host_allowed(host):
    """A regulator's own host (a government address) or a grid operator's; never a refused one."""
    if any(host == h or host.endswith("." + h) for h in REFUSED_HOSTS):
        return False
    if host.endswith(".gov") or host.endswith(".us"):
        return True
    return any(host == h or host.endswith("." + h) for h in OPERATOR_HOSTS)


def read_pass(letter, base):
    path = os.path.join(base, letter, "actions.csv")
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        for c in PASS_COLS:
            r[c] = (r.get(c) or "").strip()
        r["collected_in"] = f"pass {letter}"
    return rows


def html_text(s):
    s = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", s)
    return H.unescape(re.sub(r"<[^>]+>", " ", s))


def texts_of(base, letter, row):
    """The saved text files of a row's document: the local file itself when it is text; the files under the pass's
    text/ whose name is the local file's (folders joined by two underscores, as the passes save them) with .txt; the
    files the row's notes name."""
    pdir = os.path.join(base, letter)
    tdir = os.path.join(pdir, "text")
    lf = row.get("local_file", "").replace("\\", "/")
    out = []

    def add(p):
        if p and os.path.isfile(p) and p not in out:
            out.append(p)

    rel = lf
    m = re.search(r"(?:^|/)large_load_rules/%s/(.+)$" % re.escape(letter), lf)
    if m:
        rel = m.group(1)
    elif os.path.isabs(lf) and os.path.isfile(lf):
        rel = os.path.relpath(lf, pdir).replace("\\", "/")
    rel = rel.lstrip("./")
    if rel.startswith("text/"):
        add(os.path.join(pdir, rel))
    inner = re.sub(r"^(raw|text)/", "", rel)
    stem = inner.replace("/", "__")
    if os.path.isdir(tdir) and stem:
        for n in sorted(os.listdir(tdir)):
            if n == stem or n == stem + ".txt" or (n.startswith(stem + ".") and n.endswith(".txt")):
                add(os.path.join(tdir, n))
        base_name = os.path.basename(inner)
        for n in sorted(os.listdir(tdir)):
            if n in (base_name, base_name + ".txt") or n.endswith("__" + base_name + ".txt") or n.endswith("__" + base_name):
                add(os.path.join(tdir, n))
    for m in re.finditer(r"text/([^\s();,]+)", row.get("notes", "")):
        add(os.path.join(tdir, m.group(1).rstrip(".")))
    return out, os.path.join(pdir, rel) if rel else ""


def load_text(path, cache):
    if path not in cache:
        with open(path, encoding="utf-8", errors="replace") as f:
            raw = f.read()
        if re.search(r"(?i)<html|<body|<div", raw[:4000]):
            raw = html_text(raw)
        pages = raw.split(FF) if FF in raw else None
        cache[path] = (norm(raw), [norm(p) for p in pages] if pages else None,
                       hashlib.sha256(raw.encode("utf-8", "replace")).hexdigest())
    return cache[path]


def page_of(sent, whole, pages):
    """The 1-based page of the saved text that holds the sentence: the first page it stands on whole, or the page
    where it begins when it runs over a page break. None when the text has no pages."""
    if not pages:
        return None
    for i, p in enumerate(pages, 1):
        if sent in p:
            return i
    at = whole.find(sent)
    if at < 0:
        return None
    run = 0
    for i, p in enumerate(pages, 1):
        run += len(p) + (1 if p else 0)
        if at < run:
            return i
    return len(pages)


def proved(row, base, letter, cache):
    """(reasons it does not prove, [] when it does; page found here or ''; the text file; its hash; how)."""
    sent = norm(row.get("sentence", ""))
    if not sent:
        return ["no sentence"], "", "", "", ""
    files, raw_path = texts_of(base, letter, row)
    if not files:
        return ["no saved text for the row's document (%s)" % (row.get("local_file") or "no local file")], "", "", "", ""
    for path in files:
        whole, pages, sha = load_text(path, cache)
        if sent in whole:
            pg = page_of(sent, whole, pages)
            is_pdf = ".pdf" in os.path.basename(path).lower() or row.get("document_url", "").lower().split("?")[0].endswith(".pdf")
            if is_pdf and pages is None and row.get("page", "").strip():
                how = "the saved text holds the sentence; the text has no page breaks, so the pass's page is kept"
                return [], row["page"].strip(), path, sha, how
            how = "the saved text holds the sentence" + ("; page found here" if pg else "")
            if pg and row.get("page", "").strip().isdigit() and int(row["page"]) != pg:
                how += " (the pass wrote page %s)" % row["page"].strip()
            return [], str(pg or ""), path, sha, how
    return ["the sentence is not a literal substring of the saved text"], "", "", "", ""


def real_date(s):
    try:
        return dt.date.fromisoformat(s).isoformat() == s
    except ValueError:
        return False


def row_check(r):
    """The reasons a row does not hold what a row must; [] when it does."""
    why = []
    if r["verified"].lower() != "yes":
        why.append("not marked verified by its pass")
    key = regulator_key(r["regulator"])
    if not key:
        why.append("the regulator is not one of the eleven (federal regulators and state commissions only)")
    else:
        want_j = "federal" if key == "ferc" else "state"
        if r["jurisdiction"] != want_j:
            why.append(f"jurisdiction {r['jurisdiction']!r} does not fit the regulator")
        if r["state"] != REGULATORS[key][1]:
            why.append(f"state {r['state']!r} does not fit the regulator")
    if not r["docket_number"]:
        why.append("no docket number")
    if r["row_kind"] not in KINDS:
        why.append(f"row_kind {r['row_kind']!r}")
    topics = [t.strip() for t in r["topic"].split(";") if t.strip()]
    if not topics or any(t not in TOPICS for t in topics):
        why.append(f"topic {r['topic']!r} is not of the four")
    if r["status_class"] not in CLASSES:
        why.append(f"status_class {r['status_class']!r}")
    if not real_date(r["document_date"]):
        why.append(f"no document date that is a real date ({r['document_date']!r})")
    elif r["document_date"] > dt.datetime.now(dt.timezone.utc).date().isoformat():
        why.append("a document date in the future")
    url = r["document_url"]
    host = host_of(url)
    if not host:
        why.append("no http address")
    else:
        if any(host == h or host.endswith("." + h) for h in REFUSED_HOSTS):
            why.append("an address this project never requests (MISO, or PJM's Data Miner or API)")
        elif not host_allowed(host):
            why.append(f"the document's host ({host}) is not a regulator's or a grid operator's")
        if EMAIL_IN_URL.search(url):
            why.append("address holds a filer's e-mail address: not requested")
    if r["docket_url"] and EMAIL_IN_URL.search(r["docket_url"]):
        why.append("the docket address holds an e-mail address")
    text = (r["proceeding_title"] + " " + r["document_title"] + " " + r["sentence"]).lower()
    hit = [w for w in MUNICIPAL if w in text]
    if hit:
        why.append("municipal (%s): out of scope" % ", ".join(hit))
    if DASH in r["sentence"]:
        pass  # a document's own em dash is the document's; the sentence is kept as written
    bad = [g for g in (x.strip() for x in r["grids"].split(";")) if g and g not in GRID_WORDS]
    if bad:
        why.append(f"grids names {bad}, not a grid operator")
    return why


def sentence_from(r):
    """(what the sentence is cut from, its kind) by SENTENCE_FROM."""
    lf = r.get("local_file", "").replace("\\", "/").lower()
    title = norm(r.get("document_title", "")).lower()
    for file_pat, title_pat, words, kind in SENTENCE_FROM:
        if file_pat and re.search(file_pat, lf):
            return words, kind
        if title_pat and re.search(title_pat, title):
            return words, kind
    return "document text", "document"


def flags_of(r, name):
    """The flags of a row, by rule: its docket number is not in its own document (a pass B row whose notes do not
    say 'docket number in the document'); a single-customer contract (SINGLE_CUSTOMER); a draft."""
    out = []
    if r["collected_in"] == "pass B" and "docket number in the document" not in r["notes"]:
        out.append(FLAG_DOCKET)
    if any(r["docket_number"].startswith(d) for d in SINGLE_CUSTOMER.get(name, [])):
        out.append(FLAG_SINGLE)
    if norm(r["document_title"]).lower().startswith("draft") or norm(r["status_as_worded"]).upper() == "DRAFT":
        out.append(FLAG_DRAFT)
    return out


def event_id(key, r):
    h = hashlib.sha1((r["document_url"] + "|" + norm(r["sentence"])).encode("utf-8")).hexdigest()[:10]
    d = re.sub(r"[^A-Za-z0-9.-]+", "-", r["docket_number"]).strip("-")
    return f"{key}:{d}:{r['row_kind']}:{h}"


def to_row(r, page, text_file, sha, how, raw_root):
    key = regulator_key(r["regulator"])
    name = REGULATORS[key][0]
    rel = os.path.relpath(text_file, os.path.dirname(raw_root)).replace("\\", "/")
    cut, kind = sentence_from(r)
    flags = flags_of(r, name)
    notes = norm(r["notes"])
    if FLAG_DRAFT in flags and r["status_class"] != "not stated":
        # a draft's adoption rests on no adopted text: the class is not stated, and the pass's reading stays in notes
        notes += f" [status class {r['status_class']} by the pass, on another draft's word; set to not stated here: no adopted text was read]"
        r = dict(r, status_class="not stated")
    return {
        "event_id": event_id(key, r), "event_date": r["document_date"],
        "event_type": "regulatory_" + r["row_kind"], "parties": name, "entity_ids": "", "mw": "", "price": "",
        "currency": "", "status": r["status_class"], "source": f"{key}:dockets", "source_url": r["document_url"],
        "regulator": name, "jurisdiction": r["jurisdiction"], "state": r["state"],
        "grids": ";".join(x.strip() for x in r["grids"].split(";") if x.strip()),
        "docket_number": r["docket_number"], "proceeding_title": norm(r["proceeding_title"]), "row_kind": r["row_kind"],
        "topic": ";".join(t.strip() for t in r["topic"].split(";") if t.strip()),
        "document_title": norm(r["document_title"]), "status_as_worded": norm(r["status_as_worded"]),
        "status_class": r["status_class"], "docket_url": r["docket_url"], "page": page, "sentence": norm(r["sentence"]),
        "sentence_from": cut, "sentence_kind": kind, "row_flag": "; ".join(flags),
        "text_file": "warehouse/raw/" + rel, "text_sha256": sha, "proved_how": how, "collected_in": r["collected_in"],
        "notes": notes, "terms_url": r["terms_url"], "retrieved_at": r["retrieved_at"],
    }


def pass_counts(base, letter):
    """Requests and bytes of a pass from its requests.csv (every request it made), and its rows collected."""
    path = os.path.join(base, letter, "requests.csv")
    n = b = 0
    if os.path.exists(path):
        with open(path, encoding="utf-8-sig", newline="") as f:
            for r in csv.DictReader(f):
                n += 1
                v = (r.get("bytes") or "").strip()
                b += int(v) if v.isdigit() else 0
    return n, b


def load_terms(path=TERMS_FILE):
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        return {t["regulator"]: t for t in json.load(f)["regulators"]}


PUBLIC_CLASSES = ("allowed", "public record")
HELD_CLASSES = ("restricted", "not quoted")


def class_of(regulator, terms):
    """The class of a regulator's terms (large_load_rule_terms.json): allowed, public record, restricted or not
    quoted. A regulator the file does not name, or one whose class needs a quotation and has none, is not quoted."""
    t = terms.get(regulator) or {}
    c = t.get("class", "not quoted")
    if c in ("allowed", "public record", "restricted") and not t.get("terms_quote"):
        return "not quoted"
    return c if c in PUBLIC_CLASSES + HELD_CLASSES else "not quoted"


def license_of(regulators, terms):
    """({regulator: 'public' or 'internal'}, {regulator: its class}): a regulator's rows are public only if its own
    quoted terms allow reuse or are a public-records statement; a regulator whose terms restrict copying, or whose
    terms no pass quoted, has its rows in the internal table."""
    classes = {r: class_of(r, terms) for r in sorted(regulators)}
    return {r: ("public" if c in PUBLIC_CLASSES else "internal") for r, c in classes.items()}, classes


def build(base, log):
    read, absent, collected, left, taken = [], [], [], [], {}
    cache = {}
    for letter in PASSES:
        rows = read_pass(letter, base)
        if rows is None:
            absent.append(letter)
            continue
        read.append(letter)
        collected += rows
        for r in rows:
            why = row_check(r)
            key = regulator_key(r["regulator"])
            if key and (REGULATORS[key][0], r["docket_number"], r["row_kind"]) in DOCKET_NOT_TIED and "docket number in the document" not in r["notes"]:
                why.append("its docket number is tied to its document only by matching company, subject and date across two "
                           "lists, not by the regulator's own words")
            page = text_file = sha = how = ""
            if not why:
                why, page, text_file, sha, how = proved(r, base, letter, cache)
            if why:
                left.append(dict(r, why_not_taken="; ".join(why)))
                continue
            row = to_row(r, page, text_file, sha, how, base)
            if row["event_id"] in taken:
                left.append(dict(r, why_not_taken=f"the same document and sentence as a row already taken ({taken[row['event_id']]['collected_in']})"))
                continue
            taken[row["event_id"]] = row
    if len(taken) > ROW_CEILING:
        raise RuntimeError(f"{len(taken)} rows: over the ceiling of {ROW_CEILING}")
    out = pd.DataFrame(list(taken.values()), columns=COLS)
    if len(out):
        out = out.sort_values(["event_date", "event_id"], ascending=[False, True]).reset_index(drop=True)
    log(f"  passes read: {' '.join(read) or 'none'}; not there: {' '.join(absent) or 'none'}")
    log(f"  collected {len(collected)}, taken {len(out)}, not taken {len(left)}")
    return dict(out=out, left=left, read=read, absent=absent, collected=collected)


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW: proceedings and orders on large loads, each with its sentence")
    ap.add_argument("--out-dir", help="a trial run: the table and its log under this directory; nothing in warehouse/output")
    ap.add_argument("--raw-root", help="the directory that holds the passes' folders A, B and C (default: this copy's warehouse/raw/large_load_rules)")
    a = ap.parse_args(argv)
    base = os.path.abspath(a.raw_root) if a.raw_root else RAW
    run_id = pd.Timestamp.now(tz="UTC").strftime("%Y%m%dT%H%M%SZ")
    if a.out_dir:
        os.makedirs(a.out_dir, exist_ok=True)
        ip.set_out_dir(a.out_dir)
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{NAME}_{run_id}.log"))
    b = build(base, log)
    out, left = b["out"], b["left"]
    beside = a.out_dir or base
    with open(os.path.join(beside, f"{NAME}_not_taken.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=PASS_COLS + ["collected_in", "why_not_taken"], lineterminator="\n", extrasaction="ignore")
        w.writeheader()
        w.writerows(left)
    if not len(out):
        log("no row taken: no table is written")
        print(f"{NAME}: passes read {b['read']}, collected {len(b['collected'])}, taken 0: no table is written")
        log.close()
        return 1
    terms = load_terms()
    lic, classes = license_of(set(out["regulator"]), terms)
    counts = {p: pass_counts(base, p) for p in PASSES}
    reqs, byts = sum(v[0] for v in counts.values()), sum(v[1] for v in counts.values())
    by_kind_all = out.groupby("sentence_kind").size().to_dict()
    parts = {NAME: out[out["regulator"].map(lic) == "public"], NAME_HELD: out[out["regulator"].map(lic) == "internal"]}
    summary = []
    for name, part in parts.items():
        public = name == NAME
        source = SOURCE if public else SOURCE_HELD
        path = os.path.join(ip.OUT_DIR, name + ".csv")
        if not len(part):
            if os.path.exists(path):
                raise RuntimeError(f"{name} would be empty and a file of it exists: not replaced by nothing; a person removes it")
            summary.append(f"{name}: no row")
            continue
        part = part.reset_index(drop=True)
        regs = sorted(set(part["regulator"]))
        by_reg = part.groupby("regulator").size().to_dict()
        by_kind = part.groupby("row_kind").size().to_dict()
        by_class = part.groupby("status_class").size().to_dict()
        by_cut = part.groupby("sentence_from").size().to_dict()
        other = NAME_HELD if public else NAME
        if public:
            lic_line = ("License: public. This table holds only the rows of regulators whose own quoted terms allow reuse or are a "
                        "public-records statement (" + "; ".join(f"{r}: {classes[r]}" for r in regs) + "); each sentence that decided it is quoted "
                        "word for word in warehouse/config/large_load_rule_terms.json and in " + METHOD + ". A public-records statement is "
                        "about access, not reuse: a decision for the owner to confirm.")
        else:
            lic_line = ("License: internal. These regulators' own terms restrict copying, or no terms of theirs were read ("
                        + "; ".join(f"{r}: {classes[r]}" for r in regs) + "; warehouse/config/large_load_rule_terms.json). Not in the public "
                        "Redivis dataset and not in the live set. A page may show a row's facts (date, regulator, docket number, status "
                        "class, topic, the link) and a model's read of it, never the sentence or the worded status.")
        header = [
            "Energy Research Warehouse (ERW): proceedings and orders on large-load interconnection, large-load tariffs, "
            "transmission cost allocation and interconnection reform at FERC and ten state utility commissions, each with "
            "the exact sentence that states what it does (session 154): " + ("the rows of the regulators whose terms allow "
            "their text to be shown" if public else "the rows of the regulators whose terms restrict copying or were not read") +
            f". The other rows are in {other}: one table, one license.",
            "Shape: events (docs/datastandard.md v0), event_type regulatory_proceeding (the docket itself: its opening order, "
            "notice or petition is the document) or regulatory_order (an order, rule or decision in it). event_date is the "
            "date on the document. status is the status class; status_as_worded is the regulator's own wording where its "
            "page or the document states one, else empty.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/large_load_rules.py from the research passes of 8 October 2026 "
            f"(warehouse/raw/large_load_rules/A, B and C, not in git; read in this run: {' '.join(b['read']) or 'none'}; not there: "
            f"{' '.join(b['absent']) or 'none'}): the rows, the rejects, every document opened, every request, the notes, the "
            "documents as downloaded and their extracted text",
            f"Run log: warehouse/output/logs/{NAME}_{run_id}.log",
            f"Source: {source}: each row's source_url is the regulator's own document (source names the regulator's dockets); "
            "docket_url is the docket's own page where one answers a plain request. Method: " + METHOD + ".",
            f"This run, both tables: {len(b['collected'])} rows collected by the passes, {len(out)} taken, {len(left)} not taken "
            f"({NAME}_not_taken.csv, each with its reason). This table: {len(part)} rows ({by_kind}). By regulator: {by_reg}. By "
            f"status class: {by_class}.",
            f"What a sentence is cut from (sentence_from): {by_cut}. sentence_kind counts two kinds apart: document (the "
            "document's own text) and record (the regulator's own summary or record of it: a docket card or page, meeting "
            "minutes, an agenda, a list, a news release), where the document sits behind a robot check or is a scan. row_flag: "
            "a docket number that is not in the row's own document; a single-customer contract; a draft.",
            f"The pull against its ceiling of {ROW_CEILING} rows: rows collected {len(b['collected'])}; requests {reqs} and bytes {byts} "
            "by the passes' own requests.csv (" + "; ".join(f"{p}: {v[0]} requests, {v[1]} bytes" for p, v in counts.items()) + ").",
            "Every sentence is a literal substring of the saved document's text (white space normalized), proved again by this "
            "script; page is the PDF page found here. Nothing is filled: a field a document does not state is empty. "
            "status_class and topic are the collecting pass's reading, beside the regulator's words, not a person's review.",
            "Not legal advice and not complete: a docket system cannot be proved complete from outside. Federal regulators "
            "and state commissions only: nothing municipal (permitting, zoning, local hearings) is recorded.",
            lic_line,
        ]
        ip.write_snapshot(part, name, header, lambda m: log(m.strip()), COLS)
        ip.update_sources([{"source": source, "publisher": "Energy Research Warehouse (ERW), collected from the public dockets of FERC and ten state "
                            "utility commissions by an AI research agent, each sentence proved by code",
                            "report": "Proceedings and orders on large loads, 8 October 2026 (docs/accelerator/rules_in_motion.md): "
                                      + ("the regulators whose terms allow their text to be shown: " if public else
                                         "the regulators whose terms restrict copying or were not read: ") + "; ".join(regs),
                            "report_url": METHOD_URL, "document_list": "", "license": "public" if public else "internal", "tables": [name]}])
        summary.append(f"{name}: {len(part)} rows, {by_reg}; kinds {by_kind}; status classes {by_class}")
    detail = (f"passes {' '.join(b['read'])}; collected {len(b['collected'])}, taken {len(out)} ({len(parts[NAME])} public, "
              f"{len(parts[NAME_HELD])} internal), not taken {len(left)}; sentences cut from {by_kind_all}; requests {reqs}, bytes {byts}")
    ip.write_status(NAME, run_id, [dict(table=NAME, market="all", status="ok", detail=detail)])
    log(detail)
    print(f"{NAME}: {detail}")
    for ln in summary:
        print("  " + ln)
        log("  " + ln)
    print("  terms classes: " + "; ".join(f"{r}: {c}" for r, c in classes.items()))
    print("  flags: " + str(out["row_flag"].replace("", "none").str.split("; ").explode().value_counts().to_dict()))
    print("  sentence_from: " + str(out.groupby(["sentence_kind", "sentence_from"]).size().to_dict()))
    log.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
