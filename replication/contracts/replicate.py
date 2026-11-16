#!/usr/bin/env python3
"""ERW, the contracts page (/contracts, "Where power contracts are being struck", and its four views): the replication
a reader with the internal tables can run (session 7501, chain 304).

Written from the method note (docs/methods/contracts.md) and the two source tables alone, ferc_eqr_contracts and
ferc_eqr_contracts_history, not from the page's code and not from the six derived tables the page's figures come
through: every count, sum, rank and list the four views show is computed again here, in this file's own words, from the
rows as FERC's filers filed them, and set beside the figure the page itself draws on the same rows
(site/scripts/contracts-figures.mjs calls the page's own code and reads the HTML). A difference is inside the tolerance
when it is at most half the last digit the page shows.

    python replication/contracts/copy_rows.py        # what the page is served, into rows/ (not in git)
    python replication/contracts/replicate.py        # N of N, or each difference named
    python replication/contracts/replicate.py --write       # also writes page_figures.json and page_figures.csv
    python replication/contracts/replicate.py --headline    # only the do-file's lines (replicate.do)

    --tables DIR    the folder of tables (default: this checkout's warehouse/output, else the main checkout's)
    --rows DIR      the folder copy_rows.py wrote (default: this folder's rows/)
    --page FILE     the page's figures as a file (the JSON the node script prints) instead of running node
    --no-near       skip the near-spelling pairs (the slowest step); the count of doubtful pairs is then not compared

The eight tables are internal (docs/methods/ferc_eqr_contracts.md, "License"): no row, no party's name and no party's
own figure is printed or written by this file. A figure of one party (a cell of a ranking) and a party's name are
compared and counted, and the written files say only whether each agreed. Exit 0 when every figure is inside its
tolerance or its difference is one this file names (NAMED), 1 when another differs or a key is on one side only, 2
when the inputs cannot be read. Standard library only.
"""
import argparse
import csv
import datetime as dt
import difflib
import json
import os
import re
import shutil
import subprocess
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SITE = os.path.join(ROOT, "site")

# ---- the note, section 2: the constants
EVENT_DAYS = 1000            # the live set keeps the rows executed in the 1,000 days before a load
SHOWN = 400                  # the list draws the first 400 rows of a quarter
QUARTERS_LISTED = 12
BAS_LISTED = 14
TOP = 25
THREE = {"ENERGY": "energy", "CAPACITY": "capacity", "TOLLING ENERGY": "tolling"}
PRODUCT_GROUPS = {"power": set(THREE), "energy": {"ENERGY"}, "capacity": {"CAPACITY"}, "tolling": {"TOLLING ENERGY"}, "all": None}

# ---- the note, section 5: the six rules of a buyer's name
ABBREVIATIONS = {"CORPORATION": "CORP", "INCORPORATED": "INC", "COMPANY": "CO", "LIMITED": "LTD", "COOP": "COOPERATIVE", "ASSN": "ASSOCIATION",
                 "ASSOC": "ASSOCIATION", "ELEC": "ELECTRIC", "DEPT": "DEPARTMENT", "AUTH": "AUTHORITY", "MGMT": "MANAGEMENT", "SVC": "SERVICE",
                 "SVCS": "SERVICES", "INTL": "INTERNATIONAL", "NATL": "NATIONAL", "PWR": "POWER", "MKTG": "MARKETING", "TRANSM": "TRANSMISSION"}
MUNICIPAL = {"CITY", "TOWN", "VILLAGE", "COUNTY", "BOROUGH"}
LEGAL_FORMS = {"LLC", "LLP", "LP", "INC", "CORP", "CO", "LTD", "PLC", "NA"}
LONG_FORMS = [("LIMITED LIABILITY COMPANY", "LLC"), ("LTD LIABILITY CO", "LLC"), ("LIMITED PARTNERSHIP", "LP"), ("LTD PARTNERSHIP", "LP"),
              ("L L C", "LLC"), ("L L P", "LLP"), ("L P", "LP"), ("P L C", "PLC"), ("N A", "NA")]
CLAUSE = re.compile(r"\s+(D/B/A|DBA|F/K/A|FKA|AS AGENT FOR|AS AGNT FOR|A/K/A)\s+.*$|\s*\([^)]*\)\s*$", re.I)
NUMERAL = re.compile(r"^(\d+|[IVX]+|[A-H])$")

# ---- the note, section 7: a price from the words
AMOUNT = re.compile(r"\$\s*([0-9][0-9,]*(?:\.[0-9]+)?|\.[0-9]+)")
PERIODS = {"MO": "(?:mo|mos|month|mth)", "DAY": "(?:day)", "YR": "(?:yr|year)", "WK": "(?:wk|week)"}
UNIT_WORDS = [("$/MWH", "(?:mwh|mw-h|megawatt[- ]?hours?)"), ("$/KWH", "(?:kwh|kw-h|kilowatt[- ]?hours?)")]
for _p, _long in (("KW", "kilowatt"), ("MW", "megawatt")):
    for _k, _t in PERIODS.items():
        UNIT_WORDS.append((f"$/{_p}-{_k}", rf"(?:{_p.lower()}|{_long})\s*[-/ ]\s*{_t}"))
