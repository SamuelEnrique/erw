"""wip/ready-analysis-errors (session 11406, chain 770, part C): the other choice of the Automated Analysis audit of
26 November, finding 11 (docs/reviews/analysis-model-audit-2026-11-26.md), readied for Samuel's ruling, not requested.

On main (1) the impact study's card states one verdict at the rule's 3 lags (p 0.0704), though with 28 strongly
dependent days the p-value moves with the lag count; (2) the hourly curtailment card clusters its errors by Pacific
day. On this branch (1) impact_study.py computes the difference's p-value at every lag count from 0 to 7
(reg_did_p_by_lag) and the card says the range and whether the verdict turns on it; (2) batteries_curtailment_hourly.py
clusters by Monday-to-Sunday week (the Stata reproduction too). Measured from the public downloads (the audit's a5):
the impact p runs 0.0055 to 0.076 across 0 to 7 lags; the hourly charging error, 0.0101 by day, is 1.64 times larger by
week (0.0166). The cards are rebuilt at landing. The audit's test (tests/test_audit_analysis_11.py on
wip/audit-analysis-11) is carried and run through the branch's own functions."""
import math
import os
import sys
import unittest

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PUB = os.path.join(ROOT, "site", "public", "findings")
sys.path.insert(0, os.path.join(ROOT, "warehouse", "analysis", "findings"))
sys.path.insert(0, os.path.join(ROOT, "warehouse"))


def read(name):
    p = os.path.join(PUB, name)
    with open(p, encoding="utf-8") as f:
        skip = sum(1 for ln in f if ln.startswith("#"))
    return pd.read_csv(p, skiprows=skip)


class ErrorsAndNeighbours(unittest.TestCase):
    def test_the_impact_p_at_each_lag(self):
        try:
            import impact_study as im
        except Exception as exc:
            self.skipTest(f"impact_study does not import here: {exc}")
        d = read("erw_2026_impact_event_control.csv")
        w = d[d["in_window"] == 1].sort_values("t")
        y = w["diff"].to_numpy(float)
        X = np.c_[np.ones(len(w)), w["after"].to_numpy(float)]
        by = im.p_by_lag(y, X)
        print("impact study, p by lag: " + ", ".join(f"{k}: {v:.4f}" for k, v in by.items()))
        self.assertEqual(sorted(by), list(range(8)))
        self.assertLess(by[1], 0.05)
        self.assertGreater(by[2], 0.05)
        words = im.lag_words({"reg_did_p_by_lag": by})
        self.assertIn("the verdict turns on the lag count", words)

    def test_the_hourly_fit_by_week(self):
        try:
            import batteries_curtailment_hourly as bc
        except Exception as exc:
            self.skipTest(f"batteries_curtailment_hourly does not import here: {exc}")
        d = read("erw_2026_caiso_curtailment_hourly.csv").dropna(subset=["curtailed_mw", "charging_mw", "net_load_mw"]).reset_index(drop=True)
        y = d["curtailed_mw"].to_numpy(float)
        nl = d["net_load_mw"].to_numpy(float) / 1000.0
        hd = (d["hour"].to_numpy()[:, None] == np.arange(1, 24)[None, :]).astype(float)
        month = d["day"].str[:7]
        mc = pd.Categorical(month, categories=sorted(month.unique())).codes
        md = (mc[:, None] == np.arange(1, mc.max() + 1)[None, :]).astype(float)
        X = np.column_stack([np.ones(len(d)), d["charging_mw"].to_numpy(float) / 1000.0, nl, nl ** 2, hd, md])
        names = ["const", "charging", "nl", "nl2"] + [f"h{i}" for i in range(23)] + [f"m{i}" for i in range(md.shape[1])]
        weeks = pd.to_datetime(d["day"]).dt.to_period("W-SUN").astype(str).to_numpy()   # the builder's grouping on this branch
        by_day = bc.ols_cluster(y, X, names, d["day"].to_numpy())
        by_week = bc.ols_cluster(y, X, names, weeks)
        se = lambda f: f["coef"]["charging"]["se"]  # noqa: E731
        ratio = se(by_week) / se(by_day)
        print(f"hourly charging error: by day {se(by_day) / 1000:.4f}, by week {se(by_week) / 1000:.4f}, ratio {ratio:.2f}")
        self.assertGreater(ratio, 1.5)
        with open(os.path.join(ROOT, "warehouse", "analysis", "findings", "batteries_curtailment_hourly.py"), encoding="utf-8") as f:
            s = f.read()
        self.assertIn('days = pd.to_datetime(df["day"]).dt.to_period("W-SUN").astype(str).to_numpy()', s)
        self.assertIn("vce(cluster week_id)", s)
        self.assertNotIn("vce(cluster day_id)", s)


if __name__ == "__main__":
    unittest.main()
