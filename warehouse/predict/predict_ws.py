"""ERW forecast (predict): wind and solar output a day ahead, by region, scored against the operators' own forecasts
where the warehouse holds them (chain 730, part F, Samuel's order of 27 November 2026). Method note:
docs/methods/predict_wind_solar.md.

Reads only. Places and their target series (the output the forecast is scored against):
  - region-<code>, EIA's thirteen regions: eia930_region_fuel_hourly's net_generation_wind_mw and _solar_mw. The
    operator's forecast is held only for Texas (TEX is ERCOT alone, and EIA-930's figure equals ERCOT's own actual
    to the megawatt): ercot_wind_solar_forecast's wind_forecast_24h_mw and solar_forecast_24h_mw, the newest posting
    published at least 24 hours before the hour (from 27 September 2026).
  - grid-caiso, CAISO's own wind and solar output, its three trading hubs summed (caiso_wind_solar_forecast's
    wind_actual_mw and solar_actual_mw, from June 2023), against CAISO's day-ahead market forecast of the same
    (wind_forecast_dam_mw, solar_forecast_dam_mw). EIA-930's California region is a larger footprint (CAISO's hubs
    are 60 to 92 percent of it), so CAISO's forecast is scored against CAISO's own actual, never against EIA-930's.

The forecast for local day T is taken as made at 20:00 UTC on T-1 from output through day A = T-2 (h = 2), as the
demand forecast. No weather enters: no dated forecast of wind or cloud is held for the regions (the NWS airport
forecasts began on 26 November 2026, at one airport an ISO, and carry no cloud cover).

Methods (each by local hour):
  yesterday   the same hour of day A;
  profile7    the mean of the same hour over days A-6 to A;
  regression  least squares in megawatts on: 1, the hour on day A, day A's mean, the hour's mean over A-6..A, the
              hour's highest over A-13..A (the envelope, which carries new capacity), refit for every target day on
              the 365 days before it (at least 120), and never below zero.
The choice: the lowest mean absolute error over the last two years held, on the hours every candidate holds (the
operator's too, where held). Band: the 10th and 90th percentile of the method's own past errors (actual less
forecast, MW) at the same local hour over 365 days, the low end not clipped (net output at night is a little below zero).
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
FIT_DAYS = 365
MIN_FIT = 120
BAND_DAYS = 365
BAND_MIN = 60
BAND_Q = (0.1, 0.9)
FIRST_TARGET = pd.Timestamp("2019-07-01")
METHODS = ["yesterday", "profile7", "regression"]
FUELS = ["wind", "solar"]
REGION_FUEL = "eia930_region_fuel_hourly"
CAISO = "caiso_wind_solar_forecast"
ERCOT = "ercot_wind_solar_forecast"


def panels():
    """{(place, fuel): (actual Series, operator Series or None)}, UTC hourly, MW."""
    def build():
        r = data.read(REGION_FUEL, ["entity", "variable", "ts_utc", "value"],
                      lambda d: d["variable"].isin(["net_generation_wind_mw", "net_generation_solar_mw"]))
        r["col"] = "region-" + r["entity"].str.split(":", n=1).str[1].str.lower() + "|" + r["variable"].str.split("_").str[2] + "|actual"
        c = data.read(CAISO, ["entity", "variable", "ts_utc", "value"])
        e = data.read(ERCOT, ["entity", "variable", "ts_utc", "value"])
        cols = {}
        for col, g in r.groupby("col"):
            s = g.set_index("ts")["value"].astype(float)
            cols[col] = s[~s.index.duplicated(keep="last")]
        for fuel in FUELS:
            for kind, var in (("actual", f"{fuel}_actual_mw"), ("operator", f"{fuel}_forecast_dam_mw")):
                g = c[c["variable"] == var]
                w = g.pivot_table(index="ts", columns="entity", values="value", aggfunc="last")
                # every hub that has ever reported the fuel must report the hour (ZP26's wind began later: two of three)
                need = w.notna().any().sum() if fuel == "solar" else 2
                cols[f"grid-caiso|{fuel}|{kind}"] = w.sum(axis=1, min_count=int(need))
            g = e[(e["entity"] == "ercot:SYSTEM") & (e["variable"] == f"{fuel}_forecast_24h_mw")]
            s = g.set_index("ts")["value"].astype(float)
            cols[f"region-tex|{fuel}|operator"] = s[~s.index.duplicated(keep="last")]
        df = pd.DataFrame(cols).sort_index()
        df = df.reindex(pd.date_range(df.index.min(), df.index.max(), freq="h"))
        df.index.name = "ts"
        return df
    return data.cached("ws", [REGION_FUEL, CAISO, ERCOT], build)


BA_FUEL = "eia930_ba_wind_solar_hourly"


def ba_panels():
    """The authorities' wind and solar output (session 10603; eia930_ba_wind_solar_hourly, data request 10, July 2018 on):
    columns ba-<code>|<fuel>|actual, UTC hourly, MW. Kept apart from panels(), whose regions and CAISO it leaves as
    they are."""
    def build():
        r = data.read(BA_FUEL, ["entity", "variable", "ts_utc", "value"])
        r["col"] = "ba-" + r["entity"].str.split(":", n=1).str[1].str.lower() + "|" + r["variable"].str.split("_").str[2] + "|actual"
        cols = {}
        for col, g in r.groupby("col"):
            s = g.set_index("ts")["value"].astype(float)
            cols[col] = s[~s.index.duplicated(keep="last")]
        df = pd.DataFrame(cols).sort_index()
        df = df.reindex(pd.date_range(df.index.min(), df.index.max(), freq="h"))
        df.index.name = "ts"
        return df
    return data.cached("ws_ba", [BA_FUEL], build)


def all_panels():
    """panels() with ba_panels() beside it where the authority table is held."""
    df = panels()
    if os.path.exists(data.table_path(BA_FUEL)):
        b = ba_panels()
        df = pd.concat([df, b], axis=1)
        df = df.reindex(pd.date_range(df.index.min(), df.index.max(), freq="h"))
        df.index.name = "ts"
    return df


def series_of(df, place, fuel):
    a = df.get(f"{place}|{fuel}|actual")
    o = df.get(f"{place}|{fuel}|operator")
    return a, o


def features(M, h=H):
    """X[i, k, :] the regression's row for day i and local hour k, from days up to i - h; Y[i, k] the output."""
    raw = M.to_numpy(dtype=float)
    n = len(raw)
    filled = raw.copy()
    lone = np.isnan(raw[:, 1:23]) & np.isfinite(raw[:, 0:22]) & np.isfinite(raw[:, 2:24])
    filled[:, 1:23] = np.where(lone, (raw[:, 0:22] + raw[:, 2:24]) / 2.0, raw[:, 1:23])

    def lag(a, d):
        out = np.full_like(a, np.nan)
        if d < n:
            out[d:] = a[:n - d]
        return out
    A = lag(filled, h)
    amean = np.repeat(np.mean(A, axis=1)[:, None], 24, axis=1)
    stack7 = np.stack([lag(filled, h + j) for j in range(7)], axis=0)
    prof7 = np.where(np.isfinite(stack7).all(axis=0), np.mean(stack7, axis=0), np.nan)
    stack14 = np.stack([lag(filled, h + j) for j in range(14)], axis=0)
    env = np.where(np.isfinite(stack14).sum(axis=0) >= 10, np.nanmax(np.where(np.isfinite(stack14), stack14, -np.inf), axis=0), np.nan)
    X = np.stack([np.ones_like(A), A, amean, prof7, env], axis=2)
    return X, raw, A, prof7


