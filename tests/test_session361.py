"""Session 361: Research's statistics (Newey-West beside HC1, the claims of a round, a step against a trend).

Energy Research Warehouse (ERW). The yearly series below are the full years of session 251's seven usable hunt drafts,
read from their own CSVs (runs/hunt/2026-10-13, not in git): fixtures for the step test's reproduction.

  1. Newey-West: at no lag it is HC1; it equals impact_study's own Newey-West; HC1 is unchanged by it;
  2. Benjamini-Hochberg q-values, by hand;
  3. the step test flags the five drafts session 251 called a step or a hump and not the two it called trends;
  4. the eleven library cards: every key they had is as the commit before session 361 wrote it, and each carries the
     round; the cards on the HC1 helper carry Newey-West, their HC1 equal to the card's own numbers;
  5. the daily run computes the cards again after the scan and adds only the files git holds.

    python -m unittest tests.test_session361 -v
"""

import json
import os
import subprocess
import sys
import unittest
from unittest import mock

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "analysis", "findings"))
import findings_common as C  # noqa: E402
import impact_study  # noqa: E402

DRAFTS = [  # (block of the verification, what, years, values, session 251 called it a step or a hump)
    ("20", "CAISO evening carbon", [2019, 2020, 2021, 2022, 2023, 2024, 2025], [11.358898, 14.209402, 11.550099, 11.421683, 7.178703, -2.119661, -9.369461], True),
    ("21", "ERCOT LZ_WEST negative hours", list(range(2015, 2026)), [1.381279, 2.413479, 2.842466, 3.047945, 2.899543, 6.762295, 9.497717, 9.954338, 7.659817, 7.79827, 5.422374], True),
    ("22", "ERCOT West hub night spread", list(range(2015, 2026)), [-0.4325, -0.1975, -0.105, 0.36625, -0.0025, -0.09125, 0.38, 1.11375, 1.37375, 0.38375, 1.53625], False),
    ("23", "PJM night wind", [2019, 2020, 2021, 2023, 2024, 2025], [3.436602, 3.514562, 3.878003, 4.079669, 4.29144, 4.326741], False),
    ("24", "CAISO evening battery discharge", [2019, 2020, 2021, 2022, 2023, 2024, 2025], [38.542532, 38.291464, 76.016507, 68.693619, 74.004945, 74.493959, 70.803552], True),
    ("25", "CAISO stress-day imports", [2019, 2020, 2021, 2022, 2023, 2024], [21.578031, 22.380822, 18.889136, 19.208914, 7.930713, 10.746853], True),
    ("26", "ERCOT LZ_SOUTH negative hours", list(range(2015, 2026)), [0.627854, 1.514117, 0.593607, 0.399543, 0.627854, 0.990437, 3.002283, 2.385845, 2.111872, 2.720856, 2.39726], True),
]
LIBRARY = ["batteries_curtailment", "batteries_curtailment_hourly", "batteries_lunch", "batteries_lunch_grids", "gas_sets_price", "impact_study",
           "negative_prices_west", "peak_hour_grids", "peak_hour_moved", "queue_divorce", "who_rescues_whom"]


def data(n=60, seed=3):
    rng = np.random.default_rng(seed)
    X = np.c_[np.ones(n), rng.normal(size=n), rng.normal(size=n)]
    e = np.convolve(rng.normal(size=n + 2), [1, 0.6, 0.3], "valid")
    return X @ [1.0, 0.5, -0.2] + e, X


class TestNeweyWest(unittest.TestCase):
    def test_no_lag_is_hc1(self):
        y, X = data()
        with mock.patch.object(C, "nw_lag", return_value=0):
            f = C.ols_hc1(y, X, ["a", "b", "c"])
        for k in "abc":
            self.assertAlmostEqual(f["coef"][k]["se_nw"], f["coef"][k]["se"], places=12)

    def test_equals_impact_studys(self):
        y, X = data(90)
        f = C.ols_hc1(y, X, ["a", "b", "c"])
        _, se, _ = impact_study.newey_west(y, X, f["nw_lag"])
        self.assertEqual(f["nw_lag"], impact_study.newey_lags(90))
        for k, s in zip("abc", se):
            self.assertAlmostEqual(f["coef"][k]["se_nw"], float(s), places=12)

    def test_lag_rule(self):
        self.assertEqual([C.nw_lag(n) for n in (24, 92, 405)], [2, 3, 5])


