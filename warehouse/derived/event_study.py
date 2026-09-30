#!/usr/bin/env python3
"""Event studies of the Historical Event Analyzer's events (session 47): the effect of each event on each grid's daily
demand served and, where held, on ERCOT's daily hub price, against weekday-aligned baseline days.

Energy Research Warehouse (ERW) derived table, research. Writes one series table,

    warehouse/output/event_study_estimates.csv    tier derived, public; partition columns ba and event

from event_window_daily (every event and grid in it) and, for the hour-of-day profile, the hourly demand of the EIA-930
extracts the event builder read (warehouse/raw/eia930_emissions/<run>/<ba>_hours.csv). No request, no model.

    python warehouse/derived/event_study.py

Specification (docs/methods/event_study.md), per event, grid and outcome (daily demand served, demand_mwh, MWh; the
daily mean real-time hub price, rt_mean, USD/MWh), on the event's window days and its baseline days:

    y_d = a + sum_k b_k 1[d = event day k] + dow effects (Monday the reference) + year effects + e_d

- Year effects are coded to sum to zero over the baseline years, and the event year takes none: the event year's
  counterfactual level is the mean of its baseline years' levels. With one baseline year there is no year contrast.
- Each event day's effect b_k is the day's value less its counterfactual, the baseline-only fit (a, dow, year) at that
  day: exactly the dummy regression's coefficient. Its standard error is sqrt(s2 + x' V x): the baseline residual
  variance s2 (the day's own noise) plus the variance of the fitted counterfactual, V the heteroskedasticity-robust
  (HC1) covariance of the baseline fit. A one-day dummy has a residual of zero, so a robust covariance alone would leave
  the day's own noise out.
- The pooled effect is one indicator for every window day in the same regression, with HC1 standard errors.
- Intervals are estimate +/- 1.96 standard errors (normal, 95 percent).
- counterfactual_mean: the mean counterfactual over the window days, for reading the pooled effect as a percent.
- Hour-of-day profile (demand only, where an extract is held): the pooled specification run on each local hour's
  demand (MW, the hour's MWh) separately.
Temperature is not held: no estimate controls for weather.

Variables: <outcome>_effect_day (ts_utc the event day), <outcome>_effect_pooled and <outcome>_counterfactual_mean
(ts_utc the window's first day), demand_mw_effect_hHH (ts_utc the window's first day). value is the estimate; x_std_error,
x_ci_low, x_ci_high, x_n (days, or hours, in the regression) and x_spec (the specification id) follow.
"""

import datetime as dt
import glob
import os
import sys
import traceback

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, HERE)
import iso_prices as ip  # noqa: E402

NAME = "event_study_estimates"
SOURCE = "erw:event_study"
METHOD_URL = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/event_study.md"
SPEC = "dow_year_mean_v1"
Z = 1.959963984540054
COLS = ip.SERIES_COLS + ["ba", "event", "x_std_error", "x_ci_low", "x_ci_high", "x_n", "x_spec", "x_term"]
OUTCOMES = {"demand_mwh": "MWh", "rt_mean": "USD/MWh"}
# The event windows, local dates inclusive: warehouse/derived/event_window.py (EVENTS, MULTI); tests check they match
WINDOWS = {
    "uri_2021": ("2021-02-07", "2021-02-24"),
    "covid_2020": ("2020-03-01", "2020-05-31"),
    "caiso_heat_2020": ("2020-08-10", "2020-08-24"),
    "elliott_2022": ("2022-12-19", "2022-12-29"),
    "ercot_heat_2023": ("2023-08-01", "2023-09-10"),
}
# each BA's local day, as event_window.py reads the extracts (COVID's time zones)
TZ = {"ciso": "America/Los_Angeles", "erco": "America/Chicago", "isne": "America/New_York", "miso": "EST",
      "nyis": "America/New_York", "pjm": "America/New_York", "swpp": "America/Chicago", "us48": "America/New_York"}


def design(dates, event, years_base, pooled):
    """The regression's columns: intercept, [pooled indicator], dow (Tuesday to Sunday), year contrasts."""
    d = pd.to_datetime(pd.Series(dates))
    cols = [np.ones(len(d))]
    names = ["intercept"]
    if pooled:
        cols.append(np.asarray(event, dtype=float))
        names.append("pooled")
    for k in range(1, 7):
        cols.append((d.dt.dayofweek == k).to_numpy(dtype=float))
        names.append(f"dow{k}")
    yr = d.dt.year.to_numpy()
    if len(years_base) >= 2:
        last = years_base[-1]
        for y in years_base[:-1]:
            cols.append(np.where(event, 0.0, (yr == y).astype(float) - (yr == last).astype(float)))
            names.append(f"year{y}")
    return np.column_stack(cols), names


