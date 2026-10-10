"""Finding: "By how much do batteries cut curtailment" (session 174, econometric).

CAISO's daily curtailment (solar plus wind, MWh) on the day's battery charging (MWh), controlling for solar output and
the month: an ordinary least squares regression with HC1 standard errors, over the days the warehouse holds all three
series (CAISO's five-minute battery series begins on 2025-08-24). Three specifications: charging alone; charging with
solar generation; charging with solar generation and month-of-sample fixed effects. The effect is stated in plain words,
as an association in a before-and-after with controls, never as a cause: on a sunny day both charging and curtailment
rise, which is why solar output is held fixed; what the regression cannot separate is the batteries' own dispatch from
the market conditions that call for it.

Session 182: the Pearson correlation coefficient r of daily curtailment with daily charging is reported beside R2 (its
square is the R2 of the charging-alone fit), in the numbers, the paragraph, the footnote, the CSV's header and the
do-file; the do-file now reads the CSV past its four comment lines. The hourly card is batteries_curtailment_hourly.

Tables: caiso_curtailment_daily (CAISO's production and curtailment report), caiso_battery_storage (CAISO Today's Outlook,
batteries MW every five minutes; negative is charging), caiso_fuel_supply (Today's Outlook, solar MW by hour).
"""

import os

import numpy as np
import pandas as pd

from findings_common import METHOD_URL, NoData, callout, do_destring, do_file, do_sentinels, fmt, now_iso, ols_hc1, read_table, to_utc

NAME = "batteries_curtailment"
TITLE = "BY HOW MUCH DO BATTERIES CUT CURTAILMENT"
KIND = "econometric"
INPUTS = {
    "curtailed": {"label": "Curtailment counted", "default": "solar_and_wind", "choices": ["solar_and_wind", "solar_only"],
                  "words": {"solar_and_wind": "solar and wind", "solar_only": "solar only"}},
    "first_month": {"label": "First month", "default": "2025-08", "choices": ["2025-08", "2026-01"]},
}
TABLES = ["caiso_curtailment_daily", "caiso_battery_storage", "caiso_fuel_supply"]
CSV_NAME = "erw_2026_caiso_curtailment_batteries.csv"
TZ = "America/Los_Angeles"


def compute(params, in_dir=None):
    which = str(params.get("curtailed", "solar_and_wind"))
    first_month = str(params.get("first_month", "2025-08"))
    cur = read_table("caiso_curtailment_daily", in_dir, usecols=["ts_utc", "variable", "value"],
                     keep=lambda c: c["variable"].isin(["curtailed_solar_mwh", "curtailed_wind_mwh"]) & (c["ts_utc"] >= "2025-08-01"))
    if cur.empty:
        raise NoData("caiso_curtailment_daily has no rows from 2025-08")
    cur["value"] = cur["value"].astype(float)
    cur["day"] = cur["ts_utc"].str[:10]
    cw = cur.pivot_table(index="day", columns="variable", values="value", aggfunc="first")
    bat = read_table("caiso_battery_storage", in_dir, usecols=["ts_utc", "variable", "value"], keep=lambda c: c["variable"] == "batteries_mw")
    if bat.empty:
        raise NoData("caiso_battery_storage has no batteries_mw rows")
    bat["value"] = bat["value"].astype(float)
    bt = to_utc(bat["ts_utc"]).dt.tz_convert(TZ)
    bat["day"] = bt.dt.strftime("%Y-%m-%d")
    bat["charge_mwh"] = np.where(bat["value"] < 0, -bat["value"], 0.0) * (5 / 60)
    bat["discharge_mwh"] = np.where(bat["value"] > 0, bat["value"], 0.0) * (5 / 60)
    bd = bat.groupby("day").agg(charging_mwh=("charge_mwh", "sum"), discharging_mwh=("discharge_mwh", "sum"), n_intervals=("value", "size"))
    sol = read_table("caiso_fuel_supply", in_dir, usecols=["ts_utc", "variable", "value"], keep=lambda c: c["variable"] == "solar_mw")
    if sol.empty:
        raise NoData("caiso_fuel_supply has no solar_mw rows")
    sol["value"] = sol["value"].astype(float)
    st = to_utc(sol["ts_utc"]).dt.tz_convert(TZ)
    sol["day"] = st.dt.strftime("%Y-%m-%d")
    sd = sol.groupby("day").agg(solar_mwh=("value", "sum"), n_hours=("value", "size"))
    df = cw.join(bd, how="inner").join(sd, how="inner")
    df = df[(df.index >= first_month + "-01") & (df["n_intervals"] >= 276) & (df["n_hours"] >= 23)]
    if len(df) < 30:
        raise NoData(f"only {len(df)} days hold curtailment, charging and solar together")
    df["curtailed_mwh"] = df["curtailed_solar_mwh"] + (df["curtailed_wind_mwh"] if which == "solar_and_wind" else 0.0)
    rows = [{"day": d, "month": d[:7], "curtailed_mwh": float(r["curtailed_mwh"]), "curtailed_solar_mwh": float(r["curtailed_solar_mwh"]),
             "curtailed_wind_mwh": float(r["curtailed_wind_mwh"]), "charging_mwh": float(r["charging_mwh"]), "discharging_mwh": float(r["discharging_mwh"]),
             "solar_mwh": float(r["solar_mwh"]), "battery_intervals": int(r["n_intervals"]), "solar_hours": int(r["n_hours"])}
            for d, r in df.sort_index().iterrows()]
    meta = {"curtailed": which, "first_month": first_month, "first_day": rows[0]["day"], "last_day": rows[-1]["day"], "n_days": len(rows)}
    return rows, meta


