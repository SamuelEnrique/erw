#!/usr/bin/env python3
"""Demand growth with the weather taken out: for each of the seven grids, how much of each year's change in demand the
year's temperatures explain, and how much they do not (session 126).

Energy Research Warehouse (ERW). One derived table, eia930_demand_weather, from EIA-930 hourly demand and
noaa_grid_weather_hourly. Method: docs/methods/demand_weather.md. Page: /demand/weather (in review).

    python warehouse/derived/demand_weather.py                 # the table, under the data lock
    python warehouse/derived/demand_weather.py --out-dir DIR   # a trial: the table under DIR, nothing in warehouse/output
    python warehouse/derived/demand_weather.py --snapshot      # also the site's own copy (site/data/demand_weather.json)
    python warehouse/derived/demand_weather.py --cache DIR     # keep each grid's hourly demand in DIR between runs

Inputs (no request is made): EIA-930 hourly demand as demand_growth.py reads it (EIA's Adjusted demand, California's
late hours set back), and each grid's weighted hourly weather (noaa_grid_weather_hourly). An hour of demand is used only
when it passes the impossible-value rule of session 118 (impossible_hours.screen: held, above zero, within a quarter of
the median of the four hours around it, and within the grid's own range). Nothing is filled.

THE FIT. For each grid, on the local years 2019 to 2021, one least-squares line for each of 48 kinds of hour (24 hours
of the local day, weekday or weekend):

    demand = a + b1 HD + b2 HD^2 + b3 CD + b4 CD^2 + b5 HD24 + b6 CD24

HD and CD are the grid's heating and cooling degrees of the hour (base 65 F, taken at each station and weighted), HD24
and CD24 their means over the 24 hours before it (a building holds yesterday's heat). Heating and cooling have their
own terms, and every kind of hour its own seven numbers. There is no trend, no month and no holiday in it: whatever
repeats every year by the calendar and not by the temperature is carried by the temperature it travels with.
Texas's hours of 15 to 19 February 2021 are left out of the fit: ERCOT was shedding load, so the meter did not record
what customers would have used. They stay in the year's own figures.

WHAT IS REPORTED, for each grid and each year after 2021, for four figures: the year's energy (the mean of its hours),
the summer peak (the highest hour of June to September), the winter peak (the highest hour of December of the year
before to February) and the overnight minimum (the mean over the year's days of the lowest hour from midnight to 6 am,
local: the hours a load that never switches off shows most plainly). With A the figure from metered demand and P the
same figure from the fit's hours (what the customers of 2019 to 2021 would have used in that year's weather), and A0
and P0 their means over the years 2019 to 2021:

    growth                 A / A0 - 1
    explained by weather   P / P0 - 1
    not explained          the first minus the second

Both figures of a year come from the same hours: those where demand passes the rule and the weather is held. A figure
is written when at least 95 percent of its hours (or days) are. The newest year is partial: its energy and overnight
minimum are compared over the same days of the year in 2019 to 2021.

THE UNCERTAINTY comes from years the fit has not seen. Each of 2019, 2020 and 2021 is left out in turn, the fit is
made on the other two, and the left-out year's "not explained" is computed against them. A grid whose customers did
not change should come back at zero; what comes back is the fit's miss plus whatever really changed that year (2020
holds the lockdowns). The uncertainty of a figure is the largest of those misses, in absolute value. A peak is a single
hour, so its uncertainty is never taken as less than the fit's mean absolute error on an hour it had not seen. A
figure smaller than its uncertainty is not a finding (x_finding no), whatever its sign; and neither is a peak whose
hour was hotter (summer) or colder (winter) than any hour of 2019 to 2021, where the fit reaches past what it was made
on (x_finding beyond).

WHAT THE REMAINDER IS NOT. "Not explained" is growth the temperature does not explain. Population, electrification,
industry, datacenters, rooftop solar behind the meter (which lowers metered demand), prices and efficiency are all in
it together. The warehouse cannot split them.
"""

import argparse
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, HERE)
import caiso_join as cj  # noqa: E402
import demand_growth as dg  # noqa: E402
import impossible_hours  # noqa: E402
import iso_prices as ip  # noqa: E402

