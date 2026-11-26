"""Session 10224: one rule changed at a time, and the size of each claim, on /industry's own file (site/data/industry.json).

Standard library only; reads the file and nothing else. Prints one block a measure.
    python runs/c10224/measures.py
"""
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
F = json.load(open(os.path.join(ROOT, "site", "data", "industry.json"), encoding="utf-8"))
M, I, S, E, O = F["monthly"], F["industries"], F["states_annual"], F["electricity_sales_monthly"], F["outlook"]
mi = {m: i for i, m in enumerate(M["months"])}
yrs = [int(y) for y in S["years"]]
THREE = [n for n in I["industries"] if len(n) == 3 and n.isdigit()]
BTU = 3412  # Btu per kWh, EIA's heat content of electricity


def mv(k, m):
    return M["by_source"][k][mi[m]] if m in mi else None


def ysum(k, y):
    v = [mv(k, f"{y}-{x:02d}") for x in range(1, 13)]
    return None if any(a is None for a in v) else sum(v)


def reg(n, r="us"):
    return I["industries"][n]["by_region"].get(r, {})


def el(n, r="us"):
    return I["industries"][n].get("electricity_mwh", {}).get(r, {})


def sv(st, k, y, part="consumption_tbtu"):
    a = S["states"][st].get(part, {}).get(k)
    return None if a is None else a[yrs.index(y)]


def price(st, y):
    return S["states"][st]["price_usd_per_mmbtu"][yrs.index(y)]


print("== 1. The headline row: the Monthly Energy Review's sector against the survey's manufacturing fuel, 2022")
mer22 = ysum("total", 2022)
mer22_end = ysum("end_use_total", 2022)
allm = reg("total") if "total" in I["industries"] else {}
sum21 = sum(reg(n)["total"] for n in THREE if reg(n).get("total") is not None)
print(f"MER industrial total 2022 {mer22:,.3f} TBtu; end use {mer22_end:,.3f}; MECS all manufacturing fuel {allm.get('total')}; the 21 three-digit industries {sum21:,.0f}")
print(f"MECS fuel as percent of MER total {100 * allm.get('total', sum21) / mer22:.1f}; of MER end use {100 * allm.get('total', sum21) / mer22_end:.1f}")
print(f"Chemicals (325) fuel 3,976 TBtu as percent of the MER 2025 sector total {100 * reg('325')['total'] / ysum('total', 2025):.1f}")

print("\n== 2. MECS 'Net electricity' (Table 3.2) restated from Table 11.1 and 11.3, and against net demand")
rows = []
for n in sorted(I["industries"]):
    e, f = el(n), reg(n)
    need = ["elec_purchases", "elec_transfers_in", "elec_sales_transfers_offsite"]
    if f.get("net_electricity") is None or any(e.get(k) is None for k in need):
        continue
    gr = e.get("gen_renewable") or 0.0
    net = (e["elec_purchases"] + e["elec_transfers_in"] + gr - e["elec_sales_transfers_offsite"]) * BTU / 1e9
    rows.append((n, f["net_electricity"], round(net, 1), abs(net - f["net_electricity"]) <= 1.0))
ok = sum(r[3] for r in rows)
print(f"industries with every component: {len(rows)}; net electricity = (purchases + transfers in + renewable generation - sales offsite) at 3,412 Btu/kWh within 1 TBtu: {ok}")
print("  misses:", [r for r in rows if not r[3]][:8])
print("three-digit industries, US: net electricity (TBtu) as TWh, net demand TWh, onsite generation TWh, net electricity as percent of net demand")
share = []
for n in THREE:
    e, f = el(n), reg(n)
    if f.get("net_electricity") is None or e.get("elec_net_demand") is None:
        continue
    ne = f["net_electricity"] * 1e9 / BTU / 1e6
    nd = e["elec_net_demand"] / 1e6
    share.append((n, I["industries"][n]["name"], round(ne, 1), round(nd, 1), round((e.get("elec_onsite_generation") or 0) / 1e6, 1), round(100 * ne / nd, 1)))
for r in sorted(share, key=lambda r: r[5])[:8]:
    print("  ", r)
t = el("total") if "total" in I["industries"] else {}
if t:
    print(f"all manufacturing: net demand {t['elec_net_demand']:,.0f} MWh; onsite generation {t['elec_onsite_generation']:,.0f} ({100 * t['elec_onsite_generation'] / t['elec_net_demand']:.1f} percent); purchases {t['elec_purchases']:,.0f}; net electricity {reg('total')['net_electricity']} TBtu = {reg('total')['net_electricity'] * 1e9 / BTU / 1e6:,.1f} TWh")
