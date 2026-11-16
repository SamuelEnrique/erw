"""Session 7019 (chain 301, done-line request 36): the ERCOT peak premium's annual table carries, for every year, the
same metrics over 1 January to the local day and time of the last input interval (ytd_<variable>), so the partial year
has a like figure beside each earlier year. No request, no model call."""
import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
import ercot_peak_premium as pp  # noqa: E402


class TheCut(unittest.TestCase):
    def test_the_same_local_moment_each_year(self):
        last = pd.Timestamp("2026-11-15T05:45:00Z").tz_convert(pp.TZ)          # 2026-11-14 23:45 Central
        self.assertEqual(str(pp.ytd_cut(last, 2025)), "2025-11-14 23:45:00-06:00")
        self.assertEqual(str(pp.ytd_cut(last, 2019)), "2019-11-14 23:45:00-06:00")

    def test_29_february_in_a_year_without_it(self):
        last = pd.Timestamp("2028-02-29 10:00").tz_localize(pp.TZ)
        self.assertEqual(str(pp.ytd_cut(last, 2027)), "2027-02-28 10:00:00-06:00")
        self.assertEqual(str(pp.ytd_cut(last, 2024)), "2024-02-29 10:00:00-06:00")

    def test_the_builder_writes_the_variables_on_the_annual_table_only(self):
        with open(os.path.join(ROOT, "warehouse", "derived", "ercot_peak_premium.py"), encoding="utf-8") as f:
            s = f.read()
        self.assertIn('annual.append((hub, f"ytd_{var}", f"{y}-01-01T00:00:00Z", v, unit))', s)
        self.assertIn('if name == "ercot_peak_premium_annual" else []', s)


if __name__ == "__main__":
    unittest.main()
