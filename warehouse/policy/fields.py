#!/usr/bin/env python3
"""The precise fields of a policy action (session 3056, chain 166): body, instrument, status, every dated step the
document states, the next step, and the action's own figure, each kept with the words it was read from.

Energy Research Warehouse (ERW), platform tool 12. warehouse/connectors/policy_sources.py calls derive() for each
action it builds, with the Federal Register's record of the document (or none, for a news release) and the
document's text (the printed text of a Register document, read once; a release's title and summary). No model is
called and nothing is guessed: a field the record and the text do not state is empty. The audit these fields answer
is docs/reviews/policy-audit-2026-11-06.md (classes 1 to 5 and 8); the fixture is tests/fixtures/policy/.

The columns, added beside the table's own (no column the Digest or the page reads changes its name or meaning):

  body                the issuing body at the level a reader filters by: FERC, NRC, DOE, EPA, IRS, Treasury, BOEM,
                      BLM, OSMRE, BSEE, Interior, PUCT, CPUC, or "<State> Governor" for a governor's release listed
                      on a commission's page (`agency` keeps the connector's short name)
  instrument          one of INSTRUMENTS: what the document is, read from its title and action line (`action_type`
                      keeps the Register's category)
  action_status       one of STATUSES, as of the document's date
  dates               every dated step the text states, as "kind=YYYY-MM-DD" joined by "; " (kinds: KINDS)
  dates_evidence      the words each date stands in, in the same order, joined by " | "
  next_step           the first dated step on or after the document's date, as words ("comments due")
  next_step_date      its date (YYYY-MM-DD)
  next_step_evidence  the words it stands in
  figure_value        the action's own figure, a number (USD as dollars), only from the title or the document's
                      opening paragraph and only with one of the units of FIGURE_UNITS
  figure_unit         MW, GW, kW, MWh, kV, Dth/d, Bcf/d, MMcf/d or USD
  figure_evidence     the sentence it stands in
  docket_ids          the docket and project numbers, one form each ("50-616", never "050-616"), joined by ";"
  fields_from         what the fields were read from: "record and text", "text", "record and summary", "summary",
                      "record", or "title" (a release: its title and its feed's summary are its text)
"""

import re

FIELD_COLS = ["body", "instrument", "action_status", "dates", "dates_evidence", "next_step", "next_step_date",
              "next_step_evidence", "figure_value", "figure_unit", "figure_evidence", "docket_ids", "fields_from"]

INSTRUMENTS = ["rule", "proposed_rule", "order", "guidance", "approval", "lease_sale", "award", "application",
               "complaint", "environmental_review", "meeting", "decision", "notice", "announcement"]
STATUSES = ["proposed", "final", "effective", "stayed", "vacated", "withdrawn", "filed", "open", "scheduled", "issued",
            "announced"]
KINDS = ["effective", "expires", "comments_due", "intervention_due", "review_due", "decision_due", "meeting"]
KIND_WORDS = {"effective": "takes effect", "expires": "ends", "comments_due": "comments due",
              "intervention_due": "interventions or hearing requests due", "review_due": "environmental document due",
              "decision_due": "decision due", "meeting": "meeting or session"}
FIGURE_UNITS = ["MW", "GW", "kW", "MWh", "kV", "Dth/d", "Bcf/d", "MMcf/d", "USD"]

# The Register's agency names (its record's `agencies`) and the body each is filed under. A department is the body
# only when no bureau of it is named.
BODIES = {"Federal Energy Regulatory Commission": "FERC", "Nuclear Regulatory Commission": "NRC",
          "Environmental Protection Agency": "EPA", "Internal Revenue Service": "IRS",
          "Ocean Energy Management Bureau": "BOEM", "Land Management Bureau": "BLM",
          "Surface Mining Reclamation and Enforcement Office": "OSMRE",
          "Safety and Environmental Enforcement Bureau": "BSEE", "Reclamation Bureau": "Reclamation",
          "Fish and Wildlife Service": "FWS", "Indian Affairs Bureau": "BIA", "Geological Survey": "USGS",
          "National Park Service": "NPS", "Energy Department": "DOE", "Interior Department": "Interior",
          "Treasury Department": "Treasury"}
