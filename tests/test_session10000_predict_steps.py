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

    def test_the_hub_prices_right_after_the_forecast(self):
        # predict data request 13: price_hubs.py right after run.py
        s = self.s
        self.assertLess(s.index("soft_step dm_predict "), s.index("soft_step dm_predict_price_hubs "))
        self.assertLess(s.index("soft_step dm_predict_price_hubs "), s.index("soft_step dm_predict_tables "))
        self.assertIn('soft_step dm_predict_price_hubs "$PYTHON" warehouse/predict/price_hubs.py', s)

    def test_the_longer_backtest_on_sundays(self):
        # the second predict data request 15: long_backtest.py once a week, after the forecasts two to seven days ahead
        s = self.s
        self.assertIn('if [ "$(date -u +%u)" = "7" ]; then soft_step dm_predict_long_backtest "$PYTHON" '
                      'warehouse/predict/long_backtest.py; fi', s)
        self.assertLess(s.index("soft_step dm_predict_ahead "), s.index("soft_step dm_predict_long_backtest "))
        self.assertTrue(os.path.exists(os.path.join(ROOT, "warehouse", "predict", "long_backtest.py")))
        # predict data request 16: long_price.py beside it
        self.assertIn('if [ "$(date -u +%u)" = "7" ]; then soft_step dm_predict_long_price "$PYTHON" '
                      'warehouse/predict/long_price.py; fi', s)
        self.assertLess(s.index("soft_step dm_predict_long_backtest "), s.index("soft_step dm_predict_long_price "))
        self.assertTrue(os.path.exists(os.path.join(ROOT, "warehouse", "predict", "long_price.py")))
        # predict data request 18: ahead.py --more beside them
        self.assertIn('if [ "$(date -u +%u)" = "7" ]; then soft_step dm_predict_ahead_more "$PYTHON" '
                      'warehouse/predict/ahead.py --more; fi', s)
        self.assertLess(s.index("soft_step dm_predict_long_price "), s.index("soft_step dm_predict_ahead_more "))

    def test_their_files_are_committed(self):
        self.assertIn("PAGE_PATHS+=(site/data/predict)", self.s)
        for f in ("wind_solar.py", "rt_price.py"):
            self.assertTrue(os.path.exists(os.path.join(ROOT, "warehouse", "predict", f)), f)


if __name__ == "__main__":
    unittest.main()
