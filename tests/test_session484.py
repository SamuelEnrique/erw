"""Session 484: FERC Form 714 hourly demand by planning area, from PUDL's core table. ts_utc is the hour's start, one
hour before PUDL's datetime_utc (the hour's end; checked against ERCOT's own load for 2025); a year's table holds the
hours that start in it; values are as filed (negatives kept); a repeated hour stops the run; nothing is filled."""

import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import ferc714_demand as fd  # noqa: E402

RESP = pd.DataFrame({"respondent_id_ferc714": [58, 119], "respondent_name_ferc714": ["ERCOT", "PJM Interconnection, LLC"]})


def demand(rows):
    d = pd.DataFrame(rows, columns=["respondent_id_ferc714", "datetime_utc", "demand_mwh"])
    d["datetime_utc"] = pd.to_datetime(d["datetime_utc"])
    d["start"] = d["datetime_utc"] - pd.Timedelta(hours=1)
    return d


class Rows(unittest.TestCase):
    def test_the_hour_starts_an_hour_before_pudls_stamp(self):
        s = fd.rows(demand([(58, "2025-01-01 01:00", 40000.0), (58, "2025-01-01 02:00", 39000.0)]), RESP, 2025, "u", "r", "v")
        self.assertEqual(list(s["ts_utc"]), ["2025-01-01T00:00:00Z", "2025-01-01T01:00:00Z"])
        self.assertEqual(list(s["entity"]), ["ferc714:58", "ferc714:58"])
        self.assertEqual(set(s["node"]), {"ERCOT"})
        self.assertEqual(list(s.columns), fd.ip.SERIES_COLS)

    def test_a_year_holds_the_hours_that_start_in_it(self):
        d = demand([(58, "2025-01-01 00:00", 1.0), (58, "2025-01-01 01:00", 2.0), (58, "2026-01-01 00:00", 3.0)])
        self.assertEqual(list(fd.rows(d, RESP, 2025, "u", "r", "v")["value"]), [2.0, 3.0])  # 2024-12-31 23:00 is 2024's
        self.assertEqual(list(fd.rows(d, RESP, 2024, "u", "r", "v")["value"]), [1.0])

    def test_values_are_as_filed_negatives_included(self):
        s = fd.rows(demand([(119, "2025-03-01 05:00", -614.0)]), RESP, 2025, "u", "r", "v")
        self.assertEqual(list(s["value"]), [-614.0])
        self.assertEqual((s["unit"].iloc[0], s["freq"].iloc[0], s["variable"].iloc[0]), ("MW", "PT1H", "demand"))

    def test_a_repeated_hour_stops_the_run(self):
        with self.assertRaisesRegex(RuntimeError, "given twice"):
            fd.rows(demand([(58, "2025-01-01 01:00", 1.0), (58, "2025-01-01 01:00", 2.0)]), RESP, 2025, "u", "r", "v")

    def test_only_the_core_table_is_read(self):
        self.assertIn("core_ferc714__hourly_planning_area_demand", fd.DEMAND)
        self.assertNotIn("out_ferc714", fd.DEMAND)  # PUDL's out_ table imputes missing hours

    def test_the_name_fits_the_standard(self):
        self.assertEqual(fd.table_name(2025), "ferc714_area_demand_2025")
        self.assertLessEqual(len(fd.table_name(2025)), 40)


if __name__ == "__main__":
    unittest.main()
