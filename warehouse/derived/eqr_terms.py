#!/usr/bin/env python3
"""The contracts tracker, to useful: what each contract row of FERC's Electric Quarterly Reports says in terms a reader
can sort by (session 125).

Energy Research Warehouse (ERW). Method: docs/methods/eqr_terms.md. No request is made, no model is called: every
reading below is a rule, and every row says which rule read it or why none did.

    python warehouse/derived/eqr_terms.py                 # the three tables, under the data lock
    python warehouse/derived/eqr_terms.py --out-dir DIR   # a trial run: the tables under DIR, nothing in warehouse/output

Inputs: ferc_eqr_contracts (the newest quarter), ferc_eqr_contracts_history (the quarters before it, where held) and
ferc_eqr_buyer_names (the buyer names by rule, warehouse/derived/eqr_buyers.py). All internal; so is everything here.

ferc_eqr_contract_terms (events): one row for each row of ferc_eqr_contracts, with the same event_id.
    parties                  seller;buyer, the buyer under the name the rules count it as (the certain merges applied)
    x_buyer_as_filed, x_buyer_counted_as, x_buyer_merged     the name filed; the name it is counted under; yes when a rule
                             changed it. The doubtful pairs (ferc_eqr_buyer_doubtful) are not merged, here or anywhere
    mw, x_mw_source          the quantity when the filing states it in MW, or in kW (divided by 1,000): "MW" or "KW".
                             A quantity in MWh, in MW-months or with no units is not a number of megawatts and is left;
                             so is a quantity of zero
    x_mw_ranked              yes, or no when the megawatts stated are more than the largest power station operating in
                             the United States holds (eia860m_operating_generators, summed by plant: 6,809 MW in the
                             2026-08 vintage). No one contract is for more than that: such a figure is another unit
                             filed under MW (a year's megawatt-hours, kilowatts). It stays in mw as filed and is left
                             out of the ranking, counted. A figure under the ceiling can be mislabelled too, and
                             nothing here can tell
    price, x_price_source    USD per MWh: "filed" when the rate is filed as a number in $/MWH or $/KWH; "words" when it
                             was read from the rate description (below) in one of those two units; else empty
    x_price_words, x_price_words_unit     the number and the unit read from the words, in FERC's own spelling of the unit
                             ($/MWH, $/KWH, $/KW-MO, $/MW-MO, $/MW-DAY, $/KW-DAY, $/KW-YR, $/MW-YR, $/KW-WK, $/MW-WK)
    x_price_unread           for a row whose rate is words and no number: why no price was read (the list below), or ""
    x_rate_kind              number (a rate is filed as a number, in any unit), words (words and no number), none
    x_tag                    tolling, or storage, from the product fields only; "" otherwise
    x_storage_words_in       the other fields of the row in which the words storage, battery or BESS stand (rate
                             description, agreement identifier, tariff reference, seller name), separated by ";". Not a
                             tag: a seller named for a battery sells other things too, and a tariff's storage schedule
                             is not a contract for a battery. It says where a person would have to read
    x_contract               the filer's company identifier and its contract identifier: one contract
    x_first_quarter, x_quarters_held      the earliest quarter held in which that contract is filed, and how many hold it

READING A PRICE FROM THE WORDS. Only for a row with no rate filed as a number, and only when the words leave one
reading. All of these must hold; the first that fails is the row's x_price_unread:
    no_dollar_amount     the words hold no dollar amount ("Market Based", a tariff's name, a formula in words)
    several_amounts      more than one dollar amount (a schedule by year, peak and off-peak, tiers)
    no_unit              the amount is not followed at once by a unit of energy or of capacity over time ("Deposit:
                         $25,000", "$1.55 per kW", "rate is $0.00"): a dollar figure alone is not a price
    conditional          a word that makes the amount one case among others or the start of a formula: escalates,
                         adjusted, index, CPI, formula, factor, tier, excess, greater or less or more than, up to, above,
                         below, plus, minus, times, a multiplication or addition sign, a percent, LMP, market, peak, a year, a
                         date, if, unless, until, agreed, may be revised, a cap, a ceiling, a floor, a credit, a discount, a
                         penalty, an estimate: the amount is then a bound or one case, not the price
    other_numbers        another number that is not a quantity in MW, kW, MWh or kWh stands in the words
    units_disagree       the filing's own rate-units field names a different unit from the one in the words
A row that passes holds exactly one dollar amount with its unit, at most quantities beside it, and no condition.

TAGS, FROM THE PRODUCT FIELDS ONLY. tolling: the product name is TOLLING ENERGY. storage: a product field (product
name, product type, class, term, increment) names storage or a battery. No product field does: FERC's product list has
no storage product, so the tag is empty in every row, and the words do appear elsewhere (rate descriptions, agreement
identifiers, sellers' names), which this table does not read for the tag. The counts are in the log and the method.

ferc_eqr_party_mw (entities): the buyers (by counted-as name) and sellers (by FERC's company identifier) of energy,
capacity and tolling whose contracts in force state a quantity in megawatts, ranked by megawatts.
    x_mw_stated          the sum, over the party's contracts that state one, of the largest MW any row of the contract
                         states (a contract's rows repeat its quantity by period and by product: adding the rows up would
                         count it many times). Rows with x_mw_ranked no are left out
    x_contracts_with_mw, x_contracts, x_rank_mw, x_rank_contracts (its rank by contracts in ferc_eqr_party_totals' order),
    x_contracts_over (its contracts left out for stating more than the ceiling), x_mw_ceiling

ferc_eqr_quarter_changes (series, freq P3M, ts_utc the quarter's first day, entity ferc_eqr:<energy|capacity|tolling|all>):
    contracts_in_force, rows_in_force, contracts_new (in force in this quarter's file and not in the one before),
    contracts_gone (in the one before and not in this one), contracts_kept. A contract is the filer's company identifier
    and its own contract identifier; a filer that renumbers its contracts makes one gone and one new.
"""

