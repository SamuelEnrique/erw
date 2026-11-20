"""Replication of the page "Energy use by industry" (/industry).

Energy Research Warehouse (ERW). Session 8012 (chain 505, part B1), 19 November 2026.

What it does. The page draws site/data/industry.json (contract: section 9 of docs/state/page_files_regions.md;
method: docs/methods/industry_page.md). This script reads the page as a reader's browser receives it, takes every
figure marked on it (each carries data-fig="<key>"), and computes each again from the file with its own arithmetic,
written from the method note and not from the page's code (site/lib/industry.ts): a month's figure, a year's twelve
months summed, an industry's share of the three-digit industries' sum, a percent change, a state's figures, and EIA's
projections. A figure the page writes as "not held" must have no figure in the file. Then two cross-checks set one EIA
publication beside another:

1. The industrial sector's total of the year, from the Monthly Energy Review's twelve months (Table 2.4), beside the
   State Energy Data System's total for the United States in the same year.
2. Electricity sold to industrial customers in the year, from Form EIA-861M's twelve months (MWh), beside the State
   Energy Data System's industrial electricity for the United States (TBtu), at 3,412 Btu per kWh.

    python replication/industry/replicate.py --base http://localhost:3000 [--query "year=2023&sa=OH"]

The page is in review: the script opens the internal view with INTERNAL_COSTS_TOKEN (read from the environment or
site/.env.local). Exit 0 when every figure is reproduced, 1 when one differs, 2 when the page cannot be read. It writes
figures.csv (every figure, the page's and the file's) and crosscheck.csv beside itself.
"""
import argparse
import csv
import html
import http.cookiejar
import json
import os
import re
import sys
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
FILE = os.path.join(ROOT, "site", "data", "industry.json")
MONTHLY = ["total", "end_use_total", "natural_gas", "petroleum", "electricity_retail_sales", "electrical_system_losses", "renewables", "coal"]
FUELS = ["total", "net_electricity", "natural_gas", "coal", "coke_and_breeze", "residual_fuel_oil", "distillate_fuel_oil", "hgl", "hydrogen", "other"]
SEDS = ["total", "natural_gas", "petroleum", "electricity", "electrical_system_losses", "renewables", "coal"]
ELEC = ["elec_net_demand", "elec_purchases", "elec_transfers_in", "elec_onsite_generation", "gen_cogeneration", "gen_renewable", "gen_other", "elec_sales_transfers_offsite"]


def token():
    t = os.environ.get("INTERNAL_COSTS_TOKEN")
    if t:
        return t
    env = os.path.join(ROOT, "site", ".env.local")
    if os.path.exists(env):
        for line in open(env, encoding="utf-8"):
            if line.startswith("INTERNAL_COSTS_TOKEN="):
                return line.split("=", 1)[1].strip().strip('"')
    return None


def read_page(base, query):
    jar = http.cookiejar.CookieJar()
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    t = token()
    if t:
        op.open(f"{base}/internal/unlock?token={urllib.parse.quote(t)}", timeout=60).read()
    return op.open(f"{base}/industry{'?' + query if query else ''}", timeout=120).read().decode("utf-8")


def page_figures(text):
    figs = {}
    for m in re.finditer(r'data-fig="([^"]+)"[^>]*>([^<]*)<', text):
        figs[m.group(1)] = html.unescape(m.group(2)).replace("<!-- -->", "")
    for m in re.finditer(r'data-not-held="([^"]+)"', text):
        figs.setdefault(m.group(1), None)
    return figs


def num(s):
    """A figure as the page prints it, as a number (percent, dollars, billions and TWh as printed)."""
    if s is None:
        return None
    t = s.replace(",", "").replace("$", "").replace("bn", "").replace("%", "").replace("+", "").strip()
    return float(t)


def month_value(f, key, month):
    m = f["monthly"]
    if month not in m["months"]:
        return None
    return m["by_source"].get(key, [None] * len(m["months"]))[m["months"].index(month)]


def year_sum(f, key, year):
    vals = [month_value(f, key, f"{year}-{mm:02d}") for mm in range(1, 13)]
    return None if any(v is None for v in vals) else sum(vals)


