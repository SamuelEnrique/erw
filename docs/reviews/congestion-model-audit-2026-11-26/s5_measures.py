"""Session 10220: one rule changed at a time, and the claims measured, from site/data/conditions/congestion.json alone.
Read only. Writes measures.json beside it.
usage: s5_measures.py"""
import json
import os
import re
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
F = json.load(open(os.path.join(ROOT, "site", "data", "conditions", "congestion.json"), encoding="utf-8"))
M = {}


def label(c):  # the page's label (constraintLabel): the name, and the contingency unless it is BASE
    return f"{c['name']} (contingency {c['contingency']})" if c["contingency"] and c["contingency"] != "BASE" else c["name"]


# 1. One element under several keys: the same label twice, and the same name under several contingencies
print("== 1. Names and keys")
for op, O in F["constraints"].items():
    by_label = defaultdict(list)
    by_name = defaultdict(list)
    for k, c in O["constraints"].items():
        by_label[label(c)].append(k)
        by_name[c["name"]].append(k)
    twice = {l: ks for l, ks in by_label.items() if len(ks) > 1}
    print(f"{op}: {len(O['constraints'])} detailed keys; labels drawn identically for two or more keys: {len(twice)}")
    for l, ks in list(twice.items())[:8]:
        print("   ", l, "<-", ks, [sorted(O["constraints"][k]["by_year"]) for k in ks])
    multi = {n: ks for n, ks in by_name.items() if len(ks) > 1}
    print(f"   names under two or more keys among the detailed: {len(multi)}")
    M[f"{op}_same_label"] = {l: ks for l, ks in twice.items()}
    # every year held, and the newest year: ranks by key against ranks by name (summing the detailed keys of a name)
    for yr in ("all", O["years"][-1], "2025"):
        def fig(c, f):
            return c[f] if yr == "all" else c["by_year"].get(yr, {}).get(f, 0) or 0
        for f, top in (("hours", "by_hours"), ("cost", "by_cost")):
            keyed = O["top"][yr][top]
            agg = defaultdict(float)
            for k, c in O["constraints"].items():
                agg[c["name"]] += fig(c, f)
            named = sorted(agg, key=lambda n: -agg[n])[:25]
            keyed_names = [O["constraints"][k]["name"] for k in keyed]
            first_by_key = O["constraints"][keyed[0]]
            print(f"   {yr} {top}: first by key {keyed[0]} ({fig(first_by_key, f):,.1f}); first by name {named[0]} ({agg[named[0]]:,.1f});"
                  f" names in the keyed top 25 that recur: {len(keyed_names) - len(set(keyed_names))}; names of the named top 25 not in the keyed list: {len(set(named) - set(keyed_names))}")
            M[f"{op}_{yr}_{top}_first_by_name"] = [named[0], agg[named[0]], keyed[0], fig(first_by_key, f)]
            M[f"{op}_{yr}_{top}_named_top10"] = [(n, round(agg[n], 1)) for n in named[:10]]

# the market monitor's four SPP flowgates of 2025 (the note's cross-check ranks them by name): their ranks on the page
print("\n== 1b. The SPP monitor's four flowgates of 2025, on the page's list (by key) and by name")
O = F["constraints"]["spp"]
keyed = O["top"]["2025"]["by_cost"]
for n in ["OSAWEBCLESOO", "TMP128_29363", "TMP563_26603", "TMP266_27514"]:
    pos = [(i + 1, k, O["constraints"][k]["by_year"]["2025"]["cost"]) for i, k in enumerate(keyed) if O["constraints"][k]["name"] == n]
    print(f"   {n}: on the page's 2025 cost list at {pos if pos else 'not in the 25'}")

# 2. Shadow prices at a ceiling: a highest of exactly 1,500.00 (SPP) and the months whose highest reaches it
print("\n== 2. The highest shadow prices")
for op, O in F["constraints"].items():
    tops = defaultdict(int)
    months_at = []
    for k, c in O["constraints"].items():
        for m in c["monthly"]:
            if m[3] is not None and m[3] >= 1499.995:
                months_at.append((k, m[0], m[1], m[2], m[3]))
        tops[round(c["abs_max"] or 0, 2)] += 1
    common = sorted(tops.items(), key=lambda kv: -kv[1])[:6]
    print(f"{op}: the most common highest values among detailed constraints: {common}")
    print(f"   constraint-months whose highest is 1,500.00 or more: {len(months_at)}; the largest highest held: {max((c['abs_max'] or 0) for c in O['constraints'].values())}")
    yr = O["years"][-1]
    for top in ("by_hours", "by_cost"):
        hi = [O["constraints"][k]["by_year"][yr]["abs_max"] for k in O["top"][yr][top]]
        print(f"   {yr} {top}: of the 25, highest at 1,500.00: {sum(h >= 1499.995 for h in hi)}; at 1,400 or more: {sum(h >= 1400 for h in hi)}")
    M[f"{op}_months_at_1500"] = len(months_at)

