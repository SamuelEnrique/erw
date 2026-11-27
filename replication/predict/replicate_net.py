#!/usr/bin/env python3
"""Replication of the ERW forecast's net demand rows (site/data/predict/scores.json, series net_demand), chain 730,
part F. Written from docs/methods/predict.md section 20 and predict_wind_solar.md; it imports nothing of the builder,
only the other two replication scripts (replicate.py for the demand, replicate_ws.py for wind and solar). For each
region and ERCO: the demand forecast chosen by the note's rule (the regression's forecasts as stored in the backtest
table, the simple methods rebuilt), less the wind and solar forecasts chosen by theirs (rebuilt and refitted here),
against EIA-930's demand less EIA-930's wind and solar; yesterday likewise, net; the operator's where its three
forecasts are held (Texas). Prints N of N and writes replication/predict/figures_net.csv.
    python replication/predict/replicate_net.py --tables DIR --backtest PATH [--file site/data/predict/scores.json]
"""
import argparse
import csv
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import replicate as rd  # noqa: E402
import replicate_ws as rw  # noqa: E402

CHOICE = 730


def demand_erw(p, dem, tz, ops, bt):
    f = rd.local(dem[p], tz[p])
    M = rd.mat(f)
    pos = pd.Series(np.arange(len(M)), index=M.index)
    x = f[f["day"] >= rd.FIRST].copy()
    i = pos.reindex(x["day"]).to_numpy()
    k = x["hour"].to_numpy()
    raw = M.to_numpy(float)
    x["yesterday"] = np.where(i >= rd.H, raw[np.clip(i - rd.H, 0, None), k], np.nan)
    x["week_ago"] = np.where(i >= 7, raw[np.clip(i - 7, 0, None), k], np.nan)
    x["operator"] = ops[p].reindex(pd.DatetimeIndex(x["ts"])).to_numpy() if p in ops else np.nan
    for meth in ("regression", "regression_recent"):
        b = bt[(bt["x_place"] == p) & (bt["x_method"] == meth)]
        x[meth] = pd.Series(b["value"].to_numpy(float), index=pd.DatetimeIndex(pd.to_datetime(b["ts_utc"], utc=True))).reindex(pd.DatetimeIndex(x["ts"])).to_numpy()
    last = x["day"].max()
    rec = x[x["day"] > last - pd.Timedelta(days=CHOICE)].dropna(subset=["actual", "yesterday", "week_ago", "regression", "regression_recent", "operator"])
    maes = {m: rd.score(rec, m)[1] for m in ("yesterday", "week_ago", "regression", "regression_recent")}
    x["erw"] = x[min((v, m) for m, v in maes.items())[1]]
    return x.set_index("ts")


def ws_erw(wsp, fuel, rf, e):
    code = wsp.split("-")[1].upper()
    act = rw.one_series(rf[(rf["entity"] == f"eia930:{code}") & (rf["variable"] == f"net_generation_{fuel}_mw")])
    g = rw.methods(rw.local(act, rw.TZ[wsp]), rw.TZ[wsp])
    op = rw.one_series(e[(e["entity"] == "ercot:SYSTEM") & (e["variable"] == f"{fuel}_forecast_24h_mw")]) if wsp == "region-tex" else None
    g["operator"] = op.reindex(pd.DatetimeIndex(g["ts"])).to_numpy() if op is not None else np.nan
    last = g["day"].max()
    rec = g[g["day"] > last - pd.Timedelta(days=CHOICE)].dropna(subset=["actual", "yesterday", "profile7", "regression"])
    maes = {m: rw.score(rec, m)[1] for m in ("yesterday", "profile7", "regression")}
    g["erw"] = g[min((v, m) for m, v in maes.items())[1]]
    return g.set_index("ts")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tables", default=os.path.join(rd.ROOT, "warehouse", "output"))
    ap.add_argument("--backtest", default=os.path.join(rd.ROOT, "warehouse", "output", "predict_demand_backtest.csv"))
    ap.add_argument("--file", default=os.path.join(rd.ROOT, "site", "data", "predict", "scores.json"))
    a = ap.parse_args()
    sc = json.load(open(a.file, encoding="utf-8"))
    cols = sc["rows_columns"]
    shown = {(r[0], r[2], r[3]): dict(zip(cols, r)) for r in sc["rows"] if r[1] == "net_demand"}
    places = sorted({k[0] for k in shown})
    dem, tz = rd.demand_places(a.tables, places)
    ops = rd.operator(a.tables)
    bt = rd.read(a.backtest, ["ts_utc", "value", "x_place", "x_method"])
    rf = rw.read(os.path.join(a.tables, "eia930_region_fuel_hourly.csv"), ["entity", "variable", "ts_utc", "value"])
    e = rw.read(os.path.join(a.tables, "ercot_wind_solar_forecast.csv"), ["entity", "variable", "ts_utc", "value"])
    figs = []
    for p in places:
        wsp = "region-tex" if p == "ba-erco" else p
        d = demand_erw(p, dem, tz, ops, bt)
        w = ws_erw(wsp, "wind", rf, e)
        s = ws_erw(wsp, "solar", rf, e)
        x = pd.DataFrame({"day": d["day"], "hour": d["hour"]})
        for col in ("actual", "erw", "operator", "yesterday"):
            x[col] = d[col] - w[col].reindex(d.index) - s[col].reindex(d.index)
        c = x.dropna(subset=["actual", "erw", "yesterday"])
        sets = [("all", c), ("last_2_years", c[c["day"] > c["day"].max() - pd.Timedelta(days=CHOICE)])]
        co = x.dropna(subset=["actual", "erw", "yesterday", "operator"])
        ms = {"all": ["erw", "yesterday"], "last_2_years": ["erw", "yesterday"], "with_operator": ["erw", "yesterday", "operator"]}
        if len(co):
            sets.append(("with_operator", co))
        for cut, g in sets:
            for m in ms[cut]:
                n, mae, nmae = rw.score(g, m)
                r = shown.get((p, m, cut))
                ok = r is not None and r["hours"] == n and abs(r["mae"] - mae) <= 0.11 and (nmae is None or abs(r["mape"] - nmae) <= 0.011)
                figs.append((f"{p}.{m}.{cut}", None if r is None else (r["hours"], r["mae"], r["mape"]), (n, mae, nmae), ok))
        print(f"{p}: {sum(1 for f_ in figs if f_[0].startswith(p + '.') and f_[3])} of {sum(1 for f_ in figs if f_[0].startswith(p + '.'))} figures equal", flush=True)
    with open(os.path.join(HERE, "figures_net.csv"), "w", encoding="utf-8", newline="\n") as fh:
        wr = csv.writer(fh, lineterminator="\n")
        wr.writerow(["key", "file", "recomputed", "equal"])
        wr.writerows(figs)
    ok = sum(1 for f_ in figs if f_[3])
    print(f"net demand: {ok} of {len(figs)} figures equal")
    for f_ in [f_ for f_ in figs if not f_[3]][:40]:
        print("  differs:", f_)
    sys.exit(0 if ok == len(figs) else 1)


if __name__ == "__main__":
    main()
