"""Energy Research Warehouse (ERW), session 381: Research's replication, for a reader without Stata.

Reruns the figures of the ten cards of the findings library on /research (their default inputs) from the CSVs the
cards download, and nothing else: no table of the warehouse, no request, no file written. Each card's do-file in this
folder does the same in Stata; this file is its Python mirror, standard library and numpy only. Session 582 added the
tenth, peak_hour_moved (ERCOT and CAISO, erw_2026_peak_hour_solar.csv): /research shows its six callouts and until then
no mirror rebuilt them.

    python erw_2026_research_replication.py [folder]                (default: this file's folder)
    python erw_2026_research_replication.py [folder] --json <dir>   (compare with the cards' JSON in <dir>)

Prints one line a figure, `<card>.<key> = <value>`, under the card's name. With --json, each figure is set beside the
same key of <dir>/<card>.json ("numbers"; in the repository, site/data/findings) and the line says "same" or
"DIFFERENT"; the exit code is 1 when any differs. Exit 2 when a CSV is missing or unreadable.

The rules are the cards' own (warehouse/analysis/findings/<card>.py, numbers_from_rows) and the do-files':
- OLS with HC1 standard errors (Stata's `regress, vce(robust)`), p from Student's t on n - k degrees of freedom;
- OLS with standard errors clustered by day (`vce(cluster day_id)`): the factor (G / (G - 1)) ((N - 1) / (N - K)),
  p from Student's t on G - 1 degrees of freedom;
- OLS with Newey-West standard errors (`newey`, lag(L)): Bartlett weights 1 - j / (L + 1), the factor n / (n - k),
  L = floor(4 (n / 100) ^ (2 / 9)).
"""

import csv
import json
import math
import os
import sys

import numpy as np

CARDS = [
    ("batteries_lunch_grids", "erw_2026_grids_spikes_batteries.csv"),
    ("batteries_curtailment", "erw_2026_caiso_curtailment_batteries.csv"),
    ("batteries_curtailment_hourly", "erw_2026_caiso_curtailment_hourly.csv"),
    ("impact_study", "erw_2026_impact_event_control.csv"),
    ("gas_sets_price", "erw_2026_gas_share_hours.csv"),
    ("negative_prices_west", "erw_2026_negative_hours_hubs.csv"),
    ("peak_hour_grids", "erw_2026_grids_peak_hour_solar.csv"),
    ("peak_hour_moved", "erw_2026_peak_hour_solar.csv"),   # session 582
    ("queue_divorce", "erw_2026_queue_outcomes_technology.csv"),
    ("who_rescues_whom", "erw_2026_event_interchange_flips.csv"),
]


# ---------------------------------------------------------------- reading
def value(s):
    """A cell as the cards read it back: blank is missing, True and False are booleans, a number is a number."""
    s = s.strip()
    if s == "":
        return None
    if s in ("True", "False"):
        return s == "True"
    try:
        f = float(s)
    except ValueError:
        return s
    return int(f) if f.is_integer() and "." not in s and "e" not in s.lower() else f


def read_rows(path):
    with open(path, encoding="utf-8", newline="") as f:
        lines = [ln for ln in f if not ln.startswith("#")]
    reader = csv.DictReader(lines)
    return [{k: value(v) for k, v in r.items()} for r in reader]


# ---------------------------------------------------------------- Student's t, without scipy
def _betacf(a, b, x):
    """The continued fraction of the incomplete beta function (modified Lentz)."""
    tiny = 1e-300
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    d = 1.0 / (d if abs(d) > tiny else tiny)
    h = d
    for m in range(1, 1000):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > tiny else tiny)
        c = 1.0 + aa / c
        c = c if abs(c) > tiny else tiny
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > tiny else tiny)
        c = 1.0 + aa / c
        c = c if abs(c) > tiny else tiny
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 1e-16:
            break
    return h


