#!/usr/bin/env python3
"""The datacenter tracker's fields, one vocabulary each, kept only where a story states them (session 2236, chain 156).

Energy Research Warehouse (ERW). `warehouse/datacenters/extract.py` asks the model for these and passes every facility
through `finish()`; `derive()` gives every row, old or new, the fields that are read from the row's own stored values and
the warehouse's tables (the grid from the words or the state, the utility from EIA-861's counties). The audit of
6 November 2026 (`docs/reviews/deals-audit-2026-11-06.md`, rows A11 to A15) named what they answer. Nothing here calls a
model; `utilities()` reads `utility_service_territories` from disk.
"""

import os
import re
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))

# MW_BASIS: what a stated MW measures. The audit's row A11: 14 of 60 facilities state MW without saying, and one
# ("Nebius signs on for 50MW at Neom's Oxagon data center") is a tenant's share, not the facility's.
MW_BASES = [
    ("it", "IT or critical load: the words IT, critical, compute, of IT capacity"),
    ("total", "the facility's total power, grid or utility capacity, its power demand, a campus of N GW"),
    ("tenant", "one tenant's share of a facility: signs on for, leases, takes N MW"),
    ("phase", "a phase or a building of the facility, not the whole: first phase, initial, first N MW"),
    ("unstated", "the words state MW and not which"),
]
MW_BASIS_IDS = [b for b, _ in MW_BASES]

# POWER_KIND: how the facility is powered, from the stated power_source words; "" when none is stated.
POWER_KINDS = [
    ("behind_the_meter_gas", r"(?:on-?site|behind[- ]the[- ]meter|off-?grid|own|dedicated|mobile).{0,30}(?:gas|turbine)|gas turbines?|generator fleet"),
    ("nuclear", r"nuclear|reactor|smr"),
    ("renewables_storage", r"solar|wind|batter|storage|renewable"),
    ("gas", r"\bgas\b|natural gas|combined[- ]cycle"),
    # off the grid or on the site with no fuel stated (Krolmap's "225MW off-grid data center"): before "grid", whose
    # word "off-grid" contains
    ("behind_the_meter", r"off-?grid|behind[- ]the[- ]meter|on-?site|co-?locat"),
    ("grid", r"(?<!off-)(?<!off )\bgrid\b|utility|power (?:deal|agreement|purchase)|ppa"),
]

STATE_GRID = {  # the site's lib/deals2.ts STATE_GRID: the grid operator that serves most of a state, where one does
    "TX": "ERCOT", "CA": "CAISO", "NY": "NYISO",
    "CT": "ISO-NE", "ME": "ISO-NE", "MA": "ISO-NE", "NH": "ISO-NE", "RI": "ISO-NE", "VT": "ISO-NE",
    "PA": "PJM", "NJ": "PJM", "MD": "PJM", "DE": "PJM", "VA": "PJM", "WV": "PJM", "OH": "PJM", "DC": "PJM",
    "MN": "MISO", "IA": "MISO", "WI": "MISO", "MI": "MISO", "LA": "MISO",
    "OK": "SPP", "KS": "SPP", "NE": "SPP",
}
GRID_WORDS = {
    "ERCOT": r"ercot", "PJM": r"pjm", "MISO": r"miso\b|midcontinent independent", "SPP": r"\bspp\b|southwest power pool",
    "CAISO": r"caiso|california iso", "NYISO": r"nyiso", "ISO-NE": r"iso-ne|iso new england",
}
NEW_COLS = ["mw_basis", "power_kind", "grid", "grid_basis", "utility_eia861", "utility_eia861_number", "utilities_in_county",
            "energized_year", "country", "fields_version"]   # the announcement is first_story_at, as before
VERSION = "2236"


def norm(s):
    return " ".join(str(s or "").replace("’", "'").replace(" ", " ").split()).lower()


def mw_basis(d, text):
    """The model's basis when its span is in the story and says it; "unstated" for a MW without one; "" without MW."""
    if not (d.get("mw") or ""):
        return ""
    b = (d.get("mw_basis") or "").strip()
    span = norm(d.get("mw_basis_text"))
    if b in MW_BASIS_IDS and b != "unstated" and span and span in text:
        return b
    return "unstated"


def power_kind(power_source):
    p = norm(power_source)
    if not p:
        return ""
    for k, pat in POWER_KINDS:
        if re.search(pat, p):
            return k
    return "other"


