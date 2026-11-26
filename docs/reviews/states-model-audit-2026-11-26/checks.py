"""Session 10223 (states audit): three checks on the page's files.

    python checks.py <site/data/states dir>

1. The sign of EIA's net interstate trade in the state profile: supply less disposition with the trade added (the
   page's "in less out") and with it taken away ("out less in"); the rest should be EIA's direct use, small and not
   below zero.
2. DC's largest source if the months EIA withheld natural gas were gas, and with the source not held.
3. The United States' plants: Puerto Rico in the ten largest, the planned and the retiring.
"""
import json
import os
import sys

SD = sys.argv[1]
idx = json.load(open(os.path.join(SD, "index.json"), encoding="utf-8"))
F = {r["state"]: json.load(open(os.path.join(SD, r["file"]), encoding="utf-8")) for r in idx["states"]}

print("== 1. Net interstate trade: which sign balances the profile (newest year)")
plus_neg = minus_neg = 0
rows = []
for st, f in F.items():
    d = f["disposition"]
    if not d.get("years"):
        continue
    i = len(d["years"]) - 1
    v = {k: ((a[i] if a else None) or 0) for k, a in d["values"].items()}
    dis = v["full_service_providers"] + v["energy_only_providers"] + v["estimated_losses"] + v["total_international_exports"]
    base = v["total_net_generation"] + v["total_international_imports"]
    rest_in = base + v["net_interstate_trade"] - dis     # trade read as in less out
    rest_out = base - v["net_interstate_trade"] - dis    # trade read as out less in
    plus_neg += rest_in < 0
    minus_neg += rest_out < 0
    rows.append((st, d["years"][i], round(v["net_interstate_trade"]), round(100 * rest_in / dis, 1), round(100 * rest_out / dis, 1)))
print(f"  places: {len(rows)}; the rest (EIA's direct use) below zero when trade is read 'in less out': {plus_neg}; when read 'out less in': {minus_neg}")
print("  state, year, trade, rest as percent of disposition read in-less-out, read out-less-in:")
for r in sorted(rows, key=lambda r: r[0]):
    print("   ", r)
absrest_in = sorted(abs(r[3]) for r in rows)
absrest_out = sorted(abs(r[4]) for r in rows)
print(f"  median absolute rest: in-less-out {absrest_in[len(rows)//2]} percent; out-less-in {absrest_out[len(rows)//2]} percent")

print("\n== 2. DC's last twelve months")
g = F["DC"]["generation"]
last = g["months"][-12:]
tot = g["last12"]["total_mwh"]
gas = g["last12"]["mwh"]["natural_gas"]
ni = g["by_source"]["not_itemized"][-12:]
gas_m = g["by_source"]["natural_gas"][-12:]
withheld = sum(n for n, x in zip(ni, gas_m) if x is None and n is not None)
print(f"  total {tot:,.1f} MWh; natural gas over 9 months {gas:,.1f} ({100 * gas / tot:.2f} percent); not itemized in the 3 months gas is missing {withheld:,.1f}")
print(f"  if those three months' unitemized generation were gas: {100 * (gas + withheld) / tot:.2f} percent")
shares = {s: v for s, v in g["last12"]["share_pct"].items() if v is not None and s != "natural_gas"}
top2 = max(shares, key=shares.get)
print(f"  with natural gas not held, the largest source would be {top2} at {shares[top2]} percent; every share: {g['last12']['share_pct']}")

print("\n== 3. The United States' plants and Puerto Rico")
us = F["US"]["plants"]
print("  ten largest:", [(p["name"], p["county"], p["nameplate_mw"]) for p in us["largest"]])
pr = F["US"]["plants"]
print(f"  US capacity {us['capacity_total_mw']:,.1f} MW; plants {us['plants']}")

print("\n== 4. Use per person (the page prints none): retail sales over the 2025 county population")
for st in ("TX", "CA", "VA", "WY", "DC"):
    f = F[st]
    pop = f["serving"].get("population")
    s = f["retail"]["last12"]["by_sector"]["all"]["sales_mwh"]
    print(f"  {st}: {s / pop:.2f} MWh a person a year (sales {s:,.0f} MWh, people {pop:,})" if pop else f"  {st}: no population")
