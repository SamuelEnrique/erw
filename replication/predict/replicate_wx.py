#!/usr/bin/env python3
"""Replication of the separate line "with the weather forecast" (scores.json, series demand_weather_forecast), chain 730,
part F. Written from docs/methods/predict.md section 19; it imports nothing of the builder, only replicate.py's readers
and its regression rows (refit), to which the weather's three regressors are added here: the airport's temperature
over 100, its square, and the day's mean over 100. Fitted on the airport's observed temperature (NOAA's measured hours,
then NWS's observations after NOAA's last), applied with the NWS forecast for the airport issued no later than 20:00 UTC
the day before (the issued table and the latest-only table's early rows; the latest such issue). Every figure of the
series' rows is recomputed. Prints N of N and writes replication/predict/figures_wx.csv.
    python replication/predict/replicate_wx.py --tables DIR --backtest PATH [--file site/data/predict/scores.json]
"""
import argparse
import csv
import json
import os
import sys

import numpy as np
import pandas as pd
from pandas.tseries.holiday import USFederalHolidayCalendar

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import replicate as rd  # noqa: E402
import replicate_net as rn  # noqa: E402

AIRPORTS = {"KDFW": ("DFW", ["region-tex", "ba-erco"]), "KLAX": ("LAX", ["region-cal", "ba-ciso"]),
            "KLGA": ("LGA", ["region-ny", "ba-nyis"]), "KBOS": ("BOS", ["region-ne", "ba-isne"]),
            "KPHL": ("PHL", ["region-mida", "ba-pjm"]), "KIND": ("IND", ["region-midw", "ba-miso"]),
            "KOKC": ("OKC", ["region-cent", "ba-swpp"])}
MADE = 20


def read(path, cols):
    n = rd.header_rows(path)
    with open(path, "rb") as fh:
        for _ in range(n):
            fh.readline()
        d = pd.read_csv(fh, usecols=cols, engine="pyarrow")
    d["ts"] = pd.to_datetime(d["ts_utc"], utc=True)
    return d


def day_matrix(s, tz, days):
    loc = s.index.tz_convert(tz)
    f = pd.DataFrame({"v": s.to_numpy(float), "day": loc.tz_localize(None).normalize(), "hour": loc.hour})
    T = f.groupby(["day", "hour"])["v"].mean().unstack("hour").reindex(columns=range(24)).reindex(days).to_numpy(float)
    lone = np.isnan(T[:, 1:23]) & np.isfinite(T[:, :22]) & np.isfinite(T[:, 2:])
    T[:, 1:23] = np.where(lone, (T[:, :22] + T[:, 2:]) / 2.0, T[:, 1:23])
    return T


def forecast_matrix(fc, airport, tz, days):
    r = fc[fc["airport"] == airport].copy()
    loc = r["ts"].dt.tz_convert(tz)
    r["day"] = loc.dt.tz_localize(None).dt.normalize()
    r["hour"] = loc.dt.hour
    r = r[r["vintage"] <= (r["day"] - pd.Timedelta(days=1)).dt.tz_localize("UTC") + pd.Timedelta(hours=MADE)]
    r = r.sort_values("vintage").drop_duplicates(subset=["ts"], keep="last")
    F = r.groupby(["day", "hour"])["value"].mean().unstack("hour").reindex(columns=range(24)).reindex(days).to_numpy(float)
    lone = np.isnan(F[:, 1:23]) & np.isfinite(F[:, :22]) & np.isfinite(F[:, 2:])
    F[:, 1:23] = np.where(lone, (F[:, :22] + F[:, 2:]) / 2.0, F[:, 1:23])
    F[~np.isfinite(F).all(axis=1)] = np.nan
    return F


def wx(T, i, k):
    m = np.mean(T[i])
    return [T[i, k] / 100.0, (T[i, k] / 100.0) ** 2, m / 100.0]


