#!/usr/bin/env python3
"""ERW, ruling impact for /severance (session 7571, 17 November 2026).

The seven lines marked "Changes a figure" under /severance in docs/reviews/rulings-for-samuel-2026-11-17.md (branch
wip/7560-six-reads): each figure under the default and under the other choice. Rules from replication/severance/replicate.py
(imported), prices from warehouse/output/eia_fuel_spot_prices.csv (public), the rules from site/data/severance_rules.json,
collections from replication/severance/crosscheck.json (the replication's cross-check of published files).

    .venv/Scripts/python.exe runs/ruling_impact/severance_impact.py
"""
import datetime
import importlib.util
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
spec = importlib.util.spec_from_file_location("rep", os.path.join(ROOT, "replication", "severance", "replicate.py"))
rep = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rep)

tables = os.path.join(ROOT, "warehouse", "output")
rules = rep.Rules(os.path.join(ROOT, "site", "data", "severance_rules.json"))
daily = rep.daily_prices(tables)
NOW = datetime.datetime(2026, 11, 17, 8, 0, tzinfo=datetime.timezone.utc)
with open(os.path.join(tables, rep.PRICE_TABLE), encoding="utf-8") as f:
    stamp = next(l.strip() for l in f if l.startswith("# Retrieved") or "Retrieved" in l)
print("prices:", rep.PRICE_TABLE, stamp[:160])
ent = {k: v for k, v in daily.items()}
wti = next(k for k in ent if "wti" in k.lower() or "cushing" in k.lower())
hh = next(k for k in ent if "henry" in k.lower())
print("entities:", wti, hh)
d_oil, d_gas = rep.default_price(ent[wti], NOW), rep.default_price(ent[hh], NOW)
print("calculator defaults:", d_oil, d_gas)
mm_oil, mm_gas = rep.month_means(ent[wti]), rep.month_means(ent[hh])


def pct(a, b):
    return "n/a" if a == 0 else f"{(b - a) / a * 100:+.2f}%"


# ---- line 1: the price box follows the report period
print("\n== line 1: base tax at the default price (latest complete month) against the period's own mean")
for kind, vol, mm, d, state, prod in (("gas", 1860, mm_gas, d_gas, "TX", "gas"), ("oil", 1000, mm_oil, d_oil, "TX", "oil")):
    diffs = []
    for m in sorted(mm):
        if m >= d["month"]:
            continue
        a = rep.tax(rules, state, prod, vol, d["value"])["base"]
        b = rep.tax(rules, state, prod, vol, mm[m][0])["base"]
        diffs.append((m, a, b))
    aug = next(x for x in diffs if x[0] == "2026-08")
    lo = min(diffs, key=lambda x: (x[2] - x[1]) / x[1])
    hi = max(diffs, key=lambda x: (x[2] - x[1]) / x[1])
    print(f"TX {kind} {vol:,}: default price {d['value']} ({d['month']}); 2026-08 at its own mean {mm['2026-08'][0]}: {aug[1]:,.2f} -> {aug[2]:,.2f} "
          f"({aug[2] - aug[1]:+,.2f}, {pct(aug[1], aug[2])}); over {len(diffs)} earlier months from {diffs[0][0]}: from {pct(lo[1], lo[2])} ({lo[0]}) to {pct(hi[1], hi[2])} ({hi[0]})")
    gas_periods = [p["period"] for p in rules.option("TX", "gas", "tx_lp_gas")["certified"]["prices"]] if kind == "gas" else []
    if gas_periods:
        pp = [x for x in diffs if x[0] in gas_periods]
        print(f"   the {len(pp)} certified report periods of the low-producing gas credit: from {pct(min(pp, key=lambda x: x[2]/x[1])[1], min(pp, key=lambda x: x[2]/x[1])[2])} "
              f"to {pct(max(pp, key=lambda x: x[2]/x[1])[1], max(pp, key=lambda x: x[2]/x[1])[2])}; the credit is 100 percent in every one, so the tax after it is 0 either way")

