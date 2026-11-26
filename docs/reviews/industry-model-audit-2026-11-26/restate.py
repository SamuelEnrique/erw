"""Session 10224: an independent restatement of every figure /industry prints, from the page's own file.

Written from docs/methods/industry_page.md ("The page") and the page's own words (its headings, hovers and decisions),
not from site/lib/industry.ts or replication/industry/replicate.py: standard library only. For one query (the default
view when none is given) it computes, from site/data/industry.json, every figure the page marks (data-fig) and every
figure it writes as "not held", writes each as the page's words say it is written (TBtu whole from 100 up and to one
decimal below; percent to one decimal with its sign; dollars to the cent; billions to one decimal; MWh whole; TWh to
one decimal), and sets each beside the drawing made by draw_industry.mjs. It also sets the order of the industries and
of the states, the headline labels and the names in the hovers beside the drawing.

    python runs/c10224/restate.py <drawn prefix> [query string]

Exit 0 when every item is equal, 1 when one differs.
"""
import decimal
import json
import os
import re
import sys
import urllib.parse

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
F = json.load(open(os.path.join(ROOT, "site", "data", "industry.json"), encoding="utf-8"))
prefix = sys.argv[1]
query = sys.argv[2] if len(sys.argv) > 2 else ""
q = dict(urllib.parse.parse_qsl(query))
drawn = json.load(open(prefix + "_figures.json", encoding="utf-8"))
html = open(prefix + ".html", encoding="utf-8").read()
text = open(prefix + ".txt", encoding="utf-8").read()
FIG = drawn["figures"]


def rnd(v, nd):
    """Half away from zero on the decimal written, as a reader rounds (and as the browser's number formatting does)."""
    d = decimal.Decimal(repr(v)).quantize(decimal.Decimal(1).scaleb(-nd), rounding=decimal.ROUND_HALF_UP)
    return d


def grouped(v, nd):
    d = rnd(v, nd)
    s = f"{d:,.{nd}f}"
    if nd and "." in s:
        s = s.rstrip("0").rstrip(".")
    return "-0" if s == "-0" else s


def tb(v):
    return None if v is None else grouped(v, 0 if abs(v) >= 100 else 1)


def pct(v):
    return None if v is None else f"{'+' if v >= 0 else '-'}{abs(rnd(v, 1)):.1f}%"


def usd(v):
    return None if v is None else f"${rnd(v, 2):.2f}"


def bn(v):
    return None if v is None else f"${rnd(v / 1e9, 1):,.1f} bn"


def mwh(v):
    return None if v is None else f"{rnd(v, 0):,.0f}"


def twh(v):
    return None if v is None else grouped(v / 1e6, 1)


want = {}
# ---- the Monthly Energy Review: the newest month whose total is held, the same month a year before, a whole year
M = F["monthly"]
mi = {m: i for i, m in enumerate(M["months"])}
def mv(k, m):
    i = mi.get(m)
    return None if i is None else M["by_source"].get(k, [None] * len(M["months"]))[i]
last = [m for m in M["months"] if mv("total", m) is not None][-1]
ago = f"{int(last[:4]) - 1}{last[4:]}"
def ysum(k, y):
    vals = [mv(k, f"{y}-{x:02d}") for x in range(1, 13)]
    return None if any(v is None for v in vals) else sum(vals)
wy = next(y for y in range(int(last[:4]), 1972, -1) if ysum("total", y) is not None)
want["h-month"] = tb(mv("total", last))
want["h-year"] = tb(ysum("total", wy))
for k in ["total", "end_use_total", "natural_gas", "petroleum", "electricity_retail_sales", "electrical_system_losses", "renewables", "coal"]:
    a, b = mv(k, last), mv(k, ago)
    want[f"m-{k}"], want[f"m1-{k}"] = tb(a), tb(b)
    want[f"mc-{k}"] = None if a is None or b is None or b == 0 else pct(100 * (a - b) / b)