def betainc(a, b, x):
    """The regularized incomplete beta function I_x(a, b)."""
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    lbt = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log1p(-x)
    if x < (a + 1.0) / (a + b + 2.0):
        return math.exp(lbt) * _betacf(a, b, x) / a
    return 1.0 - math.exp(lbt) * _betacf(b, a, 1.0 - x) / b


def p_two_sided(t, df):
    """2 P(T > |t|) for Student's t on df degrees of freedom."""
    if not math.isfinite(t):
        return float("nan")
    return betainc(df / 2.0, 0.5, df / (df + t * t))


# ---------------------------------------------------------------- the three regressions
def ols(y, X):
    y, X = np.asarray(y, float), np.asarray(X, float)
    bread = np.linalg.inv(X.T @ X)
    beta = bread @ X.T @ y
    e = y - X @ beta
    tot = float(((y - y.mean()) ** 2).sum())
    r2 = 1 - float((e ** 2).sum()) / tot if tot > 0 else float("nan")
    return y, X, bread, beta, e, r2


def hc1(y, X):
    y, X, bread, beta, e, r2 = ols(y, X)
    n, k = X.shape
    meat = (X * (e ** 2)[:, None]).T @ X
    se = np.sqrt(np.diag((n / (n - k)) * bread @ meat @ bread))
    p = [p_two_sided(b / s, n - k) for b, s in zip(beta, se)]
    return {"coef": list(beta), "se": list(se), "p": p, "n": n, "r2": r2}


def clustered(y, X, groups):
    y, X, bread, beta, e, r2 = ols(y, X)
    n, k = X.shape
    names = sorted(set(groups))
    index = {g: i for i, g in enumerate(names)}
    codes = np.array([index[g] for g in groups])
    S = np.zeros((len(names), k))
    np.add.at(S, codes, X * e[:, None])
    g = len(names)
    se = np.sqrt(np.diag((g / (g - 1)) * ((n - 1) / (n - k)) * (bread @ (S.T @ S) @ bread)))
    p = [p_two_sided(b / s, g - 1) for b, s in zip(beta, se)]
    return {"coef": list(beta), "se": list(se), "p": p, "n": n, "r2": r2, "clusters": g}


def newey(y, X):
    y, X, bread, beta, e, r2 = ols(y, X)
    n, k = X.shape
    lags = int(math.floor(4 * (n / 100.0) ** (2.0 / 9.0)))
    Z = X * e[:, None]
    S = Z.T @ Z
    for j in range(1, min(lags, n - 1) + 1):
        G = Z[j:].T @ Z[:-j]
        S = S + (1.0 - j / (lags + 1.0)) * (G + G.T)
    se = np.sqrt(np.diag((n / (n - k)) * bread @ S @ bread))
    p = [p_two_sided(b / s, n - k) if s > 0 else float("nan") for b, s in zip(beta, se)]
    return {"coef": list(beta), "se": list(se), "p": p, "n": n, "r2": r2, "lags": lags}