class TestBH(unittest.TestCase):
    def test_by_hand(self):
        # m = 4: sorted 0.01, 0.02, 0.03, 0.5 -> 0.04, 0.04, 0.04, 0.5 (each the running minimum from the top)
        self.assertEqual([round(q, 10) for q in C.bh_q([0.03, 0.01, 0.5, 0.02])], [0.04, 0.04, 0.5, 0.04])
        self.assertEqual(C.bh_q([None, 0.2]), [None, 0.2])


class TestStep(unittest.TestCase):
    def test_session_251s_five_steps(self):
        for block, what, years, values, step in DRAFTS:
            s = C.step_or_trend(years, values)
            self.assertEqual(s["step_better"], step, f"{block} {what}: {s}")
            if step:
                self.assertTrue(s["words"].startswith("a step, not a trend"))

    def test_the_break_years(self):
        breaks = {b: C.step_or_trend(y, v)["break_year"] for b, _, y, v, s in DRAFTS if s}
        self.assertEqual(breaks, {"20": "2024", "21": "2020", "24": "2021", "25": "2023", "26": "2021"})

    def test_short_series(self):
        self.assertIsNone(C.step_or_trend([2020, 2021, 2022], [1, 2, 3]))
        self.assertIsNone(C.trend_p([2020, 2021], [1, 2]))


class TestCards(unittest.TestCase):
    def card(self, cid, rev=None):
        p = f"site/data/findings/{cid}.json"
        if rev:
            r = subprocess.run(["git", "show", f"{rev}:{p}"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
            return json.loads(r.stdout) if r.returncode == 0 else None
        with open(os.path.join(ROOT, p), encoding="utf-8") as f:
            return json.load(f)

    def test_every_key_as_before(self):
        r = subprocess.run(["git", "log", "--format=%H", "-1", "--", "site/data/findings/batteries_lunch.json"], cwd=ROOT, capture_output=True, text=True)
        head = r.stdout.strip()
        if not head:
            self.skipTest("no history of the cards here")
        before_rev = None
        for sha in subprocess.run(["git", "log", "--format=%H", "--", "site/data/findings/batteries_lunch.json"], cwd=ROOT, capture_output=True, text=True).stdout.split():
            old = self.card("batteries_lunch", sha)
            if old is not None and "statistics" not in old:
                before_rev = sha
                break
        if before_rev is None:
            self.skipTest("no commit of the cards before session 361 here")
        for cid in LIBRARY:
            old, new = self.card(cid, before_rev), self.card(cid)
            if old is None or "statistics" in old or new.get("computed_at") != old.get("computed_at"):
                continue  # recomputed since by the daily run: its numbers are the day's
            for k, v in old.items():
                self.assertEqual(new.get(k), v, f"{cid}: {k} moved")

    def test_round_and_newey_west(self):
        for cid in LIBRARY:
            s = self.card(cid)["statistics"]
            self.assertEqual(s["round"]["claims_tested"], self.card(LIBRARY[0])["statistics"]["round"]["claims_tested"], cid)  # one round
            self.assertGreater(s["round"]["claims_tested"], 0, cid)
        for cid, n in (("batteries_lunch", 3), ("batteries_lunch_grids", 15), ("batteries_curtailment", 4)):
            c = self.card(cid)
            rows = c["statistics"]["newey_west"]["rows"]
            self.assertEqual(len(rows), n)
            for r in rows:
                self.assertAlmostEqual(r["se_hc1"] / c["numbers"][r["numbers_key"] + "_se"], 1.0, places=9)
                self.assertGreater(r["se_nw"], 0)
        self.assertNotIn("newey_west", self.card("impact_study")["statistics"])


class TestDailyRun(unittest.TestCase):
    def test_step_after_the_scan(self):
        with open(os.path.join(ROOT, "warehouse", "run_data_machine.sh"), encoding="utf-8") as f:
            s = f.read()
        self.assertLess(s.index("soft_step dm_scanner"), s.index("soft_step dm_findings_recompute"))
        self.assertIn("put_back dm_findings_recompute site/data/findings site/public/findings", s)
        self.assertIn("git add -u -- site/data/findings site/public/findings", s)
        self.assertIn("warehouse/metadata/findings_recompute.csv", s)


if __name__ == "__main__":
    unittest.main()