DEPARTMENTS = {"DOE", "Interior", "Treasury"}
# Without the record (a row read before this session): the docket's own prefix names the bureau
DOCKET_BODY = [(re.compile(r"\bBOEM-"), "BOEM"), (re.compile(r"\b(?:SATS No\.|OSM-)"), "OSMRE"), (re.compile(r"\bBSEE-"), "BSEE")]
GOVERNOR = re.compile(r"^\s*Governor\s+[A-Z][a-z]+", re.I)
GOVERNOR_STATE = {"PUCT": "Texas", "CPUC": "California"}

MONTHS = "January|February|March|April|May|June|July|August|September|October|November|December"
# session 3125: a release writes "Tue., Oct. 13, 2026"; the abbreviated months are read too (longest first)
MONTHS_ABBR = r"Sept\.?|Jan\.?|Feb\.?|Mar\.?|Apr\.?|Jun\.?|Jul\.?|Aug\.?|Sep\.?|Oct\.?|Nov\.?|Dec\.?"
DATE = re.compile(rf"\b({MONTHS}|{MONTHS_ABBR})\s+(\d{{1,2}}),\s+(20\d\d)\b")
MONTH_NO = {m: i for i, m in enumerate(MONTHS.split("|"), 1)}
MONTH_NO.update({m[:3]: i for m, i in list(MONTH_NO.items())})
MONTH_NO["Sept"] = 9
# a full stop that ends a sentence: not the stop of p.m., a.m., No., Nos., U.S., Inc., Co., Corp., L.P., e.g., i.e., St.
ABBREV = re.compile(r"(?:\b[ap]\.m|\bNos?|\bU\.S|\bInc|\bCo|\bCorp|\bL\.P|\bLtd|\be\.g|\bi\.e|\bSt|\bNo|\bDr|\bMr|\bMs|\b[A-Z])$")


def _sentences_end(text, start, end):
    """The offset of the last sentence end in text[start:end] (after its stop), or start."""
    best = start
    for m in re.finditer(r"\.\)?\s+(?=[A-Z\[(\"`])|\n\s*\n", text[start:end]):
        stop = start + m.start()
        if text[stop] == "." and ABBREV.search(text[max(0, stop - 8):stop]):
            continue
        best = start + m.end()
    return best


def _sentence_at(text, i, j):
    """The sentence that holds text[i:j], at most 400 characters, whitespace folded."""
    a = _sentences_end(text, max(0, i - 400), i)
    m = None
    for m in re.finditer(r"\.(?:\s+|$)|\n\s*\n", text[j:j + 400]):
        stop = j + m.start()
        if text[stop:stop + 1] == "." and ABBREV.search(text[max(0, stop - 8):stop]):
            m = None
            continue
        break
    b = j + m.end() if m else min(len(text), j + 400)
    return re.sub(r"\s+", " ", text[a:b]).strip()


def iso(m):
    return f"{m.group(3)}-{MONTH_NO[m.group(1).rstrip('.')]:02d}-{int(m.group(2)):02d}"


def body(agency, record=None, docket="", title="", parties=""):
    """The issuing body (above): the record's most specific agency, else the docket's bureau, else a governor's
    release on a commission's page, else the connector's agency."""
    names = [BODIES.get(n) for n in (record or {}).get("agencies") or []]
    names = [n for n in names if n]
    if "FERC" in names:
        return "FERC"
    named = [n for n in names if n not in DEPARTMENTS]
    if named:
        return named[0]
    for pat, b in DOCKET_BODY:
        if pat.search(docket or ""):
            return b
    if agency in GOVERNOR_STATE and (GOVERNOR.search(title or "") or "Governor" in (parties or "")):
        return f"{GOVERNOR_STATE[agency]} Governor"
    return names[0] if names else agency


