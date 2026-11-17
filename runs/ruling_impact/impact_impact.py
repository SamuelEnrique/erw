#!/usr/bin/env python3
"""ERW, ruling impact for /impact (session 7575, 17 November 2026).

The 36 lines marked "Changes a figure" under /impact in docs/reviews/rulings-for-samuel-2026-11-17.md (branch
wip/7560-six-reads). The engine is replication/impact/replicate.py (imported: defaults, inputs, run, property_tax,
severance), on warehouse/output/nlr_jedi_multipliers.csv and the parameter files site/data/forecast/*.json and
site/data/severance_rules.json. The other choice of a line is put into a copy of the parameters, never into the files.

    .venv/Scripts/python.exe runs/ruling_impact/impact_impact.py
"""
import copy
import importlib.util
import json
import os
import statistics

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
spec = importlib.util.spec_from_file_location("rep", os.path.join(ROOT, "replication", "impact", "replicate.py"))
rep = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rep)
P0 = rep.Params()
JEDI = rep.read_jedi(os.path.join(ROOT, "warehouse", "output", "nlr_jedi_multipliers.csv"))


def M(v):
    return "none" if v is None else f"{v / 1e6:,.2f} million"


def pct(a, b):
    return "n/a" if not a else f"{(b - a) / a * 100:+.1f}%"


def go(tech, state, P=None, **given):
    P = P or P0
    x = rep.inputs(P, tech, state, given)
    return x, rep.run(P, JEDI, x)


def life_value(r):
    return sum(y["value"] for y in r["years"] if y["phase"] == "operations" and y["value"] is not None)


def line(n, text):
    print(f"\n== line {n}: {text}")


def rule_of(P, state, rid):
    return next(r for r in P.property[state]["rules"] if r["id"] == rid)


NV = dict(mw=36, capex=4956.83, start=2026, iaval=True, own=1.0917, ownyears=60)    # Lone Mountain Geothermal, the read's case 1
IA = dict(mw=252, start=2027, iaval=True, levy=30)                                   # Silver Queen, the read's case 3
TXG = dict(mw=1445, start=2027, instate=100)                                         # CPV Basin Ranch, the read's case 4

# 1. Nevada's abatement: the taxable value whole or 45 percent
line(1, "Nevada, local option on and a rate typed: 'Taxable value' whole (the change made) or 45 percent")
x, r = go("geothermal", "nv", **NV)
P = copy.deepcopy(P0)
rule_of(P, "nv", "nv_renewable_abatement").pop("abates")
_, r2 = go("geothermal", "nv", P, **NV)
y0 = next(y for y in r["years"] if y["phase"] == "operations")
y1 = next(y for y in r2["years"] if y["phase"] == "operations")
moved = sum(1 for a, b in zip(r["years"], r2["years"]) if a["value"] != b["value"])
print(f"first operating year {y0['year']}: whole {M(y0['value'])} against 45 percent {M(y1['value'])}; years whose cell moves: {moved}; "
      f"property tax over the life {M(r['sums']['property'])} and {M(r2['sums']['property'])} (no tax moves); taxes, present value {M(r['pv']['taxes'])} and {M(r2['pv']['taxes'])}")

# 2. 'Taxes, present value' made of taxes not held
line(2, "'Taxes, present value' adds only the taxes with a figure: how many default cases read a 0 or a partial sum")
zero_missing, partial, total = [], 0, 0
for (tech, st) in sorted(JEDI):
    if st == "us":
        continue
    xx, rr = go(tech, st)
    if rr is None:
        continue
    total += 1
    pv = rr["pv"]
    missing = [k for k in ("property", "sales", "severance") if pv[k] is None and not (k == "severance" and tech != "natural_gas")]
    if missing:
        partial += 1
    if pv["taxes"] == 0 and missing:
        zero_missing.append(f"{tech}/{st}")
