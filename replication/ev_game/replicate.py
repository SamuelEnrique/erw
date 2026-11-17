#!/usr/bin/env python3
"""ERW, Should your family get an EV? (/play/ev): the replication a reader can run (session 7536, chain 304).

The game prices a year of driving on gasoline and on electricity, and from it the payback and the net present value of
the EV, for the United States or a chosen state, with every input the player's to move. Its rules are stated in the
method note (docs/methods/ev_game.md: "The model", "Every input, its default and its source", "The chart's axes" and
"The figures keyed for check-values"); its two prices are rows of two ERW tables of EIA's figures
(eia_retail_electricity_prices, eia_regional_retail_fuel_prices), which the page reads through its own file
site/data/ev_prices.json. This script reads the note's rules (typed below, each with the note's words), the two tables,
that file and the players' cases (cases.json), and nothing else. For each case it recomputes every figure the game
shows a player, and every outcome it marks (payback "at once" or "never", "Saved" or "Extra a year", whether the lines
cross), and sets each beside what the game shows for the same case (page_figures.json, read off the game drawn to HTML
by site/scripts/ev-game-figures.mjs), with whether it is inside half of the page's last shown digit.

It was written from the note, not from the page's code (site/lib/ev.ts, site/app/play/ev/EvGame.tsx), and shares
nothing with it.

    python replication/ev_game/replicate.py                     every figure, N of N, and the prices against the tables
    python replication/ev_game/replicate.py --in-dir DIR        the two tables from DIR (default warehouse/output)
    python replication/ev_game/replicate.py --headline          the five headline figures of the do-file
    python replication/ev_game/replicate.py --crosscheck        the prices set beside EIA's, AFDC's and PG&E's own figures

Exit 0 when every figure is inside its tolerance, 1 when one is not, 2 when the inputs cannot be read. Standard
library only. No request is made and nothing is written.
"""
import csv
import json
import math
import os
import sys

# Ruling alternative 1 of /play/ev (session 7720, branch wip/alt-ev-game-1; not a default on main): California's home price
# defaults to PG&E's E-TOU-C winter off-peak total rate, USD 0.36757 per kWh (site/data/bill_rules.json, read 30 September 2026).
TOU_DEFAULT = {"CA": 367.57}
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
PRICES = os.path.join(ROOT, "site", "data", "ev_prices.json")
E_TABLE, G_TABLE = "eia_retail_electricity_prices", "eia_regional_retail_fuel_prices"

# The note, "Every input, its default and its source": the default, and a word of the source the page must cite.
DEFAULTS = {
    "miles": (15000, "Fuel Economy Guide"), "mpg": (27, "vehicle 48061"), "kwhPerMile": (0.31, "vehicle 48697"),
    "gasCar": (28600, "Equinox LT"), "evCar": (33600, "Equinox EV LT1"), "homeShare": (100, "assumption"),
    "years": (8, "assumption"), "rate": (5, "Circular A-94"), "credit": (7500, "30 September 2025"),
}
# EIA's Petroleum Administration for Defense Districts, as EIA's weekly gasoline survey publishes them (the note,
# "Gasoline by state where EIA publishes it, else by region"): the nine states with their own weekly series, and the
# region every other state takes. Written from EIA's PADD definitions, not from the page's builder.
OWN = {"CA", "CO", "FL", "MA", "MN", "NY", "OH", "TX", "WA"}
PADD = {
    "R1X": ("PADD 1A", "CT ME MA NH RI VT"), "R1Y": ("PADD 1B", "DE DC MD NJ NY PA"), "R1Z": ("PADD 1C", "FL GA NC SC VA WV"),
    "R20": ("PADD 2", "IL IN IA KS KY MI MN MO NE ND SD OH OK TN WI"), "R30": ("PADD 3", "AL AR LA MS NM TX"),
    "R40": ("PADD 4", "CO ID MT UT WY"), "R5XCA": ("PADD 5 except California", "AK AZ HI NV OR WA"),
}
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def table(path, keep):
    """A warehouse-shaped CSV: '#' header lines, then a header row with entity, variable, ts_utc, value."""
    out = {}
    with open(path, encoding="utf-8") as f:
        for d in csv.DictReader(line for line in f if not line.startswith("#")):
            if keep(d["entity"]) and d["value"] != "":
                out[(d["entity"], d["ts_utc"][:10])] = float(d["value"])
    return out


