"""Session 10220: the page's mean LMP of each hub, month by month, against the warehouse's own hub price tables (another
source path: iso_hub_prices_history and iso_dam_hub_prices, written by warehouse/connectors/iso_prices.py, not by the
congestion connector). And the day-ahead against the real-time hub spread (SP15 less NP15; SPP North real time less
day-ahead), which the page does not show. Streams the tables line by line, keeps monthly sums only (and the hours of
2025 for SP15 and NP15, one year). Read only.
usage: s4_lmp.py <main copy warehouse/output dir>"""
import csv
import datetime as dt
import json
import os
import sys
from collections import defaultdict
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT = sys.argv[1]
F = json.load(open(os.path.join(ROOT, "site", "data", "conditions", "congestion.json"), encoding="utf-8"))
TZ = {"spp": ZoneInfo("America/Chicago"), "caiso": ZoneInfo("America/Los_Angeles")}
WANT = {"caiso:TH_NP15_GEN-APND", "caiso:TH_SP15_GEN-APND", "caiso:TH_ZP26_GEN-APND", "spp:SPPNORTH_HUB", "spp:SPPSOUTH_HUB"}
sums = defaultdict(lambda: [0.0, 0])           # (table, entity, variable, local month) -> sum, count
hours = defaultdict(dict)                      # (entity, variable) -> {utc hour start: value}, 2025 local year only


def stream(name):
    with open(os.path.join(OUT, name), encoding="utf-8") as fh:
        for line in fh:
            if not line.startswith("#"):
                cols = next(csv.reader([line]))
                break
        ie, iv, it, ix = cols.index("entity"), cols.index("variable"), cols.index("ts_utc"), cols.index("value")
        for row in csv.reader(fh):
            e = row[ie]
            if e not in WANT:
                continue
            t = dt.datetime.fromisoformat(row[it].replace("Z", "+00:00"))
            loc = t.astimezone(TZ[e.split(":")[0]])
            v = float(row[ix])
            s = sums[(name, e, row[iv], loc.strftime("%Y-%m"))]
            s[0] += v
            s[1] += 1
            if loc.year == 2025 and e in ("caiso:TH_NP15_GEN-APND", "caiso:TH_SP15_GEN-APND", "spp:SPPNORTH_HUB"):
                hours[(e, row[iv])][t.replace(minute=0)] = hours[(e, row[iv])].get(t.replace(minute=0), 0.0) + v / (4 if "15m" in row[iv] else 1)


for name in ("iso_hub_prices_history.csv", "iso_dam_hub_prices.csv"):
    stream(name)

# 1. Monthly mean day-ahead LMP: the page file against the price tables, whole months only (the table's count equals
#    the page's hours for that month)
page = {}
for op in F["places"]:
    for p in F["places"][op]:
        for m in p["monthly"]:
            page[(p["id"], m[0])] = (m[1], m[2])
n = eq = 0
worst = []
for (name, e, var, mon), (s, c) in sorted(sums.items()):
    if var != "lmp_dam" or (e, mon) not in page:
        continue
    ph, pl = page[(e, mon)]
    if c != ph:
        continue
    n += 1
    mine = round(s / c, 2)
    eq += abs(mine - pl) <= 0.0051
    if abs(mine - pl) > 0.0051:
        worst.append((name, e, mon, pl, mine))
print(f"whole months compared (the table holds every hour the page does): {n}; the mean LMP equal to the cent: {eq}")
for w in worst[:20]:
    print("  differs", w)
print("months whose hour count differs between the page and the table (not compared above):")
for (name, e, var, mon), (s, c) in sorted(sums.items()):
    if var == "lmp_dam" and (e, mon) in page and c != page[(e, mon)][0]:
        print(f"   {name} {e} {mon}: table {c} hours mean {s / c:.2f}; page {page[(e, mon)][0]} hours mean {page[(e, mon)][1]}")
print("months by table:", {name: len({(e, mon) for (nm, e, var, mon) in sums if nm == name and var == 'lmp_dam' and (e, mon) in page}) for name in ("iso_hub_prices_history.csv", "iso_dam_hub_prices.csv")})

# 2. The SP15 less NP15 spread: day-ahead (the page's two congestion parts and loss parts give it) against real time
def monthly_mean(name, e, var, mon):
    s = sums.get((name, e, var, mon))
    return s[0] / s[1] if s and s[1] else None


