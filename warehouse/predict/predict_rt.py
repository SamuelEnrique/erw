"""ERW forecast (predict): the real-time price a day ahead at the three public hubs (chain 730, part F, Samuel's order of
27 November 2026). Method note: docs/methods/predict_price.md, section 7.

Reads only. Hubs (warehouse/metadata/license_verdicts.csv: "may be public"): ERCOT HB_NORTH, SPP North Hub, CAISO SP15.
The real-time price of an hour is the mean of its four fifteen-minute prices (market *_rtm of the price tables), written
only when all four are held. The day-ahead price is the hour's day-ahead price (predict_data.price_panel).

The forecast for local day T is taken as made at 22:00 UTC on T-1: after every one of the three day-ahead markets has
published its prices for day T on its ordinary timeline (ERCOT about 19:30 UTC, SPP about 19:00 to 20:00 UTC, CAISO
about 20:00 to 21:00 UTC), and with the real-time prices read through day T-2 (the latest whole local day before the
hour of making, h = 2). A day on which a market published late is not detected: the timeline is the market's own.

Methods (each by local hour):
  day_ahead     the day-ahead price for the hour: the market's own forecast of the real-time price; the comparator
                (as the operator's forecast is for demand), never an ERW method;
  yesterday     the real-time price of the same hour on day T-2;
  regression    least squares on: 1, the day-ahead price for the hour, the real-time less day-ahead price at the hour
                on T-2, and its mean over T-8 to T-2; refit for every target day on the 730 days before it (at least
                300).
The choice, the band and the scores are those of the day-ahead price forecast (predict_price.md): the ERW method with
the lowest mean absolute error over the last two years on the hours every method and the day-ahead price hold; the
10th and 90th percentile of past errors at the hour over 365 days; MAPE over hours whose price is at least 5 USD/MWh.
"""
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(HERE)
import predict_data as data  # noqa: E402
import predict_demand as demand  # noqa: E402

H = 2
FIT_DAYS = 730
MIN_FIT = 300
BAND_DAYS = 365
BAND_MIN = 60
MADE_HOUR = 22
FIRST_TARGET = pd.Timestamp("2019-07-01")
METHODS = ["yesterday", "regression"]
HUB_TZ = {"ercot": "America/Chicago", "spp": "America/Chicago", "caiso": "America/Los_Angeles"}


def rt_panel():
    """Wide frame, index the UTC hour (start), one column a grid of HUBS: the real-time price, USD/MWh, the mean of the
    hour's four fifteen-minute prices, held only when all four are."""
    def build():
        frames = []
        for order, t in enumerate(data.PRICE_TABLES):
            d = data.read(t, ["entity", "ts_utc", "value", "market"],
                          lambda d: d["market"].astype(str).str.endswith("_rtm") & d["entity"].isin(list(data.HUBS.values())))
            d["order"] = order
            frames.append(d[["entity", "ts", "value", "order"]])
        d = pd.concat(frames, ignore_index=True).sort_values(["entity", "ts", "order"])
        d = d.drop_duplicates(subset=["entity", "ts"], keep="last")
        d["hour"] = d["ts"].dt.floor("h")
        inv = {v: k for k, v in data.HUBS.items()}
        cols = {}
        for e, g in d.groupby("entity"):
            a = g.groupby("hour")["value"].agg(["mean", "size"])
            cols[inv[e]] = a["mean"].where(a["size"] == 4)
        df = pd.DataFrame(cols)
        df = df.reindex(pd.date_range(df.index.min(), df.index.max(), freq="h"))
        df.index.name = "ts"
        return df
    return data.cached("rt_" + "_".join(sorted(data.HUBS)), data.PRICE_TABLES, build)


def walk(X, Y, h=H, fit_days=FIT_DAYS, min_fit=MIN_FIT):
    n, K, p = X.shape
    valid = np.isfinite(X).all(axis=2) & np.isfinite(Y)
    cn = np.concatenate([np.zeros((1, K)), np.cumsum(valid, axis=0)])
    P = np.full((n, K), np.nan)
    for i in range(n):
        hi = i - h + 1
        if hi <= 0:
            continue
        lo = max(0, hi - fit_days)
        ok = (cn[hi] - cn[lo] >= min_fit) & np.isfinite(X[i]).all(axis=1)
        for k in np.flatnonzero(ok):
            v = valid[lo:hi, k]
            beta = np.linalg.lstsq(X[lo:hi, k][v], Y[lo:hi, k][v], rcond=None)[0]
            P[i, k] = float(X[i, k] @ beta)
    return P


def band(M, P, h=H, days=BAND_DAYS, min_n=BAND_MIN, q=(0.1, 0.9)):
    E = pd.DataFrame(M.to_numpy(dtype=float) - P)
    roll = E.rolling(days, min_periods=min_n)
    return P + roll.quantile(q[0]).shift(h).to_numpy(), P + roll.quantile(q[1]).shift(h).to_numpy()


def place_forecasts(rt, da, tz, h=H):
    """rt, da: hourly UTC Series of one hub. Returns dict(frame, M, P, lo, hi, D): M the real-time price by local day and
    hour, extended by h days still to come; D the day-ahead price on the same grid (held for day T when the forecast
    is made, by the timeline above)."""
    frame = demand.local_frame(rt, tz)
    last = demand.last_whole_day(frame, tz)
    frame = frame[frame["day"] <= last]
    M = demand.matrix(frame)
    M = M.reindex(pd.date_range(M.index.min(), M.index.max() + pd.Timedelta(days=h), freq="D"))
    D = demand.matrix(demand.local_frame(da, tz)).reindex(M.index).to_numpy(dtype=float)
    raw = M.to_numpy(dtype=float)
    n = len(raw)

    def back(a, d):
        o = np.full_like(a, np.nan)
        o[d:] = a[:n - d]
        return o
    spread = raw - D
    y = back(raw, h)
    s1 = back(spread, h)
    s7 = np.stack([back(spread, h + j) for j in range(7)])
    s7m = np.where(np.isfinite(s7).sum(axis=0) >= 5, np.nanmean(np.where(np.isfinite(s7), s7, np.nan), axis=0), np.nan)
    X = np.stack([np.ones_like(D), D, s1, s7m], axis=2)
    P = {"yesterday": y, "regression": walk(X, raw, h), "day_ahead": D}
    lo, hi = {}, {}
    for m, arr in P.items():
        lo[m], hi[m] = band(M, arr, h)
    return {"frame": frame, "M": M, "P": P, "lo": lo, "hi": hi, "h": h}
