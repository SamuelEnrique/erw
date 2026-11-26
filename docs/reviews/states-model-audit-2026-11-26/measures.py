"""Session 10223 (states audit): measures on the page's files and the main copy's tables (read only).

    python measures.py <warehouse output dir> <site/data/states dir>

Each block prints one measure the audit cites. Standard library only.
"""
import csv
import json
import os
import sys
from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP

OUT, SD = sys.argv[1:3]
SRCS = ["coal", "natural_gas", "nuclear", "hydro", "wind", "solar", "other_renewables", "oil_and_other", "not_itemized"]
idx = json.load(open(os.path.join(SD, "index.json"), encoding="utf-8"))
F = {r["state"]: json.load(open(os.path.join(SD, r["file"]), encoding="utf-8")) for r in idx["states"]}


def rows(name, need=None):
    with open(os.path.join(OUT, name + ".csv"), encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(ln for ln in fh if not ln.startswith("#")):
            if need is None or need(r):
                yield r


def js_fixed(v, nd):
    """JavaScript's toFixed: the exact binary value, ties to the larger."""
    return str(Decimal(v).quantize(Decimal(1).scaleb(-nd), rounding=ROUND_HALF_UP))


def hu(v, nd):
    return str(Decimal(repr(v)).quantize(Decimal(1).scaleb(-nd), rounding=ROUND_HALF_UP))


print("== 1. Sources summed over fewer than twelve months in the last twelve months (DC, NE, AK, UT)")
for st in ("DC", "NE", "AK", "UT"):
    g = F[st]["generation"]
    last = g["months"][-12:]
    for s in SRCS:
        a = g["by_source"][s][-12:]
        if any(v is None for v in a) and any(v is not None for v in a):
            miss = [m for m, v in zip(last, a) if v is None]
            ni = g["by_source"]["not_itemized"][-12:]
            ni_in_miss = [ni[last.index(m)] for m in miss]
            print(f"  {st} {s}: missing {miss}; share printed {g['last12']['share_pct'][s]}; not itemized in those months {ni_in_miss}; "
                  f"months held {[v for v in a if v is not None][:12]}")
    top = max(SRCS, key=lambda s: g["last12"]["share_pct"][s] if g["last12"]["share_pct"][s] is not None else -1)
    print(f"  {st}: headline largest source {top} {g['last12']['share_pct'][top]}; total {g['last12']['total_mwh']}")

print("\n== 2. Double rounding: the file's rounded figure rounded again by the page")
n_price = n_price_bad = 0
bad_price = []
for st, f in F.items():
    r = f["retail"]
    if not r.get("last12"):
        continue
    for sec, b in r["last12"]["by_sector"].items():
        if b["price_usd_per_mwh"] is None:
            continue
        n_price += 1
        exact = b["revenue_usd"] / b["sales_mwh"]
        shown = js_fixed(b["price_usd_per_mwh"] / 10, 2)
        true = hu(exact / 10, 2)
        if shown != true:
            n_price_bad += 1
            bad_price.append((st, sec, b["price_usd_per_mwh"], round(exact, 4), shown, true))
print(f"  twelve-month prices (cents a kWh): {n_price_bad} of {n_price} print a last digit other than revenue over sales rounded once")
for x in bad_price:
    print("   ", x)
n_sh = n_sh_bad = 0
bad_sh = []
for st, f in F.items():
    g = f["generation"]
    if not g.get("last12"):
        continue
    for s in SRCS:
        v, m = g["last12"]["share_pct"][s], g["last12"]["mwh"][s]
        if v is None:
            continue
        n_sh += 1
        exact = 100 * m / g["last12"]["total_mwh"]
        if js_fixed(v, 1) != hu(exact, 1):
            n_sh_bad += 1
            bad_sh.append((st, s, v, round(exact, 4), js_fixed(v, 1), hu(exact, 1)))
print(f"  twelve-month shares: {n_sh_bad} of {n_sh} print a last digit other than the share rounded once")
for x in bad_sh:
    print("   ", x)
n_sv = n_sv_bad = 0
bad_sv = []
for st, f in F.items():
    s = f["serving"]
    if not s.get("by_authority") or s.get("shares_reason"):
        continue
    tot = sum(a["population"] for a in s["by_authority"])
    for a in s["by_authority"]:
        n_sv += 1
        exact = 100 * a["population"] / tot
        if js_fixed(a["share_pct"], 1) != hu(exact, 1):
            n_sv_bad += 1
            bad_sv.append((st, a["code"], a["share_pct"], round(exact, 4), js_fixed(a["share_pct"], 1), hu(exact, 1)))
print(f"  shares of the people: {n_sv_bad} of {n_sv} print a last digit other than the share rounded once")
for x in bad_sv:
    print("   ", x)

print("\n== 3. Pumped storage: which group it is in, in generation and in capacity")
ps = defaultdict(float)
hy = defaultdict(float)
st_ = defaultdict(float)
for r in rows("eia860m_operating_generators"):
    try:
        mw = float(r["nameplate_mw"])
    except ValueError:
        mw = 0.0
    if r["technology"] == "Hydroelectric Pumped Storage":
        ps[r["state"]] += mw
        if r["technology_group"] != "storage":
            print("   pumped storage outside storage:", r["state"], r["technology_group"])
    if r["technology_group"] == "hydro":
        hy[r["state"]] += mw
    if r["technology_group"] == "storage":
        st_[r["state"]] += mw
tot_ps = sum(ps.values())
print(f"  EIA-860M pumped storage, nameplate: {tot_ps:,.1f} MW in {len(ps)} states, all in the group 'storage' (the page: 'Batteries and pumped storage'); the group 'hydro' (the page: 'Hydro (with pumped storage)') holds none")
for s, mw in sorted(ps.items(), key=lambda kv: -kv[1])[:6]:
    print(f"   {s}: pumped storage {mw:,.1f} MW of storage {st_[s]:,.1f}; hydro {hy[s]:,.1f}")
for st in ("VA", "CA", "US"):
    g = F[st]["generation"]
    print(f"  {st} generation, oil and other (which holds EIA's HPS, pumped storage), last twelve months: {g['last12']['mwh']['oil_and_other']:,.1f} MWh; months below zero since 2015: "
          f"{sum(1 for m, v in zip(g['months'], g['by_source']['oil_and_other']) if v is not None and v < 0 and m >= '2015')}")
neg = sorted(((st, s, y, v) for st, f in F.items() for s in SRCS for y, v in zip(f["generation"]["years"], f["generation"]["annual"][s]) if v is not None and v < 0), key=lambda x: x[3])
print(f"  whole years below zero: {len(neg)}, by source: { {s: sum(1 for x in neg if x[1] == s) for s in SRCS if any(x[1] == s for x in neg)} }; lowest {neg[:3]}")

print("\n== 4. A state spanning grids: people against generating capacity, by authority (EIA-860M plants' authority)")
cap = defaultdict(lambda: defaultdict(float))
for r in rows("eia860m_operating_generators"):
    try:
        mw = float(r["nameplate_mw"])
    except ValueError:
        mw = 0.0
    cap[r["state"]][r["balancing_authority"] or "none named"] += mw
for st in ("TX", "IL", "IN", "LA", "MN", "NM", "MO", "KY"):
    s = F[st]["serving"]
    tot = sum(cap[st].values())
    people = {a["code"]: a["share_pct"] for a in s["by_authority"]} if s.get("by_authority") else {}
    capsh = {k: round(100 * v / tot, 2) for k, v in sorted(cap[st].items(), key=lambda kv: -kv[1])[:5]}
    print(f"  {st}: people {people}; capacity {capsh}")

print("\n== 5. What is coming: under construction against planned")
coming = defaultdict(lambda: [0.0, 0.0])
for r in rows("eia860m_planned_generators"):
    try:
        mw = float(r["nameplate_mw"])
    except ValueError:
        mw = 0.0
    for k in (r["state"], "US"):
        coming[k][0] += mw
        if r["status"] == "under_construction":
            coming[k][1] += mw
for st in ("TX", "CA", "VA", "US"):
    a, b = coming[st]
    print(f"  {st}: planned and under construction {a:,.0f} MW, of which under construction {b:,.0f} ({100 * b / a:.1f} percent)")
stat = defaultdict(float)
for r in rows("eia860m_planned_generators", lambda r: r["state"] == "TX"):
    try:
        stat[r["eia_status_label"]] += float(r["nameplate_mw"])
    except ValueError:
        pass
print("  Texas by EIA's status:", {k: round(v) for k, v in sorted(stat.items(), key=lambda kv: -kv[1])})

print("\n== 6. Capacity holds storage")
for st in ("TX", "CA", "AZ", "US"):
    p = F[st]["plants"]
    s = (p["capacity_by_technology"].get("storage") or {}).get("nameplate_mw") or 0
    print(f"  {st}: storage {s:,.1f} of {p['capacity_total_mw']:,.1f} MW ({100 * s / p['capacity_total_mw']:.1f} percent)")

print("\n== 7. The United States against the sum of the states, and Puerto Rico")
sums = defaultdict(float)
for st, f in F.items():
    if st == "US":
        continue
    sums["gen"] += f["generation"]["last12"]["total_mwh"]
    sums["cap"] += f["plants"]["capacity_total_mw"] or 0
    sums["sales"] += f["retail"]["last12"]["by_sector"]["all"]["sales_mwh"] or 0
us = F["US"]
print(f"  generation last twelve months: US {us['generation']['last12']['total_mwh']:,.1f}, sum of 51 {sums['gen']:,.1f}")
print(f"  capacity: US {us['plants']['capacity_total_mw']:,.1f}, sum of 51 {sums['cap']:,.1f}")
print(f"  retail sales: US {us['retail']['last12']['by_sector']['all']['sales_mwh']:,.1f}, sum of 51 {sums['sales']:,.1f}")
pr_op = sum(float(r["nameplate_mw"] or 0) for r in rows("eia860m_operating_generators", lambda r: r["state"] == "PR"))
pr_pl = sum(1 for _ in rows("eia860m_planned_generators", lambda r: r["state"] == "PR"))
other = sorted({r["state"] for r in rows("eia860m_operating_generators")} - set(F))
print(f"  EIA-860M operating generators in places with no file: {other}; Puerto Rico {pr_op:,.1f} MW nameplate, {pr_pl} planned rows")
pr_sales = sum(1 for _ in rows("eia_retail_sales_monthly", lambda r: r["entity"].split(":")[2] == "PR"))
print(f"  retail sales rows for PR: {pr_sales}")

print("\n== 8. CO2 per MWh generated: EIA's rate against the file's tons over the profile's net generation")
gaps = []
for st, f in F.items():
    c, d = f["co2"], f["disposition"]
    if not c.get("years") or not d.get("years"):
        continue
    y = c["years"][-1]
    t = c["tons_by_fuel"]["all"][-1]
    if y in d["years"] and t is not None:
        g = d["values"]["total_net_generation"][d["years"].index(y)]
        r = c["rate_kg_per_mwh"][-1]
        mine = 1000 * t / g
        gaps.append((st, y, r, round(mine, 1), round(100 * (r - mine) / mine, 2)))
gaps.sort(key=lambda x: -abs(x[4]))
print(f"  {len(gaps)} places; largest relative gaps: {gaps[:6]}; within 1 percent: {sum(1 for x in gaps if abs(x[4]) <= 1)}")

print("\n== 9. Supply and disposition: generation + imports + net interstate trade against sales + losses + exports")
for st in ("TX", "CA", "VA", "VT", "WV", "DC"):
    d = F[st]["disposition"]
    if not d.get("years"):
        continue
    i = len(d["years"]) - 1
    v = {k: (a[i] if a else None) for k, a in d["values"].items()}
    sup = v["total_net_generation"] + (v["total_international_imports"] or 0) + v["net_interstate_trade"]
    dis = v["full_service_providers"] + v["energy_only_providers"] + v["estimated_losses"] + (v["total_international_exports"] or 0)
    print(f"  {st} {d['years'][i]}: supply {sup:,.0f}, sales+losses+exports {dis:,.0f}, rest (direct use and unaccounted) {sup - dis:,.0f} ({100 * (sup - dis) / sup:.2f} percent)")

print("\n== 10. Total energy against the five fuels; electricity sold is made from them")
for st in ("TX", "CA", "VA", "WV", "US"):
    e = F[st]["energy"]
    i = len(e["years"]) - 1
    b = {k: (a[i] if a else None) for k, a in e["by_source"].items()}
    five = sum(b[k] for k in ("coal", "natural_gas", "petroleum", "nuclear", "renewables"))
    print(f"  {st} {e['years'][i]}: total {b['total']:,.1f}; five fuels {five:,.1f}; total less five {b['total'] - five:,.1f}; electricity sold {b['electricity_retail_sales']:,.1f}")

print("\n== 11. The all-sector price against the price at one sector mix (the United States' twelve months)")
us12 = F["US"]["retail"]["last12"]["by_sector"]
secs = ("residential", "commercial", "industrial", "transportation")
w = {s: us12[s]["sales_mwh"] / us12["all"]["sales_mwh"] for s in secs}
rank_a, rank_b = [], []
for st, f in F.items():
    if st == "US":
        continue
    b = f["retail"]["last12"]["by_sector"]
    if any(b[s]["price_usd_per_mwh"] is None for s in secs[:3]):
        continue
    fixed = sum(w[s] * (b[s]["price_usd_per_mwh"] or 0) for s in secs[:3]) / sum(w[s] for s in secs[:3])
    rank_a.append((b["all"]["price_usd_per_mwh"], st))
    rank_b.append((fixed, st))
ra = {st: i + 1 for i, (_, st) in enumerate(sorted(rank_a))}
rb = {st: i + 1 for i, (_, st) in enumerate(sorted(rank_b))}
moves = sorted(((abs(ra[s] - rb[s]), s, ra[s], rb[s]) for s in ra), reverse=True)
print(f"  US weights {({k: round(v, 4) for k, v in w.items()})}; places ranked {len(ra)}")
print(f"  rank by all-sector price (1 = cheapest) against rank at the US mix, largest moves: {moves[:8]}")
for st in ("TX", "CA", "LA", "WV", "VA"):
    b = F[st]["retail"]["last12"]["by_sector"]
    fixed = [x for x, s in rank_b if s == st][0]
    ind_share = b["industrial"]["sales_mwh"] / b["all"]["sales_mwh"]
    print(f"   {st}: all-sector {b['all']['price_usd_per_mwh']/10:.2f} cents (rank {ra[st]}), at the US mix {fixed/10:.2f} (rank {rb[st]}); industrial share of sales {100*ind_share:.1f} percent")

print("\n== 12. Figures under the last digit shown, printed as zero")
tiny = []
for st, f in F.items():
    for sec, b in (f["retail"].get("last12") or {"by_sector": {}})["by_sector"].items():
        if b["sales_mwh"] and 0 < b["sales_mwh"] < 50000:
            tiny.append((st, sec, b["sales_mwh"], b["revenue_usd"]))
    g = f["generation"].get("last12")
    if g:
        for s in SRCS:
            v = g["share_pct"][s]
            if v is not None and v != 0 and abs(v) < 0.05:
                tiny.append((st, s, "share", v))
print(f"  {len(tiny)} figures print as 0.0 or $0.00 bn or 0.0% though the file holds a figure other than zero; e.g. {tiny[:6]}")

print("\n== 13. The ten largest plants: a plant whose authority is another state's grid")
for st in ("TX",):
    for p in F[st]["plants"]["largest"]:
        print(f"   {p['name']}: {p['balancing_authority']}, {p['nameplate_mw']} MW")