import argparse
import os
import re
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, HERE)
import eqr_buyers as eb  # noqa: E402
import iso_prices as ip  # noqa: E402

CONTRACTS, HISTORY, NAMES = "ferc_eqr_contracts", "ferc_eqr_contracts_history", "ferc_eqr_buyer_names"
PLANTS = "eia860m_operating_generators"
TERMS, PARTY_MW, CHANGES = "ferc_eqr_contract_terms", "ferc_eqr_party_mw", "ferc_eqr_quarter_changes"
SOURCE = "erw:eqr_terms"
METHOD_URL = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/eqr_terms.md"
PRODUCTS = eb.PRODUCTS
EVENT_COLS = eb.EVENT_COLS
TERM_COLS = EVENT_COLS + ["x_buyer_as_filed", "x_buyer_counted_as", "x_buyer_merged", "x_product", "x_tag", "x_mw_source", "x_mw_ranked", "x_price_source", "x_price_words",
                          "x_price_words_unit", "x_price_unread", "x_rate_kind", "x_storage_words_in", "x_contract", "x_first_quarter", "x_quarters_held", "x_quarter", "retrieved_at"]

AMOUNT = re.compile(r"\$\s*([0-9][0-9,]*(?:\.[0-9]+)?|\.[0-9]+)")
# a unit that follows the amount at once: "/MWh", " per kW-month", "/KW-MO"
_T = {"MO": r"(?:mo|mos|month|mth)", "DAY": r"(?:day)", "YR": r"(?:yr|year)", "WK": r"(?:wk|week)"}
UNITS = [("$/MWH", r"(?:mwh|mw-h|megawatt[- ]?hours?)"), ("$/KWH", r"(?:kwh|kw-h|kilowatt[- ]?hours?)")] \
    + [(f"$/{p}-{k}", rf"(?:{p.lower()}|{'megawatt' if p == 'MW' else 'kilowatt'})\s*[-/ ]\s*{t}") for p in ("KW", "MW") for k, t in _T.items()]