# The instrument rules, in order: the first that matches is the instrument. `hay` is the title and the Register's
# action line, lower case; for a release, its opening words too (a release names its order in its first sentence).
INSTRUMENT_RULES = [
    ("complaint", re.compile(r"\bv\.\s|\bcomplaint\b")),
    ("lease_sale", re.compile(r"\blease sale\b|\bnotice of sale\b")),
    ("guidance", re.compile(r"\bpolicy statement\b|\bguidance\b|\bregulatory guide\b|\bdraft guide\b|\btrial guide\b|\bstaff guidance\b")),
    ("order", re.compile(r"\bemergency orders?\b|\bauthorization for continued project operation\b|;\s*exemption\s*$|\bexemption\b.*\bissuance\b|\border no\.")),
    # an application the Commission has accepted or that was tendered is an application, whatever else its title says
    ("application", re.compile(r"\bapplication (?:accepted|tendered)\b|\bnotice of (?:intent to file )?(?:license )?application\b")),
    ("meeting", re.compile(r"\bscoping sessions?\b|\bpublic (?:meeting|forum|hearing)s?\b|\bmeeting\b|\bto hold\b.*\bhearing\b")),
    ("environmental_review", re.compile(r"\benvironmental (?:assessment|impact statement)\b|\bscoping period\b|\bfinding of no significant impact\b|\benvironmental issues\b")),
    ("application", re.compile(r"\bapplications?\b|\brequest (?:under|for)\b|\bnotice of request\b|\bnotice; receipt\b|\bamendment request\b|\bpetition for\b")),
    ("approval", re.compile(r"\bapproval\b|\bapproving\b|\bapproves?\b|\bclean data determination\b")),
    ("decision", re.compile(r"\bdecisions? on\b")),
    ("award", re.compile(r"\bfunding\b|\bgrants?\b|\bawards?\b|\bselects?\b|\bselected\b|\binvestments?\b")),
]


def instrument(action_type, title, status_line="", lead=""):
    hay = f"{title} ; {status_line}".lower()
    if action_type == "press_release":
        hay += " ; " + (lead or "")[:700].lower()
    if action_type in ("rule", "proposed_rule"):
        # a Register rule is a rule, or the approval of a state's program or plan that the Register files as one
        return "approval" if dict(INSTRUMENT_RULES)["approval"].search(hay) else action_type
    for name, pat in INSTRUMENT_RULES:
        if name == "approval" or (name == "award" and action_type != "press_release"):
            continue   # an approval is read only of a Register rule (above); an award only of a release
        if pat.search(hay):
            return name
    if re.search(r"\border\b", (status_line or "").lower()) and not re.search(r"order imposing procedures", (status_line or "").lower()):
        return "order"
    return "announcement" if action_type == "press_release" else "notice"


def status(inst, action_type, title, status_line, event_date, dates):
    """The action's status as of its document (STATUSES)."""
    hay = f"{title} ; {status_line}".lower()
    # session 3060, on the whole table: a reinstatement of a terminated lease, a land order's "withdrawal" of land from
    # entry, a meeting on a termination plan and a request ("motion to vacate", "partial vacatur" asked for) are not
    # an action withdrawn or vacated; a termination still proposed is proposed
    if re.search(r"\bproposed termination\b", hay):
        return "proposed"
    if inst != "meeting" and not re.search(r"\breinstatement\b|\bpublic land order\b|\barea withdrawal\b", hay) and re.search(
            r"\bwithdraw(?:al|n|s)?\b|\bterminat(?:ion|ed|es|e)\b", hay):
        return "withdrawn"
    if re.search(r"\bvacat(?:ur|ed|es|e)\b", hay) and not re.search(r"\bmotion to vacate\b|\bvacate in part\b|\bpartial vacatur\b", hay):
        return "vacated"
    if re.search(r"\bstay of\b|\bstayed\b|;\s*stay\b|\badministrative stay\b", hay):
        return "stayed"
    eff = [d for k, d, _ in dates if k == "effective"]
    if inst in ("rule", "approval", "proposed_rule"):
        if action_type == "proposed_rule" or re.search(r"\bproposed\b", (status_line or "").lower()):
            return "proposed"
        return "effective" if eff and min(eff) <= event_date else "final"
    if inst in ("guidance", "lease_sale"):
        return "proposed" if re.search(r"\bdraft\b|\bproposed\b|\btrial\b", hay) else ("final" if inst == "lease_sale" else "issued")
    if inst == "environmental_review":
        if re.search(r"\bscoping\b|\bintent to prepare\b", hay):
            return "open"
        if re.search(r"\bschedule\b", hay):
            return "scheduled"
        return "issued"
    if inst in ("application", "complaint"):
        return "filed"
    if inst == "meeting":
        return "scheduled"
    if inst in ("award", "announcement"):
        return "announced"
    if inst == "notice" and eff and min(eff) <= event_date:
        return "effective"
    return "issued"


