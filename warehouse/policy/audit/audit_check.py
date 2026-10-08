#!/usr/bin/env python3
"""Session 154: check each sampled policy action's extracted fields against its saved source document, by code.

Energy Research Warehouse (ERW). Reads the table rows (--in-dir), the sample and the documents audit_fetch.py saved, and
writes, under --out:

  auto_checks.csv   one line per (event_id, field) of the extracted fields, with a class and both values:
                    correct, wrong (the source states another value), missing (the source states it, the row is
                    empty), not_in_source (the row holds a value the source does not state), source_silent (neither
                    holds it), not_reachable (no document)
  dossier.md        each row beside the head of its document, for the fields that are a judgment (read by a person)

A Federal Register row is checked against two things the Register publishes for the same document number: the API
record (the fields the connector reads) and the printed document's own text (its heading, bracketed docket lines, RIN
line, title, ACTION and SUMMARY). Where the two disagree the printed document governs and the line says so.
No table is written and no request is made here.

    python warehouse/policy/audit/audit_check.py --in-dir C:/Users/lossa/Documents/erw/warehouse/output --out <audit>
"""

import argparse
import csv
import html as H
import io
import json
import os
import re
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "connectors")))

MONTHS = {m: i for i, m in enumerate(["January", "February", "March", "April", "May", "June", "July", "August",
                                      "September", "October", "November", "December"], 1)}
SECTION = {"Notices": "notice", "Rules and Regulations": "rule", "Proposed Rules": "proposed_rule"}
AGENCY_TEXT = [("FERC", "federal energy regulatory commission"), ("NRC", "nuclear regulatory commission"),
               ("BLM", "bureau of land management"), ("EPA", "environmental protection agency"),
               ("DOE", "department of energy"), ("Interior", "department of the interior")]


def read_events(path):
    with open(path, encoding="utf-8") as f:
        head = [ln for ln in f if ln.startswith("#")]
    return pd.read_csv(path, skiprows=len(head), dtype=str, keep_default_na=False)


def ws(s):
    s = (s or "").replace(chr(0x2014), ", ").replace(chr(0x2013), "-").replace(chr(0x2019), "'").replace(chr(0x2018), "'")
    s = s.replace(chr(0x201c), '"').replace(chr(0x201d), '"').replace(chr(0xa0), " ").replace(chr(0xad), "")
    s = s.replace("``", '"').replace("''", '"').replace("--", ", ")  # the print's quote marks and its dash
    return re.sub(r"\s+", " ", s).strip()


def loose(s):
    """For 'is this literally there' comparisons: white space, dashes and the print's hyphenation at line ends."""
    return re.sub(r"\s*,\s*", ", ", re.sub(r"\s*-\s*", "-", ws(s))).casefold()


def fr_text(raw):
    """The printed document as plain text (the Register's raw text is HTML around a <pre>)."""
    return H.unescape(re.sub(r"<[^>]+>", "", raw))


def fr_parse(text, agency_names=None):
    """The heading of a printed Federal Register document: date, section, number, agencies, bracket lines, RINs,
    title, ACTION, SUMMARY."""
    out = {"date": "", "section": "", "number": "", "agencies": [], "brackets": [], "rins": [], "title": "",
           "action": "", "summary": ""}
    m = re.search(r"\[Federal Register Volume \d+, Number \d+ \(\w+, (\w+) (\d{1,2}), (\d{4})\)\]", text)
    if m:
        out["date"] = f"{m.group(3)}-{MONTHS[m.group(1)]:02d}-{int(m.group(2)):02d}"
    m = re.search(r"^\[(Notices|Rules and Regulations|Proposed Rules|Presidential Documents)\]", text, re.M)
    out["section"] = m.group(1) if m else ""
    m = re.search(r"\[FR Doc No: ([^\]]+)\]", text)
    out["number"] = m.group(1).strip() if m else ""
    body = text[m.end():] if m else text
    nl = chr(10)
    body = nl.join(ln for ln in body.split(nl) if not ln.startswith(chr(0))
                   and not re.fullmatch(r"\[\[Page \d+\]\]", ln.strip()) and not re.fullmatch(r"-{20,}", ln.strip()))
    body = body.replace(chr(0), "")
    blocks = [b.strip() for b in re.split(r"\n\s*\n", body) if b.strip()]
    known = {ws(x).casefold() for x in (agency_names or [])}
    i = 0
    while i < len(blocks) and (i == 0 or ws(blocks[i]).casefold() in known):
        out["agencies"].append(ws(blocks[i]))  # the department in capitals, then the bureau as the Register names it
        i += 1
    while i < len(blocks) and (blocks[i].startswith("[") or re.match(r"(\d+ CFR|RIN )", blocks[i])):
        out["brackets"] += [ws(x) for x in re.findall(r"\[([^\]]+)\]", blocks[i], re.S)]
        i += 1
    out["title"] = ws(blocks[i]) if i < len(blocks) else ""
    head = body[:6000]
    out["rins"] = sorted(set(re.findall(r"\bRIN\s+(\d{4}-[A-Z]{2}\d{2})\b", head)))
    m = re.search(r"\nACTION:\s*(.*?)\n\s*\n", body, re.S)
    out["action"] = ws(m.group(1)) if m else ""
    m = re.search(r"\nSUMMARY:\s*(.*?)\n\s*\n(?=[A-Z][A-Z ]+:)", body, re.S)
    out["summary"] = ws(m.group(1)) if m else ""
    out["body"] = body
    return out


