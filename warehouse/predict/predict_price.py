"""ERW forecast (predict): the forecast of a grid's day-ahead hub price, its methods and its walk-forward backtest.

Session 10600, chain 730 (part E). Method note: docs/methods/predict_price.md.

The forecast of the day-ahead price of a place's day T is taken as made at 14:00 UTC on day T-1, before any grid
forecast here publishes its day-ahead results for T. At that hour the hub's day-ahead prices are held through day T-1
(each grid publishes a day's prices the day before it), the place's demand through 23:00 local on day T-3 (EIA's
six-month files of T-2), and Henry Hub as published at least ten days before. So the price methods read the hub's
prices through day A = T - hp (hp = 1), and the demand through day T - hd (hd = 3):

  yesterday   the same local hour of day A (the price of day T-1, already published)
  week_ago    the same local hour of day T-7
  regression  one least-squares regression a local hour, in USD/MWh (not logs: prices fall below zero), refit for
              every day T on the 730 days before it whose price was held when T's forecast was made: on the price of
              the same hour on day A, day A's mean price, the same hour on T-7, the mean of the seven days ending on
              A, the ERW's own demand forecast for the hour (the demand regression made with horizon hd) over the
              mean demand of the seven days ending on T-hd, that ratio squared, Henry Hub, the weekday and holidays of
              T, and one yearly wave.

The band: the 10th and 90th percentile of the method's own past errors (actual less forecast, USD/MWh) at the same
local hour over the 365 days held when the forecast is made.
"""
import numpy as np
import pandas as pd

import predict_demand as demand

PRICE_MADE_HOUR = 14
FIT_DAYS = 730
MIN_FIT_DAYS = 300
METHODS = ["yesterday", "week_ago", "regression"]
FEATURES = ["const", "p_same_hour_A", "p_mean_A", "p_same_hour_T7", "p_mean_week_A", "load_ratio", "load_ratio_sq", "henry_hub",
            "dow_T_mon", "dow_T_tue", "dow_T_wed", "dow_T_thu", "dow_T_fri", "dow_T_sat", "hol_T", "bridge_T", "sin1_T", "cos1_T"]
GAS_LAG_DAYS = 10
MAPE_FLOOR = 5.0
SPIKE_Q = 0.99


def gas_by_day(gas, days, lag=GAS_LAG_DAYS):
    """For each local day T of `days`: the latest Henry Hub price dated at least `lag` days before day T-1 (the day the
    forecast is made), USD/MMBtu. `gas` is a Series indexed by date."""
    g = gas.sort_index()
    g.index = pd.DatetimeIndex(g.index).tz_localize(None).normalize()
    cut = days - pd.Timedelta(days=1 + lag)
    pos = g.index.searchsorted(cut, side="right") - 1
    vals = np.where(pos >= 0, g.to_numpy()[np.clip(pos, 0, None)], np.nan)
    return vals


def features(Mp, Dfc, Md, gas_vals, hp=1, hd=3):
    """X[i, k, :] for target day Mp.index[i], local hour k, and Y[i, k] the day's price. Mp: the hub's day-ahead price
    by local day and hour; Dfc: the demand regression's forecast for the same days (made with horizon hd), aligned to
    Mp's days; Md: the demand matrix, aligned likewise; gas_vals: Henry Hub by day (gas_by_day)."""
    days = Mp.index
    n = len(days)
    raw = Mp.to_numpy(dtype=float)
    filled = raw.copy()
    lone = np.isnan(raw[:, 1:23]) & np.isfinite(raw[:, 0:22]) & np.isfinite(raw[:, 2:24])
    filled[:, 1:23] = np.where(lone, (raw[:, 0:22] + raw[:, 2:24]) / 2.0, raw[:, 1:23])
    day_mean = np.mean(filled, axis=1)

    def lag(a, d):
        out = np.full_like(a, np.nan, dtype=float)
        if d < n:
            out[d:] = a[:n - d]
        return out

    p_A = lag(filled, hp)
    pm_A = lag(day_mean, hp)
    p_7 = lag(filled, 7)
    week = pd.Series(day_mean).rolling(7, min_periods=5).mean().to_numpy()
    pw_A = lag(week, hp)
    dmean = np.mean(Md.to_numpy(dtype=float), axis=1)
    dweek = pd.Series(dmean).rolling(7, min_periods=5).mean().to_numpy()
    dw_A = lag(dweek, hd)
    ratio = Dfc / dw_A[:, None]
    hol, bri = demand.calendar(days)
    dow = days.dayofweek.to_numpy()
    doy = days.dayofyear.to_numpy() / 365.25
    common = np.column_stack([pm_A, pw_A, gas_vals] + [(dow == d).astype(float) for d in range(6)]
                             + [hol.astype(float), bri.astype(float), np.sin(2 * np.pi * doy), np.cos(2 * np.pi * doy)])
    X = np.empty((n, 24, len(FEATURES)))
    for k in range(24):
        X[:, k, 0] = 1.0
        X[:, k, 1] = p_A[:, k]
        X[:, k, 2] = common[:, 0]
        X[:, k, 3] = p_7[:, k]
        X[:, k, 4] = common[:, 1]
        X[:, k, 5] = ratio[:, k]
        X[:, k, 6] = ratio[:, k] ** 2
        X[:, k, 7] = common[:, 2]
        X[:, k, 8:] = common[:, 3:]
    return X, raw


def band(Mp, P, h, days=demand.BAND_DAYS, min_n=demand.BAND_MIN, q=demand.BAND_Q):
    """(lo, hi): P plus the q-quantiles of the errors actual - P at the same local hour, over target days up to i-h."""
    e = Mp.to_numpy(dtype=float) - P
    E = pd.DataFrame(np.where(np.isfinite(e), e, np.nan))
    roll = E.rolling(days, min_periods=min_n)
    return P + roll.quantile(q[0]).shift(h).to_numpy(), P + roll.quantile(q[1]).shift(h).to_numpy()


def place_forecasts(price, tz, dem_series, dem_tz, gas, hp=1, hd=3):
    """One hub's backtest for one place: price a Series (UTC hours) of the hub's day-ahead price; dem_series the
    place's demand (UTC hours); gas Henry Hub by date. Returns dict(frame, M, P, lo, hi, hp, hd)."""
    frame = demand.local_frame(price, tz)
    last = demand.last_whole_day(frame, tz)
    frame = frame[frame["day"] <= last]
    M = demand.matrix(frame)
    M = M.reindex(pd.date_range(M.index.min(), M.index.max() + pd.Timedelta(days=hp), freq="D"))
    dres = demand.place_forecasts(dem_series, dem_tz, h=hd)
    Dm = dres["M"]
    Dfc = pd.DataFrame(dres["P"]["regression"], index=Dm.index).reindex(M.index).to_numpy()
    Md = Dm.reindex(M.index)
    X, Y = features(M, Dfc, Md, gas_by_day(gas, M.index), hp=hp, hd=hd)
    reg, B = demand.walk_ols(X, Y, hp, FIT_DAYS, MIN_FIT_DAYS)
    raw = M.to_numpy(dtype=float)
    n = len(raw)
    y = np.full_like(raw, np.nan)
    w = np.full_like(raw, np.nan)
    y[hp:] = raw[:n - hp]
    w[7:] = raw[:n - 7]
    P = {"yesterday": y, "week_ago": w, "regression": reg}
    lo, hi = {}, {}
    for m, arr in P.items():
        lo[m], hi[m] = band(M, arr, hp)
    return {"frame": frame, "M": M, "P": P, "lo": lo, "hi": hi, "B": B, "h": hp, "hd": hd}