UNIT_AT_ONCE = [(name, re.compile(r"\s*(?:/|per)\s*" + pat + r"(?![a-z])", re.I)) for name, pat in UNIT_WORDS]
CONDITION = re.compile(
    r"escalat|adjust|index|\bcpi\b|formula|\btiers?\b|excess|greater|less than|up to|\babove\b|\bbelow\b|\bplus\b|\bminus\b|\btimes\b|multipl|[+*%]|percent|"
    r"\blmp\b|market|peak|\b(?:19|20)\d\d\b|\d{1,2}/\d{1,2}/\d{2,4}|thru|through|deposit|start|\bor\b|higher of|lower of|lesser|not to exceed|maximum|minimum|"
    r"\bx\b|\bif\b|more than|no case|agreed|revis|factor|unless|\buntil\b|credit|\bcap\b|ceiling|floor|discount|penalt|estimat", re.I)
A_NUMBER = re.compile(r"(?<![A-Za-z$.\d])([0-9][0-9,]*(?:\.[0-9]+)?)(?![\d])")
A_QUANTITY = re.compile(r"\s*-?\s*(?:mw|kw|mwh|kwh|megawatts?|kilowatts?)(?![a-z/-])", re.I)
REASONS = ["no_dollar_amount", "several_amounts", "no_unit", "conditional", "other_numbers", "units_disagree"]
STORAGE_WORD = re.compile(r"storage|batter|\bbess\b", re.I)

# A difference this file names instead of failing on: the key (or a pattern of keys), and why the two sides differ.
NAMED = [
    (re.compile(r"^mw\|(energy|capacity|tolling)\|mw\|(buyer|seller)\|\d+\|place$"),
     "the megawatts view's 'Place by contracts' is ranked by contracts then name; the view it points to ranks by contracts, then rows, then name. "
     "Parties tied on contracts stand at different places in the two (faults row 7, the data machine's builder)."),
]


def tables_dir(given):
    for d in ([given] if given else []) + [os.path.join(ROOT, "warehouse", "output"), os.path.join(os.path.dirname(ROOT), "erw", "warehouse", "output")]:
        if d and os.path.exists(os.path.join(d, "ferc_eqr_contracts.csv")):
            return d
    return None


def rows_of(path):
    """Each row of a table as a dict, one at a time. A table's first lines are comments that begin with '#'."""
    csv.field_size_limit(1 << 30)
    with open(path, encoding="utf-8", newline="") as f:
        pos = f.tell()
        line = f.readline()
        while line.startswith("#"):
            pos = f.tell()
            line = f.readline()
        f.seek(pos)
        yield from csv.DictReader(f)


def quarter_of(day):
    return f"{day[:4]}-Q{(int(day[5:7]) - 1) // 3 + 1}"


def ferc_day(v):
    """'20250723' as FERC files a date, to a date; None for anything else. A month's day past its end runs into the next
    month, as the page's browser engine reads it (the note, section 3)."""
    s = (v or "").strip()
    if not re.fullmatch(r"\d{8}", s):
        return None
    y, m, d = int(s[:4]), int(s[4:6]), int(s[6:])
    if not (1 <= m <= 12 and 1 <= d <= 31) or y < 1:
        return None
    try:
        return dt.date(y, m, 1) + dt.timedelta(days=d - 1)
    except (ValueError, OverflowError):
        return None


class Row:
    """One row of ferc_eqr_contracts, the columns the page's figures are read from (the note, section 1)."""
    __slots__ = ("id", "day", "in_force", "product", "company", "contract", "seller", "buyer", "affiliate", "agreement", "quantity", "units", "rate",
                 "rate_units", "words", "ba", "start", "end", "tariff", "product_fields", "filed_for")

    def __init__(self, r):
        self.id, self.day = r["event_id"], r["event_date"][:10]
        self.in_force = r["x_actual_termination_date"].strip() == ""
        self.product = r["x_product_name"].strip().upper()
        self.company, self.contract = r["x_company_id"], r["x_company_id"] + "|" + r["x_contract_unique_id"]
        self.seller, self.buyer = r["x_seller_company_name"], r["x_customer_company_name"]
        self.affiliate = r["x_contract_affiliate"].strip().upper() == "Y"
        self.agreement = r["x_contract_service_agreement_id"]
        self.quantity, self.units = r["x_quantity"], r["x_units"]
        self.rate, self.rate_units, self.words = r["x_rate"], r["x_rate_units"], r["x_rate_description"]
        self.ba = r["x_point_of_delivery_balancing_authority"]
        self.start, self.end = r["x_commencement_date_of_contract_term"], r["x_contract_termination_date"]
        self.tariff, self.filed_for = r["x_ferc_tariff_reference"], r["x_quarter"]
        self.product_fields = " | ".join(r[c] for c in ("x_product_name", "x_product_type_name", "x_class_name", "x_term_name", "x_increment_name"))


def authority(v):
    """A delivery balancing authority as the panel names it (the note, section 3): FERC's code trimmed and in capitals,
    'not stated' for a row that files none."""
    return v.strip().upper() or "not stated"


def megawatts(quantity, units):
    """The megawatts a row states (the note, section 6): the quantity when its units are MW, a thousandth of it when kW;
    a quantity of zero, or in any other unit, is none."""
    u = (units or "").strip().upper()
    try:
        q = float(str(quantity).replace(",", ""))
    except ValueError:
        return None
    if not q > 0 or u not in ("MW", "KW"):
        return None
    return q if u == "MW" else q / 1000.0


