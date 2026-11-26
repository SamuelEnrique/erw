"""Audit of Automated Analysis (session 10204): the cards' regressions re-done by hand from their own downloads.

1. impact_study (default card: ERCOT North Hub against NYISO New York City, Uri, 14 days): b and its Newey-West error
   from the CSV's in-window rows, written out (no statsmodels), then the same error at other lag counts.
2. batteries_curtailment_hourly: the third fit (charging, net load and its square, 23 hour and the month-of-sample
   dummies) by least squares, its error clustered by day (Stata's factor), then clustered by week and by month.
3. batteries_lunch_grids, batteries_curtailment, batteries_lunch: each regression's p by HC1 (the card's) and by
   Newey-West (beside it), and which cross 0.05.

Run: python runs/a5_cards.py <repo root> > runs/a5.out
"""
import json
import math
import os
import sys

import numpy as np
import pandas as pd
from scipy import stats

ROOT = sys.argv[1]
PUB = os.path.join(ROOT, "site", "public", "findings")
DATA = os.path.join(ROOT, "site", "data", "findings")


def read(path):
    with open(path, encoding="utf-8") as f:
        skip = sum(1 for ln in f if ln.startswith("#"))
    return pd.read_csv(path, skiprows=skip)


def newey(y, X, L):
    n, k = X.shape
    XtX_inv = np.linalg.inv(X.T @ X)
    b = XtX_inv @ X.T @ y
    e = y - X @ b
    S = (X * e[:, None]).T @ (X * e[:, None])
    for j in range(1, L + 1):
        G = (X[j:] * e[j:, None]).T @ (X[:-j] * e[:-j, None])
        S += (1 - j / (L + 1)) * (G + G.T)
    V = (n / (n - k)) * XtX_inv @ S @ XtX_inv
    se = np.sqrt(np.diag(V))
    p = 2 * stats.t.sf(np.abs(b / se), n - k)
    return b, se, p


def impact():
    d = read(os.path.join(PUB, "erw_2026_impact_event_control.csv"))
    print("impact_study CSV rows:", len(d), "of which in the window:", int(d["in_window"].sum()),
          "; control_value cells held (NYISO New York City, daily):", int(d["control_value"].notna().sum()))
    w = d[d["in_window"] == 1].sort_values("t")
    y = w["diff"].to_numpy(float)
    X = np.c_[np.ones(len(w)), w["after"].to_numpy(float)]
    n = len(w)
    L = int(math.floor(4 * (n / 100) ** (2 / 9)))
    b, se, p = newey(y, X, L)
    print(f"  n {n}, lag rule gives {L}; b {b[1]:.4f}, se {se[1]:.4f}, p {p[1]:.4f}  (card: 3,016.4007, 1,598.9276, 0.0704)")
    did = (w.loc[w.after == 1, "series_value"].mean() - w.loc[w.after == 0, "series_value"].mean()) - \
          (w.loc[w.after == 1, "control_value"].mean() - w.loc[w.after == 0, "control_value"].mean())
    print(f"  difference in differences from the means: {did:.4f}")
    for lag in (0, 1, 2, 3, 5, 7, 10, 13):
        b, se, p = newey(y, X, lag)
        print(f"  lags {lag:2d}: se {se[1]:9.2f}, p {p[1]:.4f}")
    # the plain OLS error, which assumes independent days
    e = y - X @ np.linalg.lstsq(X, y, rcond=None)[0]
    s2 = (e @ e) / (n - 2)
    se_ols = math.sqrt(s2 * np.linalg.inv(X.T @ X)[1, 1])
    print(f"  ordinary least squares error (independent, equal-variance days): {se_ols:.2f}")
    # the autocorrelation of the residuals within each half, which the lag rule is meant to cover
    for a in (0, 1):
        r = w.loc[w.after == a, "diff"].to_numpy(float)
        r = r - r.mean()
        rho = [float((r[k:] * r[:-k]).sum() / (r * r).sum()) for k in (1, 2, 3, 5, 7)]
        print(f"  residual autocorrelation, after={a}, lags 1,2,3,5,7: " + ", ".join(f"{x:.3f}" for x in rho))


def cluster(y, X, groups):
    n, k = X.shape
    bread = np.linalg.inv(X.T @ X)
    b = bread @ (X.T @ y)
    e = y - X @ b
    codes, uniq = pd.factorize(np.asarray(groups), sort=True)
    S = np.zeros((len(uniq), k))
    np.add.at(S, codes, X * e[:, None])
    g = len(uniq)
    V = (g / (g - 1)) * ((n - 1) / (n - k)) * (bread @ (S.T @ S) @ bread)
    se = np.sqrt(np.diag(V))
    p = 2 * stats.t.sf(np.abs(b / se), g - 1)
    return b, se, p, g


def hourly():
    d = read(os.path.join(PUB, "erw_2026_caiso_curtailment_hourly.csv"))
    d = d.dropna(subset=["curtailed_mw", "charging_mw", "net_load_mw"]).reset_index(drop=True)
    y = d["curtailed_mw"].to_numpy(float)
    chg = d["charging_mw"].to_numpy(float) / 1000.0
    nl = d["net_load_mw"].to_numpy(float) / 1000.0
    hd = (d["hour"].to_numpy()[:, None] == np.arange(1, 24)[None, :]).astype(float)
    month = d["day"].str[:7]
    months = sorted(month.unique())
    mc = pd.Categorical(month, categories=months).codes
    md = (mc[:, None] == np.arange(1, len(months))[None, :]).astype(float)
    X = np.column_stack([np.ones(len(d)), chg, nl, nl ** 2, hd, md])
    del hd, md
    day = pd.to_datetime(d["day"])
    week = (day - pd.to_timedelta(day.dt.dayofweek, unit="D")).dt.strftime("%Y-%m-%d")
    print(f"batteries_curtailment_hourly: n {len(d)}, k {X.shape[1]}, months {len(months)}")
    for name, g in (("day", d["day"]), ("week (Monday to Sunday)", week), ("month", month)):
        b, se, p, G = cluster(y, X, g.to_numpy())
        print(f"  clustered by {name}: {G} clusters; charging per MW {b[1] / 1000:.7f}, se {se[1] / 1000:.7f}, t {b[1] / se[1]:.2f}, p {p[1]:.3g}")
    print("  card: -0.0956246, se 0.0101466 (clustered by day)")


def nw_rows():
    for card in ("batteries_lunch_grids", "batteries_curtailment", "batteries_lunch"):
        j = json.load(open(os.path.join(DATA, card + ".json"), encoding="utf-8"))
        rows = (j.get("statistics") or {}).get("newey_west", {}).get("rows", [])
        flips = [r for r in rows if (r["p_hc1"] < 0.05) != (r["p_nw"] < 0.05)]
        print(f"{card}: {len(rows)} regressions; HC1 p < 0.05: {sum(r['p_hc1'] < 0.05 for r in rows)}; Newey-West p < 0.05: {sum(r['p_nw'] < 0.05 for r in rows)}")
        for r in flips:
            print(f"   crosses 0.05: {r['spec']} coef {r['coef']:.4g}, HC1 se {r['se_hc1']:.4g} p {r['p_hc1']:.4f}; NW se {r['se_nw']:.4g} p {r['p_nw']:.4f}, lags {r['nw_lag']}, n {r['n']}")


if __name__ == "__main__":
    impact()
    nw_rows()
    hourly()
