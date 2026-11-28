"""Session 11404 (chain 770): an independent restatement of /impact's datacenter, written from docs/methods/forecast.md
section 13 (13.1 and 13.2) and the parameter files' own words, not from site/lib/dcimpact.ts. Standard library only.

It recomputes (1) the five medians the defaults rest on, from the announced rows; (2) every figure of a run, by year,
for the cases in cases.json (written by dc_page.mjs, which runs the page's own code on the same inputs); and writes
restated.json for compare.py.

Run from the worktree's root: python runs/c770/s11404/restate.py
"""
import json
import math
import statistics

D = "site/data/forecast/"
load = lambda n: json.load(open(D + n, encoding="utf-8"))
ANN, RULES, WAGES, SALES, INCOME, DEFL = (load("datacenter_announced.json"), load("datacenter_rules.json"), load("datacenter_wages.json"),
                                          load("sales_tax.json"), load("income_tax.json"), load("deflator.json"))
IDX = DEFL["index"]


def to2025(v, y):
    # 13.2 / the builder's words: each announcement's dollars by the GDP price index; a year not held (2026) as 2025
    return v * IDX["2025"] / IDX[str(y)] if str(y) in IDX else v


# ---- (1) the medians ------------------------------------------------------------------------------------------------
def medians():
    mw, inv, pmw, pbn, cbn = [], [], [], [], []
    for r in ANN["rows"]:
        if r.get("to_date"):
            continue
        m = (r.get("mw") or {}).get("value")
        i = r.get("investment")
        gen = r.get("investment_includes_generation") or bool(r.get("investment_partial"))
        i25 = to2025(i["value"], i.get("year", 2025)) if i and not gen else None
        p = r.get("permanent_jobs")
        pok = p is not None and "kind not stated" not in p["measure"]
        c = r.get("construction_jobs")
        if m:
            mw.append(m)
        if m and i25:
            inv.append(i25 / 1e6 / m)
        if m and pok:
            pmw.append(p["value"] / m)
        if i25 and pok:
            pbn.append(p["value"] / (i25 / 1e9))
        if i25 and c:
            cbn.append(c["value"] / (i25 / 1e9))
    out = {}
    for k, v in (("mw_stated", mw), ("investment_per_mw", inv), ("permanent_jobs_per_mw", pmw), ("permanent_jobs_per_billion", pbn),
                 ("construction_jobs_per_billion", cbn)):
        out[k] = {"n": len(v), "median": statistics.median(v), "mean": statistics.mean(v), "low": min(v), "high": max(v)}
    return out


# ---- (2) a run ------------------------------------------------------------------------------------------------------
def rnd(v, d):
    # the page rounds half away from zero on positive numbers (Math.round): floor(v * 10^d + 0.5)
    return math.floor(v * 10 ** d + 0.5) / 10 ** d


def defaults(state, s, med):
    mw = s.get("mw", rnd(med["mw_stated"]["median"], 3))
    invest = s.get("invest", rnd(mw * med["investment_per_mw"]["median"], 2))
    st = SALES["states"].get(state)
    w = WAGES["states"].get(state, {})
    k = IDX["2025"] / IDX[str(WAGES["year"])]
    x = {"state": state, "mw": mw, "invest": invest, "start": 2027, "build": math.ceil(RULES["build"]["months"] / 12), "life": RULES["life"]["years"],
         "bld": RULES["split"]["building_pct"], "eq": RULES["split"]["equipment_pct"], "land": RULES["split"]["land_pct"], "refresh": RULES["refresh"]["years"],
         "perm": rnd(mw * med["permanent_jobs_per_mw"]["median"], 1), "cons": rnd(invest / 1000 * med["construction_jobs_per_billion"]["median"], 1),
         "opwage": rnd(w["operations"]["per_job_usd"] * k, 0) if "operations" in w else None,
         "conswage": rnd(w["construction"]["per_job_usd"] * k, 0) if "construction" in w else None,
         "sales": rnd((st["state_rate"] + st["avg_local_rate"]) * 100, 4) if st else 0, "matshare": None, "dcex": True,
         "brate": None, "erate": None, "bldyears": None, "abate": 0, "abateyears": None, "mwh": None, "rate": 7, "eqv1": 100, "eqstep": 0, "eqfloor": 0}
    x.update(s)
    return x


