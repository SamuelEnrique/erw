#!/usr/bin/env python3
"""Session 10207: one rule of the severance calculator changed at a time, each measured on the default case or the case
named, with the restatement's own arithmetic (restate.py, imported).

    python measures.py <eia_fuel_spot_prices.csv> <severance_rules.json> <crosscheck.json> <gas.json> <now ISO> <out.json>
"""
import json
import statistics
import sys
from decimal import Decimal as D

csv_path, rules_path, cross_path, gas_path, now_iso, out_path = sys.argv[1:7]
sys.argv = ["restate.py", csv_path, rules_path, now_iso, out_path.replace(".json", "_restate.json")]
import restate as R  # noqa: E402  (runs the restatement once, writing its own copy)

fig, cents, rules = R.figure, R.cents, R.rules
out = {}
oil, gas = R.oil["value"], R.gas["value"]


def pct(a, b):
    return float((a - b) / b * 100) if b else None


def tax(st, p, price, **k):
    return fig(st, p, 1000, price, **k)["baseTotal"]


base_oil = tax("TX", "oil", oil)
base_gas = tax("TX", "gas", gas)
out["default"] = {"oil_price": str(oil), "gas_price": str(gas), "tx_oil_tax": str(cents(base_oil)), "tx_gas_tax": str(cents(base_gas))}

# A, B: the month the default price stands on
import csv  # noqa: E402
daily = {}
with open(csv_path, encoding="utf-8") as f:
    for r in csv.DictReader(l for l in f if not l.startswith("#")):
        if r["variable"] == "spot_price" and r["entity"] in ("eia:wti_cushing", "eia:henry_hub"):
            daily.setdefault(r["entity"], []).append((r["ts_utc"][:10], D(r["value"])))
for e in daily:
    daily[e].sort()


def month_means(e):
    by = {}
    for d, v in daily[e]:
        by.setdefault(d[:7], []).append(v)
    return {m: sum(v) / len(v) for m, v in by.items()}


mm = {e: month_means(e) for e in daily}
last12 = [f"{y}-{m:02d}" for y, m in [(2025, 11), (2025, 12)] + [(2026, k) for k in range(1, 11)]]
for e, prod, st, base in (("eia:wti_cushing", "oil", "TX", base_oil), ("eia:henry_hub", "gas", "TX", base_gas)):
    m12 = cents(sum(mm[e][m] for m in last12) / 12)
    nov = [v for d, v in daily[e] if d.startswith("2026-11")]
    novm = cents(sum(nov) / len(nov))
    months = sorted(m for m in mm[e] if "2025-11" <= m <= "2026-10")
    vals = [float(mm[e][m]) for m in months]
    out[f"window|{prod}"] = {
        "twelve_month_mean": str(m12), "tax_at_twelve": str(cents(tax(st, prod, m12))), "change_pct": pct(tax(st, prod, m12), base),
        "november_partial_days": len(nov), "november_mean": str(novm), "tax_at_november": str(cents(tax(st, prod, novm))), "november_change_pct": pct(tax(st, prod, novm), base),
        "monthly_min": min(vals), "monthly_max": max(vals), "monthly_cv_pct": statistics.pstdev(vals) / statistics.mean(vals) * 100,
        "months": {m: round(float(mm[e][m]), 4) for m in months},
    }

# C: the mean rounded to the cent before the tax
unr = R.oil["mean"]
out["rounding|oil"] = {"unrounded_mean": str(unr), "tax_unrounded": str(cents(tax("TX", "oil", unr))), "tax_rounded": str(cents(base_oil))}

# D: an Mcf as 1.034 MMBtu (EIA's heat content, the rule /impact uses)
heat = D(str(json.load(open(gas_path, encoding="utf-8"))["btu_per_cf"])) / 1000
for st in ("TX", "NM", "LA"):
    a, b = tax(st, "gas", gas), tax(st, "gas", gas * heat)
    out[f"heat|{st}"] = {"tax_1to1": str(cents(a)), "tax_at_1034": str(cents(b)), "change_pct": pct(b, a)}

# E: Louisiana's completion date
a, b = tax("LA", "oil", oil, variant="la_oil_pre2025"), tax("LA", "oil", oil, variant="la_oil_post2025")
out["la_completion"] = {"before": str(cents(a)), "on_or_after": str(cents(b)), "change_pct": pct(b, a)}

# F: Louisiana's transport deduction on condensate (the statute: "gross value"), USD 2 a barrel, 1,000 bbl
a, b = tax("LA", "condensate", oil), tax("LA", "condensate", oil, transport=D(2))
out["la_condensate_transport"] = {"no_deduction": str(cents(a)), "with_2_per_bbl": str(cents(b)), "change": str(cents(b - a)), "change_pct": pct(b, a)}
# the page's own sample lease: FICTIONAL-LA-2, 40 bbl in 2026-07 and 38 in 2026-08, transport_per_bbl 1.5, the months' WTI means
s = D(0)
for m, v in (("2026-07", 40), ("2026-08", 38)):
    p = cents(mm["eia:wti_cushing"][m])
    s += fig("LA", "condensate", v, p)["baseTotal"] - fig("LA", "condensate", v, p, transport=D("1.5"))["baseTotal"]