def lines(M, Tobs, F):
    """{day index: (P_forecast[24], P_observed[24])} on the days F holds, refitted from the note's words."""
    raw = M.to_numpy(float)
    fil = raw.copy()
    for j in range(1, 23):
        lone = np.isnan(raw[:, j]) & ~np.isnan(raw[:, j - 1]) & ~np.isnan(raw[:, j + 1])
        fil[lone, j] = (raw[lone, j - 1] + raw[lone, j + 1]) / 2
    days = M.index
    lf = np.log(np.where(fil > 0, fil, np.nan))
    dmean = np.where((np.isnan(fil) | ~(fil > 0)).any(axis=1), np.nan, fil.mean(axis=1))
    week = pd.Series(dmean, index=days).rolling(7, min_periods=5).mean()
    hol = USFederalHolidayCalendar().holidays(days.min() - pd.Timedelta(days=30), days.max() + pd.Timedelta(days=30))
    thanks = [d for d in hol if d.month == 11 and d.day >= 22 and d.dayofweek == 3]
    pos = {d: i for i, d in enumerate(days)}

    def bridge(d):
        b = (d - pd.Timedelta(days=1)) in thanks or (d.month == 12 and (d.day == 24 or d.day >= 26))
        return float(b and d not in hol)

    def base(D, k):
        A, S = D - pd.Timedelta(days=rd.H), D - pd.Timedelta(days=7)
        if A not in pos or S not in pos:
            return None
        a, s = pos[A], pos[S]
        x = [1.0, lf[a, k], np.log(dmean[a]), lf[s, k], np.log(week.iloc[a])]
        x += [float(D.dayofweek == w) for w in range(6)] + [float(A.dayofweek == w) for w in range(6)]
        x += [float(D in hol), bridge(D), float(A in hol), bridge(A), float(S in hol), bridge(S)]
        t = D.dayofyear / 365.25
        return x + [np.sin(2 * np.pi * t), np.cos(2 * np.pi * t), np.sin(4 * np.pi * t), np.cos(4 * np.pi * t)]

    out = {}
    for i in np.flatnonzero(np.isfinite(F).all(axis=1)):
        T = days[i]
        pf, po = np.full(24, np.nan), np.full(24, np.nan)
        for k in range(24):
            rows, ys = [], []
            for D in pd.date_range(T - pd.Timedelta(days=rd.H + 729), T - pd.Timedelta(days=rd.H), freq="D"):
                if D not in pos:
                    continue
                b = base(D, k)
                if b is None:
                    continue
                x = np.array(b + wx(Tobs, pos[D], k))
                if not np.isfinite(x).all() or not raw[pos[D], k] > 0:
                    continue
                rows.append(x)
                ys.append(np.log(raw[pos[D], k]))
            b = base(T, k)
            if len(rows) < 300 or b is None:
                continue
            xf = np.array(b + wx(F, i, k))
            if not np.isfinite(xf).all():
                continue
            beta = np.linalg.lstsq(np.array(rows), np.array(ys), rcond=None)[0]
            pf[k] = float(np.exp(xf @ beta))
            xo = np.array(b + wx(Tobs, i, k))
            if np.isfinite(xo).all():
                po[k] = float(np.exp(xo @ beta))
        out[i] = (pf, po)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tables", default=os.path.join(rd.ROOT, "warehouse", "output"))
    ap.add_argument("--backtest", default=os.path.join(rd.ROOT, "warehouse", "output", "predict_demand_backtest.csv"))
    ap.add_argument("--file", default=os.path.join(rd.ROOT, "site", "data", "predict", "scores.json"))
    a = ap.parse_args()
    sc = json.load(open(a.file, encoding="utf-8"))
    cols = sc["rows_columns"]
    shown = {(r[0], r[2]): dict(zip(cols, r)) for r in sc["rows"] if r[1] == "demand_weather_forecast"}
    places = sorted({k[0] for k in shown})
    dem, tz = rd.demand_places(a.tables, places)
    ops = rd.operator(a.tables)
    bt = rd.read(a.backtest, ["ts_utc", "value", "x_place", "x_method"])
    i1 = read(os.path.join(a.tables, "weather_forecast_issued_hourly.csv"), ["entity", "variable", "ts_utc", "value", "vintage"])
    i1 = i1[i1["variable"].astype(str).str.startswith("temperature_f_lead")]
    i2 = read(os.path.join(a.tables, "weather_forecast_hourly.csv"), ["entity", "variable", "ts_utc", "value", "vintage"])
    i2 = i2[i2["variable"] == "temperature_f"]
    fc = pd.concat([i1, i2], ignore_index=True)
    fc["airport"] = fc["entity"].str.split(":", n=1).str[1]
    fc["vintage"] = pd.to_datetime(fc["vintage"], utc=True, errors="coerce")
    fc = fc.dropna(subset=["vintage", "value"]).drop_duplicates(subset=["airport", "ts", "vintage"], keep="first")
    names = {v[0]: k for k, v in AIRPORTS.items()}
    no = read(os.path.join(a.tables, "noaa_station_weather_hourly.csv"), ["variable", "ts_utc", "value", "node"])
    no = no[(no["variable"] == "temperature_f") & no["node"].isin(list(names))]
    nw = read(os.path.join(a.tables, "weather_obs_hourly.csv"), ["entity", "variable", "ts_utc", "value"])
    nw = nw[nw["variable"] == "temperature_f"]
    figs = []
    for p in places:
        airport = next(k for k, v in AIRPORTS.items() if p in v[1])
        g = no[no["node"] == AIRPORTS[airport][0]]
        s = pd.Series(g["value"].to_numpy(float), index=pd.DatetimeIndex(g["ts"])).sort_index()
        s = s[~s.index.duplicated(keep="last")]
        h = nw[nw["entity"] == "nws:" + airport]
        t = pd.Series(h["value"].to_numpy(float), index=pd.DatetimeIndex(h["ts"])).sort_index()
        t = t[~t.index.duplicated(keep="last")]
        obs = pd.concat([s, t[t.index > s.index.max()]]).sort_index()
        f = rd.local(dem[p], tz[p])
        M = rd.mat(f)
        M = M.reindex(pd.date_range(M.index.min(), M.index.max() + pd.Timedelta(days=rd.H), freq="D"))
        Tobs = day_matrix(obs, tz[p], M.index)
        F = forecast_matrix(fc, airport, tz[p], M.index)
        got = lines(M, Tobs, F)
        x = rn.demand_erw(p, dem, tz, ops, bt).reset_index()
        pos = pd.Series(np.arange(len(M)), index=M.index)
        ii = pos.reindex(x["day"]).to_numpy()
        kk = x["hour"].to_numpy()
        pf = np.full(len(x), np.nan)
        po = np.full(len(x), np.nan)
        for j, (i, k) in enumerate(zip(ii, kk)):
            if i in got:
                pf[j], po[j] = got[i][0][k], got[i][1][k]
        x["with_weather_forecast"], x["with_airport_weather_known"] = pf, po
        ms = ["with_weather_forecast", "with_airport_weather_known", "erw", "operator", "regression", "regression_recent"]
        c = x.dropna(subset=["actual"] + ms)
        for m in ms:
            n, mae, mape = rd.score(c, m) if len(c) else (0, None, None)
            r = shown.get((p, m))
            ok = r is not None and r["hours"] == n and (mae is None or (abs(r["mae"] - mae) <= 0.011 and abs(r["mape"] - mape) <= 0.0011))
            figs.append((f"{p}.{m}", None if r is None else (r["hours"], r["mae"], r["mape"]), (n, mae, mape), ok))
        print(f"{p} ({airport}, {c['day'].nunique()} days): {sum(1 for f_ in figs if f_[0].startswith(p + '.') and f_[3])} of {len(ms)} figures equal", flush=True)
    with open(os.path.join(HERE, "figures_wx.csv"), "w", encoding="utf-8", newline="\n") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["key", "file", "recomputed", "equal"])
        w.writerows(figs)
    ok = sum(1 for f_ in figs if f_[3])
    print(f"with the weather forecast: {ok} of {len(figs)} figures equal")
    for f_ in [f_ for f_ in figs if not f_[3]][:40]:
        print("  differs:", f_)
    sys.exit(0 if ok == len(figs) else 1)


if __name__ == "__main__":
    main()