UNIT_AFTER = [(name, re.compile(r"\s*(?:/|per)\s*" + pat + r"(?![a-z])", re.I)) for name, pat in UNITS]
CONDITION = re.compile(r"escalat|adjust|index|\bcpi\b|formula|\btiers?\b|excess|greater|less than|up to|\babove\b|\bbelow\b|\bplus\b|\bminus\b|\btimes\b|multipl|[+*%]|percent|\blmp\b|market|peak|"
                       r"\b(?:19|20)\d\d\b|\d{1,2}/\d{1,2}/\d{2,4}|thru|through|deposit|start|\bor\b|higher of|lower of|lesser|not to exceed|maximum|minimum|\bx\b|\bif\b|more than|no case|agreed|revis|factor|unless|\buntil\b|credit|"
                       r"\bcap\b|ceiling|floor|discount|penalt|estimat", re.I)
NUMBER = re.compile(r"(?<![A-Za-z$.\d])([0-9][0-9,]*(?:\.[0-9]+)?)(?![\d])")
QUANTITY_AFTER = re.compile(r"\s*-?\s*(?:mw|kw|mwh|kwh|megawatts?|kilowatts?)(?![a-z/-])", re.I)
PER_MWH = {"$/MWH": 1.0, "$/KWH": 1000.0}
FILED_UNITS = {"$/MWH": "$/MWH", "$/KWH": "$/KWH", "$/KW-MO": "$/KW-MO", "$/MW-MO": "$/MW-MO", "$/MW-DAY": "$/MW-DAY", "$/KW-DAY": "$/KW-DAY", "$/KW-YR": "$/KW-YR",
               "$/MW-YR": "$/MW-YR", "$/KW-WK": "$/KW-WK", "$/MW-WK": "$/MW-WK"}
STORAGE_WORD = re.compile(r"storage|batter|\bbess\b", re.I)
PRODUCT_FIELDS = ["x_product_name", "x_product_type_name", "x_class_name", "x_term_name", "x_increment_name"]
OTHER_FIELDS = {"x_rate_description": "rate_description", "x_contract_service_agreement_id": "agreement_id", "x_ferc_tariff_reference": "tariff_reference",
                "x_seller_company_name": "seller_name"}
REASONS = ["no_dollar_amount", "several_amounts", "no_unit", "conditional", "other_numbers", "units_disagree"]


def read_price(text, filed_units=""):
    """A price from a rate description, only where number and unit are unambiguous: (value, unit, "") or (None, "", why).
    The rules are the docstring's, in its order."""
    t = " ".join(str(text or "").split())
    amounts = list(AMOUNT.finditer(t))
    if not amounts:
        return None, "", "no_dollar_amount"
    if len(amounts) > 1:
        return None, "", "several_amounts"
    m = amounts[0]
    unit, end = "", m.end()
    for name, pat in UNIT_AFTER:
        u = pat.match(t, m.end())
        if u:
            unit, end = name, u.end()
            break
    if not unit:
        return None, "", "no_unit"
    rest = t[:m.start()] + " " + t[end:]
    if CONDITION.search(rest):
        return None, "", "conditional"
    for n in NUMBER.finditer(rest):
        if not QUANTITY_AFTER.match(rest, n.end()):
            return None, "", "other_numbers"
    filed = FILED_UNITS.get(str(filed_units or "").strip().upper())
    if str(filed_units or "").strip() and filed != unit:
        return None, "", "units_disagree"
    return float(m.group(1).replace(",", "")), unit, ""