for r in ["us", "northeast", "midwest", "south", "west"]:
    e = el("total", r)
    if e.get("elec_net_demand") and e.get("elec_onsite_generation") is not None:
        print(f"  region {r}: onsite generation {100 * e['elec_onsite_generation'] / e['elec_net_demand']:.1f} percent of net demand ({e['elec_onsite_generation'] / 1e6:,.1f} of {e['elec_net_demand'] / 1e6:,.1f} TWh)")

print("\n== 3. The largest industry by another measure (US, three-digit)")
def order(key, fn):
    v = [(n, fn(n)) for n in THREE]
    v = sorted([x for x in v if x[1] is not None], key=lambda x: -x[1])
    return [(n, I["industries"][n]["name"], round(x, 1)) for n, x in v[:6]]
print("by fuel total (the page):", order("t", lambda n: reg(n).get("total")))
print("by net demand for electricity, TWh:", order("nd", lambda n: (el(n).get("elec_net_demand") or None) and el(n)["elec_net_demand"] / 1e6))
print("by electricity purchases, TWh:", order("p", lambda n: (el(n).get("elec_purchases") or None) and el(n)["elec_purchases"] / 1e6))
print("by fuel less 'Other' (byproduct and other fuels), TBtu:", order("o", lambda n: None if reg(n).get("total") is None or reg(n).get("other") is None else reg(n)["total"] - reg(n)["other"]))

print("\n== 4. The states' 'Average price' against the expenditures and the total printed beside it, 2024")
fits = {}
for st in sorted(S["states"]):
    p, x, tot = price(st, 2024), sv(st, "total", 2024, "expenditures_usd"), sv(st, "total", 2024)
    if not p or x is None or not tot:
        continue
    q = x / p / 1e6  # TBtu the price is per
    end, loss = sv(st, "end_use_total", 2024), sv(st, "electrical_system_losses", 2024)
    fits[st] = (round(q, 1), tot, round(100 * q / tot, 1), round(x / tot / 1e6, 2), p, end, round(100 * q / end, 1) if end else None)
for st in ["US", "TX", "LA", "CA", "PA", "IN", "OH", "HI", "AK", "WY"]:
    if st in fits:
        q, tot, pc, naive, p, end, pe = fits[st]
        print(f"  {st}: expenditures / price = {q:,.1f} TBtu; Total printed {tot:,.1f} ({pc} percent of it); expenditures / Total = ${naive}/MMBtu against the printed ${p}; as percent of end use {pe}")
pcs = sorted(v[2] for v in fits.values())
print(f"  over {len(fits)} rows: the price's quantity is {pcs[0]} to {pcs[-1]} percent of the Total printed; median {pcs[len(pcs) // 2]}")

print("\n== 5. What an industrial buyer asks: electricity and natural gas by state, 2024 (SEDS expenditures over consumption)")
ep = {}
for st in sorted(S["states"]):
    xe, qe = sv(st, "electricity", 2024, "expenditures_usd"), sv(st, "electricity", 2024)
    xg, qg = sv(st, "natural_gas", 2024, "expenditures_usd"), sv(st, "natural_gas", 2024)
    ep[st] = (None if not xe or not qe else round(xe / (qe * 1e9 / BTU), 2), None if not xg or not qg else round(xg / (qg * 1e6), 2))
for st in ["US", "TX", "LA", "CA", "PA", "OH", "IN", "HI"]:
    print(f"  {st}: electricity ${ep[st][0]}/MWh; natural gas ${ep[st][1]}/MMBtu; the page's all-fuel price ${price(st, 2024)}/MMBtu")
cheap = sorted([(v[0], st) for st, v in ep.items() if v[0] and st != "US"])
print("  cheapest electricity:", cheap[:5], "dearest:", cheap[-5:])

print("\n== 6. The states ranked by another total, 2024 (top six)")
sts = [st for st in S["states"] if st != "US"]
def top(fn):
    v = sorted([(fn(st), st) for st in sts if fn(st) is not None], reverse=True)
    return [(st, round(x, 1)) for x, st in v[:6]]
print("by total (the page):", top(lambda st: sv(st, "total", 2024)))
print("by end use (losses out):", top(lambda st: sv(st, "end_use_total", 2024)))
print("by total less HGL:", top(lambda st: None if sv(st, "hgl", 2024) is None else sv(st, "total", 2024) - sv(st, "hgl", 2024)))
print("by electricity sold:", top(lambda st: sv(st, "electricity", 2024)))
for st in ["TX", "LA", "US"]:
    print(f"  {st}: HGL {sv(st, 'hgl', 2024):,.1f} of total {sv(st, 'total', 2024):,.1f} ({100 * sv(st, 'hgl', 2024) / sv(st, 'total', 2024):.1f} percent); petroleum {sv(st, 'petroleum', 2024):,.1f}; losses {sv(st, 'electrical_system_losses', 2024):,.1f}")
