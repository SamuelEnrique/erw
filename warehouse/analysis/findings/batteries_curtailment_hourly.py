"""Finding: "By how much do batteries cut curtailment, hour by hour" (session 182, econometric). CAISO, hourly.

The daily card (batteries_curtailment) asks the question of days; this one asks it within the day. For every hour CAISO's
fuel supply table holds from 2019: curtailment (solar plus wind, MW over the hour), battery charging (MW over the hour)
and net load (demand less wind and solar). Three things are computed.

1. What net load alone predicts. Ordinary least squares of hourly curtailment on net load in GW, its square, 23
   hour-of-day dummies and month-of-sample dummies. The residual (observed less predicted) is averaged over the hours
   the fleet charges, by year.
2. The charging coefficient. The same regression with charging MW added, and two shorter ones (charging alone; charging
   with net load and its square). Standard errors are cluster-robust by Pacific day, with Stata's small-sample factor
   (G / (G - 1)) * ((N - 1) / (N - K)) and p from Student's t on G - 1 degrees of freedom: hours of one day share the
   day's weather, outages and prices, so their errors are not independent, and a day is the natural cluster. The Pearson
   correlation of hourly curtailment with charging is reported beside each R2.
3. The fleet-saturation reading. Hours in which charging is at the fleet's ceiling while curtailment is still on. The
   ceiling is measured two ways and both are shown: the largest hourly charging of the 30 Pacific days before the hour's
   day, and the fleet's nameplate MW of that month from EIA-860M. An hour is at the ceiling when charging is at or above
   the chosen percent of it (90 by default).

What the coefficient is and is not: batteries charge when prices are low, and prices are low when solar is being turned
down, so charging and curtailment keep the same hours by construction of the market. The coefficient is the association
of the two with net load, the hour and the month held fixed. It is not the curtailment batteries prevent, which would
need to know what curtailment would have been without them.

Tables: caiso_curtailment_intervals (CAISO production and curtailments workbooks, 5-minute MW to 2025-12-31; Daily
Renewable Report, hourly MWh from 2026-01-01; a listed interval is a curtailment, an interval not listed on a covered
day is zero), caiso_fuel_supply_history and caiso_fuel_supply (Today's Outlook, hourly MW by source; batteries positive
discharging, negative charging), storage_buildout_monthly (iso:caiso battery_operating_mw, EIA-860M).
"""

import os

import numpy as np
import pandas as pd

from findings_common import METHOD_URL, NoData, callout, do_destring, do_file, do_sentinels, fmt, now_iso, read_table, to_utc

NAME = "batteries_curtailment_hourly"
DATA_MACHINE_ONLY = True  # its histories are not restored on the Roundup's runner (run_finding.py --tables)
TITLE = "BY HOW MUCH DO BATTERIES CUT CURTAILMENT, HOUR BY HOUR"
KIND = "econometric"
INPUTS = {
    "first_year": {"label": "First year", "default": 2019, "choices": [2019, 2021, 2023]},
    "ceiling_pct": {"label": "At the ceiling from (percent of it)", "default": 90, "choices": [90, 95]},
}
TABLES = ["caiso_curtailment_intervals", "caiso_fuel_supply_history", "caiso_fuel_supply", "storage_buildout_monthly"]
CSV_NAME = "erw_2026_caiso_curtailment_hourly.csv"
TZ = "America/Los_Angeles"
SOURCES = ["solar_mw", "wind_mw", "geothermal_mw", "biomass_mw", "biogas_mw", "small_hydro_mw", "coal_mw", "nuclear_mw",
           "natural_gas_mw", "large_hydro_mw", "batteries_mw", "imports_mw", "other_mw"]
TRAIL_DAYS = 30        # the trailing window of the observed ceiling, Pacific days before the hour's day
TRAIL_MIN_DAYS = 20    # of which this many must be held
CURTAILED_ON = 1.0     # MW: curtailment counts as on in an hour from 1 MW
GW_CHARGING = 1000.0   # MW: the first year whose largest charging hour reached 1 GW is the callout's "before"
COLUMNS = ["day", "hour", "curtailed_mw", "charging_mw", "net_load_mw", "fleet_mw", "trail_max_charging_mw"]