def stated_mw(quantity, units):
    """The megawatts a row states: (MW, "MW" or "KW"), or (None, ""). Only MW and kW are megawatts."""
    u = str(units or "").strip().upper()
    try:
        q = float(str(quantity).replace(",", ""))
    except ValueError:
        return None, ""
    if not q > 0:
        return None, ""
    if u == "MW":
        return q, "MW"
    if u == "KW":
        return q / 1000.0, "KW"
    return None, ""


def largest_plant(in_dir):
    """The megawatts of the largest power station operating in the United States, and the vintage of EIA's inventory:
    the most any one contract can be for. Read from the warehouse, never typed in."""
    g, path = read_table(PLANTS, in_dir)
    if g is None:
        raise SystemExit(f"{PLANTS} is not on this machine: the ceiling on a contract's megawatts is read from it")
    mw = pd.to_numeric(g["capacity_mw"], errors="coerce").groupby(g["plant_id"]).sum()
    return float(mw.max()), sorted(g["vintage"].unique())[-1]


def tag_of(row):
    """tolling or storage, from the product fields only; "" otherwise."""
    if str(row.get("x_product_name", "")).strip().upper() == "TOLLING ENERGY":
        return "tolling"
    if any(STORAGE_WORD.search(str(row.get(c, ""))) for c in PRODUCT_FIELDS):
        return "storage"
    return ""


def quarter_start(q):
    return f"{q[:4]}-{3 * (int(q[-1]) - 1) + 1:02d}-01T00:00:00Z"


def contract_key(d):
    return d["x_company_id"] + "|" + d["x_contract_unique_id"]


def quarter_changes(frames):
    """{quarter: frame}: contracts in force per quarter and product, and what is new, gone and kept against the quarter
    before it among those held. Rows of dicts (product, quarter, variable, value)."""
    out = []
    quarters = sorted(frames)
    sets = {}
    for q in quarters:
        d = frames[q]
        f = d[d["status"] == "in_force"]
        prod = f["x_product_name"].str.upper().map(PRODUCTS)
        key = contract_key(f)
        for p in ["all"] + list(PRODUCTS.values()):
            k = key if p == "all" else key[prod == p]
            sets[(q, p)] = set(k)
            out.append(dict(product=p, quarter=q, variable="contracts_in_force", value=len(sets[(q, p)])))
            out.append(dict(product=p, quarter=q, variable="rows_in_force", value=int(len(k))))
    for a, b in zip(quarters, quarters[1:]):
        consecutive = (int(b[:4]) * 4 + int(b[-1])) - (int(a[:4]) * 4 + int(a[-1])) == 1
        if not consecutive:
            continue  # a quarter that is not held in between: new and gone would be two quarters' worth
        for p in ["all"] + list(PRODUCTS.values()):
            was, now = sets[(a, p)], sets[(b, p)]
            out += [dict(product=p, quarter=b, variable="contracts_new", value=len(now - was)), dict(product=p, quarter=b, variable="contracts_gone", value=len(was - now)),
                    dict(product=p, quarter=b, variable="contracts_kept", value=len(now & was))]
    return out