print("  the table's parts drawn (natural gas, petroleum, electricity, losses, renewables, coal) summed against the total:")
for st in ["TX", "LA", "CA", "US"]:
    parts = sum(sv(st, k, 2024) or 0 for k in ["natural_gas", "petroleum", "electricity", "electrical_system_losses", "renewables", "coal"])
    print(f"    {st}: parts {parts:,.1f}; total {sv(st, 'total', 2024):,.1f}; gap {sv(st, 'total', 2024) - parts:,.1f}")

print("\n== 7. The monthly change: one month against twelve")
last = [m for m in M["months"] if mv("total", m) is not None][-1]
y, mo = int(last[:4]), int(last[5:])
def roll(k, y, mo):
    out = []
    for i in range(12):
        mm, yy = mo - i, y
        while mm <= 0:
            mm += 12
            yy -= 1
        out.append(mv(k, f"{yy}-{mm:02d}"))
    return sum(out)
for k in ["total", "natural_gas", "petroleum", "electricity_retail_sales", "coal"]:
    a, b = mv(k, last), mv(k, f"{y - 1}-{mo:02d}")
    ra, rb = roll(k, y, mo), roll(k, y - 1, mo)
    print(f"  {k}: {last} on a year before {100 * (a - b) / b:+.1f} percent; twelve months to {last} on the twelve before {100 * (ra - rb) / rb:+.1f} percent")

print("\n== 8. Shares of what total")
held = [reg(n)["total"] for n in THREE if reg(n).get("total") is not None]
print(f"  sum of the 21 three-digit totals {sum(held):,.0f}; all manufacturing {allm.get('total')}; chemicals' share of the 21 {100 * reg('325')['total'] / sum(held):.2f}; of all manufacturing {100 * reg('325')['total'] / allm.get('total', 1):.2f}")
for r in ["us", "northeast", "midwest", "south", "west"]:
    wh = [n for n in THREE if reg(n, r).get("total") is None]
    print(f"  region {r}: three-digit totals withheld {len(wh)} {wh}; shares drawn {'none' if wh else 'all 21'}")

print("\n== 9. The not-held cells of the default view (US, the 21 industries, ten fuels)")
nh = {}
for n in THREE:
    for fu in I["fuels"]:
        if reg(n).get(fu) is None:
            nh.setdefault(fu, []).append(n)
print("  ", {k: len(v) for k, v in nh.items()}, "total", sum(len(v) for v in nh.values()))
zeros = sum(1 for n in THREE for fu in I["fuels"] if reg(n).get(fu) == 0)
print(f"  cells printed 0: {zeros}")

print("\n== 10. The outlook's iron and steel against the survey")
o = O["industries"]["iron_and_steel"]["Iron and Steel : Energy Use : Total"]
print(f"  AEO2026 iron and steel total energy use, 2025, Counterfactual Baseline {o['cb2026'][0]} TBtu; MECS 2022 331110 fuel total {reg('331110').get('total')}; 331 {reg('331')['total']}")
print(f"  outlook history years in the file: {O['history_years']}; first year {O['years'][0]}")
bc = O["industries"]["bulk_chemicals"]
print("  bulk chemicals series:", [k for k in bc][:40])

print("\n== 11. A state's change since 2019 on another base")
for st in ["TX", "LA"]:
    for b in [2018, 2019, 2021]:
        a0, a1 = sv(st, "total", b), sv(st, "total", 2024)
        print(f"  {st} total {b} to 2024: {100 * (a1 - a0) / a0:+.1f} percent")
print("\n== 12. A region's shares on the survey's own all-manufacturing total, where one industry's total is withheld")
for r in ["northeast", "midwest", "south", "west"]:
    allr = reg("total", r).get("total") if "total" in I["industries"] else None
    held = sorted([(reg(n, r)["total"], n) for n in THREE if reg(n, r).get("total") is not None], reverse=True)
    s21 = sum(v for v, _ in held)
    top = [(n, I["industries"][n]["name"], v, round(100 * v / allr, 1) if allr else None) for v, n in held[:3]]
    print(f"  {r}: all manufacturing {allr}; held three-digit sum {s21:,.0f} ({len(held)} of 21; the withheld at most {allr - s21 if allr else None:,.0f}); top three on all manufacturing {top}")
sys.exit(0)