print("\nSP15 less NP15, by year (means of the hours both hubs hold), day-ahead against real time, from iso_hub_prices_history:")
H = hours
for var_da, var_rt in [("lmp_dam", "lmp_rtm_15m_mean")]:
    sp_da, np_da = H[("caiso:TH_SP15_GEN-APND", var_da)], H[("caiso:TH_NP15_GEN-APND", var_da)]
    sp_rt, np_rt = H[("caiso:TH_SP15_GEN-APND", var_rt)], H[("caiso:TH_NP15_GEN-APND", var_rt)]
    common = sorted(set(sp_da) & set(np_da) & set(sp_rt) & set(np_rt))
    d_da = [sp_da[t] - np_da[t] for t in common]
    d_rt = [sp_rt[t] - np_rt[t] for t in common]
    mean = lambda xs: sum(xs) / len(xs)
    sd = lambda xs: (sum((x - mean(xs)) ** 2 for x in xs) / (len(xs) - 1)) ** 0.5
    diff = [b - a for a, b in zip(d_da, d_rt)]
    print(f"  2025, {len(common)} hours: day-ahead spread mean {mean(d_da):.2f}, sd {sd(d_da):.2f}; real-time spread mean {mean(d_rt):.2f}, sd {sd(d_rt):.2f};"
          f" real time less day-ahead spread: mean {mean(diff):.2f}, mean absolute {mean([abs(x) for x in diff]):.2f}, hours where they differ by more than 10: {sum(abs(x) > 10 for x in diff)}")
    srt = sorted(d_rt)
    print(f"  2025 real-time spread: lowest {srt[0]:.2f}, highest {srt[-1]:.2f}; day-ahead lowest {min(d_da):.2f}, highest {max(d_da):.2f}")
    # how much of the year's real-time spread its 10 most extreme hours carry
    tot = sum(d_rt)
    ext = sorted(d_rt, key=abs, reverse=True)[:10]
    print(f"  2025 real-time spread summed {tot:.0f}; its 10 most extreme hours sum {sum(ext):.0f}")

# 3. The page's own day-ahead parts give the SP15 less NP15 spread: the congestion part's difference and the loss part's
P = {p["id"]: p for op in F["places"] for p in F["places"][op]}
print("\nThe page's day-ahead parts, SP15 less NP15 and SPP South less North, by year (hour-weighted means of the months):")
def yearpart(pid, y, col):
    ms = [m for m in P[pid]["monthly"] if m[0][:4] == y and m[col] is not None]
    h = sum(m[1] for m in ms)
    return sum(m[1] * m[col] for m in ms) / h if h else None
for a, b in [("caiso:TH_SP15_GEN-APND", "caiso:TH_NP15_GEN-APND"), ("spp:SPPSOUTH_HUB", "spp:SPPNORTH_HUB")]:
    for y in ("2023", "2024", "2025", "2026"):
        if y not in P[a]["by_year"]:
            continue
        dl = yearpart(a, y, 2) - yearpart(b, y, 2)
        dc = yearpart(a, y, 4) - yearpart(b, y, 4)
        dlo = yearpart(a, y, 5) - yearpart(b, y, 5)
        de = yearpart(a, y, 3) - yearpart(b, y, 3)
        print(f"  {a.split(':')[1]} less {b.split(':')[1]} {y}: LMP {dl:.2f} = energy {de:.2f} + congestion {dc:.2f} + loss {dlo:.2f}"
              + (f" + ghg {yearpart(a, y, 6) - yearpart(b, y, 6):.2f}" if a.startswith("caiso") else "") + f"; loss is {100 * abs(dlo) / (abs(dc) + abs(dlo)):.0f} percent of the two parts' sizes")

# 4. SPP North: real time less day-ahead by month (iso_hub_prices_history)
print("\nSPP North hub, real time less day-ahead, monthly means (iso_hub_prices_history):")
for mon in sorted({m for (nm, e, var, m) in sums if e == "spp:SPPNORTH_HUB" and nm == "iso_hub_prices_history.csv"}):
    da = monthly_mean("iso_hub_prices_history.csv", "spp:SPPNORTH_HUB", "lmp_dam", mon)
    rt = monthly_mean("iso_hub_prices_history.csv", "spp:SPPNORTH_HUB", "lmp_rtm_15m_mean", mon)
    if da is not None and rt is not None:
        print(f"  {mon}: day-ahead {da:.2f}, real time {rt:.2f}, real time less day-ahead {rt - da:+.2f}")
