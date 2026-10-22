"""Sessions 612 and 613: EIA-930's demand by sub-region for a whole year, in twelve monthly windows of EIA's hour-ending
periods (2025: from 2025-01-01T01 to 2026-01-01T00, the year's hours from 00:00 UTC on 1 January to 23:00 on 31
December), as its own table; the yearly table is held from /data and Redivis v1 until uploaded.
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia930_subba as S  # noqa: E402
import release_v1 as R  # noqa: E402


class TheYear(unittest.TestCase):
    def test_twelve_windows_that_meet(self):
        w = S.year_windows(2025)
        self.assertEqual(len(w), 12)
        self.assertEqual(w[0], ("2025-01-01T01", "2025-02-01T00"))
        self.assertEqual(w[1][0], "2025-02-01T01")
        self.assertEqual(w[-1], ("2025-12-01T01", "2026-01-01T00"))

    def test_a_ceiling_of_its_own(self):
        self.assertEqual(S.YEAR_CEILING, 89)

    def test_held_until_uploaded(self):
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as h:
            y = h.read()
        self.assertIn("  - eia930_subba_demand_hourly_2025\n", y[y.index("catalogue_hold:"):])
        self.assertIn("upload.py eia930_subba_demand_hourly_2025", R.STORAGE_HELD["eia930_subba_demand_hourly_2025"])
        # sessions 620 and 621: 2024 the same way
        self.assertIn("  - eia930_subba_demand_hourly_2024\n", y[y.index("catalogue_hold:"):])
        self.assertIn("upload.py eia930_subba_demand_hourly_2024", R.STORAGE_HELD["eia930_subba_demand_hourly_2024"])
        # sessions 627 and 628: 2023 the same way
        self.assertIn("  - eia930_subba_demand_hourly_2023\n", y[y.index("catalogue_hold:"):])
        self.assertIn("upload.py eia930_subba_demand_hourly_2023", R.STORAGE_HELD["eia930_subba_demand_hourly_2023"])
        # sessions 633 and 634: 2022 the same way
        self.assertIn("  - eia930_subba_demand_hourly_2022\n", y[y.index("catalogue_hold:"):])
        self.assertIn("upload.py eia930_subba_demand_hourly_2022", R.STORAGE_HELD["eia930_subba_demand_hourly_2022"])

    def test_no_em_dash(self):
        with open(os.path.join(ROOT, "tests", "test_session612.py"), encoding="utf-8") as h:
            self.assertNotIn(chr(0x2014), h.read())


if __name__ == "__main__":
    unittest.main()