NAME = "eia930_demand_weather"
SOURCE = "erw:demand_weather"
METHOD_URL = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/demand_weather.md"
WEATHER = "noaa_grid_weather_hourly"
SITE_FILE = os.path.join(ROOT, "site", "data", "demand_weather.json")
TRAIN = (2019, 2020, 2021)
SUMMER, WINTER = (6, 7, 8, 9), (12, 1, 2)
NIGHT = (0, 1, 2, 3, 4, 5)        # local hours, hour beginning
NEAR = 0.95                       # a figure is written when at least this share of its hours, or days, is used
LAG, LAG_MIN = 24, 18             # the hours before, and how many of them must be held for their mean
SHED = {"ERCO": ("2021-02-15", "2021-02-19")}   # local days left out of the fit: the grid was shedding load
BAS = ("ERCO", "CISO", "PJM", "MISO", "SWPP", "NYIS", "ISNE")
METRICS = ("energy", "summer_peak", "winter_peak", "overnight_min")
PEAKS = ("summer_peak", "winter_peak")
LABEL = {"energy": "the year's energy", "summer_peak": "the summer peak", "winter_peak": "the winter peak", "overnight_min": "the overnight minimum"}
FEATURES = ("one", "hd", "hd2", "cd", "cd2", "hd24", "cd24")
PLAIN = ("one", "hd", "cd")       # the comparison: the same 48 lines with heating and cooling degrees only


def read_weather(path):
    """{BA: frame by UTC hour with temperature_f, dew_point_f, heating_degrees_f, cooling_degrees_f} from the table."""
    w = pd.read_csv(path, skiprows=ip.header_rows(path), usecols=["variable", "ts_utc", "value", "ba"], dtype={"variable": str, "ts_utc": str, "ba": str})
    out = {}
    for ba, g in w.groupby("ba"):
        p = g.pivot(index="ts_utc", columns="variable", values="value")
        p.index = pd.to_datetime(p.index, utc=True)
        out[ba.upper()] = p.sort_index()
    return out


def read_demand(ba, cache=None):
    """The grid's hourly demand as demand_growth.py reads it, with the workbook's path. cache: a folder keeping it."""
    f = os.path.join(cache, f"{ba}.csv") if cache else None
    if f and os.path.exists(f):
        d = pd.read_csv(f, index_col=0)
        d.index = pd.to_datetime(d.index, utc=True)
        with open(f[:-4] + ".txt", encoding="utf-8") as fh:
            path = fh.readline().strip()
        return d["demand"], path
    d, path, col = dg.read_demand(ba)
    if f:
        os.makedirs(cache, exist_ok=True)
        d.to_frame("demand").to_csv(f)
        with open(f[:-4] + ".txt", "w", encoding="utf-8") as fh:
            fh.write(f"{path}\n{col}\n")
    return d, path


def frame(demand, weather, tz, ba=None):
    """One row an hour: demand as the rule leaves it (NaN where an hour is not used), the weather, the local calendar,
    and the fit's terms. Every hour from the first to the last of the weather is a row, so a lag is taken by the clock."""
    idx = pd.date_range(weather.index.min(), weather.index.max(), freq="h")
    x = pd.DataFrame(index=idx)
    full = demand.reindex(pd.date_range(demand.index.min(), demand.index.max(), freq="h"))
    x["demand"] = impossible_hours.screen(full).reindex(idx)
    x["raw"] = full.reindex(idx)
    for c in ("temperature_f", "dew_point_f", "heating_degrees_f", "cooling_degrees_f"):
        x[c] = weather[c].reindex(idx) if c in weather else np.nan
    local = idx.tz_convert(tz)
    x["year"], x["month"], x["hour"], x["dow"] = local.year, local.month, local.hour, local.dayofweek
    x["day"] = local.strftime("%Y-%m-%d")
    x["md"] = local.strftime("%m-%d")
    x["weekend"] = (x["dow"] >= 5).astype(int)
    x["winter"] = np.where(x["month"] == 12, x["year"] + 1, x["year"])   # a winter is named by its January
    x["one"] = 1.0
    x["hd"], x["cd"] = x["heating_degrees_f"], x["cooling_degrees_f"]
    x["hd2"], x["cd2"] = x["hd"] ** 2, x["cd"] ** 2
    x["hd24"] = x["hd"].shift(1).rolling(LAG, min_periods=LAG_MIN).mean()
    x["cd24"] = x["cd"].shift(1).rolling(LAG, min_periods=LAG_MIN).mean()
    x["shed"] = False
    if ba in SHED:
        x["shed"] = (x["day"] >= SHED[ba][0]) & (x["day"] <= SHED[ba][1])
    return x


