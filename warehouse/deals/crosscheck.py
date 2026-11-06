#!/usr/bin/env python3
"""The deal tracker's figures cross-checked against the headlines (session 2235, chain 156).

Energy Research Warehouse (ERW). Every figure of `energy_deals` was kept only where its span is in a story and parses
to the same value (session 15). This module reads each record's headlines again, after the record is built, and flags
(never changes, never drops) what a reader should see before trusting a figure (`docs/reviews/deals-audit-2026-11-06.md`
rows A7 and A8):

1. **The headline's figure against the record's.** A headline that states a size in MW or GW, an energy in MWh or GWh,
   or a sum in US dollars, where the record holds another value or none: "headline: 960 MW; record: none". A sum the
   headline gives as a valuation, a market value or a company-wide investment ("valued at $2.4 billion", "$58 billion
   US shale giant", "to invest $15 billion") is not the deal's and is not compared. Two headlines of one record that
   state two values are both listed, and the record's value must be one of them.
2. **MW and MWh never confused.** A record whose `mw` equals a figure its headlines state in MWh (or whose `mwh` equals
   one stated in MW) is flagged: "mw 462 is a figure the headline states in MWh".
3. **USD and USD per MWh never confused.** A `usd_per_mwh` above 1,000, or a deal sum (`usd`) under 1,000 where the
   words state a price per MWh, is flagged.
4. **The term in years only.** A term the words state in months stays empty (session 15's check) and is flagged with
   the months, so a reader sees that a term exists.
5. **The sanity bounds** of `warehouse/deals/fields.py` (a 50 GW PPA, a term over 40 years): flagged, never dropped.

`flags(row, titles)` returns the list; the extractor writes it to the record's `flags` column ("; " between flags) on
every run, so a record's flags follow its stories. No model; nothing is estimated or converted.
"""

import math
import re

import fields

NUM = r"(\d[\d,]*(?:\.\d+)?)"
MW_RE = re.compile(NUM + r"\s*-?\s*(gw|gigawatts?|mw|megawatts?)(?:dc|ac)?(?![a-z])", re.I)
MWH_RE = re.compile(NUM + r"\s*-?\s*(twh|gwh|mwh|gigawatt.hours?|megawatt.hours?)(?![a-z])", re.I)
USD_RE = re.compile(r"(?:us)?\$\s*" + NUM + r"\s*(trillion|tn|billion|bn|b|million|mn|mm|m)?(?![a-z])", re.I)
MONTHS_RE = re.compile(NUM + r"\s*-?\s*months?", re.I)
PER_MWH_RE = re.compile(r"(?:per\s+(?:mwh|megawatt.hour)|/\s*mwh)", re.I)
NOT_THE_DEALS = re.compile(r"(valued at|valuation|market (?:cap|value)|worth of|to invest|invest(?:s|ing|ment)? (?:of )?(?:\$|us\$)|"
                           r"pledges?|giant|group|company|independent|to create|capex|spending|budget)", re.I)
SCALE = {"gw": 1000.0, "gigawatt": 1000.0, "gigawatts": 1000.0, "mw": 1.0, "megawatt": 1.0, "megawatts": 1.0,
         "twh": 1e6, "gwh": 1000.0, "mwh": 1.0, "trillion": 1e12, "tn": 1e12, "billion": 1e9, "bn": 1e9, "b": 1e9,
         "million": 1e6, "mn": 1e6, "mm": 1e6, "m": 1e6}


def _scale(unit):
    u = unit.lower()
    if u.startswith("gigawatt") and "hour" in u:
        return 1000.0
    if u.startswith("megawatt") and "hour" in u:
        return 1.0
    return SCALE.get(u, 1.0)


def _num(v):
    try:
        x = float(v)
        return x if math.isfinite(x) else None
    except (TypeError, ValueError):
        return None


