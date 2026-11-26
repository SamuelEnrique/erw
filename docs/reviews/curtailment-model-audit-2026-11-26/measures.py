"""Session 10210 (curtailment audit): one rule changed at a time, each measured from the page's files, the restatement
of worth (worth_2025.json, worth_2026.json) and the main copy's tables (read only).

    python measures.py <site/data> <main copy warehouse/output> <out.json>
"""
import csv
import json
import os
import sys
from collections import defaultdict

data, src, outp = sys.argv[1], sys.argv[2], sys.argv[3]
J = lambda *p: json.load(open(os.path.join(data, *p), encoding="utf-8"))
prof, shares, worth, ercot = J("curtailment_profile.json"), J("curtailment", "shares.json"), J("curtailment", "worth.json"), J("curtailment", "ercot.json")
here = os.path.dirname(os.path.abspath(__file__))
W = {y: json.load(open(os.path.join(here, f"worth_{y}.json"), encoding="utf-8")) for y in ("2025", "2026")}
M = {}

# 1. which hub, which market: the year's value at each (worth.json, the year record or the months summed)
wc = worth["grids"]["caiso"]
for y in ("2025", "2026"):
    for hub in wc["hubs"]:
        for mk in ("rt", "da"):
            ms = [v for m, v in wc["hubs"][hub][mk]["months"].items() if m.startswith(y)]
            val, mwh = sum(v["value_usd"] for v in ms), sum(v["curtailed_mwh_priced"] for v in ms)
            M[f"1_value|{y}|{hub}|{mk}"] = {"usd": val, "usd_per_mwh": round(val / mwh, 2), "months": len(ms)}

# 2. the flat load: hours with any curtailment against hours with at least 1, 10, 100 MWh (SP15 real time)
for y, C in W.items():
    agg = defaultdict(float)
    for m, rec in C["months"].items():
        r = rec.get("caiso:TH_SP15_GEN-APND|rt")
        if not r or "missing" in r:
            continue
        agg["hours_priced"] += r["hours_priced"]
        agg["hours_any"] += r["hours_curtailed_priced"]
        agg["sum_any"] += (r["price_curtailed"] or 0) * r["hours_curtailed_priced"]
        agg["sum_all"] += r["price_all"] * r["hours_priced"]
        agg["mwh"] += r["curtailed_mwh_priced"]
        agg["usd"] += r["value_usd"]
        agg["mwh_under1h"] += 0
        for th in (1, 10, 100):
            agg[f"hours_ge{th}"] += r[f"hours_ge{th}"]
            agg[f"sum_ge{th}"] += (r[f"price_ge{th}"] or 0) * r[f"hours_ge{th}"]
        agg["mwh_in_hours_under10"] += r["mwh_in_hours_under10"]
    M[f"2_flat|{y}"] = {"months": len(C["months"]), "hours_priced": agg["hours_priced"], "hours_any": agg["hours_any"], "share_hours_any_pct": round(100 * agg["hours_any"] / agg["hours_priced"], 1),
                        "flat_any": round(agg["sum_any"] / agg["hours_any"], 2), "all": round(agg["sum_all"] / agg["hours_priced"], 2), "curtailment_weighted": round(agg["usd"] / agg["mwh"], 2),
                        **{f"hours_ge{th}": agg[f"hours_ge{th}"] for th in (1, 10, 100)}, **{f"flat_ge{th}": round(agg[f"sum_ge{th}"] / agg[f"hours_ge{th}"], 2) for th in (1, 10, 100)},
                        "hours_under1_mwh": agg["hours_any"] - agg["hours_ge1"], "mwh_in_hours_under10": round(agg["mwh_in_hours_under10"], 1)}

# 3. the battery rule on five-minute intervals against the same energy summed to the hour (2025, the last year of five-minute)
for D in ("2", "4", "8"):
    a = sum(r[f"absorb{D}_intervals"] for r in W["2025"]["months"].values())
    b = sum(r[f"absorb{D}_hourly"] for r in W["2025"]["months"].values())
    M[f"3_battery|2025|{D}h"] = {"intervals": round(a, 2), "hourly": round(b, 2), "pct": round(100 * (b - a) / a, 2)}

# 4. the share's output in 2026: Today's Outlook (the page) against the Daily Renewable Report (caiso_curtailment_daily)
gen = defaultdict(dict)
cur = defaultdict(float)
with open(os.path.join(src, "caiso_curtailment_daily.csv"), encoding="utf-8", newline="") as f:
    for r in csv.DictReader(line for line in f if not line.startswith("#")):
        if r["entity"] != "caiso:ISO" or not r["ts_utc"].startswith("2026"):
            continue
        d = r["ts_utc"][:10]
        if r["variable"] in ("solar_generation_mwh", "wind_generation_mwh"):
            gen[d][r["variable"]] = float(r["value"])
        elif r["variable"] in ("curtailed_solar_mwh", "curtailed_wind_mwh"):
            cur[d] += float(r["value"])
cs = shares["grids"]["caiso"]["months"]
rows4 = {}
for m in sorted(x for x in cs if x.startswith("2026")):
    days = [d for d in gen if d.startswith(m) and len(gen[d]) == 2]
    if not days:
        continue
    c = sum(cur[d] for d in days)
    o = sum(gen[d]["solar_generation_mwh"] + gen[d]["wind_generation_mwh"] for d in days)
    rows4[m] = {"days_with_report_output": len(days), "share_on_report_output": round(100 * c / (c + o), 2), "page_share": cs[m]["share_pct"]}
