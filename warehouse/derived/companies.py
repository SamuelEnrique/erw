#!/usr/bin/env python3
"""The company database (platform tool 10): one row a company the warehouse already knows, every name it goes by, and
every row of every table that names it (sessions 3301 to 3303, chain 200).

Energy Research Warehouse (ERW). Three derived tables, computed from tables held; no request is made, no model is
called, nothing is filled in. Method: docs/methods/companies.md.

    python warehouse/derived/companies.py                 # the three tables, under the data lock
    python warehouse/derived/companies.py --out-dir DIR   # a trial: the tables under DIR

company_directory (entities, entity_type company): one row a company: its name, canonical id, kind, segment, parent, HQ state
where a held table states it, first and last seen, and its footprint (deals and their MW and USD, plants operated and
their MW by fuel, MW owned, planned MW, datacenter facilities and MW, queue positions and MW, reactors, policy actions).

company_aliases (entities, entity_type company_alias): one row a name a company goes by, in each table and role it
appears in, with the first row it came from and the count of rows.

company_links (entities, entity_type company_link): one row a company and a row of an input table, with the role the
company plays in it (buyer, seller, operator, owner, utility, developer, licensee, agency ...), the name as the row
writes it, the rule that matched it, a confidence, the row's license, and the row's MW, USD, date, fuel, state and grid
where the row states them.

The resolution (docs/methods/companies.md, "The rules"):

1. A name is normalized (`norm`): ASCII, lower case, "&" read as "and", punctuation dropped, EIA's abbreviations
   expanded ("Elec" electric, "Coop" cooperative, "Assn" association ...), a leading "the" and the legal forms at the
   end dropped ("Inc", "LLC", "Corp", "Co", "Company", "LP", "Ltd", "plc", "SA", "AG" ...).
2. An EIA utility id is an anchor: every row that carries the same id (EIA-861's utility number, EIA-860's operator
   utility id and owner id, which are the same codes) is one company, whatever its name; two ids are never merged by
   name.
3. The reviewed aliases (warehouse/companies/reviewed_aliases.csv, each with the rows that show it) map a name to
   another; a reviewed row may also give a parent and a kind.
4. A name without an id joins the anchored company whose normalized name it equals, where exactly one does.
5. Names left are grouped on their normalized name; two such groups whose names differ only by a company word at the
   end ("Energy", "Power", "Group") are one, where that shorter name is not a common word and only one group has it.
6. A parent is a second field, never in place of the name: from the NRC's parent company field and the reviewed
   aliases only.

Each link's confidence follows its rule: 1.0 an EIA id; 0.95 a reviewed alias; 0.9 the same normalized name as an
anchored company; 0.85 the same normalized name among names without an id; 0.7 a company word added.
"""

import argparse
import csv
import datetime as dt
import hashlib
import os
import re
import sys
import traceback
import unicodedata
from collections import Counter, defaultdict

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import iso_prices as ip  # noqa: E402

NAME, ALIASES, LINKS = "company_directory", "company_aliases", "company_links"
SOURCE = "erw:companies"
REVIEWED = os.path.join(ROOT, "warehouse", "companies", "reviewed_aliases.csv")
COVERAGE = os.path.join(ROOT, "warehouse", "metadata", "coverage.csv")
LICENSE_STATUS = os.path.join(ROOT, "warehouse", "metadata", "license_status.csv")
ENTITY_COLS = ["entity_id", "entity_type", "name", "geo", "lat", "lon", "capacity_mw", "status",
               "status_date", "operator", "source", "source_url", "retrieved_at", "vintage"]

INPUTS = ["energy_deals", "datacenter_projects", "datacenter_facilities", "eia860m_operating_generators",
          "eia860m_planned_generators", "eia860_plants_annual", "eia860_generator_owners", "eia861_utility_data",
          "utility_service_territories", "ercot_interconnection_queue", "nyiso_interconnection_queue",
          "policy_actions", "nrc_power_reactors"]

# ---------------------------------------------------------------------------------------------------------------
# 1. Normalization

LEGAL = {"inc", "incorporated", "corp", "corporation", "co", "company", "llc", "lc", "l l c", "lp", "l p", "llp",
         "ltd", "limited", "plc", "sa", "ag", "nv", "bv", "gmbh", "se", "spa", "sarl", "pllc", "pc", "asa", "ab",
         "oyj", "kk", "pte", "pty", "sas", "srl", "lllp", "the"}
# EIA's own abbreviations in utility and operator names, read whole words only
ABBREV = {"elec": "electric", "electrc": "electric", "coop": "cooperative", "co op": "cooperative",
          "cooperatve": "cooperative", "assn": "association", "assoc": "association", "mun": "municipal",
          "muni": "municipal", "pwr": "power", "dept": "department", "util": "utility", "utils": "utilities",
          "svc": "service", "svcs": "services", "mgmt": "management", "dist": "district", "auth": "authority",
          "admin": "administration", "intl": "international", "natl": "national", "pub": "public", "corp": "corp"}
GENERIC_END = ("energy", "power", "group")
# a shorter name rule 5 never takes: a common word, a place or a kind, not a company
COMMON = {"american", "national", "united", "first", "new", "north", "south", "east", "west", "northern", "southern",
          "eastern", "western", "central", "pacific", "atlantic", "general", "global", "international", "public",
          "city", "county", "state", "us", "usa", "texas", "california", "new york", "florida", "clean", "green",
          "solar", "wind", "renewable", "renewables", "nuclear", "gas", "electric", "community", "sun", "blue", "red",
          "great", "golden", "sunrise", "pioneer", "summit", "eagle", "liberty", "star", "alpha", "apex", "next"}
STATE_TAG = re.compile(r"\s*-?\s*\(([A-Z]{2})\)\s*$")


def ascii_fold(s):
    return unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode("ascii")


