"""Session 10000 (chain 701, data request 8 of docs/state/data_requests_predict.md, chain 730): the data machine runs
warehouse/predict/wind_solar.py right after the day's forecast, and warehouse/predict/rt_price.py as its last step before
the commit (as late as the run goes; the request asks for 22:00 UTC or later). No table is read."""
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class TheTwoSteps(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(ROOT, "warehouse", "run_data_machine.sh"), encoding="utf-8") as f:
            self.s = f.read()

    def test_wind_and_solar_right_after_the_forecast(self):
        s = self.s
        self.assertLess(s.index("soft_step dm_predict "), s.index("soft_step dm_predict_wind_solar "))
        self.assertLess(s.index("soft_step dm_predict_wind_solar "), s.index("soft_step dm_predict_ahead "))
        self.assertIn('soft_step dm_predict_wind_solar "$PYTHON" warehouse/predict/wind_solar.py', s)

    def test_the_real_time_price_last_before_the_commit(self):
        s = self.s
        rt = s.index("soft_step dm_predict_rt_price ")
        self.assertLess(rt, s.index("# ---- 4. the commit"))
        self.assertNotIn("soft_step ", s[rt + 10:s.index("# ---- 4. the commit")])   # nothing runs after it
        self.assertIn('soft_step dm_predict_rt_price "$PYTHON" warehouse/predict/rt_price.py', s)

    def test_their_files_are_committed(self):
        self.assertIn("PAGE_PATHS+=(site/data/predict)", self.s)
        for f in ("wind_solar.py", "rt_price.py"):
            self.assertTrue(os.path.exists(os.path.join(ROOT, "warehouse", "predict", f)), f)


if __name__ == "__main__":
    unittest.main()