def region_of(code):
    return next(k for k, (_, states) in PADD.items() if code in states.split())


def money(v, d=0):
    return round(v, d)


def compute(x):
    """The note, "The model". x: miles, mpg, kwhPerMile, gas (USD/gal), power (USD/MWh), gasCar, evCar, years, rate,
    credit (0 when off), homeShare, public (USD/MWh or None)."""
    h = x["homeShare"]
    if h >= 100:
        kwh_price = x["power"] / 1000
    elif x["public"] is None:
        return None  # "Below 100 percent at home, the result waits for this price"
    else:
        kwh_price = (h / 100 * x["power"] + (1 - h / 100) * x["public"]) / 1000
    gas_year = x["miles"] / x["mpg"] * x["gas"]
    ev_year = x["miles"] * x["kwhPerMile"] * kwh_price
    save = gas_year - ev_year
    extra = x["evCar"] - x["gasCar"] - x["credit"]
    payback = 0 if extra <= 0 else (extra / save if save > 0 else None)
    npv = sum(save / (1 + x["rate"] / 100) ** t for t in range(1, int(x["years"]) + 1)) - extra
    rows = [(t, x["gasCar"] + gas_year * t, x["evCar"] - x["credit"] + ev_year * t) for t in range(int(x["years"]) + 1)]
    cross = payback if payback is not None and 0 < payback <= x["years"] else None
    return {"gas_year": gas_year, "ev_year": ev_year, "save": save, "extra": extra, "payback": payback, "npv": npv, "rows": rows, "cross": cross}


def axis(rows):
    """The note, "The chart's axes": the money axis in steps of $5k, or $10k past $40k, or $20k past $100k, from $0 to
    the first step at or above the dearest point."""
    top = max(max(g, e) for _, g, e in rows)
    step = 20000 if top > 100000 else 10000 if top > 40000 else 5000
    ymax = math.ceil(top / step) * step
    return " ".join("$0" if v == 0 else f"${v // 1000}k" for v in range(0, ymax + 1, step))


def fmt_num(v, d):
    return f"{v:,.{d}f}"


def case_inputs(start, prices):
    start = start or {}
    code = start.get("code", "US")
    place = prices["us"] if code == "US" else next(s for s in prices["states"] if s["code"] == code)
    name = "the United States as a whole" if code == "US" else place["name"]
    v = {k: d for k, (d, _) in DEFAULTS.items()}
    v.update(start.get("v", {}))
    credit_on = bool(start.get("creditOn"))
    gas = start["gas"] if start.get("gas") is not None else (place["gas"] or {}).get("value")
    # ruling alternative 1 (wip/alt-ev-game-1): a time-of-use default where the site holds one (PG&E E-TOU-C winter off-peak, site/data/bill_rules.json)
    tou = TOU_DEFAULT.get(code) if place is not None and code != "US" else None
    power = start["power"] if start.get("power") is not None else tou if tou is not None else (place["power"] or {}).get("value")
    typed = start.get("publicCents", "")
    try:
        pub = float(typed) * 10 if typed.strip() != "" else None
        pub = pub if pub is not None and math.isfinite(pub) and pub >= 0 else None
    except ValueError:
        pub = None
    x = None
    if gas is not None and power is not None:
        x = dict(v, gas=gas, power=power, credit=v["credit"] if credit_on else 0, public=pub)
    moved = {k for k in DEFAULTS if k in start.get("v", {}) and start["v"][k] != DEFAULTS[k][0]}
    at_defaults = not credit_on and start.get("gas") is None and start.get("power") is None and not moved
    return {"code": code, "place": place, "name": name, "v": v, "credit_on": credit_on, "gas": gas, "power": power, "typed": typed,
            "x": x, "moved": moved, "at_defaults": at_defaults, "gas_over": start.get("gas") is not None, "power_over": start.get("power") is not None}


def day_words(ts):
    y, m, d = (int(p) for p in ts.split("-"))
    return f"{MONTHS[m - 1]} {d}, {y}"


def month_words(ts):
    y, m, _ = (int(p) for p in ts.split("-"))
    return f"{MONTHS[m - 1]} {y}"


