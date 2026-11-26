#!/usr/bin/env python3
"""Session 10207 (chain 710, part D): an independent restatement of the severance calculator's figures, written from the
method note (docs/methods/severance.md, "How a figure is computed" and "Default prices") and the rules file alone, not
from the page's code. Decimal arithmetic throughout, so a cent is rounded half up on the exact figure.

    python restate.py <eia_fuel_spot_prices.csv> <severance_rules.json> <now ISO> <out.json>

Standard library only; reads two files, writes one."""
import csv
import json
import sys
from decimal import Decimal as D, ROUND_HALF_UP

csv_path, rules_path, now_iso, out_path = sys.argv[1:5]
rules = json.load(open(rules_path, encoding="utf-8"), parse_float=D)


def cents(x):
    return x.quantize(D("0.01"), rounding=ROUND_HALF_UP)


# ---- default prices: the note's "Default prices", the calculator
y, m = int(now_iso[:4]), int(now_iso[5:7])
m3 = m - 3
ys = y
while m3 < 1:
    m3 += 12
    ys -= 1
since = f"{ys:04d}-{m3:02d}-01T00:00:00Z"
rows = {}
with open(csv_path, encoding="utf-8") as f:
    body = (l for l in f if not l.startswith("#"))
    for r in csv.DictReader(body):
        if r["variable"] != "spot_price" or r["entity"] not in ("eia:wti_cushing", "eia:henry_hub"):
            continue
        if r["ts_utc"] >= since:
            rows.setdefault(r["entity"], []).append((r["ts_utc"], D(r["value"])))


def latest_complete(entity):
    xs = rows.get(entity, [])
    months = sorted({t[:7] for t, _ in xs})
    if len(months) < 2:
        return None
    mo = months[-2]  # complete once a later month is held
    vals = [v for t, v in xs if t.startswith(mo)]
    return {"month": mo, "n": len(vals), "mean": sum(vals) / len(vals), "value": cents(sum(vals) / len(vals))}


oil = latest_complete("eia:wti_cushing")
gas = latest_complete("eia:henry_hub")


# ---- the calculator: the note's steps 1 to 8
def figure(st, p, volume, price, variant=None, adval_pct=D(0), royalty=D(0), trucking=D(0), transport=D(0), option=None, credit=None):
    S = rules["states"][st]
    P = S["products"][p]
    vol, price = D(volume), D(price)
    gross = vol * price  # step 1
    taxable = gross  # step 2
    vd = S.get("value_deduction")
    if vd and p in vd["products"]:
        if vd.get("royalty"):
            taxable = gross - gross * royalty / 100 - vol * trucking
        else:
            taxable = gross - vol * transport
    taxable = max(D(0), taxable)
    lines = []
    for b in P["base"]:  # step 3
        r = b["rate"]
        if r == "variant":
            v = next((w for w in P["variants"] if w["id"] == variant), P["variants"][0])
            rate = v["rate"]
        elif r == "district":
            rate = adval_pct / 100
        elif r == "choice":
            rate = b["choices"][0]["rate"]
        else:
            rate = r
        tax = vol * rate if b["basis"] == "per_unit" else taxable * rate
        if "min_per_unit" in b:
            tax = max(tax, vol * b["min_per_unit"])
        lines.append((b["id"], rate, tax))
    base_total = sum(t for _, _, t in lines)  # step 4
    with_total = base_total
    if option:  # step 5: replaces the first base tax only
        o = next(q for q in P["options"] if q["id"] == option and q["group"] == "rate")
        first_rate, first_tax = lines[0][1], lines[0][2]
        k = o["kind"]
        if k == "rate":
            t = taxable * o["rate"]
            if "exempt_below_price" in o and vol > 0 and taxable / vol < o["exempt_below_price"]:
                t = D(0)
        elif k == "per_unit":
            t = vol * o["rate"]
        elif k == "rate_param":
            pr = o["param"]["default"]
            t = taxable * (o["rate"] * (1 - D(pr) / 100) if o["rate"] is not None else D(pr) / 100)
        elif k == "exempt_pct":
            t = first_tax * (1 - D(o["pct"]) / 100)
        elif k == "hcg_ratio":
            ratio = D(o["param"]["default"])
            t = taxable * max(D(0), first_rate - first_rate * ratio / 2)
        elif k == "credit_tier":
            t = first_tax * (1 - credit_pct(o) / 100)
        with_total = base_total - first_tax + t
    if credit:  # step 7
        o = next(q for q in P["options"] if q["id"] == credit and q["group"] == "credit")
        with_total = with_total * (1 - credit_pct(o) / 100)
    fees = {f["id"]: vol * f["per_unit"] for f in P["fees"]}  # step 8
    return {"gross": gross, "taxable": taxable, "baseTotal": base_total, "withTotal": with_total, "savings": base_total - with_total,
            "lines": {i: t for i, _, t in lines}, "fees": fees}


def credit_pct(o):
    """Step 6: the latest period the file lists (the calculator's default), the first bound whose floor it is over."""
    price = o["certified"]["prices"][0]["price"]
    for b in o["bounds"]:
        if b["above"] is None or price > b["above"]:
            return D(b["pct"])


out = {"price": {"oil": oil, "gas": gas}, "cases": {}}
for st, S in rules["states"].items():
    for p, P in S["products"].items():
        price = gas["value"] if p == "gas" else oil["value"]
        c = out["cases"]
        c[f"{st}|{p}|base"] = figure(st, p, 1000, price)
        for v in P.get("variants", []):
            c[f"{st}|{p}|variant={v['id']}"] = figure(st, p, 1000, price, variant=v["id"])
        for o in P["options"]:
            if o["group"] == "rate":
                c[f"{st}|{p}|opt={o['id']}"] = figure(st, p, 1000, price, option=o["id"])
            else:
                c[f"{st}|{p}|credit={o['id']}"] = figure(st, p, 1000, price, credit=o["id"])
        dist = next((b for b in P["base"] if b["rate"] == "district"), None)
        if dist:
            for d in dist["districts"]["list"]:
                c[f"{st}|{p}|district={d['label']}"] = figure(st, p, 1000, price, adval_pct=d["rate"] * 100)
        if st == "NM":
            c[f"{st}|{p}|jal_royalty12.5_truck1"] = figure(st, p, 1000, price, adval_pct=D("1.4863"), royalty=D("12.5"), trucking=D(1))
        if st == "LA" and p != "gas":
            c[f"{st}|{p}|transport2"] = figure(st, p, 1000, price, transport=D(2))


def plain(x):
    if isinstance(x, D):
        return str(x)
    if isinstance(x, dict):
        return {k: plain(v) for k, v in x.items()}
    return x


json.dump(plain(out), open(out_path, "w", encoding="utf-8"), indent=1)
print(f"oil {oil['month']} n={oil['n']} mean={oil['mean']:.6f} -> {oil['value']}; gas {gas['month']} n={gas['n']} mean={gas['mean']:.6f} -> {gas['value']}; cases {len(out['cases'])}")
