#!/usr/bin/env python3
"""Replication of the ERW forecast of the day-ahead hub price (session 10603, chain 730): the price rows of
site/data/predict/scores.json (the six places whose grid's hub prices are public, method note predict_price.md
sections 1 to 4) and every row of site/data/predict/price_hubs.json (the four hubs added, section 10).

Written from docs/methods/predict_price.md and docs/methods/predict.md, not from warehouse/predict/: it imports nothing
of the builder (the demand readers and the last-whole-day rule are replication/predict/replicate.py's). Everything is
rebuilt from the public tables: the hub's day-ahead prices (later tables win for the same hour), the place's demand,
Henry Hub; the demand regression made with demand through T-3 (predict.md section 3, refitted here for every target
day), the price regression of section 3 refitted for every target day, the two simple methods, the choice by the rule,
and every score of every cut. Ordinary least squares on each window's own rows (numpy.linalg.lstsq).

    python replication/predict/replicate_price.py --tables DIR [--scores site/data/predict/scores.json] [--hubs site/data/predict/price_hubs.json]
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
sys.path.append(HERE)
import replicate as rep  # noqa: E402  (the replication's own readers)

FIRST = pd.Timestamp("2019-07-01")
HP, HD, FIT, MIN_FIT, CHOICE, FLOOR, SPIKE, GAS_LAG = 1, 3, 730, 300, 730, 5.0, 0.99, 10
TABLES = ["ercot_all_hub_prices_history", "iso_hub_prices_history_2018", "iso_hub_prices_history", "iso_dam_hub_prices"]
# the place files (section 1): place -> hub; the hubs added (section 10): hub-<grid> -> (hub, the grid's demand place)
PLACE_HUB = {"region-tex": "ercot:HB_NORTH", "ba-erco": "ercot:HB_NORTH", "region-cent": "spp:SPPNORTH_HUB", "ba-swpp": "spp:SPPNORTH_HUB",
             "region-cal": "caiso:TH_SP15_GEN-APND", "ba-ciso": "caiso:TH_SP15_GEN-APND"}
HUB_PLACES = {"hub-ercot-houston": ("ercot:HB_HOUSTON", "ba-erco"), "hub-ercot-south": ("ercot:HB_SOUTH", "ba-erco"),
              "hub-ercot-west": ("ercot:HB_WEST", "ba-erco"), "hub-caiso-np15": ("caiso:TH_NP15_GEN-APND", "ba-ciso")}
METHODS = ["erw", "yesterday", "week_ago", "regression"]


def dam(tables, hubs):
    frames = []
    for order, t in enumerate(TABLES):
        d = rep.read(os.path.join(tables, t + ".csv"), ["entity", "ts_utc", "value", "market"])
        d = d[d["entity"].isin(hubs) & d["market"].astype(str).str.endswith("_dam")].copy()
        d["order"] = order
        frames.append(d)
    d = pd.concat(frames)
    d["ts"] = pd.to_datetime(d["ts_utc"], utc=True)
    d = d.sort_values(["entity", "ts", "order"]).drop_duplicates(["entity", "ts"], keep="last")
    return {e: pd.Series(g["value"].to_numpy(float), index=pd.DatetimeIndex(g["ts"])).dropna() for e, g in d.groupby("entity")}


def henry(tables):
    d = rep.read(os.path.join(tables, "eia_fuel_spot_prices.csv"), ["entity", "variable", "ts_utc", "value"])
    d = d[(d["entity"] == "eia:henry_hub") & (d["variable"] == "spot_price")]
    s = pd.Series(d["value"].to_numpy(float), index=pd.to_datetime(d["ts_utc"], utc=True).dt.tz_localize(None).dt.normalize())
    return s[~s.index.duplicated(keep="last")].sort_index().dropna()


def calendar(days):
    hol_days = USFederalHolidayCalendar().holidays(days.min() - pd.Timedelta(days=400), days.max() + pd.Timedelta(days=400))
    thanks = hol_days[(hol_days.month == 11) & (hol_days.day >= 22) & (hol_days.dayofweek == 3)]
    hol = np.asarray(days.isin(hol_days))
    bri = np.asarray(days.isin(thanks + pd.Timedelta(days=1)) | ((days.month == 12) & ((days.day == 24) | (days.day >= 26)))) & ~hol
    return hol.astype(float), bri.astype(float)


def lag(a, d):
    o = np.full(a.shape, np.nan)
    o[d:] = a[:len(a) - d]
    return o


def fill_lone(raw):
    f = raw.copy()
    for j in range(1, 23):
        lone = np.isnan(raw[:, j]) & ~np.isnan(raw[:, j - 1]) & ~np.isnan(raw[:, j + 1])
        f[lone, j] = (raw[lone, j - 1] + raw[lone, j + 1]) / 2
    return f


def walk(X, Y, h):
    """For each day i and hour k: OLS on the rows j = i-h-729 .. i-h held with every regressor (at least 300)."""
    n, K, _ = X.shape
    ok = np.isfinite(X).all(axis=2) & np.isfinite(Y)
    P = np.full((n, K), np.nan)
    for i in range(h, n):
        j1, j0 = i - h + 1, max(0, i - h + 1 - FIT)
        for k in range(K):
            v = ok[j0:j1, k]
            if v.sum() < MIN_FIT or not np.isfinite(X[i, k]).all():
                continue
            P[i, k] = float(X[i, k] @ np.linalg.lstsq(X[j0:j1, k][v], Y[j0:j1, k][v], rcond=None)[0])
    return P


def demand_regression(dem, tz, h=HD):
    """predict.md section 3: the regression in logs, made with demand through day T-h. Returns (days, forecast MW, M)."""
    f = rep.local(dem, tz)
    M = rep.mat(f)
    M = M.reindex(pd.date_range(M.index.min(), M.index.max() + pd.Timedelta(days=h), freq="D"))
    days = M.index
    raw = M.to_numpy(float)
    fil = fill_lone(raw)
    with np.errstate(divide="ignore", invalid="ignore"):
        lf = np.log(np.where(fil > 0, fil, np.nan))
        ly = np.log(np.where(raw > 0, raw, np.nan))
    dmean = np.where((np.isnan(fil) | ~(fil > 0)).any(axis=1), np.nan, np.nanmean(np.where(fil > 0, fil, np.nan), axis=1))
    week = np.log(pd.Series(dmean).rolling(7, min_periods=5).mean().to_numpy())
    hol, bri = calendar(days)
    dow, dowA = days.dayofweek.to_numpy(), (days - pd.Timedelta(days=h)).dayofweek.to_numpy()
    t = days.dayofyear.to_numpy() / 365.25
    common = [np.log(lag(dmean, h)), lag(week, h)] + [(dow == w).astype(float) for w in range(6)] + [(dowA == w).astype(float) for w in range(6)]
    common += [hol, bri, lag(hol, h), lag(bri, h), lag(hol, 7), lag(bri, 7), np.sin(2 * np.pi * t), np.cos(2 * np.pi * t), np.sin(4 * np.pi * t), np.cos(4 * np.pi * t)]
    lA, l7 = lag(lf, h), lag(lf, 7)
    X = np.stack([np.stack([np.ones(len(days)), lA[:, k], common[0], l7[:, k]] + common[1:], axis=1) for k in range(24)], axis=1)
    return days, np.exp(walk(X, ly, h)), M


def price_place(price, tz, dem, dtz, gas):
    """predict_price.md sections 2 to 4 for one hub read with one place's demand: the hourly frame of target days."""
    f = rep.local(price, tz)
    M = rep.mat(f)
    M = M.reindex(pd.date_range(M.index.min(), M.index.max() + pd.Timedelta(days=HP), freq="D"))
    days = M.index
    raw = M.to_numpy(float)
    fil = fill_lone(raw)
    dmean_p = np.mean(fil, axis=1)
    week = pd.Series(dmean_p).rolling(7, min_periods=5).mean().to_numpy()
    ddays, dfc, Md = demand_regression(dem, dtz)
    Dfc = pd.DataFrame(dfc, index=ddays).reindex(days).to_numpy()
    dmean_d = np.mean(Md.reindex(days).to_numpy(float), axis=1)
    dweek = lag(pd.Series(dmean_d).rolling(7, min_periods=5).mean().to_numpy(), HD)
    ratio = Dfc / dweek[:, None]
    g = gas.index.searchsorted(days - pd.Timedelta(days=1 + GAS_LAG), side="right") - 1
    hh = np.where(g >= 0, gas.to_numpy()[np.clip(g, 0, None)], np.nan)
    hol, bri = calendar(days)
    dow = days.dayofweek.to_numpy()
    t = days.dayofyear.to_numpy() / 365.25
    pA, p7 = lag(fil, HP), lag(fil, 7)
    tail = [hh] + [(dow == w).astype(float) for w in range(6)] + [hol, bri, np.sin(2 * np.pi * t), np.cos(2 * np.pi * t)]
    X = np.stack([np.stack([np.ones(len(days)), pA[:, k], lag(dmean_p, HP), p7[:, k], lag(week, HP), ratio[:, k], ratio[:, k] ** 2] + tail, axis=1)
                  for k in range(24)], axis=1)
    P = walk(X, raw, HP)
    pos = pd.Series(np.arange(len(days)), index=days)
    x = f[f["day"] >= FIRST].copy()
    i = pos.reindex(x["day"]).to_numpy()
    k = x["hour"].to_numpy()
    x["yesterday"], x["week_ago"], x["regression"] = lag(raw, HP)[i, k], lag(raw, 7)[i, k], P[i, k]
    return x.reset_index(drop=True)