def fit(x, years, features=FEATURES):
    """The 48 lines, from the hours of `years` that are used and not shed. Returns {(hour, weekend): coefficients}."""
    ok = x["year"].isin(years) & x["demand"].notna() & x[list(features)].notna().all(axis=1) & ~x["shed"]
    t = x[ok]
    model = {}
    for key, g in t.groupby(["hour", "weekend"]):
        if len(g) < 3 * len(features):
            continue
        model[key] = np.linalg.lstsq(g[list(features)].to_numpy(), g["demand"].to_numpy(), rcond=None)[0]
    return model


def predict(x, model, features=FEATURES):
    """The fit's demand for every hour whose terms are held (NaN elsewhere)."""
    out = pd.Series(np.nan, index=x.index)
    X = x[list(features)]
    held = X.notna().all(axis=1)
    for (hour, weekend), b in model.items():
        m = held & (x["hour"] == hour) & (x["weekend"] == weekend)
        out[m] = X[m].to_numpy() @ b
    return out


def stat(x, pred, metric, year, through=None):
    """One figure of one year, from metered demand (A) and from the fit (P) over the same hours. Returns a dict with
    a, p, used, wanted (hours, or days for the overnight minimum), at (the hour of A, for a peak) or None when under
    NEAR. through: "MM-DD", the last day of the year counted (the partial year, and the same days of the earlier ones)."""
    both = x["demand"].notna() & pred.notna()
    if metric in ("energy", "overnight_min"):
        sel = x["year"] == year
        if through:
            sel &= x["md"] <= through
    elif metric == "summer_peak":
        sel = (x["year"] == year) & x["month"].isin(SUMMER)
    else:
        sel = (x["winter"] == year) & x["month"].isin(WINTER)
    wanted = int(sel.sum())
    if metric == "winter_peak":   # a winter whose December is before the weather begins is short of its hours
        tz = x.index.tz_convert(x.attrs["tz"])
        wanted = int((pd.Timestamp(f"{year}-03-01", tz=x.attrs["tz"]) - pd.Timestamp(f"{year - 1}-12-01", tz=x.attrs["tz"])) / pd.Timedelta(hours=1))
        del tz
    if metric == "summer_peak":
        wanted = int((pd.Timestamp(f"{year}-10-01", tz=x.attrs["tz"]) - pd.Timestamp(f"{year}-06-01", tz=x.attrs["tz"])) / pd.Timedelta(hours=1))
    use = sel & both
    if metric == "overnight_min":
        n = x[sel & x["hour"].isin(NIGHT)]
        ok = (sel & both & x["hour"].isin(NIGHT))
        days_all = n["day"].nunique()
        g = pd.DataFrame({"day": x["day"][ok], "a": x["demand"][ok], "p": pred[ok]}).groupby("day")
        whole = g["a"].size() == len(NIGHT)
        a, p = g["a"].min()[whole], g["p"].min()[whole]
        if not days_all or len(a) / days_all < NEAR:
            return None
        return dict(a=float(a.mean()), p=float(p.mean()), used=int(len(a)), wanted=int(days_all), at=None)
    used = int(use.sum())
    if not wanted or used / wanted < NEAR:
        return None
    if metric == "energy":
        return dict(a=float(x["demand"][use].mean()), p=float(pred[use].mean()), used=used, wanted=wanted, at=None)
    at = x["demand"][use].idxmax()
    return dict(a=float(x["demand"][use].max()), p=float(pred[use].max()), used=used, wanted=wanted, at=at, at_pred=pred[use].idxmax())