def curtailment_hours(in_dir):
    """Curtailed MWh by UTC hour (solar plus wind), the Pacific days the table covers, and its own day totals."""
    ci = read_table("caiso_curtailment_intervals", in_dir, usecols=["variable", "ts_utc", "value", "freq"])
    if ci.empty:
        raise NoData("caiso_curtailment_intervals has no rows")
    ci["value"] = ci["value"].astype(float)
    days = ci[ci["freq"] == "P1D"]
    d10 = days["ts_utc"].str[:10]
    covered = set(d10[days["variable"] == "curtailed_solar_day_mwh"]) & set(d10[days["variable"] == "curtailed_wind_day_mwh"])
    day_total = days.groupby(d10)["value"].sum().to_dict()
    iv = ci[ci["freq"].isin(["PT5M", "PT1H"])].copy()
    iv["mwh"] = np.where(iv["freq"] == "PT5M", iv["value"] * (5 / 60), iv["value"])
    iv["hour_utc"] = to_utc(iv["ts_utc"]).dt.floor("h")
    return iv.groupby("hour_utc")["mwh"].sum(), covered, day_total


def supply_hours(in_dir):
    """Today's Outlook by UTC hour, every source held: charging, demand (the sum of the sources) and net load."""
    parts = [read_table(t, in_dir, usecols=["variable", "ts_utc", "value"]) for t in ("caiso_fuel_supply_history", "caiso_fuel_supply")]
    f = pd.concat(parts, ignore_index=True).drop_duplicates(["variable", "ts_utc"], keep="last")
    f["value"] = pd.to_numeric(f["value"], errors="coerce")
    w = f.pivot(index="ts_utc", columns="variable", values="value")
    if any(s not in w.columns for s in SOURCES):
        raise NoData("the fuel supply tables do not hold every source")
    w = w.dropna(subset=SOURCES)
    w["demand_mw"] = w[SOURCES].sum(axis=1)
    w["net_load_mw"] = w["demand_mw"] - w["solar_mw"] - w["wind_mw"]
    w["charging_mw"] = (-w["batteries_mw"]).clip(lower=0.0)
    w["faulty"] = (w["natural_gas_mw"] < -100) | (w["wind_mw"] < -100) | (w["small_hydro_mw"] > 2000) | (w["demand_mw"] < 10000)
    return w


def fleet_by_month(in_dir):
    s = read_table("storage_buildout_monthly", in_dir, usecols=["entity", "variable", "ts_utc", "value"],
                   keep=lambda c: (c["entity"] == "iso:caiso") & (c["variable"] == "battery_operating_mw"))
    if s.empty:
        raise NoData("storage_buildout_monthly has no iso:caiso battery_operating_mw rows")
    return {t[:7]: float(v) for t, v in zip(s["ts_utc"], s["value"])}


def compute(params, in_dir=None):
    first_year = int(params.get("first_year", 2019))
    ceiling_pct = int(params.get("ceiling_pct", 90))
    cur, covered, day_total = curtailment_hours(in_dir)
    w = supply_hours(in_dir)
    fleet = fleet_by_month(in_dir)
    ts = to_utc(pd.Series(w.index))
    local = ts.dt.tz_convert(TZ)
    df = pd.DataFrame({"hour_utc": ts.to_numpy(), "day": local.dt.strftime("%Y-%m-%d").to_numpy(), "hour": local.dt.hour.to_numpy(),
                       "charging_mw": w["charging_mw"].to_numpy(), "net_load_mw": w["net_load_mw"].to_numpy(), "faulty": w["faulty"].to_numpy()})
    df["curtailed_mw"] = cur.reindex(pd.DatetimeIndex(ts)).fillna(0.0).to_numpy()   # an interval CAISO does not list had no curtailment
    df = df[df["day"].isin(covered) & (df["day"] >= f"{first_year}-01-01")].sort_values("hour_utc")
    per_day = df.groupby("day").agg(n=("hour", "size"), faulty=("faulty", "max"))
    short_days = sorted(per_day.index[per_day["n"] < 23])
    faulty_days = sorted(per_day.index[per_day["faulty"]])
    df = df[~df["day"].isin(set(short_days) | set(faulty_days))]
    if len(df) < 24 * 365:
        raise NoData(f"only {len(df)} hours hold curtailment and the fuel supply together")
    # the table's own day totals against the hours summed: the reconciliation the footnote reports
    hsum = df.groupby("day")["curtailed_mw"].sum()
    diff = np.array([abs(hsum[d] - day_total[d]) for d in hsum.index])
    # the observed ceiling: the largest charging hour of the 30 Pacific days before the day, 20 of them held
    dmax = df.groupby("day")["charging_mw"].max()
    cal = pd.date_range(dmax.index.min(), dmax.index.max(), freq="D").strftime("%Y-%m-%d")
    trail = dmax.reindex(cal).rolling(TRAIL_DAYS, min_periods=TRAIL_MIN_DAYS).max().shift(1)
    df["trail_max_charging_mw"] = df["day"].map(trail.to_dict())
    df["fleet_mw"] = df["day"].str[:7].map(fleet)
    rows = []
    for r in df.itertuples(index=False):
        rows.append({"day": r.day, "hour": int(r.hour), "curtailed_mw": round(float(r.curtailed_mw), 1), "charging_mw": round(float(r.charging_mw), 1),
                     "net_load_mw": round(float(r.net_load_mw), 1), "fleet_mw": None if pd.isna(r.fleet_mw) else round(float(r.fleet_mw), 1),
                     "trail_max_charging_mw": None if pd.isna(r.trail_max_charging_mw) else round(float(r.trail_max_charging_mw), 1)})
    meta = {"first_year": first_year, "ceiling_pct": ceiling_pct, "first_day": rows[0]["day"], "last_day": rows[-1]["day"], "n_hours": len(rows),
            "n_days": int(df["day"].nunique()), "days_short": len(short_days), "days_faulty": faulty_days, "fleet_last_month": max(fleet),
            "reconcile_days": int(len(diff)), "reconcile_max_abs_mwh": float(diff.max()), "reconcile_days_within_1_mwh": int((diff <= 1.0).sum()),
            "curtailment_last_day": max(covered), "supply_last_hour_utc": str(w.index.max())}
    return rows, meta


