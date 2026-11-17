#!/usr/bin/env python3
"""ERW, ruling impact for /play/ev (session 7584, 17 November 2026).

The five lines marked "Changes a figure" under the EV game in docs/reviews/rulings-for-samuel-2026-11-17.md (branch
wip/7560-six-reads). The model is replication/ev_game/replicate.py of branch wip/7536-play-ev (copied unchanged to
runs/ruling_impact/ev_game/ and imported: compute, case_inputs); the page's prices are site/data/ev_prices.json (built
15 October 2026); the newest rows held are eia_regional_retail_fuel_prices and eia_retail_electricity_prices
(warehouse/output, retrieved 5 November 2026).

    .venv/Scripts/python.exe runs/ruling_impact/ev-game_impact.py
"""
import csv
import importlib.util
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
spec = importlib.util.spec_from_file_location("ev", os.path.join(ROOT, "runs", "ruling_impact", "ev_game", "replicate.py"))
ev = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ev)
PR = json.load(open(os.path.join(ROOT, "site", "data", "ev_prices.json"), encoding="utf-8"))
OUT = os.path.join(ROOT, "warehouse", "output")


def newest(table, entity):
    best = None
    with open(os.path.join(OUT, table + ".csv"), encoding="utf-8", newline="") as f:
        for r in csv.DictReader(l for l in f if not l.startswith("#")):
            if r["entity"] == entity and r["value"] and (best is None or r["ts_utc"] > best[0]):
                best = (r["ts_utc"][:10], float(r["value"]))
    return best


def show(label, x):
    r = ev.compute(x)
    pb = "at once" if r["payback"] == 0 else ("never" if r["payback"] is None else f"{r['payback']:.1f} years")
    return f"{label}: saved a year USD {r['save']:,.0f}, payback {pb}, net present value USD {r['npv']:,.0f}", r


def line(n, t):
    print(f"\n== line {n}: {t}")


base = ev.case_inputs({}, PR)["x"]
print(show(f"the US as it opens (gasoline {base['gas']} USD/gal of {PR['us']['gas']['ts']}, electricity {base['power']} USD/MWh of {PR['us']['power']['ts']})", base)[0])

line(1, "the price file as built on 15 October 2026 (default) or rebuilt daily from the newest rows")
g = newest("eia_regional_retail_fuel_prices", "eia:EMM_EPMR_PTE_NUS_DPG")
p = newest("eia_retail_electricity_prices", "eia:retail_price:US:RES")
for label, x in ((f"gasoline {g[1]} ({g[0]})", dict(base, gas=g[1])), (f"and electricity {p[1]} ({p[0]})", dict(base, gas=g[1], power=p[1])),
                 ("the rulings line's example, gasoline 3.995", dict(base, gas=3.995))):
    print(show(label, x)[0])
for code in ("CA", "TX", "NY"):
    st = ev.case_inputs({"code": code}, PR)["x"]
    pe = newest("eia_retail_electricity_prices", f"eia:retail_price:{code}:RES")
    print(show(f"{code} as it opens (power {st['power']}, gas {st['gas']})", st)[0] + " | " + show(f"newest power {pe[1]} ({pe[0]})", dict(st, power=pe[1]))[0])

line(2, "home electricity at the state's average residential price (default) or a time-of-use rate (PG&E E-TOU-C off-peak)")
ca = ev.case_inputs({"code": "CA"}, PR)["x"]
print(show(f"California as it opens ({ca['power']} USD/MWh, EIA's average)", ca)[0])
for c in (367.57, 399.40):
    print(show(f"PG&E E-TOU-C off-peak {c / 10:.3f} cents", dict(ca, power=c))[0])

line(3, "the car prices of the 2025 models (default, 'to confirm') or the 2026 models'")
d = ev.case_inputs({}, PR)["x"]
a = ev.compute(d)
b = ev.compute(dict(d, evCar=d["evCar"] + 1000))
print(f"the 2026 prices are not held: not computed. Each USD 1,000 on the EV's price moves the payback by {b['payback'] - a['payback']:+.2f} years and the net present value by USD {b['npv'] - a['npv']:+,.0f} (US defaults)")

line(4, "the efficiency and miles defaults as read on 15 October 2026 (default) or read again from fueleconomy.gov")
print("not computed: fueleconomy.gov refused the connection, so no newer figure is held; the defaults stand (27 mpg, 0.31 kWh a mile, 15,000 miles)")

line(5, "the electricity slider by 0.1 cent (default) or a box to three decimals (39.940 set as 39.9)")
r1 = ev.compute(dict(ca, power=399.40))
r2 = ev.compute(dict(ca, power=399.0))
print(f"California at 39.940 cents: payback {r1['payback']:.2f} years, net present value USD {r1['npv']:,.2f}; at 39.9: {r2['payback']:.2f} and {r2['npv']:,.2f}; "
      f"difference {r1['payback'] - r2['payback']:+.3f} years and USD {r1['npv'] - r2['npv']:+,.2f}")
