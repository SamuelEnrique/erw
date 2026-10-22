#!/usr/bin/env python3
"""Where can a large load go: the All grids tab's figures, computed a second time outside the site (session 712).

Energy Research Warehouse (ERW). docs/methods/siting.md, "The replication". Standard library only. For three hub and
zone rows and three ERCOT nodes, under each of the four profiles at its defaults, this computes every figure of the tab
from its sources and prints it beside the page's own:

    the live set, with the anon key only     ercot_4cp_intervals (the four peaks), lbnl_interconnection_queue (the months
                                             to connect), eia930_demand_growth (demand growth), carbon_intensity_hourly
                                             (the carbon over the hours run), ercot_large_load_status (approved MW)
    the tab's own files, in the repository   the hourly hub and zone prices (site/data/datacenter: the history is not in
                                             the live set), the node basis, eGRID's subregions, EIA-861's utilities and
                                             the Commission's rate (site/data/siting, site/data/datacenter): tables held
                                             out of the live set for its size or their terms

    python warehouse/replication/siting.py --repo . [--page http://localhost:3000]

SUPABASE_URL and SUPABASE_ANON_KEY are read from the environment (the anon key: what any reader of the site may use).
With --page, the page's addresses are read with the internal cookie (INTERNAL_COSTS_TOKEN in the environment: the tab is
in review) and each figure is set beside the page's data-raw; without it, the figures are printed alone. Exit 0 when every
figure set beside the page equals it (to 1e-9 relative), 1 when one differs or a read fails, 2 on bad input.
"""

import argparse
import calendar
import html
import json
import math
import os
import re
import sys
import urllib.parse
import urllib.request

ROWS = ["ercot:HB_HUBAVG", "caiso:TH_SP15_GEN-APND", "nyiso:N.Y.C."]
NODES = 3
NODE_HUB = "HB_HUBAVG"
NEAR, NODE_NEAR = 0.95, 0.9
PROFILES = {
    "datacenter": {"lf": 0.9, "curtail": "none", "strike": None},
    "flexible": {"lf": 0.9, "curtail": "peaks_strike", "strike": 1000},
    "electrolyzer": {"lf": 0.55, "curtail": "below_strike", "strike": None},
    "industry": {"lf": 0.8, "curtail": "interruptible", "strike": None},
}
NO_CAPACITY = {"ercot", "caiso", "spp"}


def js_round(x):
    """JavaScript's Math.round (half up), not Python's (half to even)."""
    return math.floor(x + 0.5)


# ---------------------------------------------------------------------------------------------------------------------
# the hours, as lib/datacenter.ts counts them (standard time, every day 24)
# ---------------------------------------------------------------------------------------------------------------------

def leap(y):
    return y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)


def month_starts(y):
    out = [0]
    for m in range(12):
        out.append(out[-1] + 24 * calendar.monthrange(y, m + 1)[1])
    return out


def expand(f, region, buy):
    out = [None] * f["hours"]
    s = f["regions"].get(region, {}).get(buy)
    if s:
        for i, v in enumerate(s["v"]):
            out[s["s"] + i] = v
    return out


def months_of_year(y, p, w):
    st, out = month_starts(y), []
    for m in range(12):
        r = {"m": f"{y}-{m + 1:02d}", "due": st[m + 1] - st[m], "held": 0, "flat": 0.0, "cost": 0.0, "energy": 0.0, "down": 0}
        for i in range(st[m], st[m + 1]):
            v = p[i]
            if v is None:
                continue
            r["held"] += 1
            r["flat"] += v
            r["cost"] += v * w[i]
            r["energy"] += w[i]
            if w[i] == 0:
                r["down"] += 1
        r["complete"] = r["held"] >= NEAR * r["due"]
        if r["held"]:
            out.append(r)
    return out