def norm(name):
    """The normalized form of a name (rule 1): '' for a blank."""
    s = ascii_fold(name or "").lower().strip()
    if not s:
        return ""
    s = s.replace("&", " and ").replace("+", " and ")
    s = re.sub(r"[’'`]", "", s)                       # O'Brien -> obrien, Xcel's -> xcels
    s = re.sub(r"(?<=\b[a-z])\.(?=[a-z]\b)", "", s)          # U.S. -> us, L.L.C. -> llc (with the next line)
    s = re.sub(r"[^a-z0-9]+", " ", s).strip()
    s = re.sub(r"\bl l c\b", "llc", s)
    s = re.sub(r"\bl l p\b", "llp", s)
    s = re.sub(r"\bl p\b", "lp", s)
    s = re.sub(r"\bco op\b", "cooperative", s)
    words = [ABBREV.get(w, w) for w in s.split()]
    # "Co" inside a name is "Company" ("Public Service Co of Colorado"); at the end it is a legal form, dropped below
    words = [("company" if w == "co" and i < len(words) - 1 else w) for i, w in enumerate(words)]
    if words and words[0] == "the" and len(words) > 1:
        words = words[1:]
    while len(words) > 1 and words[-1] in LEGAL:
        words = words[:-1]
    return " ".join(words)


def core(key):
    """A normalized name with one company word dropped from its end (rule 5), or None when it has none or what is
    left is a common word or shorter than four letters."""
    words = key.split()
    if len(words) < 2 or words[-1] not in GENERIC_END:
        return None
    rest = " ".join(words[:-1])
    while rest.split() and rest.split()[-1] in LEGAL:
        rest = " ".join(rest.split()[:-1])
    if len(rest.replace(" ", "")) < 4 or rest in COMMON:
        return None
    return rest


def slug(key):
    return re.sub(r"[^a-z0-9]+", "-", key).strip("-")[:60] or "x"


# ---------------------------------------------------------------------------------------------------------------
# Parties written as text: split, and descriptions left out

DESCRIPTIONS = {"investors", "investor", "banks", "bank", "lenders", "lender", "shareholders", "management",
                "hyperscaler", "a hyperscaler", "us hyperscaler", "partners", "buyers", "bondholders", "creditors",
                "undisclosed", "undisclosed buyer", "undisclosed investors", "unnamed", "unnamed buyer", "others",
                "consortium", "a consortium", "government", "the government", "us government", "federal government"}
COUNTRIES = {"united states", "us", "usa", "south korea", "korea", "japan", "china", "india", "germany", "france",
             "united kingdom", "uk", "canada", "mexico", "brazil", "australia", "saudi arabia", "qatar",
             "united arab emirates", "uae", "norway", "italy", "spain", "netherlands", "poland", "indonesia",
             "vietnam", "taiwan", "singapore", "malaysia", "egypt", "turkey", "argentina", "chile", "russia",
             "ukraine", "israel", "kuwait", "oman", "iraq", "iran", "nigeria", "south africa", "philippines",
             "thailand", "kazakhstan", "azerbaijan", "mozambique", "guyana", "colombia", "peru", "sweden", "finland",
             "denmark", "belgium", "austria", "switzerland", "ireland", "portugal", "greece", "romania", "czech republic",
             "hungary", "new zealand", "pakistan", "bangladesh", "algeria", "libya", "angola", "senegal", "tanzania",
             "kenya", "morocco", "jordan", "bahrain", "venezuela", "trinidad and tobago", "ecuador", "bolivia"}
# names that hold the word "and" and are one company
AND_NAMES = ("industrial and commercial bank of china", "procter and gamble", "johnson and johnson",
             "trinidad and tobago", "black and veatch", "burns and mcdonnell", "babcock and wilcox",
             "hyundai engineering and construction", "samsung c and t", "public service enterprise group",
             "ernst and young", "marsh and mclennan", "texas new mexico power")


def split_parties(text):
    """The names in a party field: split on ";" and ","; then on " and " unless the piece is a name that holds
    "and" (AND_NAMES). A piece's leading "and " is dropped."""
    out = []
    for semi in str(text or "").split(";"):
        for piece in re.split(r",\s+(?![^()]*\))", semi):
            piece = re.sub(r"^\s*and\s+", "", piece.strip())
            if not piece:
                continue
            if " and " in piece and not any(a in norm(piece) for a in AND_NAMES):
                out.extend(p.strip() for p in piece.split(" and ") if p.strip())
            else:
                out.append(piece)
    return out


# a party that ends in one of these lower-case words describes a thing ("Amazon data center unit", "Japanese firms"),
# or that is tied to a company by a hyphen ("Meta-backed data centre"), or names a government or a law
DESC_END = re.compile(r"\s(unit|subsidiary|vehicle|arm|consortium|joint venture|firms?|buyers?|investors?|banks|"
                      r"people|owners|project|refinery|data cent(?:er|re)s?|government|ministry|state|startup|"
                      r"partners)$")
DESC_ANY = re.compile(r"-(backed|tied|linked|owned)\b|\bJV$|\bAct$|^State of\b|^The Government of\b|\bgovernment\b|"
                      r"\bMinistry\b|\bStartup$", re.I)


def is_description(name):
    """A party that is a description, a country or a word, not a name: a lower-case start, a listed description, a
    country, a description's words (DESC_END, DESC_ANY), or nothing left once normalized."""
    s = str(name or "").strip()
    if not s or s[0].islower():
        return True
    if DESC_END.search(s) or DESC_ANY.search(s):
        return True
    k = norm(s)
    return not k or k in DESCRIPTIONS or k in COUNTRIES


POSSESSIVE = re.compile(r"^(.+?)['’]s\s+([A-Z0-9].*)$")


def split_possessive(name):
    """("X's Y") -> (Y, X): the name is Y and X its parent, as the row writes it; else (name, "")."""
    m = POSSESSIVE.match(str(name or "").strip())
    if m and not is_description(m.group(2)):
        return m.group(2).strip(), m.group(1).strip()
    return str(name or "").strip(), ""


def parse_parent(text):
    """The NRC's parent field as (parent, [aliases]): "X with principal subsidiaries ..." is X; "X doing business as Y"
    is Y, the name the parent goes by (X is the licensee's own name); "X (ACR)" is X with ACR an alias."""
    s = str(text or "").strip()
    if not s:
        return "", []
    aliases = []
    s = re.split(r"\s+with principal subsidiar", s)[0].strip().rstrip(",")
    m = re.match(r"(.*?)\s+(?:doing business as|d/b/a|dba)\s+(.*)$", s, re.I)
    if m:
        s = m.group(2).strip()
    m = re.match(r"(.*?)\s*\(([A-Za-z0-9&.\- ]{2,12})\)\s*$", s)
    if m:
        s = m.group(1).strip()
        aliases.append(m.group(2).strip())
    return s, aliases