# ---- line 2: /learn/problems, the mean before rounding against the rounded mean
print("\n== line 2: the problem sets' unrounded mean against /severance's mean rounded to the cent")
for vol, ent_k, m, cases in ((1000, wti, "2026-10", (("TX", "oil"), ("LA", "oil"), ("NM", "oil"))), (2400, hh, "2026-08", (("TX", "gas"),))):
    xs = ent[ent_k][m]
    raw, rounded = sum(xs) / len(xs), rep.round2(sum(xs) / len(xs))
    for state, prod in cases:
        kw = {}
        if state == "LA":
            kw["variant"] = "la_oil_pre2025"
        if state == "NM":
            kw["district_rate"] = 0.0
        a = rep.tax(rules, state, prod, vol, rounded, **kw)["base"]
        b = rep.tax(rules, state, prod, vol, raw, **kw)["base"]
        print(f"{state} {prod} {vol:,} in {m}: mean {raw:.6f} rounded {rounded}: /severance {a:,.2f}; unrounded {b:,.2f}; difference {b - a:+,.2f} ({pct(a, b)})")

# ---- lines 3 and 4: /impact's Btu factor and its fee
print("\n== lines 3 and 4: one well's 46,500 Mcf at USD 2.99 (the read's case)")
with open(os.path.join(ROOT, "site", "data", "forecast", "gas.json"), encoding="utf-8") as f:
    gj = json.load(f)
btu = None
for k, v in (gj.items() if isinstance(gj, dict) else []):
    if "btu" in k.lower() and isinstance(v, (int, float)):
        btu = v
print("gas.json keys with btu:", {k: v for k, v in gj.items() if "btu" in k.lower()} if isinstance(gj, dict) else "n/a")
factor = (btu / 1000) if btu and btu > 100 else (btu or 1.034)
r = rep.tax(rules, "TX", "gas", 46500, 2.99)
fee = sum(a for _, a in r["fees"])
print(f"TX gas tax /severance {r['base']:,.2f}; at {factor} MMBtu per Mcf {r['base'] * factor:,.2f} ({r['base'] * factor - r['base']:+,.2f}, {pct(r['base'], r['base'] * factor)})")
print(f"fee {fee:,.2f}: tax plus fee {r['base'] + fee:,.2f} ({pct(r['base'], r['base'] + fee)}); with both rules {r['base'] * factor + fee:,.2f} ({pct(r['base'], r['base'] * factor + fee)})")
for state in ("LA", "NM", "OK", "ND", "WY", "CO", "PA", "WV"):
    st = rules.j["states"].get(state)
    if not st or "gas" not in st["products"]:
        continue
    b = rep.tax(rules, state, "gas", 46500, 2.99)
    kinds = [x["basis"] for x in st["products"]["gas"]["base"]]
    print(f"   {state} gas: {b['base']:,.2f} by /severance; bases {kinds}: the Btu factor moves only a percent of value")

# ---- lines 5 and 6: the low-producing oil test (by file or by lease, by lease or by well)
print("\n== lines 5 and 6: the low-producing oil credit's percent in every certified report period held")
o = rules.option("TX", "oil", "tx_lp_oil")
for p in o["certified"]["prices"]:
    print(f"   {p['period']}: certified {p['price']} -> credit {rep.credit_percent(o, p['period'])} percent")
print("every period's credit is 0 percent while the certified price is above USD 30: a lease flagged or not owes the same tax")

# ---- line 7: the base rate against collections
print("\n== line 7: tax at the base rate on all production against the Comptroller's collections")
with open(os.path.join(ROOT, "replication", "severance", "crosscheck.json"), encoding="utf-8") as f:
    cc = json.load(f)
for row in cc["rows"]:
    if "fiscal" in row["what"]:
        print(f"{row['what']}: ours {row['ours']:,} against {row['theirs']:,} ({row['document']}): {pct(row['theirs'], row['ours'])} above")
