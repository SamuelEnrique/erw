#!/usr/bin/env python3
"""Replication of the ERW forecast's report card (site/data/predict/scores.json), demand rows (chain 730, part F).

Written from docs/methods/predict.md and the contract (docs/state/page_files_predict.md), not from warehouse/predict/:
it imports nothing of the builder. Three checks:

 1. Every demand figure of scores.json (hours, mean absolute error, mean absolute percent error, for every place,
    method and cut) is recomputed from the public tables: the demand (eia930_ba_demand_hourly, a region summed by the
    demand pages' rule, warehouse/derived/region_files.py), the operator's forecast (eia930_forecast_error_hourly, its
    screened hours left out), the two simple methods rebuilt here from the demand, and the regression's forecasts as
    stored in the backtest table (predict_demand_backtest, data request 3; until it is loaded, the file run.py writes).
 2. The regression itself is refitted here, from the note's words, on sample days of every place (ordinary least
    squares on the window's own rows, numpy.linalg.lstsq; the builder solves running normal equations), and set beside
    the stored forecast.

 3. (session 10603) The rows demand_peak of scores.json, the day's peak of the note's section 11, recomputed from the same
    hours, with the peak's own choice.

Prints N of N for each, names every difference, writes replication/predict/figures.csv. The regressions' figures are
allowed the bound of the backtest table's rounding (0.1 MW a forecast: 0.05 MW in the MAE, 5 over the demand in the
MAPE), which shows only where the demand is a few dozen MW (session 10603); every other figure is held to the file's own.

    python replication/predict/replicate.py --tables DIR --backtest PATH [--file site/data/predict/scores.json]
"""
import argparse
import csv
import glob
import json
import os
import sys

import numpy as np
import pandas as pd
from pandas.tseries.holiday import USFederalHolidayCalendar

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
FIRST = pd.Timestamp("2019-07-01")
H = 2
SAMPLE_DAYS = ["2020-08-14", "2022-12-23", "2024-07-15", "2026-11-20"]


def header_rows(path):
    n = 0
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.startswith("#"):
                break
            n += 1
    return n


def read(path, cols):
    """A table's columns, its header lines skipped by count (never by the comment character)."""
    n = header_rows(path)
    with open(path, "rb") as fh:
        for _ in range(n):
            fh.readline()
        return pd.read_csv(fh, usecols=cols, engine="pyarrow")


def demand_places(tables, places):
    """{place: hourly Series}: an authority's demand_mw; a region by region_files.region_demand (the pages' own rule)."""
    sys.path.append(os.path.join(ROOT, "warehouse", "connectors"))
    sys.path.append(os.path.join(ROOT, "warehouse", "derived"))
    import region_files as rp
    rp.ROOT = os.path.abspath(os.path.join(tables, "..", ".."))
    ref, _ = rp.reference()
    d = read(os.path.join(tables, "eia930_ba_demand_hourly.csv"), ["entity", "variable", "ts_utc", "value"])
    d = d[d["variable"] == "demand_mw"].copy()
    d["ts"] = pd.to_datetime(d["ts_utc"], utc=True)
    out, tz = {}, {}
    for p in places:
        kind, code = p.split("-", 1)
        code = code.upper()
        if kind == "region":
            s, _ = rp.region_demand(code, ref, d)
            tz[p] = rp.REGION_TZ[code]
        else:
            g = d[d["entity"] == f"eia930:{code}"]
            s = pd.Series(g["value"].to_numpy(float), index=pd.DatetimeIndex(g["ts"])).sort_index()
            s = s[~s.index.duplicated(keep="last")]
            tz[p] = rp.BA_TZ.get(code) or ref[code]["tz"]
        out[p] = s.dropna()
    return out, tz


def operator(tables):
    d = read(os.path.join(tables, "eia930_forecast_error_hourly.csv"), ["entity", "ts_utc", "x_level", "x_forecast_mw", "x_screened"])
    d = d[d["x_screened"].astype(str).isin(["0", "False", "false"])]
    d["place"] = np.where(d["x_level"] == "region", "region-", "ba-") + d["entity"].str.split(":").str[1].str.lower()
    d["ts"] = pd.to_datetime(d["ts_utc"], utc=True)
    return {p: pd.Series(g["x_forecast_mw"].to_numpy(float), index=pd.DatetimeIndex(g["ts"])).sort_index() for p, g in d.groupby("place")}


