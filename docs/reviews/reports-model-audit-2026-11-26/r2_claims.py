"""Session 10232 (reports audit), r2: the choices and claims of the two draft reports, restated from the warehouse CSVs
(no import of the site's code): which month and hubs each section picks, and whether each sentence's claim holds.

    python runs/c10232/r2_claims.py <csv dir> <raw extract dir>
"""
import csv
import os
import statistics as st
import sys
from collections import defaultdict

CSV_DIR, EXTRACT_DIR = sys.argv[1], sys.argv[2]
OPEN = ["caiso:TH_SP15_GEN-APND", "ercot:HB_HUBAVG", "spp:SPPNORTH_HUB"]
ALL6 = OPEN + ["isone:.H.INTERNAL_HUB", "miso:INDIANA.HUB", "nyiso:N.Y.C."]
ERCOT = "ercot:HB_HUBAVG"


def read(name):
    with open(os.path.join(CSV_DIR, name + ".csv"), encoding="utf-8") as f:
        return list(csv.DictReader(ln for ln in f if not ln.startswith("#")))


M = defaultdict(dict)
for r in read("cost_of_power_monthly"):
    M[(r["entity"], r["ts_utc"][:10])][r["variable"]] = float(r["value"])


def hub_months(e, market):
    out = []
    for (ee, ts), m in sorted(M.items()):
        if ee == e and f"{market}_shape_premium" in m:
            out.append((ts, m[f"{market}_shape_premium"], m.get(f"{market}_hours"), m.get("hours_in_month"),
                        m.get(f"{market}_hours") == m.get("hours_in_month")))
    return out


print("== Shape premium: section 'Six ISOs' ==")
da_months = sorted({ts for (e, ts), m in M.items() if "da_shape_premium" in m}, reverse=True)
latest = next(ts for ts in da_months if all("da_shape_premium" in M.get((e, ts), {}) for e in OPEN))
print(f"latest day-ahead month every open hub holds: {latest}")
for e in OPEN:
    m = M[(e, latest)]
    print(f"  {e}: da premium {m['da_shape_premium']:.4f}, da_hours {m['da_hours']:.0f} of {m['hours_in_month']:.0f}")
neg = [e for e in OPEN if M[(e, latest)]["da_shape_premium"] <= 0]
print(f"  hubs with a premium at or below zero in that month: {neg} (the page says 'in every hub, the grid's own load paid more')")
complete_da = next(ts for ts in da_months if all(M.get((e, ts), {}).get("da_hours") == M.get((e, ts), {}).get("hours_in_month")
                                                 and "da_shape_premium" in M.get((e, ts), {}) for e in OPEN))
print(f"latest day-ahead month complete at every open hub: {complete_da}")
for e in OPEN:
    m = M[(e, complete_da)]
    print(f"  {e}: da premium {m['da_shape_premium']:.4f}, simple {m['da_simple_mean']:.4f}, pct {m['da_shape_premium'] / m['da_simple_mean'] * 100:.2f}")
# how often the 'latest month' rule lands on a partial month: every month of the table, as if it were the newest
part = 0
tot = 0
for ts in sorted(set(da_months)):
    if not all("da_shape_premium" in M.get((e, ts), {}) for e in OPEN):
        continue
    tot += 1
    if not all(M[(e, ts)]["da_hours"] == M[(e, ts)]["hours_in_month"] for e in OPEN):
        part += 1
print(f"months every open hub holds day-ahead: {tot}; of them partial at one hub or more: {part}")
# every month every open hub holds complete: the sign
signs = []
for ts in sorted(set(da_months)):
    if all(M.get((e, ts), {}).get("da_hours") == M.get((e, ts), {}).get("hours_in_month") and "da_shape_premium" in M.get((e, ts), {}) for e in OPEN):
        signs.append((ts, [round(M[(e, ts)]["da_shape_premium"], 2) for e in OPEN]))
nonpos = [s for s in signs if any(v <= 0 for v in s[1])]
print(f"complete day-ahead months at all three: {len(signs)}; months with a premium at or below zero at one hub or more: {len(nonpos)}: {nonpos}")
# with all six hubs (as the words were written, before the hold)
signs6 = []
for ts in sorted(set(da_months)):
    if all("da_shape_premium" in M.get((e, ts), {}) for e in ALL6):
        signs6.append((ts, {e.split(':')[0]: round(M[(e, ts)]["da_shape_premium"], 2) for e in ALL6 if M[(e, ts)]["da_shape_premium"] <= 0}))
print(f"months all six hubs hold day-ahead: {len(signs6)}; with a premium at or below zero somewhere: {[s for s in signs6 if s[1]]}")