def fit(rows):
    """The three regressions, curtailment (MWh) on charging (GWh), with HC1 standard errors."""
    y = np.array([r["curtailed_mwh"] for r in rows], float)
    ch = np.array([r["charging_mwh"] for r in rows], float) / 1000.0
    so = np.array([r["solar_mwh"] for r in rows], float) / 1000.0
    months = sorted({r["month"] for r in rows})
    dums = np.array([[1.0 if r["month"] == m else 0.0 for m in months[1:]] for r in rows])
    one = np.ones(len(rows))
    out = {}
    out["charging"] = ols_hc1(y, np.column_stack([one, ch]), ["const", "charging_gwh"])
    out["charging_solar"] = ols_hc1(y, np.column_stack([one, ch, so]), ["const", "charging_gwh", "solar_gwh"])
    out["charging_solar_month"] = ols_hc1(y, np.column_stack([one, ch, so, dums]), ["const", "charging_gwh", "solar_gwh"] + [f"m_{m}" for m in months[1:]])
    return out, months


def numbers_from_rows(rows, params=None):
    f, months = fit(rows)
    ch = np.array([r["charging_mwh"] for r in rows], float)
    cu = np.array([r["curtailed_mwh"] for r in rows], float)
    med = float(np.median(ch))
    lo, hi = cu[ch <= med], cu[ch > med]
    n = {"n_days": len(rows), "n_months": len(months), "first_day": rows[0]["day"], "last_day": rows[-1]["day"],
         "mean_curtailed_mwh": float(cu.mean()), "mean_charging_mwh": float(ch.mean()), "mean_solar_mwh": float(np.mean([r["solar_mwh"] for r in rows])),
         "median_charging_mwh": med, "curtailed_low_charging_days": float(lo.mean()), "curtailed_high_charging_days": float(hi.mean()),
         "n_low_days": int(len(lo)), "n_high_days": int(len(hi)), "max_charging_mwh": float(ch.max()), "max_curtailed_mwh": float(cu.max())}
    for k in ("charging", "charging_solar", "charging_solar_month"):
        c = f[k]["coef"]["charging_gwh"]
        n[f"{k}_coef"], n[f"{k}_se"], n[f"{k}_p"], n[f"{k}_r2"], n[f"{k}_n"] = c["coef"], c["se"], c["p"], f[k]["r2"], f[k]["n"]
    s = f["charging_solar_month"]["coef"]["solar_gwh"]
    n["solar_coef"], n["solar_se"], n["solar_p"] = s["coef"], s["se"], s["p"]
    r = float(np.corrcoef(cu, ch)[0, 1])   # session 182: Pearson's r, curtailment with charging, raw
    n["corr_curtailed_charging"], n["corr_squared"] = r, r * r
    return n