FIELD_FMT = {
    "miles": lambda m: f"{m:,.0f} miles", "mpg": lambda m: f"{m:g} mpg", "kwhPerMile": lambda m: f"{m:.2f} kWh",
    "gasCar": lambda m: f"${m:,.0f}", "evCar": lambda m: f"${m:,.0f}", "homeShare": lambda m: f"{m:g} percent",
    "years": lambda m: f"{m:g} year{'' if m == 1 else 's'}", "rate": lambda m: f"{m:.1f} percent", "credit": lambda m: f"${m:,.0f}",
}
PARENTS = {"miles_a_year": "miles", "the_gasoline_car_s_miles_per_gallon": "mpg", "the_ev_s_kwh_per_mile": "kwhPerMile",
           "the_gasoline_car_s_price_usd": "gasCar", "the_ev_s_price_usd": "evCar", "charging_done_at_home_percent": "homeShare",
           "years_you_keep_the_car": "years", "interest_rate_percent_a_year": "rate"}


def expected(key, c, prices):
    """What the note's rules give for one figure of one case: a number, or words that must match."""
    x, place, v = c["x"], c["place"], c["v"]
    r = compute(x) if x else None
    if key.startswith("field_") and key.endswith("_mine"):
        k = key[6:-5]
        moved = c["power_over"] if k == "power" else c["gas_over"] if k == "gas" else k in c["moved"]
        return "changed by you" if moved else "default"
    if key == "field_power" or key == "parents_electricity_at_home":
        return c["power"] / 10
    if key == "field_gas" or key == "parents_gasoline":
        return c["gas"]
    if key.startswith("field_"):
        return v[key[6:]]
    if key == "tip_power_default":
        return (TOU_DEFAULT.get(c["code"]) or place["power"]["value"]) / 10   # TOU: wip/alt-ev-game-1
    if key == "tip_gas_default":
        return place["gas"]["value"]
    if key.startswith("tip_") and key.endswith("_default"):
        return DEFAULTS[key[4:-8]][0]
    if key == "tip_power_month":
        return month_words(place["power"]["ts"])
    if key == "tip_gas_week":
        return day_words(place["gas"]["ts"])
    if key == "tip_gas_entity":
        return gas_entity(c["code"])
    if key == "tip_gas_where":
        if c["code"] == "US":
            return "the US average"
        if c["code"] in OWN:
            return f"{place['name']}'s own weekly series"
        return ("contains", PADD[region_of(c["code"])][0] + ")", f"EIA does not publish a weekly price for {place['name']}, so this is its region's")
    if key == "credit_switch":
        return "on" if c["credit_on"] else "off"
    if key == "waiting":
        if c["gas"] is None or c["power"] is None:
            return ("contains", "holds no")
        return "Type a public charger's price on the left to see the results."
    if key == "payback":
        return "never" if r["payback"] is None else "at once" if r["payback"] == 0 else r["payback"]
    if key == "payback_tip_extra":
        return r["extra"]
    if key == "payback_tip_after_credit":
        return "yes" if c["credit_on"] else "no"
    if key == "npv":
        return r["npv"]
    if key in ("npv_years", "chart_years"):
        return x["years"]
    if key == "npv_tip_rate":
        return x["rate"]
    if key == "gas_year":
        return r["gas_year"]
    if key == "ev_year":
        return r["ev_year"]
    if key == "save_year":
        return abs(r["save"])
    if key == "save_year_label":
        return "Saved a year with the EV" if r["save"] >= 0 else "Extra a year with the EV"
    if key in ("sr_power_cents", "raw_power_cents"):
        return round(c["power"] * 10) / 100
    if key in ("sr_gas", "raw_gas"):
        return c["gas"]
    if key == "raw_payback":
        return round(r["payback"] * 10) / 10
    if key == "raw_npv":
        return round(r["npv"])
    if key == "chart_gas_start":
        return r["rows"][0][1]
    if key == "chart_ev_start":
        return r["rows"][0][2]
    if key == "chart_gas_end":
        return r["rows"][-1][1]
    if key == "chart_ev_end":
        return r["rows"][-1][2]
    if key in ("chart_summary_cross", "chart_cross_label"):
        return "none" if r is None or r["cross"] is None else r["cross"]
    if key == "chart_y_ticks":
        return axis(r["rows"])
    if key == "chart_x_labels":
        return " ".join("_" if x["years"] > 10 and t % 2 else str(t) for t in range(int(x["years"]) + 1))
    if key == "parents_a_public_charger_s_price":
        return "not typed" if c["typed"].strip() == "" else f"{c['typed']} cents/kWh"
    if key == "parents_federal_tax_credit":
        return v["credit"] if c["credit_on"] else 0
    if key.startswith("parents_src_"):
        k = key[12:]
        if k == "electricity_at_home":
            if not c["power_over"] and c["code"] in TOU_DEFAULT:   # wip/alt-ev-game-1
                return "PG&E's E-TOU-C off-peak total rate, winter (October through May) (wip/alt-ev-game-1)"
            return "changed by you" if c["power_over"] else f"{E_TABLE}, {place['power']['entity']}, {month_words(place['power']['ts'])}"
        if k == "gasoline":
            return "changed by you" if c["gas_over"] else f"{G_TABLE}, {place['gas']['entity']}, week of {day_words(place['gas']['ts'])}"
        if k == "a_public_charger_s_price":
            return "typed by you"
        if k == "federal_tax_credit":
            return ("contains", "No federal credit for cars bought after 30 September 2025")
        f = PARENTS[k]
        return "changed by you" if f in c["moved"] else ("contains", DEFAULTS[f][1])
    if key.startswith("parents_"):
        return v[PARENTS[key[8:]]]
    if key == "built":
        return prices["built_at"][:10]
    raise KeyError(key)