def walk(X, Y, h=H, fit_days=FIT_DAYS, min_fit=MIN_FIT):
    """Walk-forward least squares by hour (rows j <= i - h, the last fit_days of them), never below zero."""
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
            P[i, k] = max(0.0, float(X[i, k] @ beta))
    return P


def band(M, P, h=H, days=BAND_DAYS, min_n=BAND_MIN, q=BAND_Q):
    """(lo, hi): P plus the q-quantiles of the past errors (actual - P) at the hour, over target days i-h-days+1..i-h."""
    raw = M.to_numpy(dtype=float)
    E = pd.DataFrame(raw - P)
    roll = E.rolling(days, min_periods=min_n)
    qlo = roll.quantile(q[0]).shift(h).to_numpy()
    qhi = roll.quantile(q[1]).shift(h).to_numpy()
    # the low end is not clipped at zero: a plant's net output at night is a little below zero (its own use)
    return P + qlo, P + qhi


CURTAIL = "caiso_curtailment_intervals"


def curtailment():
    """{fuel: hourly Series (UTC, MWh in the hour)}: CAISO's curtailed wind and solar, every reason summed; the five-minute
    MW to 2025 averaged over the hour's twelve intervals (only intervals with a curtailment are written, so a missing
    interval is zero), the hourly MWh from 2026. An hour of a Pacific day that the daily rows cover and that has no
    interval is zero; a day not covered is not held."""
    def build():
        d = data.read(CURTAIL, ["variable", "ts_utc", "value", "freq"])
        out = {}
        for fuel in FUELS:
            g = d[d["variable"].str.startswith(f"curtailed_{fuel}_")]
            five = g[g["freq"] == "PT5M"]
            hourly_ = g[g["freq"] == "PT1H"]
            day = g[g["freq"] == "P1D"]
            a = five.groupby(five["ts"].dt.floor("h"))["value"].sum() / 12.0
            b = hourly_.groupby("ts")["value"].sum()
            s = pd.concat([a, b]).groupby(level=0).sum()
            days = pd.DatetimeIndex(day["ts"].dt.tz_localize(None).dt.normalize().unique())
            start = days.min().tz_localize("America/Los_Angeles").tz_convert("UTC")
            end = (days.max() + pd.Timedelta(days=1)).tz_localize("America/Los_Angeles").tz_convert("UTC")
            idx = pd.date_range(start, end, freq="h", inclusive="left")
            covered = idx.tz_convert("America/Los_Angeles").tz_localize(None).normalize().isin(days)
            full = pd.Series(np.where(covered, 0.0, np.nan), index=idx)
            full.loc[full.index.intersection(s.index)] = s.reindex(full.index.intersection(s.index)).to_numpy()
            out[fuel] = full
        df = pd.DataFrame(out)
        df.index.name = "ts"
        return df
    return data.cached("curtail", [CURTAIL], build)


