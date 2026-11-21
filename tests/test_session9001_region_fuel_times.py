"""Session 9001 (data request 570): eia930_region_fuel_hourly on the data machine held 7,511,587 times written as
pandas writes them (2018-07-11 07:00:00+00:00), from a restore, beside the merge's new rows in the standard form; the
merge compared keys as text, so 1,552,608 keys repeated, the validator blocked the table, and region_files.py (and the
region page files after it) stopped from 19 November. The held rows' times are put in the standard form before the
merge, so a restored table heals on its next run.
"""
import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))


class HeldTimesInTheStandardForm(unittest.TestCase):
    def test_pandas_written_times_become_utc_z(self):
        import eia930_region_fuel_hourly as rf
        old = pd.DataFrame({"entity": ["eia930:CAL"] * 3, "variable": ["net_generation_coal_mw"] * 3,
                            "ts_utc": ["2026-01-02 12:00:00+00:00", "2026-01-02T13:00:00Z", "2018-07-01 04:00:00+00:00"]})
        got = rf.held_utc(old)["ts_utc"].tolist()
        self.assertEqual(got, ["2026-01-02T12:00:00Z", "2026-01-02T13:00:00Z", "2018-07-01T04:00:00Z"])

    def test_a_merge_after_it_keeps_one_row_a_key(self):
        import eia930_region_fuel_hourly as rf
        old = pd.DataFrame({"entity": ["eia930:CAL"], "variable": ["net_generation_coal_mw"], "ts_utc": ["2026-01-02 12:00:00+00:00"]})
        new_key = {"eia930:CAL|net_generation_coal_mw|2026-01-02T12:00:00Z"}
        old = rf.held_utc(old)
        key = old["entity"] + "|" + old["variable"] + "|" + old["ts_utc"]
        self.assertEqual(int((~key.isin(new_key)).sum()), 0)

    def test_the_merge_calls_it(self):
        with open(os.path.join(ROOT, "warehouse", "connectors", "eia930_region_fuel_hourly.py"), encoding="utf-8") as f:
            s = f.read()
        self.assertLess(s.index("old = held_utc(old)"), s.index('key = old["entity"] + "|" + old["variable"] + "|" + old["ts_utc"]'))


if __name__ == "__main__":
    unittest.main()