out["la_condensate_transport|sample"] = {"deduction_effect_on_sample": str(cents(s))}

# G: New Mexico's district
for p in ("oil", "gas"):
    price = gas if p == "gas" else oil
    lst = next(b for b in rules["states"]["NM"]["products"][p]["base"] if b["rate"] == "district")["districts"]["list"]
    rates = sorted(d["rate"] for d in lst)
    med = rates[len(rates) // 2]
    none = tax("NM", p, price)
    out[f"nm_district|{p}"] = {
        "none": str(cents(none)), "min": str(cents(tax("NM", p, price, adval_pct=rates[0] * 100))),
        "median_rate_pct": str(med * 100), "median": str(cents(tax("NM", p, price, adval_pct=med * 100))),
        "max": str(cents(tax("NM", p, price, adval_pct=rates[-1] * 100))),
        "none_vs_median_pct": pct(none, tax("NM", p, price, adval_pct=med * 100)),
        "none_vs_max_pct": pct(none, tax("NM", p, price, adval_pct=rates[-1] * 100)),
    }

# H: New Mexico's oil conservation rate, 0.24 against 0.19 percent
out["nm_conservation|oil"] = {"at_0.24": str(cents(oil * 1000 * D("0.0024"))), "at_0.19": str(cents(oil * 1000 * D("0.0019"))), "change": str(cents(oil * 1000 * D("-0.0005")))}

# I: WTI Cushing against Texas's first purchase price (the cross-check's fiscal years)
cx = json.load(open(cross_path, encoding="utf-8"))["rows"]
get = lambda frag: next(r["ours"] for r in cx if frag in r["what"])  # noqa: E731
for fy in ("2025", "2026"):
    fpp = get(f"fiscal {fy}: 4.6 percent of EIA's production at the Texas first purchase price")
    wti = get(f"fiscal {fy}: 4.6 percent of EIA's production at the WTI Cushing")
    out[f"tx_fpp|fy{fy}"] = {"at_fpp": fpp, "at_wti": wti, "wti_over_fpp_pct": (wti - fpp) / fpp * 100}

# J: the certified period published since (September 2026, the faults file row 2)
for p, price in (("oil", D("48.59")), ("gas", D("1.23"))):
    o = next(q for q in rules["states"]["TX"]["products"][p]["options"] if q.get("certified"))
    tier = next(b["pct"] for b in o["bounds"] if b["above"] is None or price > b["above"])
    out[f"certified_sep2026|{p}"] = {"price": str(price), "credit_pct": tier, "credit_pct_aug": next(b["pct"] for b in o["bounds"] if b["above"] is None or D(str(o["certified"]["prices"][0]["price"])) > b["above"])}

# K: the price under which Texas oil's floor binds
out["tx_floor"] = {"binds_below_usd_per_bbl": str(D("0.046") / D("0.046"))}

# L: the effective rate, tax over gross, each state at the default prices
eff = {}
for st, S in rules["states"].items():
    for p in S["products"]:
        price = gas if p == "gas" else oil
        f0 = fig(st, p, 1000, price)
        eff[f"{st}|{p}"] = float(f0["baseTotal"] / f0["gross"] * 100)
        if st == "NM":
            lst = next(b for b in S["products"][p]["base"] if b["rate"] == "district")["districts"]["list"]
            med = sorted(d["rate"] for d in lst)[len(lst) // 2]
            f1 = fig(st, p, 1000, price, adval_pct=med * 100)
            eff[f"{st}|{p}|median district"] = float(f1["baseTotal"] / f1["gross"] * 100)
out["effective_rate_pct"] = eff
# Louisiana's gas tax is per Mcf: its share of value at the twelve months' lowest and highest Henry Hub means
hhv = out["window|gas"]["months"]
out["la_gas_share_of_value_pct"] = {m: float(D("0.1514") / D(str(v)) * 100) for m, v in hhv.items()}

# M: a federal lease's one-eighth royalty in New Mexico
a, b = tax("NM", "oil", oil), tax("NM", "oil", oil, royalty=D("12.5"))
out["nm_royalty12.5|oil"] = {"none": str(cents(a)), "royalty": str(cents(b)), "change_pct": pct(b, a)}

json.dump(out, open(out_path, "w", encoding="utf-8"), indent=1, default=str)
for k, v in out.items():
    print(k, json.dumps(v, default=str)[:400])