def local(s, tz):
    loc = s.index.tz_convert(tz)
    f = pd.DataFrame({"ts": s.index, "actual": s.to_numpy(), "day": loc.tz_localize(None).normalize(), "hour": loc.hour})
    # the last whole local day: every hour of it held
    for day in sorted(f["day"].unique())[::-1][:10]:
        day = pd.Timestamp(day)
        a = day.tz_localize(tz)
        b = (day + pd.Timedelta(days=1)).tz_localize(tz)
        if (f["day"] == day).sum() >= int((b - a).total_seconds() // 3600):
            return f[f["day"] <= day]
    return f


def mat(f):
    M = f.groupby(["day", "hour"])["actual"].mean().unstack("hour").reindex(columns=range(24))
    return M.reindex(pd.date_range(M.index.min(), M.index.max(), freq="D"))


def score(x, m):
    e = (x[m] - x["actual"]).abs()
    return len(x), round(float(e.mean()), 2), round(float((e / x["actual"]).mean() * 100), 3)


def refit(M, T, k, recent=False):
    """The note's regression for day T and hour k, fitted here on the window's own rows; with recent, the regression
    with the three recent regressors of the note's section 14 (the last hour of day A, the hour on A-1, the hour on T-14)."""
    raw = M.to_numpy(float)
    fil = raw.copy()
    for j in range(1, 23):
        lone = np.isnan(raw[:, j]) & ~np.isnan(raw[:, j - 1]) & ~np.isnan(raw[:, j + 1])
        fil[lone, j] = (raw[lone, j - 1] + raw[lone, j + 1]) / 2
    days = M.index
    lf = np.log(np.where(fil > 0, fil, np.nan))
    # a day's mean only when every hour is held and above zero (an hour at or below zero is taken as not held)
    dmean = np.where((np.isnan(fil) | ~(fil > 0)).any(axis=1), np.nan, fil.mean(axis=1))
    week = pd.Series(dmean, index=days).rolling(7, min_periods=5).mean()
    hol_days = USFederalHolidayCalendar().holidays(days.min() - pd.Timedelta(days=30), days.max() + pd.Timedelta(days=30))
    thanks = [d for d in hol_days if d.month == 11 and d.day >= 22 and d.dayofweek == 3]
    pos = {d: i for i, d in enumerate(days)}

    def is_hol(d):
        return float(d in hol_days)

    def is_bridge(d):
        b = (d - pd.Timedelta(days=1)) in thanks or (d.month == 12 and (d.day == 24 or d.day >= 26))
        return float(b and d not in hol_days)

    def row(D):
        i = pos.get(D)
        A, S = D - pd.Timedelta(days=H), D - pd.Timedelta(days=7)
        A1, F = D - pd.Timedelta(days=H + 1), D - pd.Timedelta(days=14)
        if i is None or A not in pos or S not in pos or (recent and (A1 not in pos or F not in pos)):
            return None
        a, s = pos[A], pos[S]
        x = [1.0, lf[a, k], np.log(dmean[a]), lf[s, k], np.log(week.iloc[a])]
        x += [float(D.dayofweek == w) for w in range(6)] + [float(A.dayofweek == w) for w in range(6)]
        x += [is_hol(D), is_bridge(D), is_hol(A), is_bridge(A), is_hol(S), is_bridge(S)]
        t = D.dayofyear / 365.25
        x += [np.sin(2 * np.pi * t), np.cos(2 * np.pi * t), np.sin(4 * np.pi * t), np.cos(4 * np.pi * t)]
        if recent:
            x += [lf[a, 23], lf[pos[A1], k], lf[pos[F], k]]
        return np.array(x)

    rows, ys = [], []
    for D in pd.date_range(T - pd.Timedelta(days=H + 729), T - pd.Timedelta(days=H), freq="D"):
        x = row(D)
        if x is None or not np.isfinite(x).all() or not raw[pos[D], k] > 0:
            continue
        rows.append(x)
        ys.append(np.log(raw[pos[D], k]))
    xT = row(T)
    if len(rows) < 300 or xT is None or not np.isfinite(xT).all():
        return None
    beta = np.linalg.lstsq(np.array(rows), np.array(ys), rcond=None)[0]
    return float(np.exp(xT @ beta))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tables", default=os.path.join(ROOT, "warehouse", "output"))
    ap.add_argument("--backtest", default=os.path.join(ROOT, "warehouse", "output", "predict_demand_backtest.csv"))
    ap.add_argument("--file", default=os.path.join(ROOT, "site", "data", "predict", "scores.json"))
    a = ap.parse_args()
    sc = json.load(open(a.file, encoding="utf-8"))
    cols = sc["rows_columns"]
    rows = [dict(zip(cols, r)) for r in sc["rows"] if r[1] == "demand"]
    places = sorted({r["place"] for r in rows})
    dem, tz = demand_places(a.tables, places)
    ops = operator(a.tables)
    bt = read(a.backtest, ["ts_utc", "value", "x_place", "x_method"])
    bt = bt[bt["x_method"].isin(["regression", "regression_recent"])]
    events = {}
    for p in sorted(glob.glob(os.path.join(ROOT, "site", "data", "regions", "events", "*.json"))):
        e = json.load(open(p, encoding="utf-8"))
        events[os.path.basename(p)[:-5].replace("_", "-")] = (pd.Timestamp(e["start"]), pd.Timestamp(e["end"]))
    figs, refits = [], []
    for p in places:
        f = local(dem[p], tz[p])
        M = mat(f)
        pos = pd.Series(np.arange(len(M)), index=M.index)
        x = f[f["day"] >= FIRST].copy()
        i = pos.reindex(x["day"]).to_numpy()
        k = x["hour"].to_numpy()
        raw = M.to_numpy(float)
        x["yesterday"] = np.where(i >= H, raw[np.clip(i - H, 0, None), k], np.nan)
        x["week_ago"] = np.where(i >= 7, raw[np.clip(i - 7, 0, None), k], np.nan)
        x["operator"] = ops[p].reindex(pd.DatetimeIndex(x["ts"])).to_numpy() if p in ops else np.nan
        for meth in ("regression", "regression_recent"):
            b = bt[(bt["x_place"] == p) & (bt["x_method"] == meth)]
            x[meth] = pd.Series(b["value"].to_numpy(float), index=pd.DatetimeIndex(pd.to_datetime(b["ts_utc"], utc=True))).reindex(pd.DatetimeIndex(x["ts"])).to_numpy()
        maes = {}
        last = x["day"].max()
        recent = x[x["day"] > last - pd.Timedelta(days=730)]
        c2 = recent.dropna(subset=["actual", "yesterday", "week_ago", "regression", "regression_recent", "operator"])
        for m in ("yesterday", "week_ago", "regression", "regression_recent"):
            maes[m] = score(c2, m)[1]
        chosen = min((v, m) for m, v in maes.items())[1]
        x["erw"] = x[chosen]
        c = x.dropna(subset=["actual", "erw", "operator", "yesterday", "week_ago", "regression", "regression_recent"]).reset_index(drop=True)
        last = c["day"].max()
        rec = c["day"] > last - pd.Timedelta(days=730)
        cuts = {("all", ""): np.ones(len(c), bool), ("last_2_years", ""): rec.to_numpy()}
        mo = c["day"].dt.strftime("%Y-%m")
        for m_ in sorted(mo.unique()):
            cuts[("month", m_)] = (mo == m_).to_numpy()
        for h in range(24):
            cuts[("hour", str(h))] = (rec & (c["hour"] == h)).to_numpy()
        top = c.groupby("day")["actual"].max().sort_values(ascending=False).index[:10]
        cuts[("top10", "")] = c["day"].isin(top).to_numpy()
        for eid, (s0, s1) in events.items():
            msk = ((c["day"] >= s0) & (c["day"] <= s1)).to_numpy()
            if msk.any():
                cuts[("event", eid)] = msk
        # the operator's filing check (method note section 18): a month whose filed forecast sums more than 5 percent
        # from the demand over the hours both hold is flagged; the cuts operator_sound(_last_2_years) take the rest
        if p in ops:
            y = x[(x["actual"] > 0) & x["operator"].notna()]
            g = y.groupby(y["day"].dt.strftime("%Y-%m"))[["operator", "actual"]].sum()
            sound = set(g.index[((g["operator"] / g["actual"] * 100) - 100).abs() <= 5.0])
            ok_m = mo.isin(sorted(sound)).to_numpy()
            cuts[("operator_sound", "")] = ok_m
            cuts[("operator_sound_last_2_years", "")] = ok_m & rec.to_numpy()
        shown = {(r["method"], r["cut"], r["key"]): r for r in rows if r["place"] == p}
        for (cut, key), msk in cuts.items():
            for m in ("erw", "operator", "yesterday", "week_ago", "regression", "regression_recent"):
                if not msk.any():
                    # a cut with no hours (no sound month in the last two years): the file's row is present, empty
                    n, mae, mape = 0, None, None
                    r = shown.get((m, cut, key))
                    ok = r is not None and r["hours"] == 0 and r["mae"] is None
                    figs.append((f"{p}.{m}.{cut}.{key}", None if r is None else (r["hours"], r["mae"], r["mape"]), (n, mae, mape), ok))
                    continue
                n, mae, mape = score(c[msk], m)
                r = shown.get((m, cut, key))
                # the regressions are read from the backtest table, which stores each forecast to 0.1 MW: their figures
                # may differ by the bound of that rounding, 0.05 MW an hour (session 10603: it shows in the MAPE's third
                # decimal only where the demand is a few dozen MW); every other method is held to the rounding of the file
                st = m in ("regression", "regression_recent") or (m == "erw" and chosen in ("regression", "regression_recent"))
                tol_mae = 0.011 + (0.05 if st else 0)
                tol_mape = 0.0011 + (float((5.0 / c[msk]["actual"]).mean()) if st and n else 0)
                ok = r is not None and r["hours"] == n and abs(r["mae"] - mae) <= tol_mae and abs(r["mape"] - mape) <= tol_mape
                figs.append((f"{p}.{m}.{cut}.{key}", None if r is None else (r["hours"], r["mae"], r["mape"]), (n, mae, mape), ok))
        extra = set(shown) - {(m, cu, ke) for (cu, ke) in cuts for m in ("erw", "operator", "yesterday", "week_ago", "regression", "regression_recent")}
        for e in sorted(extra):
            figs.append((f"{p}.{e[0]}.{e[1]}.{e[2]}", shown[e]["hours"], None, False))
        # the day's peak (method note section 11, session 10603): the days whose every hour held by the demand is held by
        # every method; each method's peak the highest of its hourly forecasts; the peak's own choice, the candidate
        # whose day peaks missed least over the last two years (its MAE to 0.1 MW, a tie by name); rows demand_peak
        nx = x.groupby("day")["hour"].size()
        nc = c.groupby("day")["hour"].size()
        cp = c[c["day"].isin(nc.index[(nc == nx.reindex(nc.index)).to_numpy()])]
        gp = cp.groupby("day")
        pk = pd.DataFrame({"actual": gp["actual"].max()})
        for m in ("erw", "operator", "yesterday", "week_ago", "regression", "regression_recent"):
            pk[m] = gp[m].max()
        pk = pk.reset_index()

        def pscore(z, m):
            e = (z[m] - z["actual"]).abs()
            return len(z), round(float(e.mean()), 1), round(float((e / z["actual"]).mean() * 100), 3)
        rp = pk[pk["day"] > pk["day"].max() - pd.Timedelta(days=730)]
        pchoice = min((pscore(rp, m)[1], m) for m in ("yesterday", "week_ago", "regression", "regression_recent"))[1]
        pk["erw"] = pk[pchoice]
        pshown = {(r[2], r[3]): dict(zip(cols, r)) for r in sc["rows"] if r[0] == p and r[1] == "demand_peak"}
        for cut, z in (("all", pk), ("last_2_years", pk[pk["day"] > pk["day"].max() - pd.Timedelta(days=730)])):
            for m in ("erw", "operator", "yesterday", "week_ago", "regression", "regression_recent"):
                n, mae, mape = pscore(z, m)
                r = pshown.get((m, cut))
                st = m in ("regression", "regression_recent") or (m == "erw" and pchoice in ("regression", "regression_recent"))
                tol_mae = 0.051 + (0.05 if st else 0)
                tol_mape = 0.0011 + (float((5.0 / z["actual"]).mean()) if st and n else 0)
                ok = r is not None and r["hours"] == n and abs(r["mae"] - mae) <= tol_mae and abs(r["mape"] - mape) <= tol_mape
                figs.append((f"{p}.peak.{m}.{cut}", None if r is None else (r["hours"], r["mae"], r["mape"]), (n, mae, mape), ok))
        # the regression refitted here on sample days
        for d in SAMPLE_DAYS:
            T = pd.Timestamp(d)
            if T not in M.index:
                continue
            for hr in (3, 17):
                for meth in ("regression", "regression_recent"):
                    mine = refit(M, T, hr, recent=meth == "regression_recent")
                    ts = x.loc[(x["day"] == T) & (x["hour"] == hr), meth]
                    stored = float(ts.iloc[0]) if len(ts) and np.isfinite(ts.iloc[0]) else None
                    ok = (mine is None and stored is None) or (mine is not None and stored is not None and abs(mine - stored) <= 0.15)
                    refits.append((f"{p}.{meth}.{d}.h{hr}", stored, mine, ok))
        print(f"{p}: chosen {chosen}, {sum(1 for f_ in figs if f_[0].startswith(p + '.') and f_[3])} of {sum(1 for f_ in figs if f_[0].startswith(p + '.'))} figures equal", flush=True)
    out = os.path.join(HERE, "figures.csv")
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["key", "page", "recomputed", "equal"])
        for r in figs + refits:
            w.writerow(r)
    nf, okf = len(figs), sum(1 for r in figs if r[3])
    nr, okr = len(refits), sum(1 for r in refits if r[3])
    print(f"scores: {okf} of {nf} figures equal; regression refitted: {okr} of {nr} equal (to 0.15 MW, the backtest table's one decimal)")
    for r in [r for r in figs + refits if not r[3]][:40]:
        print("  differs:", r)
    sys.exit(0 if okf == nf and okr == nr else 1)


if __name__ == "__main__":
    main()