def filed_mw(r):
    """The megawatts 'as filed' of the largest view (the note, section 5): the quantity when the units are exactly 'MW',
    any size, zero included. No ceiling, no kW."""
    if r.units != "MW" or r.quantity.strip() == "":
        return None
    try:
        return float(r.quantity)
    except ValueError:
        return None


def name_key(name):
    """A buyer's name after rules 1 to 5 (the note, section 5)."""
    s = " ".join(name.upper().split())
    s = s.replace("&", " AND ")
    s = re.sub(r"[.,'\"`()\[\]]", "", s)
    words = re.sub(r"[-/]", " ", s).split()
    if len(words) > 1 and words[0] == "THE":
        words = words[1:]
    held_back = bool(words) and (words[0] in MUNICIPAL or "OF" in words)
    words = [w if (w == "CO" and i == len(words) - 1 and held_back) else ABBREVIATIONS.get(w, w) for i, w in enumerate(words)]
    for long, short in LONG_FORMS:
        form = long.split()
        if len(words) > len(form) and words[-len(form):] == form:
            words = words[:-len(form)] + [short]
            break
    return " ".join(words)


def stem_form(key):
    w = key.split()
    if len(w) > 1 and w[-1] in LEGAL_FORMS and not (w[-1] == "CO" and (w[0] in MUNICIPAL or "OF" in w)):
        return " ".join(w[:-1]), w[-1]
    return key, ""


def buyer_groups(counts, near=True):
    """{name as filed: rows} to {name as filed: group key}, the name each group is shown under, and the doubtful pairs by
    reason (the note, section 5)."""
    key = {raw: name_key(raw) for raw in counts}
    forms = defaultdict(set)
    for k in set(key.values()):
        stem, form = stem_form(k)
        forms[stem].add(form)
    with_form, doubtful = {}, Counter()
    seen = set()
    for stem, fs in forms.items():
        real = sorted(f for f in fs if f)
        if "" in fs and len(real) == 1:
            with_form[stem] = f"{stem} {real[0]}"                 # rule 6: a name filed with and without its one legal form
        if len(real) > 1:
            names = [f"{stem} {f}" for f in real] + ([stem] if "" in fs else [])
            for i in range(len(names)):
                for j in range(i + 1, len(names)):
                    seen.add(tuple(sorted((names[i], names[j]))))
                    doubtful["different_legal_form"] += 1
    group = {raw: with_form.get(k, k) for raw, k in key.items()}
    keys = set(group.values())
    for raw, g in group.items():
        base = CLAUSE.sub("", raw)
        if base != raw and base.strip():
            bk = name_key(base)
            bk = with_form.get(bk, bk)
            pair = tuple(sorted((g, bk)))
            if bk in keys and bk != g and pair not in seen:
                seen.add(pair)
                doubtful["extra_clause"] += 1
    if near:
        blocks = defaultdict(list)
        for g in sorted(keys):
            if len(g) >= 12:
                blocks[g[:4]].append(g)
        for block in blocks.values():
            for i, a in enumerate(block):
                for b in block[i + 1:]:
                    if abs(len(a) - len(b)) > 3 or tuple(sorted((a, b))) in seen:
                        continue
                    m = difflib.SequenceMatcher(None, a, b, autojunk=False)
                    if m.real_quick_ratio() < 0.94 or m.quick_ratio() < 0.94 or m.ratio() < 0.94:
                        continue
                    odd = set(a.split()) ^ set(b.split())
                    if odd and all(NUMERAL.match(w) for w in odd):
                        continue
                    if stem_form(a)[0] == stem_form(b)[0]:
                        continue
                    seen.add(tuple(sorted((a, b))))
                    doubtful["near_spelling"] += 1
    best = {}
    for raw, g in group.items():
        if g not in best or counts[raw] > counts[best[g]] or (counts[raw] == counts[best[g]] and raw < best[g]):
            best[g] = raw
    return group, best, doubtful


def price_in_words(text, filed_units):
    """A price read from a rate filed as words: (value, unit, '') or (None, '', the first test failed)."""
    t = " ".join((text or "").split())
    found = list(AMOUNT.finditer(t))
    if not found:
        return None, "", "no_dollar_amount"
    if len(found) > 1:
        return None, "", "several_amounts"
    m = found[0]
    unit, end = "", m.end()
    for name, pat in UNIT_AT_ONCE:
        u = pat.match(t, m.end())
        if u:
            unit, end = name, u.end()
            break
    if not unit:
        return None, "", "no_unit"
    rest = t[:m.start()] + " " + t[end:]
    if CONDITION.search(rest):
        return None, "", "conditional"
    if any(not A_QUANTITY.match(rest, n.end()) for n in A_NUMBER.finditer(rest)):
        return None, "", "other_numbers"
    filed = (filed_units or "").strip().upper()
    if filed and filed != unit:
        return None, "", "units_disagree"
    return float(m.group(1).replace(",", "")), unit, ""


def is_number(v):
    try:
        x = float(v)
    except ValueError:
        return False
    return x == x


def ranked(parties, order):
    return sorted(parties, key=order)