def consecutive(files):
    by = {f["year"]: f for f in files}
    ys = sorted(by)
    return [by.get(y, {"year": y, "hours": 8784 if leap(y) else 8760, "regions": {}}) for y in range(ys[0], ys[-1] + 1)] if ys else []


def prev(m, k):
    y, mo = int(m[:4]), int(m[5:7]) - k
    while mo <= 0:
        y, mo = y - 1, mo + 12
    return f"{y}-{mo:02d}"


def last_twelve(ms):
    by = {r["m"]: r for r in ms}
    for r in reversed(ms):
        if not r["complete"]:
            continue
        tw = [by.get(prev(r["m"], k)) for k in range(12)]
        if all(t and t["complete"] for t in tw):
            return list(reversed(tw))
    return None


def flat_twelve(files, region, buy):
    ms = []
    for f in consecutive(files):
        p = expand(f, region, buy)
        ms += months_of_year(f["year"], p, [0 if v is None else 1 for v in p])
    l12 = last_twelve(ms)
    if not l12:
        return None
    held = sum(r["held"] for r in l12)
    return {"per": sum(r["flat"] for r in l12) / held, "from": l12[0]["m"], "to": l12[11]["m"], "months": [r["m"] for r in l12]}


def hour_of(ts, behind):
    """The year and hour, in standard time, of an instant: app/cost-of-power/model.ts's steps."""
    y, mo, d = int(ts[:4]), int(ts[5:7]), int(ts[8:10])
    h, mi = int(ts[11:13]), int(ts[14:16])
    import datetime as dt
    t = dt.datetime(y, mo, d, h, mi, tzinfo=dt.timezone.utc) - dt.timedelta(hours=behind)
    return t.year, int((t - dt.datetime(t.year, 1, 1, tzinfo=dt.timezone.utc)).total_seconds() // 3600)


def rule_weight(curtail, v, peak, strike, at_or_below):
    if v is None:
        return 0
    if curtail == "peaks_strike":
        return 0 if peak or (strike is not None and v >= strike) else 1
    if curtail == "below_strike":
        if strike is None:
            return 1
        return 1 if (v <= strike if at_or_below else v < strike) else 0
    return 1


def profile_twelve(files, region, prof, behind, cp, grid):
    flat = flat_twelve(files, region, "da")
    if not flat:
        return None
    p = PROFILES[prof]
    y0, y1 = int(flat["from"][:4]), int(flat["to"][:4])
    years = []
    for f in sorted((f for f in files if y0 <= f["year"] <= y1), key=lambda f: f["year"]):
        pr, st = expand(f, region, "da"), month_starts(f["year"])
        win = [False] * len(pr)
        for m in range(12):
            lab = f"{f['year']}-{m + 1:02d}"
            if flat["from"] <= lab <= flat["to"]:
                for i in range(st[m], st[m + 1]):
                    win[i] = pr[i] is not None
        years.append((f, pr, win))
    prices = [v for _, pr, win in years for i, v in enumerate(pr) if win[i]]
    strike, at_or_below = p["strike"], False
    if p["curtail"] == "below_strike" and strike is None:
        strike = sorted(prices)[min(len(prices), max(1, js_round(p["lf"] * len(prices)))) - 1]
        at_or_below = True
    peaks = {}
    if p["curtail"] == "peaks_strike" and grid == "ercot":
        for sm in cp["summers"]:
            for iv in sm["intervals"]:
                y, i = hour_of(iv["ts"], behind)
                peaks.setdefault(y, set()).add(i)
    run = lost = held = 0
    cost = 0.0
    weights = []
    for f, pr, win in years:
        w = [rule_weight(p["curtail"], v, i in peaks.get(f["year"], ()), strike, at_or_below) for i, v in enumerate(pr)]
        weights.append((f["year"], w, win))
        for r in months_of_year(f["year"], pr, w):
            if flat["from"] <= r["m"] <= flat["to"]:
                held += r["held"]
                lost += r["down"]
                run += r["energy"]
                cost += r["cost"]
    return {"per": cost / run if run else None, "run": run, "lost": lost, "held": held, "strike": strike, "at_or_below": at_or_below, "weights": weights, "flat": flat}


# ---------------------------------------------------------------------------------------------------------------------
# the reads
# ---------------------------------------------------------------------------------------------------------------------

def rest(base, key, table, params):
    q = urllib.parse.urlencode(params)
    out, start = [], 0
    while True:
        req = urllib.request.Request(f"{base}/{table}?{q}", headers={"apikey": key, "Authorization": f"Bearer {key}", "Range": f"{start}-{start + 999}"})
        with urllib.request.urlopen(req, timeout=120) as r:
            page = json.load(r)
        out += page
        if len(page) < 1000:
            return out
        start += 1000


def read_json(repo, *p):
    with open(os.path.join(repo, "site", "data", *p), encoding="utf-8") as f:
        return json.load(f)


def page_keys(base, token, path):
    req = urllib.request.Request(f"{base}/internal/unlock", data=urllib.parse.urlencode({"token": token}).encode(), method="POST",
                                 headers={"Content-Type": "application/x-www-form-urlencoded", "Origin": base, "User-Agent": "erw-replication"})
    opener = urllib.request.build_opener(NoRedirect)
    try:
        r = opener.open(req, timeout=60)
        cookies = r.headers.get_all("Set-Cookie") or []
    except urllib.error.HTTPError as e:
        cookies = e.headers.get_all("Set-Cookie") or []
    cookie = "; ".join(c.split(";")[0] for c in cookies)
    with urllib.request.urlopen(urllib.request.Request(f"{base}{path}", headers={"Cookie": cookie, "User-Agent": "erw-replication"}), timeout=300) as r:
        text = r.read().decode("utf-8")
    return {html.unescape(k): float(v) for k, v in re.findall(r'data-check="([^"]*)" data-raw="([^"]*)"', text)}


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


# ---------------------------------------------------------------------------------------------------------------------
# the figures
# ---------------------------------------------------------------------------------------------------------------------

def pkey(prof):
    p = PROFILES[prof]
    lf = ("%g" % p["lf"])
    return f"profile={prof}&lf={lf}&strike={'row' if p['strike'] is None else p['strike']}"


def figures(repo, base, key):
    index = read_json(repo, "datacenter", "index.json")
    nodes = read_json(repo, "siting", "nodes.json")
    carbon = read_json(repo, "siting", "carbon.json")
    utility = read_json(repo, "siting", "utility.json")
    delivery = read_json(repo, "datacenter", "texas_delivery.json")
    years = {}

    def files(grid):
        if grid not in years:
            years[grid] = [read_json(repo, "datacenter", f"{grid}_{y}.json") for y in index["grids"][grid]["years"]]
        return years[grid]
    # the live set, the anon key
    cp_rows = rest(base, key, "series", {"select": "ts_utc,value", "table_name": "eq.ercot_4cp_intervals", "entity": "eq.ercot:system", "variable": "eq.cp4_load_mw", "order": "ts_utc"})
    summers = {}
    for r in cp_rows:
        summers.setdefault(int(r["ts_utc"][:4]), []).append({"ts": r["ts_utc"][:19] + "Z"})
    cp = {"summers": [{"year": y, "intervals": v} for y, v in sorted(summers.items())]}
    rates = sorted((r for r in delivery["matrix"] if r["quantity"] == "postage_stamp_rate" and r["status"] == "approved" and r["matrix"] != "B"), key=lambda r: r["year"])
    rate = rates[-1]["value"]
    out = {}
    held_nodes = [n for n in sorted(nodes["nodes"], key=lambda n: n["id"]) if n.get("dam_basis")][:40]

    def node_energy(hub, n):
        s = days = due = 0
        for m in hub["months"]:
            due += calendar.monthrange(int(m[:4]), int(m[5:7]))[1]
            b = n.get("dam_basis", {}).get(m)
            if b:
                s += b[0] * b[1]
                days += b[1]
        return (s / days, days, due) if days >= NODE_NEAR * due else None
    hub_flat = flat_twelve(files("ercot"), NODE_HUB, "da")
    chosen = [n for n in held_nodes if node_energy(hub_flat, n)][:NODES]
    for prof in PROFILES:
        k = pkey(prof)
        for rid in ROWS + [f"ercot:{n['id']}" for n in chosen]:
            grid, region = rid.split(":", 1)
            node = grid == "ercot" and not region.startswith(("HB_", "LZ_"))
            behind = index["grids"][grid]["std_hours_behind_utc"]
            reg = NODE_HUB if node else region
            t = profile_twelve(files(grid), reg, prof, behind, cp, grid)
            basis = None
            if node:
                ne = node_energy(t["flat"], next(n for n in nodes["nodes"] if n["id"] == region))
                basis = ne[0]
                out[f"allgrids|basis|{rid}"] = basis
            energy = (t["per"] if prof != "datacenter" else t["flat"]["per"]) + (basis or 0)
            out[f"allgrids|energy|{rid}|da" + ("" if prof == "datacenter" else f"|{k}")] = energy
            if prof != "datacenter":
                out[f"allgrids|lost|{rid}|{k}"] = t["lost"]
            if grid == "ercot":
                summer = [s for s in cp["summers"] if len(s["intervals"]) == 4][-1]
                hours = t["run"] * 8760 / t["held"]
                by = {f["year"]: f for f in files("ercot")}

                def at(ts, curtail):
                    y, i = hour_of(ts, behind)
                    v = expand(by[y], reg, "da")[i] if y in by else None
                    if v is None:
                        return None
                    return rule_weight(curtail, v, True, t["strike"] if curtail == PROFILES[prof]["curtail"] else None, t["at_or_below"])
                own = [at(iv["ts"], PROFILES[prof]["curtail"]) for iv in summer["intervals"]]
                share = sum(own) / 4 if None not in own else None
                tx = rate * 1000 * share / hours if share is not None else None
                if not node:
                    out[f"allgrids|tx|{rid}|{k}"] = tx
                    out[f"allgrids|tx|{rid}|firm|{k}"] = rate * 1000 / hours
                if tx is not None:
                    out[f"allgrids|allin|{rid}|{k}"] = energy + tx
            if prof == "electrolyzer" and not node:
                out.setdefault("_carbonh", []).append((rid, grid, t))
    # the grid-level figures of the three rows
    lbnl = rest(base, key, "entities", {"select": "extra", "table_name": "eq.lbnl_interconnection_queue", "status": "eq.operating"})
    names = {"ercot": "ERCOT", "caiso": "CAISO", "nyiso": "NYISO"}
    for rid in ROWS:
        grid = rid.split(":")[0]
        import datetime as dt
        months = []
        for e in lbnl:
            x = e["extra"] or {}
            if x.get("region") != names[grid] or not x.get("q_date") or not x.get("on_date"):
                continue
            on, q = dt.date.fromisoformat(x["on_date"][:10]), dt.date.fromisoformat(x["q_date"][:10])
            if 2023 <= on.year <= 2025 and on >= q:
                months.append((on - q).days / 30.4375)
        months.sort()
        if len(months) >= 5:
            n = len(months)
            out[f"allgrids|connect|{rid}"] = (months[n // 2] if n % 2 else (months[n // 2 - 1] + months[n // 2]) / 2)
        sub = {"ercot": "ERCT", "caiso": "CAMX", "nyiso": "NYCW"}[grid]
        a = carbon["areas"][sub]
        out[f"allgrids|carbon|{rid}"] = a["co2_tons"] * 2000 / a["gen_mwh"] * 0.45359237
        u = utility["by"][{"ercot": "TX|ERCO", "caiso": "CA|CISO", "nyiso": "NY|NYIS"}[grid]]
        out[f"allgrids|utilrev|{rid}"] = u["revenue_usd"] / u["sales_mwh"]
    # the carbon over the electrolyzer's hours, from the live set's hourly intensity
    for rid, grid, t in out.pop("_carbonh", []):
        ba = {"ercot": "ERCO", "caiso": "CISO", "nyiso": "NYIS"}[grid]
        rows = rest(base, key, "series", {"select": "ts_utc,value", "table_name": "eq.carbon_intensity_hourly", "entity": f"eq.eia930:{ba}", "variable": "eq.intensity_demand",
                                          "ts_utc": f"gte.{t['flat']['from']}-01", "order": "ts_utc"})
        behind = index["grids"][grid]["std_hours_behind_utc"]
        hourly = {}
        for r in rows:
            y, i = hour_of(r["ts_utc"][:19], behind)
            hourly[(y, i)] = round(float(r["value"]), 1)
        s = e = hours = of = 0
        for y, w, win in t["weights"]:
            for i, wi in enumerate(w):
                if not win[i] or wi <= 0:
                    continue
                of += 1
                v = hourly.get((y, i))
                if v is None:
                    continue
                s += v * wi
                e += wi
                hours += 1
        if of and hours >= 0.9 * of and e:
            out[f"allgrids|carbonh|{rid}|{pkey('electrolyzer')}"] = s / e
    return out


PAGES = ["/cost-of-power?view=allgrids", "/cost-of-power?view=allgrids&profile=flexible", "/cost-of-power?view=allgrids&profile=electrolyzer",
         "/cost-of-power?view=allgrids&profile=industry", "/cost-of-power?view=allgrids&rows=nodes", "/cost-of-power?view=allgrids&rows=nodes&profile=flexible",
         "/cost-of-power?view=allgrids&rows=nodes&profile=electrolyzer", "/cost-of-power?view=allgrids&rows=nodes&profile=industry"]


def main(argv=None):
    ap = argparse.ArgumentParser(description="The All grids tab's figures, a second time")
    ap.add_argument("--repo", default=".", help="the repository's checkout (its site/data files)")
    ap.add_argument("--page", help="a build of the site to set the figures beside (e.g. http://localhost:3000)")
    a = ap.parse_args(argv)
    url, key = os.environ.get("SUPABASE_URL", "").rstrip("/"), os.environ.get("SUPABASE_ANON_KEY", "")
    if not url or not key:
        print("SUPABASE_URL and SUPABASE_ANON_KEY are needed (the anon key)", file=sys.stderr)
        return 2
    base = url if url.endswith("/rest/v1") else f"{url}/rest/v1"
    try:
        got = figures(a.repo, base, key)
    except Exception as e:
        print(f"FAILED: {type(e).__name__}: {e}", file=sys.stderr)
        return 1
    page = {}
    if a.page:
        token = os.environ.get("INTERNAL_COSTS_TOKEN", "")
        for p in PAGES:
            page.update(page_keys(a.page.rstrip("/"), token, p))
    bad = 0
    print(f"{'key':<100} {'replication':>16} {'page':>16}  equal")
    for k, v in sorted(got.items()):
        pv = page.get(k)
        if v is None:
            eq = "no figure" if pv is None else "NO"
        elif pv is None:
            eq = "not on the page" if a.page else ""
        else:
            eq = "yes" if math.isclose(v, pv, rel_tol=1e-9, abs_tol=1e-9) else "NO"
        bad += eq == "NO"
        print(f"{k:<100} {'' if v is None else f'{v:.6f}':>16} {'' if pv is None else f'{pv:.6f}':>16}  {eq}")
    n = sum(1 for k in got if k in page)
    print(f"{len(got)} figures computed; {n} set beside the page; {bad} differ")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
