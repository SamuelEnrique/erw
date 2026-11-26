#!/usr/bin/env python3
"""Session 10207: the page's own figures (lib.json, from lib_figures.mjs) beside the independent restatement
(restate.json, from restate.py), and the default view's printed words beside the restated figures.

    python compare.py <lib.json> <restate.json> <severance_rules.json>

Exit 0 when every figure agrees to the cent and to 1e-9 relative, 1 otherwise."""
import json
import sys
from decimal import Decimal as D, ROUND_HALF_UP

lib = json.load(open(sys.argv[1], encoding="utf-8"))
res = json.load(open(sys.argv[2], encoding="utf-8"))
rules = json.load(open(sys.argv[3], encoding="utf-8"))
bad = 0
n = 0
worst = (0.0, "")


def cents(x):
    return D(str(x)).quantize(D("0.01"), rounding=ROUND_HALF_UP)


def usd(x):
    return "${:,.2f}".format(cents(x))


def same(a, b, key):
    global bad, n, worst
    n += 1
    a, b = float(a), float(b)
    gap = abs(a - b)
    rel = gap / max(1.0, abs(b))
    if rel > worst[0]:
        worst = (rel, key)
    # the cent the page prints: JS rounds its float, the restatement rounds the exact decimal
    if rel > 1e-9 or usd(a) != usd(b):
        bad += 1
        print(f"DIFF {key}: page {a!r} restated {b!r}")


# 1. default prices
for k in ("oil", "gas"):
    p, r = lib["price"][k], res["price"][k]
    n += 1
    if not (p["month"] == r["month"] and p["n"] == r["n"] and abs(p["value"] - float(r["value"])) < 1e-12):
        bad += 1
        print(f"DIFF price {k}: page {p} restated {r}")
    print(f"default {k}: {r['month']}, {r['n']} days, mean {float(r['mean']):.6f}, rounded {r['value']} (page {p['value']})")

# 2. every case
keys = sorted(set(lib["cases"]) | set(res["cases"]))
for k in keys:
    if k not in lib["cases"] or k not in res["cases"]:
        bad += 1
        print(f"ONE SIDE {k}")
        continue
    a, b = lib["cases"][k], res["cases"][k]
    for f in ("gross", "taxable", "baseTotal", "withTotal", "savings"):
        same(a[f], b[f], f"{k}|{f}")
    for i in b["lines"]:
        same(a["lines"][i], b["lines"][i], f"{k}|line {i}")
    for i in b["fees"]:
        same(a["fees"][i], b["fees"][i], f"{k}|fee {i}")

# 3. the default view's printed figures, from the drawn page
text = lib["printed"]["page"]
d = res["cases"]["TX|oil|base"]
o = res["price"]["oil"]
want = [
    f"WTI Cushing, the mean of {o['n']} daily EIA spot prices in {o['month']}, ${o['value']} per barrel",
    f"Gross value {usd(d['gross'])}",
    f"Oil production tax, 4.6% {usd(d['lines']['tx_oil'])}",
    f"Tax at the base rate {usd(d['baseTotal'])}",
    f"Tax with the exemptions chosen {usd(d['withTotal'])}",
    f"Savings {usd(d['savings'])}",
    f"Oil Field Clean-Up Fee (a fee, not in the tax or the savings) {usd(d['fees']['tx_oil_fee'])}",
    f"Rules version {rules['version']}",
]
# the rule list: every base rate as a percent of value or dollars a unit, every fee, the latest certified prices
for st, S in rules["states"].items():
    for p, P in S["products"].items():
        for b in P["base"]:
            if isinstance(b["rate"], (int, float)):
                s = f"${b['rate']} per {P['unit']}" if b["basis"] == "per_unit" else f"{D(str(b['rate'])) * 100:f}".rstrip("0").rstrip(".") + "% of value"
                want.append(f"{p}, {b['name']}: {s}")
        for fe in P["fees"]:
            want.append(f"{p}, {fe['name']}: ${fe['per_unit']} per {P['unit']}")
        for op in P["options"]:
            if op.get("certified"):
                c0 = op["certified"]["prices"][0]
                want.append(f"Latest certified price: ${c0['price']:.2f} for {op['certified']['as_of']} (2005 dollars)")
for w in want:
    n += 1
    if w not in text:
        bad += 1
        print(f"NOT PRINTED: {w}")
    else:
        print(f"printed: {w}")
print(f"\n{n} compared, {bad} differ; the largest relative gap {worst[0]:.3g} ({worst[1]})")
sys.exit(1 if bad else 0)
