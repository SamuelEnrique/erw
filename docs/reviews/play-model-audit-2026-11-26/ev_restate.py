"""Session 10227 (play audit): "Should your family get an EV?" re-done from its method note's words, with none of the
site's code, and its price file checked against the warehouse's own tables (the main copy's warehouse/output, read only).

    python ev_restate.py <main output dir>      (writes retail.json and ev_restate.json beside this file)
"""
import json
import os
import sys

OUT_DIR = sys.argv[1]
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
EV = json.load(open(os.path.join(ROOT, "site", "data", "ev_prices.json"), encoding="utf-8"))
D = dict(miles=15000, mpg=27, kwh_mile=0.31, gas_car=28600, ev_car=33600, years=8, rate=5.0, credit=0.0)


def rows(name):
    with open(os.path.join(OUT_DIR, name), encoding="utf-8") as f:
        head = True
        for ln in f:
            if ln.startswith("#"):
                continue
            if head:
                head = False
                continue
            yield ln


# 1. every residential price series, and every regular gasoline series the price file names
want_gas = {EV["us"]["gas"]["entity"]} | {s["gas"]["entity"] for s in EV["states"] if s.get("gas")}
power, gas = {}, {}
for ln in rows("eia_retail_electricity_prices.csv"):
    e, v, ts, val = ln.split(",", 4)[:4]
    if e.endswith(":RES") and val:
        power.setdefault(e, {})[ts[:10]] = float(val)
for ln in rows("eia_regional_retail_fuel_prices.csv"):
    e, v, ts, val = ln.split(",", 4)[:4]
    if e in want_gas and val:
        gas.setdefault(e, {})[ts[:10]] = float(val)
json.dump({"power": power, "gas": gas}, open(os.path.join(HERE, "retail.json"), "w"))


def verdict(power_mwh, gas_gal, x=D, discount_payback=False):
    g100 = 100 / x["mpg"] * gas_gal
    e100 = 100 * x["kwh_mile"] * power_mwh / 1000
    gy, ey = g100 * x["miles"] / 100, e100 * x["miles"] / 100
    save = gy - ey
    extra = x["ev_car"] - x["gas_car"] - x["credit"]
    pv = sum(save / (1 + x["rate"] / 100) ** t for t in range(1, x["years"] + 1))
    if extra <= 0:
        pb = 0.0
    elif save <= 0:
        pb = None
    elif not discount_payback:
        pb = extra / save
    else:  # the year the discounted savings first reach the extra, interpolated within the year; None past 30 years
        acc, pb = 0.0, None
        for t in range(1, 31):
            add = save / (1 + x["rate"] / 100) ** t
            if acc + add >= extra:
                pb = t - 1 + (extra - acc) / add
                break
            acc += add
    return dict(g100=g100, e100=e100, gas_year=gy, ev_year=ey, save=save, extra=extra, payback=pb, npv=pv - extra)


places = [dict(code="US", **EV["us"])] + EV["states"]
out = {"check": [], "default": {}, "rules": {}}
bad = 0
for P in places:
    for kind, series in (("power", power), ("gas", gas)):
        c = P.get(kind)
        if not c:
            out["check"].append(f"{P['code']} {kind}: not held in the file")
            continue
        s = series.get(c["entity"], {})
        newest = max(s) if s else None
        ok = newest == c["ts"] and abs(s[newest] - c["value"]) < 1e-9 if newest else False
        if not ok:
            bad += 1
            out["check"].append(f"{P['code']} {kind}: file {c['ts']} {c['value']}; table newest {newest} {s.get(newest) if newest else None}")
    if not (P.get("power") and P.get("gas")):
        continue
    pw, gs = P["power"]["value"], P["gas"]["value"]
    v = verdict(pw, gs)
    out["default"][P["code"]] = v
    # one rule changed at a time
    ps = sorted(power[P["power"]["entity"]].items())
    last12 = [x for _, x in ps[-12:]]
    pw12 = sum(last12) / 12
    gser = sorted(gas[P["gas"]["entity"]].items())
    g52 = [x for _, x in gser[-52:]]
    gs52 = sum(g52) / len(g52)
    out["rules"][P["code"]] = {
        "power_newest": pw, "power_12m": pw12, "months_12m": [ps[-12][0], ps[-1][0]],
        "gas_newest": gs, "gas_52w": gs52, "weeks_52w": [gser[-len(g52)][0], gser[-1][0]],
        "power_12m_verdict": verdict(pw12, gs), "gas_52w_verdict": verdict(pw, gs52), "both_verdict": verdict(pw12, gs52),
        "discounted_payback": verdict(pw, gs, discount_payback=True)["payback"],
    }
json.dump(out, open(os.path.join(HERE, "ev_restate.json"), "w"), indent=1)
print("file against the tables, mismatches:", bad)
for x in out["check"][:20]:
    print("  ", x)
for code in ("US", "CA", "TX", "HI", "WA", "MA", "LA"):
    if code in out["default"]:
        v, r = out["default"][code], out["rules"][code]
        print(f"{code}: power {r['power_newest']} gas {r['gas_newest']} | gas/yr {v['gas_year']:.2f} ev/yr {v['ev_year']:.2f} save {v['save']:.2f} payback {v['payback']} npv {v['npv']:.2f}"
              f" | 12m power {r['power_12m']:.2f} ({r['months_12m']}) payback {r['power_12m_verdict']['payback']} npv {r['power_12m_verdict']['npv']:.2f}"
              f" | 52w gas {r['gas_52w']:.4f} payback {r['gas_52w_verdict']['payback']} npv {r['gas_52w_verdict']['npv']:.2f} | disc payback {r['discounted_payback']}")