# What the words before a date say of it, in the order they are tried. The clause is the text between the sentence's
# start (or the date before it in the same sentence) and the date.
CLAUSE_RULES = [
    ("review_due", re.compile(r"issuance of (?:the )?(?:ea|eis|final eis|environmental assessment)\s*$|notice of availability of the (?:final )?eis\s*$", re.I)),
    ("decision_due", re.compile(r"decision deadline\W*(?:\\\d+\\)?\s*$", re.I)),
    # session 3125: a water quality certification's deadline ("Reasonable Period of Time to Act on the Certification
    # Request: One year, August 27, 2027")
    ("decision_due", re.compile(r"reasonable period of time to act on the certification request:\s*(?:[a-z]+ )?(?:years?|months?)?\W*$", re.I)),
    # session 3125: an event's date under its own heading ("When: Tue., Oct. 13, 2026"; "Scoping Session / Date:")
    ("meeting", re.compile(r"^\W*when:\s*$", re.I)),
    ("comments_due", re.compile(r"\bcomments?\b", re.I)),
    ("intervention_due", re.compile(r"\bintervene\b|\bintervention\b|\bprotests?\b|\brequest for a hearing\b|\bhearing request", re.I)),
    ("effective", re.compile(r"\b(?:is|are|will be|becomes?|shall be) effective(?: on| as of)?\s*$|\beffective date is\s*$|\bfor a period effective\s*$|\bin effect beginning(?: on)?\s*$|\btakes? effect(?: on)?\s*$", re.I)),
    ("meeting", re.compile(r"\b(?:scoping|public) (?:session|meeting)s?\b[^.]{0,120}$|\bhearing (?:will be held|is scheduled)\b[^.]{0,60}$", re.I)),
]
# A date in these words is not a step of the action: a filing's or a signature's own date.
NOT_A_STEP = re.compile(r"(?:\bdated|\bdate filed|\bfiled on|\bsigned on|\bsubmitted on|\bopening of this docket on|\bas of)\W*$", re.I)
# A deadline's words end right before its date (its hour taken out): "must be filed by", "on or before", "is", ":"
DEADLINE_END = re.compile(r"(?:\bdue(?: on| by)?|\bby|\bbefore|\bno later than|\blater than|\buntil|\bis|\bshortened to|\bperiod to|:)\s*$", re.I)
WEEKDAY = r"Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|Mon\.|Tue\.|Tues\.|Wed\.|Thu\.|Thurs\.|Fri\.|Sat\.|Sun\."
HOUR_ETC = re.compile(rf"\s*(?:\d{{1,2}}:\d\d\s*[ap]\.?m\.?,?|Eastern (?:Standard |Daylight )?Time|E[DS]?T|Eastern time|on|,|{WEEKDAY})\s*$")