def chart(rows, n):
    b = n["charging_coef"]
    a = float(np.mean([r["curtailed_mwh"] for r in rows]) - b * np.mean([r["charging_mwh"] for r in rows]) / 1000.0)
    xs = [r["charging_mwh"] / 1000.0 for r in rows]
    return {"kind": "scatter", "x": [], "x_label": "battery charging, GWh in the day",
            "series": [{"name": "A day", "type": "line", "unit": "GWh curtailed", "values": []}],
            "points": [{"x": r["charging_mwh"] / 1000.0, "y": r["curtailed_mwh"] / 1000.0, "label": r["day"], "solar": r["solar_mwh"] / 1000.0} for r in rows],
            "fit": {"name": "Fit, charging alone", "intercept": a / 1000.0, "slope": b / 1000.0, "x_min": min(xs), "x_max": max(xs)},
            "y_left_label": "curtailed, GWh in the day", "decimals": 2}


def card(rows, params, meta):
    n = numbers_from_rows(rows, params)
    b, se, p = n["charging_solar_month_coef"], n["charging_solar_month_se"], n["charging_solar_month_p"]
    b0, b1 = n["charging_coef"], n["charging_solar_coef"]
    if p < 0.05 and b < 0:
        sub = "Days with more charging see less curtailment, solar and month held fixed, and the estimate is not noise"
        words = (f"each extra GWh a day of charging goes with {fmt(-b, 0)} MWh less curtailment, solar output and the month held fixed "
                 f"(standard error {fmt(se, 0)}, p {fmt(p, 3)}): an association, not a measured cause")
    elif p < 0.05 and b > 0:
        sub = "Days with more charging see more curtailment, even with solar and the month held fixed"
        words = (f"each extra GWh a day of charging goes with {fmt(b, 0)} MWh more curtailment, solar output and the month held fixed "
                 f"(standard error {fmt(se, 0)}, p {fmt(p, 3)}): the batteries charge on the days the grid has most to spare")
    else:
        sub = "With solar and the month held fixed, the data cannot pin curtailment on the batteries either way"
        words = (f"each extra GWh a day of charging goes with {fmt(b, 0)} MWh of curtailment (standard error {fmt(se, 0)}, p {fmt(p, 3)}): "
                 "an estimate that spans zero once solar output and the month are held fixed")
    why = (f"Over {fmt(n['n_days'], 0)} days from {n['first_day']} to {n['last_day']}, CAISO curtailed {fmt(n['mean_curtailed_mwh'], 0)} MWh a day on average while its "
           f"batteries charged {fmt(n['mean_charging_mwh'], 0)} MWh a day. On the days with charging at or below the median ({fmt(n['median_charging_mwh'], 0)} MWh), "
           f"curtailment averaged {fmt(n['curtailed_low_charging_days'], 0)} MWh; above it, {fmt(n['curtailed_high_charging_days'], 0)}. Day by day the two correlate at "
           f"r = {fmt(n['corr_curtailed_charging'], 2)} (R2 {fmt(n['charging_r2'], 2)}, charging alone). Charging alone goes with "
           f"{fmt(b0, 0)} MWh of curtailment per GWh charged; with solar output held fixed, {fmt(b1, 0)}; with the month too, {fmt(b, 0)} "
           f"(standard error {fmt(se, 0)}, p {fmt(p, 3)}, R2 {fmt(n['charging_solar_month_r2'], 2)}). Solar output itself goes with {fmt(n['solar_coef'], 0)} MWh of "
           f"curtailment per GWh (standard error {fmt(n['solar_se'], 0)}). The raw association and the controlled one can differ in sign: sunny spring days bring both "
           "charging and curtailment, so the question is what charging adds on a day like any other, and that is the third estimate. What it cannot separate is the "
           "batteries' dispatch from the prices that call for it.")
    foot = (f"Data: caiso_curtailment_daily (CAISO production and curtailment report, MWh a day; 'solar and wind' is curtailed_solar_mwh plus curtailed_wind_mwh, "
            f"'solar only' the first), caiso_battery_storage (Today's Outlook, batteries MW every 5 minutes; charging is the negative values summed times 5/60, "
            f"a day needs at least 276 of its 288 intervals), caiso_fuel_supply (Today's Outlook, solar MW by hour summed to MWh, at least 23 hours), all on "
            f"{TZ} days, {n['first_day']} to {n['last_day']}, {fmt(n['n_days'], 0)} days in {fmt(n['n_months'], 0)} calendar months (the battery series begins "
            "2025-08-24). Regressions: OLS of daily curtailment (MWh) on charging (GWh); on charging and solar (GWh); on both and month-of-sample dummies; "
            "HC1 standard errors (Stata's vce(robust)), p from Student's t. The split at the median charging day is a plain comparison of means. r is the Pearson correlation of daily curtailment "
            f"with daily charging over these days, {fmt(n['corr_curtailed_charging'], 3)}; its square, {fmt(n['corr_squared'], 3)}, is the R2 of the charging-alone fit. "
            "No instrument, "
            "no event window: an association.")
    table = {"columns": ["Specification", "Per GWh charged (MWh curtailed)", "SE (HC1)", "p", "Days", "R2"],
             "rows": [{"measure": "charging alone", "coef_per_gw": n["charging_coef"], "se": n["charging_se"], "p": n["charging_p"], "n": n["charging_n"], "r2": n["charging_r2"]},
                      {"measure": "charging, solar output held fixed", "coef_per_gw": n["charging_solar_coef"], "se": n["charging_solar_se"], "p": n["charging_solar_p"], "n": n["charging_solar_n"], "r2": n["charging_solar_r2"]},
                      {"measure": "charging, solar output and month held fixed", "coef_per_gw": b, "se": se, "p": p, "n": n["charging_solar_month_n"], "r2": n["charging_solar_month_r2"]}],
             "in_words": words}
    return {
        "id": NAME, "title": TITLE, "kind": KIND, "subtitle": sub,
        "params": {"curtailed": meta["curtailed"], "first_month": meta["first_month"]},
        "inputs_words": {"curtailed": INPUTS["curtailed"]["words"][meta["curtailed"]], "first_month": meta["first_month"]},
        "chart": chart(rows, n),
        "callouts": [
            callout("Curtailment on low and high charging days, MWh a day", "at or below the median", f"{fmt(n['curtailed_low_charging_days'], 0)}", "above it", f"{fmt(n['curtailed_high_charging_days'], 0)}"),
            callout("MWh curtailed per GWh charged", "charging alone", f"{fmt(b0, 0)}", "solar and month fixed", f"{fmt(b, 0)}"),
            callout("The controlled estimate", "standard error", f"{fmt(se, 0)}", "R2", f"{fmt(n['charging_solar_month_r2'], 2)}"),
        ],
        "why": why, "footnote": foot, "numbers": n, "effect_table": table,
        "source_line": "Source: CAISO production and curtailment report; CAISO Today's Outlook (storage, fuel source); ERW tables " + ", ".join(TABLES) + ".",
        "tables": TABLES, "computed_at": now_iso(), "method": METHOD_URL,
        "csv_header": [f"Energy Research Warehouse (ERW): finding {NAME}, {TITLE}", f"Computed {now_iso()} by warehouse/analysis/findings/{NAME}.py; method {METHOD_URL}",
                       "Rows: one per Pacific day: curtailed MWh (as counted), solar and wind curtailed, battery charging and discharging MWh, solar generation MWh, intervals and hours held",
                       "Sources: " + ", ".join(TABLES) + f". Pearson r of curtailed_mwh with charging_mwh over these rows: {n['corr_curtailed_charging']:.6f} "
                       f"(r squared {n['corr_squared']:.6f}, the R2 of the charging-alone fit)"],
    }