# ---- the 2022 survey: the 21 three-digit industries by their total in the region, the shares of their sum
I = F["industries"]
three = [n for n in I["industries"] if len(n) == 3 and n.isdigit()]
region = q.get("region", "us")
def reg(n, r):
    return I["industries"][n]["by_region"].get(r, {})
tot = {n: reg(n, region).get("total") for n in three}
held = sorted([n for n in three if tot[n] is not None], key=lambda n: -tot[n])
order_ind = held + [n for n in I["ranked_3_digit"] if tot.get(n) is None]
s = sum(tot[n] for n in held)
FUELS = ["total", "net_electricity", "natural_gas", "coal", "coke_and_breeze", "residual_fuel_oil", "distillate_fuel_oil", "hgl", "hydrogen", "other"]
for n in three:
    want[f"sh-{n}"] = None if len(held) < len(three) else f"{rnd(100 * tot[n] / s, 1):.1f}%"
    for fu in FUELS:
        want[f"f-{n}-{fu}"] = tb(reg(n, region).get(fu))
us_tot = {n: reg(n, "us").get("total") for n in three}
us_order = sorted([n for n in three if us_tot[n] is not None], key=lambda n: -us_tot[n])
want["h-top"] = tb(us_tot[us_order[0]])
ia, ib = q.get("a", us_order[0]), q.get("b", us_order[1])
for side, n in (("a", ia), ("b", ib)):
    for fu in FUELS:
        want[f"{side}-{fu}"] = tb(reg(n, region).get(fu))
    for e in ["elec_net_demand", "elec_purchases", "elec_transfers_in", "elec_onsite_generation", "gen_cogeneration", "gen_renewable", "gen_other", "elec_sales_transfers_offsite"]:
        want[f"e{side}-{e}"] = mwh(I["industries"][n].get("electricity_mwh", {}).get(region, {}).get(e))
# ---- the State Energy Data System: the newest year with the nation's total; states by the chosen source
S = F["states_annual"]
yrs = [int(y) for y in S["years"]]
newest = [y for i, y in enumerate(yrs) if S["states"]["US"]["consumption_tbtu"]["total"][i] is not None][-1]
year = int(q.get("year", newest))
src = q.get("src", "total")
yi = yrs.index(year)
def sv(st, k, y=year, part="consumption_tbtu"):
    a = S["states"][st].get(part, {}).get(k)
    return None if a is None else a[yrs.index(y)]
sts = [st for st in S["states"] if st != "US"]
vals = {st: sv(st, src) for st in sts}
order_st = sorted([st for st in sts if vals[st] is not None], key=lambda st: -vals[st]) + [st for st in sts if vals[st] is None]
for st in sts:
    want[f"s-{st}"] = tb(vals[st])
    if src != "total":
        want[f"st-{st}"] = tb(sv(st, "total"))
    want[f"sp-{st}"] = usd(S["states"][st]["price_usd_per_mmbtu"][yi])
    want[f"se-{st}"] = bn(sv(st, "total", part="expenditures_usd"))
tot_new = {st: sv(st, "total", newest) for st in sts}
first2 = sorted([st for st in sts if tot_new[st] is not None], key=lambda st: -tot_new[st])[:2]
sa, sb = q.get("sa", first2[0]), q.get("sb", first2[1])
E = F["electricity_sales_monthly"]
for side, st in (("sa", sa), ("sb", sb)):
    for k in ["total", "natural_gas", "petroleum", "electricity", "electrical_system_losses", "renewables", "coal"]:
        want[f"{side}-{k}"] = tb(sv(st, k))
    a0, a1 = sv(st, "total", 2019), sv(st, "total")
    want[f"{side}-chg"] = None if a0 in (None, 0) or a1 is None else pct(100 * (a1 - a0) / a0)
    want[f"{side}-price"] = usd(S["states"][st]["price_usd_per_mmbtu"][yi])
    want[f"{side}-exp"] = bn(sv(st, "total", part="expenditures_usd"))
    ms = [E["states"].get(st, [None] * len(E["months"]))[E["months"].index(f"{year}-{x:02d}")] if f"{year}-{x:02d}" in E["months"] else None for x in range(1, 13)]
    want[f"{side}-sales"] = None if any(v is None for v in ms) else twh(sum(ms))