def compute(rows, history, ceiling, load_day, today, near=True):
    """Every figure of the four views, by its key, and the words (names, quarters) by theirs."""
    F, W = {}, {}
    cutoff = (dt.date.fromisoformat(load_day) - dt.timedelta(days=EVENT_DAYS)).isoformat()
    filed_for = sorted({r.filed_for for r in rows})[-1].replace("_", "-")          # the quarter the filings were made for
    live = [r for r in rows if r.day >= cutoff]

    # ---- view 1: the contracts by the quarter signed (the note, section 3)
    by_q = defaultdict(list)
    for r in live:
        by_q[quarter_of(r.day)].append(r)
    listed = sorted((q for q in by_q if q <= filed_for), reverse=True)[:QUARTERS_LISTED]
    later = sorted((q for q in by_q if q > filed_for), reverse=True)
    W["quarter|listed"], W["quarter|default"] = " ".join(listed), listed[0].replace("-", " ")
    W["panel|later_last"], W["panel|filed_for"] = later[0].replace("-", " ") if later else "", filed_for.replace("-", " ")
    W["panel|first"], W["panel|last"] = min(r.day for r in live), max(r.day for r in live)
    W["odd_address|quarter"] = W["quarter|default"]
    for q in listed:
        F[f"panel|quarter_rows|{q}"] = len(by_q[q])
    F["panel|later_rows"] = sum(len(by_q[q]) for q in later)
    with_number = sum(1 for r in live if r.rate.strip() != "")
    F["limits|rows_held"] = F["cannot_see|rows_held"] = len(live)
    F["limits|unpriced"] = len(live) - with_number                 # the rows that file no number
    F["check|limits|rows_that_file_words_and_no_number"] = sum(1 for r in live if r.rate.strip() == "" and r.words.strip() != "")
    F["cannot_see|ercot_rows"] = sum(1 for r in live if authority(r.ba) == "ERCO")
    oldest = listed[-1]
    start = f"{oldest[:4]}-{3 * (int(oldest[-1]) - 1) + 1:02d}-01"
    F["panel|oldest_quarter_whole_rows"] = sum(1 for r in rows if quarter_of(r.day) == oldest)      # the same quarter in the whole file
    W["panel|oldest_quarter_from"] = W["panel|first"] if W["panel|first"] > start else ""

    def page(q, slug, ba):
        group = PRODUCT_GROUPS[slug]
        every = sorted(by_q[q], key=lambda r: (r.seller, r.id))
        every.sort(key=lambda r: r.day, reverse=True)
        of_product = [r for r in every if group is None or r.product in group]
        shown = [r for r in of_product if ba is None or authority(r.ba) == ba]
        k = f"quarter|{q}|{slug}|{ba or 'every'}"
        F[f"{k}|rows"] = F[f"{k}|headline_rows"] = len(shown)
        F[f"{k}|agreements"] = len({(r.seller, r.agreement) for r in shown})
        F[f"{k}|sellers"] = len({r.seller for r in shown if r.seller})
        F[f"{k}|buyers"] = len({r.buyer for r in shown if r.buyer})
        F[f"{k}|priced"] = F[f"{k}|headline_priced"] = sum(1 for r in shown if r.rate.strip() != "")
        F[f"{k}|headline_unpriced"] = len(shown) - F[f"{k}|priced"]
        F[f"{k}|headline_affiliate"] = sum(1 for r in shown if r.affiliate)
        drawn = shown[:SHOWN]
        F[f"{k}|table_rows_drawn"] = len(drawn)
        F[f"{k}|as_filed_marks"] = sum(1 for r in drawn if r.day > today)
        years = []
        for r in drawn:
            a, b = ferc_day(r.start), ferc_day(r.end)
            if a and b and b >= a:
                years.append((b - a).days / 365.25)
        F[f"{k}|terms_in_years_drawn"] = len(years)
        if years:
            F[f"{k}|longest_term_years_drawn"] = max(years)
        return of_product

    for q in listed:
        for slug in PRODUCT_GROUPS:
            of_product = page(q, slug, None)
            bas = Counter(authority(r.ba) for r in of_product)
            order = sorted(bas.items(), key=lambda x: (-x[1], x[0]))[:BAS_LISTED]
            F[f"panel|ba_listed|{q}|{slug}"] = len(order)
            for i, (ba, n) in enumerate(order, 1):
                F[f"panel|ba_rows|{q}|{slug}|{i}"] = n
                W[f"panel|ba_name|{q}|{slug}|{i}"] = ba
                if q == listed[0] and slug == "power":
                    page(q, slug, ba)

    # ---- view 2: the largest buyers and sellers (the note, section 5)
    name_rows = Counter(r.buyer for r in rows)
    group, shown_as, doubtful = buyer_groups(name_rows, near)
    sizes = Counter(group.values())
    names = {"filed": len(name_rows), "after": len(sizes), "merged": sum(1 for raw in group if sizes[group[raw]] > 1), "doubtful": sum(doubtful.values())}
    book = [r for r in rows if r.in_force and r.product in THREE]
    seller_spellings = defaultdict(Counter)
    for r in book:
        seller_spellings[r.company][r.seller] += 1
    seller_name = {c: s.most_common(1)[0][0] for c, s in seller_spellings.items()}
    largest_rank = {}
    for slug in ("energy", "capacity", "tolling"):
        of = [r for r in book if THREE[r.product] == slug]
        sides = {"buyer": defaultdict(list), "seller": defaultdict(list)}
        for r in of:
            sides["buyer"][shown_as[group[r.buyer]]].append(r)
            sides["seller"][r.company].append(r)
        totals = {}
        for role, parties in sides.items():
            out = []
            for party, rs in parties.items():
                mw = [x for x in (filed_mw(r) for r in rs) if x is not None]
                out.append({"key": party, "name": party if role == "buyer" else seller_name[party], "contracts": len({r.contract for r in rs}), "rows": len(rs),
                            "counterparties": len({r.company for r in rs} if role == "buyer" else {shown_as[group[r.buyer]] for r in rs}),
                            "mw": round(sum(mw), 1), "rows_with_mw": len(mw), "over": sum(1 for x in mw if x > ceiling)})
            out.sort(key=lambda p: (-p["contracts"], -p["rows"], p["name"]))
            totals[role] = out
            largest_rank[(role, slug)] = {p["key"]: i for i, p in enumerate(out, 1)}
        k = f"largest|{slug}"
        F[f"{k}|contracts"] = sum(p["contracts"] for p in totals["buyer"])
        F[f"{k}|product_rows"] = len(of)
        F[f"{k}|buyers"], F[f"{k}|sellers"] = len(totals["buyer"]), len(totals["seller"])
        F[f"{k}|top|buyer"], F[f"{k}|top|seller"] = totals["buyer"][0]["contracts"], totals["seller"][0]["contracts"]
        F[f"{k}|listed_top"] = TOP
        F[f"{k}|names|filed"], F[f"{k}|names|after"], F[f"{k}|names|merged"] = names["filed"], names["after"], names["merged"]
        if near:
            F[f"{k}|names|doubtful"] = names["doubtful"]
        none = 0
        for role in ("buyer", "seller"):
            for i, p in enumerate(totals[role][:TOP], 1):
                W[f"{k}|party|{role}|{i}"] = p["name"]
                F[f"{k}|{role}|{i}|contracts"], F[f"{k}|{role}|{i}|rows"] = p["contracts"], p["rows"]
                F[f"{k}|{role}|{i}|counterparties"], F[f"{k}|{role}|{i}|rows_with_mw"] = p["counterparties"], p["rows_with_mw"]
                if p["rows_with_mw"] > 0:
                    F[f"{k}|{role}|{i}|mw"] = p["mw"]
                else:
                    none += 1
        F[f"{k}|cells_none_filed"] = none
        F[f"check|largest|{slug}|cells_with_a_row_over_the_ceiling"] = sum(1 for role in totals for p in totals[role][:TOP] if p["over"])
        W[f"{k}|quarter"] = filed_for.replace("-", " ")

    # ---- view 3: ranked by megawatts stated (the note, section 6)
    F["check|rows_stating_megawatts"] = sum(1 for r in rows if megawatts(r.quantity, r.units) is not None)
    rows_over = sum(1 for r in rows if (megawatts(r.quantity, r.units) or 0) > ceiling)
    for slug in ("energy", "capacity", "tolling"):
        of = [r for r in book if THREE[r.product] == slug]
        k = f"mw|{slug}"
        contracts = {r.contract for r in of}
        stated = defaultdict(float)
        over = set()
        for r in of:
            x = megawatts(r.quantity, r.units)
            if x is None:
                continue
            if x > ceiling:
                over.add(r.contract)
            else:
                stated[r.contract] = max(stated[r.contract], x)
        F[f"{k}|mw|contracts"] = F[f"{k}|in_force_in_headline"] = len(contracts)
        F[f"{k}|mw|with"], F[f"{k}|mw|over"] = len(stated), len(over)
        F[f"{k}|ceiling"], F[f"{k}|rows_over_every_product"] = ceiling, rows_over
        W[f"{k}|quarter"] = filed_for.replace("-", " ")
        for role in ("buyer", "seller"):
            of_party = defaultdict(set)
            for r in of:
                of_party[shown_as[group[r.buyer]] if role == "buyer" else r.company].add(r.contract)
            out = []
            name_of = (lambda x: x) if role == "buyer" else (lambda x: seller_name[x])
            by_name = {x: i for i, x in enumerate(sorted(of_party, key=lambda x: (-len(of_party[x]), name_of(x))), 1)}   # by contracts, then name: not the largest view's order
            for party, cs in of_party.items():
                have = [stated[c] for c in cs if c in stated]
                if have:
                    out.append({"key": party, "name": party if role == "buyer" else seller_name[party], "mw": round(sum(have), 3), "with": len(have), "contracts": len(cs)})
            out.sort(key=lambda p: (-p["mw"], p["name"]))
            F[f"{k}|mw|{role}s"] = len(out)
            if role == "buyer":
                F[f"{k}|mw|total"] = round(sum(p["mw"] for p in out), 1)
            for i, p in enumerate(out[:TOP], 1):
                W[f"{k}|party|mw|{role}|{i}"] = p["name"]
                F[f"{k}|mw|{role}|{i}|mw"], F[f"{k}|mw|{role}|{i}|with"], F[f"{k}|mw|{role}|{i}|contracts"] = p["mw"], p["with"], p["contracts"]
                F[f"{k}|mw|{role}|{i}|place"] = largest_rank[(role, slug)][p["key"]]        # its place in the largest view
                F[f"check|by_name|{k}|mw|{role}|{i}|place"] = by_name[p["key"]]

    # ---- view 4: what the filings state (the note, section 7)
    k = "terms"
    number = sum(1 for r in rows if is_number(r.rate)) if rows else 0
    words_only = [r for r in rows if not is_number(r.rate) and r.words.strip() != ""]
    F[f"{k}|terms|rows"] = F[f"{k}|buyers_of_rows"] = len(rows)
    F[f"{k}|terms|number"] = F[f"{k}|headline_filed_number"] = number
    F[f"{k}|terms|words"] = len(words_only)
    F[f"{k}|headline_neither"] = len(rows) - number - len(words_only)
    why, units, per_mwh = Counter(), Counter(), 0
    for r in words_only:
        value, unit, reason = price_in_words(r.words, r.rate_units)
        if value is None:
            why[reason] += 1
        else:
            units[unit] += 1
            per_mwh += unit in ("$/MWH", "$/KWH")
    read = sum(units.values())
    F[f"{k}|terms|read"] = F[f"{k}|unread|read"] = read
    F[f"{k}|terms|unread"] = len(words_only) - read
    F[f"{k}|read_usd_per_mwh"] = per_mwh
    for reason in REASONS:
        F[f"{k}|unread|{reason}"] = why[reason]
    for unit, n in units.items():
        F[f"{k}|read_by_unit|{unit}"] = n
    tolling = [r for r in rows if r.product == "TOLLING ENERGY"]
    F[f"{k}|tag|tolling_rows"], F[f"{k}|tag|tolling_contracts"] = len(tolling), len({r.contract for r in tolling})
    F["check|tolling_contracts_in_force"] = len({r.contract for r in tolling if r.in_force})
    F[f"{k}|tag|storage_rows"] = sum(1 for r in rows if r.product != "TOLLING ENERGY" and STORAGE_WORD.search(r.product_fields))
    fields = {"seller_name": lambda r: r.seller, "rate_description": lambda r: r.words, "agreement_id": lambda r: r.agreement, "tariff_reference": lambda r: r.tariff}
    for f, get in fields.items():
        F[f"{k}|tag|{f}"] = sum(1 for r in rows if STORAGE_WORD.search(get(r)))
    F[f"{k}|tag|elsewhere"] = sum(1 for r in rows if any(STORAGE_WORD.search(get(r)) for get in fields.values()))
    F[f"{k}|buyers|merged"] = sum(1 for r in rows if sizes[group[r.buyer]] > 1)
    if near:
        F[f"{k}|buyers|doubtful"] = names["doubtful"]
    W[f"{k}|quarter"] = filed_for.replace("-", " ")
    # contracts new and gone: each quarter's contracts in force, by product, against the quarter before
    sets = dict(history)
    newest = filed_for.replace("-", "_")
    sets[newest] = {"all": {r.contract for r in rows if r.in_force}, **{slug: {r.contract for r in book if THREE[r.product] == slug} for slug in ("energy", "capacity", "tolling")}}
    quarters = sorted(sets)
    for i, q in enumerate(quarters):
        for p in ("all", "energy", "capacity", "tolling"):
            F[f"{k}|change|{q}|{p}|in_force"] = len(sets[q][p])
            if i and (int(q[:4]) * 4 + int(q[-1])) - (int(quarters[i - 1][:4]) * 4 + int(quarters[i - 1][-1])) == 1:
                was, now = sets[quarters[i - 1]][p], sets[q][p]
                F[f"{k}|change|{q}|{p}|contracts_new"], F[f"{k}|change|{q}|{p}|contracts_gone"], F[f"{k}|change|{q}|{p}|contracts_kept"] = len(now - was), len(was - now), len(now & was)

    # ---- a server that holds no token (what a visitor's request can ever reach): no figure, no row
    F["no_token|figures_drawn"] = F["no_token|table_rows_drawn"] = 0
    companies = {q: len(s["companies"]) for q, s in history.items()}
    companies[newest] = len({r.company for r in rows})
    return F, W, {"cutoff": cutoff, "filed_for": filed_for, "live": len(live), "doubtful": dict(doubtful), "companies": companies}


