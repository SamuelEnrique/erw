#!/usr/bin/env python3
"""ERW, Local impact (/impact, the forecast tool): the replication a reader can run (session 7506, chain 304).

Written from the method note alone (docs/methods/forecast.md, sections 2 to 8 and 12; docs/methods/economic_impact.md,
section 1), not from the page's code. It reads

  - the table nlr_jedi_multipliers (JEDI's jobs, earnings and output per MW by technology and state; public, NLR's
    notice kept in its header), from --in-dir (default warehouse/output, or the environment's ERW_OUTPUT_DIR) or --jedi;
  - the parameter files the note names, site/data/forecast/*.json, and the gas rules of site/data/severance_rules.json;
  - this folder's page_figures.json: the addresses (the default page, ten planned projects of EIA-860M, six addresses
    the site's value check reads) and, for each, every figure the page's own view draws
    (site/scripts/impact-figures.mjs reads them from the drawn HTML);

recomputes every figure, and prints each case's count and the first differences. A figure matches when it is inside
half of the page's last shown digit (the file's `tolerance`); a cell the page draws with no number must have no number
here, with the same word; a figure the page does not draw must not exist here.

    python replication/impact/replicate.py --in-dir warehouse/output
    python replication/impact/replicate.py --in-dir warehouse/output --headline   # the five figures of replicate.do
    python replication/impact/replicate.py --in-dir warehouse/output --rows       # writes rows/ for replicate.do
    python replication/impact/replicate.py --figures <another page_figures.json>   # the page's figures drawn elsewhere
    python replication/impact/replicate.py --in-dir warehouse/output --parameters # the parameter table beside the files

Exit 0 when every figure matches, 1 when one does not, 2 when an input cannot be read. Standard library only.
"""
import csv
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
DATA = os.path.join(ROOT, "site", "data", "forecast")
TECHS = ["land_based_wind", "utility_pv", "natural_gas", "geothermal"]
EFFECTS = ["onsite", "supply_chain", "induced", "total"]
MEASURES = ["jobs", "earnings", "output"]
BASE_YEAR = 2025
DEFAULT_START = 2027

# The fields of a scenario (the note, section 12): the name in the address, the least and the most the page takes, and
# whether it is a whole number. Scenario B's names are the same after "b".
FIELDS = [("mw", "mw", 1, 10000, False), ("capex", "cost", 100, 20000, False), ("start", "start", 2026, 2060, True),
          ("build", "build", 1, 10, True), ("life", "life", 1, 60, True), ("local", "local", 0, 200, True),
          ("om", "om", 0, 300, True), ("sales", "sales", 0, 15, False), ("taxable", "taxable", 0, 100, False),
          ("exempt", "exempt", 0, 100, False), ("iaval", "iaval", 0, 1, True), ("optrate", "optrate", 0, 20000, False),
          ("levy", "levy", 0, 200, False), ("own", "own", 0, 10, False), ("ownyears", "ownyears", 1, 60, True),
          ("cf", "cf", 0.01, 1, False), ("ilr", "ilr", 1, 2, False), ("heat", "heat", 5000, 15000, True),
          ("instate", "instate", 0, 100, False), ("gasprice", "gasprice", 0.5, 30, False), ("rate", "rate", 0, 20, False)]


def js_round(v):
    """Round half up, as the page's own rounding does (the note, section 2)."""
    return math.floor(v + 0.5)


def rnd(v, d):
    return js_round(v * 10 ** d) / 10 ** d


def load(name, folder=DATA):
    with open(os.path.join(folder, name), encoding="utf-8") as f:
        return json.load(f)


class Params:
    def __init__(self):
        self.eia = load("eia_capex.json")["technologies"]
        self.jedi_cost = load("jedi_costs.json")["technologies"]
        self.index = load("deflator.json")["index"]
        self.capacity = load("capacity_factors.json")
        self.sales = load("sales_tax.json")["states"]
        self.income = load("income_tax.json")["states"]
        self.property = load("property_rules.json")["states"]
        self.taxable = load("jedi_taxable.json")["technologies"]
        self.gas = load("gas.json")
        self.exempt = load("sales_exemptions.json")["states"]
        self.severance = load("severance_rules.json", os.path.join(ROOT, "site", "data"))["states"]

    def to2025(self, year):
        return self.index[str(BASE_YEAR)] / self.index[str(year)]

    def rules(self, tech, state):
        return [r for r in self.property.get(state, {}).get("rules", []) if tech in r["technologies"]]


