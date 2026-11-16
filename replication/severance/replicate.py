#!/usr/bin/env python3
"""ERW, the severance tax tool (/severance, its Lease tab, and the internal /severance/lease/real): the replication a
reader can run (session 7502, chain 304).

Written from the method note (docs/methods/severance.md, "The tool as a reader meets it") and the rules file
(site/data/severance_rules.json) alone, not from the page's code: every figure the calculator shows at its default and
at the named cases of cases.json, every figure the Lease tab shows on the page's own sample lease (sample_lease.csv,
the page's "Download the sample"), and the totals the internal page shows for four real leases picked by a stated rule,
is computed again here, in this file's own words, and set beside the figure the page's own functions give on the same
rows (site/scripts/severance-figures.mjs, run with node, or a file of its output). A difference is inside the
tolerance when it is at most half the last digit the page shows: half a cent for a dollar figure and a price, nothing
for a count.

    python replication/severance/replicate.py --tables DIR            # N of N, or each difference named
    python replication/severance/replicate.py --tables DIR --write    # also writes page_figures.json and page_figures.csv
    python replication/severance/replicate.py --tables DIR --headline # only the do-file's lines, and rows/spot_slim.csv

    --tables DIR  the folder that holds eia_fuel_spot_prices.csv (public: the CSV the page offers under both tabs) and,
                  for the real leases, rrc_lease_production_monthly.csv (internal: a warehouse machine holds it; without
                  it the real leases are left out and said so). Default: warehouse/output of this copy.
    --page FILE   the page's figures as a file (the JSON the node script prints) instead of running node
    --now ISO     the instant the page is drawn at (default: now); it sets which month is the latest complete one

rrc_lease_production_monthly is internal (the Railroad Commission grants no reuse in writing): no row of it, no lease
id, lease name or operator is printed or written here. A real lease is named by the rule that picks it, and only its
totals over its months are written. Exit 0 when every figure is inside its tolerance or its difference is one this file
names (NAMED below), 1 when another differs or a key is on one side only, 2 when the inputs cannot be read. Standard
library only.
"""
import argparse
import calendar
import csv
import datetime
import hashlib
import json
import math
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SITE = os.path.join(ROOT, "site")
PRICE_TABLE = "eia_fuel_spot_prices.csv"
RRC_TABLE = "rrc_lease_production_monthly.csv"
PRODUCTS = ["oil", "gas", "condensate"]
# The note, "The lease file": a fact given on any row of a well holds for its other rows.
WELL_FACTS = ["completion_date", "depth_ft", "horizontal", "well_type", "inactive_months", "hcg_cost_ratio", "nm_district", "royalty_pct",
              "trucking_per_unit", "transport_per_bbl"]

# A difference this file names instead of failing on: the key, and why the two sides are not the same thing.
NAMED = {}


def round2(x):
    """Two decimals, half up, as the page rounds a mean price."""
    return math.floor(x * 100 + 0.5) / 100


def days_in(month):
    y, m = int(month[:4]), int(month[5:7])
    return calendar.monthrange(y, m)[1]


