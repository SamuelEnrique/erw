# Session 10203: one rule of /cost-of-power changed at a time, the default case (ERCOT, LZ_NORTH, flat, real time,
# 100 MW, the page's last twelve months), each measured from files on this machine. Reuses restate.py's functions
# (the independent restatement), not the site's library. Read only; writes nothing but its printout.
#   python runs/c10203/measures.py <site dir> <main copy warehouse/output dir>
import bisect
import csv
import json
import math
import os
import statistics
import sys
from datetime import datetime, timedelta, timezone

sys.argv = [sys.argv[0], sys.argv[1], "ercot", "LZ_NORTH", "rt"] + sys.argv[2:]
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import restate as R  # noqa: E402

OUT = sys.argv[5]
SITE = sys.argv[1]
res = {}
years = R.load_years("ercot")
pay = [R.series(f, "LZ_NORTH", "rt") for f in years]
da = [R.series(f, "LZ_NORTH", "da") for f in years]
flatw = [R.flat_weights(p) for p in pay]
ms = R.months(years, pay, flatw)
base = R.way(ms)
B = base["per"]
res["base"] = dict(per=B, months=f"{base['first']} to {base['last']}", gpu_hour=R.finance(base)["gpuHour"], pv=R.finance(base)["pv"])
l12 = [r for r in ms if base["first"] <= r["m"] <= base["last"]]
res["l12_hours_held_of_due"] = [sum(r["held"] for r in l12), sum(r["due"] for r in l12)]

# 1. the hub beside it, and day-ahead (the page shows both)
hp = [R.series(f, "HB_NORTH", "rt") for f in years]
hm = [r for r in R.months(years, hp, [R.flat_weights(p) for p in hp]) if base["first"] <= r["m"] <= base["last"]]
res["m1_hub_HB_NORTH"] = R.span(hm)["flat"] - B
dm = R.months(years, da, [R.flat_weights(p) for p in da])
res["m2_day_ahead"] = R.span([r for r in dm if base["first"] <= r["m"] <= base["last"]])["per"] - B

# 3. months in the grid's prevailing (clock) time instead of standard time: the hour i of a standard-time year starts
# at UTC = 1 Jan 00:00 + 6 h + i; its clock month in America/Chicago (CDT from the second Sunday of March 02:00 to the
# first Sunday of November 02:00).


def second_sunday_march(y):
    d = datetime(y, 3, 8)
    return d + timedelta(days=(6 - d.weekday()) % 7)


def first_sunday_nov(y):
    d = datetime(y, 11, 1)
    return d + timedelta(days=(6 - d.weekday()) % 7)


def clock_month(y, i):
    std = datetime(y, 1, 1) + timedelta(hours=i)  # standard-time wall clock
    s, e = second_sunday_march(std.year) + timedelta(hours=2), first_sunday_nov(std.year) + timedelta(hours=1)
    wall = std + timedelta(hours=1) if s <= std < e else std
    return f"{wall.year}-{wall.month:02d}"


cm = {}
for k, f in enumerate(years):
    for i, v in enumerate(pay[k]):
        if v is None:
            continue
        m = clock_month(f["year"], i)
        a = cm.setdefault(m, [0.0, 0])
        a[0] += v
        a[1] += 1
mm = [m for m in sorted(cm) if base["first"] <= m <= base["last"]]
res["m3_clock_time_months"] = sum(cm[m][0] for m in mm) / sum(cm[m][1] for m in mm) - B

# 4. power per GPU at the datasheet's own 10.2 / 8 = 1.275 kW, and the overhead ratio at the hover's Google 1.09
f0 = R.finance(base)
f1 = R.finance(base, gpu=1.275)
f2 = R.finance(base, pue=1.09)
res["m4_gpu_1_275"] = dict(gpu_hour=f1["gpuHour"], change=f1["gpuHour"] / f0["gpuHour"] - 1, gpus_100mw=100 * f1["gpusPerMw"])
res["m5_pue_1_09"] = dict(gpu_hour=f2["gpuHour"], change=f2["gpuHour"] / f0["gpuHour"] - 1, gpus_100mw=100 * f2["gpusPerMw"])

# 6. dollars of two kinds: flat prices discounted at a nominal 9.6 percent; prices rising with inflation
for g in (2.0, 2.5):
    fg = R.finance(base, growth=g)
    res[f"m6_inflation_{g}"] = dict(pv_100mw=fg["pv"] * 100, pv_change=fg["pv"] / f0["pv"] - 1, level=fg["level"])
res["m6_pv_100mw_default"] = f0["pv"] * 100

# 7. the bad month by interpolated percentile (the 90th of 36 monthly prices) against nearest rank
done = [r for r in ms if r["complete"]]
to = base["last"]
fr = R.prev(to, 35)
pm = sorted(r["cost"] / r["energy"] for r in done if fr <= r["m"] <= to)
res["m7_bad_interpolated_p90"] = statistics.quantiles(pm, n=10, method="inclusive")[-1]
res["m7_bad_nearest_rank"] = base["bad"]["per"]


# --- tables of the main copy (read only) ---
def rows(name):
    with open(os.path.join(OUT, name), encoding="utf-8") as fh:
        lines = (l for l in fh if not l.startswith("#"))
        yield from csv.DictReader(lines)


def ts(s):
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


# 8. ERCOT's ancillary services, a load's share: the day-ahead plan's quantity times its clearing price, over ERCOT's
# load in the same hours (ercot_as_quantities holds 40 days)
qty = {}
for r in rows("ercot_as_quantities.csv"):
    qty[(r["entity"], r["ts_utc"])] = float(r["value"])