def read_jedi(path):
    """{(technology, state): {(phase, effect, measure): per MW}}, in the table's own order of first appearance."""
    out = {}
    with open(path, encoding="utf-8", newline="") as f:
        rows = csv.DictReader(line for line in f if not line.startswith("#"))
        for r in rows:
            if r["variable"] not in MEASURES:
                continue
            p = r["entity"].split(":")
            if len(p) != 5 or p[0] != "nlr_jedi":
                continue
            out.setdefault((p[1], p[2]), {})[(p[3], p[4], r["variable"])] = float(r["value"])
    whole = {}
    for k, v in out.items():
        if len(v) == 24 and all(math.isfinite(x) for x in v.values()):
            whole[k] = v
    return whole


# ---- section 2: the defaults ---------------------------------------------------------------------------------------
def defaults(P, tech, state):
    e = P.eia[tech]
    s = e["states"].get(state)
    if s:  # a state with several cities is their plain mean
        cities = [c["usd_per_kw"] for c in s["cities"]]
        cost_2023 = sum(cities) / len(cities)
    else:
        cost_2023 = e["base_usd_per_kw"]
    if tech == "natural_gas":
        cf = P.gas["capacity_factor"]
    elif tech == "geothermal":
        cf = None
    else:
        c = P.capacity[tech]
        cf = c["states"][state]["median"] if state in c["states"] else c["us"]["median"]
    if tech == "utility_pv":
        c = P.capacity["utility_pv_ilr"]
        ilr = rnd(c["states"][state]["median"] if state in c["states"] else c["us"]["median"], 4)
    else:
        ilr = 1
    st = P.sales.get(state)
    share = P.taxable[tech]["taxable_share"]
    rules = P.rules(tech, state)
    optrate = next((r.get("default_usd_per_mw") for r in rules if r["kind"] == "capacity_option"), None)
    levy = next((r.get("default_levy") for r in rules if r["kind"] == "valuation"), None)
    price = P.gas["price_usd_per_mmbtu"]
    return {
        "tech": tech, "state": state, "mw": e["case_mw"], "capex": rnd(cost_2023 * P.to2025(e["dollar_year"]), 2),
        "start": DEFAULT_START, "build": math.ceil(e["construction_months"] / 12), "life": e["operating_life_years"],
        "local": 100, "om": 100, "rate": 7, "cf": None if cf is None else rnd(cf, 4), "ilr": ilr,
        "sales": rnd((st["state_rate"] + st["avg_local_rate"]) * 100, 4) if st else 0,
        "taxable": None if share is None else rnd(share * 100, 4),
        "exempt": P.exempt.get(state, {}).get(tech, {}).get("exempt_pct", 0), "iaval": False, "optrate": optrate,
        "levy": levy, "own": None, "ownyears": None, "heat": P.gas["heat_rate_btu_per_kwh"], "instate": 0,
        "gasprice": None if price is None else rnd(price, 4),
    }


def scenario_values(query, view, base=None):
    """What the address sets for one scenario: its technology, its state, and the fields given (clamped to the field's range)."""
    pre = "b" if view == "b" else ""
    tech = query.get(pre + "tech")
    state = query.get(pre + "state")
    if tech not in TECHS:
        tech = base[0] if base else "land_based_wind"
    if not state:
        state = base[1] if base else "tx"
    given = {}
    for key, name, lo, hi, whole in FIELDS:
        raw = query.get(pre + name)
        if raw is None or raw == "":
            continue
        try:
            v = float(raw)
        except ValueError:
            continue
        if not math.isfinite(v):
            continue
        v = min(hi, max(lo, v))
        if whole:
            v = js_round(v)
        given[key] = (v == 1) if key == "iaval" else v
    return tech, state, given


def inputs(P, tech, state, given):
    x = defaults(P, tech, state)
    x.update(given)
    return x


