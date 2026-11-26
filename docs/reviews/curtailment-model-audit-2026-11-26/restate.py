"""Session 10210 (curtailment audit): every figure the default /curtailment view prints (CAISO, the newest year held,
a 4-hour battery), restated from the page's own files with none of the site's code, written from the method note
(docs/methods/curtailment.md) and the page's own words. Standard library only.

    python restate.py <site/data> <fixture.json> <out.json>

Each figure is written as the page writes it (whole numbers with commas, two decimals, "-29.0 million"), under the
key the page marks it with (data-n), so compare.py can set the two side by side. The two live reads (the daily and
monthly tables) come from fixture.json, the rows of the main copy's tables the draw script answered with.
"""
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_EVEN, ROUND_HALF_UP

data, fxp, outp = sys.argv[1], sys.argv[2], sys.argv[3]
J = lambda *p: json.load(open(os.path.join(data, *p), encoding="utf-8"))
prof, shares, free, worth = J("curtailment_profile.json"), J("curtailment", "shares.json"), J("curtailment", "free_energy.json"), J("curtailment", "worth.json")
fx = json.load(open(fxp, encoding="utf-8"))


def whole(v):
    # JavaScript Math.round: floor(x + 0.5), so a half goes toward +infinity
    return f"{int((Decimal(repr(v)) + Decimal('0.5')).to_integral_value(rounding='ROUND_FLOOR')):,}"


def two(v):
    return f"{Decimal(repr(v)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP):,.2f}" if v >= 0 else "-" + f"{Decimal(repr(-v)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP):,.2f}"


def usd(v):
    a, s = abs(v), "-" if v < 0 else ""
    if a >= 1e9:
        return f"{s}{a / 1e9:.2f} billion"
    if a >= 1e6:
        return f"{s}{a / 1e6:.1f} million"
    return s + whole(a)


R = {}
# ---- the period: the newest year of the profile (the reset line says "the latest year held") --------------------
year = sorted(prof["years"])[-1]
Y = prof["years"][year]
months_of_year = sorted(m for m in prof["months"] if m.startswith(year))
solar = sum(prof["months"][m]["curtailed_solar_mwh"] for m in months_of_year)
wind = sum(prof["months"][m]["curtailed_wind_mwh"] for m in months_of_year)
R["year"] = year
R["sum|solar"] = R["head|solar"] = R["reason|solar|all"] = whole(solar)
R["sum|wind"] = R["head|wind"] = R["reason|wind|all"] = whole(wind)
loc = {f: sum(prof["months"][m][f"curtailed_{f}_local_mwh"] for m in months_of_year) for f in ("solar", "wind")}
sysm = {f: sum(prof["months"][m][f"curtailed_{f}_system_mwh"] for m in months_of_year) for f in ("solar", "wind")}
uns = {f: sum(prof["months"][m].get(f"curtailed_{f}_unspecified_mwh", 0) for m in months_of_year) for f in ("solar", "wind")}
R["sum|local"] = R["head|local"] = whole(loc["solar"] + loc["wind"])
R["sum|system"] = R["head|system"] = whole(sysm["solar"] + sysm["wind"])
for f in ("solar", "wind"):
    R[f"reason|{f}|local"], R[f"reason|{f}|system"], R[f"reason|{f}|unspecified"] = whole(loc[f]), whole(sysm[f]), whole(uns[f])
    for k in ("econ", "ss", "oi"):
        R[f"cat|{f}|{k}"] = whole(sum(prof["months"][m].get(f"curtailed_{f}_{k}_mwh", 0) for m in months_of_year))
