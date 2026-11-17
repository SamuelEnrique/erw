#!/usr/bin/env python3
"""ERW, ruling impact for /learn/bill (session 7581, 17 November 2026).

The eight lines marked "Changes a figure" under /learn/bill in docs/reviews/rulings-for-samuel-2026-11-17.md (branch
wip/7560-six-reads). The page's rules are site/data/bill_rules.json; the arithmetic is replication/bill/replicate.py
(imported); the wholesale rows are replication/bill/source_rows.csv (cost_of_power_monthly as the live set served it on
16 November 2026). Each other choice is put into a copy of the rules or the rows in memory.

    .venv/Scripts/python.exe runs/ruling_impact/bill_impact.py
"""
import calendar
import copy
import importlib.util
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
spec = importlib.util.spec_from_file_location("rep", os.path.join(ROOT, "replication", "bill", "replicate.py"))
rep = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rep)
R0 = rep.load_json(rep.RULES)
ROWS = rep.table_rows(os.path.join(ROOT, "replication", "bill", "source_rows.csv"))
WS = {k: rep.wholesale(ROWS, R0["bills"][k]["wholesale_entity"]) for k in rep.KEYS}


def card(rules, k, typed=None, w=None):
    e, _, x = rep.expected(rules, k, typed or {}, w if w is not None else WS[k])
    return e, x


def pct(a, b):
    return "n/a" if not a else f"{(b - a) / a * 100:+.2f}%"


print("the cards as they open: " + "; ".join(f"{k} {card(R0, k)[0]['total']:,.2f} USD at {card(R0, k)[1]['kwh']} kWh, wholesale {WS[k]['month']} {WS[k]['price']:.2f} USD/MWh" for k in rep.KEYS))

# 1. CenterPoint's TC5 Refund at 0
print("\n== line 1: the rules re-read on a schedule: CenterPoint's TC5 Refund went to 0 on 13 November 2026")
R = copy.deepcopy(R0)
for p in R["bills"]["TXC"]["per_kwh"]:
    if p["name"] == "TC5 Refund":
        old = p["rate"]
        p["rate"] = 0.0
a, b = card(R0, "TXC")[0]["total"], card(R, "TXC")[0]["total"]
print(f"TC5 Refund {old} -> 0 USD/kWh: the CenterPoint card at 600 kWh {a:,.2f} -> {b:,.2f} ({b - a:+.2f}, {pct(a, b)}); the derived default energy charge would fall by the same per kWh, "
      f"{old:+.6f}, to keep the default bill at EIA's average: 0.0853 -> {0.0853 + old:.6f} (rounded {round(0.0853 + old, 4)})")

# 2. SDG&E's baseline by climate zone
print("\n== line 2: SDG&E with a 0 kWh baseline allowance (default) or a climate zone's allowance")
e, x = card(R0, "SDGE")
bc = R0["bills"]["SDGE"]["baseline_credit"]
print(f"the SDG&E card: {e['total']:,.2f} USD at {x['kwh']} kWh ({e['total'] / x['kwh'] * 100:.2f} cents a kWh; EIA's 2024 SDG&E residential average 43.63)")
for allow in (100, 200, 300):
    e2, _ = card(R0, "SDGE", {"baselineKwh": allow})
    print(f"   an allowance of {allow} kWh for the month (an example; the zones' allowances are not held): {e2['total']:,.2f} USD ({e2['total'] - e['total']:+,.2f}, {pct(e['total'], e2['total'])}), "
          f"{e2['total'] / x['kwh'] * 100:.2f} cents a kWh")
print(f"the credit is {bc['rate']} USD a kWh on use up to {bc['share'] * 100:.0f} percent of the allowance; the climate zones' allowances (SDG&E's baseline sheet) are not held: the default's own figure is not computed")

# 3. losses on the wires; Texas load zones
print("\n== line 3: the wholesale share on metered kWh (default) or with about 5 percent lost on the wires; Texas homes against their load zone")
for k in rep.KEYS:
    e, x = card(R0, k)
    w = WS[k]
    s0 = x["kwh"] * w["price"] / 1000 / e["total"] * 100
    s1 = x["kwh"] * 1.05 * w["price"] / 1000 / e["total"] * 100
    print(f"{k}: wholesale share {s0:.1f} -> {s1:.1f} percent ({s1 - s0:+.1f} points); wholesale dollars {x['kwh'] * w['price'] / 1000:,.2f} -> {x['kwh'] * 1.05 * w['price'] / 1000:,.2f}")
print("the load zones (Houston, North): ERCOT's zone prices are not in cost_of_power_monthly (data request row 209) nor held on this machine: not computed")

# 4. a month missing a single hour counted complete
print("\n== line 4: only whole months (default) or a month missing one hour counted whole")


def wholesale_relaxed(rows, entity):
    by = {}
    for r in rows:
        if r["entity"] == entity:
            by.setdefault(r["month"], {})[r["variable"]] = r["value"]
    months = sorted(m for m, v in by.items() if "rt_load_weighted" in v)
    full = [m for m in months if by[m].get("rt_hours") is not None and by[m].get("hours_in_month") is not None and by[m]["rt_hours"] >= by[m]["hours_in_month"] - 1]
    m = full[-1] if full else months[-1]
    return {"price": by[m]["rt_load_weighted"], "month": m, "partial": m not in full}