def growth(x, pred, metric, year, base_years, through=None):
    """A year's growth, the part the weather explains and the part it does not, against the mean of base_years (those
    of them that hold the figure). None when the year or every base year lacks it."""
    s = stat(x, pred, metric, year, through)
    base = [b for b in (stat(x, pred, metric, y, through) for y in base_years) if b]
    if not s or not base:
        return None
    a0, p0 = float(np.mean([b["a"] for b in base])), float(np.mean([b["p"] for b in base]))
    g, e = s["a"] / a0 - 1, s["p"] / p0 - 1
    return dict(actual=s["a"], expected=s["p"], base=a0, base_expected=p0, growth_pct=100 * g, weather_pct=100 * e,
                unexplained_pct=100 * (g - e), used=s["used"], wanted=s["wanted"], base_years=len(base), at=s["at"])


def holdouts(x, features=FEATURES, through=None):
    """Each training year left out in turn: the fit on the other two, the left-out year's figures against them, and the
    hour-by-hour error on the left-out year. Returns ({year: {metric: growth dict}}, {year: (mean absolute percent
    error, hours)}, the left-out predictions as one series)."""
    out, err, pooled = {}, {}, pd.Series(np.nan, index=x.index)
    for k in TRAIN:
        others = tuple(y for y in TRAIN if y != k)
        pred = predict(x, fit(x, others, features), features)
        out[k] = {m: growth(x, pred, m, k, others, through if m in ("energy", "overnight_min") else None) for m in METRICS}
        m = (x["year"] == k) & x["demand"].notna() & pred.notna() & ~x["shed"]
        err[k] = (float(((pred[m] - x["demand"][m]).abs() / x["demand"][m]).mean() * 100), int(m.sum()))
        pooled[m] = pred[m]
    return out, err, pooled


def uncertainty(hold, metric):
    """The largest miss, in absolute value, of the years left out that hold the figure; and how many did."""
    v = [abs(h[metric]["unexplained_pct"]) for h in hold.values() if h[metric]]
    return (float(max(v)), len(v)) if v else (None, 0)