# ---------------------------------------------------------------------------------------------------------------
# Fuels and grids, as the inputs write them

FUEL = {"SUN": "solar", "WND": "wind", "NG": "gas", "OG": "gas", "BFG": "gas", "PG": "gas", "SGC": "gas",
        "BIT": "coal", "SUB": "coal", "LIG": "coal", "RC": "coal", "WC": "coal", "ANT": "coal", "SC": "coal",
        "NUC": "nuclear", "WAT": "hydro", "MWH": "storage", "DFO": "oil", "RFO": "oil", "JF": "oil", "KER": "oil",
        "WO": "oil", "PC": "oil", "GEO": "geothermal"}
FUELS = ["solar", "wind", "gas", "coal", "nuclear", "hydro", "storage", "oil", "geothermal", "other"]
BA_GRID = {"ERCO": "ERCOT", "CISO": "CAISO", "PJM": "PJM", "MISO": "MISO", "NYIS": "NYISO", "ISNE": "ISO-NE",
           "SWPP": "SPP"}
RTO_COLS = {"x_rto_caiso": "CAISO", "x_rto_ercot": "ERCOT", "x_rto_pjm": "PJM", "x_rto_nyiso": "NYISO",
            "x_rto_spp": "SPP", "x_rto_miso": "MISO", "x_rto_isone": "ISO-NE"}


def fuel_of_code(code):
    return FUEL.get(str(code or "").strip().upper(), "other") if str(code or "").strip() else ""


def fuel_of_text(text):
    t = str(text or "").lower()
    for word, fuel in (("storage", "storage"), ("battery", "storage"), ("solar", "solar"), ("photovoltaic", "solar"),
                       ("wind", "wind"), ("nuclear", "nuclear"), ("hydro", "hydro"), ("coal", "coal"),
                       ("geothermal", "geothermal"), ("lng", "gas"), ("gas", "gas"), ("combined cycle", "gas"),
                       ("combustion", "gas"), ("methane", "gas"), ("oil", "oil"), ("transmission", "transmission"),
                       ("data center", "datacenters"), ("datacenter", "datacenters"), ("fusion", "fusion"),
                       ("uranium", "nuclear"), ("smr", "nuclear")):
        if word in t:
            return fuel
    return "other" if t.strip() else ""


def num(v):
    try:
        x = float(str(v).replace(",", ""))
    except (TypeError, ValueError):
        return None
    return x if x == x else None


def year_of(v):
    m = re.match(r"^\s*(\d{4})", str(v or ""))
    return m.group(1) if m else ""


def date_of(v):
    m = re.match(r"^\s*(\d{4}-\d{2}-\d{2})", str(v or ""))
    if m:
        return m.group(1)
    y = year_of(v)
    return f"{y}-01-01" if y else ""


def eia_id(v):
    x = num(v)
    return str(int(x)) if x is not None and x > 0 else ""


# ---------------------------------------------------------------------------------------------------------------
# Reading the inputs: one mention a name in a row

def read_table(path):
    n = 0
    with open(path, encoding="utf-8") as f:
        for ln in f:
            if not ln.startswith("#"):
                break
            n += 1
    return pd.read_csv(path, skiprows=n, dtype=str, keep_default_na=False, low_memory=False)