# ---- section 6: income tax -----------------------------------------------------------------------------------------
def income_tax(s, w):
    if not s or s.get("none") or not w > 0:
        return 0.0
    taxable = max(0.0, w - (s.get("standard_deduction_single") or 0) - (s.get("personal_exemption_single") or 0))
    tax = 0.0
    b = s["brackets"]
    for i, br in enumerate(b):
        lo = br["over_usd"]
        hi = b[i + 1]["over_usd"] if i + 1 < len(b) else math.inf
        if taxable > lo:
            tax += (min(taxable, hi) - lo) * br["rate"]
    return max(0.0, tax - (s.get("personal_credit_single") or 0))


# ---- section 4: property tax of operating year i (0 is the first) -----------------------------------------------------
def production_rate(r, mw):
    if "usd_per_mwh" in r:
        return r["usd_per_mwh"]
    for t in r.get("tiers", []):
        lo = t.get("min_mw_exclusive", t.get("min_mw_ac_exclusive", 0))
        if mw > lo and ("max_mw" not in t or mw <= t["max_mw"]):
            return t["usd_per_mwh"]
    return 0


def own_share(x, i):
    return max(0.0, 1 - i / x["ownyears"])


def property_tax(P, x, i):
    """(tax or None, taxable value or None, the ids of the rules applied)."""
    rules = P.rules(x["tech"], x["state"])
    mw, option = x["mw"], x["iaval"]
    mwh = None if x["cf"] is None else mw * 8760 * x["cf"]
    spend = x["capex"] * mw * 1000
    has_own = x["own"] is not None and x["ownyears"] is not None and x["ownyears"] > 0
    tax, value, used = 0.0, None, []
    for r in rules:
        if "min_mw" in r and mw < r["min_mw"]:
            continue
        kind = r["kind"]
        if kind == "capacity":
            tax += mw * r.get("usd_per_mw_year", 0)
            used.append(r)
        elif kind == "production":
            rate = production_rate(r, mw)
            if rate > 0 and mwh is not None:
                tax += 0 if i < r.get("exempt_years", 0) else mwh * rate
                used.append(r)
        elif kind == "capacity_option":
            if not option or x["optrate"] is None:
                continue
            if i >= r.get("years", math.inf):
                return None, None, [r]            # after the agreement's years no rule is held
            tax += mw * min(r.get("usd_per_mw_max", math.inf), max(r.get("usd_per_mw_min", 0), x["optrate"]))
            used.append(r)
        elif kind == "exempt_years":
            if i < r.get("years", 0):
                return 0.0, None, [r]             # exempt: 0, a figure the statute gives
        elif kind == "valuation":
            if r.get("requires") == "option" and not option:
                continue
            if x["levy"] is None:
                return None, None, [r]            # the levy is the reader's and is not given
            base = mw * r["usd_per_mw_value"] if "usd_per_mw_value" in r else spend
            if "schedule_pct" in r:
                pct = r["schedule_pct"][i] if i < len(r["schedule_pct"]) else r.get("then_pct", 0)
            else:
                pct = max(r.get("floor_pct", 0), 100 - r.get("depr_pct_per_year", 0) * i)
            value = base * (pct / 100) * r.get("assessment_ratio", 1)
            tax += value * (x["levy"] / 1000)
            used.append(r)
    if used:
        if all(r.get("adds_to_property") for r in used) and has_own:
            share = own_share(x, i)                # the tax adds to the property tax: the reader's own rate beside it
            return tax + spend * share * (x["own"] / 100), spend * share, used + [{"id": "own", "kind": "own"}]
        return tax, value, used
    if has_own:
        share = own_share(x, i)
        calendar = x["start"] + x["build"] + i
        ex = None
        for r in rules:
            if r["kind"] != "own_exempt":
                continue
            if calendar > r.get("until_year", math.inf):
                continue
            if r.get("requires") == "option" and not option:
                continue
            if "years" in r and not (i if r.get("years_from") == "operation" else x["build"] + i) < r["years"]:   # years_from: wip/alt-impact-21
                continue
            if "above_mw" in r and not mw > r["above_mw"]:
                continue
            if "below_mw" in r and not mw < r["below_mw"]:
                continue
            if "op_years" in r and not i < r["op_years"]:
                continue
            if "built_before" in r and not x["start"] + x["build"] <= r["built_before"]:
                continue
            if "min_mw" in r and not mw >= r["min_mw"]:
                continue
            ex = r
            break
        exempt = 0.0
        if ex is not None:
            if "exempt_steps" in ex:
                exempt = next((s["share"] for s in ex["exempt_steps"] if "until" not in s or i < s["until"]), 0)
            else:
                exempt = ex.get("exempt_share", 0)
        taxed = 1 - exempt
        # an abatement of the tax (Nevada, NRS 701A.370: "55 percent of the taxes") leaves the taxable value whole
        # (the note, section 12.1, "An exemption of part of the own rate's base"); an exemption of value takes its share off
        value = spend * share * (1 if ex is not None and ex.get("abates") == "tax" else taxed)
        return spend * share * taxed * (x["own"] / 100), value, [{"id": "own", "kind": "own"}] + ([ex] if ex else [])
    return None, None, []