def analyse(demand, weather, tz, ba, features=FEATURES):
    """One grid: the fit on 2019 to 2021, each later year's figures, the left-out years, the fit's error."""
    x = frame(demand, weather, tz, ba)
    x.attrs["tz"] = tz
    model = fit(x, TRAIN, features)
    pred = predict(x, model, features)
    both = x["demand"].notna() & pred.notna()
    last_day = x["day"][both].max()
    # the newest year's last whole local day with every hour used; its energy and overnight minimum stop there
    newest = int(x["year"][both].max())
    days = x[both & (x["year"] == newest)].groupby("day").size()
    whole = days[days >= 23]
    through = whole.index.max()[5:] if len(whole) else None
    hold, err, pooled = holdouts(x, features)
    hold_ytd, _, _ = holdouts(x, features, through)
    ho = pooled.notna() & x["demand"].notna()
    oos = float(((pooled[ho] - x["demand"][ho]).abs() / x["demand"][ho]).mean() * 100)   # the error on one hour left out
    years = {}
    lim = {v: float(x.loc[x["year"].isin(TRAIN) & x["demand"].notna(), v].max()) for v in ("hd", "cd")}
    for y in sorted(set(x["year"][both])):
        if y in TRAIN:
            continue
        partial = y == newest and through and through < "12-31"
        row = {}
        for m in METRICS:
            thr = through if partial and m in ("energy", "overnight_min") else None
            g = growth(x, pred, m, y, TRAIN, thr)
            if not g:
                row[m] = None
                continue
            u, n = uncertainty(hold_ytd if thr else hold, m)
            if u is not None and m in PEAKS:
                u = max(u, oos)      # a peak is one hour: its uncertainty is never under the fit's error on one hour
            g["uncertainty_pct"], g["holdouts"] = u, n
            g["window"] = f"1 January to {thr}" if thr else ("the year" if m in ("energy", "overnight_min") else "the season")
            if g["at"] is not None:
                v = "cd" if m == "summer_peak" else "hd"
                g["outside"] = bool(x.loc[g["at"], v] > lim[v])     # hotter, or colder, than any hour the fit saw
                g["at"] = ip.utc_iso(g["at"])
            # a finding: larger than its uncertainty, and not a peak in weather beyond anything the fit was made on
            g["finding"] = bool(u is not None and abs(g["unexplained_pct"]) > u and not g.get("outside"))
            row[m] = g
        years[int(y)] = row
    tr = x["year"].isin(TRAIN) & both & ~x["shed"]
    ins = float(((pred[tr] - x["demand"][tr]).abs() / x["demand"][tr]).mean() * 100)
    d = pd.DataFrame({"a": x["demand"][ho], "p": pooled[ho], "day": x["day"][ho]}).groupby("day").mean()
    oos_day = float(((d["p"] - d["a"]).abs() / d["a"]).mean() * 100)
    used = x["year"].isin(TRAIN) & x["raw"].notna()
    fitinfo = dict(hours=int(tr.sum()), kinds=len(model), in_sample_mape_pct=ins, oos_mape_pct=oos, oos_daily_mape_pct=oos_day,
                   oos_by_year={int(k): dict(mape_pct=v[0], hours=v[1]) for k, v in err.items()},
                   hours_not_used=int((x["year"].isin(TRAIN) & x["raw"].notna() & x["demand"].isna()).sum()),
                   hours_held=int(used.sum()), shed_hours=int((x["shed"] & x["demand"].notna()).sum()),
                   hd_max=lim["hd"], cd_max=lim["cd"])
    holdout = {int(k): {m: (None if not h[m] else {kk: h[m][kk] for kk in ("growth_pct", "weather_pct", "unexplained_pct", "actual", "expected")}) for m in METRICS} for k, h in hold.items()}
    return dict(x=x, pred=pred, years=years, fit=fitinfo, holdout=holdout, through=through, newest=newest, last_day=last_day)


def shift_test(x, pred, start, end):
    """Does demand sit on the right hour? The fit's mean absolute percent error over [start, end) with demand moved one
    hour earlier, left alone, and moved one hour later. The clock that is right gives the smallest error."""
    m = (x.index >= pd.Timestamp(start)) & (x.index < pd.Timestamp(end))
    out = {}
    for s in (-1, 0, 1):
        d = x["demand"].shift(s)
        ok = m & d.notna() & pred.notna()
        out[s] = dict(mape_pct=float(((pred[ok] - d[ok]).abs() / d[ok]).mean() * 100) if ok.sum() else None,
                      bias_pct=float((d[ok].mean() / pred[ok].mean() - 1) * 100) if ok.sum() else None, hours=int(ok.sum()))
    return out


def california(res):
    """California across December 2025. EIA dated its hours one hour late until caiso_join.LATE_TO, and its generation
    series changed on caiso_join.JOIN. For the eight weeks before the first date and the eight weeks from the second, in
    2025 and on the same dates a year earlier: the fit's error with demand an hour early, as read, and an hour late; and
    how far metered demand stood above the fit."""
    x, pred = res["x"], res["pred"]
    late_to, join = pd.Timestamp(cj.LATE_TO).tz_convert("UTC"), pd.Timestamp(cj.JOIN).tz_convert("UTC")
    out = {"late_to": ip.utc_iso(late_to), "join": ip.utc_iso(join), "windows": []}
    for back in (0, 1):
        o = pd.DateOffset(years=back)
        for label, a, b in (("the eight weeks before the hours were dated right", late_to - pd.Timedelta(days=56), late_to),
                            ("the eight weeks from the change in EIA's generation series", join, join + pd.Timedelta(days=56))):
            a2, b2 = a - o, b - o
            out["windows"].append(dict(label=label, start=ip.utc_iso(a2), end=ip.utc_iso(b2), a_year_earlier=bool(back),
                                       shifts={str(k): v for k, v in shift_test(x, pred, a2, b2).items()}))
    return out