def read_history(path):
    """{quarter: {product or all: the contracts in force}} of the quarters before the newest."""
    sets = defaultdict(lambda: defaultdict(set))
    for r in rows_of(path):
        sets[r["x_quarter"]]["companies"].add(r["x_company_id"])
        if r["x_actual_termination_date"].strip() != "":
            continue
        c = r["x_company_id"] + "|" + r["x_contract_unique_id"]
        sets[r["x_quarter"]]["all"].add(c)
        slug = THREE.get(r["x_product_name"].strip().upper())
        if slug:
            sets[r["x_quarter"]][slug].add(c)
    return {q: {p: s.get(p, set()) for p in ("all", "energy", "capacity", "tolling", "companies")} for q, s in sets.items()}


def largest_station(path):
    """The megawatts of the largest power station operating in the United States: EIA's inventory of operating
    generators, nameplate summed by plant (the note, section 6)."""
    mw = defaultdict(float)
    for r in rows_of(path):
        try:
            mw[r["plant_id"]] += float(r["capacity_mw"])
        except ValueError:
            pass
    return max(mw.values())


def tolerance(key):
    if key.endswith("|mw") or key.endswith("|mw|total"):
        return 0.05            # megawatts are shown to one decimal
    if key.endswith("longest_term_years_drawn"):
        return 0.05
    return 0.5


