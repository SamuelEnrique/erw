#!/usr/bin/env python3
"""ERW, What is on an electricity bill (/learn/bill): the replication a reader can run (session 7533, chain 304).

The page builds five residential bills from the utilities' tariffs and sets each against a wholesale price. Its rules
are stated in two places a reader can open: the rates, each with its tariff passage, in the page's own file
site/data/bill_rules.json, and the arithmetic in the method note (docs/methods/bill.md, "The arithmetic, line by
line"). The wholesale price is a row of the ERW table cost_of_power_monthly. This script reads those three and nothing
else, recomputes every figure the page prints for each case (the page as it opens, and the calculator for each case of
cases.json), and sets each beside the figure the page shows for the same case (page_figures.json, read off the page
drawn to HTML by site/scripts/bill-figures.mjs), with the difference and whether it is inside half of the page's last
shown digit. The numbers inside each line's words (the kWh in each period or inside the baseline, the rate) are
recomputed too.

It was written from the note and the rules file, not from the page's code (site/lib/bill.ts), and shares nothing with it.

    python replication/bill/replicate.py                     every figure, N of N
    python replication/bill/replicate.py --in-dir DIR        the wholesale rows from DIR/cost_of_power_monthly.csv
    python replication/bill/replicate.py --headline          the five headline figures of the do-file
    python replication/bill/replicate.py --texas-default     the Texas energy charges' derivation, from EIA's row
    python replication/bill/replicate.py --crosscheck        the figures set beside EIA's published ones

Exit 0 when every figure is inside its tolerance, 1 when one is not, 2 when the inputs cannot be read. Standard
library only. No request is made and nothing is written.
"""
import csv
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
RULES = os.path.join(ROOT, "site", "data", "bill_rules.json")
KEYS = ["CA", "SCE", "SDGE", "TX", "TXC"]


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def table_rows(path):
    """A warehouse-shaped CSV: '#' header lines, then a header row with entity, variable, ts_utc, value."""
    with open(path, encoding="utf-8") as f:
        r = csv.DictReader(line for line in f if not line.startswith("#"))
        return [{"entity": d["entity"], "variable": d["variable"], "month": d["ts_utc"][:7], "value": float(d["value"])} for d in r]


def wholesale(rows, entity):
    """The note, "The wholesale share": the load-weighted real-time price of the latest complete month (rt_hours equal
    to hours_in_month), else of the latest month held, said to be partial."""
    by = {}
    for r in rows:
        if r["entity"] == entity:
            by.setdefault(r["month"], {})[r["variable"]] = r["value"]
    months = sorted(m for m, v in by.items() if "rt_load_weighted" in v)
    full = [m for m in months if by[m].get("rt_hours") is not None and by[m].get("rt_hours") == by[m].get("hours_in_month")]
    if not months:
        return None
    m = full[-1] if full else months[-1]
    return {"price": by[m]["rt_load_weighted"], "month": m, "partial": m not in full}


def months_held(rows, entity):
    """Session 7547 (the read): the note, "The month field": every month with a load-weighted price for the bill's zone,
    newest first, each with its price and whether it is partial (rt_hours not equal to hours_in_month)."""
    by = {}
    for r in rows:
        if r["entity"] == entity:
            by.setdefault(r["month"], {})[r["variable"]] = r["value"]
    out = []
    for m in sorted((m for m, v in by.items() if "rt_load_weighted" in v), reverse=True):
        full = by[m].get("rt_hours") is not None and by[m].get("rt_hours") == by[m].get("hours_in_month")
        out.append({"price": by[m]["rt_load_weighted"], "month": m, "partial": not full})
    return out


# the note, "The power line": the line of each bill that charges for the power itself; SDG&E's tariff splits none out
POWER_LINE = {"CA": "Generation", "SCE": "Generation", "SDGE": None, "TX": "Energy charge (your retail electric provider)",
              "TXC": "Energy charge (your retail electric provider)"}


# --- the arithmetic, line by line (the note) ----------------------------------------------------------------------

def defaults(rules, key, typed):
    """A case's inputs: the bill's defaults in the rules file, with the typed values over them."""
    b = rules["bills"][key]
    d = b["defaults"]
    if key in ("TX", "TXC"):
        x = {"kwh": d["kwh"], "energyRate": b["energy_default"]["rate"]}
    elif key == "CA":
        x = {"kwh": d["kwh"], "peakShare": d["peak_share"], "season": d["season"], "territory": d["territory"], "tier": d["income_tier"], "days": d["days"], "climateCredit": d["climate_credit"]}
    else:
        x = {"kwh": d["kwh"], "peakShare": d["peak_share"], "superShare": d["super_share"], "weekdayShare": d.get("weekday_share", 5 / 7), "season": d["season"],
             "days": d["days"], "region": d.get("region"), "baselineKwh": d.get("baseline_kwh"), "climateCredit": d.get("climate_credit", False)}
    x.update(typed or {})
    return x