print("\n== Shape premium: 'Eight years of ERCOT' ==")
em = [m for m in hub_months(ERCOT, "rt") if m[4]]
allm = hub_months(ERCOT, "rt")
print(f"complete real-time months {len(em)}, first {em[0][0]}, last {em[-1][0]}; months held {len(allm)}")
missing = [m[0] for m in allm if not m[4]]
print(f"months held but not complete (left out of the chart, which places bars by order, not by date): {missing}")
noprem = sorted(set(ts for (e, ts) in M if e == ERCOT) - set(m[0] for m in allm))
print(f"months with no real-time premium row: {noprem}")
rank = sorted(em, key=lambda m: -m[1])
print("largest twelve complete months:", [(m[0], round(m[1], 2)) for m in rank[:12]])
ex = [m for m in rank if m[0] != "2021-02-01"]
top10 = ex[:10]
summer = sum(1 for m in top10 if m[0][5:7] in ("07", "08", "09"))
print(f"away from Uri, of the ten largest months {summer} fall in July to September")
by_year = defaultdict(list)
for m in em:
    by_year[m[0][:4]].append(m)
for y in sorted(by_year):
    ms = by_year[y]
    big = max(ms, key=lambda m: m[1])
    print(f"  {y}: {len(ms)} complete months; largest {big[0][:7]} {big[1]:.2f}")
print("yearly USD per MW (complete years), with and without February 2021:")
for y in sorted(by_year):
    ms = by_year[y]
    if len(ms) != 12:
        continue
    usd = sum(m[1] * m[2] for m in ms)
    usd_x = sum(m[1] * m[2] for m in ms if m[0] != "2021-02-01")
    print(f"  {y}: {usd:,.2f}" + (f"; without February: {usd_x:,.2f} (February is {(usd - usd_x) / usd * 100:.1f} percent of the year)" if y == "2021" else ""))
for y in ("2025",):
    ms = by_year.get(y, [])
    print(f"  {y}: {len(ms)} complete months; sum over them {sum(m[1] * m[2] for m in ms):,.2f} (not a complete year: left out of the page's table)")

print("\n== Shape premium: day-ahead against real time, ERCOT, complete months of both ==")
da = {m[0]: m[1] for m in hub_months(ERCOT, "da") if m[4]}
rt = {m[0]: m[1] for m in em}
both = sorted(set(da) & set(rt))
d = [rt[t] - da[t] for t in both if t != "2021-02-01"]
print(f"months {len(both)}; real time less day-ahead, without February 2021: median {st.median(d):.2f}, mean {st.mean(d):.2f}, "
      f"largest {max(d):.2f}, smallest {min(d):.2f}; opposite signs in {sum(1 for t in both if (rt[t] > 0) != (da[t] > 0))} months")
print(f"February 2021: real time {rt.get('2021-02-01', float('nan')):.2f}, day-ahead {da.get('2021-02-01', float('nan')):.2f}")

print("\n== Shape premium: 'Where in the day' ==")
P = defaultdict(dict)
for r in read("cost_of_power_hourly_profile"):
    P[(r["entity"], r["ts_utc"][:10])][r["variable"]] = float(r["value"])
pm = max(ts for (e, ts) in P)
for e in OPEN:
    cells = {k: v for k, v in P[(e, pm)].items() if k.startswith("rt_mean_h")}
    lo = min(cells, key=cells.get)
    hi = max(cells, key=cells.get)
    days = P[(e, pm)].get("rt_days_h12")
    print(f"  {pm} {e}: cheapest {lo[-2:]}:00 {cells[lo]:.2f}, dearest {hi[-2:]}:00 {cells[hi]:.2f}, days {days}")
prev = sorted({ts for (e, ts) in P})[-2]
for e in OPEN:
    cells = {k: v for k, v in P[(e, prev)].items() if k.startswith("rt_mean_h")}
    lo = min(cells, key=cells.get)
    hi = max(cells, key=cells.get)
    print(f"  {prev} (the month before) {e}: cheapest {lo[-2:]}:00 {cells[lo]:.2f}, dearest {hi[-2:]}:00 {cells[hi]:.2f}, days {P[(e, prev)].get('rt_days_h12')}, ratio {cells[hi] / cells[lo]:.2f}")

print("\n== AI gigawatts: the table read as the page reads it ==")
A = defaultdict(dict)
for r in read("ai_power_regions"):
    A[r["entity"].split(":")[1]][r["variable"]] = float(r["value"])
REG = ["caiso", "ercot", "isone", "miso", "nyiso", "pjm", "spp"]
HELD = {"isone", "miso", "nyiso"}