def internal(key):
    """A key that names one party's own figure: compared, never written with its value."""
    return bool(re.search(r"\|(buyer|seller)\|\d+\|", key) or re.search(r"^largest\|[a-z]+\|top\|", key))


def headline(rows, ceiling):
    """The do-file's lines, step for step (replicate.do)."""
    in_force = [r for r in rows if r.in_force]
    energy = [r for r in in_force if r.product == "ENERGY"]
    three = [r for r in rows if r.product in THREE]
    stated = {}
    for r in energy:
        x = megawatts(r.quantity, r.units)
        if x is not None and x <= ceiling:
            stated[r.contract] = max(stated.get(r.contract, 0.0), x)
    print(f"1. contract rows filed for the quarter: {len(rows):,}")
    print(f"2. rows that file their rate as a number: {sum(1 for r in rows if is_number(r.rate)):,}")
    print(f"3. rows that file words and no number: {sum(1 for r in rows if not is_number(r.rate) and r.words.strip()):,}")
    print(f"4. energy contracts in force: {len({r.contract for r in energy}):,}")
    print(f"5. energy contracts in force that state megawatts, and the megawatts: {len(stated):,}, {sum(stated.values()):,.1f}")
    print(f"6. rows of energy, capacity and tolling executed in 2026 Q2: {sum(1 for r in three if '2026-04-01' <= r.day < '2026-07-01'):,}")
    print(f"7. tolling rows, and their contracts: {sum(1 for r in rows if r.product == 'TOLLING ENERGY'):,}, {len({r.contract for r in rows if r.product == 'TOLLING ENERGY'}):,}")


