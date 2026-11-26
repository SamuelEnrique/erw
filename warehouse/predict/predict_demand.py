"""ERW forecast (predict): the forecast of a place's hourly demand, its methods and its walk-forward backtest.

Session 10600, chain 730 (part D). Method note: docs/methods/predict.md, which states every rule below in words.

The forecast of a place's day T (in the place's own clock) is made from the place's demand through the last whole
local day held, day A = T - h: h = 2 for the day-ahead forecast (made at 20:00 UTC on T-1, when the warehouse holds
demand through 23:00 local on T-2; docs/reviews/predict-ground-2026-11-26.md). Every method is held to that:

  yesterday   the same local hour of day A (the latest whole day held)
  week_ago    the same local hour of day T-7
  regression  one least-squares regression a local hour, refit for every day T on the FIT_DAYS days before it whose
              demand was held when T's forecast was made (target days up to A): the log of the hour's demand on
              the log of the same hour on day A, the log of day A's mean, the log of the same hour on T-7, the log of
              the mean of the seven days ending on A, the day of the week of T and of A, the holidays and bridge days
              of T, of A and of T-7, and two yearly waves of T's day of the year. No weather: no dated weather forecast
              is held (the ground, section 2).

The band of a method is the 10th and 90th percentile of that method's own past errors at the same local hour (the log
of actual over forecast, out of sample), over the BAND_DAYS days of target days held when the forecast is made.

Nothing here reads a row dated after the forecast's information cut: `features` builds day T's row from days A and
earlier and from T-7 (h <= 7 is required), and the fit for T uses target days up to A only. tests/test_predict.py
holds both rules.
"""
import numpy as np
import pandas as pd
from pandas.tseries.holiday import USFederalHolidayCalendar

FIRST_TARGET = pd.Timestamp("2019-07-01")
FIT_DAYS = 730
MIN_FIT_DAYS = 300
BAND_DAYS = 365
BAND_MIN = 60
BAND_Q = (0.10, 0.90)
METHODS = ["yesterday", "week_ago", "regression"]
FEATURES = ["const", "l_same_hour_A", "l_mean_A", "l_same_hour_T7", "l_mean_week_A",
            "dow_T_mon", "dow_T_tue", "dow_T_wed", "dow_T_thu", "dow_T_fri", "dow_T_sat",
            "dow_A_mon", "dow_A_tue", "dow_A_wed", "dow_A_thu", "dow_A_fri", "dow_A_sat",
            "hol_T", "bridge_T", "hol_A", "bridge_A", "hol_T7", "bridge_T7",
            "sin1_T", "cos1_T", "sin2_T", "cos2_T"]


def calendar(days):
    """(holiday, bridge) booleans for each date of `days` (a naive DatetimeIndex of midnights).

    holiday: a US federal holiday or its observed day (pandas' USFederalHolidayCalendar, a rule, not a table).
    bridge: the day after Thanksgiving, 24 December, and 26 to 31 December."""
    lo, hi = days.min() - pd.Timedelta(days=400), days.max() + pd.Timedelta(days=400)
    hol = USFederalHolidayCalendar().holidays(lo, hi)
    thanks = hol[(hol.month == 11) & (hol.day >= 22) & (hol.dayofweek == 3)]
    holiday = np.asarray(days.isin(hol))
    bridge = np.asarray(days.isin(thanks + pd.Timedelta(days=1)) | ((days.month == 12) & ((days.day == 24) | (days.day >= 26))))
    return holiday, bridge & ~holiday


def local_frame(s, tz):
    """The place's hours with their local day and hour: DataFrame(ts, value, day, hour), one row a UTC hour."""
    s = s.dropna()
    loc = s.index.tz_convert(tz)
    return pd.DataFrame({"ts": s.index, "value": s.to_numpy(dtype=float),
                         "day": loc.tz_localize(None).normalize(), "hour": loc.hour})


def matrix(frame):
    """M[day, hour]: the local day's demand by local hour (the repeated autumn hour: the mean of its two), every day from
    the first to the last held, NaN where not held."""
    M = frame.groupby(["day", "hour"])["value"].mean().unstack("hour").reindex(columns=range(24))
    return M.reindex(pd.date_range(M.index.min(), M.index.max(), freq="D"))