def stata(params):
    V = ["curtailed_mwh", "curtailed_solar_mwh", "curtailed_wind_mwh", "charging_mwh", "discharging_mwh", "solar_mwh", "battery_intervals", "solar_hours"]
    return do_file([
        f"* ERW finding {NAME}: {TITLE}. Reproduces the card's correlation and three regressions from {CSV_NAME}.",
        "* The CSV begins with four comment lines: the names are on line 5 and the data begin on line 6 (session 182).",
        "clear all",
        f'import delimited "{CSV_NAME}", varnames(5) rowrange(6) stringcols(_all) clear',
        *do_destring(V),
        *do_sentinels(V),
        "gen charging_gwh = charging_mwh / 1000",
        "gen solar_gwh = solar_mwh / 1000",
        "encode month, gen(month_id)",
        "correlate curtailed_mwh charging_mwh",
        "regress curtailed_mwh charging_gwh, vce(robust)",
        "regress curtailed_mwh charging_gwh solar_gwh, vce(robust)",
        "regress curtailed_mwh charging_gwh solar_gwh i.month_id, vce(robust)",
        "summarize charging_mwh, detail",
        "gen high_charging = charging_mwh > r(p50)",
        "tabstat curtailed_mwh, by(high_charging) statistics(mean n) format(%9.0f)",
    ])


SOURCE_PATH = os.path.abspath(__file__)