def last_month(f):
    m = f["monthly"]
    for i in range(len(m["months"]) - 1, -1, -1):
        if m["by_source"]["total"][i] is not None:
            return m["months"][i]
    return None


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://localhost:3000")
    ap.add_argument("--query", default="")
    a = ap.parse_args(argv)
    f = json.load(open(FILE, encoding="utf-8"))
    try:
        text = read_page(a.base, a.query)
    except Exception as e:  # noqa: BLE001
        print(f"the page could not be read: {e}")
        return 2
    figs = page_figures(text)
    if not figs:
        print("no figure on the page (is it the in-review page? set INTERNAL_COSTS_TOKEN)")
        return 2
    q = dict(urllib.parse.parse_qsl(a.query))
    want = {}
    # the headlines and the monthly table
    last = last_month(f)
    want["h-month"] = month_value(f, "total", last)
    whole = next(y for y in range(int(last[:4]), 1972, -1) if year_sum(f, "total", y) is not None)
    want["h-year"] = year_sum(f, "total", whole)
    ind = f["industries"]
    us = sorted([n for n in ind["ranked_3_digit"] if ind["industries"][n]["by_region"].get("us", {}).get("total") is not None],
                key=lambda n: -ind["industries"][n]["by_region"]["us"]["total"])
    want["h-top"] = ind["industries"][us[0]]["by_region"]["us"]["total"]
    ago = f"{int(last[:4]) - 1}{last[4:]}"
    for k in MONTHLY:
        x, y = month_value(f, k, last), month_value(f, k, ago)
        want[f"m-{k}"], want[f"m1-{k}"] = x, y
        want[f"mc-{k}"] = None if x is None or y is None or not y else 100 * (x - y) / y
    # the industries ranked, in the region chosen
    region = q.get("region", "us")
    rows = {n: ind["industries"][n]["by_region"].get(region, {}) for n in ind["ranked_3_digit"]}
    withheld = any(r.get("total") is None for r in rows.values())
    s = sum(r["total"] for r in rows.values() if r.get("total") is not None)
    for n, r in rows.items():
        want[f"sh-{n}"] = None if withheld or r.get("total") is None else 100 * r["total"] / s
        for fu in FUELS:
            want[f"f-{n}-{fu}"] = r.get(fu)
    ia, ib = q.get("a", us[0]), q.get("b", us[1])
    for side, n in (("a", ia), ("b", ib)):
        for fu in FUELS:
            want[f"{side}-{fu}"] = ind["industries"][n]["by_region"].get(region, {}).get(fu)
        for e in ELEC:
            want[f"e{side}-{e}"] = ind["industries"][n].get("electricity_mwh", {}).get(region, {}).get(e)
    # the states
    st = f["states_annual"]
    years = [int(y) for y in st["years"]]
    newest = max(y for i, y in enumerate(years) if st["states"]["US"]["consumption_tbtu"]["total"][i] is not None)
    year = int(q.get("year", newest))
    src = q.get("src", "total")
    i = years.index(year)
    for code, d in st["states"].items():
        if code == "US":
            continue
        want[f"s-{code}"] = d["consumption_tbtu"].get(src, [None] * len(years))[i]
        want[f"st-{code}"] = d["consumption_tbtu"]["total"][i]
        want[f"sp-{code}"] = d["price_usd_per_mmbtu"][i]
        e = d["expenditures_usd"]["total"][i]
        want[f"se-{code}"] = None if e is None else e / 1e9
    ranked = sorted([c for c in st["states"] if c != "US" and st["states"][c]["consumption_tbtu"]["total"][years.index(newest)] is not None],
                    key=lambda c: -st["states"][c]["consumption_tbtu"]["total"][years.index(newest)])
    sales = f["electricity_sales_monthly"]
    for side, code in (("sa", q.get("sa", ranked[0])), ("sb", q.get("sb", ranked[1]))):
        d = st["states"][code]
        for k in SEDS:
            want[f"{side}-{k}"] = d["consumption_tbtu"].get(k, [None] * len(years))[i]
        a0, a1 = d["consumption_tbtu"]["total"][years.index(2019)], d["consumption_tbtu"]["total"][i]
        want[f"{side}-chg"] = None if a0 is None or a1 is None or not a0 else 100 * (a1 - a0) / a0
        want[f"{side}-price"] = d["price_usd_per_mmbtu"][i]
        e = d["expenditures_usd"]["total"][i]
        want[f"{side}-exp"] = None if e is None else e / 1e9
        ms = [sales["states"].get(code, [None] * len(sales["months"]))[sales["months"].index(f"{year}-{mm:02d}")] if f"{year}-{mm:02d}" in sales["months"] else None for mm in range(1, 13)]
        want[f"{side}-sales"] = None if any(v is None for v in ms) else sum(ms) / 1e6
    # the outlook, every case in the years the table shows
    o = f["outlook"]
    oi = q.get("oi", "iron_and_steel")
    names = list(o["industries"][oi])
    totals = sorted([n for n in names if re.search(r"Total$|Total Energy Use$", n) and "Ethanol" not in n], key=lambda n: "Total Energy Use" not in n)
    os_ = q.get("os", (totals + sorted(n for n in names if n not in totals))[0])
    for c in o["cases"]:
        for yi, yy in enumerate(o["years"]):
            if int(yy) % 5 == 0 or yi == 0:
                want[f"o-{c}-{yy}"] = o["industries"][oi][os_].get(c, [None] * len(o["years"]))[yi]
    # compare
    out, bad = [], 0
    for k, w in sorted(want.items()):
        if k not in figs:
            continue
        p = figs[k]
        pv = num(p)
        if w is None or pv is None:
            ok = w is None and pv is None
        else:
            tol = 0.051 if k.startswith(("mc-", "sh-", "sa-chg", "sb-chg", "sp-", "sa-price", "sb-price", "se-", "sa-exp", "sb-exp", "sa-sales", "sb-sales")) else (0.51 if abs(w) >= 100 else 0.051)
            ok = abs(pv - w) <= tol
        bad += 0 if ok else 1
        out.append({"figure": k, "page": p, "file": w, "same": "yes" if ok else "NO"})
    with open(os.path.join(HERE, "figures.csv"), "w", encoding="utf-8", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=["figure", "page", "file", "same"])
        wr.writeheader()
        wr.writerows(out)
    unchecked = sorted(k for k in figs if k not in want)
    # the cross-checks (two EIA publications beside each other), for every year both hold
    cc = []
    for y in years:
        mer = year_sum(f, "total", y)
        seds = st["states"]["US"]["consumption_tbtu"]["total"][years.index(y)]
        if mer is not None and seds is not None:
            cc.append({"year": y, "check": "industrial total, TBtu", "a": "Monthly Energy Review, twelve months", "a_value": round(mer, 3),
                       "b": "State Energy Data System, United States", "b_value": seds, "diff_pct": round(100 * (mer - seds) / seds, 2)})
        ms = [sales["states"]["US"][sales["months"].index(f"{y}-{mm:02d}")] if f"{y}-{mm:02d}" in sales["months"] else None for mm in range(1, 13)]
        el = st["states"]["US"]["consumption_tbtu"]["electricity"][years.index(y)]
        if all(v is not None for v in ms) and el is not None:
            tb = sum(ms) * 3412 / 1e9
            cc.append({"year": y, "check": "electricity sold to industry, TBtu", "a": "Form EIA-861M, twelve months at 3,412 Btu per kWh", "a_value": round(tb, 3),
                       "b": "State Energy Data System, United States", "b_value": el, "diff_pct": round(100 * (tb - el) / el, 2)})
    with open(os.path.join(HERE, "crosscheck.csv"), "w", encoding="utf-8", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=["year", "check", "a", "a_value", "b", "b_value", "diff_pct"])
        wr.writeheader()
        wr.writerows(cc)
    print(f"{len(out)} figures compared, {len(out) - bad} reproduced, {bad} differ; {len(unchecked)} marked figures not computed here: {unchecked[:8]}")
    for r in cc[-4:]:
        print(f"  cross-check {r['year']} {r['check']}: {r['a_value']} against {r['b_value']} ({r['diff_pct']} percent)")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