x, r = go("geothermal", "nv", mw=36, capex=4956.83, start=2026)
print(f"Lone Mountain as opened: property {r['pv']['property']}, sales {r['pv']['sales']}, income {r['pv']['income']}, severance {r['pv']['severance']}: the cell reads USD {r['pv']['taxes']:,.0f}")
print(f"of {total} default cases (technology and state): {partial} leave a tax out of the sum; {len(zero_missing)} read USD 0 made of taxes not held: {', '.join(zero_missing)}")
x, r = go("land_based_wind", "tx")
print(f"the page as it opens (Texas wind): {M(r['pv']['taxes'])}, all of it sales and use tax ({M(r['pv']['sales'])}); property not held, income 0")

# 3. Nevada's 20 years counted from the first operating year
line(3, "Nevada's 20 abated years from the first construction year (default) or from the first operating year")
x, r = go("geothermal", "nv", **NV)
P = copy.deepcopy(P0)
rr_ = rule_of(P, "nv", "nv_renewable_abatement")
rr_["years"] = rr_["years"] + int(x["build"])
_, r2 = go("geothermal", "nv", P, **NV)
ops = [y for y in r["years"] if y["phase"] == "operations"][:20]
ops2 = [y for y in r2["years"] if y["phase"] == "operations"][:20]
print(f"construction years {int(x['build'])}; the first 20 operating years ({ops[0]['year']} to {ops[-1]['year']}): paid {M(sum(y['property'] for y in ops))} "
      f"against {M(sum(y['property'] for y in ops2))} (the Department of Taxation: USD 15,034,766); over the life {M(r['sums']['property'])} against {M(r2['sums']['property'])}; "
      f"property, present value {M(r['pv']['property'])} against {M(r2['pv']['property'])} ({pct(r['pv']['property'], r2['pv']['property'])})")

# 4. geothermal's taxable share
line(4, "Geothermal's taxable share of spending: not given (default) or one plant's 3.3 or 48 percent")
x, r = go("geothermal", "nv", mw=36, capex=4956.83, start=2026)
for share in (3.3, 48):
    _, r2 = go("geothermal", "nv", mw=36, capex=4956.83, start=2026, taxable=share)
    print(f"Lone Mountain, {share} percent: sales and use tax 'not held' -> {M(r2['sums']['sales'])}; taxes, present value USD {r['pv']['taxes']:,.0f} -> {M(r2['pv']['taxes'])}")
n_geo = sum(1 for (t, s) in JEDI if t == "geothermal" and s != "us")
print(f"every state's geothermal case moves the same way ({n_geo} states with JEDI rows)")

# 5. New Mexico's district ad valorem production tax on gas
line(5, "New Mexico gas plant, all fuel in state: severance with no district (default) or with a district's ad valorem rate")
x, r = go("natural_gas", "nm", instate=100)
nm = P0.severance["NM"]["products"]["gas"]
dist = next(b for b in nm["base"] if b["rate"] == "district")["districts"]["list"]
rates = sorted(d["rate"] for d in dist)
base = next(y for y in r["years"] if y["phase"] == "operations")["severance"]
mmbtu = x["mw"] * 8760 * x["cf"] * x["heat"] / 1000
mcf = mmbtu / (P0.gas["btu_per_cf"] / 1000)
value = mcf * x["gasprice"] * P0.gas["btu_per_cf"] / 1000
for label, rt in (("lowest", rates[0]), ("median", statistics.median(rates)), ("highest", rates[-1])):
    print(f"{label} district ({rt * 100:.2f} percent): severance each year {M(base)} -> {M(base + value * rt)} ({pct(base, base + value * rt)})")
print(f"{len(rates)} districts held in severance_rules.json; the gas plant's value of fuel a year {M(value)}")

# 6. Louisiana's gas severance from a held table's rate
line(6, "Louisiana gas plant, all fuel in state: severance drawn (default) or held because its rate's table is held")
x, r = go("natural_gas", "la", instate=100)
y = next(y for y in r["years"] if y["phase"] == "operations")
print(f"severance each year {M(y['severance'])} -> 'license needed' (blank); over the life {M(r['sums']['severance'])}; taxes, present value {M(r['pv']['taxes'])} -> {M(r['pv']['taxes'] - r['pv']['severance'])} "
      f"({pct(r['pv']['taxes'], r['pv']['taxes'] - r['pv']['severance'])})")