def stated(title):
    """{"mw": [...], "mwh": [...], "usd": [...]} the figures a headline states, in MW, MWh and USD."""
    out = {"mw": [], "mwh": [], "usd": []}
    t = " ".join(str(title or "").split())
    for m in MWH_RE.finditer(t):
        out["mwh"].append(float(m.group(1).replace(",", "")) * _scale(m.group(2)))
    for m in MW_RE.finditer(t):
        out["mw"].append(float(m.group(1).replace(",", "")) * _scale(m.group(2)))
    for m in USD_RE.finditer(t):
        before = t[max(0, m.start() - 22):m.start()]
        after = t[m.end():m.end() + 28]
        if NOT_THE_DEALS.search(before) or re.match(r"\s*(?:-?\s*plus\s+)?(?:us\s+)?(?:shale\s+)?(?:giant|group|company|independent|"
                                                    r"market|value|valuation|ai infrastructure|investment)", after, re.I):
            continue
        unit = m.group(2) or ""
        if not unit and float(m.group(1).replace(",", "")) < 1000:
            continue   # "$50" with no scale is a price or a share price, not a deal's sum
        out["usd"].append(float(m.group(1).replace(",", "")) * (_scale(unit) if unit else 1.0))
    return out


def _close(a, b):
    return a is not None and b is not None and math.isclose(a, b, rel_tol=0.02)


def _fmt(field, v):
    if field == "usd":
        return f"USD {v / 1e9:g} billion" if v >= 1e9 else f"USD {v / 1e6:g} million" if v >= 1e6 else f"USD {v:g}"
    return f"{v:g} {'MW' if field == 'mw' else 'MWh'}"


def flags(row, titles, text=""):
    """The flags of one record: row is its dict (mw, mwh, usd or dollars, usd_per_mwh or price, term_years); titles the
    headlines of its stories; text, optional, the plain words of its stories (titles and summaries)."""
    out = []
    rec = {"mw": _num(row.get("mw")), "mwh": _num(row.get("mwh")),
           "usd": _num(row.get("usd") if row.get("usd") not in (None, "") else row.get("dollars"))}
    seen = {"mw": [], "mwh": [], "usd": []}
    for t in titles:
        for f, vals in stated(t).items():
            for v in vals:
                if not any(_close(v, x) for x in seen[f]):
                    seen[f].append(v)
    for f in ("mw", "mwh", "usd"):
        if not seen[f]:
            continue
        if rec[f] is None:
            out.append(f"headline: {', '.join(_fmt(f, v) for v in seen[f])}; record: none")
        elif not any(_close(rec[f], v) for v in seen[f]):
            out.append(f"headline: {', '.join(_fmt(f, v) for v in seen[f])}; record: {_fmt(f, rec[f])}")
    # MW and MWh confused
    if rec["mw"] is not None and any(_close(rec["mw"], v) for v in seen["mwh"]) and not any(_close(rec["mw"], v) for v in seen["mw"]):
        out.append(f"mw {fields.num(rec['mw'])} is a figure the headline states in MWh")
    if rec["mwh"] is not None and any(_close(rec["mwh"], v) for v in seen["mw"]) and not any(_close(rec["mwh"], v) for v in seen["mwh"]):
        out.append(f"mwh {fields.num(rec['mwh'])} is a figure the headline states in MW")
    # USD and USD per MWh confused
    p = _num(row.get("usd_per_mwh") if row.get("usd_per_mwh") not in (None, "") else row.get("price"))
    if p is not None and p > fields.BOUNDS["usd_per_mwh"]:
        out.append(f"usd_per_mwh {fields.num(p)} is above the bound of {fields.num(fields.BOUNDS['usd_per_mwh'])}: a sum, not a price?")
    words = " ".join(titles) + " " + (text or "")
    if rec["usd"] is not None and rec["usd"] < 1000 and PER_MWH_RE.search(words):
        out.append(f"usd {fields.num(rec['usd'])} is under 1,000 where the words state a price per MWh: a price, not a sum?")
    # a term in months
    if _num(row.get("term_years")) is None:
        m = MONTHS_RE.search(words)
        if m and re.search(r"contract|agreement|deal|ppa|term|lease|supply", words, re.I):
            out.append(f"term stated in months ({m.group(0)}): term_years left empty")
    out.extend(fields.flags_of({"mw": rec["mw"], "mwh": rec["mwh"], "usd": rec["usd"],
                                "term_years": _num(row.get("term_years"))}))
    return out