# ---------------------------------------------------------------- the cards
def batteries_lunch_grids(rows):
    """Each grid's spike measures on battery GW, mean load GW, Henry Hub and month-of-year (HC1); the first and last
    full years' worst-interval multiple. ERCOT keeps the first card's rule for its years (the last year before the
    newest); the other grids use the CSV's full_year flag."""
    n = {}
    for grid in ("ercot", "caiso", "nyiso", "isone", "spp"):
        G = [r for r in rows if r["grid"] == grid]
        years = {r["period"]: r for r in G if r["kind"] == "year"}
        ys = sorted(years)
        if grid == "ercot":
            first, last = ys[0], max(y for y in ys if y < ys[-1])
        else:
            full = [y for y in ys if years[y]["full_year"]]
            first, last = (full[0], full[-1]) if full else (None, None)
        n[f"{grid}_multiple_first"] = years[first]["worst_interval_multiple"] if first else None
        n[f"{grid}_multiple_last"] = years[last]["worst_interval_multiple"] if last else None
        R = [r for r in G if r["kind"] == "month" and r["battery_mw"] is not None and r["load_mean_mw"] is not None
             and r["henry_hub_usd_mmbtu"] is not None and r["worst_interval_multiple"] is not None]
        n[f"{grid}_reg_n"] = len(R)
        if len(R) <= 17:
            continue
        X = [[1.0, r["battery_mw"] / 1000.0, r["load_mean_mw"] / 1000.0, r["henry_hub_usd_mmbtu"]]
             + [1.0 if int(r["period"][5:7]) == m else 0.0 for m in range(2, 13)] for r in R]
        for col, short in (("worst_interval_multiple", "multiple"), ("hours_ge_1000", "hours1000"), ("hours_top1pct", "top1")):
            f = hc1([r[col] for r in R], X)
            n[f"{grid}_reg_{short}_coef"], n[f"{grid}_reg_{short}_se"], n[f"{grid}_reg_{short}_p"] = f["coef"][1], f["se"][1], f["p"][1]
            n[f"{grid}_reg_{short}_r2"] = f["r2"]
    return n


def batteries_curtailment(rows):
    y = [r["curtailed_mwh"] for r in rows]
    ch = [r["charging_mwh"] / 1000.0 for r in rows]
    so = [r["solar_mwh"] / 1000.0 for r in rows]
    months = sorted({r["month"] for r in rows})
    dums = [[1.0 if r["month"] == m else 0.0 for m in months[1:]] for r in rows]
    fits = {"charging": hc1(y, [[1.0, c] for c in ch]),
            "charging_solar": hc1(y, [[1.0, c, s] for c, s in zip(ch, so)]),
            "charging_solar_month": hc1(y, [[1.0, c, s] + d for c, s, d in zip(ch, so, dums)])}
    cu, chm = np.array(y, float), np.array([r["charging_mwh"] for r in rows], float)
    med = float(np.median(chm))
    n = {"n_days": len(rows), "n_months": len(months), "median_charging_mwh": med,
         "curtailed_low_charging_days": float(cu[chm <= med].mean()), "curtailed_high_charging_days": float(cu[chm > med].mean()),
         "n_low_days": int((chm <= med).sum()), "n_high_days": int((chm > med).sum()),
         "mean_curtailed_mwh": float(cu.mean()), "mean_charging_mwh": float(chm.mean())}
    for k, f in fits.items():
        n[f"{k}_coef"], n[f"{k}_se"], n[f"{k}_p"], n[f"{k}_r2"], n[f"{k}_n"] = f["coef"][1], f["se"][1], f["p"][1], f["r2"], f["n"]
    f = fits["charging_solar_month"]
    n["solar_coef"], n["solar_se"], n["solar_p"] = f["coef"][2], f["se"][2], f["p"][2]
    r = float(np.corrcoef(cu, chm)[0, 1])
    n["corr_curtailed_charging"], n["corr_squared"] = r, r * r
    return n