def metric(x, m, floor=None):
    if not len(x):
        return 0, None, None
    e = (x[m] - x["actual"]).abs()
    a = x["actual"].abs()
    keep = a >= floor if floor is not None else a > 0
    return int(len(x)), round(float(e.mean()), 2), (round(float((e[keep] / a[keep]).mean() * 100), 3) if keep.any() else None)


def figures(place, x, shown, events):
    rec = x[x["day"] > x["day"].max() - pd.Timedelta(days=CHOICE)].dropna(subset=["actual", "yesterday", "week_ago", "regression"])
    maes = {m: metric(rec, m)[1] for m in ("yesterday", "week_ago", "regression")}
    x["erw"] = x[min((v, m) for m, v in maes.items() if v is not None)[1]]
    c = x.dropna(subset=["actual"] + METHODS).reset_index(drop=True)
    r2 = (c["day"] > c["day"].max() - pd.Timedelta(days=CHOICE)).to_numpy()
    cuts = {("all", ""): np.ones(len(c), bool), ("last_2_years", ""): r2}
    mo = c["day"].dt.strftime("%Y-%m").to_numpy()
    for m_ in sorted(set(mo)):
        cuts[("month", m_)] = mo == m_
    for h in range(24):
        cuts[("hour", str(h))] = r2 & (c["hour"].to_numpy() == h)
    top = set(c.groupby("day")["actual"].max().dropna().sort_values(ascending=False).index[:10])
    cuts[("top10", "")] = c["day"].isin(top).to_numpy()
    for eid, (s0, s1) in events.items():
        msk = ((c["day"] >= s0) & (c["day"] <= s1)).to_numpy()
        if msk.any():
            cuts[("event", eid)] = msk
    cuts[("spike", "")] = (c["actual"] > c["actual"].quantile(SPIKE)).to_numpy()
    out = []
    for (cut, key), msk in cuts.items():
        for m in METHODS:
            n, mae, mape = metric(c[msk], m, FLOOR)
            r = shown.get((place, m, cut, key))
            ok = r is not None and r["hours"] == n and ((mae is None and r["mae"] is None) or (mae is not None and r["mae"] is not None and abs(r["mae"] - mae) <= 0.011)) and \
                ((mape is None and r["mape"] is None) or (mape is not None and r["mape"] is not None and abs(r["mape"] - mape) <= 0.0011))
            out.append((f"{place}.{m}.{cut}.{key}", None if r is None else (r["hours"], r["mae"], r["mape"]), (n, mae, mape), ok))
    extra = {k for k in shown if k[0] == place and k[1] in METHODS and (k[2], k[3]) not in cuts}
    for k in sorted(extra):
        out.append((".".join(k), shown[k], None, False))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tables", default=os.path.join(ROOT, "warehouse", "output"))
    ap.add_argument("--scores", default=os.path.join(ROOT, "site", "data", "predict", "scores.json"))
    ap.add_argument("--hubs", default=os.path.join(ROOT, "site", "data", "predict", "price_hubs.json"))
    a = ap.parse_args()
    shown = {}
    for path in (a.scores, a.hubs):
        doc = json.load(open(path, encoding="utf-8"))
        cols = doc["rows_columns"]
        for r in doc["rows"]:
            d = dict(zip(cols, r))
            if d["series"] == "price" and d["method"] in METHODS:
                shown[(d["place"], d["method"], d["cut"], d["key"])] = d
    events = {}
    for p in sorted(glob.glob(os.path.join(ROOT, "site", "data", "regions", "events", "*.json"))):
        e = json.load(open(p, encoding="utf-8"))
        if e.get("start") and e.get("end"):
            events[os.path.basename(p)[:-5].replace("_", "-")] = (pd.Timestamp(e["start"]), pd.Timestamp(e["end"]))
    demand_needed = sorted(set(PLACE_HUB) | {v[1] for v in HUB_PLACES.values()})
    dem, tz = rep.demand_places(a.tables, demand_needed)
    prices = dam(a.tables, sorted(set(PLACE_HUB.values()) | {v[0] for v in HUB_PLACES.values()}))
    gas = henry(a.tables)
    figs = []
    jobs = [(p, hub, p) for p, hub in PLACE_HUB.items()] + [(p, hub, dp) for p, (hub, dp) in HUB_PLACES.items()]
    for place, hub, dp in jobs:
        x = price_place(prices[hub], tz[dp], dem[dp], tz[dp], gas)
        got = figures(place, x, shown, events)
        figs += got
        print(f"{place} ({hub}, demand {dp}): {sum(1 for g in got if g[3])} of {len(got)} figures equal", flush=True)
    with open(os.path.join(HERE, "figures_price.csv"), "w", encoding="utf-8", newline="\n") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["key", "file", "recomputed", "equal"])
        w.writerows(figs)
    ok = sum(1 for f_ in figs if f_[3])
    print(f"day-ahead price: {ok} of {len(figs)} figures equal")
    for f_ in [f_ for f_ in figs if not f_[3]][:40]:
        print("  differs:", f_)
    sys.exit(0 if ok == len(figs) else 1)


if __name__ == "__main__":
    main()