def ols_hc1(X, y):
    """OLS coefficients, HC1 covariance, residuals, and the residual variance."""
    n, k = X.shape
    xtx_inv = np.linalg.pinv(X.T @ X)
    b = xtx_inv @ X.T @ y
    e = y - X @ b
    meat = (X * (e ** 2)[:, None]).T @ X
    V = xtx_inv @ meat @ xtx_inv * (n / (n - k))
    s2 = float(e @ e) / (n - k)
    return b, V, e, s2


def drop_empty(X, names):
    """Columns that are all zero (a weekday or year absent from the sample) are dropped, so X'X is invertible."""
    keep = [j for j in range(X.shape[1]) if np.any(X[:, j] != 0)]
    return X[:, keep], [names[j] for j in keep]


def estimate(dates, y, event):
    """Per-day and pooled effects for one series. dates: local days (YYYY-MM-DD); event: booleans."""
    dates = list(dates)
    y = np.asarray(y, dtype=float)
    event = np.asarray(event, dtype=bool)
    years_base = sorted({int(d[:4]) for d, ev in zip(dates, event) if not ev})
    # the baseline-only fit: the counterfactual of each event day
    Xall, nall = design(dates, event, years_base, pooled=False)
    Xb, nb = drop_empty(Xall[~event], nall)
    b, V, _, s2 = ols_hc1(Xb, y[~event])
    Xe = Xall[event][:, [nall.index(c) for c in nb]]
    cf = Xe @ b
    days = []
    for i, d in enumerate([d for d, ev in zip(dates, event) if ev]):
        se = float(np.sqrt(s2 + Xe[i] @ V @ Xe[i]))
        est = float(y[event][i] - cf[i])
        days.append(dict(day=d, estimate=est, se=se, cf=float(cf[i])))
    # the pooled regression
    Xp, npn = drop_empty(*design(dates, event, years_base, pooled=True))
    bp, Vp, _, _ = ols_hc1(Xp, y)
    j = npn.index("pooled")
    pooled = dict(estimate=float(bp[j]), se=float(np.sqrt(Vp[j, j])), n=len(y))
    return dict(days=days, pooled=pooled, cf_mean=float(np.mean(cf)), n=len(y), n_base=int((~event).sum()))


def read_window_table():
    path = os.path.join(ip.OUT_DIR, "event_window_daily.csv")
    n = 0
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.startswith("#"):
                break
            n += 1
    df = pd.read_csv(path, skiprows=n, dtype=str, keep_default_na=False)
    return df[(df["freq"] == "P1D") & df["variable"].isin(list(OUTCOMES))].copy()


def extract_path(ba):
    """The newest hourly extract of a BA the event builder can have read, or None."""
    files = sorted(glob.glob(os.path.join(ip.RAW_DIR, "eia930_emissions", "*", f"{ba}_hours.csv")))
    return files[-1] if files else None


def row(entity, variable, ts, est, se, n, unit, freq, ba, event, term, geo=""):
    ci = (est - Z * se, est + Z * se) if se is not None else (None, None)
    f = lambda v: "" if v is None else repr(round(float(v), 6))  # noqa: E731
    return dict(entity=entity, variable=variable, ts_utc=f"{ts}T00:00:00Z", value=round(float(est), 6), unit=unit,
                freq=freq, geo=geo, market="", node="", source=SOURCE, source_url=METHOD_URL, retrieved_at=RETRIEVED,
                vintage="", ba=ba, event=event, x_std_error=f(se), x_ci_low=f(ci[0]), x_ci_high=f(ci[1]), x_n=str(n),
                x_spec=SPEC, x_term=term)


RETRIEVED = ""