def batteries_curtailment_hourly(rows):
    """Curtailed MW on charging MW, then with net load and its square, then with hour and month fixed effects;
    clustered by Pacific day. Charging enters in GW, as the card's fit, and its coefficient is given per MW."""
    y = np.array([r["curtailed_mw"] for r in rows], float)
    ch = np.array([r["charging_mw"] for r in rows], float)
    nl = np.array([r["net_load_mw"] for r in rows], float) / 1000.0
    days = [r["day"] for r in rows]
    months = sorted({d[:7] for d in days})
    one = np.ones(len(rows))
    hours = np.array([r["hour"] for r in rows])
    hd = (hours[:, None] == np.arange(1, 24)[None, :]).astype(float)
    mi = {m: i for i, m in enumerate(months)}
    mcode = np.array([mi[d[:7]] for d in days])
    md = (mcode[:, None] == np.arange(1, len(months))[None, :]).astype(float)
    chg = ch / 1000.0
    nlb = nl - y / 1000.0
    fits = {"charging": clustered(y, np.column_stack([one, chg]), days),
            "charging_netload": clustered(y, np.column_stack([one, chg, nl, nl ** 2]), days),
            "charging_netload_fe": clustered(y, np.column_stack([one, chg, nl, nl ** 2, hd, md]), days),
            "before_curtailment": clustered(y, np.column_stack([one, chg, nlb, nlb ** 2, hd, md]), days)}
    r = float(np.corrcoef(y, ch)[0, 1])
    n = {"n_hours": len(rows), "n_days": len(set(days)), "n_months": len(months), "clusters": fits["charging_netload_fe"]["clusters"],
         "corr_curtailed_charging": r, "corr_squared": r * r, "charging_hours": int((ch > 0).sum()),
         "curtailed_mwh_all": float(y.sum()), "mean_curtailed_mw": float(y.mean()), "mean_charging_mw": float(ch.mean())}
    for k, f in fits.items():
        n[f"{k}_coef"], n[f"{k}_se"], n[f"{k}_p"], n[f"{k}_r2"] = f["coef"][1] / 1000.0, f["se"][1] / 1000.0, f["p"][1], f["r2"]
        if k != "before_curtailment":
            n[f"{k}_n"] = f["n"]
    return n


def impact_study(rows):
    win = [r for r in rows if r["in_window"] == 1 and r["diff"] is not None]
    pre, post = [r for r in win if r["after"] == 0], [r for r in win if r["after"] == 1]
    mean = lambda rs, k: float(np.mean([r[k] for r in rs]))  # noqa: E731
    n = {"n_pre": len(pre), "n_post": len(post), "n": len(win), "series_pre": mean(pre, "series_value"), "series_post": mean(post, "series_value"),
         "control_pre": mean(pre, "control_value"), "control_post": mean(post, "control_value")}
    n["did"] = (n["series_post"] - n["series_pre"]) - (n["control_post"] - n["control_pre"])
    f = newey([r["diff"] for r in win], [[1.0, float(r["after"])] for r in win])
    n.update({"reg_const": f["coef"][0], "reg_const_se": f["se"][0], "reg_const_p": f["p"][0], "reg_did": f["coef"][1], "reg_did_se": f["se"][1],
              "reg_did_p": f["p"][1], "reg_n": f["n"], "reg_lags": f["lags"], "reg_r2": f["r2"]})
    lead = [r for r in rows if r["after"] == 0 and r["diff"] is not None]
    if len(lead) >= 7:
        g = newey([r["diff"] for r in lead], [[1.0, float(r["t"])] for r in lead])
        n.update({"pre_slope": g["coef"][1], "pre_slope_se": g["se"][1], "pre_slope_p": g["p"][1]})
    return n


def gas_sets_price(rows):
    years = sorted({r["year"] for r in rows})
    first, last = years[0], max(y for y in years if y < years[-1])
    at = {(r["grid"], r["year"]): r for r in rows}
    k = "share_below_hr7"
    n = {"first_year": first, "last_full_year": last, "this_year": years[-1], "n_cells": len(rows), "n_cells_held": sum(1 for r in rows if r[k] is not None)}
    for grid in ("ercot", "isone"):
        n[f"{grid}_first"], n[f"{grid}_last"] = at[(grid, first)][k], at[(grid, last)][k]
    n["ercot_last_hr6p5"], n["ercot_last_hr8"] = at[("ercot", last)]["share_below_hr6p5"], at[("ercot", last)]["share_below_hr8"]
    for grid in ("ercot", "caiso", "nyiso", "spp"):
        n[f"{grid}_this"] = (at.get((grid, years[-1])) or {}).get(k)
    return n


