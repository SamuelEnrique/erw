"""Audit of Automated Analysis, finding 11 (session 10204, docs/reviews/analysis-model-audit-2026-11-26.md): what the
cards' standard errors assume about neighbouring days and hours.

From the public downloads alone:
  the impact study's default card (28 days, Uri): its Newey-West error at the rule's 3 lags equals the card's, and the
    p-value crosses 0.05 between 1 and 2 lags (0.031 at 1, 0.055 at 2), so the verdict hangs on the lag count;
  the hourly curtailment card: its error clustered by Pacific day equals the card's, and clustered by Monday-to-Sunday
    week it is more than 1.5 times larger (1.64; the audit's a5).
Passes on main; showing several lags or clustering by week moves a figure: the owner's ruling.

No table, no request, no model call; the environment is read, never set."""
import math
import os
import unittest

import numpy as np
import pandas as pd
from scipy import stats

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PUB = os.path.join(ROOT, "site", "public", "findings")


def read(name):
    p = os.path.join(PUB, name)
    with open(p, encoding="utf-8") as f:
        skip = sum(1 for ln in f if ln.startswith("#"))
    return pd.read_csv(p, skiprows=skip)


def newey(y, X, L):
    n, k = X.shape
    inv = np.linalg.inv(X.T @ X)
    b = inv @ X.T @ y
    e = y - X @ b
    S = (X * e[:, None]).T @ (X * e[:, None])
    for j in range(1, L + 1):
        G = (X[j:] * e[j:, None]).T @ (X[:-j] * e[:-j, None])
        S += (1 - j / (L + 1)) * (G + G.T)
    se = np.sqrt(np.diag((n / (n - k)) * inv @ S @ inv))
    return b[1], se[1], 2 * stats.t.sf(abs(b[1] / se[1]), n - k)


def clustered(y, X, g):
    n, k = X.shape
    inv = np.linalg.inv(X.T @ X)
    b = inv @ X.T @ y
    e = y - X @ b
    codes, uniq = pd.factorize(np.asarray(g), sort=True)
    S = np.zeros((len(uniq), k))
    np.add.at(S, codes, X * e[:, None])
    G = len(uniq)
    return b[1], math.sqrt(((G / (G - 1)) * ((n - 1) / (n - k)) * (inv @ (S.T @ S) @ inv))[1, 1])


class ErrorsAndNeighbours(unittest.TestCase):
    def test_impact_verdict_hangs_on_the_lag(self):
        d = read("erw_2026_impact_event_control.csv")
        w = d[d["in_window"] == 1].sort_values("t")
        y = w["diff"].to_numpy(float)
        X = np.c_[np.ones(len(w)), w["after"].to_numpy(float)]
        b, se, p = newey(y, X, int(math.floor(4 * (len(w) / 100) ** (2 / 9))))
        self.assertAlmostEqual(b, 3016.4007, places=3)
        self.assertAlmostEqual(se, 1598.9276, places=3)
        self.assertLess(newey(y, X, 1)[2], 0.05)
        self.assertGreater(newey(y, X, 2)[2], 0.05)

    def test_hourly_error_by_week_is_larger(self):
        d = read("erw_2026_caiso_curtailment_hourly.csv").dropna(subset=["curtailed_mw", "charging_mw", "net_load_mw"]).reset_index(drop=True)
        y = d["curtailed_mw"].to_numpy(float)
        nl = d["net_load_mw"].to_numpy(float) / 1000.0
        hd = (d["hour"].to_numpy()[:, None] == np.arange(1, 24)[None, :]).astype(float)
        month = d["day"].str[:7]
        mc = pd.Categorical(month, categories=sorted(month.unique())).codes
        md = (mc[:, None] == np.arange(1, mc.max() + 1)[None, :]).astype(float)
        X = np.column_stack([np.ones(len(d)), d["charging_mw"].to_numpy(float) / 1000.0, nl, nl ** 2, hd, md])
        day = pd.to_datetime(d["day"])
        week = (day - pd.to_timedelta(day.dt.dayofweek, unit="D")).dt.strftime("%Y-%m-%d").to_numpy()
        b, se_day = clustered(y, X, d["day"].to_numpy())
        _, se_week = clustered(y, X, week)
        self.assertAlmostEqual(b / 1000, -0.0956246, places=6)
        self.assertAlmostEqual(se_day / 1000, 0.0101466, places=6)
        self.assertGreater(se_week / se_day, 1.5)


if __name__ == "__main__":
    unittest.main()