# ---- section 7: severance on the in-state share of a gas plant's fuel -------------------------------------------------
def severance(P, state, volume_mcf, price_per_mcf):
    st = P.severance.get(state.upper())
    gas = (st or {}).get("products", {}).get("gas")
    if not gas:
        return None
    value = volume_mcf * price_per_mcf        # no royalty, trucking or transport is deducted (none is given)
    total = 0.0
    for b in gas["base"]:
        rate = b["rate"] if isinstance(b["rate"], (int, float)) else 0.0   # New Mexico's district ad valorem: no district given
        total += volume_mcf * rate if b["basis"] == "per_unit" else value * rate
    for f in gas.get("fees", []):
        total += volume_mcf * f["per_unit"]
    return total


# ---- sections 3, 5, 8: the run -----------------------------------------------------------------------------------------
def run(P, jedi, x):
    tech, state = x["tech"], x["state"]
    rows = jedi.get((tech, state))
    cost = P.jedi_cost.get(tech, {}).get("states", {}).get(state, {}).get("cost_usd_per_mw")
    if not rows or not cost:
        return None
    to_now = P.to2025(P.jedi_cost[tech]["dollar_year"])
    spend = x["capex"] * x["mw"] * 1000
    spend_jedi = spend / to_now
    local = x["local"] / 100
    basis_mw = x["mw"] * x["ilr"] if tech == "utility_pv" else x["mw"]
    c, o = {}, {}
    for m in MEASURES:
        k = 1 if m == "jobs" else to_now
        for e in EFFECTS:
            c[(m, e)] = rows[("construction", e, m)] / cost * spend_jedi * local * k
            o[(m, e)] = rows[("operations", e, m)] * basis_mw * local * (x["om"] / 100) * k
    sales_total = None if x["taxable"] is None else spend * (x["taxable"] / 100) * (x["sales"] / 100) * (1 - x["exempt"] / 100)
    sev_year = None
    if tech == "natural_gas" and x["instate"] > 0 and x["gasprice"] is not None:
        mmbtu = x["mw"] * 8760 * x["cf"] * x["heat"] / 1000
        per_mcf = P.gas["btu_per_cf"] / 1000
        sev_year = severance(P, state, mmbtu / per_mcf * (x["instate"] / 100), x["gasprice"] * per_mcf)
    inc = P.income.get(state)
    years = []
    for i in range(int(x["build"])):
        f = 1 / x["build"]
        jobs, earn = c[("jobs", "total")] * f, c[("earnings", "total")] * f
        years.append({"year": x["start"] + i, "phase": "construction", "jobs": jobs, "earnings": earn,
                      "effects": {e: c[("jobs", e)] * f for e in EFFECTS}, "property": None,
                      "sales": None if sales_total is None else sales_total * f,
                      "income": jobs * income_tax(inc, earn / jobs) if jobs > 0 else 0.0, "severance": None, "mwh": None, "value": None})
    held_any, gap, production = False, False, False
    for i in range(int(x["life"])):
        tax, value, used = property_tax(P, x, i)
        if tax is None:
            gap = True
        else:
            held_any = True
            production = any(r["kind"] == "production" for r in used)   # of the last operating year held
        jobs, earn = o[("jobs", "total")], o[("earnings", "total")]
        years.append({"year": x["start"] + x["build"] + i, "phase": "operations", "jobs": jobs, "earnings": earn,
                      "effects": {e: o[("jobs", e)] for e in EFFECTS}, "property": tax, "sales": None,
                      "income": jobs * income_tax(inc, earn / jobs) if jobs > 0 else 0.0,
                      "severance": sev_year if tech == "natural_gas" else None,
                      "mwh": None if x["cf"] is None else x["mw"] * 8760 * x["cf"], "value": value})

    def total(name, pv):
        s, any_ = 0.0, False
        for y in years:
            v = y[name]
            if v is not None:
                any_ = True
                s += v / (1 + x["rate"] / 100) ** (y["year"] - x["start"]) if pv else v
        return s if any_ else None

    whole = held_any and not gap          # a life with a year not held has no property tax total
    sums = {"property": total("property", False) if whole else None, "sales": total("sales", False),
            "income": total("income", False), "severance": None if sev_year is None else total("severance", False)}
    pv = {"earnings": total("earnings", True), "property": total("property", True) if whole else None, "sales": total("sales", True),
          "income": total("income", True), "severance": None if sev_year is None else total("severance", True)}
    pv["taxes"] = (pv["property"] or 0) + (pv["sales"] or 0) + pv["income"] + (pv["severance"] or 0)
    return {"c": c, "o": o, "years": years, "sums": sums, "pv": pv, "production": production}