def negative_prices_west(rows):
    years = sorted({r["year"] for r in rows})
    first, this = years[0], years[-1]
    last = max(y for y in years if y < this)
    at = {(r["hub"], r["year"]): r for r in rows}
    n = {"first_year": first, "last_full_year": last, "this_year": this}
    for hub in sorted({r["hub"] for r in rows}):
        for tag, y in (("first", first), ("last", last), ("this", this)):
            r = at.get((hub, y))
            n[f"{hub}_{tag}"] = r["negative_hours"] if r else None
            n[f"{hub}_{tag}_share"] = r["share_pct"] if r else None
        held = [r for r in rows if r["hub"] == hub and r["negative_hours"] is not None and r["year"] < this]
        peak = max(held, key=lambda r: r["negative_hours"], default=None)
        n[f"{hub}_peak_year"], n[f"{hub}_peak"] = (peak["year"], peak["negative_hours"]) if peak else (None, None)
    return n


def peak_hour_grids(rows):
    years = sorted({r["year"] for r in rows})
    this = years[-1]
    at = {(r["grid"], r["year"], r["hour"]): r for r in rows}
    n = {}
    for grid in sorted({r["grid"] for r in rows}):
        held = [y for y in years if (at.get((grid, y, 0)) or {}).get("n_days")]
        for tag, y in (("first", held[0] if held else None), ("last", max((v for v in held if v < this), default=None))):
            r = at.get((grid, y, 0)) if y is not None else None
            n[f"{grid}_{tag}_year"] = y
            for col, short in (("median_peak_hour", "median_hour"), ("share_evening_pct", "evening_pct"), ("share_midday_pct", "midday_pct"), ("n_days", "days")):
                n[f"{grid}_{tag}_{short}"] = r[col] if r else None
            if r:
                top = max((at[(grid, y, h)] for h in range(24)), key=lambda x: x["share_days_pct"] or 0)
                n[f"{grid}_{tag}_modal_hour"], n[f"{grid}_{tag}_modal_pct"] = top["hour"], top["share_days_pct"]
    return n


def peak_hour_moved(rows):
    """Session 582: the card's numbers_from_rows (warehouse/analysis/findings/peak_hour_moved.py), grid by grid in the
    file's order: the first year held, the last full year held and this year, each with its median peak hour, its
    shares of days peaking in the evening and at midday, its days, its solar MW at year end and its modal hour."""
    years = sorted({r["year"] for r in rows})
    first, this = years[0], years[-1]
    last_full = max(y for y in years if y < this)
    at = {(r["grid"], r["year"], r["hour"]): r for r in rows}
    n = {"first_year": first, "last_full_year": last_full, "this_year": this}
    for grid in dict.fromkeys(r["grid"] for r in rows):
        held = [y for y in years if (at.get((grid, y, 0)) or {}).get("n_days")]
        n[f"{grid}_first_held_year"] = held[0] if held else None
        n[f"{grid}_last_full_held_year"] = max((y for y in held if y < this), default=None)
        for tag, y in (("first", n[f"{grid}_first_held_year"]), ("last", n[f"{grid}_last_full_held_year"]), ("this", this if this in held else None)):
            r = at.get((grid, y, 0)) if y is not None else None
            n[f"{grid}_{tag}_year"] = y
            for col, short in (("median_peak_hour", "median_hour"), ("share_evening_pct", "evening_pct"), ("share_midday_pct", "midday_pct"),
                               ("n_days", "days"), ("solar_mw_yearend", "solar_mw")):
                n[f"{grid}_{tag}_{short}"] = r[col] if r else None
            if r:
                top = max((x for x in rows if x["grid"] == grid and x["year"] == y), key=lambda x: x["share_days_pct"] or 0)
                n[f"{grid}_{tag}_modal_hour"], n[f"{grid}_{tag}_modal_pct"] = top["hour"], top["share_days_pct"]
            else:
                n[f"{grid}_{tag}_modal_hour"] = n[f"{grid}_{tag}_modal_pct"] = None
        n[f"{grid}_solar_mw_first_year"] = (at.get((grid, first, 0)) or {}).get("solar_mw_yearend")
        n[f"{grid}_solar_mw_last_full_year"] = (at.get((grid, last_full, 0)) or {}).get("solar_mw_yearend")
    return n