def ols_cluster(y, X, names, groups):
    """OLS with cluster-robust standard errors, as Stata's `regress, vce(cluster g)`: the sandwich with the clusters'
    summed scores, times (G / (G - 1)) * ((N - 1) / (N - K)); p from Student's t on G - 1 degrees of freedom."""
    from scipy import stats
    y = np.asarray(y, float)
    X = np.asarray(X, float)
    n, k = X.shape
    bread = np.linalg.inv(X.T @ X)
    beta = bread @ (X.T @ y)
    e = y - X @ beta
    codes, uniq = pd.factorize(np.asarray(groups), sort=True)
    order = np.argsort(codes, kind="stable")
    starts = np.flatnonzero(np.r_[True, np.diff(codes[order]) != 0])
    S = np.add.reduceat((X * e[:, None])[order], starts, axis=0)
    g = len(uniq)
    V = (g / (g - 1)) * ((n - 1) / (n - k)) * (bread @ (S.T @ S) @ bread)
    se = np.sqrt(np.diag(V))
    t = beta / se
    p = 2 * stats.t.sf(np.abs(t), g - 1)
    ss_tot = float(((y - y.mean()) ** 2).sum())
    return {"coef": {nm: {"coef": float(b), "se": float(s), "t": float(tt), "p": float(pp)} for nm, b, s, tt, pp in zip(names, beta, se, t, p)},
            "n": int(n), "k": int(k), "clusters": int(g), "r2": 1 - float((e ** 2).sum()) / ss_tot, "fitted": X @ beta, "se_kind": "cluster by day"}