def bill_ca(rules, x):
    """PG&E E-TOU-C: each unbundled component; a time-of-use component pro-rates the peak share over all use (Sheet 1's
    rule); the Conservation Incentive Adjustment credits the baseline kWh and charges the rest; the baseline is the
    territory's daily quantity for the season times the days, never more than the use; then the Base Services Charge of
    the income tier per day, and the climate credit when chosen. Each line: (name, amount, numbers in its words)."""
    ca = rules["bills"]["CA"]
    si = 0 if x["season"] == "summer" else 1
    base = min(x["kwh"], ca["baseline_quantities"]["code_B"][x["territory"]][si] * x["days"])
    lines = []
    for c in ca["components"]:
        if c["basis"] == "per_kWh_tou":
            pk, off = c["rate"][x["season"]]
            lines.append((c["name"], x["kwh"] * (x["peakShare"] * pk + (1 - x["peakShare"]) * off), [x["kwh"], x["peakShare"] * 100, pk, off]))
        elif c["basis"] == "per_kWh_baseline_split":
            r = c["rate"]
            lines.append((c["name"], base * r["baseline"] + (x["kwh"] - base) * r["over"], [base, r["baseline"], x["kwh"] - base, r["over"]]))
        else:
            lines.append((c["name"], x["kwh"] * c["rate"], [x["kwh"], c["rate"]]))
    per_day = ca["base_services"]["tiers"][x["tier"]]
    lines.append((f"Base Services Charge (Income Tier {x['tier']})", x["days"] * per_day, [x["days"], per_day]))
    if x["climateCredit"]:
        lines.append((ca["climate_credit"]["name"], ca["climate_credit"]["rate"], []))
    return lines


def ca_by_totals(rules, x):
    """The same bill by Sheet 2's total rates: energy at the TOU totals, the baseline credit, the daily charge."""
    ca = rules["bills"]["CA"]
    s = ca["seasons"][x["season"]]
    si = 0 if x["season"] == "summer" else 1
    base = min(x["kwh"], ca["baseline_quantities"]["code_B"][x["territory"]][si] * x["days"])
    return (x["kwh"] * (x["peakShare"] * s["peak"] + (1 - x["peakShare"]) * s["offpeak"]) + base * ca["baseline_credit"]["rate"]
            + x["days"] * ca["base_services"]["tiers"][x["tier"]] + (ca["climate_credit"]["rate"] if x["climateCredit"] else 0))


def shares(kind, x):
    """Each period's share of the month: SCE in summer, 4 to 9 p.m. on-peak on weekdays and mid-peak on weekends, the
    rest off-peak (no super off-peak in summer); SCE in winter, 4 to 9 p.m. mid-peak, the super off-peak share, the rest
    off-peak; SDG&E, 4 to 9 p.m. on-peak, the super off-peak share, the rest off-peak. In the order the line prints."""
    p, s = x["peakShare"], x["superShare"]
    if kind == "sce":
        if x["season"] == "summer":
            return [("on", p * x["weekdayShare"]), ("mid", p * (1 - x["weekdayShare"])), ("off", 1 - p)]
        return [("mid", p), ("super", s), ("off", 1 - p - s)]
    return [("on", p), ("super", s), ("off", 1 - p - s)]


def bill_tou(rules, key, x):
    b = rules["bills"][key]
    sh = shares(b["kind"], x)
    lines = []
    for c in b["components"]:
        if c["basis"] == "per_kWh_period":
            r = c["rate"][x["season"]]
            nums = []
            for k, v in sh:
                nums += [round(x["kwh"] * v * 10) / 10, r[k]]
            lines.append((c["name"], sum(x["kwh"] * v * r[k] for k, v in sh), nums))
        else:
            lines.append((c["name"], x["kwh"] * c["rate"], [x["kwh"], c["rate"]]))
    bc = b["baseline_credit"]
    if b["kind"] == "sce":
        q = b["baseline_quantities"]["basic"][x["region"]][0 if x["season"] == "summer" else 1]
        base = min(x["kwh"], q * x["days"])
        nums = [base, float(x["region"]), bc["rate"]]
    else:
        base = min(x["kwh"], (x["baselineKwh"] or 0) * bc.get("share", 1))
        nums = [base, 130, x["baselineKwh"] or 0, bc["rate"]]
    lines.append(("Baseline credit", base * bc["rate"], nums))
    lines.append(("Base Services Charge", x["days"] * b["base_services"]["rate"], [x["days"], b["base_services"]["rate"]]))
    if x.get("climateCredit") and b.get("climate_credit"):
        lines.append(("California Climate Credit", b["climate_credit"]["rate"], []))
    return lines