def features(M, h):
    """X[i, k, :] the regression's row for target day M.index[i] and local hour k, made with horizon h; Y[i, k] the log
    of the demand. A single missing hour inside a day is taken as the mean of its two neighbours for the features only
    (the 23-hour day of the spring change, a lone gap); never for a target or a score."""
    if not 1 <= h <= 7:
        raise ValueError("horizon must be 1 to 7 days: week_ago reads day T-7")
    days = M.index
    n = len(days)
    raw = M.to_numpy(dtype=float)
    filled = raw.copy()
    lone = np.isnan(raw[:, 1:23]) & np.isfinite(raw[:, 0:22]) & np.isfinite(raw[:, 2:24])
    filled[:, 1:23] = np.where(lone, (raw[:, 0:22] + raw[:, 2:24]) / 2.0, raw[:, 1:23])
    with np.errstate(divide="ignore", invalid="ignore"):
        lf = np.log(np.where(filled > 0, filled, np.nan))
        ly = np.log(np.where(raw > 0, raw, np.nan))
    day_mean = np.log(np.mean(np.exp(lf), axis=1))   # NaN unless every hour of the day is there

    def lag(a, d):
        out = np.full_like(a, np.nan)
        if d < n:
            out[d:] = a[:n - d]
        return out

    l_A = lag(lf, h)
    l_mean_A = lag(day_mean, h)
    l_T7 = lag(lf, 7)
    dm = pd.Series(np.exp(day_mean))
    week = np.log(dm.rolling(7, min_periods=5).mean().to_numpy())
    l_week_A = lag(week, h)
    hol, bri = calendar(days)
    dow = days.dayofweek.to_numpy()
    dow_A = (days - pd.Timedelta(days=h)).dayofweek.to_numpy()  # the calendar's, known for every day
    hol_A, bri_A = lag(hol.astype(float), h), lag(bri.astype(float), h)
    hol_7, bri_7 = lag(hol.astype(float), 7), lag(bri.astype(float), 7)
    doy = days.dayofyear.to_numpy() / 365.25
    common = np.column_stack([np.ones(n), l_mean_A, l_week_A]
                             + [(dow == d).astype(float) for d in range(6)]
                             + [(dow_A == d).astype(float) for d in range(6)]
                             + [hol.astype(float), bri.astype(float), hol_A, bri_A, hol_7, bri_7,
                                np.sin(2 * np.pi * doy), np.cos(2 * np.pi * doy), np.sin(4 * np.pi * doy), np.cos(4 * np.pi * doy)])
    X = np.empty((n, 24, len(FEATURES)))
    for k in range(24):
        X[:, k, 0] = common[:, 0]
        X[:, k, 1] = l_A[:, k]
        X[:, k, 2] = common[:, 1]
        X[:, k, 3] = l_T7[:, k]
        X[:, k, 4:] = common[:, 2:]
    return X, ly


def regression(M, h, fit_days=FIT_DAYS, min_fit=MIN_FIT_DAYS):
    """P[i, k]: the regression's forecast for day i, hour k, each day's 24 fits made on target days i-h-fit_days+1 to
    i-h only (an expanding window until fit_days are held); NaN where fewer than min_fit days could be used.
    Also returns the coefficient array B[i, k, :] (NaN where no fit)."""
    X, Y = features(M, h)
    L, B = walk_ols(X, Y, h, fit_days, min_fit)
    return np.exp(L), B


def walk_ols(X, Y, h, fit_days=FIT_DAYS, min_fit=MIN_FIT_DAYS):
    """The walk-forward least squares shared by every regression of the forecast: for each day i and hour k, the
    coefficients fitted on rows j = i-h-fit_days+1 to i-h (those held, with every regressor present) and the fitted
    value X[i, k] . beta. Returns (L, B): L[i, k] the fitted value (NaN without a fit or a full row), B the
    coefficients. Each window is solved from its own rows by numpy.linalg.lstsq (an SVD), the plainest form, which
    replication/predict/replicate.py repeats; until session 10601 the windows were solved from differences of running
    normal equations, which gave the same forecasts at the stored precision."""
    n, K, p = X.shape
    valid = np.isfinite(X).all(axis=2) & np.isfinite(Y)
    cn = np.concatenate([np.zeros((1, K)), np.cumsum(valid, axis=0)])
    P = np.full((n, K), np.nan)
    B = np.full((n, K, p), np.nan)
    for i in range(n):
        hi = i - h + 1            # rows j < hi, i.e. j <= i - h
        if hi <= 0:
            continue
        lo = max(0, hi - fit_days)
        ok = (cn[hi] - cn[lo] >= min_fit) & np.isfinite(X[i]).all(axis=1)
        for k in np.flatnonzero(ok):
            v = valid[lo:hi, k]
            beta = np.linalg.lstsq(X[lo:hi, k][v], Y[lo:hi, k][v], rcond=None)[0]
            B[i, k] = beta
            P[i, k] = float(X[i, k] @ beta)
    return P, B