def licenses(tables, coverage=COVERAGE, status=LICENSE_STATUS):
    """{table: 'public' or 'internal'}: internal where coverage says internal, or license_status.csv says 'license
    needed' with no permission recorded (from its day on)."""
    lic = {t: "public" for t in tables}
    if os.path.exists(coverage):
        with open(coverage, encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                if r.get("table") in lic and r.get("license") == "internal":
                    lic[r["table"]] = "internal"
    today = dt.datetime.now(dt.timezone.utc).date().isoformat()
    if os.path.exists(status):
        with open(status, encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                if (r.get("table") in lic and r.get("status") == "license needed" and not r.get("permission")
                        and (r.get("from") or "") <= today):
                    lic[r["table"]] = "internal"
    return lic


def mention(table, row_id, role, raw, anchor="", **kw):
    m = dict(table=table, row_id=row_id, role=role, raw=str(raw).strip(), anchor=anchor, mw="", usd="", date="",
             fuel="", state="", grid="", extra="")
    m.update({k: ("" if v is None else v) for k, v in kw.items()})
    return m


def m_deals(d):
    out = []
    for r in d.to_dict("records"):
        kw = dict(mw=r.get("mw", ""), usd=r.get("dollars", ""), date=date_of(r.get("event_date")),
                  fuel=fuel_of_text(r.get("technology")), state=r.get("state", ""), extra=r.get("deal_type", ""))
        for role, col in (("buyer", "buyer"), ("seller", "seller"), ("party", "other_parties")):
            for p in split_parties(r.get(col, "")):
                if is_description(p):
                    continue
                name, parent = split_possessive(p)
                out.append(mention("energy_deals", r["event_id"], role, name, parent_hint=parent, written=p, **kw))
    return out


def m_datacenters(d, table):
    out = []
    for r in d.to_dict("records"):
        kw = dict(mw=r.get("mw", "") or r.get("capacity_mw", ""), state=r.get("state", ""),
                  date=date_of(r.get("first_story_at") or r.get("status_date")), fuel="datacenters",
                  extra=r.get("status", ""))
        for role in ("operator", "developer", "utility"):
            for p in split_parties(r.get(role, "")):
                if not is_description(p):
                    out.append(mention(table, r["entity_id"], role, p, **(kw if role != "utility" else
                                                                          dict(kw, mw=""))))
    return out


def m_860m(d, table):
    out = []
    for r in d.to_dict("records"):
        if not r.get("operator"):
            continue
        date = r.get("status_date") if table.endswith("operating_generators") else r.get("planned_operation_date")
        out.append(mention(table, r["entity_id"], "operator", r["operator"], eia_id(r.get("utility_id")),
                           mw=r.get("nameplate_mw", ""), date=date_of(date), fuel=fuel_of_code(r.get("energy_source")),
                           state=r.get("state", ""), grid=BA_GRID.get(r.get("balancing_authority", ""), ""),
                           extra=f"plant {eia_id(r.get('plant_id'))}"))
    return out


def m_plants(d):
    out = []
    for r in d.to_dict("records"):
        if r.get("operator"):
            out.append(mention("eia860_plants_annual", r["entity_id"], "operator", r["operator"],
                               eia_id(r.get("x_utility_id")), state=r.get("x_state", ""),
                               grid=BA_GRID.get(r.get("x_balancing_authority_code", ""), ""),
                               extra=r.get("x_sector_name", "")))
    return out


def m_owners(d, nameplate):
    out = []
    for r in d.to_dict("records"):
        parts = r["entity_id"].split(":")
        owner = parts[3] if len(parts) > 3 else ""
        plant, gen = (parts[1], parts[2]) if len(parts) > 2 else ("", "")
        pct = num(r.get("x_percent_owned"))
        mw = nameplate.get((plant, gen))
        owned = round(mw * pct, 3) if mw is not None and pct is not None else ""
        out.append(mention("eia860_generator_owners", r["entity_id"], "owner", r["name"], eia_id(owner), mw=owned,
                           state=r.get("x_state", ""), extra=r.get("x_owner_state", "")))
    return out


def m_861(d):
    out = []
    for r in d.to_dict("records"):
        grids = ";".join(g for c, g in RTO_COLS.items() if str(r.get(c, "")).upper() in ("Y", "TRUE", "1", "X"))
        out.append(mention("eia861_utility_data", r["entity_id"], "utility", r["name"], eia_id(r.get("x_utility_number")),
                           date=date_of(r.get("x_year")), state=r.get("x_state", ""), grid=grids,
                           extra=r.get("x_ownership", "")))
    return out


def m_territories(d):
    return [mention("utility_service_territories", r["entity_id"], "service_territory", r["name"],
                    eia_id(r.get("x_utility_number")), state=r.get("x_state", ""), date=date_of(r.get("x_data_year")),
                    extra=r.get("x_county", "")) for r in d.to_dict("records")]


def m_queue(d, table, grid):
    out = []
    for r in d.to_dict("records"):
        if not r.get("operator"):
            continue
        out.append(mention(table, r["entity_id"], "interconnection_customer", r["operator"], mw=r.get("capacity_mw", ""),
                           date=date_of(r.get("queue_date")), fuel=fuel_of_text(r.get("fuel_technology")),
                           state=r.get("state", ""), grid=grid,
                           extra="withdrawn" if r.get("withdrawn_date") or r.get("iso_status") == "Withdrawn"
                           else (r.get("iso_status") or "")))
    return out


def m_policy(d):
    out = []
    for r in d.to_dict("records"):
        for p in str(r.get("parties", "")).split(";"):
            p = p.strip()
            if p and not is_description(p):
                out.append(mention("policy_actions", r["event_id"], "agency", p, date=date_of(r.get("event_date")),
                                   state=r.get("states", ""), extra=r.get("action_type", "")))
    return out


def m_nrc(d):
    out, parents = [], []
    for r in d.to_dict("records"):
        kw = dict(mw=r.get("capacity_mw", ""), fuel="nuclear", date=date_of(r.get("x_commercial_operation")),
                  state=(r.get("x_location", "").rsplit(",", 1)[-1].strip()[:2]
                         if re.search(r",\s*[A-Z]{2}", r.get("x_location", "")) else ""))
        seen = set()
        for role, col in (("licensee", "x_licensee"), ("operator", "operator")):
            v = r.get(col, "").strip()
            if v and norm(v) not in seen:
                seen.add(norm(v))
                out.append(mention("nrc_power_reactors", r["entity_id"], role, v, **kw))
        parent, aliases = parse_parent(r.get("x_parent_company", ""))
        if parent:
            out.append(mention("nrc_power_reactors", r["entity_id"], "parent", parent, **kw))
            child = r.get("x_licensee", "").strip() or r.get("operator", "").strip()
            if child and norm(child) != norm(parent):
                parents.append((child, parent, r["entity_id"]))
            for a in aliases:
                parents.append(("alias", a, parent, r["entity_id"]))
    return out, parents


def read_reviewed(path=REVIEWED):
    """The reviewed aliases: [{alias, canonical, parent, kind, eia_utility_id, evidence}]."""
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8", newline="") as f:
        rows = [r for r in csv.DictReader(ln for ln in f if not ln.startswith("#"))]
    for r in rows:
        if not (r.get("evidence") or "").strip():
            raise ValueError(f"reviewed alias {r.get('alias')!r} has no evidence")
    return rows


# ---------------------------------------------------------------------------------------------------------------
# 2 to 5. The resolution

CONF = {"eia_id": 1.0, "reviewed_alias": 0.95, "anchored_name": 0.9, "name": 0.85, "company_word": 0.7}


def resolve(mentions, reviewed, nrc_pairs=()):
    """Each mention's company: returns (companies {cid: info}, links [mention + cid, rule, confidence])."""
    rev = {}
    rev_kind, rev_parent, rev_eia = {}, {}, {}
    for r in reviewed:
        a, c = norm(r["alias"]), norm(r.get("canonical") or r["alias"])
        if a and c and a != c:
            rev[a] = c
        if r.get("kind"):
            rev_kind[c] = r["kind"].strip()
        if r.get("parent"):
            rev_parent[c] = r["parent"].strip()
        if eia_id(r.get("eia_utility_id")):
            rev_eia[c] = eia_id(r.get("eia_utility_id"))
    for pair in nrc_pairs:                                # the NRC's "doing business as" and "(ACR)" names
        if pair[0] == "alias":
            _, a, parent, _ = pair
            if norm(a) and norm(a) != norm(parent) and norm(a) not in rev:
                rev[norm(a)] = norm(parent)

    def key_of(raw):
        k = norm(raw)
        if k in rev:
            return rev[k], True
        return k, False

    # 2. anchors: an EIA id is a company; a reviewed alias may give a name its id
    anchor_keys = defaultdict(set)                         # normalized name -> {ids}
    for m in mentions:
        k, _ = key_of(m["raw"])
        m["key"] = k
        if not m["anchor"] and k in rev_eia:
            m["anchor"], m["via_rev_id"] = rev_eia[k], True
        if m["anchor"]:
            anchor_keys[k].add(m["anchor"])
    # 4. a name without an id joins the one anchored company of that name
    cid_of = {}
    for m in mentions:
        rule = None
        if m["anchor"]:
            cid = f"company:eia-{m['anchor']}"
            rule = "reviewed_alias" if m.get("via_rev_id") else "eia_id"
        elif len(anchor_keys.get(m["key"], ())) == 1:
            cid = f"company:eia-{next(iter(anchor_keys[m['key']]))}"
            rule = "anchored_name"
        else:
            cid = None
        if cid and norm(m["raw"]) in rev and rule != "eia_id":
            rule = "reviewed_alias"
        m["cid"], m["rule"] = cid, rule
    # 5. names left: grouped on the normalized name, and on the name with a company word dropped
    left = Counter(m["key"] for m in mentions if not m["cid"])
    by_core = defaultdict(set)
    for k in left:
        c = core(k)
        if c:
            by_core[c].add(k)
    target = {}
    for c, keys in by_core.items():
        if c in left and c not in anchor_keys:           # the shorter name is itself held: the longer joins it
            for k in keys:
                target[k] = c
        elif len(keys) > 1 and c not in anchor_keys:      # several longer forms of one name, the shorter not held
            canon = max(keys, key=lambda k: (left[k], -len(k)))
            for k in keys:
                if k != canon:
                    target[k] = canon
    for m in mentions:
        if m["cid"]:
            continue
        k = target.get(m["key"], m["key"])
        m["cid"] = f"company:{slug(k)}"
        if norm(m["raw"]) in rev:
            m["rule"] = "reviewed_alias"
        elif k != m["key"]:
            m["rule"] = "company_word"
        else:
            m["rule"] = "name"
        m["key"] = k
    for m in mentions:
        m["confidence"] = CONF[m["rule"]]
    return mentions, rev_kind, rev_parent


# ---------------------------------------------------------------------------------------------------------------
# The companies: name, kind, segment, parent, HQ state, footprint

LAB_KIND = "lab or hyperscaler"
KIND_ORDER = ["regulator", LAB_KIND, "OEM", "utility", "IPP", "lender or investor", "developer", "operator", "other"]
KINDS = set(KIND_ORDER)
UTILITY_OWNERSHIP = {"Investor Owned", "Cooperative", "Municipal", "Political Subdivision", "State", "Federal",
                     "Municipal Mktg Authority"}
GOV_WORDS = re.compile(r"\b(department|commission|agency|bureau|administration|office|service|survey|council|"
                       r"corps|governor|ministry|regulatory|secretary|endowment|foundation|institute|archives)\b", re.I)
GOV_ACRONYMS = {"nrc", "doe", "ferc", "epa", "cpuc", "puct", "blm", "boem", "irs", "ercot", "nerc"}
FINANCE_DEALS = {"debt", "equity_raise", "project_finance"}


def name_for(ms, canon=None):
    """A company's name: the reviewed aliases' canonical name, else EIA-861's newest name, else the NRC's parent
    field's, else the name its rows use most (the longest of the most used)."""
    for m in ms:
        if canon and m["key"] in canon:
            return canon[m["key"]]
    u = [m for m in ms if m["table"] == "eia861_utility_data"]
    if u:
        return max(u, key=lambda m: (m["date"], m["raw"]))["raw"]
    p = Counter(m["raw"] for m in ms if m["table"] == "nrc_power_reactors" and m["role"] == "parent")
    if p:
        return p.most_common(1)[0][0]
    c = Counter(m["raw"] for m in ms if m["role"] != "parent") or Counter(m["raw"] for m in ms)
    top = max(c.values())
    return sorted([n for n, v in c.items() if v == top], key=lambda n: (-len(n), n))[0]


def kind_for(ms, key, rev_kind):
    """(kind, basis): the first of KIND_ORDER that the company's rows show."""
    shows = {}
    if key in rev_kind and rev_kind[key] in KINDS:
        shows[rev_kind[key]] = "reviewed_aliases.csv"
    for m in ms:
        t, role = m["table"], m["role"]
        if t == "policy_actions":
            if GOV_WORDS.search(m["raw"]) or norm(m["raw"]) in GOV_ACRONYMS:
                shows.setdefault("regulator", "policy_actions agency")
        elif t == "eia861_utility_data" and m["extra"] in UTILITY_OWNERSHIP:
            shows.setdefault("utility", f"EIA-861 ownership {m['extra']}")
        elif t == "eia860_plants_annual" and m["extra"] == "Electric Utility":
            shows.setdefault("utility", "EIA-860 sector Electric Utility")
        elif t == "eia860_plants_annual" and m["extra"].startswith("IPP"):
            shows.setdefault("IPP", f"EIA-860 sector {m['extra']}")
        elif t == "energy_deals" and role == "buyer" and m["extra"] in FINANCE_DEALS:
            shows.setdefault("lender or investor", f"energy_deals buyer of {m['extra']}")
        elif t == "energy_deals" and role == "seller" and m["extra"] == "ppa":
            shows.setdefault("IPP", "energy_deals seller of a PPA")
        elif t == "nrc_power_reactors" and role in ("licensee", "operator"):
            shows.setdefault("operator", f"NRC {role}")
        elif t in ("ercot_interconnection_queue", "nyiso_interconnection_queue", "eia860m_planned_generators"):
            shows.setdefault("developer", f"{t} {role}")
        elif t.startswith("datacenter_") and role == "developer":
            shows.setdefault("developer", f"{t} developer")
        elif t.startswith("datacenter_") and role == "operator":
            shows.setdefault("operator", f"{t} operator")
        elif t == "utility_service_territories":
            shows.setdefault("utility", "EIA-861 service territory")
    if "utility" in shows and "regulator" in shows:
        shows.pop("regulator")                     # a federal power marketer (WAPA, BPA) is a utility
    for k in KIND_ORDER:
        if k in shows:
            return k, shows[k]
    return "other", "no rule"


def segment_for(mw_by, n, kind):
    """(segment, basis): the fuel or line with the most MW across the company's plants, plans, queue positions,
    facilities and deals; else its kind's line."""
    if mw_by:
        seg, v = max(mw_by.items(), key=lambda kv: (kv[1], kv[0]))
        if v > 0:
            return seg, "most MW"
    if n:
        seg, v = max(n.items(), key=lambda kv: (kv[1], kv[0]))
        return seg, "most rows"
    if kind == "utility":
        return "utility", "kind"
    if kind == "regulator":
        return "government", "kind"
    return "", ""


def build(mentions, rev_kind, rev_parent, nrc_pairs, lic, canon=None):
    """(companies, aliases, links) DataFrames. canon: {normalized name: the reviewed aliases' canonical name}."""
    by = defaultdict(list)
    for m in mentions:
        by[m["cid"]].append(m)
    key_of_cid = {cid: Counter(m["key"] for m in ms).most_common(1)[0][0] for cid, ms in by.items()}
    cid_of_key = {}
    for cid, ms in by.items():
        for m in ms:
            cid_of_key.setdefault(m["key"], cid)
    # parents: the NRC's (licensee -> parent) and the reviewed file's
    parent_of = {}
    for pair in nrc_pairs:
        if pair[0] != "alias":
            child, parent, row = pair
            c = cid_of_key.get(norm(child))
            if c:
                parent_of.setdefault(c, (parent, f"nrc_power_reactors {row}"))
    for m in mentions:                                   # "Blackstone's QTS": QTS, parent Blackstone
        if m.get("parent_hint"):
            parent_of.setdefault(m["cid"], (m["parent_hint"], f"{m['table']} {m['row_id']}: {m.get('written', '')}"))
    for k, p in rev_parent.items():
        c = cid_of_key.get(k)
        if c:
            parent_of[c] = (p, "reviewed_aliases.csv")
    comp_rows, link_rows, alias_rows = [], [], []
    for cid, ms in sorted(by.items()):
        name = name_for(ms, canon)
        kind, kind_basis = kind_for(ms, key_of_cid[cid], rev_kind)
        f = defaultdict(float)
        cnt = defaultdict(int)
        mw_by, n_by = defaultdict(float), defaultdict(int)
        deals, plants, planned, fac, queue, policy, reactors, owned_gens = set(), set(), set(), set(), set(), set(), set(), set()
        grids, states, dates = set(), Counter(), []
        hq = Counter()
        pub = 0
        for m in ms:
            mw = num(m["mw"])
            t = m["table"]
            if lic.get(t) == "public":
                pub += 1
            if m["date"]:
                dates.append(m["date"])
            for g in str(m["grid"]).split(";"):
                if g:
                    grids.add(g)
            if m["state"] and len(m["state"]) == 2 and t != "policy_actions":
                states[m["state"]] += 1
            if t == "energy_deals" and m["row_id"] not in deals:
                deals.add(m["row_id"])
                f["deals_mw"] += mw or 0
                f["deals_usd"] += num(m["usd"]) or 0
                if m["fuel"]:
                    n_by[m["fuel"]] += 1
                    mw_by[m["fuel"]] += mw or 0
            elif t == "eia860m_operating_generators":
                plants.add(m["extra"])
                f["plants_mw"] += mw or 0
                fu = m["fuel"] or "other"
                f[f"mw_{fu}"] += mw or 0
                mw_by[fu] += mw or 0
                cnt["generators"] += 1
            elif t == "eia860m_planned_generators":
                planned.add(m["extra"])
                f["planned_mw"] += mw or 0
                mw_by[m["fuel"] or "other"] += mw or 0
            elif t == "eia860_generator_owners":
                owned_gens.add(m["row_id"])
                f["owned_mw"] += mw or 0
                if m["extra"]:
                    hq[m["extra"]] += 1
            elif t == "datacenter_facilities" and m["role"] in ("operator", "developer") and m["row_id"] not in fac:
                fac.add(m["row_id"])
                f["facilities_mw"] += mw or 0
                mw_by["datacenters"] += mw or 0
            elif t in ("ercot_interconnection_queue", "nyiso_interconnection_queue"):
                if m["extra"] != "withdrawn" and m["extra"] != "Completed":
                    queue.add(m["row_id"])
                    f["queue_mw"] += mw or 0
                    mw_by[m["fuel"] or "other"] += mw or 0
            elif t == "policy_actions":
                policy.add(m["row_id"])
            elif t == "nrc_power_reactors" and m["role"] in ("licensee", "operator") and m["row_id"] not in reactors:
                reactors.add(m["row_id"])
                f["reactors_mw"] += mw or 0
        if kind == "regulator":
            mw_by.clear()
        seg, seg_basis = segment_for({k: v for k, v in mw_by.items() if k not in ("other", "")},
                                     {k: v for k, v in n_by.items() if k not in ("other", "")}, kind)
        parent, parent_basis = parent_of.get(cid, ("", ""))
        if parent and norm(parent) == key_of_cid[cid]:
            parent, parent_basis = "", ""
        anchor = cid.split("company:eia-")[1] if cid.startswith("company:eia-") else ""
        hq_state = hq.most_common(1)[0][0] if hq else ""
        tables = sorted({m["table"] for m in ms})
        footprint = f["plants_mw"] + f["planned_mw"] + f["queue_mw"] + f["facilities_mw"] + f["deals_mw"] + f["owned_mw"]
        row = dict(entity_id=cid, entity_type="company", name=name, geo="US", lat="", lon="",
                   capacity_mw=round(f["plants_mw"], 1) if plants else "", status="", status_date=max(dates) if dates else "",
                   operator="", source=SOURCE, source_url="", retrieved_at="", vintage="",
                   kind=kind, kind_basis=kind_basis, segment=seg, segment_basis=seg_basis,
                   parent=parent, parent_id=cid_of_key.get(norm(parent), "") if parent else "", parent_basis=parent_basis,
                   eia_utility_id=anchor, hq_state=hq_state,
                   hq_basis="EIA-860 owner address" if hq_state else "",
                   states=";".join(s for s, _ in states.most_common()), grids=";".join(sorted(grids)),
                   first_seen=min(dates) if dates else "", last_seen=max(dates) if dates else "",
                   n_deals=len(deals), deals_mw=round(f["deals_mw"], 1), deals_usd=round(f["deals_usd"]),
                   n_plants=len(plants), n_generators=cnt["generators"], plants_mw=round(f["plants_mw"], 1),
                   **{f"mw_{fu}": round(f[f"mw_{fu}"], 1) for fu in FUELS},
                   n_owned_generators=len(owned_gens), owned_mw=round(f["owned_mw"], 1),
                   n_planned_plants=len(planned), planned_mw=round(f["planned_mw"], 1),
                   n_facilities=len(fac), facilities_mw=round(f["facilities_mw"], 1),
                   n_queue=len(queue), queue_mw=round(f["queue_mw"], 1),
                   n_reactors=len(reactors), reactors_mw=round(f["reactors_mw"], 1),
                   n_policy_actions=len(policy), n_links=len(ms), n_public_links=pub,
                   n_names=len({m["raw"] for m in ms}), tables=";".join(tables),
                   footprint_mw=round(footprint, 1),
                   min_confidence=min(m["confidence"] for m in ms),
                   license="public" if pub == len(ms) else ("mixed" if pub else "internal"))
        comp_rows.append(row)
        seen_alias = {}
        for m in ms:
            h = hashlib.sha1(f"{m['table']}|{m['row_id']}|{m['role']}|{m['raw']}".encode()).hexdigest()[:16]
            link_rows.append(dict(entity_id=f"company_link:{h}", entity_type="company_link", name=name, geo="", lat="",
                                  lon="", capacity_mw=m["mw"], status="", status_date=m["date"], operator="",
                                  source=SOURCE, source_url="", retrieved_at="", vintage="",
                                  company_id=cid, input_table=m["table"], input_row=m["row_id"], role=m["role"],
                                  name_as_written=m["raw"], match_rule=m["rule"], confidence=m["confidence"],
                                  license=lic.get(m["table"], "internal"), mw=m["mw"], usd=m["usd"], date=m["date"],
                                  fuel=m["fuel"], state=m["state"], grid=m["grid"], detail=m["extra"]))
            ak = (m["raw"], m["table"], m["role"])
            if ak not in seen_alias:
                seen_alias[ak] = dict(first_row=m["row_id"], n=0, rule=m["rule"], conf=m["confidence"])
            seen_alias[ak]["n"] += 1
        for (raw, t, role), a in sorted(seen_alias.items()):
            h = hashlib.sha1(f"{cid}|{raw}|{t}|{role}".encode()).hexdigest()[:16]
            alias_rows.append(dict(entity_id=f"company_alias:{h}", entity_type="company_alias", name=raw, geo="",
                                   lat="", lon="", capacity_mw="", status="", status_date="", operator="",
                                   source=SOURCE, source_url="", retrieved_at="", vintage="",
                                   company_id=cid, company_name=name, alias=raw, normalized=norm(raw),
                                   input_table=t, role=role, first_row=a["first_row"], n_rows=a["n"],
                                   match_rule=a["rule"], confidence=a["conf"], license=lic.get(t, "internal")))
    comp = pd.DataFrame(comp_rows)
    comp = comp.sort_values(["footprint_mw", "n_links", "entity_id"], ascending=[False, False, True])
    return comp.reset_index(drop=True), pd.DataFrame(alias_rows), pd.DataFrame(link_rows)


# ---------------------------------------------------------------------------------------------------------------

def gather(out_dir=None):
    """(mentions, nrc_pairs, {table: (source_url, retrieved_at, vintage)}) from the held tables."""
    base = out_dir or ip.OUT_DIR
    t = {name: read_table(os.path.join(base, name + ".csv")) for name in INPUTS}
    op = t["eia860m_operating_generators"]
    nameplate = {(eia_id(r["plant_id"]), str(r["generator_id"]).strip()): num(r["nameplate_mw"])
                 for r in op[["plant_id", "generator_id", "nameplate_mw"]].to_dict("records")}
    ms = []
    ms += m_deals(t["energy_deals"])
    ms += m_datacenters(t["datacenter_projects"], "datacenter_projects")
    ms += m_datacenters(t["datacenter_facilities"], "datacenter_facilities")
    ms += m_860m(op, "eia860m_operating_generators")
    ms += m_860m(t["eia860m_planned_generators"], "eia860m_planned_generators")
    ms += m_plants(t["eia860_plants_annual"])
    ms += m_owners(t["eia860_generator_owners"], nameplate)
    ms += m_861(t["eia861_utility_data"])
    ms += m_territories(t["utility_service_territories"])
    ms += m_queue(t["ercot_interconnection_queue"], "ercot_interconnection_queue", "ERCOT")
    ms += m_queue(t["nyiso_interconnection_queue"], "nyiso_interconnection_queue", "NYISO")
    ms += m_policy(t["policy_actions"])
    nrc, pairs = m_nrc(t["nrc_power_reactors"])
    ms += nrc
    prov = {}
    for name, df in t.items():
        prov[name] = (len(df), df["retrieved_at"].max() if "retrieved_at" in df and len(df) else "")
    return ms, pairs, prov


def match_rates(links):
    """{table: {rows named, links by rule}} for the report and the header."""
    out = {}
    for t, g in links.groupby("input_table"):
        out[t] = dict(links=len(g), rows=g["input_row"].nunique(), companies=g["company_id"].nunique(),
                      **{r: int((g["match_rule"] == r).sum()) for r in CONF})
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="The company database: companies, their aliases and their links")
    ap.add_argument("--out-dir", help="a trial: the tables under this folder, not warehouse/output")
    ap.add_argument("--in-dir", help="read the input tables from this folder (a trial from a worktree reads the main "
                                     "checkout's warehouse/output); default this repository's warehouse/output")
    args = ap.parse_args(argv)
    in_dir = args.in_dir or ip.OUT_DIR
    if args.out_dir:
        raw_dir = ip.RAW_DIR
        ip.set_out_dir(args.out_dir)
        ip.RAW_DIR = raw_dir
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"companies_{run_id}.log"))
    try:
        ms, pairs, prov = gather(in_dir)
        reviewed = read_reviewed()
        lic = licenses(INPUTS)
        ms, rev_kind, rev_parent = resolve(ms, reviewed, pairs)
        canon = {norm(r.get("canonical") or r["alias"]): (r.get("canonical") or r["alias"]).strip() for r in reviewed}
        comp, aliases, links = build(ms, rev_kind, rev_parent, pairs, lic, canon)
        rates = match_rates(links)
        ret = f"{run_id[:4]}-{run_id[4:6]}-{run_id[6:8]}T{run_id[9:11]}:{run_id[11:13]}:{run_id[13:15]}Z"
        url = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/companies.md"
        for df in (comp, aliases, links):
            df["source_url"], df["retrieved_at"], df["vintage"] = url, ret, run_id[:8]
        internal = sorted(t for t, v in lic.items() if v == "internal")
        common = [
            f"Derived from: {'; '.join(INPUTS)}",
            f"Built by warehouse/derived/companies.py (sessions 3301 to 3303); method docs/methods/companies.md; reviewed aliases warehouse/companies/reviewed_aliases.csv ({len(reviewed)} rows, each with its evidence)",
            f"Retrieved: {run_id} (UTC), computed from the tables held; no request was made and no model was called.",
            f"Run log: warehouse/output/logs/companies_{run_id}.log",
            "Source: erw:companies, the ERW's resolution of the names in its own tables (each input's source in its own header).",
            f"License: public (every input is public in coverage). Rows from inputs whose publisher asks for permission ({', '.join(internal)}: license_status.csv) carry license internal in company_links and company_aliases, are left out of public downloads, and the company_directory columns built from them (n_deals, deals_mw, deals_usd, n_facilities, facilities_mw, and queue figures from NYISO) are internal figures.",
            "Inputs: " + "; ".join(f"{t} {n:,} rows (retrieved {r})" for t, (n, r) in prov.items()),
        ]
        rate_line = "Match by input (links: eia_id, reviewed_alias, anchored_name, name, company_word): " + "; ".join(
            f"{t} {v['links']:,} ({v['eia_id']:,}, {v['reviewed_alias']:,}, {v['anchored_name']:,}, {v['name']:,}, {v['company_word']:,})"
            for t, v in sorted(rates.items()))
        h1 = [f"Energy Research Warehouse (ERW): the company database (platform tool 10), every company named in {len(INPUTS)} held tables, one row a company (session 3302)",
              "Shape: entities (docs/datastandard.md v0), entity_type company. entity_id company:eia-<EIA utility id> where the company has one, else company:<normalized name>; kind one of regulator, lab or hyperscaler, OEM, utility, IPP, lender or investor, developer, operator, other (the first its rows show, kind_basis says which row); segment the fuel or line with the most MW (segment_basis); parent a second field from the NRC and the reviewed aliases only; hq_state from EIA-860's owner address only; first_seen and last_seen the earliest and latest date its rows state; MW are nameplate (EIA-860M), as stated (deals, facilities, queue); owned_mw nameplate times the percent owned; footprint_mw the sum of plants_mw, owned_mw, planned_mw, queue_mw, facilities_mw and deals_mw, a sort key only (a plant both operated and owned counts twice).",
              f"Rows: {len(comp):,} companies from {len(links):,} links; {int((comp['eia_utility_id'] != '').sum()):,} with an EIA utility id.",
              rate_line] + common
        h2 = [f"Energy Research Warehouse (ERW): every name a company of the company database goes by, by input table and role (session 3302)",
              "Shape: entities (docs/datastandard.md v0), entity_type company_alias. One row a (company, name as written, table, role); first_row the first input row with it; n_rows the rows; match_rule and confidence as in company_links; license the input's.",
              f"Rows: {len(aliases):,} names of {aliases['company_id'].nunique():,} companies."] + common
        h3 = [f"Energy Research Warehouse (ERW): the company database's links, one row a company named in a row of an input table (session 3302)",
              "Shape: entities (docs/datastandard.md v0), entity_type company_link. company_id the company; input_table and input_row the row (its entity_id or event_id); role what the company is in it; name_as_written the row's own words; match_rule eia_id (1.0), reviewed_alias (0.95), anchored_name (0.9), name (0.85), company_word (0.7), the confidence; license the input's (internal where its publisher asks for permission); mw, usd, date, fuel, state and grid as the row states them (owner rows: nameplate times percent owned; detail the deal type, status, sector, ownership or county).",
              f"Rows: {len(links):,} links of {links['company_id'].nunique():,} companies; {int((links['license'] == 'public').sum()):,} public, {int((links['license'] != 'public').sum()):,} internal."] + common
        comp_extra = [c for c in comp.columns if c not in ENTITY_COLS]
        alias_extra = [c for c in aliases.columns if c not in ENTITY_COLS]
        link_extra = [c for c in links.columns if c not in ENTITY_COLS]
        ip.write_snapshot(comp, NAME, h1, log, cols=ENTITY_COLS + comp_extra)
        ip.write_snapshot(aliases, ALIASES, h2, log, cols=ENTITY_COLS + alias_extra)
        ip.write_snapshot(links, LINKS, h3, log, cols=ENTITY_COLS + link_extra)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Energy Research Warehouse (ERW), derived",
                                    report="The company database: every company named in the warehouse's tables, its names and its rows (docs/methods/companies.md)",
                                    report_url=url, document_list="docs/methods/companies.md", license="public",
                                    tables=[NAME, ALIASES, LINKS])])
        for t, v in sorted(rates.items()):
            log(f"{t}: {v}")
        print(f"{NAME}: {len(comp):,} companies; {ALIASES}: {len(aliases):,}; {LINKS}: {len(links):,}")
        rc = 0
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED, no output file written:\n{tb}")
        print(f"companies FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        rc = 1
    log.close()
    return rc


if __name__ == "__main__":
    sys.exit(main())