def bill_tx(rules, key, x):
    """Texas: the retailer's energy charge (the reader's plan), the wires company's fixed monthly charges, its per-kWh
    charges and riders."""
    t = rules["bills"][key]
    lines = [("Energy charge (your retail electric provider)", x["kwh"] * x["energyRate"], [x["kwh"], x["energyRate"]])]
    lines += [(f["name"], f["rate"], []) for f in t["fixed"]]
    lines += [(p["name"], x["kwh"] * p["rate"], [x["kwh"], p["rate"]]) for p in t["per_kwh"]]
    return lines


def bill(rules, key, x):
    return bill_ca(rules, x) if key == "CA" else bill_tx(rules, key, x) if key in ("TX", "TXC") else bill_tou(rules, key, x)


def half_up(v, digits=0):
    """Rounding as the page prints (half away from zero), used only to name a figure the page rounds to a whole."""
    q = 10 ** digits
    return (int(abs(v) * q + 0.5) / q) * (1 if v >= 0 else -1)


# --- every figure ---------------------------------------------------------------------------------------------------

def expected(rules, key, typed, w):
    """Each figure the calculator prints for a case, by key, and each line's numbers."""
    x = defaults(rules, key, typed)
    lines = bill(rules, key, x)
    total = sum(a for _, a, _ in lines)
    out, nums = {}, {}
    for name, amount, n in lines:
        out[f"line|{name}"] = amount
        nums[f"line|{name}"] = n
    out["total"] = total
    if x["kwh"]:
        out["per_kwh"] = total / x["kwh"]
    if w is not None and total > 0:
        wusd = x["kwh"] * w["price"] / 1000
        out["bar|wholesale_usd"] = wusd
        out["bar|share_pct"] = half_up(max(0.0, min(1.0, wusd / total)) * 100)
        out["bar|kwh"] = x["kwh"]
        out["bar|price"] = w["price"]
        out["bar|month"] = w["month"]
        out["bar|rest_usd"] = total - wusd
        # session 7547: the power line under the bar
        if POWER_LINE[key] is None:
            out["power|none"] = "none"
        else:
            amount = sum(a for n, a, _ in lines if n == POWER_LINE[key])
            out["power|line"] = POWER_LINE[key]
            out["power|usd"] = amount
            out["power|share_pct"] = half_up(amount / total * 100)
            out["power|wholesale_usd"] = wusd
    return out, nums, x


def expected_months(rows, rules, key):
    """Session 7547: the options of the month field, by key (a partial month's key ends in '|partial')."""
    return {f"month|{m['month']}" + ("|partial" if m["partial"] else ""): m["price"] for m in months_held(rows, rules["bills"][key]["wholesale_entity"])}


def expected_page(rules, ws):
    out, nums = {}, {}
    for k in KEYS:
        e, _, x = expected(rules, k, {}, ws[k])
        out[f"card|{k}|total"] = e["total"]
        out[f"card|{k}|kwh"] = x["kwh"]
        w = ws[k]
        if w is not None:
            wusd = x["kwh"] * w["price"] / 1000
            out[f"card|{k}|wholesale_usd"] = wusd
            out[f"card|{k}|share_pct"] = wusd / e["total"] * 100
            out[f"card|{k}|price"] = w["price"]
            out[f"card|{k}|month"] = w["month"] + (", a partial month" if w["partial"] else "")
        if k in ("TX", "TXC"):
            out[f"card|{k}|energy_rate"] = rules["bills"][k]["energy_default"]["rate"]
    e, n, _ = expected(rules, "CA", {}, ws["CA"])
    for k, v in e.items():
        out[f"opens|{k}"] = v
    for k, v in n.items():
        nums[f"opens|{k}"] = v
    for t, q in rules["bills"]["CA"]["baseline_quantities"]["code_B"].items():
        out[f"opens|territory|{t}|summer"], out[f"opens|territory|{t}|winter"] = q
    for t, r in rules["bills"]["CA"]["base_services"]["tiers"].items():
        out[f"opens|tier|{t}"] = r
    return out, nums


