"""Session 47: the event study module.

Energy Research Warehouse (ERW). No network, no model.
1. warehouse/derived/event_study.py's estimator against a synthetic panel with a known effect: baseline years at -5
   and +5 about their mean, a day-of-week pattern, an event-day effect of 20 + k (recovered exactly per day with no
   noise) and a constant effect of 25 (recovered by the pooled indicator; its interval covers it with noise).
2. The event windows of event_study.py and site/lib/eventstudy.ts are event_window.py's.
3. site/scripts/test-eventstudy.mjs: the TypeScript twin on the same synthetic panel, and equal to the Python table on
   every daily and pooled estimate where the warehouse files are on this machine.
4. The table, where it is on this machine: each interval is the estimate +/- 1.96 standard errors.
5. notebooks/event_study.ipynb runs and reproduces the table (it asserts so itself).

    python -m unittest tests.test_session47 -v
"""

import os
import re
import shutil
import subprocess
import sys
import unittest

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import event_study as es  # noqa: E402


def panel(noise, constant, seed=7):
    rng = np.random.default_rng(seed)
    dates, y, ev, truth = [], [], [], []
    for yr, lvl in ((2019, -5.0), (2020, 5.0), (2021, 0.0)):
        for k in range(20):
            d = pd.Timestamp(yr, 2, 1 + k)
            effect = (25.0 if constant else 20.0 + k) if yr == 2021 else 0.0
            dates.append(d.strftime("%Y-%m-%d"))
            ev.append(yr == 2021)
            truth.append(effect)
            y.append(100 + lvl + 3 * d.dayofweek + effect + noise * rng.standard_normal())
    return dates, np.array(y), ev, truth


class Estimator(unittest.TestCase):
    def test_each_day_recovered_exactly_without_noise(self):
        dates, y, ev, truth = panel(0, constant=False)
        r = es.estimate(dates, y, ev)
        got = [d["estimate"] for d in r["days"]]
        self.assertTrue(np.allclose(got, [t for t, e in zip(truth, ev) if e], atol=1e-9), got)

    def test_a_constant_effect_is_the_pooled_effect(self):
        dates, y, ev, _ = panel(0, constant=True)
        self.assertAlmostEqual(es.estimate(dates, y, ev)["pooled"]["estimate"], 25.0, places=9)
        # with noise, the 95 percent interval covers the truth in about 95 of 100 panels (one panel can miss by chance)
        hits = 0
        for seed in range(200):
            dates, y, ev, _ = panel(2, constant=True, seed=seed)
            p = es.estimate(dates, y, ev)["pooled"]
            hits += abs(p["estimate"] - 25.0) < es.Z * p["se"]
        self.assertTrue(0.88 <= hits / 200 <= 0.99, hits)

    def test_a_day_standard_error_includes_the_days_own_noise(self):
        dates, y, ev, _ = panel(2, constant=True)
        r = es.estimate(dates, y, ev)
        self.assertTrue(all(d["se"] > 1.0 for d in r["days"]))  # noise sd 2: the day's own noise is in its error


class Windows(unittest.TestCase):
    def test_windows_match_event_window_py(self):
        src = open(os.path.join(ROOT, "warehouse", "derived", "event_window.py"), encoding="utf-8").read()
        ts = open(os.path.join(ROOT, "site", "lib", "eventstudy.ts"), encoding="utf-8").read()
        for ev, (s, e) in es.WINDOWS.items():
            i = src.index(f'event="{ev}"')
            self.assertIn(f'start="{s}", end="{e}"', src[i:i + 300], ev)
            self.assertIn(f'{ev}: ["{s}", "{e}"]', ts, ev)


class TypeScriptTwin(unittest.TestCase):
    def test_synthetic_and_parity(self):
        node = shutil.which("node")
        if not node:
            self.skipTest("node is not installed")
        r = subprocess.run([node, os.path.join("scripts", "test-eventstudy.mjs")], cwd=os.path.join(ROOT, "site"),
                           capture_output=True, text=True, timeout=300)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


class Notebook(unittest.TestCase):
    def test_the_replication_notebook_reproduces_the_table(self):
        """notebooks/event_study.ipynb, its code cells run in order: it asserts its estimates equal the table's."""
        import json
        if not os.path.exists(os.path.join(ROOT, "warehouse", "output", "event_study_estimates.csv")):
            self.skipTest("the warehouse tables are not on this machine")
        sys.path.insert(0, os.path.join(ROOT, "package", "src"))
        nb = json.load(open(os.path.join(ROOT, "notebooks", "event_study.ipynb"), encoding="utf-8"))
        g = {}
        for c in nb["cells"]:
            if c["cell_type"] == "code":
                exec("".join(c["source"]), g)  # noqa: S102  the repository's own notebook
        self.assertEqual(len(g["pooled"]), 21)


class Table(unittest.TestCase):
    def test_intervals(self):
        path = os.path.join(ROOT, "warehouse", "output", "event_study_estimates.csv")
        if not os.path.exists(path):
            self.skipTest("event_study_estimates.csv is not on this machine")
        n = sum(1 for ln in open(path, encoding="utf-8") if ln.startswith("#"))
        df = pd.read_csv(path, skiprows=n)
        se = df.dropna(subset=["x_std_error"])
        self.assertTrue(np.allclose(se["x_ci_low"], se["value"] - es.Z * se["x_std_error"], atol=1e-4))
        self.assertTrue(np.allclose(se["x_ci_high"], se["value"] + es.Z * se["x_std_error"], atol=1e-4))
        self.assertTrue(set(df["x_spec"]) <= {es.SPEC, es.SPEC_T, es.SPEC_R})  # session 49: two more specifications
        self.assertTrue(all(re.match(r"^(demand_mwh|rt_mean)_(effect_day|effect_pooled|counterfactual_mean)(_temp)?$|^(demand_mwh|rt_mean)_effect_pooled_trend$|^demand_mw_effect_h\d\d$", v)
                            for v in df["variable"]))


if __name__ == "__main__":
    unittest.main()