# 7. on-site jobs
line(7, "Jobs: the three effects added (default) or the on-site figure beside them")
for name, (t, s, g) in (("Lone Mountain", ("geothermal", "nv", NV)), ("the page as it opens", ("land_based_wind", "tx", {})), ("CPV Basin Ranch", ("natural_gas", "tx", TXG))):
    x, r = go(t, s, **g)
    c, o = r["c"], r["o"]
    print(f"{name}: construction job-years {c[('jobs', 'total')]:,.0f}, on site {c[('jobs', 'onsite')]:,.0f} ({c[('jobs', 'onsite')] / c[('jobs', 'total')] * 100:.0f} percent); "
          f"operating jobs a year {o[('jobs', 'total')]:,.1f}, on site {o[('jobs', 'onsite')]:,.1f}")

# 8. sales tax by receiver
line(8, "Sales and use tax as one figure (default) or split into the state's rate and the average local rate")
for name, (t, s, g) in (("the page as it opens", ("land_based_wind", "tx", {})), ("CPV Basin Ranch", ("natural_gas", "tx", TXG)), ("Lone Mountain", ("geothermal", "nv", dict(NV, taxable=3.3)))):
    x, r = go(t, s, **g)
    st = P0.sales[s]
    tot = r["sums"]["sales"]
    if tot is None:
        print(f"{name}: no sales tax held")
        continue
    sh = st["state_rate"] / (st["state_rate"] + st["avg_local_rate"])
    print(f"{name}: {M(tot)} = state {M(tot * sh)} ({st['state_rate'] * 100:.2f} points) + average local {M(tot * (1 - sh))} ({st['avg_local_rate'] * 100:.2f} points)")

# 9. B less A
line(9, "A and B: no difference column (default) or a third column, B less A")
xa, ra = go("geothermal", "nv", **NV)
nv_off = dict(NV, iaval=False)
xb, rb = go("geothermal", "nv", **nv_off)
fa, fb = rep.table_figures(xa, ra), rep.table_figures(xb, rb)
for k in ("y1:property", "sum:property", "pv:taxes", "c:jobs:total"):
    a, b = fa.get(k), fb.get(k)
    print(f"Lone Mountain, option on (A) and off (B), {k}: A {M(a)}, B {M(b)}, B less A {'none' if a is None or b is None else M(b - a)}")
print(f"the column adds {len(fa)} cells (one per row of the table)")

# 10. Iowa wind without the ordinance
line(10, "Iowa wind without the ordinance: 'not held' (default) or the levy applied to the capital cost")
xa, ra = go("land_based_wind", "ia", **IA)
xb, rb = go("land_based_wind", "ia", **dict(IA, iaval=False))
spend = xa["capex"] * xa["mw"] * 1000
alt_year = spend * IA["levy"] / 1000
alt_sum = alt_year * xa["life"]
alt_pv = sum(alt_year / (1 + xa["rate"] / 100) ** (xa["build"] + i) for i in range(int(xa["life"])))
print(f"with the ordinance (A): over the life {M(ra['sums']['property'])}, present value {M(ra['pv']['property'])}; without (B): {M(rb['sums']['property'])}")
print(f"without, levy {IA['levy']} on the whole cost each year (no Iowa schedule for unordained wind is held, so no depreciation): {M(alt_year)} a year, {M(alt_sum)} over {int(xa['life'])} years, "
      f"present value {M(alt_pv)}; what the ordinance gives up {M(alt_sum - ra['sums']['property'])} over the life (an upper bound)")