def income_tax(st, w):
    # section 6: one single filer on the average wage; deduction and exemption off the wage, brackets, then any credit
    if not st or st.get("none") or w <= 0:
        return 0.0
    t = max(0.0, w - (st.get("standard_deduction_single") or 0) - (st.get("personal_exemption_single") or 0))
    b = st["brackets"]
    tax = 0.0
    for i, br in enumerate(b):
        hi = b[i + 1]["over_usd"] if i + 1 < len(b) else math.inf
        if t > br["over_usd"]:
            tax += (min(t, hi) - br["over_usd"]) * br["rate"]
    return max(0.0, tax - (st.get("personal_credit_single") or 0))


def run(x):
    rule = RULES["states"].get(x["state"], {})
    ex = rule.get("sales_exemption")
    usd = x["invest"] * 1e6
    bld, eqc = usd * x["bld"] / 100, usd * x["eq"] / 100
    # supply chain and induced: the study's indirect and induced over direct, applied to on-site jobs and earnings
    mult = RULES["multipliers"].get(x["state"])

    def phase(n, wage, ph):
        j = {"onsite": n, "supply_chain": 0.0, "induced": 0.0}
        e = {"onsite": n * wage, "supply_chain": 0.0, "induced": 0.0}
        if mult:
            m = mult[ph]
            for eff, key in (("supply_chain", "indirect"), ("induced", "induced")):
                j[eff] = n * m[key]["jobs"] / m["direct"]["jobs"]
                e[eff] = n * wage * m[key]["earnings_musd"] / m["direct"]["earnings_musd"]
        j["total"] = j["onsite"] + j["supply_chain"] + j["induced"]
        e["total"] = e["onsite"] + e["supply_chain"] + e["induced"]
        return j, e

    cj, ce = phase(x["cons"], x["conswage"], "construction")
    oj, oe = phase(x["perm"], x["opwage"], "operations")
    # eligibility: investment and permanent jobs against the statute's thresholds (13.1); MW, start and spending-before rules
    elig = False
    if ex and not ex.get("discretionary"):
        spent = usd
        if "invest_before_year" in ex:
            spent = usd * max(0, min(x["build"], ex["invest_before_year"] - x["start"])) / x["build"]
        elig = (spent >= ex["min_investment_usd"] and x["perm"] >= ex["min_jobs"]
                and ("min_mw" not in ex or x["mw"] >= ex["min_mw"])
                and ("start_before_year" not in ex or x["start"] < ex["start_before_year"]))
    applied = elig and x["dcex"]

    def runs_in(y):
        if not ex:
            return False
        if "last_year" in ex and y > ex["last_year"]:
            return False
        term = ex.get("term_years")
        big = ex.get("term_years_big")
        if big and usd >= big["min_investment_usd"]:
            term = big["years"]
        return term is None or y < x["start"] + term

    share = 1.0
    if ex and ex.get("rate_part") == "state":
        share = min(1.0, SALES["states"][x["state"]]["state_rate"] * 100 / (x["sales"] or 1))

    def sales(eq_bought, bld_bought, y):
        bt = 0.0 if x["matshare"] is None else bld_bought * x["matshare"] / 100 * x["sales"] / 100
        et = eq_bought * x["sales"] / 100
        f = 0.0
        if applied and runs_in(y):
            f = ((et if "equipment" in ex["covers"] else 0) + (bt if "construction" in ex["covers"] else 0)) * share
        return et + bt, f, et + bt - f

    prop = rule.get("property")
    if prop and "min_investment_usd" in prop and usd < prop["min_investment_usd"]:
        prop = None
    br, er = (prop["building_ratio"], prop["equipment_ratio"]) if prop else (1, 1)
    inc_st = INCOME["states"].get(x["state"])
    elec = None
    el = rule.get("electricity")
    if el and x["mwh"] is not None:
        mk = x["mwh"] * 1000 / 12
        t, lo = 0.0, 0.0
        for b in el["blocks"]:
            hi = math.inf if b["upto_kwh"] is None else b["upto_kwh"]
            if mk > lo:
                t += (min(mk, hi) - lo) * b["usd_per_kwh"]
            lo = hi
        elec = t * 12
        alt = el.get("elective")
        if alt and x["mwh"] * 1000 >= alt["min_annual_kwh"]:
            yk, t2, lo = x["mwh"] * 1000, 0.0, 0.0
            for b in alt["annual_blocks"]:
                hi = math.inf if b["upto_kwh"] is None else b["upto_kwh"]
                if yk > lo:
                    t2 += (min(yk, hi) - lo) * b["usd_per_kwh"]
                lo = hi
            elec = min(elec, t2)
    years = []
    for i in range(x["build"]):
        y = x["start"] + i
        b, f, p = sales(eqc / x["build"], bld / x["build"], y)
        years.append({"year": y, "jobs": cj["total"], "earnings": ce["total"], "onsite": cj["onsite"], "equipment": eqc / x["build"],
                      "property": None, "propb": None, "prope": None, "salesbefore": b, "forgone": f, "sales": p,
                      "income": cj["total"] * income_tax(inc_st, ce["total"] / cj["total"]) if cj["total"] > 0 else 0.0, "elec": None})
    for i in range(x["life"]):
        y = x["start"] + x["build"] + i
        bought = eqc if (x["refresh"] > 0 and i > 0 and i % x["refresh"] == 0) else 0.0
        b, f, p = sales(bought, 0.0, y)
        bv = bld * (max(0.0, 1 - i / x["bldyears"]) if x["bldyears"] else 1)
        age = i % x["refresh"] if x["refresh"] > 0 else i
        ev = eqc * max(x["eqfloor"], x["eqv1"] - x["eqstep"] * age) / 100
        keep = 1 - x["abate"] / 100 if x["abate"] > 0 and (x["abateyears"] is None or i < x["abateyears"]) else 1
        pb = None if x["brate"] is None else bv * br * x["brate"] / 100 * keep
        pe = None if x["erate"] is None else ev * er * x["erate"] / 100 * keep
        years.append({"year": y, "jobs": oj["total"], "earnings": oe["total"], "onsite": oj["onsite"], "equipment": bought,
                      "property": pb + pe if pb is not None and pe is not None else None, "propb": pb, "prope": pe,
                      "salesbefore": b, "forgone": f, "sales": p,
                      "income": oj["total"] * income_tax(inc_st, oe["total"] / oj["total"]) if oj["total"] > 0 else 0.0, "elec": elec})
    disc = lambda y: (1 + x["rate"] / 100) ** -(y - x["start"])

    def tot(k, pv):
        vals = [(yr[k], yr["year"]) for yr in years if yr[k] is not None]
        return sum(v * (disc(y) if pv else 1) for v, y in vals) if vals else None

    streams = ["earnings", "propb", "prope", "salesbefore", "forgone", "sales", "income", "elec"]
    S = {k: tot(k, False) for k in streams}
    PV = {k: tot(k, True) for k in streams}
    allprop = all(yr["property"] is not None for yr in years[x["build"]:])
    S["property"] = tot("property", False) if allprop else None
    PV["property"] = tot("property", True) if allprop else None
    S["jobs"] = sum(yr["jobs"] for yr in years)
    PV["taxes"] = (PV["property"] or 0) + (PV["sales"] or 0) + PV["income"] + (PV["elec"] or 0)
    y1 = years[x["build"]]
    return {"x": x, "eligible": elig, "applied": applied, "cjobs": cj["total"] * x["build"], "cearn": ce["total"] * x["build"],
            "ojobs": oj["total"], "oearn": oe["total"], "c_onsite": cj["onsite"] * x["build"], "o_onsite": oj["onsite"],
            "sum": S, "pv": PV, "y1": {k: y1[k] for k in ("property", "propb", "prope", "income", "elec", "sales")}, "years": years}