def party_mw(t):
    """The parties of energy, capacity and tolling whose contracts in force state megawatts, ranked by megawatts. t: the
    terms rows (with seller, company id, counted-as buyer, product, contract, mw). Rows of dicts."""
    x = t[(t["status"] == "in_force") & t["x_product"].isin(PRODUCTS.values())].copy()
    x["mw_n"] = pd.to_numeric(x["mw"], errors="coerce").where(x["x_mw_ranked"] == "yes")
    x["over"] = x["x_mw_ranked"] == "no"
    rows = []
    for role, key in (("buyer", "x_buyer_counted_as"), ("seller", "company_id")):
        per_contract = x.groupby(["x_product", key, "x_contract"])["mw_n"].max().reset_index()      # the largest MW any row of the contract states
        g = per_contract.groupby(["x_product", key]).agg(mw=("mw_n", "sum"), with_mw=("mw_n", "count"), contracts=("x_contract", "nunique")).reset_index()
        over = x[x["over"]].groupby(["x_product", key])["x_contract"].nunique()
        g["over"] = [int(over.get((p, k), 0)) for p, k in zip(g["x_product"], g[key])]
        names = x.groupby(key)["seller"].agg(lambda s: s.value_counts().index[0]) if role == "seller" else None
        for product, p in g.groupby("x_product"):
            p = p.assign(name=p[key] if role == "buyer" else p[key].map(names))
            by_contracts = p.sort_values(["contracts", "name"], ascending=[False, True]).reset_index(drop=True)
            rank_c = {r[key]: i for i, r in enumerate(by_contracts.to_dict("records"), 1)}
            have = p[p["with_mw"] > 0].sort_values(["mw", "name"], ascending=[False, True]).reset_index(drop=True)
            for i, r in enumerate(have.to_dict("records"), 1):
                rows.append(dict(role=role, product=product, rank_mw=i, name=r["name"], mw=round(float(r["mw"]), 3), contracts_with_mw=int(r["with_mw"]), contracts=int(r["contracts"]),
                                 rank_contracts=rank_c[r[key]], contracts_over=int(r["over"]), company_id=r[key] if role == "seller" else ""))
    return rows


def terms(d, names, first_seen, held, retrieved, ceiling):
    """The terms rows of one quarter's contracts. names: {name as filed: (counted as, merged yes/no)}; ceiling: the most
    megawatts one contract can be for (largest_plant)."""
    buyer = d["x_customer_company_name"]
    counted = buyer.map(lambda n: names.get(n, (n, "no"))[0])
    merged = buyer.map(lambda n: names.get(n, (n, "no"))[1])
    mw = [stated_mw(q, u) for q, u in zip(d["x_quantity"], d["x_units"])]
    rate_num = pd.to_numeric(d["x_rate"].where(d["x_rate"] != ""), errors="coerce")
    ru = d["x_rate_units"].str.strip().str.upper()
    price, src, words, wunit, unread = [], [], [], [], []
    for r, u, text in zip(rate_num, ru, d["x_rate_description"]):
        if r == r:  # a number is filed
            price.append(r * PER_MWH[u] if u in PER_MWH else None)
            src.append("filed" if u in PER_MWH else "")
            words.append(None), wunit.append(""), unread.append("")
            continue
        if not str(text).strip():
            price.append(None), src.append(""), words.append(None), wunit.append(""), unread.append("")
            continue
        v, unit, why = read_price(text, u)
        words.append(v), wunit.append(unit), unread.append(why)
        price.append(v * PER_MWH[unit] if v is not None and unit in PER_MWH else None)
        src.append("words" if v is not None and unit in PER_MWH else "")
    key = contract_key(d)
    kind = ["number" if r == r else "words" if str(text).strip() else "none" for r, text in zip(rate_num, d["x_rate_description"])]
    hits = {label: d[c].str.contains(STORAGE_WORD) if c in d.columns else pd.Series(False, index=d.index) for c, label in OTHER_FIELDS.items()}
    elsewhere = [";".join(label for label in hits if hits[label].iat[i]) for i in range(len(d))]
    out = pd.DataFrame({
        "event_id": d["event_id"], "event_date": d["event_date"], "event_type": "contract_terms", "parties": d["x_seller_company_name"] + ";" + counted, "entity_ids": d["entity_ids"],
        "mw": [("" if m is None else round(m, 6)) for m, _ in mw], "price": [("" if p is None else round(p, 6)) for p in price], "currency": ["USD" if p is not None else "" for p in price],
        "status": d["status"], "source": SOURCE, "source_url": METHOD_URL,
        "x_buyer_as_filed": buyer, "x_buyer_counted_as": counted, "x_buyer_merged": merged, "x_product": d["x_product_name"].str.upper().map(PRODUCTS).fillna(""),
        "x_tag": [tag_of(r) for r in d[PRODUCT_FIELDS].to_dict("records")], "x_mw_source": [s for _, s in mw],
        "x_mw_ranked": [("" if m is None else "yes" if m <= ceiling else "no") for m, _ in mw], "x_price_source": src,
        "x_price_words": [("" if w is None else w) for w in words], "x_price_words_unit": wunit, "x_price_unread": unread, "x_rate_kind": kind,
        "x_storage_words_in": elsewhere, "x_contract": key,
        "x_first_quarter": key.map(first_seen).fillna(d["x_quarter"]), "x_quarters_held": key.map(held).fillna(1).astype(int), "x_quarter": d["x_quarter"], "retrieved_at": retrieved})
    return out[TERM_COLS]