def gas_entity(code):
    if code == "US":
        return "eia:EMM_EPMR_PTE_NUS_DPG"
    return f"eia:EMM_EPMR_PTE_S{code}_DPG" if code in OWN else f"eia:EMM_EPMR_PTE_{region_of(code)}_DPG"


def compare(f, want):
    """True when the page's figure stands with the rule's: a number inside half the last shown digit, words equal."""
    if isinstance(want, tuple) and want[0] == "contains":
        return all(w in f["shown"] for w in want[1:])
    if isinstance(want, str):
        return f["shown"] == want
    if f["value"] is None:
        return False
    return abs(f["value"] - want) <= f["tolerance"] + 1e-9


# Differences between the page's file and the table that are named, not inside: EIA revised these two states' July 2026
# residential prices after the file was built on 15 October 2026 (the table's rows were pulled again since), so the
# file holds EIA's first figure. A data fault: docs/reviews/ev-game-faults-2026-11-16.md, row 3.
REVISED = {"NY electricity:": "EIA's July figure revised after the file was built, fault row 3",
           "PA electricity:": "EIA's July figure revised after the file was built, fault row 3"}


def source_check(prices, in_dir):
    """Each price the page file holds against the table's row for its entity and date; the entity against the note's
    rule; and the newest row each table now holds (the file is built once and committed)."""
    ep, gp = os.path.join(in_dir, f"{E_TABLE}.csv"), os.path.join(in_dir, f"{G_TABLE}.csv")
    if not (os.path.exists(ep) and os.path.exists(gp)):
        print(f"the tables: not found in {in_dir}; the prices are taken from site/data/ev_prices.json as held, not checked against the tables")
        return 0, 0, []
    el = table(ep, lambda e: e.startswith("eia:retail_price:") and e.endswith(":RES"))
    ga = table(gp, lambda e: e.startswith("eia:EMM_EPMR_PTE_"))
    ok = n = 0
    notes = []
    places = [("US", prices["us"])] + [(s["code"], s) for s in prices["states"]]
    newest_e = max(ts for (e, ts) in el if e == "eia:retail_price:US:RES")
    newest_g = max(ts for (e, ts) in ga if e == "eia:EMM_EPMR_PTE_NUS_DPG")
    for code, s in places:
        pe = f"eia:retail_price:{code}:RES"
        n += 1
        held = el.get((pe, s["power"]["ts"]))
        good = s["power"]["entity"] == pe and held is not None and abs(held - s["power"]["value"]) < 1e-9
        ok += good
        if not good:
            notes.append(f"{code} electricity: file {s['power']['entity']} {s['power']['ts']} {s['power']['value']}, table {held}")
        n += 1
        ge = gas_entity(code)
        held = ga.get((ge, s["gas"]["ts"]))
        good = s["gas"]["entity"] == ge and held is not None and abs(held - s["gas"]["value"]) < 1e-9
        ok += good
        if not good:
            notes.append(f"{code} gasoline: file {s['gas']['entity']} {s['gas']['ts']} {s['gas']['value']}, rule {ge}, table {held}")
    named = [t for t in notes if t.split(" ")[0] + " " + t.split(" ")[1] in REVISED]
    print(f"the prices of site/data/ev_prices.json against the tables' rows (entity by the note's rule, value at the file's date): {ok} of {n}, {len(named)} named")
    for t in notes:
        key = t.split(" ")[0] + " " + t.split(" ")[1]
        print(f"  {'NAMED (' + REVISED[key] + ')' if key in REVISED else 'NOT EQUAL'}: {t}")
    ok += len(named)
    fe, fg = prices["us"]["power"]["ts"], prices["us"]["gas"]["ts"]
    stale = []
    if newest_e > fe:
        stale.append(f"electricity: the file's month is {fe[:7]}, the table now holds {newest_e[:7]} (US {el[('eia:retail_price:US:RES', fe)]} then, {el[('eia:retail_price:US:RES', newest_e)]} now, USD/MWh)")
    if newest_g > fg:
        stale.append(f"gasoline: the file's week is {fg}, the table now holds {newest_g} (US {ga[('eia:EMM_EPMR_PTE_NUS_DPG', fg)]} then, {ga[('eia:EMM_EPMR_PTE_NUS_DPG', newest_g)]} now, USD a gallon)")
    for t in stale:
        print(f"  NAMED (the file was built {prices['built_at'][:10]}): {t}")
    return ok, n, stale


