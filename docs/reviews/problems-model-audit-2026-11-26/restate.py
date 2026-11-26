"""Session 10229 (problems audit): an independent restatement of every keyed figure of the five problem sets of the whole
country, the five default bills of /learn/bill and the two bill questions of "Prices and your bill".

Written from each question's own words and rule (the decisions block and docs/methods/problem_sets.md), the page files'
own fields, and the tariff passages of site/data/bill_rules.json; not from lib/problems.ts, lib/problemsets/ or
lib/bill.ts. Standard library only. For each question it forms every figure the answer prints, in the order the answer
prints them, as the page prints them (a whole number with separators, else two decimals, half away from zero on the
exact binary value, as Intl does), and checks:
  1. each restated string appears in the drawn answer, in order;
  2. every figure the drawn question carries (answer, line, steps) equals a restated figure (relative 1e-9);
  3. for each derived figure, the result a student gets from the printed inputs, against the key (the rounding measure).
usage: restate.py <site/data> <draw dir> <cost_of_power_monthly.csv>
"""
import csv
import json
import sys
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

DATA, DRAW, COP = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
J = lambda p: json.loads((DATA / p).read_text(encoding="utf-8"))
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
mwords = lambda m: f"{MONTHS[int(m[5:7]) - 1]} {m[:4]}"


def shown(v):
    v = float(v)
    if v.is_integer():
        return f"{int(v):,}"
    q = Decimal(v).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    s = f"{abs(q):,.2f}"
    return ("-" if q < 0 else "") + s


def first_max(xs):
    best = None
    for k, x in enumerate(xs):
        if isinstance(x, (int, float)) and (best is None or x > xs[best]):
            best = k
    return best


R = {}          # slug -> {qid: [(label, value, derived_from or None)]}
D = lambda op, a, b: (a / b if op == "ratio" else a - b if op == "diff" else a / b * 100)


def der(op, a, b, label):
    """A derived figure: (label, value, (op, a, b))."""
    return (label, D(op, a[1], b[1]), (op, a, b))


# ---------------------------------------------------------------------------------------- who trades with whom
t = J("regions/trade/ten.json")
mx = J("regions/trade_matrix.json")
i = max(k for k, m in enumerate(t["months"]) if m < t["built"][:7])
nb = t["neighbors"]
own = lambda c, j=i: (f"{c} own", nb[c]["net_imports_mwh"][j])
their = lambda c, j=i: (f"{c} their", nb[c]["their_report_mwh"][j])
gap = lambda c, j=i: (f"{c} gap", nb[c]["gap_mwh"][j])
T = {}
T["tx"] = [own("SE"), their("SE"), der("ratio", own("SE"), their("SE"), "SE ratio")]
tot = ("total", t["net_imports_mwh"][i])
T["t1"] = [tot] + [own(c) for c in sorted(nb)]
T["t2"] = [own("MIDW"), their("MIDW"), der("ratio", own("MIDW"), their("MIDW"), "MIDW ratio"), gap("MIDW")]
T["t3"] = [own("MIDA"), their("MIDA"), der("diff", own("MIDA"), their("MIDA"), "MIDA diff"), gap("MIDA")]
whole = [p for p in mx["region_pairs"] if p["a"] == "MIDA" and p["b"] == "TEN" and p["months_held"] == 12 and p["months_in_year"] == 12
         and None not in (p["a_report_mwh"], p["b_report_mwh"], p["gap_mwh"])]
p4 = max(whole, key=lambda p: abs(p["gap_mwh"]))  # first of equal sizes in file order, as reduce keeps the first
a4, b4 = ("MIDA a", p4["a_report_mwh"]), ("TEN b", p4["b_report_mwh"])
T["t4"] = [a4, b4, der("diff", a4, b4, "a less b"), ("gap", p4["gap_mwh"])]
mw = sorted((p for p in mx["region_pairs"] if p["a"] == "MIDW" and p["b"] == "TEN" and p["months_held"] == 12 and p["months_in_year"] == 12
            and None not in (p["a_report_mwh"], p["b_report_mwh"], p["gap_mwh"])), key=lambda p: p["year"])