def shift(month, k):
    y, m = int(month[:4]), int(month[5:7])
    n = y * 12 + (m - 1) + k
    return "%04d-%02d" % (n // 12, n % 12 + 1)


def months_from(date, month):
    """Whole months from a date's month to a production month (the month of completion is month 0)."""
    return (int(month[:4]) - int(date[:4])) * 12 + (int(month[5:7]) - int(date[5:7]))


# --- the prices (the note, "Default prices") ----------------------------------------------------------------------------

def daily_prices(tables):
    """The table's daily spot prices by entity and month."""
    out = {}
    with open(os.path.join(tables, PRICE_TABLE), encoding="utf-8", newline="") as f:
        rows = csv.reader(line for line in f if not line.startswith("#"))
        head = next(rows)
        e, v, t, val = (head.index(c) for c in ("entity", "variable", "ts_utc", "value"))
        for r in rows:
            if r[v] == "spot_price":
                out.setdefault(r[e], {}).setdefault(r[t][:7], []).append(float(r[val]))
    return out


def month_means(by_month, since="2023-01"):
    return {m: (round2(sum(xs) / len(xs)), len(xs)) for m, xs in by_month.items() if m >= since}


def default_price(by_month, now):
    """The calculator's default: the latest complete month among the three months before this one and this one. A
    month is complete once a later month is held."""
    first = shift(now.strftime("%Y-%m"), -3)
    held = sorted(m for m in by_month if m >= first)
    if len(held) < 2:
        return None
    m = held[-2]
    return {"month": m, "value": round2(sum(by_month[m]) / len(by_month[m])), "days": len(by_month[m])}


# --- the calculator (the note, "How a figure is computed") --------------------------------------------------------------

class Rules:
    def __init__(self, path):
        with open(path, encoding="utf-8") as f:
            self.j = json.load(f)
        self.version = self.j["version"]

    def product(self, state, product):
        return self.j["states"][state]["products"].get(product)

    def option(self, state, product, rule):
        p = self.product(state, product)
        return next((o for o in (p["options"] if p else []) if o["id"] == rule), None)

    def districts(self, product="oil"):
        b = next(b for b in self.product("NM", product)["base"] if b["rate"] == "district")
        return b["districts"]["list"]


def credit_percent(option, period):
    """A Texas low-producing credit: the percent the Comptroller's certified price of the report period earns. The first
    bound the price is above sets it; the last bound has no floor. A period the file does not hold earns nothing."""
    row = next((p for p in option.get("certified", {}).get("prices", []) if p["period"] == period), None)
    if row is None:
        return 0.0
    for b in option["bounds"]:
        if b["above"] is None or row["price"] > b["above"]:
            return float(b["pct"])
    return 0.0


def tax(rules, state, product, volume, price, variant=None, district_rate=0.0, royalty_pct=0.0, trucking=0.0, transport=0.0,
        option=None, param=None, period=None, credit=None, credit_period=None):
    """One month of one product: the value, each base tax, the tax at the base rate, the tax with one reduced rate and
    the credit, the savings and the fees."""
    st = rules.j["states"][state]
    p = st["products"][product]
    gross = volume * price
    taxable = gross
    vd = st.get("value_deduction")
    if vd and product in vd["products"]:
        if vd.get("royalty"):
            taxable = gross - gross * royalty_pct / 100 - volume * trucking      # New Mexico
        else:
            taxable = gross - volume * transport                                  # Louisiana oil and condensate
    taxable = max(0.0, taxable)
    lines = []
    for b in p["base"]:
        rate = b["rate"]
        if rate == "variant":
            rate = next((v["rate"] for v in p["variants"] if v["id"] == variant), p["variants"][0]["rate"])
        elif rate == "district":
            rate = district_rate
        t = volume * rate if b["basis"] == "per_unit" else taxable * rate
        if "min_per_unit" in b:
            t = max(t, volume * b["min_per_unit"])        # Texas oil: 4.6 cents a barrel when that is more
        lines.append((b["id"], rate, t))
    base_total = sum(t for _, _, t in lines)
    with_total = base_total
    effects = []      # what the page states for each rule applied: a percent of value, cents a unit, or a percent exempt or credited
    if option:
        o = next(q for q in p["options"] if q["id"] == option and q["group"] == "rate")
        first_rate, first_tax = lines[0][1], lines[0][2]
        kind = o["kind"]
        if kind == "rate":
            t = taxable * o["rate"]
            effects.append((o["id"], o["rate"] * 100))
            if "exempt_below_price" in o and volume > 0 and taxable / volume < o["exempt_below_price"]:
                t = 0.0
        elif kind == "per_unit":
            t = volume * o["rate"]
            effects.append((o["id"], o["rate"] * 100))
        elif kind == "rate_param":
            v = o["param"]["default"] if param is None else param
            reduced = v / 100 if o.get("rate") is None else o["rate"] * (1 - v / 100)
            t = taxable * reduced
            effects.append((o["id"], reduced * 100))
        elif kind == "exempt_pct":
            t = first_tax * (1 - o["pct"] / 100)
            effects.append((o["id"], o["pct"]))
        elif kind == "hcg_ratio":
            ratio = o["param"]["default"] if param is None else param
            reduced = max(0.0, first_rate - first_rate * ratio / 2)
            t = taxable * reduced
            effects.append((o["id"], reduced * 100))
        elif kind == "credit_tier":
            t = first_tax * (1 - credit_percent(o, period) / 100)
            effects.append((o["id"], credit_percent(o, period)))
        else:
            raise ValueError(kind)
        with_total = base_total - first_tax + t
    if credit:
        c = next(q for q in p["options"] if q["id"] == credit and q["group"] == "credit")
        with_total *= 1 - credit_percent(c, credit_period) / 100
        effects.append((c["id"], credit_percent(c, credit_period)))
    return {"gross": gross, "taxable": taxable, "lines": lines, "base": base_total, "with": with_total, "savings": base_total - with_total,
            "fees": [(f["id"], volume * f["per_unit"]) for f in p["fees"]], "effects": effects}


def latest_period(option):
    """The page's default report period: the first the rules file lists, its latest."""
    c = option.get("certified")
    return c["prices"][0]["period"] if c else None


def calculator(rules, cases, defaults, out):
    for c in cases:
        kind = "gas" if c["product"] == "gas" else "oil"
        price = c["price"]
        if price == "default":
            if defaults[kind] is None:
                continue
            price = defaults[kind]["value"]
        rate = 0.0
        if c.get("district"):
            rate = next(d["rate"] for d in rules.districts(c["product"]) if d["label"] == c["district"])
        kw = {}
        if c.get("option"):
            o = rules.option(c["state"], c["product"], c["option"]["id"])
            kw.update(option=o["id"], param=c["option"].get("param"), period=c["option"].get("period") or latest_period(o))
        if c.get("credit"):
            o = rules.option(c["state"], c["product"], c["credit"]["id"])
            kw.update(credit=o["id"], credit_period=c["credit"].get("period") or latest_period(o))
        r = tax(rules, c["state"], c["product"], c["volume"], price, variant=c.get("variant", "la_oil_pre2025"), district_rate=rate,
                royalty_pct=c.get("royaltyPct", 0.0), trucking=c.get("trucking", 0.0), transport=c.get("transport", 0.0), **kw)
        k = "calc|%s|" % c["id"]
        out[k + "gross"] = r["gross"]
        out[k + "taxable"] = r["taxable"]
        for rule, _, t in r["lines"]:
            out["%sline|%s" % (k, rule)] = t
        out[k + "base"] = r["base"]
        out[k + "with"] = r["with"]
        out[k + "savings"] = r["savings"]
        for fee, amount in r["fees"]:
            out["%sfee|%s" % (k, fee)] = amount
        for rule, shown in r["effects"]:
            out["%seffect|%s" % (k, rule)] = shown


def rule_list(rules, out):
    for s, st in rules.j["states"].items():
        ps = list(st["products"].values())
        out["rules|%s|base" % s] = sum(len(p["base"]) for p in ps)
        out["rules|%s|options" % s] = sum(len(p["options"]) for p in ps)
        out["rules|%s|fees" % s] = sum(len(p["fees"]) for p in ps)
        for p in ps:
            for o in p["options"]:
                if "certified" in o:
                    out["rules|%s|latest_certified" % o["id"]] = o["certified"]["prices"][0]["price"]
                    out["rules|%s|periods" % o["id"]] = len(o["certified"]["prices"])


# --- the lease tab (the note, "The lease tool" and "The lease file") ---------------------------------------------------

def number(cell):
    t = (cell or "").strip().replace("$", "").replace(",", "")
    return float(t) if t else None


def read_lease(text, rules):
    """The lease file as well-months: one per state, well and month; the first row of a well and month is the one used."""
    rows = list(csv.reader(line for line in text.splitlines() if line.strip() and not line.startswith("#")))
    head = [h.strip().lower() for h in rows[0]]
    recs = [dict(zip(head, (c.strip() for c in r + [""] * (len(head) - len(r))))) for r in rows[1:]]
    facts = {}
    for r in recs:
        f = facts.setdefault((r["state"].upper(), r["well_id"]), {})
        for c in WELL_FACTS:
            if r.get(c) and c not in f:
                f[c] = r[c]
    out, seen = [], set()
    for r in recs:
        key = (r["state"].upper(), r["well_id"])
        if key + (r["month"],) in seen:
            continue
        seen.add(key + (r["month"],))
        w = dict(facts[key])
        w.update({k: v for k, v in r.items() if v != ""})
        district = None
        if key[0] == "NM" and w.get("nm_district"):
            cell = w["nm_district"].lower()
            for d in rules.districts():
                suffix = d["label"].rsplit(" ", 1)[-1]
                if (cell.isdigit() and int(suffix) == int(cell)) or d["label"].lower() == cell:
                    district = d
                    break
        hz = (w.get("horizontal") or "").lower()
        out.append({
            "state": key[0], "well": key[1], "key": key, "month": r["month"],
            "vol": {p: number(r.get({"oil": "oil_bbl", "gas": "gas_mcf", "condensate": "condensate_bbl"}[p])) for p in PRODUCTS},
            "price": {p: number(r.get(p + "_price")) for p in PRODUCTS},
            "completion": w.get("completion_date") or None, "depth": number(w.get("depth_ft")),
            "horizontal": hz in ("yes", "y", "true", "1", "horizontal"), "days": number(r.get("days_produced")),
            "water_cut": number(r.get("water_cut_pct")), "well_type": (w.get("well_type") or "").lower() or None,
            "inactive_months": number(w.get("inactive_months")), "hcg": number(w.get("hcg_cost_ratio")), "district": district,
            "royalty": number(w.get("royalty_pct")) or 0.0, "trucking": number(w.get("trucking_per_unit")) or 0.0,
            "transport": number(w.get("transport_per_bbl")) or 0.0,
            "claimed": [x for x in (r.get("exemptions") or "").replace("|", ";").replace(" ", ";").split(";") if x],
        })
    return out


def analyse(rules, rows, book, ticks=None):
    """Every well, month and product with a volume: the base tax, the tax with the ticked rules, the fees, each rule the
    well's numbers meet with what it alone would save, and the best of them. `ticks`: by well, the rule ids ticked."""
    ticks = ticks or {}
    by_well = {}
    for r in rows:
        by_well.setdefault(r["key"], {})[r["month"]] = r
    lines = []
    for r in sorted(rows, key=lambda q: (q["state"] + "|" + q["well"], q["month"])):
        mine = by_well[r["key"]]
        for product in PRODUCTS:
            vol = r["vol"][product]
            if vol is None or vol <= 0 or rules.product(r["state"], product) is None:
                continue
            price = r["price"][product]
            if price is None:
                held = book["gas" if product == "gas" else "oil"].get(r["month"])
                if held is None:
                    lines.append({"r": r, "product": product, "price": None})
                    continue
                price = held[0]
            kw = dict(transport=r["transport"] if r["state"] == "LA" else 0.0)
            if r["state"] == "LA" and product == "oil":
                kw["variant"] = "la_oil_post2025" if r["completion"] and r["completion"] >= "2025-07-01" else "la_oil_pre2025"
            if r["state"] == "NM":
                kw.update(district_rate=r["district"]["rate"] if r["district"] else 0.0, royalty_pct=r["royalty"], trucking=r["trucking"])

            def alone(rule):
                o = rules.option(r["state"], product, rule)
                param = r["hcg"] if rule == "tx_hcg" and r["hcg"] is not None else None
                if o["group"] == "credit":
                    return tax(rules, r["state"], product, vol, price, credit=rule, credit_period=r["month"], **kw)["with"]
                return tax(rules, r["state"], product, vol, price, option=rule, param=param, period=r["month"], **kw)["with"]

            base = tax(rules, r["state"], product, vol, price, **kw)
            flags = [f for f in met(rules, rows, mine, r, product, vol) if rules.option(r["state"], product, f)]
            saves = {f: base["base"] - alone(f) for f in flags}
            own = [o for o in (rules.option(r["state"], product, t) for t in ticks.get(r["key"], [])) if o]
            rate = next((o for o in own if o["group"] == "rate"), None)
            cred = next((o for o in own if o["group"] == "credit"), None)
            with_ticked = base["base"]
            if rate or cred:
                opt = {}
                if rate:
                    opt.update(option=rate["id"], period=r["month"], param=r["hcg"] if rate["id"] == "tx_hcg" and r["hcg"] is not None else None)
                if cred:
                    opt.update(credit=cred["id"], credit_period=r["month"])
                with_ticked = tax(rules, r["state"], product, vol, price, **kw, **opt)["with"]
            info = ["nm_district"] if r["state"] == "NM" and any(b["rate"] == "district" for b in rules.product("NM", product)["base"]) else []
            lines.append({"r": r, "product": product, "price": price, "base": base["base"], "with": with_ticked,
                          "fees": sum(a for _, a in base["fees"]), "flags": flags, "saves": saves, "info": info,
                          "best": max([0.0] + list(saves.values()))})
    return lines


def inactive_before(mine, r):
    """Months without production before a month: the file's inactive_months, else the run of months just before it that
    the file holds with no oil, gas or condensate."""
    if r["inactive_months"] is not None:
        return r["inactive_months"]
    k, m = 0, shift(r["month"], -1)
    while m in mine and not any((mine[m]["vol"][p] or 0) > 0 for p in PRODUCTS):
        k, m = k + 1, shift(m, -1)
    return k


def met(rules, rows, mine, r, product, vol):
    """The rules whose thresholds the well's own numbers meet (the note's table of "may qualify" flags), in the order the
    note lists them for the state."""
    out = []
    idle = inactive_before(mine, r)
    if r["state"] == "TX":
        if product == "oil":
            # the lease's oil wells over the months of the 90 days ending with the month, as the file holds them
            oil = well_days = water = 0.0
            water_known, held = True, []
            for m in (shift(r["month"], -2), shift(r["month"], -1), r["month"]):
                rs = [q for q in rows if q["state"] == "TX" and q["month"] == m and (q["vol"]["oil"] or 0) > 0]
                if rs:
                    held.append(m)
                for q in rs:
                    oil += q["vol"]["oil"]
                    well_days += days_in(m)
                    if q["water_cut"] is None:
                        water_known = False
                    elif q["water_cut"] >= 100:
                        water = float("inf")
                    else:
                        water += q["vol"]["oil"] * q["water_cut"] / (100 - q["water_cut"])
            if well_days and r["month"] in held:
                per_water = oil / water if water_known and water > 0 else None
                if oil / well_days < 15 or (per_water is not None and per_water < 0.05):
                    out.append("tx_lp_oil")
            if idle >= 24:
                out.append("tx_oil_inactive")
        if product == "gas":
            if r["well_type"] != "oil":
                prior = [m for m in (shift(r["month"], -3), shift(r["month"], -2), shift(r["month"], -1)) if m in mine and (mine[m]["vol"]["gas"] or 0) > 0]
                ms = prior if len(prior) == 3 else [r["month"]]
                if sum(mine[m]["vol"]["gas"] or 0 for m in ms) / sum(days_in(m) for m in ms) <= 90:
                    out.append("tx_lp_gas")
                if r["hcg"] is not None and r["hcg"] > 0 and (r["completion"] is None or months_from(r["completion"], r["month"]) < 120):
                    out.append("tx_hcg")
            if idle >= 24:
                out.append("tx_gas_inactive")
    if r["state"] == "LA":
        since = months_from(r["completion"], r["month"]) if r["completion"] else None
        if r["depth"] is not None and r["depth"] > 15000 and (r["completion"] is None or r["completion"] > "1994-07-31") and (since is None or since < 24):
            out.append({"oil": "la_oil_deep", "gas": "la_gas_deep", "condensate": "la_cond_deep"}[product])
        if product == "oil":
            per_day = vol / (r["days"] if r["days"] is not None else days_in(r["month"]))
            if per_day <= 10:
                out.append("la_stripper")
            if per_day <= 25 and r["water_cut"] is not None and r["water_cut"] >= 50:
                out.append("la_incapable")
        if product == "gas" and r["well_type"] != "oil" and vol / days_in(r["month"]) < 250:
            out.append("la_gas_incapable")
        if product in ("oil", "gas") and idle >= 24:
            out.append("la_oil_inactive" if product == "oil" else "la_gas_inactive")
        if product in ("oil", "gas") and r["horizontal"]:
            limit = 18 if product == "gas" and r["completion"] and r["completion"] >= "2025-07-01" else 24
            if since is None or since < limit:
                out.append("la_oil_horizontal" if product == "oil" else "la_gas_horizontal")
    return out


def best_ticks(rules, lines):
    """"Tick the best flagged rule of each well": for each well and product, the flagged reduced rate that saves the
    most over the file (and the credit, when it saves anything); a rule that saves nothing is not ticked."""
    total = {}
    for l in lines:
        for f in l.get("flags", []):
            k = (l["r"]["key"], l["product"], f)
            total[k] = total.get(k, 0.0) + l["saves"][f]
    best = {}
    for (key, product, f), s in total.items():
        if s <= 0:
            continue
        slot = (key, product, rules.option(key[0], product, f)["group"])
        if slot not in best or best[slot][1] < s:
            best[slot] = (f, s)
    ticks = {}
    for (key, _, _), (f, _) in best.items():
        ticks.setdefault(key, []).append(f)
    return ticks


def lease_sums(lines, rows):
    priced = [l for l in lines if l["price"] is not None]
    wells = {}
    for l in priced:
        w = wells.setdefault(l["r"]["key"], {"base": 0.0, "with": 0.0, "fees": 0.0, "potential": 0.0})
        w["base"] += l["base"]
        w["with"] += l["with"]
        w["fees"] += l["fees"]
        w["potential"] += l["best"]
    for key, w in wells.items():
        w["months"] = len({r["month"] for r in rows if r["key"] == key})
    may = {}
    for l in priced:
        for f in l["flags"]:
            o = may.setdefault((l["r"]["key"], f), {"savings": 0.0, "months": set()})
            o["savings"] += l["saves"][f]
            o["months"].add(l["r"]["month"])
    return {"base": sum(w["base"] for w in wells.values()), "with": sum(w["with"] for w in wells.values()),
            "fees": sum(w["fees"] for w in wells.values()), "potential": sum(w["potential"] for w in wells.values()),
            "wells": wells, "may": may, "unpriced": len(lines) - len(priced)}


def sample_lease(rules, book, out, words):
    path = os.path.join(HERE, "sample_lease.csv")
    with open(path, encoding="utf-8", newline="") as f:
        text = f.read()
    words["lease|sample|sha256"] = hashlib.sha256(text.encode("utf-8")).hexdigest()
    rows = read_lease(text, rules)
    lines = analyse(rules, rows, book)
    s = lease_sums(lines, rows)
    k = "lease|sample|"
    out.update({k + "base": s["base"], k + "with": s["with"], k + "potential": s["potential"], k + "fees": s["fees"], k + "wells": len(s["wells"]),
                k + "lines": len(lines), k + "opportunities": len(s["may"]), k + "rows_to_check": s["unpriced"]})
    for key, w in s["wells"].items():
        out.update({"%swell|%s|months" % (k, key[1]): w["months"], "%swell|%s|base" % (k, key[1]): w["base"], "%swell|%s|potential" % (k, key[1]): w["potential"]})
    for (key, f), o in s["may"].items():
        out["%smay|%s|%s|savings" % (k, key[1], f)] = o["savings"]
        out["%smay|%s|%s|months" % (k, key[1], f)] = len(o["months"])
    for l in lines:
        kk = "%sline|%s|%s|%s|" % (k, l["r"]["well"], l["r"]["month"], l["product"])
        out.update({kk + "price": l["price"], kk + "base": l["base"], kk + "with": l["with"], kk + "best": l["best"], kk + "fees": l["fees"]})
        words[kk + "flags"] = ";".join(sorted(l["flags"] + l["info"]))
    ticked = analyse(rules, rows, book, best_ticks(rules, lines))
    t = lease_sums(ticked, rows)
    out[k + "best_ticked|with"] = t["with"]
    for key, w in t["wells"].items():
        out["%sbest_ticked|well|%s|with" % (k, key[1])] = w["with"]


# --- the real leases (the note, "Load a real lease") --------------------------------------------------------------------

def real_leases(rules, tables, book, out, words):
    path = os.path.join(tables, RRC_TABLE)
    if not os.path.exists(path):
        words["real"] = "%s is not in the tables folder (internal: a warehouse machine holds it)" % RRC_TABLE
        return
    leases = {}
    with open(path, encoding="utf-8", newline="") as f:
        rows = csv.reader(line for line in f if not line.startswith("#"))
        head = next(rows)
        ix = {c: head.index(c) for c in ("entity", "variable", "ts_utc", "value", "x_operator_no", "x_oil_gas_code", "x_wells")}
        for r in rows:
            l = leases.setdefault(r[ix["entity"]], {"id": r[ix["entity"]], "code": r[ix["x_oil_gas_code"]], "wells": int(float(r[ix["x_wells"]])),
                                                    "operator": r[ix["x_operator_no"]], "months": {}})
            l["months"].setdefault(r[ix["ts_utc"]][:7], {})[r[ix["variable"]]] = float(r[ix["value"]])
    out["real|leases"] = len(leases)
    out["real|operators"] = len({l["operator"] for l in leases.values()})

    def total(l, v):
        return sum(m.get(v, 0.0) for m in l["months"].values())

    def every(l, v):
        return len(l["months"]) == 24 and all(m.get(v, 0.0) > 0 for m in l["months"].values())

    oil = [l for l in leases.values() if l["code"] == "O"]
    gas = [l for l in leases.values() if l["code"] == "G"]
    picks = {
        "A": sorted(oil, key=lambda l: (-total(l, "oil_bbl"), l["id"])),
        "B": sorted(gas, key=lambda l: (-total(l, "gas_mcf"), l["id"])),
        "C": sorted((l for l in oil if l["wells"] == 1 and every(l, "oil_bbl")), key=lambda l: (total(l, "oil_bbl"), l["id"])),
        "D": sorted((l for l in gas if every(l, "gas_mcf")), key=lambda l: (total(l, "gas_mcf"), l["id"])),
    }
    for case, ranked in picks.items():
        if not ranked:
            words["real|%s" % case] = "no lease meets the rule"
            continue
        l = ranked[0]
        # the lease as the tool's file: Texas, one well, each month's oil, gas (a gas well's gas, or an oil lease's
        # casinghead gas) and condensate; prices blank; the well type from the RRC's lease code
        rows = []
        for m in sorted(l["months"]):
            v = l["months"][m]
            rows.append({"state": "TX", "well": "one", "key": ("TX", "one"), "month": m,
                         "vol": {"oil": v.get("oil_bbl"), "gas": (v.get("gas_mcf", 0.0) + v.get("casinghead_gas_mcf", 0.0)) if ("gas_mcf" in v or "casinghead_gas_mcf" in v) else None,
                                 "condensate": v.get("condensate_bbl")},
                         "price": {p: None for p in PRODUCTS}, "completion": None, "depth": None, "horizontal": False, "days": None, "water_cut": None,
                         "well_type": "gas" if l["code"] == "G" else "oil", "inactive_months": None, "hcg": None, "district": None,
                         "royalty": 0.0, "trucking": 0.0, "transport": 0.0, "claimed": []})
        lines = analyse(rules, rows, book)
        s = lease_sums(lines, rows)
        k = "real|%s|" % case
        out.update({k + "months": len(l["months"]), k + "lines": len(lines), k + "base": s["base"], k + "with": s["with"], k + "potential": s["potential"],
                    k + "fees": s["fees"], k + "rows_to_check": s["unpriced"]})
        for (_, f), o in s["may"].items():
            out["%smay|%s|savings" % (k, f)] = o["savings"]
            out["%smay|%s|months" % (k, f)] = len(o["months"])


# --- the comparison ---------------------------------------------------------------------------------------------------

def tolerance(key):
    """Half the last digit the page shows: a count is exact; a dollar figure and a price are shown to the cent."""
    last = key.rsplit("|", 1)[-1]
    if last in ("days", "wells", "lines", "opportunities", "rows_to_check", "months", "base_lines", "periods", "leases", "operators", "oil_months", "gas_months") \
            or (key.startswith("rules|") and last in ("base", "options", "fees")):
        return 0.0
    if "|effect|" in key:
        return 0.00005      # a rate is stated to four decimals of a percent or a cent
    return 0.005


def page_figures(tables, now, page_file):
    if page_file:
        with open(page_file, encoding="utf-8") as f:
            return json.load(f)
    node = shutil.which("node")
    if not node:
        raise RuntimeError("node is not on this machine: pass --page FILE (the JSON site/scripts/severance-figures.mjs prints)")
    r = subprocess.run([node, "--import", "./scripts/tsx-register.mjs", os.path.join("scripts", "severance-figures.mjs"), os.path.abspath(tables),
                        now.strftime("%Y-%m-%dT%H:%M:%SZ")], cwd=SITE, capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        raise RuntimeError("severance-figures.mjs failed: %s" % r.stderr[-600:])
    return json.loads(r.stdout)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tables", default=os.path.join(ROOT, "warehouse", "output"))
    ap.add_argument("--page")
    ap.add_argument("--now")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--headline", action="store_true")
    a = ap.parse_args()
    now = datetime.datetime.strptime(a.now, "%Y-%m-%dT%H:%M:%SZ") if a.now else datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
    try:
        rules = Rules(os.path.join(SITE, "data", "severance_rules.json"))
        with open(os.path.join(HERE, "cases.json"), encoding="utf-8") as f:
            cases = json.load(f)["cases"]
        daily = daily_prices(a.tables)
    except (OSError, ValueError, KeyError) as e:
        print("cannot read the inputs: %s" % e)
        return 2
    wti, hh = daily.get("eia:wti_cushing", {}), daily.get("eia:henry_hub", {})
    defaults = {"oil": default_price(wti, now), "gas": default_price(hh, now)}
    out, words = {}, {}
    for kind in ("oil", "gas"):
        d = defaults[kind]
        if d is None:
            words["price|%s" % kind] = "not held: enter a price"
        else:
            out["price|%s|value" % kind], out["price|%s|days" % kind], words["price|%s|month" % kind] = d["value"], d["days"], d["month"]
    calculator(rules, cases, defaults, out)

    if a.headline:
        os.makedirs(os.path.join(HERE, "rows"), exist_ok=True)
        with open(os.path.join(HERE, "rows", "spot_slim.csv"), "w", encoding="utf-8", newline="\n") as f:
            f.write("entity,day,month,value\n")
            for e, by in (("wti_cushing", wti), ("henry_hub", hh)):
                for m in sorted(by):
                    if m >= "2023-01":
                        for i, x in enumerate(by[m]):
                            f.write("%s,%d,%s,%r\n" % (e, i + 1, m, x))
        o, g = defaults["oil"], defaults["gas"]
        print("default oil price, WTI Cushing, mean of %s (USD per bbl): %.2f" % (o["month"], o["value"]))
        print("default gas price, Henry Hub, mean of %s (USD per MMBtu): %.2f" % (g["month"], g["value"]))
        print("Texas oil, 1,000 bbl, tax at the base rate (USD): %.2f" % out["calc|default|base"])
        print("Texas gas, 10,000 Mcf, tax at the base rate (USD): %.2f" % out["calc|TX-gas-base|base"])
        print("Louisiana oil, 1,000 bbl, well completed before July 1, 2025 (USD): %.2f" % out["calc|LA-oil-base|base"])
        print("New Mexico oil, 1,000 bbl, no district chosen (USD): %.2f" % out["calc|NM-oil-base|base"])
        return 0

    rule_list(rules, out)
    words["rules|version"] = rules.version
    for o_id in ("tx_lp_oil", "tx_lp_gas"):
        for p in ("oil", "gas"):
            o = rules.option("TX", p, o_id)
            if o:
                words["rules|%s|latest_period" % o_id] = o["certified"]["as_of"]
    book = {"oil": month_means(wti), "gas": month_means(hh)}
    out["lease|prices|oil_months"], out["lease|prices|gas_months"] = len(book["oil"]), len(book["gas"])
    sample_lease(rules, book, out, words)
    real_leases(rules, a.tables, book, out, words)

    try:
        page = page_figures(a.tables, now, a.page)
    except (RuntimeError, OSError, ValueError) as e:
        print("cannot read the page's figures: %s" % e)
        return 2
    pf, pw = page["figures"], page["words"]
    inside, named, differ = 0, [], []
    for k in sorted(set(out) | set(pf)):
        if k not in out or k not in pf:
            differ.append((k, out.get(k), pf.get(k), "on one side only"))
        elif abs(out[k] - pf[k]) <= tolerance(k) + 1e-9:
            inside += 1
        elif k in NAMED:
            named.append((k, out[k], pf[k], NAMED[k]))
        else:
            differ.append((k, out[k], pf[k], "differs"))
    word_diff = [(k, words.get(k), pw.get(k)) for k in sorted(set(words) | set(pw)) if words.get(k) != pw.get(k)]
    n = inside + len(named) + len(differ)
    for k, ours, theirs, why in named:
        print("named   %s: replication %s, page %s (%s)" % (k, ours, theirs, why))
    for k, ours, theirs, why in differ:
        print("DIFFERS %s: replication %s, page %s (%s)" % (k, ours, theirs, why))
    for k, ours, theirs in word_diff:
        print("WORDS   %s: replication %r, page %r" % (k, ours, theirs))
    print("%d of %d figures inside half the page's last shown digit; %d named; %d differ; %d of %d word keys the same (rules %s, drawn at %s)"
          % (inside, n, len(named), len(differ), len(set(words) | set(pw)) - len(word_diff), len(set(words) | set(pw)), rules.version, page.get("now")))

    if a.write:
        rows = [{"key": k, "replication": out.get(k), "page": pf.get(k), "tolerance": tolerance(k),
                 "state": "named" if k in NAMED else ("inside" if k in out and k in pf and abs(out[k] - pf[k]) <= tolerance(k) + 1e-9 else "differs")}
                for k in sorted(set(out) | set(pf))]
        with open(os.path.join(HERE, "page_figures.json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump({"note": "The severance tool's figures, the replication beside the page's own functions on the same rows (session 7502). A real lease "
                               "(keys real|A to real|D) is named by the rule that picks it, never by its id; only totals are held.",
                       "rules_version": rules.version, "drawn_at": page.get("now"), "inside": inside, "named": len(named), "differ": len(differ),
                       "figures": rows, "words": {k: {"replication": words.get(k), "page": pw.get(k)} for k in sorted(set(words) | set(pw))}}, f, indent=1)
            f.write("\n")
        with open(os.path.join(HERE, "page_figures.csv"), "w", encoding="utf-8", newline="\n") as f:
            w = csv.writer(f, lineterminator="\n")
            w.writerow(["key", "replication", "page", "tolerance", "state"])
            for r in rows:
                w.writerow([r["key"], r["replication"], r["page"], r["tolerance"], r["state"]])
    return 1 if differ or word_diff else 0


if __name__ == "__main__":
    sys.exit(main())