def analyse(rows, params=None):
    """Everything the card states, from the data rows alone: the fits, the by-year table and the by-hour profile."""
    pct = int((params or {}).get("ceiling_pct", 90))
    df = pd.DataFrame(rows, columns=COLUMNS)
    for c in COLUMNS[1:]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["year"] = df["day"].str[:4].astype(int)
    df["month"] = df["day"].str[:7]
    y = df["curtailed_mw"].to_numpy(float)
    ch = df["charging_mw"].to_numpy(float)
    nl = df["net_load_mw"].to_numpy(float) / 1000.0
    one = np.ones(len(df))
    months = sorted(df["month"].unique())
    hd = (df["hour"].to_numpy()[:, None] == np.arange(1, 24)[None, :]).astype(float)
    mcode = pd.Categorical(df["month"], categories=months).codes
    md = (mcode[:, None] == np.arange(1, len(months))[None, :]).astype(float)
    days = df["day"].to_numpy()
    chg = ch / 1000.0   # GW inside the fit for a well-conditioned matrix; the coefficient is put back per MW below
    fe_names = [f"h{h:02d}" for h in range(1, 24)] + [f"m_{m}" for m in months[1:]]
    fits = {
        "charging": ols_cluster(y, np.column_stack([one, chg]), ["const", "charging"], days),
        "charging_netload": ols_cluster(y, np.column_stack([one, chg, nl, nl ** 2]), ["const", "charging", "net_load_gw", "net_load_gw2"], days),
        "charging_netload_fe": ols_cluster(y, np.column_stack([one, chg, nl, nl ** 2, hd, md]), ["const", "charging", "net_load_gw", "net_load_gw2"] + fe_names, days),
        "netload_fe": ols_cluster(y, np.column_stack([one, nl, nl ** 2, hd, md]), ["const", "net_load_gw", "net_load_gw2"] + fe_names, days),
    }
    # the same full model with net load measured before curtailment (the curtailed MW added back to wind and solar):
    # delivered output is lower by what was curtailed, so the standard net load moves with curtailment by construction
    nlb = nl - y / 1000.0
    before = ols_cluster(y, np.column_stack([one, chg, nlb, nlb ** 2, hd, md]), ["const", "charging", "net_load_gw", "net_load_gw2"] + fe_names, days)
    df["pred"] = fits["netload_fe"]["fitted"]
    df["resid"] = y - df["pred"]
    df["is_charging"] = ch > 0
    df["on"] = y >= CURTAILED_ON
    df["rising"] = df["on"] & (df["curtailed_mw"] > df.groupby("day")["curtailed_mw"].shift(1))
    df["at_trail"] = df["is_charging"] & df["trail_max_charging_mw"].notna() & (ch >= pct / 100.0 * df["trail_max_charging_mw"].fillna(np.inf))
    df["at_fleet"] = df["fleet_mw"].notna() & (ch >= pct / 100.0 * df["fleet_mw"].fillna(np.inf))
    r = float(np.corrcoef(y, ch)[0, 1])
    years = sorted(df["year"].unique())
    last_full = max(v for v in years if v < years[-1]) if len(years) > 1 else years[0]
    n = {"n_hours": int(len(df)), "n_days": int(df["day"].nunique()), "n_months": len(months), "first_day": str(df["day"].iloc[0]), "last_day": str(df["day"].iloc[-1]),
         "first_year": int(years[0]), "last_year": int(years[-1]), "last_full_year": int(last_full), "ceiling_pct": pct,
         "corr_curtailed_charging": r, "corr_squared": r * r,
         "charging_hours": int(df["is_charging"].sum()), "charging_hours_pct": float(df["is_charging"].mean() * 100),
         "curtailed_hours_pct": float(df["on"].mean() * 100),
         "curtailed_mwh_all": float(y.sum()), "curtailed_mwh_in_charging_hours_pct": float(y[df["is_charging"].to_numpy()].sum() / y.sum() * 100),
         "mean_curtailed_mw": float(y.mean()), "mean_charging_mw": float(ch.mean())}
    for k in ("charging", "charging_netload", "charging_netload_fe"):
        c = fits[k]["coef"]["charging"]
        n[f"{k}_coef"], n[f"{k}_se"], n[f"{k}_p"] = c["coef"] / 1000.0, c["se"] / 1000.0, c["p"]
        n[f"{k}_r2"], n[f"{k}_n"] = fits[k]["r2"], fits[k]["n"]
    n["netload_fe_r2"] = fits["netload_fe"]["r2"]
    n["netload_coef_mw_per_gw"] = fits["netload_fe"]["coef"]["net_load_gw"]["coef"]
    n["netload2_coef"] = fits["netload_fe"]["coef"]["net_load_gw2"]["coef"]
    n["clusters"] = fits["charging_netload_fe"]["clusters"]
    cb = before["coef"]["charging"]
    n["before_curtailment_coef"], n["before_curtailment_se"], n["before_curtailment_p"], n["before_curtailment_r2"] = cb["coef"] / 1000.0, cb["se"] / 1000.0, cb["p"], before["r2"]
    by_year = []
    for yr, g in df.groupby("year"):
        c = g[g["is_charging"]]
        tr = g[g["trail_max_charging_mw"].notna()]
        sat = g[g["at_trail"]]
        sat_on = sat[sat["on"]]
        fl = g[g["fleet_mw"].notna()]
        tot = float(g["curtailed_mw"].sum())
        row = {"year": int(yr), "hours": int(len(g)), "charging_hours": int(len(c)), "curtailed_mwh": tot,
               "mean_charging_mw": float(g["charging_mw"].mean()),
               "obs_charging_mw": float(c["curtailed_mw"].mean()) if len(c) else None,
               "pred_charging_mw": float(c["pred"].mean()) if len(c) else None,
               "resid_charging_mw": float(c["resid"].mean()) if len(c) else None,
               "resid_other_mw": float(g.loc[~g["is_charging"], "resid"].mean()) if len(g) > len(c) else None,
               "peak_charging_mw": float(g["charging_mw"].max()),
               "ceiling_hours_held": int(len(tr)), "sat_hours": int(len(sat)), "sat_curt_hours": int(len(sat_on)),
               "sat_rising_hours": int(sat["rising"].sum()), "sat_curt_mwh": float(sat_on["curtailed_mw"].sum()),
               "sat_curt_share_pct": float(sat_on["curtailed_mw"].sum() / tot * 100) if tot > 0 else None,
               "fleet_hours_held": int(len(fl)), "fleet_sat_hours": int(g["at_fleet"].sum()),
               "peak_pct_fleet": float((fl["charging_mw"] / fl["fleet_mw"]).max() * 100) if len(fl) else None,
               "fleet_mw_last": float(fl["fleet_mw"].iloc[-1]) if len(fl) else None}
        by_year.append(row)
        for k, v in row.items():
            if k != "year":
                n[f"y{yr}_{k}"] = v
    gw_years = [b["year"] for b in by_year if b["peak_charging_mw"] >= GW_CHARGING]
    n["gw_year"] = int(gw_years[0]) if gw_years else int(years[0])
    signed = [b["resid_charging_mw"] for b in by_year if b["resid_charging_mw"] is not None]
    n["resid_years"], n["resid_years_above"], n["resid_years_below"] = len(signed), sum(1 for v in signed if v > 0), sum(1 for v in signed if v < 0)
    lf = df[df["year"] == last_full]
    by_hour = lf.groupby("hour").agg(curtailed=("curtailed_mw", "mean"), pred=("pred", "mean"), charging=("charging_mw", "mean")).reindex(range(24))
    return {"numbers": n, "by_year": by_year,
            "by_hour": {"curtailed": [None if pd.isna(v) else float(v) for v in by_hour["curtailed"]],
                        "pred": [None if pd.isna(v) else float(v) for v in by_hour["pred"]],
                        "charging": [None if pd.isna(v) else float(v) for v in by_hour["charging"]]}}