def main():
    global RETRIEVED
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    RETRIEVED = f"{run_id[:4]}-{run_id[4:6]}-{run_id[6:8]}T{run_id[9:11]}:{run_id[11:13]}:{run_id[13:15]}Z"
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    log = ip.Log(os.path.join(ip.LOG_DIR, f"event_study_{run_id}.log"))
    status = dict(table=NAME, market="all", status="ok", detail="")
    try:
        df = read_window_table()
        rows, hourly_used = [], []
        for (event, entity, variable), g in df.groupby(["event", "entity", "variable"]):
            start, end = WINDOWS[event]
            g = g.sort_values("ts_utc")
            dates = g["ts_utc"].str[:10].tolist()
            ev = [start <= d <= end for d in dates]
            r = estimate(dates, pd.to_numeric(g["value"]).to_numpy(), ev)
            unit, ba, geo = OUTCOMES[variable], g["ba"].iloc[0], g["geo"].iloc[0]
            for d in r["days"]:
                rows.append(row(entity, f"{variable}_effect_day", d["day"], d["estimate"], d["se"], r["n"], unit, "P1D",
                                ba, event, f"event day {d['day']}", geo))
            p = r["pooled"]
            rows.append(row(entity, f"{variable}_effect_pooled", start, p["estimate"], p["se"], r["n"], unit, "P1D", ba,
                            event, "pooled event-window effect, per day", geo))
            rows.append(row(entity, f"{variable}_counterfactual_mean", start, r["cf_mean"], None, r["n"], unit, "P1D",
                            ba, event, "mean counterfactual over the window days (baseline fit)", geo))
            log(f"{event} {entity} {variable}: pooled {p['estimate']:.2f} (se {p['se']:.2f}), n {r['n']} "
                f"({r['n_base']} baseline days)")
            # the hour-of-day profile of demand, where the extract is held
            if variable == "demand_mwh" and ba in TZ:
                path = extract_path(ba)
                if not path:
                    log(f"  {event} {entity}: no hourly extract on this machine; no hour profile")
                    continue
                hn = 0
                with open(path, encoding="utf-8") as f:
                    for line in f:
                        if not line.startswith("#"):
                            break
                        hn += 1
                h = pd.read_csv(path, skiprows=hn, usecols=["ts_utc", "demand_mwh"])
                local = pd.to_datetime(h["ts_utc"], utc=True).dt.tz_convert(TZ[ba])
                h["day"], h["hour"] = local.dt.strftime("%Y-%m-%d"), local.dt.hour
                h = h[h["day"].isin(set(dates))].dropna(subset=["demand_mwh"])
                for hour in range(24):
                    hh = h[h["hour"] == hour].drop_duplicates("day")  # the repeated hour of a fall-back day: the first
                    if hh["day"].nunique() < len(dates) * 0.9:
                        continue
                    hd = hh["day"].tolist()
                    hr = estimate(hd, hh["demand_mwh"].to_numpy(dtype=float), [start <= d <= end for d in hd])
                    q = hr["pooled"]
                    rows.append(row(entity, f"demand_mw_effect_h{hour:02d}", start, q["estimate"], q["se"], hr["n"], "MW",
                                    "PT1H", ba, event, f"pooled effect at local hour {hour:02d}", geo))
                hourly_used.append(f"{event} {ba}: {os.path.relpath(path, ROOT)}")
        s = pd.DataFrame(rows)[COLS]
        header = [
            "Energy Research Warehouse (ERW): event studies, the estimated effect of each event on each grid's daily "
            "demand served and ERCOT's daily hub price (derived, research, session 47)",
            "Shape: series (docs/datastandard.md v0), partition columns ba and event. value is the estimate; x_std_error, "
            "x_ci_low, x_ci_high (95 percent, estimate +/- 1.96 standard errors), x_n (days or hours in the regression), "
            "x_spec, x_term. <outcome>_effect_day at the event day; <outcome>_effect_pooled and "
            "<outcome>_counterfactual_mean at the window's first day; demand_mw_effect_hHH, the hour-of-day profile.",
            f"Specification {SPEC}: event-day indicators (and one pooled indicator), day-of-week effects, year effects "
            "summing to zero over the baseline years (the event year's counterfactual is their mean); HC1 standard "
            "errors; a day's standard error adds the baseline residual variance (docs/methods/event_study.md).",
            "Temperature is not held: no estimate controls for weather.",
            f"Retrieved: {run_id} (UTC) by warehouse/derived/event_study.py",
            f"Run log: warehouse/output/logs/event_study_{run_id}.log",
            f"Source: {SOURCE} ERW derived table, event study method (docs/methods/event_study.md), {METHOD_URL}",
            "Derived from: event_window_daily",
            "  hourly demand (the hour-of-day profile) from the EIA-930 extracts: " + ("; ".join(hourly_used) or "none"),
            "License: public. A derived table inherits the most restrictive license of its inputs (Decision 23).",
        ]
        path = os.path.join(ip.OUT_DIR, NAME + ".csv")
        if os.path.exists(path):
            os.remove(path)  # rewritten whole each run: every estimate comes from this run
        ip.write_csv(s, NAME, header, log, cols=COLS, key=["entity", "variable", "ts_utc", "event"])
        ip.update_sources([dict(source=SOURCE, publisher="Energy Research Warehouse (ERW)",
                                report="Event study estimates (warehouse/derived/event_study.py)", report_url=METHOD_URL,
                                document_list="", license="public", tables=[NAME])])
        status["detail"] = f"{len(s)} estimates for {s.groupby(['event', 'entity']).ngroups} event-grid pairs"
        print(f"event_study: {status['detail']}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED:\n{tb}")
        print(f"event_study FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        status.update(status="failed", detail=tb.strip().splitlines()[-1][:300])
    ip.write_status("event_study", run_id, [status])
    log.close()
    return 0 if status["status"] == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