# 11. the seller page's wind cost
line(11, "Capital cost of wind: EIA's USD 1,482 per kW (default); the seller page's USD 2,100 (Lazard) named in the hover, or used")
x, r = go("land_based_wind", "tx")
_, r2 = go("land_based_wind", "tx", capex=2100)
_, r3 = go("land_based_wind", "tx", capex=2100, life=30)
print(f"the page as it opens: construction job-years {r['c'][('jobs', 'total')]:,.0f} -> {r2['c'][('jobs', 'total')]:,.0f} ({pct(r['c'][('jobs', 'total')], r2['c'][('jobs', 'total')])}); "
      f"sales and use tax {M(r['sums']['sales'])} -> {M(r2['sums']['sales'])}; taxes, present value {M(r['pv']['taxes'])} -> {M(r2['pv']['taxes'])}; "
      f"with 30 years too: earnings, present value {M(r['pv']['earnings'])} -> {M(r3['pv']['earnings'])}")
print("named in the hover only: no figure moves")

# 12 to 15, 24, 25: sales tax exemption shares
SH_WIND, SH_PV, SH_GAS = 66.9358, 67.2131, 58.2524
SH_PV_RACK = (0.105263 + 0.368421 + 0.063158) / 0.642105 * 100


def sales_case(state, tech, exempt, **g):
    x, r = go(tech, state, **g)
    _, r2 = go(tech, state, exempt=exempt, **g)
    return x, r, r2


line(12, "New York: 100 percent exempt (default) or the machinery share the other states hold")
for tech, sh in (("land_based_wind", SH_WIND), ("utility_pv", SH_PV), ("natural_gas", SH_GAS)):
    x, r, r2 = sales_case("ny", tech, sh)
    print(f"New York {tech}, {x['mw']:,.0f} MW default: sales and use tax {M(r['sums']['sales'])} -> {M(r2['sums']['sales'])}; taxes, present value {M(r['pv']['taxes'])} -> {M(r2['pv']['taxes'])}")

line(13, "Wisconsin solar: 83.6 percent exempt (mounting, modules, inverters; default) or 100 percent (the electrical materials too)")
x, r, r2 = sales_case("wi", "utility_pv", 100)
print(f"Wisconsin solar default: sales and use tax {M(r['sums']['sales'])} -> {M(r2['sums']['sales'])} ({pct(r['sums']['sales'], r2['sums']['sales'])}); the 100 percent is an upper bound: the share of the remaining 16.4 percent that is electrical is not held")

line(14, "Missouri machinery and California's 3.9375 points: foundations not counted (default) or counted")
for st, tech, hi, why in (("mo", "land_based_wind", 100, "every taxable purchase exempt, the bound"), ("ca", "utility_pv", 43.6, "3.9375 / 9.03 of the tax on every purchase, the bound"),
                          ("ca", "land_based_wind", 43.6, "the same bound")):
    x, r, r2 = sales_case(st, tech, hi)
    print(f"{st} {tech}: exempt {x['exempt']} -> {hi} ({why}): sales and use tax {M(r['sums']['sales'])} -> {M(r2['sums']['sales'])} ({pct(r['sums']['sales'], r2['sums']['sales'])})")
print("the foundations' own share of JEDI's purchases is not held: the change lies between 0 and the bound")

line(15, "Gas: exempt machinery JEDI's power generation equipment, 58.3 percent (default), or with the plant equipment, 84.5 percent")
moved = []
for st, v in sorted(P0.exempt.items()):
    if v.get("natural_gas", {}).get("exempt_pct") == SH_GAS and ("natural_gas", st) in JEDI:
        x, r, r2 = sales_case(st, "natural_gas", 84.5)
        moved.append((st, r["sums"]["sales"], r2["sums"]["sales"]))
for st, a, b in moved:
    print(f"   {st}: {M(a)} -> {M(b)} ({pct(a, b)})")
print(f"{len(moved)} states move; wind's towers: their share of JEDI's purchases is not in the files (the workbook's tower line is not held), so the wind half of the line is not computed")

line(24, "Iowa solar: 67.2 percent exempt (modules and inverters; default) or with the racking (83.6) or everything (100)")
for sh in (SH_PV_RACK, 100):
    x, r, r2 = sales_case("ia", "utility_pv", sh)
    print(f"Iowa solar default, {sh:.1f} percent: sales and use tax {M(r['sums']['sales'])} -> {M(r2['sums']['sales'])} ({pct(r['sums']['sales'], r2['sums']['sales'])})")