y0, y1 = mw[0], mw[-1]
tb0, tb1, wa0, wa1 = ("TEN y0", y0["b_report_mwh"]), ("TEN y1", y1["b_report_mwh"]), ("MIDW y0", y0["a_report_mwh"]), ("MIDW y1", y1["a_report_mwh"])
T["t5"] = [der("ratio", tb1, tb0, "TEN growth"), der("ratio", wa1, wa0, "MIDW growth")]
cm = sorted((p for p in mx["region_pairs"] if p["a"] == "CAL" and p["b"] == "MEX" and p["months_in_year"] == 12), key=lambda p: p["year"])[-1]
T["t6"] = [("CAL a", cm["a_report_mwh"]), ("hours a", cm["hours_a"]), ("hours b", cm["hours_b"])]
ended = [k for k, m in enumerate(t["months"]) if m < t["built"][:7] and isinstance(nb["MIDW"]["hours_own"][k], (int, float))]
k7 = min(ended, key=lambda k: (nb["MIDW"]["hours_own"][k] / t["hours_in_month"][k], k))
h7, n7 = ("hours", nb["MIDW"]["hours_own"][k7]), ("in month", t["hours_in_month"][k7])
T["t7"] = [h7, n7, der("pct", h7, n7, "share"), own("MIDW", k7)]
R["who-trades-with-whom"] = T
WORDS = {"t-month": mwords(t["months"][i]), "t4-year": p4["year"], "t5-years": (y0["year"], y1["year"]), "t6-year": cm["year"], "t7-month": mwords(t["months"][k7])}

# ---------------------------------------------------------------------------------------- a storm across the country
el, ur = J("regions/events/elliott_2022.json"), J("regions/events/uri_2021.json")
hour = lambda f, k: (datetime.strptime(f["hours"]["start"], "%Y-%m-%dT%H:%M:%SZ") + timedelta(hours=k * f["hours"]["step_hours"])).strftime("%Y-%m-%d %H:%M UTC")
S = {}
pk = lambda f, r: first_max(f["regions"][r]["demand_mw"])
c, tn, tx = pk(el, "CAR"), pk(el, "TEN"), pk(ur, "TEX")
cd, cb = ("CAR d", el["regions"]["CAR"]["demand_mw"][c]), ("CAR b", el["regions"]["CAR"]["baseline"]["demand_mw"][c])
S["sx"] = [cd, cb, der("ratio", cd, cb, "ratio")]
td, tb = ("TEN d", el["regions"]["TEN"]["demand_mw"][tn]), ("TEN b", el["regions"]["TEN"]["baseline"]["demand_mw"][tn])
S["s1"] = [td, tb, der("ratio", td, tb, "ratio")]
xd, xb = ("TEX d", ur["regions"]["TEX"]["demand_mw"][tx]), ("TEX b", ur["regions"]["TEX"]["baseline"]["demand_mw"][tx])
S["s2"] = [xd, xb, der("diff", xd, xb, "diff")]
TG = el["regions"]["TEN"]["gen"]
gas, coal, nuc, hyd = ("gas", TG["natural_gas"][tn]), ("coal", TG["coal"][tn]), ("nuclear", TG["nuclear"][tn]), ("hydro", TG["hydro"][tn])
net, gasb = ("net gen", el["regions"]["TEN"]["net_generation_mw"][tn]), ("gas b", el["regions"]["TEN"]["baseline"]["gen"]["natural_gas"][tn])
S["s3"] = [gas, coal, nuc, hyd, der("pct", gas, net, "gas share"), net, der("ratio", gas, gasb, "gas vs b"), gasb]
XG, XB = ur["regions"]["TEX"]["gen"], ur["regions"]["TEX"]["baseline"]["gen"]
w, wb, ng, ngb = ("wind", XG["wind"][tx]), ("wind b", XB["wind"][tx]), ("gas", XG["natural_gas"][tx]), ("gas b", XB["natural_gas"][tx])
S["s4"] = [w, wb, der("diff", w, wb, "wind diff"), ng, ngb, der("ratio", ng, ngb, "gas ratio")]
ti, tib = ("TEN imports", el["regions"]["TEN"]["net_imports_mw"][tn]), ("TEN imports b", el["regions"]["TEN"]["baseline"]["net_imports_mw"][tn])
flows = [(k, el["pairs"][k]["flow_mw"][tn]) for k in sorted(k for k in el["pairs"] if k.endswith("-TEN"))]
S["s5"] = [ti, tib] + flows
xi = ("TEX imports", ur["regions"]["TEX"]["net_imports_mw"][tx])
S["s6"] = [xi, xd, ti, td, der("ratio", ti, xi, "ratio")]
ka, kb = ("CENT a", ur["pairs"]["CENT-TEX"]["flow_mw_a"][tx]), ("TEX b", ur["pairs"]["CENT-TEX"]["flow_mw_b"][tx])
S["s7"] = [ka, kb, der("diff", ka, kb, "diff")]
R["storm-across-the-country"] = S
WORDS.update({"sx-at": hour(el, c), "s1-at": hour(el, tn), "s2-at": hour(ur, tx), "top-into-TEN": max(flows, key=lambda f: f[1])[0]})

