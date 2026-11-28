"""Session 10000 (chain 701, done-line request 577): the place file's forecast for tomorrow is the ledger's, once the ledger
holds that day. A second run on the same day had drawn a newer making on the page while the ledger kept the first.
Made-up frames; no table is read."""
import importlib.util
import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def load():
    sys.path.insert(0, os.path.join(ROOT, "warehouse", "predict"))
    spec = importlib.util.spec_from_file_location("predict_run_t", os.path.join(ROOT, "warehouse", "predict", "run.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class TheLedgersMakingIsDrawn(unittest.TestCase):
    def setUp(self):
        self.m = load()
        ts = pd.to_datetime(["2026-11-27T06:00:00Z", "2026-11-27T07:00:00Z"], utc=True)
        self.tm = pd.DataFrame({"ts": ts, "hour": [0, 1], "regression_recent": [100.0, 110.0], "regression_recent_lo": [90.0, 99.0],
                                "regression_recent_hi": [110.0, 121.0], "operator": [105.0, 108.0]})
        self.p = {"place": "region-tex", "target": pd.Timestamp("2026-11-27"), "tomorrow": self.tm, "choice": "regression_recent"}
        self.ledger = pd.DataFrame({"series": ["demand", "demand"], "place": ["region-tex"] * 2, "target_day": ["2026-11-27"] * 2,
                                    "ts_utc": ["2026-11-27T06:00:00Z", "2026-11-27T07:00:00Z"], "local_hour": ["0", "1"],
                                    "made_utc": ["2026-11-26T11:00:00Z"] * 2,
                                    # session 11200: the ledger's two columns its real file carries (LEDGER_COLS), which
                                    # the old laptop's row 135 reads (a tomorrow from the ledger carries its horizon)
                                    "inputs_through_utc": ["2026-11-25T05:00:00Z"] * 2, "horizon_days": ["2"] * 2,
                                    "method": ["regression"] * 2,
                                    "erw": ["95.5", "104.5"], "lo": ["85", "94"], "hi": ["106", "115"]})

    def test_the_ledger_wins(self):
        p, made, method = self.m.from_ledger(self.p, self.ledger, "demand")
        self.assertEqual((made, method, p["choice"]), ("2026-11-26T11:00:00Z", "regression", "regression"))
        self.assertEqual(list(p["tomorrow"]["regression"]), [95.5, 104.5])
        self.assertEqual(list(p["tomorrow"]["regression_hi"]), [106.0, 115.0])
        self.assertEqual(list(p["tomorrow"]["operator"]), [105.0, 108.0])   # the operator's own forecast is kept beside it

    def test_no_ledger_day_leaves_the_making(self):
        other = self.ledger.assign(target_day="2026-11-28")
        p, made, method = self.m.from_ledger(self.p, other, "demand")
        self.assertIsNone(made)
        self.assertIs(p["tomorrow"], self.tm)

    def test_both_series_use_it(self):
        with open(os.path.join(ROOT, "warehouse", "predict", "run.py"), encoding="utf-8") as f:
            s = f.read()
        self.assertIn('from_ledger(p, ledger, "demand")', s)
        self.assertIn('from_ledger(p, ledger, "price")', s)
        self.assertEqual(s.count('s["tomorrow_from"] = '), 2)

    def test_the_peak_reads_the_ledgers_column(self):
        # the peak chooses its own method (session 10601); tomorrow drawn from the ledger holds only the ledger's
        # method, so the peak of tomorrow takes that column, never a column the frame lacks
        with open(os.path.join(ROOT, "warehouse", "predict", "run.py"), encoding="utf-8") as f:
            s = f.read()
        if "peak_choice" in s:
            self.assertIn('c = p["choice"] if made_first is not None else p.get("peak_choice", p["choice"])', s)


if __name__ == "__main__":
    unittest.main()