# ---- the outlook: the iron and steel industry's total energy use, every case, the first year and every fifth year
O = F["outlook"]
oi = q.get("oi", "iron_and_steel")
names = list(O["industries"][oi])
totals = [n for n in names if (n.endswith("Total") or n.endswith("Total Energy Use")) and "Ethanol" not in n]
totals.sort(key=lambda n: 0 if n.endswith("Total Energy Use") else 1)
os_ = q.get("os", (totals + sorted(n for n in names if n not in totals))[0])
for c in O["cases"]:
    for i, y in enumerate(O["years"]):
        if i == 0 or int(y) % 5 == 0:
            want[f"o-{c}-{y}"] = tb(O["industries"][oi][os_].get(c, [None] * len(O["years"]))[i])

# ---- compare
same, diff, only_page, only_here = 0, [], [], []
for k, v in FIG.items():
    if k not in want:
        only_page.append(k)
        continue
    if v == want[k]:
        same += 1
    else:
        diff.append((k, v, want[k]))
for k in want:
    if k not in FIG:
        only_here.append(k)
print(f"query: {query or 'default'}; marked figures drawn {len(FIG)}, restated {len(want)}; equal {same}; differ {len(diff)}")
for d in diff[:40]:
    print("  DIFFER", d)
print(f"  drawn, not restated: {only_page[:20]}")
print(f"  restated, not drawn: {len(only_here)} {only_here[:12]}")
# the orders
d_ind = [m for m in re.findall(r'title="NAICS (\d+)" data-industry-rank="\d+"', html)]
d_st = re.findall(r'data-state-rank="(\d+)">\d+\. ([^<]+)<', html)
names_st = {"DC": "District of Columbia"}
ok_ind = d_ind == order_ind
print(f"  industries' order equal: {ok_ind} ({len(d_ind)} rows)")
d_st_codes = re.findall(r'data-(?:fig|not-held)="s-([A-Z]{2})"', html)
order_ok = d_st_codes == order_st
print(f"  states' order equal: {order_ok} ({len(d_st_codes)} rows; first five drawn {[n for _, n in d_st[:5]]})")
# the labels and the names the hovers carry
months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
labels = {
    "latest month words": f"{months[int(last[5:]) - 1]} {last[:4]}: {M['labels']['total']}",
    "whole year label": f"Industrial sector, {wy}",
    "largest industry note": f"{I['industries'][us_order[0]]['name']} (NAICS {us_order[0]}), United States",
    "industries hover": f"Industry A is {I['industries'][ia]['name']} and Industry B is {I['industries'][ib]['name']}",
    "states hover": f"the two largest by the industrial sector's total consumption in {newest}",
    "file built": f"File built {F['built'][:10]}",
    "outlook to": f"EIA's outlook to {O['years'][-1]}",
    "decision first-two": f"{I['industries'][us_order[0]]['name']} and {I['industries'][us_order[1]]['name']}; Texas and Louisiana in {newest}" if first2 == ["TX", "LA"] else "states differ",
}
lab_ok = 0
for k, v in labels.items():
    hit = v in text or any(v in h for h in drawn["hovers"])
    lab_ok += hit
    print(f"  label {k}: {'equal' if hit else 'MISSING'} ({v})")
bad = len(diff) + (0 if ok_ind else 1) + (0 if order_ok else 1) + (len(labels) - lab_ok)
print(f"items: {same} figures + 2 orders + {lab_ok} labels equal; {bad} not")
sys.exit(1 if bad else 0)