def dates(text, record=None):
    """[(kind, date, evidence)] of every dated step the record and the text state, in the text's order, each (kind,
    date) once. The record's effective_on and comments_close_on are taken with the sentence that states them (or
    the record's own field name when no sentence does)."""
    out, seen, last = [], set(), None
    # a page mark, with the line breaks around it, can stand between a deadline's words and its date
    text = re.sub(r"\s*\[\[Page \d+\]\]\s*", " ", text or "")
    for m in DATE.finditer(text):
        before = text[max(0, m.start() - 300):m.start()]
        # the clause: from the sentence's start, or from the date before it in the same sentence
        cut = _sentences_end(text, max(0, m.start() - 300), m.start()) - max(0, m.start() - 300)
        clause = before[cut:]
        prev = list(DATE.finditer(clause))
        if prev:
            clause = clause[prev[-1].end():]
        clause = re.sub(r"\s+", " ", clause)
        if NOT_A_STEP.search(clause):
            continue
        # the hour of a deadline stands between its words and its date ("by 5:00 p.m. Eastern Time on")
        clause_w = HOUR_ETC.sub("", clause)
        while clause_w != clause:
            clause, clause_w = clause_w, HOUR_ETC.sub("", clause_w)
        kind = None
        # session 3125: a date under a heading of its own ("Evening Scoping Session" / "Date: Tuesday, ..."): the
        # heading is the line before, which a blank line keeps out of the clause
        if re.fullmatch(r"\W*date:\s*", clause, re.I) and re.search(
                r"\b(?:session|meeting|hearing|forum)\b[^\n]{0,40}\n\s*\n?\s*date:\s*\S*\s*$", text[max(0, m.start() - 160):m.start()], re.I):
            kind = "meeting"
        for k, pat in CLAUSE_RULES:
            if k in ("comments_due", "intervention_due"):
                hits = list(pat.finditer(clause))
                # the date is these words' only when it follows them closely and a deadline's words end the clause
                if hits and len(clause) - hits[0].end() <= 200 and DEADLINE_END.search(clause):
                    kind = k
                    break
            elif pat.search(clause):
                kind = k
                break
        # session 3125: a list of meetings ("Tue., Oct. 13, 2026 at 1 p.m. (Virtual) Tue., Oct. 27, 2026"): a date that
        # follows a meeting's date by no more than its hour and its place is a meeting too
        if kind is None and last and last[0] == "meeting" and m.start() - last[1] < 60 and \
                re.fullmatch(r"\s*(?:at\s+)?[\d:\s]*(?:[ap]\.?m\.?)?\s*(?:\([^)]{0,30}\))?\s*(?:and)?\s*", clause, re.I):
            kind = "meeting"
        if kind is None and re.fullmatch(r"\W*through\s*", clause) and last and last[0] == "effective" \
                and m.start() - last[1] < 40:
            kind = "expires"   # "effective September 17, 2026, through September 16, 2027"
        if kind is None:
            continue
        last = (kind, m.end())
        d = iso(m)
        if (kind, d) in seen:
            continue
        seen.add((kind, d))
        out.append((kind, d, _sentence_at(text, m.start(), m.end())))
    # the exemption or order "effective upon issuance": the date it was issued is its effective date
    if re.search(r"\beffective\s+upon\s+issuance\b", text, re.I):
        m = re.search(rf"\bissued\s+on\s+((?:{MONTHS})\s+\d{{1,2}},\s+20\d\d)", text)
        if m:
            d = iso(DATE.search(m.group(1)))
            if ("effective", d) not in seen:
                seen.add(("effective", d))
                out.append(("effective", d, _sentence_at(text, m.start(), m.end())))
    for field, kind in (("effective_on", "effective"), ("comments_close_on", "comments_due")):
        d = (record or {}).get(field)
        if d and (kind, d) not in seen:
            seen.add((kind, d))
            out.append((kind, d, f"the Federal Register's record: {field} {d}"))
    return out


NEXT_ORDER = {k: i for i, k in enumerate(["comments_due", "intervention_due", "meeting", "review_due", "decision_due",
                                          "effective", "expires"])}


def next_step(steps, event_date):
    """The first step on or after the document's date: (words, date, evidence), or ("", "", "")."""
    ahead = sorted((d, NEXT_ORDER[k], k, e) for k, d, e in steps if d >= event_date)
    if not ahead:
        return "", "", ""
    d, _, k, e = ahead[0]
    return KIND_WORDS[k], d, e


SCALE = {"thousand": 1e3, "million": 1e6, "billion": 1e9}
FIGURE = re.compile(
    r"\$\s?(?P<usd>\d[\d,]*(?:\.\d+)?)(?:\s*(?P<scale>thousand|million|billion))?(?![\d,])"
    r"|(?P<num>\d[\d,]*(?:\.\d+)?)[\s-]?(?P<unit>megawatts?|MW|gigawatts?|GW|kilowatts?|kW|MWh|megawatt-hours|kilovolts?|kV|"
    r"dekatherms per day|Dth/d|Bcf/d|billion cubic feet per day|MMcf/d|million cubic feet per day)\b", re.I)
UNIT_OF = {"megawatt": "MW", "mw": "MW", "gigawatt": "GW", "gw": "GW", "kilowatt": "kW", "kw": "kW", "mwh": "MWh",
           "megawatt-hours": "MWh", "kilovolt": "kV", "kv": "kV", "dekatherms per day": "Dth/d", "dth/d": "Dth/d",
           "bcf/d": "Bcf/d", "billion cubic feet per day": "Bcf/d", "mmcf/d": "MMcf/d", "million cubic feet per day": "MMcf/d"}


def lead_of(text, action_type):
    """The document's opening paragraph, where its own figure is stated: for a Register document the SUMMARY (else
    the paragraph after its heading), for a release its opening 700 characters."""
    t = text or ""
    if action_type == "press_release":
        return t[:700]
    m = re.search(r"SUMMARY:(.*?)(?:DATES:|ADDRESSES:|FOR FURTHER INFORMATION|SUPPLEMENTARY INFORMATION)", t, re.S)
    if m:
        # and the opening of its SUPPLEMENTARY INFORMATION, where a notice of intent says what is proposed
        s = re.search(r"SUPPLEMENTARY INFORMATION:(.{0,900})", t, re.S)
        return m.group(1) + ("\n" + re.sub(r"\[\[Page \d+\]\]", " ", s.group(1)) if s else "")
    # a notice without a summary (FERC's): the opening of the text after its docket heading, page marks taken out
    m = re.search(r"\[(?:Docket|Project)[^\]]*\]", t)
    body_ = t[m.end():] if m else t
    body_ = re.sub(r"\[\[Page \d+\]\]", " ", body_)
    return body_[:1800]