def simple(M, h):
    """The two simple methods: P_yesterday[i, k] = M[i-h, k], P_week_ago[i, k] = M[i-7, k] (the raw hours)."""
    raw = M.to_numpy(dtype=float)
    n = len(raw)
    y = np.full_like(raw, np.nan)
    w = np.full_like(raw, np.nan)
    y[h:] = raw[:n - h]
    w[7:] = raw[:n - 7]
    return y, w


def band(M, P, h, days=BAND_DAYS, min_n=BAND_MIN, q=BAND_Q):
    """(lo, hi) beside P: P times the exp of the q-quantiles of the log errors log(actual / P) at the same local hour,
    over target days i-h-days+1 to i-h (held when day i's forecast is made); NaN with fewer than min_n errors."""
    raw = M.to_numpy(dtype=float)
    with np.errstate(divide="ignore", invalid="ignore"):
        e = np.log(raw / P)
    E = pd.DataFrame(np.where(np.isfinite(e), e, np.nan))
    roll = E.rolling(days, min_periods=min_n)
    qlo = roll.quantile(q[0]).shift(h).to_numpy()
    qhi = roll.quantile(q[1]).shift(h).to_numpy()
    return P * np.exp(qlo), P * np.exp(qhi)


def place_forecasts(s, tz, h=2):
    """Everything one place's backtest needs: the local frame, the day matrix, and for each method its forecast and
    band by day and local hour. Returns dict(frame, M, P={method: array}, lo={...}, hi={...}, B)."""
    frame = local_frame(s, tz)
    last = last_whole_day(frame, tz)
    frame = frame[frame["day"] <= last]   # a day still partly held is not day A
    M = matrix(frame)
    # h empty days after the last day held: the rows of the days still to come, whose forecasts read only held days
    M = M.reindex(pd.date_range(M.index.min(), M.index.max() + pd.Timedelta(days=h), freq="D"))
    reg, B = regression(M, h)
    y, w = simple(M, h)
    P = {"yesterday": y, "week_ago": w, "regression": reg}
    lo, hi = {}, {}
    for m, arr in P.items():
        lo[m], hi[m] = band(M, arr, h)
    return {"frame": frame, "M": M, "P": P, "lo": lo, "hi": hi, "B": B, "h": h}


def hourly(res, operator=None, first=FIRST_TARGET):
    """One row a UTC hour of the target days from `first` to the last day held: ts, day, hour, actual, operator, and
    each method's forecast with its band."""
    f = res["frame"]
    M = res["M"]
    pos = pd.Series(np.arange(len(M)), index=M.index)
    f = f[f["day"] >= first].copy()
    i = pos.reindex(f["day"]).to_numpy()
    k = f["hour"].to_numpy()
    out = pd.DataFrame({"ts": f["ts"].to_numpy(), "day": f["day"].to_numpy(), "hour": k, "actual": f["value"].to_numpy()})
    for m in res["P"]:
        out[m] = res["P"][m][i, k]
        out[m + "_lo"] = res["lo"][m][i, k]
        out[m + "_hi"] = res["hi"][m][i, k]
    if operator is not None:
        out["operator"] = operator.reindex(pd.DatetimeIndex(out["ts"])).to_numpy()
    return out


def last_whole_day(frame, tz):
    """The last local day whose every hour is held (23, 24 or 25 of them), looking back at most ten days."""
    for day in sorted(frame["day"].unique())[::-1][:10]:
        day = pd.Timestamp(day)
        if int((frame["day"] == day).sum()) >= len(day_hours(tz, day)):
            return day
    return None


def day_hours(tz, day):
    """The UTC hours of the local day `day` (23, 24 or 25), with their local day and hour."""
    start = pd.Timestamp(day).tz_localize(tz)
    end = (pd.Timestamp(day) + pd.Timedelta(days=1)).tz_localize(tz)
    hours = pd.date_range(start.tz_convert("UTC"), end.tz_convert("UTC"), freq="h", inclusive="left")
    loc = hours.tz_convert(tz)
    return pd.DataFrame({"ts": hours, "day": loc.tz_localize(None).normalize(), "hour": loc.hour})


def tomorrow(res, tz, day):
    """The forecast for the local day `day` (a Timestamp at midnight, h days after the last day held) by each method:
    one row a UTC hour of that day, read from the rows `place_forecasts` added after the last day held."""
    M = res["M"]
    if pd.Timestamp(day) != M.index.max():
        raise ValueError(f"the day {pd.Timestamp(day).date()} is not the last row {M.index.max().date()} (h days after the last day held)")
    out = day_hours(tz, day)
    i = len(M) - 1
    k = out["hour"].to_numpy()
    for m in res["P"]:
        out[m] = res["P"][m][i, k]
        out[m + "_lo"] = res["lo"][m][i, k]
        out[m + "_hi"] = res["hi"][m][i, k]
    return out