# ---------------------------------------------------------------------------------------- under the ground and in the wind
man = J("resources/manifest.json")
Lr = {l["id"]: l for l in man["layers"]}


def legend_end(lid, end):
    """The map's legend end: the lowest low or highest high over the layer's parts (the list's legend and each other extent's)."""
    l = Lr[lid]
    vals = [l["legend"][end]] + [x["legend"][end] for x in (l.get("other_extents") or []) if x.get("legend") and isinstance(x["legend"].get(end), (int, float))]
    return min(vals) if end == "min" else max(vals)


G = {}
gl, gh = ("ghi low", legend_end("solar_ghi", "min")), ("ghi high", legend_end("solar_ghi", "max"))
G["rx"] = [gl, gh, der("ratio", gh, gl, "ratio")]
wl, ws = ("wind legend top", legend_end("wind_speed_100m", "max")), ("wind source max", Lr["wind_speed_100m"]["source_stats"]["max"])
G["r1"] = [wl, ws, der("diff", ws, wl, "diff")]
dh = ("dni high", legend_end("solar_dni", "max"))
G["r2"] = [gh, dh, der("ratio", dh, gh, "ratio")]
cfm, cfx = ("cf mean", Lr["wind_capacity_factor"]["stats"]["mean"]), ("cf max", Lr["wind_capacity_factor"]["stats"]["max"])
G["r3"] = [cfm, cfx, der("ratio", cfx, cfm, "ratio")]
geo = Lr["geothermal_hydrothermal_sites"]
gn, gt, gx = ("sites", geo["stats"]["n"]), ("total", geo["total_mwe_mean"]), ("largest", geo["stats"]["max"])
G["r4"] = [gn, gt, gx, der("pct", gx, gt, "share")]
npd = Lr["hydropower_npd"]
nc, ngy = ("cap", npd["total_cap_mw"]), ("gen", npd["total_gen_mwh_yr"])
G["r5"] = [nc, ngy, der("ratio", ngy, nc, "hours")]
bio = Lr["biomass"]
bt, bc = ("total", bio["national_total"]), ("crop", bio["parts"]["CropRes"])
G["r6"] = [bt, bc, der("pct", bc, bt, "share")]
R["under-the-ground-and-in-the-wind"] = G
# what the map's legend prints for each end (lib/resources.ts tickLabel: one decimal when the range is 5 or more, two below)
LEG = {}
for lid in ("solar_ghi", "solar_dni", "wind_speed_100m", "wind_capacity_factor"):
    lo, hi = legend_end(lid, "min"), legend_end(lid, "max")
    d = 1 if hi - lo >= 5 else 2
    LEG[lid] = (lo, hi, float(Decimal(lo).quantize(Decimal(10) ** -d, ROUND_HALF_UP)), float(Decimal(hi).quantize(Decimal(10) ** -d, ROUND_HALF_UP)), d)