def run(argv):
    in_dir = os.path.join(ROOT, "warehouse", "output")
    if "--in-dir" in argv:
        in_dir = argv[argv.index("--in-dir") + 1]
    try:
        prices = load_json(PRICES)
        page = load_json(os.path.join(HERE, "page_figures.json"))
    except (OSError, ValueError) as e:
        print(f"cannot read the inputs: {e}")
        return 2
    if "--headline" in argv:
        return headline(prices)
    if "--crosscheck" in argv:
        return crosscheck(prices, in_dir)
    if page["built_at"] != prices["built_at"]:
        print(f"page_figures.json was read from a price file built {page['built_at']}, the file now is {prices['built_at']}: redraw it")
        return 2
    sok, sn, _ = source_check(prices, in_dir)
    ok = n = 0
    misses = []
    for case in page["cases"]:
        c = case_inputs(case["start"], prices)
        for f in case["figures"]:
            n += 1
            want = expected(f["key"], c, prices)
            if compare(f, want):
                ok += 1
            else:
                misses.append(f"{case['id']} {f['key']}: page {f['shown']!r}, rule {want!r}")
    print(f"every figure the game shows, recomputed from the note's rules: {ok} of {n} inside half the page's last shown digit ({len(page['cases'])} cases)")
    for m in misses:
        print(f"  NOT INSIDE: {m}")
    print(f"in all: {ok + sok} of {n + sn}")
    return 0 if ok == n and sok == sn else 1


def headline(prices):
    """The do-file's five: the page as it opens (the United States, every default)."""
    c = case_inputs(None, prices)
    r = compute(c["x"])
    print(f"the prices: {c['power']} USD/MWh ({prices['us']['power']['ts'][:7]}), {c['gas']} USD a gallon (week of {prices['us']['gas']['ts']})")
    print(f"1 a year of gasoline (USD): {r['gas_year']:.2f}")
    print(f"2 a year of electricity (USD): {r['ev_year']:.2f}")
    print(f"3 saved a year with the EV (USD): {r['save']:.2f}")
    print(f"4 payback (years): {r['payback']:.4f}")
    print(f"5 net present value, 8 years at 5 percent (USD): {r['npv']:.2f}")
    return 0