def numbers_from_rows(rows, params=None):
    """Every number on the card, from the data rows alone (the test's proof)."""
    return analyse(rows, params)["numbers"]


def p_words(p):
    return "p < 0.001" if p < 0.001 else f"p = {p:.3f}"


def chart(a):
    n, h = a["numbers"], a["by_hour"]
    y = n["last_full_year"]
    return {"kind": "lines", "x": [f"{i:02d}" for i in range(24)], "x_label": f"Hour of the day (Pacific), mean over the hours of {y}",
            "series": [{"name": f"Curtailed, observed, {y}", "type": "line", "unit": "MW", "values": h["curtailed"]},
                       {"name": "Curtailed, what net load alone predicts", "type": "line", "unit": "MW", "values": h["pred"]},
                       {"name": f"Battery charging, {y}", "type": "line", "unit": "MW", "values": h["charging"]}],
            "y_left_label": "MW, mean of the hour", "value_suffix": " MW", "decimals": 0}


def card(rows, params, meta):
    a = analyse(rows, {"ceiling_pct": meta["ceiling_pct"]})
    n, by_year = a["numbers"], a["by_year"]
    y1, yg, pct = n["last_full_year"], n["gw_year"], n["ceiling_pct"]
    b, se, p = n["charging_netload_fe_coef"], n["charging_netload_fe_se"], n["charging_netload_fe_p"]
    b0, b1 = n["charging_coef"], n["charging_netload_coef"]
    obs, pred, res = n[f"y{y1}_obs_charging_mw"], n[f"y{y1}_pred_charging_mw"], n[f"y{y1}_resid_charging_mw"]
    side = "above" if res > 0 else "below"
    y2 = n["last_year"]
    res2 = n[f"y{y2}_resid_charging_mw"]
    side2 = "above" if res2 > 0 else "below"
    steady = n["resid_years_above"] == 0 or n["resid_years_below"] == 0
    if p < 0.05 and b > 0:
        sub = "Hours with more charging see more curtailment, not less, with net load, the hour and the month held fixed"
        words = (f"each MW of charging in an hour goes with {fmt(b, 3)} MW more curtailment in that hour, net load, the hour of the day and the month held fixed "
                 f"(standard error {fmt(se, 3)}, clustered by day, {p_words(p)}): an association, and not the curtailment batteries prevent, because batteries "
                 "charge in the cheap hours and the cheap hours are the curtailed ones")
    elif p < 0.05 and b < 0:
        sub = ("With net load, the hour and the month held fixed, hours with more charging see less curtailment" if steady else
               "With net load, the hour and the month held fixed, an hour with more charging has less curtailment on average, though not in every year")
        words = (f"each MW of charging in an hour goes with {fmt(-b, 3)} MW less curtailment in that hour, net load, the hour of the day and the month held fixed "
                 f"(standard error {fmt(se, 3)}, clustered by day, {p_words(p)}): an association, not a measured cause, since charging is chosen in the cheap "
                 "hours, which are the curtailed ones")
    else:
        sub = "With net load, the hour and the month held fixed, the hours cannot pin curtailment on charging either way"
        words = (f"each MW of charging in an hour goes with {fmt(b, 3)} MW of curtailment (standard error {fmt(se, 3)}, clustered by day, {p_words(p)}): an "
                 "estimate that spans zero once net load, the hour of the day and the month are held fixed")
    fleet_hours = sum(r["fleet_sat_hours"] for r in by_year)
    if fleet_hours == 0:
        fleet_words = (f"Against the EIA-860M nameplate the fleet was never there: no hour of the sample charged at {pct} percent of it, and the largest hour of {y1} "
                       f"was {fmt(n[f'y{y1}_peak_charging_mw'], 0)} MW, {fmt(n[f'y{y1}_peak_pct_fleet'], 1)} percent of that month's fleet.")
    else:
        fleet_words = (f"Against the EIA-860M nameplate, {fmt(fleet_hours, 0)} hours of the sample charged at {pct} percent of it or more; the largest hour of {y1} "
                       f"was {fmt(n[f'y{y1}_peak_charging_mw'], 0)} MW, {fmt(n[f'y{y1}_peak_pct_fleet'], 1)} percent of that month's fleet.")
    why = (f"Over {fmt(n['n_hours'], 0)} hours from {n['first_day']} to {n['last_day']}, CAISO's batteries charged in {fmt(n['charging_hours_pct'], 1)} percent of hours, "
           f"and {fmt(n['curtailed_mwh_in_charging_hours_pct'], 1)} percent of all curtailed energy fell in those hours: the fleet keeps the same hours as the surplus. "
           f"Hour by hour the two correlate at r = {fmt(n['corr_curtailed_charging'], 2)} (R2 {fmt(n['charging_r2'], 2)}, charging alone). Net load with its square, the "
           f"hour of the day and the month explains R2 {fmt(n['netload_fe_r2'], 2)} of hourly curtailment without knowing anything about batteries; in the charging hours "
           f"of {y1} it predicts {fmt(pred, 0)} MW and the record shows {fmt(obs, 0)} MW, {fmt(abs(res), 0)} MW {side}. The sign is not a law: that residual is above zero in "
           f"{fmt(n['resid_years_above'], 0)} of the {fmt(n['resid_years'], 0)} years and below it in {fmt(n['resid_years_below'], 0)}, and in {y2} to date it is "
           f"{fmt(abs(res2), 0)} MW {side2}. Charging alone goes with {fmt(b0, 3)} MW of "
           f"curtailment per MW charged; with net load held fixed, {fmt(b1, 3)}; with the hour and the month too, {fmt(b, 3)} (standard error {fmt(se, 3)}, "
           f"{p_words(p)}, R2 {fmt(n['charging_netload_fe_r2'], 2)}). That number is not what batteries prevent: they charge when prices are low, and prices are low "
           f"when solar is being turned down. On the ceiling: in {y1} charging reached {pct} percent of its trailing 30-day maximum in "
           f"{fmt(n[f'y{y1}_sat_hours'], 0)} hours, {fmt(n[f'y{y1}_sat_curt_hours'], 0)} of them with curtailment still on "
           f"({fmt(n[f'y{y1}_sat_curt_mwh'], 0)} MWh, {fmt(n[f'y{y1}_sat_curt_share_pct'], 1)} percent of the year's). {fleet_words} "
           "The batteries are at the table when the surplus is served; this design cannot count what they ate.")
    sat_list = "; ".join(
        f"{r['year']}: {fmt(r['sat_hours'], 0)} hours at the ceiling, {fmt(r['sat_curt_hours'], 0)} with curtailment on ({fmt(r['sat_curt_mwh'], 0)} MWh, "
        f"{fmt(r['sat_curt_share_pct'], 1)} percent of the year's; rising in {fmt(r['sat_rising_hours'], 0)}), peak hour {fmt(r['peak_charging_mw'], 0)} MW"
        + (f" or {fmt(r['peak_pct_fleet'], 1)} percent of nameplate" if r["peak_pct_fleet"] is not None else "")
        + f", residual in charging hours {fmt(r['resid_charging_mw'], 0) if r['resid_charging_mw'] is not None else 'not held'} MW"
        for r in by_year)
    foot = (f"Data: CAISO, hourly, Pacific time ({TZ}; daylight saving by time zone conversion of the UTC hour), {n['first_day']} to {n['last_day']}: "
            f"{fmt(n['n_hours'], 0)} hours on {fmt(n['n_days'], 0)} days in {fmt(n['n_months'], 0)} calendar months. Curtailment: caiso_curtailment_intervals, solar plus "
            "wind, 5-minute MW to 2025-12-31 (each interval's MW times 5/60, summed in the hour) and hourly MWh from 2026-01-01 (the six categories summed); CAISO "
            "lists only intervals with a curtailment, so an hour not listed on a day the table covers is zero. Summed by day, the hours differ from the table's own "
            f"day totals by at most {fmt(meta['reconcile_max_abs_mwh'], 3)} MWh over {fmt(meta['reconcile_days'], 0)} days "
            f"({fmt(meta['reconcile_days_within_1_mwh'], 0)} within 1 MWh). Charging and net load: caiso_fuel_supply_history and "
            "caiso_fuel_supply (Today's Outlook, the mean of the hour's twelve 5-minute values). Charging is the batteries column below zero, as a positive MW; an "
            "hour is a charging hour when the fleet took in more than it gave back. Demand is the sum of the thirteen sources (batteries net, imports net), which is "
            "the load served other than charging; net load is demand less solar and wind. A day is left out when it holds fewer than 23 hours "
            f"({fmt(meta['days_short'], 0)} days) or when any hour reads natural gas or wind below -100 MW, small hydro above 2,000 MW or demand under 10,000 MW "
            f"({fmt(len(meta['days_faulty']), 0)} days: {', '.join(meta['days_faulty']) or 'none'}); nothing is filled. Regressions: OLS of hourly curtailment (MW) on "
            "charging (MW); on charging, net load (GW) and its square; on those with 23 hour-of-day and "
            f"{fmt(n['n_months'] - 1, 0)} month-of-sample dummies; and the last without charging, whose residual is 'what net load alone predicts' (a linear fit, so "
            "its prediction is not bounded at zero and reads below it at night). Net load is measured after curtailment, as published: delivered solar and wind are lower "
            "by what was curtailed. With the curtailed MW added back (net load before curtailment) the full model's charging coefficient is "
            f"{fmt(n['before_curtailment_coef'], 3)} (standard error {fmt(n['before_curtailment_se'], 3)}, {p_words(n['before_curtailment_p'])}, R2 "
            f"{fmt(n['before_curtailment_r2'], 2)}). Standard errors "
            f"are cluster-robust by Pacific day ({fmt(n['clusters'], 0)} clusters, Stata's vce(cluster) with its small-sample factor, p from Student's t on clusters "
            "less one), because the hours of one day share its weather and prices and are not independent draws. r is the Pearson correlation of hourly curtailment "
            f"with charging over all hours. The ceiling: an hour is at it when charging is at or above {pct} percent of (a) the largest charging hour of the "
            f"{TRAIL_DAYS} Pacific days before its day (at least {TRAIL_MIN_DAYS} held) or (b) the fleet's nameplate MW of its month (storage_buildout_monthly, iso:caiso "
            f"battery_operating_mw, EIA-860M, held to {meta['fleet_last_month']}); curtailment is on from {fmt(CURTAILED_ON, 0)} MW and rising when above the hour before. "
            f"By year, measure (a): {sat_list}. Measure (b): {fmt(fleet_hours, 0)} hours in the sample. No instrument, no event window: an association.")
    table = {"columns": ["Specification", "Per MW charged (MW curtailed)", "SE (clustered by day)", "p", "Hours", "R2"],
             "rows": [{"measure": "charging alone", "coef_per_gw": b0, "se": n["charging_se"], "p": n["charging_p"], "n": n["charging_n"], "r2": n["charging_r2"]},
                      {"measure": "charging, net load and its square held fixed", "coef_per_gw": b1, "se": n["charging_netload_se"], "p": n["charging_netload_p"],
                       "n": n["charging_netload_n"], "r2": n["charging_netload_r2"]},
                      {"measure": "charging, net load, hour of day and month held fixed", "coef_per_gw": b, "se": se, "p": p, "n": n["charging_netload_fe_n"],
                       "r2": n["charging_netload_fe_r2"]}],
             "in_words": words}
    return {
        "id": NAME, "title": TITLE, "kind": KIND, "subtitle": sub,
        "params": {"first_year": meta["first_year"], "ceiling_pct": meta["ceiling_pct"]},
        "inputs_words": {"first_year": str(meta["first_year"]), "ceiling_pct": f"{meta['ceiling_pct']} percent of the ceiling"},
        "chart": chart(a),
        "callouts": [
            callout(f"Curtailment in the charging hours of {y1}, MW", "net load alone predicts", fmt(pred, 0), "observed", fmt(obs, 0)),
            callout("Hourly curtailment with charging", "correlation r", fmt(n["corr_curtailed_charging"], 2), "R2, charging alone", fmt(n["charging_r2"], 2)),
            callout(f"Hours at {pct}% of the charging ceiling, curtailment on", str(yg), fmt(n[f"y{yg}_sat_curt_hours"], 0), str(y1), fmt(n[f"y{y1}_sat_curt_hours"], 0), "hours"),
        ],
        "why": why, "footnote": foot, "numbers": n, "effect_table": table, "by_year": by_year,
        "source_line": "Source: CAISO production and curtailments data and Daily Renewable Report; CAISO Today's Outlook (supply); EIA-860M; ERW tables " + ", ".join(TABLES) + ".",
        "tables": TABLES, "computed_at": now_iso(), "method": METHOD_URL,
        "csv_header": [f"Energy Research Warehouse (ERW): finding {NAME}, {TITLE}", f"Computed {now_iso()} by warehouse/analysis/findings/{NAME}.py; method {METHOD_URL}",
                       "Rows: one per hour held (day and hour are Pacific): curtailed MW (solar plus wind), battery charging MW, net load MW (demand less solar and wind), "
                       "the fleet's EIA-860M MW of the month, the largest charging hour of the 30 days before the day; a blank is not held",
                       "Sources: " + ", ".join(TABLES)],
    }