# ---------------------------------------------------------------------------------------- where energy goes
ind = J("industry.json")
mo, II = ind["monthly"], ind["industries"]
j = max(k for k, v in enumerate(mo["by_source"]["total"]) if isinstance(v, (int, float)))
jp = mo["months"].index(f"{int(mo['months'][j][:4]) - 1}{mo['months'][j][4:]}")
f1, f2 = II["ranked_3_digit"][0], II["ranked_3_digit"][1]
inf = lambda code, reg, fuel: (f"{code} {reg} {fuel}", II["industries"][code]["by_region"][reg][fuel])
W = {}
xt, xg = inf(f1, "us", "total"), inf(f1, "us", "natural_gas")
W["ix"] = [xt, xg, der("pct", xg, xt, "share")]
tt, ee, ll = ("total", mo["by_source"]["total"][j]), ("end use", mo["by_source"]["end_use_total"][j]), ("losses", mo["by_source"]["electrical_system_losses"][j])
W["i1"] = [tt, ee, der("diff", tt, ee, "diff"), ll]
tp = ("total prev", mo["by_source"]["total"][jp])
W["i2"] = [tt, tp, der("ratio", tt, tp, "ratio")]
a1, a2 = inf(f1, "us", "total"), inf(f2, "us", "total")
W["i3"] = [a1, a2, der("ratio", a1, a2, "ratio")]
so, st = inf(f2, "us", "other"), inf(f2, "us", "total")
W["i4"] = [so, st, der("pct", so, st, "share")]
E1 = II["industries"][f1]["electricity_mwh"]["us"]
on, nd = ("onsite", E1["elec_onsite_generation"]), ("net demand", E1["elec_net_demand"])
W["i5"] = [on, nd, der("pct", on, nd, "share")]
sr = inf(f1, "south", "total")
W["i6"] = [sr, xt, der("pct", sr, xt, "share")]
sa = ind["states_annual"]
ytx, yla = sa["states"]["TX"]["consumption_tbtu"]["total"], sa["states"]["LA"]["consumption_tbtu"]["total"]
ky = max(k for k in range(len(sa["years"])) if isinstance(ytx[k], (int, float)) and isinstance(yla[k], (int, float)))
TXv, LAv = ("TX", ytx[ky]), ("LA", yla[ky])
W["i7"] = [TXv, LAv, der("ratio", TXv, LAv, "ratio")]
R["where-energy-goes"] = W
# is the ranking the order of the United States totals?
rank_ok = II["ranked_3_digit"] == sorted(II["ranked_3_digit"], key=lambda c: -(II["industries"][c]["by_region"]["us"]["total"] or -1))
WORDS.update({"i-month": mwords(mo["months"][j]), "i-prev": mwords(mo["months"][jp]), "first": f1, "second": f2, "i7-year": sa["years"][ky], "rank_is_us_total_order": rank_ok})