def read_table(name, in_dir):
    path = os.path.join(in_dir, name + ".csv")
    if not os.path.exists(path):
        return None, path
    return pd.read_csv(path, skiprows=ip.header_rows(path), low_memory=False, dtype=str, keep_default_na=False), path


def main(argv=None):
    ap = argparse.ArgumentParser(description="The contracts tracker: buyers under one name, megawatts and prices where stated, tags, and what changed by quarter")
    ap.add_argument("--out-dir", help="a trial run: the tables and their log under this directory; nothing in warehouse/output")
    a = ap.parse_args(argv)
    inputs = ip.OUT_DIR
    if a.out_dir:
        os.makedirs(a.out_dir, exist_ok=True)
    run_id = pd.Timestamp.now(tz="UTC").strftime("%Y%m%dT%H%M%SZ")
    retrieved = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
    log_dir = os.path.join(a.out_dir, "logs") if a.out_dir else ip.LOG_DIR
    os.makedirs(log_dir, exist_ok=True)
    log = ip.Log(os.path.join(log_dir, f"eqr_terms_{run_id}.log"))
    d, path = read_table(CONTRACTS, inputs)
    if d is None:
        raise SystemExit(f"{CONTRACTS} is not on this machine")
    newest = d["x_quarter"].max()
    d = d[d["x_quarter"] == newest].reset_index(drop=True)
    hist, _ = read_table(HISTORY, inputs)
    frames = {newest: d}
    if hist is not None:
        for q, g in hist.groupby("x_quarter"):
            if q != newest:
                frames[q] = g
    quarters = sorted(frames)
    log(f"  {CONTRACTS}: {len(d):,} rows of {newest}; quarters held: {', '.join(quarters)}" + ("" if hist is not None else f" ({HISTORY} is not on this machine: one quarter)"))
    seen = pd.concat([pd.DataFrame({"k": contract_key(g), "q": q}) for q, g in frames.items()], ignore_index=True).drop_duplicates()
    first_seen, held = seen.groupby("k")["q"].min(), seen.groupby("k")["q"].nunique()
    nm, _ = read_table(NAMES, inputs)
    if nm is None:
        raise SystemExit(f"{NAMES} is not on this machine: run warehouse/derived/eqr_buyers.py first")
    names = {r["name"]: (r["x_counted_as"], r["x_merged"]) for r in nm.to_dict("records")}
    ceiling, plants_vintage = largest_plant(inputs)
    t = terms(d, names, first_seen, held, retrieved, ceiling)
    over = t["x_mw_ranked"] == "no"
    log(f"  megawatts: the ceiling is {ceiling:,.0f} MW, the largest station in {PLANTS} (vintage {plants_vintage}); {int(over.sum()):,} rows of "
        f"{t.loc[over, 'x_contract'].nunique():,} contracts state more and are left out of the ranking")
    words_only = (d["x_rate"] == "") & (d["x_rate_description"].str.strip() != "")
    read = t["x_price_words"] != ""
    why = t.loc[words_only.values & ~read.values, "x_price_unread"].value_counts().to_dict()
    log(f"  rates: {int((d['x_rate'] != '').sum()):,} rows file a number; {int(words_only.sum()):,} file words and no number; of those a price was read from the words in "
        f"{int(read.sum()):,} ({t.loc[read, 'x_price_words_unit'].value_counts().to_dict()}), and {int(words_only.sum()) - int(read.sum()):,} remain unread: {why}")
    log(f"  buyers: {int((t['x_buyer_merged'] == 'yes').sum()):,} rows carry a buyer name that a rule merged with another; megawatts stated on {int((t['mw'] != '').sum()):,} rows "
        f"({t['x_mw_source'].value_counts().to_dict()}); tags: {t['x_tag'].value_counts().to_dict()}")
    elsewhere = {c: int(d[c].str.contains(STORAGE_WORD).sum()) for c in ("x_rate_description", "x_contract_service_agreement_id", "x_ferc_tariff_reference", "x_seller_company_name") if c in d.columns}
    log(f"  storage: no product field names storage or a battery in any row ({int((t['x_tag'] == 'storage').sum())} tagged); the words appear, untagged, in: {elsewhere}")
    scope = t.assign(seller=d["x_seller_company_name"].values, company_id=d["x_company_id"].values)
    pm = party_mw(scope)
    common = dict(geo="US", lat="", lon="", capacity_mw="", status_date="", operator="", source=SOURCE, source_url=METHOD_URL, retrieved_at=retrieved, vintage="")
    pm_t = pd.DataFrame([dict(entity_id=f"ferc_eqr_party_mw:{r['role']}:{r['product']}:{r['rank_mw']:05d}", entity_type="company", name=r["name"], status="active", **common,
                              x_role=r["role"], x_product=r["product"], x_rank_mw=r["rank_mw"], x_mw_stated=r["mw"], x_contracts_with_mw=r["contracts_with_mw"], x_contracts=r["contracts"],
                              x_rank_contracts=r["rank_contracts"], x_contracts_over=r["contracts_over"], x_mw_ceiling=ceiling, x_company_id=r["company_id"], x_quarter=newest)
                         for r in pm])
    ch = quarter_changes(frames)
    ch_t = pd.DataFrame([dict(entity=f"ferc_eqr:{r['product']}", variable=r["variable"], ts_utc=quarter_start(r["quarter"]), value=r["value"], unit="count", freq="P3M", geo="US", market="",
                              node="", source=SOURCE, source_url=METHOD_URL, retrieved_at=retrieved, vintage="") for r in ch])[ip.SERIES_COLS]
    if a.out_dir:
        ip.set_out_dir(a.out_dir)
    for name in (TERMS, PARTY_MW, CHANGES):
        target = os.path.join(ip.OUT_DIR, name + ".csv")
        if os.path.exists(target):
            ip._require_lock(target, f"rebuilding {name}")
            os.remove(target)  # rebuilt whole from its inputs each run
    tail = [f"Retrieved: {run_id} (UTC) by warehouse/derived/eqr_terms.py", f"Run log: warehouse/output/logs/eqr_terms_{run_id}.log",
            f"Derived from: {CONTRACTS}; {HISTORY}; {NAMES}; {PLANTS}",
            f"Source: {SOURCE} from ferc:eqr, Federal Energy Regulatory Commission, Electric Quarterly Reports; quarters held: {', '.join(quarters)}",
            "License: internal. A derived table inherits the license of its input: ferc_eqr_contracts is internal (session 83's ruling). Not in git, not public."]
    ip.write_csv(t, TERMS, [
        "Energy Research Warehouse (ERW): the contract rows of FERC's Electric Quarterly Reports in terms a reader can sort by: the buyer under one name, megawatts and "
        "prices where the filing states them, tags from the product fields (session 125)",
        f"Shape: events (docs/datastandard.md v0). One row for each row of {CONTRACTS} ({newest}), with its event_id. parties: seller;buyer as counted (the rule merges of "
        "ferc_eqr_buyer_names applied; the doubtful pairs are not merged). mw: stated in MW, or in kW over 1,000 (x_mw_source). price: USD per MWh, filed as a number "
        "in $/MWH or $/KWH, or read from the rate description in those units (x_price_source: filed, words). x_price_words, x_price_words_unit: what was read from the "
        "words, in any unit; x_price_unread: why nothing was. x_tag: tolling or storage, from the product fields only. x_contract, x_first_quarter, x_quarters_held. "
        f"x_mw_ranked: no when the megawatts stated are above {ceiling:,.0f} MW, the largest station operating in the United States ({PLANTS}, vintage {plants_vintage}).",
        f"Counts: {len(t):,} rows; words and no number {int(words_only.sum()):,}, read {int(read.sum()):,}, unread {int(words_only.sum()) - int(read.sum()):,} "
        f"({'; '.join(f'{k} {v:,}' for k, v in sorted(why.items(), key=lambda kv: -kv[1]))}). A price is read only where one dollar amount stands with its unit and no condition.",
    ] + tail, log, cols=TERM_COLS, key=["event_id"], time_col="event_date")
    ip.write_csv(pm_t, PARTY_MW, [
        "Energy Research Warehouse (ERW): the buyers and sellers of energy, capacity and tolling in FERC's Electric Quarterly Reports whose contracts in force state megawatts, "
        "ranked by megawatts (session 125)",
        "Shape: entities (docs/datastandard.md v0). One row per party, role and product. x_mw_stated: the sum, over its contracts that state one, of the largest MW any row of "
        "the contract states. x_contracts_with_mw of x_contracts state one: most contracts state none, so this ranks what is stated and is not a ranking of the market. "
        "x_rank_mw; x_rank_contracts (its place by contracts among all parties of that role and product). x_contracts_over: its contracts that state more than "
        f"x_mw_ceiling ({ceiling:,.0f} MW, the largest station in {PLANTS}, vintage {plants_vintage}) and are left out: another unit filed under MW.",
        f"Counts: {len(pm_t):,} rows of {newest}.",
    ] + tail, log, cols=eb.ENTITY_COLS + ["x_role", "x_product", "x_rank_mw", "x_mw_stated", "x_contracts_with_mw", "x_contracts", "x_rank_contracts", "x_contracts_over", "x_mw_ceiling",
                               "x_company_id", "x_quarter"],
        key=["entity_id"], time_col="retrieved_at")
    ip.write_csv(ch_t, CHANGES, [
        "Energy Research Warehouse (ERW): FERC's Electric Quarterly Reports by quarter: contracts in force, and those new, gone and kept against the quarter before (session 125)",
        "Shape: series (docs/datastandard.md v0). entity ferc_eqr:<energy|capacity|tolling|all>; freq P3M; ts_utc the quarter's first day. A contract is the filer's company "
        "identifier and its own contract identifier: a filer that renumbers its contracts makes one gone and one new. new, gone and kept are written only against a quarter "
        "that is held and next before it.",
        f"Quarters: {', '.join(quarters)}.",
    ] + tail, log)
    ip.update_sources([dict(source=SOURCE, publisher="Energy Research Warehouse (ERW), derived",
                            report="FERC EQR contract terms: buyers under one name, megawatts and prices where stated, tags, changes by quarter (docs/methods/eqr_terms.md)", report_url=METHOD_URL,
                            document_list="docs/methods/eqr_terms.md", license="internal", tables=[TERMS, PARTY_MW, CHANGES])])
    log.close()
    print(f"{TERMS}: {len(t):,} rows ({int(read.sum()):,} prices read from words, {int(words_only.sum()) - int(read.sum()):,} unread); {PARTY_MW}: {len(pm_t):,}; {CHANGES}: {len(ch_t):,} rows, "
          f"quarters {', '.join(quarters)}" + (f" (trial, under {a.out_dir})" if a.out_dir else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