# Published figures read on 16 November 2026 (the note, "The cross-check"). Each: publisher, document, date, figure.
EIA_WEEKLY_US = {"2026-10-05": 4.354, "2026-11-09": 3.995}  # EIA, Weekly U.S. Regular All Formulations Retail Gasoline Prices (series EMM_EPMR_PTE_NUS_DPG), read 16 November 2026
EIA_EPM_AUG_2026 = {  # EIA, Electric Power Monthly, Table 5.6.A, residential, August 2026, cents a kWh (released October 23, 2026)
    "US": 18.16, "CA": 29.75, "TX": 15.91, "OH": 19.38, "NY": 28.65, "MA": 30.48, "HI": 47.18, "FL": 14.99, "WA": 14.63,
    "AL": 16.33, "LA": 12.87, "ND": 13.31, "CT": 24.51,
}
AFDC_JULY_2026_GAS = 3.84  # DOE AFDC, Alternative Fuel Price Report, July 2026: national average, 1 to 15 July 2026, regular gasoline, USD a gallon
PGE_ETOUC = {"summer_peak": 0.52240, "summer_off": 0.39940, "winter_peak": 0.39757, "winter_off": 0.36757, "baseline_credit": 0.08140}  # site/data/bill_rules.json, PG&E E-TOU-C as read 2026-09-30


def crosscheck(prices, in_dir):
    gp, ep = os.path.join(in_dir, f"{G_TABLE}.csv"), os.path.join(in_dir, f"{E_TABLE}.csv")
    ga = table(gp, lambda e: e == "eia:EMM_EPMR_PTE_NUS_DPG") if os.path.exists(gp) else {}
    el = table(ep, lambda e: e.startswith("eia:retail_price:") and e.endswith(":RES")) if os.path.exists(ep) else {}
    print("ours | theirs | difference")
    us = prices["us"]
    print(f"US regular gasoline, week of {us['gas']['ts']} (the game): {us['gas']['value']:.3f} | EIA weekly series: {EIA_WEEKLY_US[us['gas']['ts']]:.3f} | {us['gas']['value'] - EIA_WEEKLY_US[us['gas']['ts']]:+.3f}")
    if ("eia:EMM_EPMR_PTE_NUS_DPG", "2026-11-09") in ga:
        t = ga[("eia:EMM_EPMR_PTE_NUS_DPG", "2026-11-09")]
        print(f"US regular gasoline, week of 2026-11-09 (the table, not yet in the game): {t:.3f} | EIA weekly series: {EIA_WEEKLY_US['2026-11-09']:.3f} | {t - EIA_WEEKLY_US['2026-11-09']:+.3f}")
    july = sorted((ts, v) for (e, ts), v in ga.items() if "2026-07-01" <= ts <= "2026-07-15")
    if july:
        m = sum(v for _, v in july) / len(july)
        print(f"US regular gasoline, the table's weeks of 1 to 15 July 2026 ({', '.join(ts for ts, _ in july)}), mean: {m:.3f} | AFDC Alternative Fuel Price Report, July 2026 (1 to 15 July): {AFDC_JULY_2026_GAS:.2f} | {m - AFDC_JULY_2026_GAS:+.3f}")
    for code, cents in EIA_EPM_AUG_2026.items():
        held = el.get((f"eia:retail_price:{code}:RES", "2026-08-01"))
        if held is not None:
            print(f"{code} residential electricity, August 2026 (the table, the month after the game's): {held / 10:.2f} cents | EIA EPM Table 5.6.A: {cents:.2f} | {held / 10 - cents:+.2f}")
    ca = next(s for s in prices["states"] if s["code"] == "CA")
    home = ca["power"]["value"] / 1000
    c = case_inputs({"code": "CA"}, prices)
    r = compute(c["x"])
    for k in ("summer_off", "winter_off"):
        x = dict(c["x"], power=PGE_ETOUC[k] * 1000)
        y = compute(x)
        print(f"California home price in the game ({ca['power']['ts'][:7]}): {home * 100:.2f} cents, a year of charging {r['ev_year']:.0f} USD | PG&E E-TOU-C {k.replace('_', ' ')}-peak total rate {PGE_ETOUC[k] * 100:.3f} cents, a year of charging {y['ev_year']:.0f} USD | {home * 100 - PGE_ETOUC[k] * 100:+.2f} cents")
    return 0


if __name__ == "__main__":
    sys.exit(run(sys.argv[1:]))
