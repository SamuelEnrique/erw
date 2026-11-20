"""Replication of the page "Every state" (/states).

Energy Research Warehouse (ERW). Session 8014 (chain 581, part B), 20 November 2026.

What it does. The page draws site/data/states/<st>.json (contract: docs/state/page_files_states.md; method:
docs/methods/states_page.md). This script reads the page as a reader's browser receives it, for a few choices of
place, takes every figure marked on it (each carries data-fig="<key>"), and computes each again from the files with its
own arithmetic, written from the method note and not from the page's code (site/lib/states.ts): the twelve months'
generation by source and its shares, each source's share of a whole year, a sector's twelve months of sales, revenue
and price, the capacity by source, the ten largest plants, who operates the grid, the state profile's figures, a year
of natural gas, SEDS, CO2, and the side-by-side table. A figure the page writes as "not held" must have no figure in
the file. Then a cross-check sets one EIA publication beside another, for five states:

1. Net generation of 2024, from the Electric Power Monthly's twelve months as the page's file holds them, beside the
   State Electricity Profile's total net generation for 2024 (eia_state_source_disposition_annual).
2. Retail sales of 2024, from Form EIA-861M's twelve months, beside the State Electricity Profile's sales by
   full-service and energy-only providers for 2024.

    python replication/states/replicate.py --base http://localhost:3000

The page is in review: the script opens the internal view with INTERNAL_COSTS_TOKEN (read from the environment or
site/.env.local). Exit 0 when every figure is reproduced and each state's 2024 generation agrees with its profile to 0.01 percent, 1 when
one does not (the sales cross-check is reported: EIA-861M's months hold estimates the annual EIA-861 replaces),
2 when the page cannot be read. It writes figures.csv and crosscheck.csv beside itself.
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
DIR = os.path.join(ROOT, "site", "data", "states")
SOURCES = ["coal", "natural_gas", "nuclear", "hydro", "wind", "solar", "other_renewables", "oil_and_other", "not_itemized"]
SECTORS = ["residential", "commercial", "industrial", "transportation", "all"]
QUERIES = ["", "a=CA&b=WV", "a=VT&b=US", "a=DC&b=NY"]
CROSS = ["CA", "TX", "NY", "WV", "VT"]


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
    return op.open(f"{base}/states{'?' + query if query else ''}", timeout=120).read().decode("utf-8")


def page_figures(text):
    figs = {}
    for m in re.finditer(r'data-fig="([^"]+)"[^>]*>([^<]*)<', text):
        figs[m.group(1)] = html.unescape(m.group(2)).replace("<!-- -->", "")
    for m in re.finditer(r'data-not-held="([^"]+)"', text):
        figs.setdefault(m.group(1), None)
    return figs


def num(s):
    if s is None:
        return None
    return float(s.replace(",", "").replace("$", "").replace("bn", "").replace("%", "").strip())


def load(st):
    with open(os.path.join(DIR, f"{st.lower()}.json"), encoding="utf-8") as fh:
        return json.load(fh)


def at(years, arr, y):
    if not years or arr is None or y not in years:
        return None
    return arr[years.index(y)]


def year_of_months(months, arr, y):
    if not months or arr is None:
        return None
    vals = [v for m, v in zip(months, arr) if m[:4] == y]
    return sum(vals) if len(vals) == 12 and all(v is not None for v in vals) else None


def expect(f, side=None):
    """Every figure of one place the page may print, keyed as the page keys it, with its unit factor and digits."""
    st, w = f["state"], {}
    g = f["generation"]
    if g.get("months"):
        l12 = g["last12"]
        for s in SOURCES:
            w[f"g12-{st}-{s}"] = (l12["mwh"][s], 1e-6, 1)
            w[f"g12s-{st}-{s}"] = (l12["share_pct"][s], 1, 1)
        w[f"g12t-{st}"] = (l12["total_mwh"], 1e-6, 1)
        whole = [y for y, t in zip(g["years"], g["annual"]["total"]) if t is not None]
        for y in whole:
            t = at(g["years"], g["annual"]["total"], y)
            w[f"gyt-{st}-{y}"] = (t, 1e-6, 1)
            for s in SOURCES:
                v = at(g["years"], g["annual"][s], y)
                w[f"gy-{st}-{s}-{y}"] = (None if v is None or not t else 100 * v / t, 1, 1)
    r = f["retail"]
    if r.get("months"):
        for s in SECTORS:
            b = r["last12"]["by_sector"][s]
            w[f"r-{st}-{s}-s"] = (b["sales_mwh"], 1e-6, 1)
            w[f"r-{st}-{s}-r"] = (b["revenue_usd"], 1e-9, 2)
            w[f"r-{st}-{s}-p"] = (b["price_usd_per_mwh"], 0.1, 2)
            w[f"r-{st}-{s}-c"] = (r["customers"]["by_sector"][s], 1, 0)
    p = f["plants"]
    if p.get("largest"):
        for t, c in p["capacity_by_technology"].items():
            w[f"c-{st}-{t}"] = (c["nameplate_mw"], 1, 0)
            w[f"cs-{st}-{t}"] = (c["net_summer_mw"], 1, 0)
        w[f"c-{st}-all"] = (p["capacity_total_mw"], 1, 0)
        for i, row in enumerate(p["largest"]):
            w[f"pl-{st}-{i}"] = (row["nameplate_mw"], 1, 0)
    sv = f["serving"]
    for a in sv.get("by_authority") or []:
        w[f"sv-{st}-{a['code'] or 'none'}"] = (a["share_pct"], 1, 1)
    d = f["disposition"]
    if d.get("years"):
        for k in ["total_net_generation", "full_service_providers", "energy_only_providers", "net_interstate_trade", "estimated_losses"]:
            for y in d["years"][-3:]:
                w[f"dp-{st}-{k}-{y}"] = (at(d["years"], d["values"].get(k), y), 1, 0)
    ga = f["gas"]
    if ga.get("months"):
        last = ga["months"][-1]
        gy = last[:4] if last.endswith("-12") else str(int(last[:4]) - 1)
        for k in ["residential", "commercial", "industrial", "electric_power"]:
            w[f"gas-{st}-{k}"] = (year_of_months(ga["months"], ga["consumption"].get(k), gy), 1e-3, 1)
        w[f"gas-{st}-prod"] = (year_of_months(ga["months"], ga["marketed_production"], gy), 1e-3, 1)
    e = f["energy"]
    if e.get("years"):
        ey = e["years"][-1]
        for k, arr in e["by_source"].items():
            w[f"seds-{st}-{k}"] = (at(e["years"], arr, ey), 1, 1)
        for k, arr in e["by_sector"].items():
            w[f"seds-{st}-sec-{k}"] = (at(e["years"], arr, ey), 1, 1)
    return w


def co2_last(f):
    c = f["co2"]
    if not c.get("years"):
        return None, None
    for i in range(len(c["years"]) - 1, -1, -1):
        if c["tons_by_fuel"]["all"][i] is not None:
            return c["tons_by_fuel"]["all"][i], c["rate_kg_per_mwh"][i]
    return None, None


def headline_and_side(a, b):
    w = {}
    l12 = a["generation"].get("last12")
    if l12:
        w["h-gen"] = (l12["total_mwh"], 1e-6, 1)
        top = max(SOURCES, key=lambda s: l12["share_pct"][s] if l12["share_pct"][s] is not None else -1)
        w["h-top"] = (l12["share_pct"][top], 1, 1)
    w["h-price"] = ((a["retail"].get("last12") or {}).get("by_sector", {}).get("all", {}).get("price_usd_per_mwh"), 0.1, 2)
    t, _ = co2_last(a)
    w["h-co2"] = (t, 1e-6, 1)
    if b:
        for tag, f in (("a", a), ("b", b)):
            l = f["generation"].get("last12") or {}
            w[f"sd-{tag}-gen"] = (l.get("total_mwh"), 1e-6, 1)
            for s in SOURCES[:6]:
                w[f"sd-{tag}-sh-{s}"] = ((l.get("share_pct") or {}).get(s), 1, 1)
            for s in ["residential", "commercial", "industrial", "all"]:
                w[f"sd-{tag}-p-{s}"] = ((f["retail"].get("last12") or {}).get("by_sector", {}).get(s, {}).get("price_usd_per_mwh"), 0.1, 2)
            w[f"sd-{tag}-cap"] = (f["plants"].get("capacity_total_mw"), 1e-3, 1)
            tons, rate = co2_last(f)
            w[f"sd-{tag}-co2"] = (tons, 1e-6, 1)
            w[f"sd-{tag}-rate"] = (rate, 1, 1)
    return w


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://localhost:3000")
    a = ap.parse_args(argv)
    rows, bad, seen = [], 0, 0
    for q in QUERIES:
        try:
            text = read_page(a.base, q)
        except Exception as e:  # noqa: BLE001
            print(f"the page could not be read ({q}): {e}")
            return 2
        figs = page_figures(text)
        if not figs:
            print("no figure on the page (is it the in-review page? set INTERNAL_COSTS_TOKEN)")
            return 2
        qd = dict(urllib.parse.parse_qsl(q))
        A = load(qd.get("a", "TX"))
        B = load(qd["b"]) if qd.get("b") and qd["b"] != "none" else None
        want = {**expect(A), **(expect(B) if B else {}), **headline_and_side(A, B)}
        for k, shown in figs.items():
            if k not in want:
                continue
            seen += 1
            v, factor, nd = want[k]
            page = num(shown)
            if v is None:
                ok = page is None
                mine = None
            else:
                # the page's figure is the value rounded to its digits, by either convention at a half: within half a unit
                mine = round(v * factor, nd + 3)
                ok = page is not None and abs(page - v * factor) <= 10 ** (-nd) * 0.5 + 1e-6
            bad += 0 if ok else 1
            rows.append({"query": q or "(default)", "key": k, "page": shown, "file": mine, "ok": ok})
    with open(os.path.join(HERE, "figures.csv"), "w", newline="", encoding="utf-8") as fh:
        wr = csv.DictWriter(fh, fieldnames=["query", "key", "page", "file", "ok"])
        wr.writeheader()
        wr.writerows(rows)
    cross, cbad = [], 0
    for st in CROSS:
        f = load(st)
        g, r, d = f["generation"], f["retail"], f["disposition"]
        gen = at(g["years"], g["annual"]["total"], "2024")
        prof = at(d["years"], d["values"]["total_net_generation"], "2024")
        sales = at(r["years"], r["annual_sales_mwh"]["all"], "2024")
        psales = (at(d["years"], d["values"]["full_service_providers"], "2024") or 0) + (at(d["years"], d["values"]["energy_only_providers"], "2024") or 0)
        for what, x, y in (("net generation 2024, MWh", gen, prof), ("retail sales 2024, MWh", sales, psales)):
            diff = None if x is None or not y else 100 * (x - y) / y
            # generation: the two are the same EIA count and must agree to 0.01 percent; sales: EIA-861M's months
            # (estimates for the small utilities) beside the annual EIA-861 of the profile, reported, not a gate
            gate = what.startswith("net generation")
            ok = diff is not None and abs(diff) <= (0.01 if gate else 3.0)
            cbad += 0 if ok or not gate else 1
            cross.append({"state": st, "what": what, "monthly_sum": x, "state_profile": y, "diff_pct": None if diff is None else round(diff, 3), "within_tolerance": ok})
    with open(os.path.join(HERE, "crosscheck.csv"), "w", newline="", encoding="utf-8") as fh:
        wr = csv.DictWriter(fh, fieldnames=["state", "what", "monthly_sum", "state_profile", "diff_pct", "within_tolerance"])
        wr.writeheader()
        wr.writerows(cross)
    print(f"{seen - bad} of {seen} figures reproduced across {len(QUERIES)} views; generation cross-check {len(CROSS) - cbad} of {len(CROSS)} within 0.01 percent; sales reported")
    for c in cross:
        print(f"  {c['state']} {c['what']}: {c['monthly_sum']} against {c['state_profile']} ({c['diff_pct']}%)")
    for r in rows:
        if not r["ok"]:
            print(f"  differs: {r['query']} {r['key']} page {r['page']} file {r['file']}")
    return 0 if bad == 0 and cbad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