line(25, "Texas: no sales tax exemption share (default, an upper bound) or the machinery share of the other states")
for tech, sh, g in (("land_based_wind", SH_WIND, {}), ("utility_pv", SH_PV, {}), ("natural_gas", SH_GAS, TXG)):
    x, r, r2 = sales_case("tx", tech, sh, **g)
    print(f"Texas {tech} ({x['mw']:,.0f} MW): sales and use tax {M(r['sums']['sales'])} -> {M(r2['sums']['sales'])} ({pct(r['sums']['sales'], r2['sums']['sales'])}); "
          f"taxes, present value {M(r['pv']['taxes'])} -> {M(r2['pv']['taxes'])}")


# property schedules: the life's taxable value and tax under a levy typed
def schedule_case(state, tech, rid, new_sched, then, levy, **g):
    g = dict(g)
    g.setdefault("levy", levy)
    x, r = go(tech, state, **g)
    P = copy.deepcopy(P0)
    rr = rule_of(P, state, rid)
    rr["schedule_pct"], rr["then_pct"] = new_sched, then
    rr.pop("depr_pct_per_year", None)
    _, r2 = go(tech, state, P, **g)
    return x, r, r2


def straight(first_drop, floor, years=60):
    return [max(floor, 100 - first_drop * (i + 1)) for i in range(years)]


line(16, "California solar, gas and geothermal at cost (default) or by AH 581 Table 4")
print("not computed: the Board of Equalization's Table 4 factors are not held in the repository (the note, section 10)")

line(17, "Washington geothermal at cost (default) or by the steam and gas fired column 7.5 (the schedule Washington's gas plants use)")
wa_gas = rule_of(P0, "wa", "wa_gas_property")
x, r, r2 = schedule_case("wa", "geothermal", "wa_geothermal_property", wa_gas["schedule_pct"], wa_gas["then_pct"], wa_gas["default_levy"])
print(f"Washington geothermal default (levy {wa_gas['default_levy']}): property over the life {M(r['sums']['property'])} -> {M(r2['sums']['property'])} ({pct(r['sums']['property'], r2['sums']['property'])}); "
      f"first year {M(next(y for y in r['years'] if y['phase'] == 'operations')['property'])} -> {M(next(y for y in r2['years'] if y['phase'] == 'operations')['property'])}; "
      f"taxes, present value {M(r['pv']['taxes'])} -> {M(r2['pv']['taxes'])}")

line(18, "South Carolina at cost (default) or 11 percent a year off to a 10 percent floor (class 6(a))")
for tech in ("utility_pv", "land_based_wind", "natural_gas"):
    x, r, r2 = schedule_case("sc", tech, "sc_property", straight(11, 10), 10, 300)
    print(f"South Carolina {tech}, a levy of 300 per 1,000 typed (an example; the percent holds at any levy): property over the life {M(r['sums']['property'])} -> {M(r2['sums']['property'])} "
          f"({pct(r['sums']['property'], r2['sums']['property'])}); present value {M(r['pv']['property'])} -> {M(r2['pv']['property'])} ({pct(r['pv']['property'], r2['pv']['property'])})")

line(19, "West Virginia: the county table (default) or central assessment by the state")
print("not computed: the state's central assessment values a plant as a unit, and no unit value or method for a merchant plant is held")

line(20, "Kentucky at cost (default) or the 62A500 Class VI factors")
print("not computed: the 62A500 factors are not held (and the note says they exclude public service companies)")

line(21, "Texas wind, gas and geothermal at cost (default) or Harris County's 20-year industrial column")
print("not computed: Harris County Appraisal District's schedule is not held")