def place_forecasts(s, tz, h=H):
    """The backtest of one place and fuel: dict(frame, M, P, lo, hi), M extended by h days still to come."""
    frame = demand.local_frame(s, tz)
    last = demand.last_whole_day(frame, tz)
    frame = frame[frame["day"] <= last]
    M = demand.matrix(frame)
    M = M.reindex(pd.date_range(M.index.min(), M.index.max() + pd.Timedelta(days=h), freq="D"))
    X, Y, A, prof7 = features(M, h)
    P = {"yesterday": A, "profile7": prof7, "regression": walk(X, Y, h)}
    lo, hi = {}, {}
    for m, arr in P.items():
        lo[m], hi[m] = band(M, arr, h)
    return {"frame": frame, "M": M, "P": P, "lo": lo, "hi": hi, "h": h}


def hourly(res, operator=None, first=FIRST_TARGET):
    return demand.hourly(res, operator, first=first)


def metric(x, m):
    """(hours, mae MW, nmae percent: the MAE over the mean actual of the same hours)."""
    if not len(x):
        return 0, None, None
    err = (x[m] - x["actual"]).abs()
    mean = x["actual"].mean()
    return int(len(x)), round(float(err.mean()), 1), (round(float(err.mean() / mean * 100), 2) if mean > 0 else None)