hours = sorted({t for (_, t) in qty})
hs = set(hours)
price = {}
for r in rows("ercot_as_prices.csv"):
    if r["variable"] == "mcpc_dam" and r["ts_utc"] in hs:
        price[(r["entity"], r["ts_utc"])] = float(r["value"])
load = {}
for r in rows("ercot_zone_load_hourly.csv"):
    if r["entity"] == "ercot:system" and r["ts_utc"] in hs:
        load[r["ts_utc"]] = float(r["value"])
cost = mwh = 0.0
n = 0
prods = sorted({e for (e, _) in qty})
for t in hours:
    if t not in load or any((p, t) not in price or (p, t) not in qty for p in prods):
        continue
    n += 1
    cost += sum(price[(p, t)] * qty[(p, t)] for p in prods)
    mwh += load[t]
res["m8_ancillary_40_days"] = dict(hours=n, first=hours[0], last=hours[-1], usd_per_mwh_load=cost / mwh if mwh else None, products=prods)
# the same over the page's twelve months: each hour's day-ahead clearing prices times the median plan quantity of the
# 40 days for that product and clock hour (an assumption: quantities vary by month), over that hour's load
medq = {}
for p in prods:
    for hh in range(24):
        v = [qty[(p, t)] for t in hours if (p, t) in qty and int(t[11:13]) == hh]
        medq[(p, hh)] = statistics.median(v)
lo, hi = "2025-11-01T06:00:00Z", "2026-11-01T06:00:00Z"
pr12 = {}
for r in rows("ercot_as_prices.csv"):
    if r["variable"] == "mcpc_dam" and lo <= r["ts_utc"] < hi and r["entity"] in prods:
        pr12[(r["entity"], r["ts_utc"])] = float(r["value"])
ld12 = {}
for r in rows("ercot_zone_load_hourly.csv"):
    if r["entity"] == "ercot:system" and lo <= r["ts_utc"] < hi:
        ld12[r["ts_utc"]] = float(r["value"])
c12 = m12 = 0.0
n12 = 0
for t, L in ld12.items():
    if all((p, t) in pr12 for p in prods):
        n12 += 1
        c12 += sum(pr12[(p, t)] * medq[(p, int(t[11:13]))] for p in prods)
        m12 += L
res["m8_ancillary_twelve_months_estimate"] = dict(hours=n12, usd_per_mwh_load=c12 / m12 if m12 else None)

# 9. a solar contract's shape: the page's contract is a share of the energy at a fixed price in every hour, the load's
# own shape. A solar PPA settled at the hub (the generator page's own file: ERCOT's fleet, HB_HUBAVG real time)
# delivers its MWh in the sun's hours. For a flat load contracting a share s of its energy from solar at strike c:
# the page's cost is (1 - s) K + s E c; settled financially at the hub it is K - sum (p_h - c) q_h, with sum q_h = s E.
# The gap, per MWh of the load, is s x (the flat load's mean hub price - solar's capture price at the hub).
sp, sw, fp, fn = 0.0, 0.0, 0.0, 0
with open(os.path.join(SITE, "public", "seller", "erw_2026_generator_hourly.csv"), encoding="utf-8") as fh:
    rd = csv.DictReader(l for l in fh if not l.startswith("#"))
    for r in rd:
        if r["in_last_twelve"] != "1":
            continue
        p = float(r["price_usd_mwh"])
        fp += p
        fn += 1
        q = float(r["solar_mwh"])
        if q == -99999:
            continue
        sp += p * q
        sw += q
res["m9_solar_shape"] = dict(window="2025-10 to 2026-09 (the generator file's twelve months)", flat_hub=fp / fn, solar_capture=sp / sw,
                             gap_per_mwh_contracted=fp / fn - sp / sw)

# 10. the load's own effect on price: a crude merit order from the twelve months, the median zone price by ERCOT load
# in 1 GW bins; an added load of D MW moves each hour's price from its bin's median to the median D MW higher. Rough:
# it ignores wind, sun and imports, which move the curve hour by hour.
ldh = {}
for r in rows("ercot_zone_load_hourly.csv"):
    if r["entity"] == "ercot:system" and lo <= r["ts_utc"] < hi:
        ldh[r["ts_utc"]] = float(r["value"])
pairs = []
start = datetime(2025, 1, 1, 6, tzinfo=timezone.utc)
for k, f in enumerate(years):
    if f["year"] not in (2025, 2026):
        continue
    y0 = datetime(f["year"], 1, 1, 6, tzinfo=timezone.utc)
    for i, v in enumerate(pay[k]):
        if v is None:
            continue
        t = (y0 + timedelta(hours=i)).strftime("%Y-%m-%dT%H:%M:%SZ")
        if t in ldh:
            pairs.append((ldh[t], v))
bins = {}
for L, p in pairs:
    bins.setdefault(int(L // 1000), []).append(p)
med = {b: statistics.median(v) for b, v in bins.items() if len(v) >= 20}


def curve(L):
    b = int(L // 1000)
    ks = sorted(med)
    if b in med:
        return med[b]
    j = bisect.bisect_left(ks, b)
    return med[ks[min(j, len(ks) - 1)]]


eff = {}
for D in (100, 1000, 5000, 10000):
    d = sum(curve(L + D) - curve(L) for L, _ in pairs) / len(pairs)
    eff[D] = d
res["m10_own_effect"] = dict(hours=len(pairs), mean_price_rise_usd_mwh=eff, mean_load_mw=sum(L for L, _ in pairs) / len(pairs))

# 11. ERCOT's mean demand in the page's 2026 file, for the size field's 10,000 MW
res["m11_demand_mean_mw_2026"] = years[-1].get("demand_mean_mw")
res["m11_peak_mw_2026"] = years[-1].get("peak_mw")
print(json.dumps(res, indent=1))