for k in rep.KEYS:
    w0, w1 = WS[k], wholesale_relaxed(ROWS, R0["bills"][k]["wholesale_entity"])
    e, x = card(R0, k)
    if w0["month"] == w1["month"]:
        print(f"{k}: the month stays {w0['month']}")
        continue
    s0, s1 = x["kwh"] * w0["price"] / 1000, x["kwh"] * w1["price"] / 1000
    print(f"{k}: month {w0['month']} -> {w1['month']}; price {w0['price']:.2f} -> {w1['price']:.2f} USD/MWh ({pct(w0['price'], w1['price'])}); wholesale {s0:,.2f} -> {s1:,.2f} USD; share {s0 / e['total'] * 100:.1f} -> {s1 / e['total'] * 100:.1f} percent")
print("the months held that miss exactly one hour, and what the card would have read while each was the newest:")
for ent in sorted({R0["bills"][k]["wholesale_entity"] for k in rep.KEYS}):
    by = {}
    for r in ROWS:
        if r["entity"] == ent:
            by.setdefault(r["month"], {})[r["variable"]] = r["value"]
    ms = sorted(m for m in by if "rt_load_weighted" in by[m])
    for i, m in enumerate(ms):
        v = by[m]
        if v.get("rt_hours") is not None and v.get("hours_in_month") is not None and v["rt_hours"] == v["hours_in_month"] - 1:
            prev = next((p for p in reversed(ms[:i]) if by[p].get("rt_hours") == by[p].get("hours_in_month")), None)
            if prev:
                a, b = by[prev]["rt_load_weighted"], v["rt_load_weighted"]
                print(f"   {ent} {m} ({v['rt_hours']:.0f} of {v['hours_in_month']:.0f} hours): the page fell back to {prev} at {a:.2f} USD/MWh; counted whole it reads {b:.2f} ({pct(a, b)}); "
                      f"600 kWh's wholesale {0.6 * a:.2f} -> {0.6 * b:.2f} USD")

# 5. SDG&E climate credit
print("\n== line 5: an SDG&E climate credit box, as SCE's and PG&E's")
for k in ("CA", "SCE"):
    cc = R0["bills"][k].get("climate_credit")
    print(f"{k}'s credit in the rules file: {cc['rate'] if cc else 'none'} USD")
print("SDG&E's credit amount is not in the rules file (its tariff sheet was not read): the box's figure is not computed; the card's total would fall by that amount in a credit month")

# 6. the Texas default energy charges from EIA's August 2026 average
print("\n== line 6: the Texas default energy charges from EIA's July 2026 average (default) or August's (0.0910 and 0.0856)")
for k, new in (("TX", 0.0910), ("TXC", 0.0856)):
    R = copy.deepcopy(R0)
    old = R["bills"][k]["energy_default"]["rate"]
    a = card(R0, k)[0]["total"]
    b = card(R0, k, {"energyRate": new})[0]["total"]
    print(f"{k}: {old} -> {new} USD/kWh: the card at 600 kWh {a:,.2f} -> {b:,.2f} ({b - a:+.2f}, {pct(a, b)})")

# 7. rules keyed by effective date
print("\n== line 7: today's rates for any bill month (default) or the rates in force in the bill's month")
print("no tariff sheet in force before the read of 1 October 2026 is held: the January 2026 bill's figures are not computed")

# 8. the wholesale price weighted by the days a meter-read span covers
print("\n== line 8: one calendar month's price (default) or the read span's months weighted by their days (e.g. a read from the 16th to the 15th)")
for k in rep.KEYS:
    w = WS[k]
    ent = R0["bills"][k]["wholesale_entity"]
    by = {r["month"]: r["value"] for r in ROWS if r["entity"] == ent and r["variable"] == "rt_load_weighted"}
    m = w["month"]
    y, mo = int(m[:4]), int(m[5:7])
    nxt = f"{y + (mo == 12)}-{(mo % 12) + 1:02d}"
    if nxt not in by:
        prev = f"{y - (mo == 1)}-{((mo - 2) % 12) + 1:02d}"
        d1 = calendar.monthrange(int(prev[:4]), int(prev[5:7]))[1] - 15
        price = (by[prev] * d1 + by[m] * 15) / (d1 + 15)
        span = f"{prev}-16 to {m}-15"
    else:
        d1 = calendar.monthrange(y, mo)[1] - 15
        price = (by[m] * d1 + by[nxt] * 15) / (d1 + 15)
        span = f"{m}-16 to {nxt}-15"
    e, x = card(R0, k)
    print(f"{k}: {m} {w['price']:.2f} USD/MWh -> the span {span} {price:.2f} ({pct(w['price'], price)}); wholesale {x['kwh'] * w['price'] / 1000:,.2f} -> {x['kwh'] * price / 1000:,.2f} USD")
