"""Replication of /impact's datacenter (chain 740, lab-desktop window 3, session 10804).

Energy Research Warehouse (ERW). A second implementation of docs/methods/forecast.md, section 13, in Python (standard
library only), from the note's words, not from site/lib/dcimpact.ts. It reads the parameter files of site/data/forecast/
(datacenter_rules.json, datacenter_wages.json, sales_tax.json, income_tax.json, deflator.json) and the cases of
page_figures.json (each case's full inputs and the page's figures, drawn by site/scripts/dc-figures.mjs), recomputes every
year's figures and every total, and prints how many agree. Exit 0 when every figure agrees within 1e-9 of its size.

Run: python replication/impact/datacenter/replicate.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
DATA = os.path.join(ROOT, "site", "data", "forecast")


def load(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as f:
        return json.load(f)


RULES, WAGES, SALES, INCOME, DEFL = (load(n) for n in ("datacenter_rules.json", "datacenter_wages.json", "sales_tax.json",
                                                         "income_tax.json", "deflator.json"))


def income_tax(state, wage):
    """Section 6: one single filer's tax on the wage, by the state's 2026 brackets."""
    s = INCOME["states"].get(state)
    if not s or s.get("none") or wage <= 0:
        return 0.0
    taxable = max(0.0, wage - (s.get("standard_deduction_single") or 0) - (s.get("personal_exemption_single") or 0))
    tax = 0.0
    b = s["brackets"]
    for i, br in enumerate(b):
        hi = b[i + 1]["over_usd"] if i + 1 < len(b) else float("inf")
        if taxable > br["over_usd"]:
            tax += (min(taxable, hi) - br["over_usd"]) * br["rate"]
    return max(0.0, tax - (s.get("personal_credit_single") or 0))


def ratios(state, phase):
    """13.1: Virginia's indirect and induced per direct, jobs and earnings (JLARC D-3, D-5); None elsewhere."""
    m = RULES["multipliers"].get(state)
    if not m:
        return None
    p = m[phase]
    return {"jobs": [p["indirect"]["jobs"] / p["direct"]["jobs"], p["induced"]["jobs"] / p["direct"]["jobs"]],
            "earn": [p["indirect"]["earnings_musd"] / p["direct"]["earnings_musd"], p["induced"]["earnings_musd"] / p["direct"]["earnings_musd"]]}


def year_jobs(onsite, wage, r):
    if r is None:
        return onsite, onsite * wage
    e = onsite * wage
    return onsite * (1 + r["jobs"][0] + r["jobs"][1]), e * (1 + r["earn"][0] + r["earn"][1])