def rows_of(ba, res, retrieved, geo):
    """The table's rows for one grid."""
    out = []

    def add(year, var, val, unit, **xk):
        if val is None or (isinstance(val, float) and np.isnan(val)):
            return
        out.append(dict(entity=f"eia930:{ba}", variable=var, ts_utc=f"{year}-01-01T00:00:00Z", value=val, unit=unit, freq="P1Y", geo=geo,
                        market="", node="", source=SOURCE, source_url=METHOD_URL, retrieved_at=retrieved, vintage="", ba=ba.lower(),
                        x_finding=xk.get("finding", ""), x_window=xk.get("window", ""), x_at=xk.get("at", "") or "", x_used=xk.get("used", "")))
    for y, row in res["years"].items():
        for m, g in row.items():
            if not g:
                continue
            k = dict(window=g["window"], used=g["used"], at=g.get("at"))
            add(y, f"{m}_mw", round(g["actual"], 1), "MW", **k)
            add(y, f"{m}_expected_mw", round(g["expected"], 1), "MW", **k)
            add(y, f"{m}_base_mw", round(g["base"], 1), "MW", **k)
            add(y, f"{m}_growth_pct", round(g["growth_pct"], 3), "pct", **k)
            add(y, f"{m}_weather_pct", round(g["weather_pct"], 3), "pct", **k)
            add(y, f"{m}_unexplained_pct", round(g["unexplained_pct"], 3), "pct", finding="yes" if g["finding"] else ("beyond" if g.get("outside") else "no"), **k)
            if g["uncertainty_pct"] is not None:
                add(y, f"{m}_uncertainty_pct", round(g["uncertainty_pct"], 3), "pct", **k)
    for y, row in res["holdout"].items():
        for m, g in row.items():
            if g:
                add(y, f"{m}_holdout_unexplained_pct", round(g["unexplained_pct"], 3), "pct", window="left out of the fit")
    f = res["fit"]
    add(TRAIN[0], "fit_hours", f["hours"], "count")
    add(TRAIN[0], "fit_in_sample_error_pct", round(f["in_sample_mape_pct"], 3), "pct")
    add(TRAIN[0], "fit_left_out_error_pct", round(f["oos_mape_pct"], 3), "pct")
    add(TRAIN[0], "fit_left_out_daily_error_pct", round(f["oos_daily_mape_pct"], 3), "pct")
    return out


def clean(o):
    """JSON without NaN, timestamps or numpy types."""
    if isinstance(o, dict):
        return {str(k): clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean(v) for v in o]
    if isinstance(o, (np.floating, float)):
        return None if np.isnan(o) else round(float(o), 4)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.bool_,)):
        return bool(o)
    if isinstance(o, pd.Timestamp):
        return ip.utc_iso(o)
    return o