# ---------------------------------------------------------------------------------------- your own balancing authority
A, Ee, C = J("regions/authority/tva.json"), J("regions/authority/erco.json"), J("regions/authority/ciso.json")
cap = lambda g: (f"cap {g}", A["owns"]["capacity_mw"][g])
TOT = ("total", A["owns"]["total_mw"])
B = {}
B["bx"] = [TOT, cap("nuclear"), der("pct", cap("nuclear"), TOT, "share")]
top = ("largest", A["owns"]["largest_plants"][0]["mw"])
B["b1"] = [top, TOT, der("pct", top, TOT, "share")]
gnu, gga = ("gen nuclear", A["burns"]["share_pct"]["nuclear"]), ("gen gas", A["burns"]["share_pct"]["natural_gas"])
B["b2"] = [der("pct", cap("nuclear"), TOT, "cap share n"), gnu, der("pct", cap("natural_gas"), TOT, "cap share g"), gga]
ri = first_max([r["mw"] for r in A["coming"]["retirements"]])
rr = A["coming"]["retirements"][ri]
rm, rc = ("ret mw", rr["mw"]), cap(rr["technology_group"])
B["b3"] = [rm, rc, der("pct", rm, rc, "share")]
ai = first_max([r["mw"] for r in A["coming"]["additions"]])
ar = A["coming"]["additions"][ai]
am, ac = ("add mw", ar["mw"]), cap(ar["technology_group"])
B["b4"] = [am, der("pct", am, ac, "share"), ac]
pi = first_max([p["exchange_gross_mwh"] for p in A["trades"]["partners"]])
pp = A["trades"]["partners"][pi]
pn, pg = ("net", pp["net_import_mwh"]), ("gross", pp["exchange_gross_mwh"])
B["b5"] = [pn, pg, der("pct", pn, pg, "share"), ("share of demand", A["trades"]["net_import_share_of_demand_pct"])]
ie, ic = ("ERCOT", Ee["burns"]["co2"]["intensity_kg_per_mwh"]), ("CAISO", C["burns"]["co2"]["intensity_kg_per_mwh"])
B["b6"] = [ie, ic, der("ratio", ie, ic, "ratio")]
pkm, ga, ge = ("peak", A["size"]["peak_mw"]), ("TVA growth", A["size"]["growth_since_2019_pct"]), ("ERCOT growth", Ee["size"]["growth_since_2019_pct"])
B["b7"] = [pkm, ga, ge, der("diff", ge, ga, "points"), ("TVA rows", A["large_loads"]["count"]), ("ERCOT rows", Ee["large_loads"]["count"])]
R["your-own-balancing-authority"] = B
WORDS.update({"b1-plant": A["owns"]["largest_plants"][0]["name"], "b3": (rr["year"], rr["technology_group"]), "b4": (ar["year"], ar["technology_group"]),
              "b5-partner": pp["code"], "b7-years": (A["size"]["growth_year"], Ee["size"]["growth_year"]), "months": (A["burns"]["months"], Ee["burns"]["months"], C["burns"]["months"])})

# ---------------------------------------------------------------------------------------- compare with the drawing
sets = json.loads((DRAW / "sets.json").read_text(encoding="utf-8"))
total_figs = equal_figs = 0
problems, rounding = [], []
for slug, qs in R.items():
    drawn = {q["id"]: q for q in sets[slug]["questions"]}
    if set(drawn) != set(qs):
        problems.append(f"{slug}: questions drawn {sorted(drawn)} restated {sorted(qs)}")
    for qid, figs in qs.items():
        figs = [f if len(f) == 3 else (f[0], f[1], None) for f in figs]
        q = drawn[qid]
        pos, text = 0, q["answer"]
        for f in figs:
            total_figs += 1
            s = shown(f[1])
            k = text.find(s, pos)
            if k < 0:
                problems.append(f"{slug} {qid}: {f[0]} restated {s} not found in order in the answer: {text}")
            else:
                equal_figs += 1
                pos = k + len(s)
        vals = [f[1] for f in figs] + [x[1] for f in figs if f[2] for x in (f[2][1], f[2][2])]
        if (slug, qid) == ("who-trades-with-whom", "t3"):  # the steps' hours behind each report (the answer prints none)
            vals += [nb["MIDA"][h][i] for h in ("hours_own", "hours_their", "hours_both")]
        for dfig in q["figures"]:
            if not any(abs(dfig["v"] - v) <= 1e-9 * max(1.0, abs(v)) for v in vals):
                problems.append(f"{slug} {qid}: drawn figure {dfig['k']} = {dfig['v']} matches no restated figure")
        for f in figs:
            if f[2]:
                op, a, b = f[2]
                from_printed = D(op, float(shown(a[1]).replace(",", "")), float(shown(b[1]).replace(",", "")))
                rounding.append((slug, qid, f[0], shown(f[1]), shown(from_printed), shown(f[1]) == shown(from_printed)))