ROW_FIGURE = {"cjobs": "c:jobs:total", "ojobs": "o:jobs:total", "cearn": "c:earnings:total", "oearn": "o:earnings:total",
              "cout": "c:output:total", "oout": "o:output:total", "prop1": "y1:property", "propl": "sum:property",
              "sales": "sum:sales", "income": "sum:income", "sev": "y1:severance", "pvtax": "pv:taxes", "pvearn": "pv:earnings"}


def table_figures(x, r):
    """Every figure of the A and B table, by its name (None where the page draws no number)."""
    first = next(y for y in r["years"] if y["phase"] == "operations")
    out = {}
    for m in MEASURES:
        out[f"c:{m}:total"] = r["c"][(m, "total")]
        out[f"o:{m}:total"] = r["o"][(m, "total")]
    out["y1:property"] = first["property"]
    out["sum:property"] = r["sums"]["property"]
    out["sum:sales"] = r["sums"]["sales"]
    out["sum:income"] = r["sums"]["income"]
    out["y1:severance"] = first["severance"]
    out["pv:taxes"] = r["pv"]["taxes"]
    out["pv:earnings"] = r["pv"]["earnings"]
    return out


def year_figures(r):
    """The table by year: jobs, earnings, MWh where a production tax is applied, the taxable value where a tax rests on
    one, property, sales, income and severance; a cell with no figure is a dash and is not a figure."""
    has_mwh = r["production"] and any(y["mwh"] is not None for y in r["years"])
    has_value = any(y["value"] is not None for y in r["years"])
    cols = ["jobs", "earnings"] + (["mwh"] if has_mwh else []) + (["value"] if has_value else []) + ["property", "sales", "income", "severance"]
    out = {}
    for y in r["years"]:
        for col in cols:
            if y[col] is not None:
                out[f"year:{y['year']}:{col}"] = y[col]
    return out


def state_figures(P, jedi, tech, state, given):
    """The scenario in every state JEDI gives a figure for: what the address set, each state's own defaults for the rest.
    The ten states with the most construction job-years, the scenario's own and the five with the fewest; the same for the
    taxes' present value."""
    per = []
    for (t, st) in jedi:
        if t != tech or st == "us":
            continue
        r = run(P, jedi, inputs(P, tech, st, given))
        if r is None:
            continue
        per.append((st, r))
    per.sort(key=lambda v: -v[1]["c"][("jobs", "total")])
    out = {}
    n = len(per)
    place = 0
    for i, (st, r) in enumerate(per):
        if i < 10 or i >= n - 5 or st == state:
            place += 1
            for e in ("onsite", "supply_chain", "induced"):
                out[f"states:jobs:{place}:{st}:{e}"] = r["c"][("jobs", e)]
    by_tax = sorted(per, key=lambda v: -v[1]["pv"]["taxes"])
    place = 0
    for i, (st, r) in enumerate(by_tax):
        if i < 10 or i >= n - 5 or st == state:
            place += 1
            out[f"states:taxes:{place}:{st}"] = r["pv"]["taxes"]
    out["states:rank"] = next(i for i, (st, _) in enumerate(per) if st == state) + 1
    out["states:count"] = n
    return out