def grid_of(text, state):
    """(grid, basis): a grid operator the story names ("named"), else the state's main grid ("state"), else none."""
    for g, pat in GRID_WORDS.items():
        if re.search(r"(?<![a-z])(?:" + pat + r")", text or ""):
            return g, "named"
    g = STATE_GRID.get((state or "").upper(), "")
    return (g, "state") if g else ("", "")


def year_in(d, field, span_field, text):
    y = str(d.get(field) or "").strip()
    span = norm(d.get(span_field))
    if re.fullmatch(r"20\d\d", y) and span and span in text and y in span:
        return y
    return ""


_UTIL = None


def territories_path():
    main = os.path.join(os.path.dirname(ROOT), "erw")
    for base in dict.fromkeys([ROOT, main]):
        for p in (os.path.join(base, "warehouse", "output", "utility_service_territories.csv"),
                  os.path.join(base, "runs", "archive_restore", "utility_service_territories.csv")):
            if os.path.exists(p):
                return p
    return None


def utilities(path=None):
    """{(state, county key): [(utility name, number), ...]} from utility_service_territories (EIA-861 2025)."""
    global _UTIL
    if _UTIL is not None and path is None:
        return _UTIL
    path = path or territories_path()
    out = {}
    if path:
        t = pd.read_csv(path, comment="#", dtype=str, keep_default_na=False,
                        usecols=["name", "x_utility_number", "x_state", "x_county"])
        for r in t.itertuples():
            out.setdefault((r.x_state.upper(), county_key(r.x_county)), []).append((r.name, r.x_utility_number))
    if path is None or path == territories_path():
        _UTIL = out
    return out


def county_key(c):
    return re.sub(r"\b(county|parish|borough|census area|city and borough|municipality)\b", "", norm(c)).strip()


def utility_of(state, county, table=None):
    """(name, number, count): the one EIA-861 utility that serves the county; ("", "", n) when n serve it."""
    if not state or not county:
        return "", "", ""
    table = utilities() if table is None else table
    us = sorted(set(table.get((state.upper(), county_key(county)), [])))
    if len(us) == 1:
        return us[0][0], us[0][1], "1"
    return "", "", str(len(us)) if us else ""


def derive(row, text="", table=None):
    """The fields every row gets from its own values: power_kind, grid with its basis, the county's utility."""
    out = dict(row)
    out["power_kind"] = power_kind(out.get("power_source"))
    g, gb = grid_of(text, out.get("state"))
    if out.get("grid_basis") == "named" and out.get("grid"):
        g, gb = out["grid"], "named"   # a grid a story once named stays named
    out["grid"], out["grid_basis"] = g, gb
    name, num, n = utility_of(out.get("state"), out.get("county"), table)
    out["utility_eia861"], out["utility_eia861_number"], out["utilities_in_county"] = name, num, n
    if not out.get("mw_basis") and out.get("mw"):
        out["mw_basis"] = "unstated"
    out["fields_version"] = out.get("fields_version") or "upgraded"
    return out


def finish(d, text):
    """The new fields of one facility from the model's answer, each kept only as stated."""
    country = " ".join(str(d.get("country") or "").split())
    span = norm(d.get("country_text"))
    if country and not (span and span in text and (norm(country) in span or len(span) <= 4)):
        country = ""
    return {"mw_basis": mw_basis(d, text), "energized_year": year_in(d, "energized_year", "energized_text", text),
            "country": country, "fields_version": VERSION}


def description(name):
    """A name field that describes and does not name: "TikTok owner", "a hyperscaler", "Meta-backed developer"."""
    return bool(re.search(r"(?:\bowner|\bparent|\bbacked|\bhyperscaler|\bstartup|\bcompany|\bfirm|\bdeveloper)$", norm(name)))


def has_place(vals):
    return any((vals.get(f) or "").strip() for f in ("site_name", "city", "county", "state", "country"))


def place_conflict(row, vals):
    """True when two facilities name different places: two states, two countries, or two cities in one state. The audit's
    class 8: xAI's Memphis site took its Mississippi story; AWS Mexico took a UAE data center."""
    a, b = (row.get("state") or ""), (vals.get("state") or "")
    if a and b and a != b:
        return True
    ca, cb = norm(row.get("country")), norm(vals.get("country"))
    if ca and cb and ca != cb:
        return True
    if a and a == b:
        for f in ("city", "county"):
            x, y = county_key(row.get(f)), county_key(vals.get(f))
            if x and y and x != y:
                return True
    return False