# 3. A few extreme months: the share of a constraint's summed shadow price that its largest month carries (newest year)
print("\n== 3. How much of a year's sum one month carries")
for op, O in F["constraints"].items():
    yr = O["years"][-1]
    shares = []
    for i, k in enumerate(O["top"][yr]["by_cost"][:10]):
        c = O["constraints"][k]
        ms = [(m[0], m[1] * m[2]) for m in c["monthly"] if m[0][:4] == yr]
        tot = sum(v for _, v in ms)
        big = max(ms, key=lambda t: t[1])
        shares.append(big[1] / tot)
        print(f"   {op} {yr} cost rank {i + 1} {label(c)}: {len(ms)} months; its largest month {big[0]} carries {100 * big[1] / tot:.0f} percent")
    M[f"{op}_{yr}_top10_cost_largest_month_share_median"] = sorted(shares)[len(shares) // 2]

# 4. A place's year mean and its months: SPP North 2026, with and without January (Winter Storm of January 2026?)
print("\n== 4. A place's year mean against its months")
P = {p["id"]: p for op in F["places"] for p in F["places"][op]}
def ymean(pid, y, col, drop=()):
    ms = [m for m in P[pid]["monthly"] if m[0][:4] == y and m[0] not in drop and m[col] is not None]
    h = sum(m[1] for m in ms)
    return sum(m[1] * m[col] for m in ms) / h
for pid in ("spp:SPPNORTH_HUB", "spp:SPPSOUTH_HUB"):
    print(f"   {pid}: months of 2025 and 2026 [month, hours, LMP, energy, congestion, loss]:")
    for m in P[pid]["monthly"]:
        if m[0] >= "2025-01":
            print("     ", m[:6])
for pid in P:
    y = sorted(P[pid]["years"])[-1]
    ms = [m for m in P[pid]["monthly"] if m[0][:4] == y]
    tot = sum(m[1] * m[4] for m in ms)
    big = max(ms, key=lambda m: abs(m[1] * m[4]))
    print(f"   {pid} {y}: mean congestion {ymean(pid, y, 4):.2f}; without its largest month ({big[0]}) {ymean(pid, y, 4, (big[0],)):.2f}; that month carries {100 * big[1] * big[4] / tot:.0f} percent of the year's sum")
north_jan = ymean("spp:SPPNORTH_HUB", "2026", 4, ("2026-01",))
print(f"   SPP North 2026 without January: {north_jan:.2f} (page 2.22)")
M["spp_north_2026_without_jan"] = north_jan
# before and after 1 April 2026 (SPP's market expanded west that day, the curtailment audit's finding 7 cites it)
for pid in ("spp:SPPNORTH_HUB", "spp:SPPSOUTH_HUB"):
    pre = [m for m in P[pid]["monthly"] if "2025-04" <= m[0] <= "2025-11"]
    post = [m for m in P[pid]["monthly"] if "2026-04" <= m[0] <= "2026-11"]
    w = lambda ms, col: sum(m[1] * m[col] for m in ms) / sum(m[1] for m in ms)
    print(f"   {pid} April to November: 2025 congestion {w(pre, 4):.2f}, energy {w(pre, 3):.2f}; 2026 congestion {w(post, 4):.2f}, energy {w(post, 3):.2f}")

# 5. The places table: one ranking of both operators' places, each part measured from its own operator's reference
print("\n== 5. The places table, as it opens (2026), and the energy part across places of one operator")
y = "2026"
rows = sorted(((pid, P[pid]["by_year"][y]["congestion_mean"]) for pid in P if y in P[pid]["by_year"]), key=lambda t: -t[1])
for i, (pid, v) in enumerate(rows):
    print(f"   {i + 1}. {pid} {v}")
for op in F["places"]:
    for m0 in ("2025-07", "2026-01"):
        e = [next((m[3] for m in p["monthly"] if m[0] == m0), None) for p in F["places"][op]]
        print(f"   {op} {m0}: the energy part at each place {e}")

# 6. The windows: the newest month and the oldest year of the places, days held, partial months drawn as whole
print("\n== 6. Windows")
for op, O in F["constraints"].items():
    print(f"   {op}: constraints first {O['first']}, last {O['last']}; days held {O['days_held']}")
for pid in P:
    last = P[pid]["monthly"][-1]
    first = P[pid]["monthly"][0]
    print(f"   {pid}: first month {first[0]} {first[1]} hours; last month {last[0]} {last[1]} hours; years {P[pid]['years']}, hours a year {[P[pid]['by_year'][y]['hours'] for y in P[pid]['years']]}")

# 7. Hours that are neither up nor down (a congestion part of exactly zero)
print("\n== 7. Hours with a congestion part of zero")
for pid in P:
    for y, v in P[pid]["by_year"].items():
        z = v["hours"] - v["hours_congestion_up"] - v["hours_congestion_down"]
        if z > 0.05 * v["hours"]:
            print(f"   {pid} {y}: {z} of {v['hours']} hours at zero ({100 * z / v['hours']:.0f} percent)")

# 8. The share: mean over mean; the months whose share is drawn and those blank
print("\n== 8. The share rule")
for pid in P:
    ms = P[pid]["monthly"]
    blank = [m[0] for m in ms if m[7] is None]
    big = [(m[0], m[7]) for m in ms if m[7] is not None and abs(m[7]) >= 50]
    if blank or big:
        print(f"   {pid}: months with no share (mean LMP not above zero): {blank}; months with a share of 50 percent or more in size: {big}")
json.dump(M, open(os.path.join(HERE, "measures.json"), "w", encoding="utf-8"), indent=1, default=str)