def view(regs, label):
    print(f"-- {label}: {regs}")
    def by(v, asc=True):
        return sorted([r for r in regs if v in A[r]], key=lambda r: A[r][v] * (1 if asc else -1))
    cheap, clean, calm, fast, self_ = by("flat_1gw_cost_usd"), by("carbon_intensity_kg_mwh"), by("scarcity_hours_200"), by("lbnl_median_years_to_cod"), by("net_import_share_pct")
    c0, c1 = cheap[0], cheap[-1]
    cr = A[c1]["flat_1gw_cost_usd"] / A[c0]["flat_1gw_cost_usd"]
    k0, k1 = clean[0], clean[-1]
    kr = A[k1]["flat_1gw_co2_t"] / A[k0]["flat_1gw_co2_t"]
    print(f"   cost: cheapest {c0}, dearest {c1}, ratio {cr:.2f}, diff {A[c1]['flat_1gw_cost_usd'] - A[c0]['flat_1gw_cost_usd']:,.0f}")
    print(f"   carbon: cleanest {k0}, dirtiest {k1}, ratio {kr:.2f}")
    s0, s1 = calm[0], calm[-1]
    sr = A[s1]["scarcity_hours_200"] / A[s0]["scarcity_hours_200"]
    f0, f1 = fast[0], fast[-1]
    fr = A[f1]["lbnl_median_years_to_cod"] / A[f0]["lbnl_median_years_to_cod"]
    print(f"   ratio of the worst to the best region: cost {cr:.2f}, carbon {kr:.2f}, hours at or above 200 {sr:.2f} ({s1} {A[s1]['scarcity_hours_200']:.0f} / {s0} {A[s0]['scarcity_hours_200']:.0f}), years to connect {fr:.2f}"
          f"; the page says carbon's gap 'is still the largest of the five measures'")
    s1000 = sorted([r for r in regs if "scarcity_hours_1000" in A[r]], key=lambda r: -A[r]["scarcity_hours_1000"])
    print(f"   hours at or above 1,000: {[(r, A[r]['scarcity_hours_1000']) for r in s1000]} (the page names the first as 'had the most')")
    dalow = [r for r in regs if "flat_da_price_usd_mwh" in A[r] and A[r]["flat_da_price_usd_mwh"] < A[r]["flat_rt_price_usd_mwh"]]
    print(f"   regions where day-ahead ran below real time: {dalow or 'none'}")
    for r in regs:
        if "flat_da_price_usd_mwh" in A[r]:
            print(f"     {r}: day-ahead less real time {A[r]['flat_da_price_usd_mwh'] - A[r]['flat_rt_price_usd_mwh']:.2f} USD/MWh")
    half = lambda lst, r: r in lst and lst.index(r) < -(-len(lst) // 2)
    lists = [cheap, clean, calm, fast, self_]
    tally = sorted([(r, sum(half(l, r) for l in lists), sum(r in l for l in lists)) for r in REG], key=lambda t: (-t[1], t[0]))
    top = [t for t in tally if t[1] == tally[0][1]]
    print(f"   tally (region, better half on, of held): {tally}; regions at the top: {[t[0] for t in top]} (the page says the first is 'the most of any region')")
    print(f"   rt hours priced: {[(r, A[r].get('rt_hours_priced')) for r in regs if 'rt_hours_priced' in A[r]]} of 8,760")


view([r for r in REG if r not in HELD], "as a visitor with the token sees it today (ISO-NE, MISO, NYISO held)")
view(REG, "all seven, as the words were written (session 62)")

print("\n== AI gigawatts: CAISO's balance either side of 16 December 2025 (the page's own banner) ==")
path = os.path.join(EXTRACT_DIR, "ciso_hours.csv")
with open(path, encoding="utf-8") as f:
    rows = list(csv.DictReader(ln for ln in f if not ln.startswith("#")))
print(f"extract columns: {list(rows[0].keys())[:12]}")
parts = {"2025-09-01 to 2025-12-15": [0.0, 0.0], "2025-12-16 to 2026-08-31": [0.0, 0.0], "the year": [0.0, 0.0]}
for r in rows:
    ts = r["ts_utc"]
    if not ("2025-09-01" <= ts[:10] < "2026-09-01"):
        continue
    try:
        d, ng = float(r["demand_mwh"]), float(r["net_generation_mwh"])
    except (ValueError, KeyError):
        continue
    key = "2025-09-01 to 2025-12-15" if ts[:10] < "2025-12-16" else "2025-12-16 to 2026-08-31"
    for k in (key, "the year"):
        parts[k][0] += d
        parts[k][1] += ng
for k, (d, ng) in parts.items():
    print(f"  {k}: demand {d:,.0f} MWh, net generation {ng:,.0f}, balance share {(d - ng) / d * 100:.2f} percent")