# ---------------------------------------------------------------------------------------- the bills
rules = json.loads((DATA / "bill_rules.json").read_text(encoding="utf-8"))["bills"]
bills = json.loads((DRAW / "bills.json").read_text(encoding="utf-8"))
out_bills = {}
# PG&E E-TOU-C, winter, 600 kWh, 20 percent at peak, territory T, Income Tier 3, 30 days: by the total rates (Sheet 2) and
# by the unbundled components (Sheet 3), each kWh pro-rated across the baseline (Sheet 1's rule)
ca = rules["CA"]; dca = ca["defaults"]
kwh, ps, days = dca["kwh"], dca["peak_share"], dca["days"]
base = min(kwh, ca["baseline_quantities"]["code_B"][dca["territory"]][1 if dca["season"] == "winter" else 0] * days)
s = ca["seasons"][dca["season"]]
ca_total_rates = kwh * (ps * s["peak"] + (1 - ps) * s["offpeak"]) + base * ca["baseline_credit"]["rate"] + days * ca["base_services"]["tiers"][dca["income_tier"]]
unb = 0.0
for comp in ca["components"]:
    r = comp["rate"]
    if comp["basis"] == "per_kWh_tou":
        pk_, off_ = r[dca["season"]]
        unb += kwh * (ps * pk_ + (1 - ps) * off_)
    elif comp["basis"] == "per_kWh_baseline_split":
        unb += base * r["baseline"] + (kwh - base) * r["over"]
    else:
        unb += kwh * r
unb += days * ca["base_services"]["tiers"][dca["income_tier"]]
gen_line = kwh * (ps * ca["components"][0]["rate"][dca["season"]][0] + (1 - ps) * ca["components"][0]["rate"][dca["season"]][1])
pcia = kwh * [c_ for c_ in ca["components"] if c_["id"] == "pcia"][0]["rate"]
out_bills["CA"] = {"by total rates": ca_total_rates, "by components": unb, "baseline kWh": base, "generation line": gen_line, "pcia": pcia}
# SCE TOU-D 4-9 PM, winter: 20 percent 4 to 9 p.m. (mid-peak in winter), a third super off-peak, the rest off-peak; Region 9
sce = rules["SCE"]; ds = sce["defaults"]
shares = {"mid": ds["peak_share"], "super": ds["super_share"], "off": 1 - ds["peak_share"] - ds["super_share"]}
sce_e = sum(ds["kwh"] * sh * (comp["rate"][ds["season"]][k] if comp["basis"] == "per_kWh_period" else comp["rate"]) for comp in sce["components"] for k, sh in shares.items())
sce_base = min(ds["kwh"], sce["baseline_quantities"]["basic"][ds["region"]][1] * ds["days"])
sce_tot = sce_e + sce_base * sce["baseline_credit"]["rate"] + ds["days"] * sce["base_services"]["rate"]
out_bills["SCE"] = {"total": sce_tot, "baseline kWh": sce_base}
sd = rules["SDGE"]; dd = sd["defaults"]
shs = {"on": dd["peak_share"], "super": dd["super_share"], "off": 1 - dd["peak_share"] - dd["super_share"]}
sd_tot = sum(dd["kwh"] * sh * sd["components"][0]["rate"][dd["season"]][k] for k, sh in shs.items()) + min(dd["kwh"], dd["baseline_kwh"] * sd["baseline_credit"]["share"]) * sd["baseline_credit"]["rate"] + dd["days"] * sd["base_services"]["rate"]
out_bills["SDGE"] = {"total": sd_tot}
for key in ("TX", "TXC"):
    b = rules[key]
    k_ = b["defaults"]["kwh"]
    energy = k_ * b["energy_default"]["rate"]
    fixed = sum(f["rate"] for f in b["fixed"])
    perk = sum(p["rate"] for p in b["per_kwh"])
    out_bills[key] = {"total": energy + fixed + k_ * perk, "energy": energy, "delivery fixed": fixed, "delivery per kWh rate": perk, "delivery": fixed + k_ * perk}