def agency_of(names):
    low = " | ".join(names).casefold()
    return next((short for short, name in AGENCY_TEXT if name in low), "")


def pdf_text(path):
    import pdfplumber
    with pdfplumber.open(path) as pdf:
        return "\n".join((p.extract_text() or "") for p in pdf.pages)


def html_text(s):
    s = re.sub(r"(?is)<(script|style|nav|header|footer)[^>]*>.*?</\1>", " ", s)
    return re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", " ", s))).strip()


def main(argv=None):
    import policy_sources as ps
    ap = argparse.ArgumentParser(description="ERW policy audit: checks by code")
    ap.add_argument("--in-dir", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    acts = read_events(os.path.join(args.in_dir, "policy_actions.csv")).set_index("event_id")
    reads = read_events(os.path.join(args.in_dir, "policy_reads.csv")).set_index("action_event_id")
    evid = read_events(os.path.join(args.in_dir, "policy_reads_evidence.csv"))
    with open(os.path.join(args.out, "sample.csv"), encoding="utf-8") as f:
        sample = [r["event_id"] for r in csv.DictReader(ln for ln in f if not ln.startswith("#"))]
    man = list(csv.DictReader(open(os.path.join(args.out, "manifest.csv"), encoding="utf-8")))
    doc = {(m["key"], m["kind"]): m for m in man if m["status"] == "200"}
    checks, md = [], []

    def add(eid, field, cls, row_val, src_val, note=""):
        checks.append(dict(event_id=eid, field=field, cls=cls, row_value=row_val[:400], source_value=src_val[:400],
                           note=note))

    for n, eid in enumerate(sample, 1):
        r = acts.loc[eid]
        md.append(f"\n\n## {n}. {eid}\n")
        md.append(f"- row: date {r.event_date} | agency {r.agency} | type {r.action_type} | status `{r.status}` | "
                  f"docket `{r.docket}` | rin `{r.rin}` | states `{r.states}` | tags `{r.sector_tags}` | "
                  f"related `{r.related_urls}`\n- row title: {r.title}\n- row abstract: {r.abstract}\n"
                  f"- MODEL: significance {r.significance} | sector {r.sector} | why: {r.why}\n- url: {r.source_url}\n")
        if eid.startswith("federalregister:"):
            a, t = doc.get((eid, "api")), doc.get((eid, "text"))
            if not a or not t:
                for fld in ("event_date", "agency", "action_type", "title", "abstract", "docket", "rin",
                            "fr_document_number", "states", "source_url"):
                    add(eid, fld, "not_reachable", r[fld], "")
                continue
            api = json.load(open(os.path.join(args.out, a["file"]), encoding="utf-8"))
            text = fr_text(open(os.path.join(args.out, t["file"]), encoding="utf-8", errors="replace").read())
            p = fr_parse(text, [x.get("raw_name") or "" for x in api.get("agencies") or []]
                         + [x.get("name") or "" for x in api.get("agencies") or []])
            # event_date: the publication date, by the table's own definition
            add(eid, "event_date", "correct" if r.event_date == p["date"] == api["publication_date"] else "wrong",
                r.event_date, f"printed {p['date']}; api {api['publication_date']}")
            add(eid, "fr_document_number", "correct" if r.fr_document_number == p["number"] == api["document_number"]
                else "wrong", r.fr_document_number, f"printed {p['number']}; api {api['document_number']}")
            add(eid, "action_type", "correct" if r.action_type == SECTION.get(p["section"]) else "wrong", r.action_type,
                f"printed section [{p['section']}]; api type {api['type']}")
            src_ag = agency_of(p["agencies"])
            add(eid, "agency", "correct" if r.agency == src_ag else "wrong", r.agency,
                f"printed {' / '.join(p['agencies'])}")
            add(eid, "title", "correct" if loose(r.title) == loose(p["title"]) else
                ("correct" if loose(r.title) == loose(ps.clean(api["title"])) else "wrong"), r.title,
                p["title"], "" if loose(r.title) == loose(p["title"]) else "differs from the print; equals the api title"
                if loose(r.title) == loose(ps.clean(api["title"])) else "")
            # abstract: literal text of the printed SUMMARY
            if r.abstract:
                lit = loose(r.abstract) in loose(p["body"])
                api_lit = loose(r.abstract) == loose(ps.clean(api.get("abstract"))[:1500])
                add(eid, "abstract", "correct" if lit else "wrong", r.abstract, p["summary"],
                    f"literal in the printed text: {lit}; equals the api abstract (first 1500): {api_lit}")
            else:
                add(eid, "abstract", "missing" if p["summary"] else "source_silent", "", p["summary"],
                    "the print has a SUMMARY" if p["summary"] else "the print has no SUMMARY and the api abstract is null")
            # docket: every element of the row is in a bracket line of the print; every bracket id is in the row
            rins = [x for x in r.rin.split(";") if x]
            row_d = [x for x in r.docket.split(";") if x and x not in rins]
            br = "; ".join(p["brackets"])
            br_ids = [ws(x) for x in re.split(r";", br) if ws(x)]
            notin = [x for x in row_d if loose(x) not in loose(br)]
            miss = [x for x in br_ids if loose(x) not in loose("; ".join(row_d))]
            cls = "source_silent" if not row_d and not br_ids else "missing" if not row_d else \
                "not_in_source" if notin and not br_ids else "wrong" if notin or miss else "correct"
            label = bool(re.search(r"\b(Docket|Project) Nos?\.", r.docket))
            add(eid, "docket", cls, ";".join(row_d), br,
                "; ".join(x for x in [f"row elements not in the print: {notin}" if notin else "",
                                      f"printed ids not in the row: {miss}" if miss else "",
                                      "the row keeps the label (Docket No., Project No.) inside the id" if label else ""] if x))
            src_rin = p["rins"] or sorted(api.get("regulation_id_numbers") or [])
            cls = "source_silent" if not rins and not src_rin else "missing" if not rins else \
                "not_in_source" if not src_rin else "correct" if sorted(rins) == sorted(src_rin) else "wrong"
            add(eid, "rin", cls, r.rin, f"printed {p['rins']}; api {api.get('regulation_id_numbers')}")
            # states: the table's definition is the states named in the title or abstract (with the Register's topics)
            defn = ps.states(f"{ps.clean(api.get('title'))} {ps.clean(api.get('abstract'))} {' '.join(api.get('topics') or [])}")
            head = ws(p["body"][:3500])
            found = {c: len(re.findall(rf"\b{nm}\b", ws(p["body"]))) for nm, c in ps.STATES.items()
                     if re.search(rf"\b{nm}\b", ws(p["body"]))}
            add(eid, "states", "to_read", r.states, f"by the connector's rule on the api record: {defn}",
                f"state names in the printed text (count): {found}")
            add(eid, "source_url", "correct" if r.source_url == api["html_url"] else "wrong", r.source_url, api["html_url"])
            add(eid, "status", "correct" if loose(r.status) == loose(p["action"]) else
                "source_silent" if not r.status and not p["action"] else "wrong", r.status, p["action"])
            md.append(f"- PRINT: agencies {p['agencies']} | brackets {p['brackets']} | rins {p['rins']} | section "
                      f"{p['section']} | action `{p['action']}`\n- print title: {p['title']}\n"
                      f"- api: topics {api.get('topics')} | effective_on {api.get('effective_on')} | dates: "
                      f"{ws(api.get('dates') or '')[:300]}\n- states in print: {found}\n")
            k = p["body"].find(p["title"][:30]) if p["title"] else 0
            after = ws(p["body"][max(k, 0):])
            long_ = eid in reads.index
            md.append(f"- DOCUMENT ({'first 9000 from SUMMARY' if long_ else 'first 2200'}):\n\n> "
                      + (after[(after.find('SUMMARY:') if 'SUMMARY:' in after else 0):][:9000] if long_ else after[:2200]) + "\n")
        else:
            m = doc.get((eid, "page"))
            if not m:
                for fld in ("event_date", "agency", "action_type", "title", "states", "source_url"):
                    add(eid, fld, "not_reachable", r[fld], "")
                continue
            path = os.path.join(args.out, m["file"])
            text = pdf_text(path) if path.endswith(".pdf") else html_text(open(path, encoding="utf-8", errors="replace").read())
            with open(path + ".txt", "w", encoding="utf-8", newline="\n") as f:
                f.write(text)
            flat = ws(text)
            d = pd.Timestamp(r.event_date)
            forms = [f"{d.strftime('%B')} {d.day}, {d.year}", f"{d.strftime('%b')}. {d.day}, {d.year}",
                     f"{d.strftime('%b')} {d.day}, {d.year}", f"{d.month}/{d.day}/{d.year}", r.event_date]
            dates = sorted(set(re.findall(r"\b(?:January|February|March|April|May|June|July|August|September|October|"
                                          r"November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)\.? "
                                          r"\d{1,2}, \d{4}", flat[:4000])))
            add(eid, "event_date", "correct" if any(x in flat for x in forms) else "to_read", r.event_date,
                f"dates in the head of the document: {dates[:6]}")
            add(eid, "title", "correct" if loose(r.title) in loose(flat) else "to_read", r.title, flat[:300])
            add(eid, "agency", "to_read", r.agency, flat[:200])
            add(eid, "action_type", "to_read", r.action_type, "")
            add(eid, "abstract", "source_silent", r.abstract, "", "a news release has no abstract field: blank by design")
            dk = sorted(set(re.findall(r"\b(?:Docket|Project|Proceeding|Rulemaking|Application)\s*(?:No\.|Number)?\s*"
                                       r"[A-Z]{0,3}[.-]?\d{2,5}[-.]\d{2,5}(?:[-.]\d{2,5})?", flat)
                            + re.findall(r"\b[RAI]\.\d{2}-\d{2}-\d{3}\b", flat)))
            add(eid, "docket", "missing" if dk and not r.docket else "source_silent" if not r.docket else "to_read",
                r.docket, "; ".join(dk))
            add(eid, "rin", "source_silent" if not r.rin else "to_read", r.rin, "")
            add(eid, "fr_document_number", "source_silent" if not r.fr_document_number else "to_read",
                r.fr_document_number, "", "a news release has no Register number")
            found = {c: len(re.findall(rf"\b{nm}\b", flat)) for nm, c in ps.STATES.items() if re.search(rf"\b{nm}\b", flat)}
            add(eid, "states", "to_read", r.states, f"state names in the release (count): {found}")
            add(eid, "source_url", "correct" if m["url"] == r.source_url and not m["error"] else "to_read", r.source_url,
                m["url"] + (" " + m["error"] if m["error"] else ""))
            md.append(f"- dates in head: {dates[:6]} | dockets found: {dk} | states in text: {found}\n"
                      f"- DOCUMENT (first {9000 if eid in reads.index else 3000}):\n\n> "
                      + flat[:9000 if eid in reads.index else 3000] + "\n")
        if eid in reads.index:
            x = reads.loc[eid]
            md.append(f"\n- READ: what_changes: {x.what_changes}\n- READ: sectors `{x.affected_sectors}` | isos "
                      f"`{x.affected_isos}` | states `{x.affected_states}` | supply {x.direction_supply} | demand "
                      f"{x.direction_demand} | prices {x.direction_prices} | buildout {x.direction_buildout}\n"
                      f"- READ: timeline: {x.timeline}\n- READ: plain_read: {x.plain_read}\n- READ: kept "
                      f"`{x.fields_kept}` | dropped `{x.fields_dropped}`\n")
            for _, e in evid[evid["read_id"] == x.event_id].iterrows():
                md.append(f"  - span [{e.field}]: {e.span}\n")
    with open(os.path.join(args.out, "auto_checks.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["event_id", "field", "cls", "row_value", "source_value", "note"],
                           lineterminator="\n")
        w.writeheader()
        w.writerows(checks)
    with open(os.path.join(args.out, "dossier.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write("# Session 154 audit dossier: each sampled row beside its source document\n" + "".join(md))
    c = pd.DataFrame(checks)
    print(c.groupby(["field", "cls"]).size().unstack(fill_value=0).to_string())
    return 0


if __name__ == "__main__":
    sys.exit(main())