def default_figures(P, tech, state):
    d = defaults(P, tech, state)
    rules = P.rules(tech, state)
    held = any(r["kind"] not in ("note", "exempt_years", "capacity_option", "own_exempt") and not (r["kind"] == "valuation" and r.get("requires") == "option")
               and not r.get("adds_to_property") for r in rules)
    shown = ["mw", "capex", "start", "build", "life", "local", "om", "sales", "taxable", "exempt", "rate"]
    if any(r.get("requires") == "option" for r in rules):
        shown.append("iaval")
    if any(r["kind"] == "capacity_option" for r in rules):
        shown.append("optrate")
    if any(r["kind"] == "valuation" for r in rules):
        shown.append("levy")
    if not held:
        shown += ["own", "ownyears"]
    if tech != "geothermal":
        shown.append("cf")
    if tech == "utility_pv":
        shown.append("ilr")
    if tech == "natural_gas":
        shown += ["heat", "instate", "gasprice"]
    out = {}
    for k in shown:
        v = d[k]
        out[f"default:{k}"] = (1 if v else 0) if isinstance(v, bool) else v
    return out


def replicate(P, jedi, case):
    """{scenario: {figure: value}} for one address."""
    q = case["query"]
    a = scenario_values(q, "a")
    b = scenario_values(q, "b", base=(a[0], a[1]))
    out = {}
    for view, (tech, state, given) in (("a", a), ("b", b)):
        x = inputs(P, tech, state, given)
        r = run(P, jedi, x)
        f = {}
        if r is not None:
            f.update(table_figures(x, r))
            f.update(year_figures(r))
            f.update(state_figures(P, jedi, tech, state, given))
        f.update(default_figures(P, tech, state))
        out[view] = (x, f)
    return out


def compare(P, jedi, pf):
    page = {}
    for f in pf["figures"]:
        page.setdefault((f["case"], f["scenario"]), {})[f["figure"]] = f
    n = bad = 0
    worst = 0.0
    lines = []
    for case in pf["cases"]:
        ours = replicate(P, jedi, case)
        cn = cbad = 0
        for view in ("a", "b"):
            x, mine = ours[view]
            theirs = page.get((case["id"], view), {})
            seen = set()
            for name, f in theirs.items():
                cn += 1
                if name.startswith("cell:"):
                    row = name[5:]
                    v = mine.get(ROW_FIGURE[row])
                    word = "none" if row == "sev" and x["tech"] != "natural_gas" else "not held"
                    ok = v is None and f["shown"].startswith(word + " (")
                    seen.add(ROW_FIGURE[row])
                    if not ok:
                        cbad += 1
                        lines.append(f"  DIFFERENT {case['id']} {view} {name}: the page draws '{f['shown']}', here {v}")
                    continue
                seen.add(name)
                v = mine.get(name)
                if f["page"] is None or v is None:
                    ok = f["page"] is None and v is None
                else:
                    tol = f["tolerance"] if f["tolerance"] is not None else 0
                    ok = abs(v - f["page"]) <= tol
                    if f["page"]:
                        worst = max(worst, abs(v - f["page"]) / abs(f["page"]))
                if not ok:
                    cbad += 1
                    lines.append(f"  DIFFERENT {case['id']} {view} {name}: the page {f['page']} ({f['shown']}), here {v}")
            for name, v in mine.items():            # a figure here that the page does not draw
                if name in seen or v is None:
                    continue
                if name.startswith("default:") and view not in ("a", "b"):
                    continue
                cn += 1
                cbad += 1
                lines.append(f"  DIFFERENT {case['id']} {view} {name}: here {v}, the page draws none")
        n += cn
        bad += cbad
        print(f"{case['id']}: {cn - cbad} of {cn} ({case['address']})")
    for line in lines[:40]:
        print(line)
    if len(lines) > 40:
        print(f"  ... and {len(lines) - 40} more")
    print(f"largest relative difference from the page's unrounded value: {worst:.2e}")
    print(f"{n - bad} of {n} inside the tolerance")
    return bad


HEADLINE = [("construction jobs, job-years", "c:jobs:total", "{:,.1f}"), ("operating jobs, each year", "o:jobs:total", "{:,.2f}"),
            ("construction earnings, USD of 2025", "c:earnings:total", "{:,.0f}"), ("taxes, present value, USD of 2025", "pv:taxes", "{:,.0f}"),
            ("earnings, present value, USD of 2025", "pv:earnings", "{:,.0f}")]