line(22, "Texas solar: the district's 10-year schedule (default) or a straight line over 10 years to 20 percent")
x, r, r2 = schedule_case("tx", "utility_pv", "tx_solar", straight(8, 20), 20, 20)
print(f"Texas solar default, a levy of 20 per 1,000 typed (an example): property over the life {M(r['sums']['property'])} -> {M(r2['sums']['property'])} ({pct(r['sums']['property'], r2['sums']['property'])}); "
      f"present value {M(r['pv']['property'])} -> {M(r2['pv']['property'])} ({pct(r['pv']['property'], r2['pv']['property'])}); "
      f"schedule {rule_of(P0, 'tx', 'tx_solar')['schedule_pct']} against {straight(8, 20)[:10]}")

line(23, "New Mexico solar: no federal credit deducted (default) or the 30 percent investment tax credit deducted from the cost taxed")
x, r = go("utility_pv", "nm", levy=30)
P = copy.deepcopy(P0)
rr = rule_of(P, "nm", "nm_solar")
rr["assessment_ratio"] = rr["assessment_ratio"] * 0.7
_, r2 = go("utility_pv", "nm", P, levy=30)
print(f"New Mexico solar default, a levy of 30 per 1,000 typed (an example): property over the life {M(r['sums']['property'])} -> {M(r2['sums']['property'])} ({pct(r['sums']['property'], r2['sums']['property'])}); "
      "the credit's rate (30 percent at the base, more with adders) is a choice the ruling would fix")

line(26, "Kansas: the ten-year exemption assumed granted (default) or not")
x, r = go("land_based_wind", "ks")
x2, r2 = go("land_based_wind", "ks", own=1.5, ownyears=25)
P = copy.deepcopy(P0)
P.property["ks"]["rules"] = [q for q in P.property["ks"]["rules"] if q["id"] != "ks_renewable_exempt"]
_, r3 = go("land_based_wind", "ks", P, own=1.5, ownyears=25)
ops = [y["property"] for y in r["years"] if y["phase"] == "operations"][:10]
print(f"Kansas wind default: years 1 to 10 USD {sum(ops):,.0f}; after them 'not held', so the life has no total ({r['sums']['property']})")
print(f"with an own rate of 1.5 percent over 25 years typed (an example): granted {M(r2['sums']['property'])} over the life, not granted {M(r3['sums']['property'])} ({pct(r2['sums']['property'], r3['sums']['property'])}); "
      f"present value {M(r2['pv']['property'])} -> {M(r3['pv']['property'])}")

line(27, "Oregon solar fee in lieu: USD 7,000 per MW (default, the statute's maximum) or a lower negotiated figure (the statute's minimum USD 5,500)")
x, r = go("utility_pv", "or", iaval=True)
_, r2 = go("utility_pv", "or", iaval=True, optrate=5500)
y20 = [y["property"] for y in r["years"] if y["phase"] == "operations"][:20]
y20b = [y["property"] for y in r2["years"] if y["phase"] == "operations"][:20]
print(f"Oregon solar default {x['mw']:,.0f} MW, option on: each year {M(y20[0])} -> {M(y20b[0])} (-21.4 percent); the 20 years {M(sum(y20))} -> {M(sum(y20b))}; "
      f"after year 20 no figure either way; present value of the fee {M(sum(v / (1 + x['rate'] / 100) ** (x['build'] + i) for i, v in enumerate(y20)))} -> "
      f"{M(sum(v / (1 + x['rate'] / 100) ** (x['build'] + i) for i, v in enumerate(y20b)))}")

line(28, "Virginia solar: subsection F's steps 80, 70, 60 (default) or subsection D's flat 80 percent; the revenue share")
g = dict(mw=100, own=1.0, ownyears=35)
x, r = go("utility_pv", "va", **g)
P = copy.deepcopy(P0)
rule_of(P, "va", "va_solar_exemption")["exempt_steps"] = [{"share": 0.8}]
_, r2 = go("utility_pv", "va", P, **g)
print(f"Virginia solar 100 MW, an own rate of 1.0 percent over 35 years typed (an example): property over the life {M(r['sums']['property'])} -> {M(r2['sums']['property'])} "
      f"({pct(r['sums']['property'], r2['sums']['property'])}); present value {M(r['pv']['property'])} -> {M(r2['pv']['property'])} ({pct(r['pv']['property'], r2['pv']['property'])})")