def queue_divorce(rows):
    a = next(r for r in rows if r["technology"] == "All technologies")
    by = {r["technology"]: r for r in rows}
    n = {k: a[k] for k in ("requested_gw", "projects", "withdrawn_pct", "operational_pct", "active_pct", "suspended_pct", "withdrawn_gw", "operational_gw")}
    n["cdc_ratio_pct"] = a["cdc_divorce_rate_per_1000"] / a["cdc_marriage_rate_per_1000"] * 100.0
    n["queue_over_cdc"] = n["withdrawn_pct"] / n["cdc_ratio_pct"]
    for tech, key in (("Gas", "gas"), ("Solar", "solar"), ("Wind", "wind")):
        n[f"{key}_withdrawn_pct"] = by[tech]["withdrawn_pct"]
    return n


def who_rescues_whom(rows):
    to_exp = [r for r in rows if r["flip"] == "import_to_export"]
    to_imp = [r for r in rows if r["flip"] == "export_to_import"]
    grid = next(r for r in rows if r["event_grid"])
    top = rows[0]   # the card reads the first row: the file is written largest swing first, as the do-file's gsort -swing_mwh_day
    return {"n_bas": len(rows), "n_to_export": len(to_exp), "n_to_import": len(to_imp), "n_same": sum(1 for r in rows if r["flip"] == "same"),
            "n_small": sum(1 for r in rows if r["flip"] == "small"), "grid_name": grid["name"],
            "grid_baseline": grid["baseline_net_mwh_day"], "grid_event": grid["event_net_mwh_day"],
            "big_exp_name": max(to_exp, key=lambda r: r["event_net_mwh_day"])["name"] if to_exp else None,
            "big_imp_name": min(to_imp, key=lambda r: r["event_net_mwh_day"])["name"] if to_imp else None,
            "biggest_swing_name": top["name"], "biggest_swing": top["swing_mwh_day"]}


# ---------------------------------------------------------------- the run
def same(ours, theirs):
    if isinstance(ours, str) or isinstance(theirs, str) or ours is None or theirs is None:
        return ours == theirs
    a, b = float(ours), float(theirs)
    if math.isnan(a) or math.isnan(b):
        return math.isnan(a) and math.isnan(b)
    return abs(a - b) <= 1e-7 * max(abs(a), abs(b)) or abs(a - b) <= 1e-12   # relative, so that a p-value of 1e-74 is held to its digits


def main(argv):
    args = list(argv)
    json_dir = None
    if "--json" in args:
        i = args.index("--json")
        if i + 1 >= len(args):
            print("usage: erw_2026_research_replication.py [folder] [--json <dir>]")
            return 2
        json_dir = args[i + 1]
        del args[i:i + 2]
    folder = args[0] if args else os.path.dirname(os.path.abspath(__file__))
    compared = differ = 0
    for card, csv_name in CARDS:
        path = os.path.join(folder, csv_name)
        if not os.path.exists(path):
            print(f"missing: {path}")
            return 2
        figures = globals()[card](read_rows(path))
        card_numbers = None
        if json_dir:
            with open(os.path.join(json_dir, card + ".json"), encoding="utf-8") as f:
                card_numbers = json.load(f)["numbers"]
        print(f"== {card} ({csv_name})")
        for key, v in figures.items():
            if card_numbers is None:
                print(f"{card}.{key} = {v}")
            elif key not in card_numbers:
                print(f"{card}.{key} = {v}  (not a figure of the card's JSON)")
            else:
                compared += 1
                ok = same(v, card_numbers[key])
                differ += 0 if ok else 1
                print(f"{'same' if ok else 'DIFFERENT'}  {card}.{key} = {v}; the card: {card_numbers[key]}")
    if json_dir:
        print(f"{compared} figures compared with the cards' JSON, {differ} different")
        return 1 if differ else 0
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