def headline(P, jedi):
    x = defaults(P, "land_based_wind", "tx")
    f = table_figures(x, run(P, jedi, x))
    print("the default project: 200 MW of land-based wind in Texas, 2027, 1 construction year, 25 operating years, 7 percent real")
    for i, (words, name, fmt) in enumerate(HEADLINE, 1):
        print(f"{i}. {words}: {fmt.format(f[name])}")


def write_rows(P, jedi, jedi_path):
    """rows/ for replicate.do: the default project's 24 rows of the table, and NLR's notice beside them."""
    folder = os.path.join(HERE, "rows")
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, "jedi_tx_wind.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["phase", "effect", "measure", "per_mw"])
        for (phase, effect, measure), v in sorted(jedi[("land_based_wind", "tx")].items()):
            w.writerow([phase, effect, measure, repr(v)])
    with open(jedi_path, encoding="utf-8") as src, open(os.path.join(folder, "NOTICE.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write("jedi_tx_wind.csv is 24 rows of the ERW table nlr_jedi_multipliers (land-based wind, Texas). The table's own header, with NLR's notice:\n\n")
        for line in src:
            if not line.startswith("#"):
                break
            f.write(line)
    print(f"wrote {os.path.join(folder, 'jedi_tx_wind.csv')} and NOTICE.txt")


def parameter_table(P, path):
    """The warehouse table forecast_tool_parameters beside the parameter files it was written from: EIA's capital cost by
    city and base case, each case's size and construction months, JEDI's taxable shares and default costs. A row this
    check cannot place in a file (a location factor, an operating life, a heat rate, the gas rows) is counted as not compared."""
    n = same = skipped = 0
    with open(path, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(line for line in f if not line.startswith("#")):
            p = r["entity"].split(":")
            kind, var, want = p[1], r["variable"], None
            if kind == "eia_capex" and var == "overnight_cost":
                e = P.eia[p[2]]
                if p[3] == "us":
                    want = e["base_usd_per_kw"]
                else:
                    city = r["x_detail"].split(",")[0]
                    want = next((c["usd_per_kw"] for c in e["states"].get(p[3].split("_")[0], {}).get("cities", []) if c["city"] == city), None)
            elif kind == "eia_capex" and var in ("construction_months", "case_mw") and p[3] == "us":
                want = P.eia[p[2]].get(var)
            elif kind == "jedi_taxable":
                want = P.taxable[p[2]]["taxable_share"]
            elif kind == "jedi_costs":
                want = P.jedi_cost[p[2]]["states"].get(p[3], {}).get("cost_usd_per_mw")
            if want is None:
                skipped += 1
                continue
            n += 1
            same += abs(float(r["value"]) - want) <= 1e-6 * max(1.0, abs(want))
    print(f"forecast_tool_parameters beside the parameter files: {same} of {n} equal; {skipped} rows of the table not compared")
    return n - same


def main(argv):
    in_dir = os.environ.get("ERW_OUTPUT_DIR") or os.path.join(ROOT, "warehouse", "output")
    jedi_path = None
    figures = os.path.join(HERE, "page_figures.json")
    args = list(argv)
    while args:
        a = args.pop(0)
        if a == "--in-dir" and args:
            in_dir = args.pop(0)
        elif a == "--jedi" and args:
            jedi_path = args.pop(0)
        elif a == "--figures" and args:
            figures = args.pop(0)
        elif a in ("--headline", "--rows", "--parameters"):
            pass
        else:
            print(__doc__)
            return 2
    jedi_path = jedi_path or os.path.join(in_dir, "nlr_jedi_multipliers.csv")
    try:
        P = Params()
        jedi = read_jedi(jedi_path)
        pf = load(os.path.basename(figures), os.path.dirname(os.path.abspath(figures)))
    except (OSError, ValueError, KeyError) as e:
        print(f"an input could not be read: {e}")
        return 2
    if not jedi:
        print(f"no row of jobs, earnings or output in {jedi_path}")
        return 2
    if "--parameters" in argv:
        try:
            return 1 if parameter_table(P, os.path.join(in_dir, "forecast_tool_parameters.csv")) else 0
        except OSError as e:
            print(f"the table could not be read: {e}")
            return 2
    if "--rows" in argv:
        write_rows(P, jedi, jedi_path)
        return 0
    if "--headline" in argv:
        headline(P, jedi)
        return 0
    return 1 if compare(P, jedi, pf) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