def detail_numbers(text):
    return [float(m.replace(",", "")) for m in re.findall(r"-?\$?(\d[\d,]*(?:\.\d+)?)", text.replace("-$", "-"))]


def compare(case_id, figures, exp, nums, report):
    ok = bad = 0
    for f in figures:
        k = f["key"]
        if k not in exp:
            report.append(f"{case_id} | {k} | shown {f['shown']} | NOT RECOMPUTED")
            bad += 1
            continue
        e = exp[k]
        if f["value"] is None:
            report.append(f"{case_id} | {k} | shown \"{f['shown']}\" | recomputed {e} | NOT PRINTED")
            bad += 1
            continue
        if f["tolerance"] is None:
            good = str(e) == str(f["value"])
            diff = "" if good else f"expected {e}"
        else:
            d = f["value"] - e
            good = abs(d) <= f["tolerance"] + 1e-9
            diff = f"{d:+.6f}"
        ok, bad = (ok + 1, bad) if good else (ok, bad + 1)
        if not good:
            report.append(f"{case_id} | {k} | shown {f['shown']} | recomputed {e} | {diff}")
        if f.get("detail") and k in nums:
            want = sorted(nums[k])
            got = sorted(abs(v) for v in detail_numbers(f["detail"]))
            want_abs = sorted(abs(v) for v in want)
            same = len(got) == len(want_abs) and all(abs(a - b) <= 0.05 + 1e-9 for a, b in zip(got, want_abs))
            # the note: the tariffs print a rate to at most six decimals and the page a kWh to a tenth, so a number with
            # more digits in the words is floating-point noise (16.9 x 30 printed as 506.99999999999994)
            noisy = [m for m in re.findall(r"\d+\.(\d+)", f["detail"]) if len(m) > 6]
            same = same and not noisy
            ok, bad = (ok + 1, bad) if same else (ok, bad + 1)
            if not same:
                report.append(f"{case_id} | {k} words | shown \"{f['detail']}\" | recomputed numbers {want_abs}")
    for k in exp:
        if not any(f["key"] == k for f in figures):
            report.append(f"{case_id} | {k} | recomputed {exp[k]} | NOT SHOWN")
            bad += 1
    return ok, bad


def run(argv):
    in_dir = None
    if "--in-dir" in argv:
        in_dir = argv[argv.index("--in-dir") + 1]
    try:
        rules = load_json(RULES)
        figs = load_json(os.path.join(HERE, "page_figures.json"))
        cases = {c["id"]: c for c in load_json(os.path.join(HERE, "cases.json"))["cases"]}
        rows = table_rows(os.path.join(in_dir, "cost_of_power_monthly.csv") if in_dir else os.path.join(HERE, "source_rows.csv"))
    except (OSError, ValueError, KeyError) as e:
        print(f"cannot read the inputs: {e}")
        return 2
    ws = {k: wholesale(rows, rules["bills"][k]["wholesale_entity"]) for k in KEYS}

    if "--headline" in argv:
        for k in KEYS:
            e, _, _ = expected(rules, k, {}, ws[k])
            print(f"{rules['bills'][k]['name']}: the default bill (USD): {e['total']:.2f}")
        return 0
    if "--texas-default" in argv:
        return texas_default(rules)
    if "--crosscheck" in argv:
        return crosscheck(rules, ws)

    report, ok, bad = [], 0, 0
    for c in figs["cases"]:
        if c["id"] == "page":
            exp, nums = expected_page(rules, ws)
            exp.update({f"opens|{k}": v for k, v in expected_months(rows, rules, "CA").items()})
        else:
            src = cases[c["id"]]
            w = ws[src["bill"]]
            month = src["typed"].get("month")
            if month:
                # session 7547: the case sets the wholesale month; the field's options are every month held
                held = {m["month"]: m for m in months_held(rows, rules["bills"][src["bill"]]["wholesale_entity"])}
                w = held.get(month, w)
            exp, nums, _ = expected(rules, src["bill"], src["typed"], w)
            if month:
                exp.update(expected_months(rows, rules, src["bill"]))
        o, b = compare(c["id"], c["figures"], exp, nums, report)
        ok, bad = ok + o, bad + b
        print(f"{c['id']}: {o} of {o + b}")
    # the unbundled PG&E lines add up to Sheet 2's total rates, for every PG&E case
    for cid, src in cases.items():
        if src["bill"] == "CA":
            x = defaults(rules, "CA", src["typed"])
            a, t = sum(v for _, v, _ in bill_ca(rules, x)), ca_by_totals(rules, x)
            good = abs(a - t) < 0.005
            ok, bad = (ok + 1, bad) if good else (ok, bad + 1)
            if not good:
                report.append(f"{cid} | PG&E lines against Sheet 2's totals | {a:.4f} against {t:.4f}")
    for line in report:
        print(line)
    print(f"{ok} of {ok + bad} figures inside half the page's last shown digit (wholesale rows: {'--in-dir ' + in_dir if in_dir else 'source_rows.csv'}; rules {rules['version']})")
    return 0 if bad == 0 else 1


