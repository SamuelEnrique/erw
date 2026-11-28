"""Session 11405 (chain 770, part C): decision 6 of the weekend page of 28 November 2026 readied, not landed without
Samuel's word. The forecast's two-to-seven-day step (warehouse/predict/ahead.py, site/data/predict/ahead.json), which
held the data machine's lock 4 h 34 min on the night of 27 November (22:28 to 03:02 UTC, docs/state/progress_c701.md),
runs once a week, on Sundays (UTC), beside the longer backtests and ahead.py --more, instead of every night. The day-ahead
forecast (run.py) and the other nightly steps are unchanged. The method note says so, and says what the page shows
through the week (the days ahead thin out as they pass: the page shows a day only after tomorrow).
"""
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


SUNDAY = 'if [ "$(date -u +%u)" = "7" ]; then soft_step '


class TheRun(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s = src("warehouse", "run_data_machine.sh")
        cls.steps = [ln.strip() for ln in cls.s.splitlines() if "soft_step dm_predict" in ln and not ln.lstrip().startswith("#")]

    def test_ahead_runs_only_on_sundays(self):
        line = [ln for ln in self.steps if "soft_step dm_predict_ahead " in ln]
        self.assertEqual(line, [SUNDAY + 'dm_predict_ahead "$PYTHON" warehouse/predict/ahead.py; fi'])

    def test_every_long_step_is_weekly(self):
        for name in ("dm_predict_ahead ", "dm_predict_long_backtest ", "dm_predict_long_price ", "dm_predict_ahead_more "):
            line = [ln for ln in self.steps if f"soft_step {name}" in ln]
            self.assertEqual(len(line), 1, name)
            self.assertTrue(line[0].startswith(SUNDAY), name)

    def test_the_nightly_forecast_steps_are_unchanged(self):
        for name in ("dm_predict ", "dm_predict_price_hubs ", "dm_predict_wind_solar ", "dm_predict_tables ", "dm_predict_rt_price "):
            line = [ln for ln in self.steps if ln.startswith(f"soft_step {name}")]
            self.assertEqual(len(line), 1, name)

    def test_the_order_is_kept(self):
        s = self.s
        self.assertLess(s.index("soft_step dm_predict_wind_solar "), s.index("soft_step dm_predict_ahead "))
        self.assertLess(s.index("soft_step dm_predict_ahead "), s.index("soft_step dm_predict_long_backtest "))


class TheNote(unittest.TestCase):
    def test_the_method_note_says_weekly_and_what_the_page_shows(self):
        n = src("docs", "methods", "predict.md")
        sec = n[n.index("## 12. Further ahead"):n.index("## 13.")]
        self.assertIn("once a week, on Sundays (UTC)", sec)
        self.assertIn("thins out through the week", sec)


if __name__ == "__main__":
    unittest.main()
