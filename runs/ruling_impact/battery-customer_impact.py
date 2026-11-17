#!/usr/bin/env python3
"""ERW, ruling impact for /battery/customer (session 7573, 17 November 2026).

The five lines marked "Changes a figure" under /battery/customer in docs/reviews/rulings-for-samuel-2026-11-17.md
(branch wip/7560-six-reads). The page reads no ERW table: its figures are arithmetic on nine typed numbers, so the
cases are replication/battery_customer/cases.json (published tariffs, each cited there) and the rules are
replication/battery_customer/replicate.py (imported).

    .venv/Scripts/python.exe runs/ruling_impact/battery-customer_impact.py
"""
import importlib.util
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
spec = importlib.util.spec_from_file_location("rep", os.path.join(ROOT, "replication", "battery_customer", "replicate.py"))
rep = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rep)
cases = rep.load("cases.json")
TARIFF = [c for c in cases["cases"] if str(c.get("kind", "")).startswith("tariff")]


def pct(a, b):
    return "n/a" if not a else f"{(b - a) / a * 100:+.1f}%"


def year_of(typed, **change):
    t = dict(typed)
    t.update({k: str(v) for k, v in change.items()})
    x, missing = rep.read_all(t)
    return None if missing else rep.saving(x)


# ---- line 1: the year as twelve of the month typed against the plan's seasons
print("== line 1: 'Saved a year', twelve of the month typed against Salt River Project E-32's own seasons")
by_season = 0.0
for cid, n in (("srp-e32-summer-peak", 2), ("srp-e32-summer", 4), ("srp-e32-winter", 6)):
    _c, _x, s = rep.case(cases, cid)
    by_season += n * s["month"]
for cid in ("srp-e32-summer-peak", "srp-e32-summer", "srp-e32-winter"):
    _c, _x, s = rep.case(cases, cid)
    print(f"{cid}: twelve of the month {s['year']:,.2f} against the year by seasons {by_season:,.2f}: {by_season - s['year']:+,.2f} ({pct(s['year'], by_season)})")
print("the other tariff cases print no season (Seattle, Austin) or one season only (SCE 2013 summer): the year does not move for them on the rates read")

# ---- line 2: energy moved capped by the building's use in the peak-rate hours
print("\n== line 2: energy moved each day capped at the peak kW times the peak hours (the most the building could take)")
for c in cases["cases"]:
    s = year_of(c["typed"])
    if s is None or not s["shifts"]:
        print(f"{c['id']}: {'no figure' if s is None else 'the battery does not shift energy (peak rate too low): nothing to cap'}")
        continue
    x, _ = rep.read_all(c["typed"])
    cap = x["peakKw"] * x["peakHours"]
    if s["out_kwh"] <= cap:
        print(f"{c['id']}: moves {s['out_kwh']:,.1f} kWh a day, the cap {cap:,.1f}: no change")
    else:
        eta = x["roundTrip"] / 100
        energy = (cap * x["peakRate"] - cap / eta * x["offPeakRate"]) * x["days"]
        print(f"{c['id']}: moves {s['out_kwh']:,.1f} kWh, cap {cap:,.1f}: energy {s['energy']:,.2f} -> {energy:,.2f} a month; year {s['year']:,.2f} -> {12 * (s['demand'] + energy):,.2f}")
ex = dict(next(c for c in cases["cases"] if c["id"] == "browser-proof")["typed"])
ex.update({"peakKw": "50"})
s = year_of(ex)
x, _ = rep.read_all(ex)
cap = x["peakKw"] * x["peakHours"]
eta = x["roundTrip"] / 100
energy = (cap * x["peakRate"] - cap / eta * x["offPeakRate"]) * x["days"]
print(f"the faults file's example (a 50 kW peak, the browser proof's 200 kW, 800 kWh battery and rates): energy {s['energy']:,.2f} -> {energy:,.2f} a month "
      f"({pct(s['energy'], energy)}); year {s['year']:,.2f} -> {12 * (s['demand'] + energy):,.2f} ({pct(s['year'], 12 * (s['demand'] + energy))})")

# ---- line 3: the starting value of the peak's length, 2 hours
print("\n== line 3: 'How long your peak lasts' at its starting 2 hours against 4, 5 and 6 (the tariffs' peak-rate windows)")
for c in TARIFF:
    base = year_of(c["typed"], peakHours=2)
    parts = [f"2 h {base['year']:,.0f}"]
    for h in (4, 5, 6):
        s = year_of(c["typed"], peakHours=h)
        parts.append(f"{h} h {s['year']:,.0f} ({pct(base['year'], s['year'])})")
    print(f"{c['id']} (typed {c['typed']['peakHours']} h): year " + "; ".join(parts))

# ---- line 4: the peak shaving at NREL's 85 percent
print("\n== line 4: 'From shaving the peak' as an upper bound against NREL's about 85 percent (NREL/TP-5400-63162, January 2015)")
for c in TARIFF:
    _c, x, s = rep.case(cases, c["id"])
    d85 = 0.85 * s["demand"]
    y85 = 12 * (d85 + s["energy"])
    print(f"{c['id']}: from the peak {s['demand']:,.2f} -> {d85:,.2f} a month ({d85 - s['demand']:+,.2f}); year {s['year']:,.2f} -> {y85:,.2f} ({pct(s['year'], y85)})")

# ---- line 5: the energy rates' limit of USD 5 against USD 1 per kWh
print("\n== line 5: the rates' limit, USD 5 per kWh (default) against USD 1")
hi = max(max(float(c["typed"]["peakRate"]), float(c["typed"]["offPeakRate"])) for c in TARIFF)
print(f"the highest rate typed in the nine tariff cases: USD {hi} per kWh: no case is refused under a limit of USD 1")
for dc, days, name in ((5.36, 26, "Seattle City, 26 days"), (12.19, 26, "Seattle Downtown, 26 days"), (6.75, 22, "SRP summer peak, 22 days"), (15.35, 21, "Austin, 21 days")):
    t = {"peakKw": "247", "demandCharge": str(dc), "peakRate": "4.9", "offPeakRate": "2.5", "batteryKw": "55", "batteryKwh": "110", "peakHours": "2", "days": str(days), "roundTrip": "86"}
    s = year_of(t)
    print(f"the read's store (247 kW, 55 kW and 110 kWh), 4.9 and 2.5 typed for cents, demand charge {dc} ({name}): limit 5: USD {s['year']:,.0f} a year; limit 1: refused, no figure "
          f"(in dollars, 0.049 and 0.025: USD {year_of(t, peakRate=0.049, offPeakRate=0.025)['year']:,.0f})")