def figure(title, text, action_type):
    """(value, unit, evidence) of the action's own figure: the first figure with a unit in the title, else in the
    opening paragraph; (None, "", "") when neither states one."""
    for src in (title or "", lead_of(text, action_type)):
        src = re.sub(r"[ \t]*\n[ \t]*", " ", src)
        found = []
        for m in FIGURE.finditer(src):
            if m.group("usd"):
                v = float(m.group("usd").replace(",", "")) * SCALE.get((m.group("scale") or "").lower(), 1)
                unit = "USD"
            else:
                v = float(m.group("num").replace(",", ""))
                u = m.group("unit").lower()
                unit = UNIT_OF.get(u) or UNIT_OF.get(u.rstrip("s"))
            if v:
                found.append((UNIT_RANK[unit], m.start(), v, unit, m))
        if found:
            # a size (capacity, energy, flow) before a voltage, a voltage before a sum of money; then the first
            _, _, v, unit, m = min(found, key=lambda x: (x[0], x[1]))
            return (int(v) if v == int(v) else v), unit, _sentence_at(src, m.start(), m.end())
    return None, "", ""


UNIT_RANK = {"MW": 0, "GW": 0, "kW": 0, "MWh": 0, "Dth/d": 0, "Bcf/d": 0, "MMcf/d": 0, "kV": 1, "USD": 2}


DOCKET_HEAD = re.compile(r"\b(?:Docket\s+(?:ID\s+)?Nos?\.|Project\s+Nos?\.|SATS\s+No\.|Docket\s+ID|Docket)\s*", re.I)


def docket_ids(docket):
    """The docket and project numbers of a docket field, one form each: "Docket Nos. 050-616 and 050-617" and
    "Docket Nos. 50-616 and 50-617" are both "50-616;50-617"."""
    out = []
    for part in (docket or "").split(";"):
        part = DOCKET_HEAD.sub("", part.strip())
        for x in re.split(r"\s*(?:,|&|\band\b)\s*", part):
            x = x.strip().strip(".").upper()
            if not x or not re.search(r"\d", x):
                continue
            x = re.sub(r"^0+(\d{2,3}-\d)", r"\1", x)
            if x not in out:
                out.append(x)
    return ";".join(out)


def derive(row, text="", record=None):
    """The fields of FIELD_COLS for one action. row: the connector's row (agency, action_type, title, status,
    docket, event_date, parties); text: the document's text ("" when none was read); record: the Register's record
    of it (its agencies, effective_on, comments_close_on) or None."""
    action_type, title, line = row.get("action_type", ""), row.get("title", ""), row.get("status", "")
    if action_type == "press_release":
        line = ""
    hay_text = text or row.get("abstract", "") or row.get("first_paragraph", "")
    steps = dates(hay_text, record)
    inst = instrument(action_type, title, line, hay_text)
    nxt = next_step(steps, row.get("event_date", "")[:10])
    v, unit, ev = figure(title, hay_text, action_type)
    src = ("record and text" if record and text else "text" if text else
           ("record and summary" if record else "summary") if (row.get("abstract") or row.get("first_paragraph")) else
           "record" if record else "title")
    return {"body": body(row.get("agency", ""), record, row.get("docket", ""), title, row.get("parties", "")),
            "instrument": inst,
            "action_status": status(inst, action_type, title, line, row.get("event_date", "")[:10], steps),
            "dates": "; ".join(f"{k}={d}" for k, d, _ in steps),
            "dates_evidence": " | ".join(e.replace("|", "/") for _, _, e in steps),
            "next_step": nxt[0], "next_step_date": nxt[1], "next_step_evidence": nxt[2],
            "figure_value": "" if v is None else str(v), "figure_unit": unit, "figure_evidence": ev,
            "docket_ids": docket_ids(row.get("docket", "")), "fields_from": src}