print("the revenue share (USD per MW, Code 58.1-2636) needs a price forecast the tool does not hold: not computed")

line(29, "Illinois and Ohio statutes: no rule held (default) or a person reads them")
print("not computed: the statutes were not read (their hosts are not requested until the owner rules); no figure exists to compare")

line(30, "Wisconsin's payments to towns and counties: on the property line (default); the caps per resident")
x, r = go("land_based_wind", "wi")
y = next(y for y in r["years"] if y["phase"] == "operations")
print(f"Wisconsin wind default {x['mw']:,.0f} MW: USD {y['property']:,.0f} a year on the line; the caps need the town's and county's residents and the caps' statute read: not computed")

line(31, "Idaho's tax on gross energy earnings: not held (default) or a sale price added")
x, r = go("land_based_wind", "id")
mwh = x["mw"] * 8760 * x["cf"]
print(f"Idaho wind default {x['mw']:,.0f} MW at capacity factor {x['cf']}: {mwh:,.0f} MWh a year; the tax is 3 percent of earnings, USD {0.03 * mwh:,.0f} a year for each USD 1 per MWh of sale price. "
      "No Idaho sale price is held in the warehouse: the figure is not computed")

line(32, "Dollars of other years: STEO's copy of BEA's deflator (default) or BEA's own")
print("not computed: BEA's tables need an API key the ERW does not hold (the note, section 10)")

line(33, "Earnings per job: JEDI's (default) or BLS's county wages (QCEW)")
print("not computed: QCEW is not held (www.bls.gov refuses automated reads)")

line(34, "The Tax Foundation's tables: used with attribution (default) or replaced by the statutes")
x, r = go("land_based_wind", "tx")
x2, r2 = go("land_based_wind", "tx", sales=6.25)
xn, rn = go("natural_gas", "ny")
print(f"which figures rest on them: sales_tax.json (state and average local rate, {len(P0.sales)} rows, 'Tax Foundation, State and Local Sales Tax Rates, Midyear 2026') "
      f"and income_tax.json (brackets, {len(P0.income)} rows, 'Tax Foundation, State Individual Income Tax Rates and Brackets, 2026'): every sales and income tax figure. "
      f"Replaced by the statutes, a state's own rate and brackets are the statute's figures and would not move where the Foundation copied them right; the average local rate has no statute "
      f"(the Foundation's population-weighted mean): left out, the page as it opens reads sales and use tax {M(r['sums']['sales'])} -> {M(r2['sums']['sales'])} "
      f"({pct(r['sums']['sales'], r2['sums']['sales'])}, the state's 6.25 percent alone). New York gas as an income-tax case: income tax over the life {M(rn['sums']['income'])}, which rests on the brackets")

line(35, "The Lincoln Institute's study: not used (default)")
print("not computed: the study is not held (its host disallows automated reads)")

line(36, "Texas rows citing comptroller.texas.gov: kept (default) or left out")
print("the Texas rows that cite comptroller.texas.gov: property_rules.json's tx_solar and tx_property (sources tx_comptroller_valuing, tx_96_1569, tx_96_313), "
      "and the gas severance from severance_rules.json (tx_cpa_gas, the Comptroller's natural gas production tax page). Texas's sales tax rates come from the Tax Foundation, not the Comptroller")
for tech, g in (("utility_pv", dict(levy=20)), ("land_based_wind", dict(levy=20)), ("natural_gas", dict(TXG, levy=20))):
    x, r = go(tech, "tx", **g)
    sev = r["pv"]["severance"] or 0
    left = (r["pv"]["sales"] or 0) + r["pv"]["income"]
    print(f"Texas {tech}, a levy of 20 per 1,000 typed (an example): property over the life {M(r['sums']['property'])} -> not held; severance over the life {M(r['sums']['severance'])} -> "
          f"{'not held' if r['sums']['severance'] else 'none either way'}; taxes, present value {M(r['pv']['taxes'])} -> {M(left)} ({pct(r['pv']['taxes'], left)})")