for key in out_bills:
    tkey = "by components" if key == "CA" else "total"
    out_bills[key]["drawn"] = bills[key]["total"]
    out_bills[key]["equal to the digit"] = shown(out_bills[key][tkey]) == bills[key]["shown"]
# the Texas default energy charge, derived again from its own arithmetic line
tx = rules["TX"]
txd = tx["energy_default"]["eia_row"]["value"] / 1000 - sum(p["rate"] for p in tx["per_kwh"]) - sum(f["rate"] for f in tx["fixed"]) / tx["defaults"]["kwh"]

# B3 and B4: the wholesale dollars and share of the two default bills, from the local cost_of_power_monthly
rows = {}
with COP.open(encoding="utf-8") as fh:
    rd = csv.DictReader(line for line in fh if not line.startswith("#"))
    for r_ in rd:
        rows.setdefault((r_["entity"], r_["ts_utc"][:7]), {})[r_["variable"]] = float(r_["value"])
b34 = {}
for key in ("CA", "TX"):
    ent = rules[key]["wholesale_entity"]
    full = sorted(m for (e, m), v in rows.items() if e == ent and "rt_hours" in v and v.get("rt_hours") == v.get("hours_in_month") and "rt_load_weighted" in v)
    m = full[-1]
    price = rows[(ent, m)]["rt_load_weighted"]
    tot_ = out_bills[key]["by components" if key == "CA" else "total"]
    wh = 600 * price / 1000
    b34[key] = {"entity": ent, "month": m, "price": price, "wholesale": wh, "share": wh / tot_ * 100, "shown": (shown(price), shown(wh), shown(wh / tot_ * 100)),
                "simple mean that month": rows[(ent, m)].get("rt_simple_mean"),
                "with 5 percent losses": (shown(wh * 1.05), shown(wh * 1.05 / tot_ * 100))}

res = {"figures restated": total_figs, "equal to the digit in order": equal_figs, "problems": problems, "words": WORDS, "map legend ends (lo, hi, printed lo, printed hi, decimals)": LEG,
       "rounding (slug, q, figure, key prints, from the printed inputs prints, equal)": rounding, "bills": out_bills, "texas default energy charge derived": txd, "b3 b4": b34}
(DRAW.parent / "restate.json").write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")
print(f"figures restated {total_figs}, equal to the digit and in order {equal_figs}; problems {len(problems)}")
for slug, qs in R.items():
    print(f"  {slug}: {len(qs)} questions, {sum(len(f) for f in qs.values())} answer figures, {sum(len(q['figures']) for q in sets[slug]['questions'])} keyed figures drawn")
for p in problems:
    print("  PROBLEM", p)
print("words", WORDS)
nd = [r for r in rounding if not r[5]]
print(f"derived figures {len(rounding)}; from the printed inputs a different last digit in {len(nd)}:")
for r in nd:
    print("  ", r)
print("map legend ends", LEG)
for lid, (lo, hi, plo, phi, d) in LEG.items():
    print(f"  {lid}: file {lo} to {hi}; the map prints {plo} to {phi}")
print("rx from the map's legend:", shown(LEG["solar_ghi"][3] / LEG["solar_ghi"][2]), "key", shown(LEG["solar_ghi"][1] / LEG["solar_ghi"][0]),
      "from the answer's printed figures", shown(float(shown(LEG["solar_ghi"][1])) / float(shown(LEG["solar_ghi"][0]))))
print("r1 from the map's legend:", shown(Lr["wind_speed_100m"]["source_stats"]["max"] - LEG["wind_speed_100m"][3]), "printed source max less map top", shown(float(shown(Lr["wind_speed_100m"]["source_stats"]["max"])) - LEG["wind_speed_100m"][3]))
print("r2 from the map's legend:", shown(LEG["solar_dni"][3] / LEG["solar_ghi"][3]))
for k, v in out_bills.items():
    print("bill", k, {a: (shown(b) if isinstance(b, float) else b) for a, b in v.items()})
print("Texas default energy charge, derived again:", txd)
for k, v in b34.items():
    print("B3/B4", k, v)