R["days_held"] = whole(sum(prof["months"][m]["days_held"] for m in months_of_year))
R["_days_in_period"] = sum(prof["months"][m]["days_in_month"] for m in months_of_year)
R["_calendar_days_of_year"] = 366 if int(year) % 4 == 0 else 365
# the hour of the day with the most, wind and solar, from the months' hours (Pacific clock)
hours = [sum(prof["months"][m].get(f"curtailed_solar_mwh_h{h:02d}", 0) + prof["months"][m].get(f"curtailed_wind_mwh_h{h:02d}", 0) for m in months_of_year) for h in range(24)]
peak = max(range(24), key=lambda h: (hours[h], -h))
R["_peak_hour"] = f"{peak:02d}:00"
R["head|peak_solar"] = whole(sum(prof["months"][m].get(f"curtailed_solar_mwh_h{peak:02d}", 0) for m in months_of_year))
R["head|peak_wind"] = whole(sum(prof["months"][m].get(f"curtailed_wind_mwh_h{peak:02d}", 0) for m in months_of_year))
second = sorted(range(24), key=lambda h: -hours[h])[1]
R["_peak_margin"] = {"peak": hours[peak], "second_hour": second, "second": hours[second], "pct": 100 * (hours[peak] - hours[second]) / hours[peak]}
# ---- the share: curtailed over curtailed plus output, the months of the year with a share --------------------------
cs = shares["grids"]["caiso"]["months"]
ym = [m for m in cs if m.startswith(year + "-")]
c = sum(cs[m]["curtailed_mwh"] for m in ym)
o = sum(cs[m]["output_mwh"] for m in ym)
R["sum|share"] = R["head|share"] = two(100 * c / (c + o))
R["_share_months"] = len(ym)
hi_m = max(sorted(cs), key=lambda m: cs[m]["share_pct"])
R["head|highest"] = R["share|highest"] = two(cs[hi_m]["share_pct"])
R["_highest_month"] = hi_m
last = sorted(cs)[-1]
R["share|last"] = two(cs[last]["share_pct"])
R["_last_month"] = last
R["share|months"] = whole(len(cs))
# ---- by month, from the monthly table (the 13 newest complete months the table holds) ----------------------------
mon = [r for r in fx["iso_curtailment_monthly"] if r["entity"] == "caiso:ISO"]
tm = sorted({r["ts_utc"][:7] for r in mon})[-13:]
for m in tm:
    R[f"share|{m}"] = two(cs[m]["share_pct"]) if m in cs else "not held"
    for v in ("curtailed_solar_mwh", "curtailed_wind_mwh"):
        x = [r["value"] for r in mon if r["variable"] == v and r["ts_utc"][:7] == m]
        R[f"_monthly|{m}|{v}"] = f"{x[0]:,.2f}" if x else ""
# ---- by day: the daily rows since 100 days before 2026-11-26 12:00 UTC, the last 90 days of them ------------------
since = (datetime(2026, 11, 26, 12, tzinfo=timezone.utc) - timedelta(days=100)).strftime("%Y-%m-%dT%H:%M:%SZ")
daily = [r for r in fx["caiso_curtailment_daily"] if r["ts_utc"] >= since]
days = sorted({r["ts_utc"] for r in daily})[-90:]
R["_days_count"] = len(days)
R["_days_span"] = [days[0][:10], days[-1][:10]]
for v in ("curtailed_solar_mwh", "curtailed_wind_mwh"):
    R[f"_days_total|{v}"] = f"{sum(r['value'] for r in daily if r['variable'] == v and r['ts_utc'] >= days[0]):,.2f}"
# ---- the batteries: the newest month of the year with them --------------------------------------------------------
bm = [m for m in months_of_year if "battery_days_held" in prof["months"][m]]
b = prof["months"][bm[-1]]
R["_battery_month"] = bm[-1]
R["sum|while"] = R["batt|while"] = two(b["curtailed_while_charging_share_pct"])
R["batt|curtailed"] = whole(b["curtailed_mwh_battery_days"])
R["batt|days"] = whole(b["battery_days_held"])
R["batt|charging"] = whole(b["battery_charging_mwh"])
# ---- where free energy is: CAISO's places, the last twelve months (two or more places hold them) -----------------
g = free["grids"]["caiso"]
held = lambda w: "basis" in w
for w in ("year", "month"):
    pl = sorted([l for l in g["locations"] if l["kind"] != "average" and held(l[w])], key=lambda l: (-l[w]["under5"], -l[w]["negative"], l["id"]))
    if w == "year":
        top = pl[0]
        R["top|year"] = R["head|cheap"] = R["heat|under5"] = whole(top["year"]["under5"])
        R["top|year|negative"] = R["heat|negative"] = whole(top["year"]["negative"])
        R["_top_place"] = top["id"]
        hs = sum(sum(r) for r in top["heat"]["under5"])
        R["_heat_sum_under5"] = hs
for l in g["locations"]:
    for w in ("month", "year"):
        if held(l[w]):
            R[f"loc|{l['id']}|{w}|under5"] = whole(l[w]["under5"])
            R[f"loc|{l['id']}|{w}|negative"] = whole(l[w]["negative"])
    if held(l["year"]):
        R[f"loc|{l['id']}|year|mean"] = two(l["year"]["mean"])
for w in ("year", "month"):
    x = g["gap"][w]
    means = {p: x["by_place"][p]["mean"] for p in x["places"]}
    lo, hi = min(means, key=means.get), max(means, key=means.get)
    R[f"gap|{w}"] = two(means[hi] - means[lo])
    R[f"gap|{w}|cheapest"], R[f"gap|{w}|dearest"] = two(means[lo]), two(means[hi])