def stata(params):
    pct = int(params.get("ceiling_pct", 90)) if params else 90
    V = ["hour", "curtailed_mw", "charging_mw", "net_load_mw", "fleet_mw", "trail_max_charging_mw"]
    return do_file([
        f"* ERW finding {NAME}: {TITLE}. Reproduces the card's correlation, regressions and ceiling counts from {CSV_NAME}.",
        "* The CSV begins with four comment lines: the names are on line 5 and the data begin on line 6.",
        "clear all",
        f'import delimited "{CSV_NAME}", varnames(5) rowrange(6) stringcols(_all) clear',
        *do_destring(V),
        *do_sentinels(V),
        "gen year = real(substr(day, 1, 4))",
        "gen month = substr(day, 1, 7)",
        "encode month, gen(month_id)",
        "encode day, gen(day_id)",
        "gen net_load_gw = net_load_mw / 1000",
        "gen net_load_gw2 = net_load_gw ^ 2",
        "gen charging_hour = charging_mw > 0",
        "correlate curtailed_mw charging_mw",
        "regress curtailed_mw charging_mw, vce(cluster day_id)",
        "regress curtailed_mw charging_mw net_load_gw net_load_gw2, vce(cluster day_id)",
        "regress curtailed_mw charging_mw net_load_gw net_load_gw2 i.hour i.month_id, vce(cluster day_id)",
        "* vce(cluster day_id) is the card's standard errors: hours of one Pacific day are not independent",
        "regress curtailed_mw net_load_gw net_load_gw2 i.hour i.month_id",
        "predict predicted, xb",
        "predict residual, residuals",
        "tabstat curtailed_mw predicted residual if charging_hour == 1, by(year) statistics(mean n) format(%9.1f)",
        "* net load before curtailment: the curtailed MW added back to wind and solar",
        "gen net_load_before_gw = (net_load_mw - curtailed_mw) / 1000",
        "gen net_load_before_gw2 = net_load_before_gw ^ 2",
        "regress curtailed_mw charging_mw net_load_before_gw net_load_before_gw2 i.hour i.month_id, vce(cluster day_id)",
        f"gen at_ceiling = charging_hour == 1 & !missing(trail_max_charging_mw) & charging_mw >= {pct / 100:.2f} * trail_max_charging_mw",
        f"gen at_nameplate = !missing(fleet_mw) & charging_mw >= {pct / 100:.2f} * fleet_mw",
        "tabstat at_ceiling at_nameplate, by(year) statistics(sum) format(%9.0f)",
        f"tabstat curtailed_mw if at_ceiling == 1 & curtailed_mw >= {CURTAILED_ON:.0f}, by(year) statistics(n sum) format(%9.0f)",
    ])


SOURCE_PATH = os.path.abspath(__file__)