def equal_weights(demands, log):
    """The trial with five equal weights a grid in place of the stated ones, from the stations' raw files. Returns
    {BA: {year: {metric: unexplained}}}, or None when the raw files are not on this machine."""
    import noaa_grid_weather as ngw
    try:
        raw, facts, _ = ngw.pull(lambda *a: None, offline=True)
    except Exception as exc:
        log(f"  the trial with equal weights was not made: {type(exc).__name__}: {str(exc)[:160]}")
        return None
    n = {}
    for f in facts.values():
        n[f["ba"]] = n.get(f["ba"], 0) + 1
    _, hours, _, _, _ = ngw.build(raw, facts, weights={c: 1.0 / n[f["ba"]] for c, f in facts.items()})
    out = {}
    for ba in BAS:
        r = analyse(demands[ba][0], hours[ba.lower()], dg.AREAS[ba]["tz"], ba)
        out[ba] = {y: {m: (g["unexplained_pct"] if g else None) for m, g in row.items()} for y, row in r["years"].items()}
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="demand growth with the weather taken out")
    ap.add_argument("--out-dir")
    ap.add_argument("--snapshot", action="store_true", help="also write the site's copy, site/data/demand_weather.json")
    ap.add_argument("--cache", help="a folder keeping each grid's hourly demand between runs")
    ap.add_argument("--weather", help="the hourly weather table (default warehouse/output/noaa_grid_weather_hourly.csv)")
    ap.add_argument("--no-equal", action="store_true", help="skip the trial with equal station weights")
    args = ap.parse_args(argv)
    weather_path = args.weather or os.path.join(ip.OUT_DIR, WEATHER + ".csv")
    if args.out_dir:
        raw_dir = ip.RAW_DIR
        ip.set_out_dir(args.out_dir)
        ip.RAW_DIR = raw_dir   # the trial with equal weights reads the stations' raw files where the pull saved them
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = pd.Timestamp.now(tz="UTC").strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"demand_weather_{run_id}.log"))
    log(f"ERW demand_weather run {run_id}: fit on {TRAIN[0]} to {TRAIN[-1]}; weather {os.path.relpath(weather_path, ROOT)}")
    weather = read_weather(weather_path)
    retrieved = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
    demands, results, plain, rows, books = {}, {}, {}, [], []
    for ba in BAS:
        demands[ba] = read_demand(ba, args.cache)
        books.append(os.path.relpath(demands[ba][1], ROOT).replace("\\", "/"))
        tz = dg.AREAS[ba]["tz"]
        results[ba] = analyse(demands[ba][0], weather[ba], tz, ba)
        p = analyse(demands[ba][0], weather[ba], tz, ba, PLAIN)
        plain[ba] = p["fit"]["oos_mape_pct"]
        f = results[ba]["fit"]
        log(f"  {dg.AREAS[ba]['name']}: {f['hours']:,} hours in the fit ({f['hours_not_used']:,} of {f['hours_held']:,} held hours of {TRAIN[0]} to {TRAIN[-1]} "
            f"not used by the rule, {f['shed_hours']} left out as load shed); error on hours left out {f['oos_mape_pct']:.2f} percent "
            f"(days {f['oos_daily_mape_pct']:.2f}; in the fit {f['in_sample_mape_pct']:.2f}; with heating and cooling degrees only {plain[ba]:.2f}); "
            f"newest year {results[ba]['newest']} through {results[ba]['through']}")
        rows += rows_of(ba, results[ba], retrieved, dg.AREAS[ba]["geo"])
    eq = None if args.no_equal else equal_weights(demands, log)
    moved = None
    if eq:
        diffs = [(abs(eq[ba][y][m] - g["unexplained_pct"]), ba, y, m) for ba in BAS for y, row in results[ba]["years"].items()
                 for m, g in row.items() if g and eq[ba].get(y, {}).get(m) is not None]
        e_only = [d for d in diffs if d[3] == "energy"]
        moved = dict(largest_any=max(diffs)[0], largest_any_where=list(max(diffs)[1:]), largest_energy=max(e_only)[0],
                     largest_energy_where=list(max(e_only)[1:]), figures=len(diffs))
        log(f"  with five equal weights a grid: the year's energy not explained moves by at most {moved['largest_energy']:.2f} points "
            f"({moved['largest_energy_where']}); any figure by at most {moved['largest_any']:.2f} ({moved['largest_any_where']})")
    ca = california(results["CISO"])
    t = pd.DataFrame(rows)
    cols = ip.SERIES_COLS + ["ba", "x_finding", "x_window", "x_at", "x_used"]
    through = min(f"{r['newest']}-{r['through']}" for r in results.values())   # the last whole local day every grid's newest year counts
    header = [
        "Energy Research Warehouse (ERW): demand growth with the weather taken out, the seven ISO balancing authorities, by year (session 126)",
        "Shape: series (docs/datastandard.md v0), partition column ba; freq P1Y, ts_utc the first day of the local year. For each of energy (the mean of the year's hours), "
        "summer_peak (the highest hour of June to September), winter_peak (the highest hour of December of the year before to February) and overnight_min (the mean over the year's "
        "days of the lowest hour from midnight to 6 am, local): <figure>_mw metered, <figure>_expected_mw the fit's (the customers of 2019 to 2021 in that year's weather), "
        "<figure>_base_mw the mean of 2019 to 2021, <figure>_growth_pct, <figure>_weather_pct (the growth the weather explains), <figure>_unexplained_pct (growth minus weather; "
        "x_finding yes when it is larger than its uncertainty, beyond when the peak's hour was hotter or colder than any hour the fit was made on) and <figure>_uncertainty_pct "
        "(the largest miss of the years left out of the fit in turn; for a peak, never under the fit's error on one hour left out). "
        "<figure>_holdout_unexplained_pct on a row of 2019 to 2021: that year left out of the fit. fit_* on the row of 2019: the fit's hours and its mean absolute percent error.",
        "The remainder is growth the temperature does not explain: population, electrification, industry, datacenters, solar behind the meter, prices and efficiency together. The warehouse cannot split them.",
        f"Retrieved: {run_id} (UTC) by warehouse/derived/demand_weather.py",
        f"Run log: warehouse/output/logs/demand_weather_{run_id}.log",
        f"Source: {SOURCE} ERW derived table, demand growth with the weather taken out (docs/methods/demand_weather.md), {METHOD_URL}",
        f"Derived from: {WEATHER}",
        "Demand: EIA-930 hourly demand (EIA's Adjusted demand), read from the workbooks " + ", ".join(books),
        "input sources: eia:gridmonitor (https://www.eia.gov/electricity/gridmonitor/knownissues/xls/<BA>.xlsx); noaa:isd_lite; noaa:lcd_v2",
        f"An hour of demand is used when it passes impossible_hours.screen (session 118). The fit: {TRAIN[0]} to {TRAIN[-1]}, 48 kinds of hour, terms {', '.join(FEATURES[1:])}. "
        f"The newest year is through {through} (local days); its energy and overnight minimum are compared over the same days of {TRAIN[0]} to {TRAIN[-1]}.",
        "License: public. A derived table inherits the most restrictive license of its inputs (Decision 23).",
        "Method: docs/methods/demand_weather.md",
    ]
    path = os.path.join(ip.OUT_DIR, NAME + ".csv")
    if os.path.exists(path):
        os.remove(path)   # rebuilt whole: a figure a later run no longer holds must leave the table
    ip.write_csv(t[cols], NAME, header, log, cols=cols)
    summary = dict(
        built_at=retrieved, table=NAME, train=list(TRAIN), through=through, metrics=list(METRICS), labels=LABEL,
        grids={ba: dict(name=dg.AREAS[ba]["name"], tz=dg.AREAS[ba]["tz"], fit={**results[ba]["fit"], "plain_oos_mape_pct": plain[ba]},
                        holdout=results[ba]["holdout"], years=results[ba]["years"], through=results[ba]["through"], newest=results[ba]["newest"])
               for ba in BAS},
        equal_weights=dict(moved=moved, unexplained=eq) if eq else None, california=ca, shed=SHED,
    )
    wsum = os.path.join(ROOT, "warehouse", "raw", "noaa_grid_weather", "summary.json")
    if os.path.exists(wsum):
        with open(wsum, encoding="utf-8") as f:
            summary["weather"] = json.load(f)
    summary = clean(summary)
    out_json = os.path.join(ip.OUT_DIR if args.out_dir else os.path.join(ROOT, "runs"), "demand_weather_summary.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=1)
    if args.snapshot:
        with open(SITE_FILE, "w", encoding="utf-8", newline="\n") as f:
            json.dump(summary, f, indent=1)
            f.write("\n")
        log(f"  the site's copy: {os.path.relpath(SITE_FILE, ROOT)}")
    if not args.out_dir:
        ip.update_sources([dict(source=SOURCE, publisher="Energy Research Warehouse (ERW)", report="ERW derived table, demand growth with the weather taken out (docs/methods/demand_weather.md)",
                                report_url=METHOD_URL, document_list="", license="public", tables=[NAME])])
        ip.write_status("demand_weather", run_id, [dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows")])
    print(f"{NAME}: {len(t):,} rows; summary {os.path.relpath(out_json, ROOT)}")
    log.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