def main(argv):
    p = argparse.ArgumentParser()
    p.add_argument("--tables")
    p.add_argument("--rows", default=os.path.join(HERE, "rows"))
    p.add_argument("--page")
    p.add_argument("--write", action="store_true")
    p.add_argument("--headline", action="store_true")
    p.add_argument("--no-near", action="store_true")
    a = p.parse_args(argv[1:])
    d = tables_dir(a.tables)
    try:
        if not d:
            raise OSError("ferc_eqr_contracts.csv is in no folder of tables (--tables)")
        rows = [Row(r) for r in rows_of(os.path.join(d, "ferc_eqr_contracts.csv"))]
        ceiling = largest_station(os.path.join(d, "eia860m_operating_generators.csv"))
        if a.headline:
            headline(rows, ceiling)
            return 0
        with open(os.path.join(a.rows, "retrieved.json"), encoding="utf-8") as f:
            stamp = json.load(f)
        history = read_history(os.path.join(d, "ferc_eqr_contracts_history.csv"))
        if a.page:
            with open(a.page, encoding="utf-8") as f:
                shown = json.load(f)
        else:
            node = shutil.which("node")
            if not node:
                raise OSError("node is not on the path (or pass --page FILE)")
            out = subprocess.run([node, "--import", "./scripts/tsx-register.mjs", "scripts/contracts-figures.mjs", os.path.abspath(a.rows)], cwd=SITE, capture_output=True)
            if out.returncode != 0:
                raise OSError("the page's figures could not be drawn: " + out.stderr.decode("utf-8", "replace")[-400:])
            shown = json.loads(out.stdout.decode("utf-8"))
    except (OSError, ValueError, KeyError) as exc:
        print(f"the inputs could not be read: {exc}")
        return 2
    today = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")
    mine, words, facts = compute(rows, history, ceiling, stamp["load_day"], today, near=not a.no_near)
    theirs, their_words = shown["figures"], shown["words"]
    checks = {k: v for k, v in mine.items() if k.startswith("check|") or k.startswith("panel|oldest_quarter")}
    mine = {k: v for k, v in mine.items() if k not in checks}
    by_name = {k[len("check|by_name|"):]: v for k, v in checks.items() if k.startswith("check|by_name|")}
    checks = {k: v for k, v in checks.items() if not k.startswith("check|by_name|")}
    checks["check|place_by_contracts|cells_of_the_megawatts_view"] = len(by_name)
    checks["check|place_by_contracts|cells_the_same_as_a_rank_by_contracts_then_name"] = sum(1 for k, v in by_name.items() if theirs.get(k) == v)
    checks["check|place_by_contracts|cells_the_same_as_the_largest_view"] = sum(1 for k in by_name if theirs.get(k) == mine.get(k))
    for q, n in sorted(facts["companies"].items()):
        checks[f"check|companies_with_a_contract_row|{q}"] = n
    if a.no_near:
        theirs = {k: v for k, v in theirs.items() if not k.endswith("|doubtful")}
    lines, bad, named = [], 0, 0
    for key in sorted(set(mine) | set(theirs)):
        got, want = mine.get(key), theirs.get(key)
        if got is None or want is None:
            lines.append((key, got, want, None, "NO: " + ("page only" if got is None else "replication only")))
            bad += 1
            continue
        diff = float(got) - float(want)
        why = next((reason for pat, reason in NAMED if pat.match(key)), None)
        if abs(diff) <= tolerance(key) + 1e-9:
            lines.append((key, got, want, diff, "yes"))
        elif why:
            lines.append((key, got, want, diff, "named: " + why))
            named += 1
        else:
            lines.append((key, got, want, diff, "NO"))
            bad += 1
    word_keys = sorted(k for k in set(words) | set(their_words) if not k.startswith(("no_token", "panel|as_filed")))
    word_bad = [k for k in word_keys if words.get(k) != their_words.get(k)]
    party_words = sum(1 for k in word_keys if "|party|" in k)
    print(f"/contracts, {len(rows):,} rows of ferc_eqr_contracts filed for {facts['filed_for']} ({stamp['retrieved']['ferc_eqr_contracts']}); "
          f"the live set of a load on {stamp['load_day']}: the {facts['live']:,} rows executed on or after {facts['cutoff']}; the page drawn on {today}")
    print("figure | replication | the page | difference | inside the tolerance")
    fmt = lambda v: "none" if v is None else (f"{v:,.3f}" if isinstance(v, float) and not float(v).is_integer() else f"{int(v):,}")
    for key, got, want, diff, state in lines:
        if internal(key):
            if state != "yes" and not state.startswith("named"):
                print(f"{key} | (a party's figure: internal) | (internal) | {'differs' if diff else ''} | {state}")
            continue
        if state != "yes" or not key.startswith(("quarter|", "panel|ba_rows")) or key.startswith(f"quarter|{words['quarter|listed'].split()[0]}|power|every"):
            print(f"{key} | {fmt(got)} | {fmt(want)} | {'' if diff is None else f'{diff:+.3f}'} | {state}")
    quiet = sum(1 for key, *_ , state in lines if state == "yes" and (internal(key) or (key.startswith(("quarter|", "panel|ba_rows")) and not key.startswith(f"quarter|{words['quarter|listed'].split()[0]}|power|every"))))
    print(f"(not printed above, each inside its tolerance: {quiet} lines, of which {sum(1 for key, *_ in lines if internal(key))} are one party's own figure, internal, "
          "and the others the same counts for every other quarter, product and balancing authority)")
    for pat, reason in NAMED:
        hit = [key for key, *_, state in lines if state.startswith("named") and pat.match(key)]
        if hit:
            print(f"named, {len(hit)} lines of one party's own figure ({pat.pattern}): {reason}")
    print(f"{len(lines) - bad - named} of {len(lines)} inside the tolerance; {named} named; {bad} not explained")
    print(f"words (quarters, dates, balancing authorities, {party_words} names of parties in the rankings): {len(word_keys) - len(word_bad)} of {len(word_keys)} the same"
          + ("" if not word_bad else "; not the same: " + ", ".join(k if "|party|" not in k else k + " (a name: internal)" for k in word_bad[:12])))
    print("checks beside the figures (no key of the page):")
    for key, v in sorted(checks.items()):
        print(f"  {key} | {fmt(v)}")
    print(f"  doubtful pairs by reason | {facts['doubtful']}")
    print(f"  the oldest quarter listed is held from {words.get('panel|oldest_quarter_from') or 'its first day'}; the largest station of EIA's inventory: {ceiling:,.1f} MW")
    print("not replicated here: the words of the list (each contract's own row: seller, buyer, product, dates, quantity, price as filed), which are the rows themselves")
    if a.write:
        figures = []
        for key, got, want, diff, state in lines:
            if internal(key):
                figures.append({"key": key, "internal": "one party's own figure: compared, not written", "agrees": state == "yes", **({"named": state[7:]} if state.startswith("named") else {})})
            else:
                figures.append({"key": key, "page": want, "replication": got, "tolerance": tolerance(key), **({"named": state[7:]} if state.startswith("named") else {})})
        meta = {"tool": "/contracts", "tables_retrieved": stamp["retrieved"], "load_day": stamp["load_day"], "window_from": facts["cutoff"], "filed_for": facts["filed_for"],
                "rows": len(rows), "rows_in_live_window": facts["live"], "drawn_on": today,
                "source": "ferc_eqr_contracts and ferc_eqr_contracts_history as CSV in warehouse/output (internal tables: FERC Electric Quarterly Reports, eqrreportviewer.ferc.gov)",
                "note": "the page's figure is what its own code draws (site/scripts/contracts-figures.mjs) when it is served the stored summary the loader's own function computes on "
                        "these tables; the page is in review and its table is internal, so a visitor is drawn none of them. A party's name and a party's own figure are compared and not written.",
                "result": f"{len(lines) - bad - named} of {len(lines)} inside the tolerance; {named} named; {bad} not explained",
                "words": f"{len(word_keys) - len(word_bad)} of {len(word_keys)} the same",
                "checks": {**{k: v for k, v in sorted(checks.items())}, "doubtful_pairs_by_reason": facts["doubtful"], "largest_station_mw": ceiling},
                "figures": figures}
        with open(os.path.join(HERE, "page_figures.json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump(meta, f, indent=1)
            f.write("\n")
        with open(os.path.join(HERE, "page_figures.csv"), "w", encoding="utf-8", newline="") as f:
            f.write(f"# ERW, /contracts: every figure of the page on the tables of {stamp['retrieved']['ferc_eqr_contracts'][2:]} and a load on {stamp['load_day']} "
                    "(replication/contracts/replicate.py --write). A party's own figure is internal: compared, not written.\n")
            w = csv.writer(f, lineterminator="\n")
            w.writerow(["key", "page", "replication", "tolerance", "agrees"])
            for x in figures:
                if "internal" in x:
                    w.writerow([x["key"], "internal", "internal", tolerance(x["key"]), "yes" if x["agrees"] else "no"])
                else:
                    w.writerow([x["key"], x["page"], x["replication"], x["tolerance"], "yes" if abs(float(x["page"]) - float(x["replication"])) <= x["tolerance"] + 1e-9 else "no"])
    return 0 if not bad and not word_bad else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
