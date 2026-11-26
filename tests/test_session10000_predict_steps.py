"""Session 10000 (chain 701, data requests 1 and 6 of docs/state/data_requests_predict.md): the data machine's daily run
makes the ERW forecast after the forecast error tables, then the forecast further ahead, and commits the page files."""
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class TheForecastSteps(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(ROOT, "warehouse", "run_data_machine.sh"), encoding="utf-8") as f:
            self.s = f.read()

    def test_the_order(self):
        a = self.s.index("soft_step dm_forecast_error ")
        b = self.s.index('soft_step dm_predict "$PYTHON" warehouse/predict/run.py')
        c = self.s.index('soft_step dm_predict_ahead "$PYTHON" warehouse/predict/ahead.py')
        self.assertLess(a, b)
        self.assertLess(b, c)

    def test_the_page_files_are_committed(self):
        self.assertIn("PAGE_PATHS+=(site/data/predict)", self.s)

    def test_the_scripts_exist(self):
        for name in ("run.py", "ahead.py"):
            self.assertTrue(os.path.exists(os.path.join(ROOT, "warehouse", "predict", name)), name)


if __name__ == "__main__":
    unittest.main()