def run(x):
    st = x["state"]
    rule = RULES["states"].get(st, {})
    ex = rule.get("sales_exemption")
    prop = rule.get("property")
    elec_rule = rule.get("electricity")
    total = x["invest"] * 1e6
    building, equipment = total * x["bld"] / 100, total * x["eq"] / 100
    rate = x["sales"] / 100

    # 13.1, the exemption: investment (spent in the build's whole years before the statute's year, where it names one)
    # and permanent jobs at least the statute's; then the years it runs
    eligible = False
    if ex:
        before = ex.get("invest_before_year")
        spent = total if before is None else total * max(0, min(x["build"], before - x["start"])) / x["build"]
        eligible = spent >= ex["min_investment_usd"] and x["perm"] >= ex["min_jobs"]

    def runs_in(year):
        if ex.get("last_year") is not None and year > ex["last_year"]:
            return False
        if ex.get("term_years") is not None and year >= x["start"] + ex["term_years"]:
            return False
        return True

    def sales(equip, build, year):
        on_building = 0.0 if x["matshare"] is None else build * x["matshare"] / 100 * rate
        on_equipment = equip * rate
        forgone = 0.0
        if eligible and x["dcex"] and runs_in(year):
            forgone = (on_equipment if "equipment" in ex["covers"] else 0.0) + (on_building if "construction" in ex["covers"] else 0.0)
        return on_equipment + on_building, forgone

    elec = None
    if elec_rule and x["mwh"] is not None:
        month = x["mwh"] * 1000 / 12
        tax, lo = 0.0, 0.0
        for blk in elec_rule["blocks"]:
            hi = float("inf") if blk["upto_kwh"] is None else blk["upto_kwh"]
            tax += max(0.0, min(month, hi) - lo) * blk["usd_per_kwh"]
            lo = hi
        elec = 12 * tax

    years = []
    cj, ce = year_jobs(x["cons"], x["conswage"], ratios(st, "construction"))
    for i in range(x["build"]):
        y = x["start"] + i
        sb, fg = sales(equipment / x["build"], building / x["build"], y)
        years.append({"year": y, "phase": "construction", "jobs": cj, "earnings": ce, "property": None, "propb": None, "prope": None,
                      "salesbefore": sb, "forgone": fg, "sales": sb - fg, "income": cj * income_tax(st, ce / cj) if cj > 0 else 0.0, "elec": None})
    oj, oe = year_jobs(x["perm"], x["opwage"], ratios(st, "operations"))
    for i in range(x["life"]):
        y = x["start"] + x["build"] + i
        bought = equipment if x["refresh"] > 0 and i > 0 and i % x["refresh"] == 0 else 0.0
        sb, fg = sales(bought, 0.0, y)
        keep = max(0.0, 1 - i / x["bldyears"]) if x["bldyears"] else 1.0
        cut = 1 - x["abate"] / 100 if x["abate"] > 0 and (x["abateyears"] is None or i < x["abateyears"]) else 1.0
        br = prop["building_ratio"] if prop else 1.0
        er = prop["equipment_ratio"] if prop else 1.0
        pb = None if x["brate"] is None else building * keep * br * x["brate"] / 100 * cut
        pe = None if x["erate"] is None else equipment * er * x["erate"] / 100 * cut
        years.append({"year": y, "phase": "operations", "jobs": oj, "earnings": oe,
                      "property": pb + pe if pb is not None and pe is not None else None, "propb": pb, "prope": pe,
                      "salesbefore": sb, "forgone": fg, "sales": sb - fg, "income": oj * income_tax(st, oe / oj) if oj > 0 else 0.0, "elec": elec})

    def total_of(k, pv):
        vals = [(y["year"], y[k]) for y in years if y[k] is not None]
        if not vals:
            return None
        return sum(v / (1 + x["rate"] / 100) ** (yr - x["start"]) if pv else v for yr, v in vals)

    sums = {k: total_of(k, False) for k in ("jobs", "earnings", "property", "propb", "prope", "salesbefore", "forgone", "sales", "income", "elec")}
    pvs = {k: total_of(k, True) for k in ("earnings", "property", "propb", "prope", "salesbefore", "forgone", "sales", "income", "elec")}
    if any(y["phase"] == "operations" and y["property"] is None for y in years):
        sums["property"] = None
        pvs["property"] = None
    pvs["taxes"] = (pvs["property"] or 0.0) + (pvs["sales"] or 0.0) + pvs["income"] + (pvs["elec"] or 0.0)
    return years, sums, pvs


def same(a, b):
    if a is None or b is None:
        return a is None and b is None
    return abs(a - b) <= 1e-9 * max(1.0, abs(b))


def main():
    with open(os.path.join(HERE, "page_figures.json"), encoding="utf-8") as f:
        cases = json.load(f)["cases"]
    n = bad = 0
    for c in cases:
        years, sums, pvs = run(c["inputs"])
        for mine, page in zip(years, c["years"]):
            for k, v in page.items():
                if k in ("year", "phase"):
                    continue
                n += 1
                if not same(mine[k], v):
                    bad += 1
                    print(f"{c['id']} {page['year']} {k}: replication {mine[k]} page {v}")
        for k, v in c["sums"].items():
            n += 1
            if not same(sums[k], v):
                bad += 1
                print(f"{c['id']} sum {k}: replication {sums[k]} page {v}")
        for k, v in c["pv"].items():
            n += 1
            if not same(pvs[k], v):
                bad += 1
                print(f"{c['id']} pv {k}: replication {pvs[k]} page {v}")
    print(f"{n - bad} of {n} figures agree")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