if __name__ == "__main__":
    med = medians()
    cases = json.load(open("runs/c770/s11404/cases.json"))
    out = {"medians": med, "runs": {}}
    rows = {r["id"]: r for r in ANN["rows"]}
    for c in cases:
        s = dict(c["set"])
        if c.get("project"):
            # the picker's words: "Picking one sets the MW, the investment (in 2025 dollars), the permanent jobs and the
            # construction workers the document states; a figure it does not state keeps its default"
            r = rows[c["project"]]
            pick = {}
            if r.get("mw"):
                pick["mw"] = r["mw"]["value"]
            i = r.get("investment")
            if i and not r.get("investment_includes_generation") and not r.get("investment_partial"):
                pick["invest"] = rnd(to2025(i["value"], i.get("year", 2025)) / 1e6, 2)
            p = r.get("permanent_jobs")
            if p and "kind not stated" not in p["measure"]:
                pick["perm"] = p["value"]
            if r.get("construction_jobs"):
                pick["cons"] = r["construction_jobs"]["value"]
            pick.update(s)
            s = pick
        x = defaults(c["state"], s, med)
        out["runs"][c["id"]] = run(x)
    json.dump(out, open("runs/c770/s11404/restated.json", "w"), indent=0)
    print("medians:", {k: (v["n"], round(v["median"], 6), "mean", round(v["mean"], 4)) for k, v in med.items()})
    print("runs:", len(out["runs"]))