M["4_share_output_2026"] = rows4

# 5. "In 2026" is ten months: the twelve months to October 2026 instead
last12 = sorted(cs)[-12:]
c12, o12 = sum(cs[m]["curtailed_mwh"] for m in last12), sum(cs[m]["output_mwh"] for m in last12)
y26 = [m for m in cs if m.startswith("2026")]
c10, o10 = sum(cs[m]["curtailed_mwh"] for m in y26), sum(cs[m]["output_mwh"] for m in y26)
y25 = [m for m in cs if m.startswith("2025")]
c25, o25 = sum(cs[m]["curtailed_mwh"] for m in y25), sum(cs[m]["output_mwh"] for m in y25)
p12 = [m for m in prof["months"] if m in last12]
M["5_period"] = {"ten_months_2026": {"share": round(100 * c10 / (c10 + o10), 2), "curtailed": round(c10)}, "twelve_months_to_2026_10": {"months": [last12[0], last12[-1]], "share": round(100 * c12 / (c12 + o12), 2), "curtailed": round(c12),
                 "profile_curtailed": round(sum(prof["months"][m]["curtailed_solar_mwh"] + prof["months"][m]["curtailed_wind_mwh"] for m in p12))}, "year_2025": {"share": round(100 * c25 / (c25 + o25), 2), "curtailed": round(c25)},
                 "nov_dec_2025_curtailed": round(sum(cs[m]["curtailed_mwh"] for m in ("2025-11", "2025-12")))}

# 6. the hour of the day on standard time (Pacific standard): daylight saving months shifted back one hour
def peak(shift):
    tot = [0.0] * 24
    for m in [x for x in prof["months"] if x.startswith("2026")]:
        r = prof["months"][m]
        v = [r.get(f"curtailed_solar_mwh_h{h:02d}", 0) + r.get(f"curtailed_wind_mwh_h{h:02d}", 0) for h in range(24)]
        frac = shift.get(m[5:], 0.0)
        for h in range(24):
            tot[(h - 1) % 24] += frac * v[h]
            tot[h] += (1 - frac) * v[h]
    p = max(range(24), key=lambda h: tot[h])
    cen = sum((h + 0.5) * x for h, x in enumerate(tot)) / sum(tot)
    return p, round(cen, 2)
dst = {"03": 24 / 31, "04": 1, "05": 1, "06": 1, "07": 1, "08": 1, "09": 1, "10": 1}
M["6_clock"] = {"clock_peak_centroid": peak({}), "standard_peak_centroid": peak(dst)}

# 7. ERCOT: the share CAISO's way (below over below plus output) against the page's (below over the limit), and the
#    autumn hour of 1 November 2026 (wind's limit at the second 01:00 Central)
w = ercot["window"]
M["7_ercot"] = {k: {"page_share_of_limit": w[k]["share_pct"], "caiso_way": round(100 * w[k]["below_hsl_mwh"] / (w[k]["below_hsl_mwh"] + w[k]["generation_mwh"]), 2), "above_mwh": w[k].get("above_hsl_mwh")} for k in ("wind", "solar")}
b = w["both"]
M["7_ercot"]["both"] = {"page_share_of_limit": b["share_pct"], "caiso_way": round(100 * b["below_hsl_mwh"] / (b["below_hsl_mwh"] + b["generation_mwh"]), 2)}
h1 = [h for h in ercot["hours"] if h["ts"].startswith("2026-11-01T0")]
M["7_ercot"]["nov1_hours"] = h1
odd = [h for h in ercot["hours"] if h["ts"] == "2026-11-01T07:00:00Z"]
if odd:
    x = max(0, odd[0]["wind_hsl"] - odd[0]["wind_gen"])
    nb, nh = b["below_hsl_mwh"] - x, b["hsl_mwh"] - odd[0]["wind_hsl"]
    M["7_ercot"]["without_nov1_0700"] = {"wind_below_that_hour": round(x, 1), "window_share_without_it": round(100 * nb / nh, 2), "window_days": [ercot["first_day"], ercot["last_day"]], "in_window": "2026-11-01" in ercot["days"] and ercot["days"]["2026-11-01"]["whole"]}

# 8. SPP: the share's output (EIA-930 SWPP) month by month, to see whether it moves with SPP's western expansion (April 2026)
sp = shares["grids"]["spp"]["months"]
M["8_spp_output"] = {m: {"output_mwh": round(sp[m]["output_mwh"]), "curtailed_mwh": round(sp[m]["curtailed_mwh"]), "share": sp[m]["share_pct"]} for m in sorted(sp) if m >= "2025-01"}
# 9. the fleet: what share of everything the fleet charged falls in "the hours with any curtailment", month by month
fl = {}
for m, r in sorted(wc["battery"]["months"].items()):
    f = r.get("fleet")
    if f and f.get("fleet_charged_mwh"):
        fl[m] = {"in_curtailed_hours_pct": round(100 * f["fleet_charged_in_curtailed_hours_mwh"] / f["fleet_charged_mwh"], 1), "fleet_charged_mwh": f["fleet_charged_mwh"], "curtailed_mwh": f["curtailed_mwh_battery_days"]}
M["9_fleet_hours"] = fl
json.dump(M, open(outp, "w", encoding="utf-8"), indent=1)
for k, v in M.items():
    print(k, json.dumps(v)[:700])