tw, ca = free["compare"]["west_texas_houston"], free["compare"]["california_north_south"]
tk = "zone" if "basis" in tw.get("zone", {}).get("year", {}) else "hub"
R["pair|texas|west|under5"], R["pair|texas|west|negative"], R["pair|texas|houston|under5"] = whole(tw[tk]["year"]["a"]["under5"]), whole(tw[tk]["year"]["a"]["negative"]), whole(tw[tk]["year"]["b"]["under5"])
R["pair|texas|west|month"], R["pair|texas|houston|month"] = whole(tw[tk]["month"]["a"]["under5"]), whole(tw[tk]["month"]["b"]["under5"])
R["pair|california|south|under5"], R["pair|california|south|negative"], R["pair|california|north|under5"] = whole(ca["hub"]["year"]["b"]["under5"]), whole(ca["hub"]["year"]["b"]["negative"]), whole(ca["hub"]["year"]["a"]["under5"])
R["pair|california|south|month"], R["pair|california|north|month"] = whole(ca["hub"]["month"]["b"]["under5"]), whole(ca["hub"]["month"]["a"]["under5"])
# ---- what it is worth: the year at each hub and market, restated from the months -----------------------------------
wc = worth["grids"]["caiso"]
for hub, sides in wc["hubs"].items():
    for mk, side in sides.items():
        ms = [side["months"][m] for m in side["months"] if m.startswith(year + "-")]
        if not ms:
            continue
        mwh = sum(v["curtailed_mwh_priced"] for v in ms)
        val = sum(v["value_usd"] for v in ms)
        hp = sum(v["hours_priced"] for v in ms)
        hc = sum(v["hours_curtailed_priced"] for v in ms)
        k = f"worth|caiso|{hub}|{mk}"
        R[f"{k}|value"] = usd(val)
        R[f"{k}|per"] = two(round(val / mwh, 2))
        R[f"{k}|neg"] = two(round(sum(v["share_mwh_negative_pct"] * v["curtailed_mwh_priced"] for v in ms) / mwh, 2))
        R[f"{k}|under5"] = two(round(sum(v["share_mwh_under5_pct"] * v["curtailed_mwh_priced"] for v in ms) / mwh, 2))
        R[f"{k}|flat"] = two(round(sum(v["price_curtailed_hours_mean"] * v["hours_curtailed_priced"] for v in ms) / hc, 2))
        R[f"{k}|all"] = two(round(sum(v["price_all_hours_mean"] * v["hours_priced"] for v in ms) / hp, 2))
        if hub == wc["main_hub"] and mk == "rt":
            for f in ("value", "per", "neg", "under5", "flat", "all"):
                R[f"worth|{f}"] = R[f"{k}|{f}"]
            R["across|caiso|value"], R["across|caiso|per"] = R[f"{k}|value"], R[f"{k}|per"]
            R["worth|mwh"] = whole(mwh)
            R["worth|hours"] = whole(hc)
            R["_worth_hours_priced"] = hp
bat = wc["battery"]
bms = [m for m in bat["months"] if m.startswith(year + "-")]
days = sum(bat["months"][m]["days_held"] for m in bms)
R["bat|days"] = whole(days)
R["bat|curtailed"] = whole(sum(bat["months"][m]["curtailed_mwh"] for m in bms))
for d in ("2", "4", "8"):
    a = sum(bat["months"][m]["absorb_mwh_per_mw"][d] for m in bms)
    R[f"bat|{d}|per_mw"] = whole(a)
    fa = sum(bat["months"][m]["fleet"]["absorb_fleet_mwh"][d] for m in bms)
    fc = sum(bat["months"][m]["fleet"]["fleet_charged_in_curtailed_hours_mwh"] for m in bms)
    R[f"bat|{d}|absorb"], R[f"bat|{d}|fleet"], R[f"bat|{d}|share"] = whole(fa), whole(fc), two(round(100 * fa / fc, 2))
R["bat|per_mw"], R["bat|absorb"], R["bat|fleet"], R["bat|share"] = R["bat|4|per_mw"], R["bat|4|absorb"], R["bat|4|fleet"], R["bat|4|share"]
R["bat|fill"] = two(100 * sum(bat["months"][m]["absorb_mwh_per_mw"]["4"] for m in bms) / (4 * days))
R["across|caiso|share|4"] = R["bat|4|share"]
ew = worth["grids"]["ercot"]["hubs"][worth["grids"]["ercot"]["main_hub"]]["rt"]["window"]
R["across|ercot|value"], R["across|ercot|per"] = usd(ew["value_usd"]), two(ew["usd_per_mwh_curtailed"])
json.dump(R, open(outp, "w", encoding="utf-8"), indent=1)
print(len([k for k in R if not k.startswith("_")]), "figures restated;", year, "peak", R["_peak_hour"], R["_peak_margin"])
