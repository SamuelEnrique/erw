"""Session 10000 (chain 701, predict data request 19): SPP's mid-term load forecast beside its actual load
(warehouse/connectors/spp_mtlf.py). Files of SPP's two layouts, made up in their shape; no request is made."""
import importlib.util
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
spec = importlib.util.spec_from_file_location("spp_mtlf_t", os.path.join(ROOT, "warehouse", "connectors", "spp_mtlf.py"))
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)

NEW = (b"Interval,GMTIntervalEnd,MTLF,Averaged Actual,BAA\n"
       b"11/27/2026 09:00:00,11/27/2026 15:00:00,32737,,SPP\n"
       b"11/27/2026 09:00:00,11/27/2026 15:00:00,2952,,SWPW\n"
       b"11/25/2026 09:00:00,11/25/2026 15:00:00,37694,37563,SPP\n")
OLD = (b"Interval,MTLF,Averaged Actual\n"
       b"11/03/2013 03:00:00,19500,19828\n"
       b"11/03/2013 02:00:00,20278,19875\n"
       b"11/03/2013 01:00:00,19675,20075\n"
       b"11/03/2013 01:00:00,20081,20451\n"
       b"11/03/2013 00:00:00,20862,21214\n")


class TheFiles(unittest.TestCase):
    def test_the_later_layout(self):
        t = M.rows_of(NEW, "OP-MTLF-202611260900.csv", "u", "2026-11-28T00:00:00Z")
        f = t[(t.variable == "load_forecast_mtlf_mw") & (t.ts_utc == "2026-11-27T14:00:00Z")]   # the hour's start, from GMT's hour ending
        self.assertEqual(sorted(f.entity), ["spp:SPP", "spp:SWPW"])
        self.assertEqual(len(t[t.variable == "load_forecast_mtlf_mw"]), 3)   # a past hour's forecast is kept beside its actual
        self.assertEqual(set(t.vintage), {"2026-11-26T15:00:00Z"})         # published 09:00 CST
        self.assertEqual(set(f.x_horizon_hours), {"23"})
        a = t[t.variable == "load_actual_mw"]
        self.assertEqual((a.entity.tolist(), a.value.tolist()), (["spp:SPP"], [37563.0]))   # an empty cell is no row
        self.assertEqual(a.x_horizon_hours.tolist(), ["-25"])

    def test_the_early_layout_and_the_autumn_change(self):
        t = M.rows_of(OLD, "OP-MTLF-201311030900.csv", "u", "2026-11-28T00:00:00Z")
        f = t[t.variable == "load_forecast_mtlf_mw"].sort_values("ts_utc")
        self.assertEqual(set(f.entity), {"spp:SPP"})
        # 03:00 CST ends at 09:00 UTC; each row before it one hour earlier, the repeated 01:00 label included
        self.assertEqual(f.ts_utc.tolist(), ["2013-11-03T04:00:00Z", "2013-11-03T05:00:00Z", "2013-11-03T06:00:00Z",
                                             "2013-11-03T07:00:00Z", "2013-11-03T08:00:00Z"])
        self.assertFalse(t.duplicated(M.KEY).any())

    def test_times_without_seconds(self):
        body = b"Interval,MTLF,Averaged Actual\n10/5/2017 14:00,30000,\n10/5/2017 13:00,29900,29950\n"
        t = M.rows_of(body, "OP-MTLF-201710050900.csv", "u", "r")
        self.assertEqual(sorted(t[t.variable == "load_forecast_mtlf_mw"].ts_utc), ["2017-10-05T17:00:00Z", "2017-10-05T18:00:00Z"])

    def test_a_file_name_and_the_day_path(self):
        import datetime as dt
        self.assertEqual(str(M.published_utc("OP-MTLF-202607010900.csv")), "2026-07-01 14:00:00+00:00")   # CDT
        self.assertEqual(M.daily_path(dt.date(2026, 11, 26)), "/2026/11/26/OP-MTLF-202611260900.csv")


class TheDailyStep(unittest.TestCase):
    def test_in_the_data_machines_run(self):
        s = open(os.path.join(ROOT, "warehouse", "run_data_machine.sh"), encoding="utf-8").read()
        self.assertIn('soft_step dm_spp_mtlf "$PYTHON" warehouse/connectors/spp_mtlf.py', s)
        self.assertLess(s.index("soft_step dm_spp_mtlf "), s.index("table_stores dm_spp_mtlf_stores spp_mtlf_hourly"))


if __name__ == "__main__":
    unittest.main()