def texas_default(rules):
    """The rules file's derivation of each Texas default energy charge: EIA's July 2026 Texas residential average, less
    the wires company's delivery charges per kWh and its fixed charges spread over 600 kWh."""
    for k in ("TX", "TXC"):
        t = rules["bills"][k]
        eia = t["energy_default"]["eia_row"]["value"] / 1000
        per = sum(p["rate"] for p in t["per_kwh"])
        fixed = sum(f["rate"] for f in t["fixed"])
        kwh = t["defaults"]["kwh"]
        rate = eia - per - fixed / kwh
        print(f"{k}: {eia:.4f} - {per:.6f} - {fixed:.2f} / {kwh} = {rate:.6f}; the file holds {t['energy_default']['rate']}; "
              f"the default bill at {kwh} kWh is {kwh * t['energy_default']['rate'] + kwh * per + fixed:.2f} USD against EIA's {kwh * eia:.2f}")
    return 0


# EIA's published figures (cross-check, the note's section "The cross-check"). Each: publisher, document, date, figure.
EIA_2024_STATE = {  # Electric Sales, Revenue, and Average Price, 2024 data, Table 5A (released October 2025)
    "CA": {"kwh": 503, "cents": 31.97, "bill": 160.86},
    "TX": {"kwh": 1096, "cents": 14.94, "bill": 163.72},
}
EIA_2024_UTILITY = {  # the same release, Table 6 (utility bundled retail sales, residential): customers, MWh, thousand USD, cents
    "CA": ("Pacific Gas & Electric Co.", 1856780, 11138420, 4412805.0, 39.62),
    "SCE": ("Southern California Edison Co", 3219520, 19540551, 6336639.0, 32.43),
    "SDGE": ("San Diego Gas & Electric Co", 307982, 1347817, 588006.5, 43.63),
}
EIA_EPM_AUG_2026 = {"CA": 29.75, "TX": 15.91}  # Electric Power Monthly, Table 5.6.A, August 2026 (released October 23, 2026)


def crosscheck(rules, ws):
    print("ours | theirs | difference")
    for k in KEYS:
        e, _, x = expected(rules, k, {}, ws[k])
        cents = e["total"] / x["kwh"] * 100
        state = "CA" if k in ("CA", "SCE", "SDGE") else "TX"
        print(f"{k} default bill, all in: {cents:.2f} cents/kWh | EIA EPM Table 5.6.A, {state} residential, August 2026: {EIA_EPM_AUG_2026[state]:.2f} | {cents - EIA_EPM_AUG_2026[state]:+.2f}")
        if k in EIA_2024_UTILITY:
            name, cust, mwh, rev, c = EIA_2024_UTILITY[k]
            print(f"{k} default bill, all in: {cents:.2f} cents/kWh | EIA ESRAP 2024 Table 6, {name}, bundled residential: {c:.2f} ({rev * 1000 / (mwh * 1000) * 100:.2f} from its revenue over its sales); "
                  f"its average month {mwh * 1000 / cust / 12:.0f} kWh against the page's 600 | {cents - c:+.2f}")
    for k, st, avg in (("CA", "CA", "ca_eia_avg"), ("TX", "TX", "tx_eia_avg")):
        x = defaults(rules, k, {"kwh": EIA_2024_STATE[st]["kwh"]})
        total = sum(a for _, a, _ in bill(rules, k, x))
        print(f"{k} bill at EIA's 2024 {st} average month ({x['kwh']} kWh): {total:.2f} USD | EIA ESRAP 2024 Table 5A, {st} average residential bill: {EIA_2024_STATE[st]['bill']:.2f} | {total - EIA_2024_STATE[st]['bill']:+.2f} (case {avg})")
    return 0


if __name__ == "__main__":
    sys.exit(run(sys.argv[1:]))
