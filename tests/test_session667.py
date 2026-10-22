"""Session 667: EIA-861's utility service territories, a utility's counties by state (chain 043).

Energy Research Warehouse (ERW). Tests warehouse/connectors/eia861_territories.py against a three-row sheet built here
(test fixtures, not EIA's values), and the table's sector rule and holds. No network.

    python -m unittest tests.test_session667 -v
"""

import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia861_territories as T  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

HEAD = ["Data Year", "Utility Number", "Utility Name", "Short Form", "State", "County"]


def sheet(rows):
    return pd.DataFrame([HEAD] + rows)


class Territories(unittest.TestCase):
    def test_a_row_a_utility_county_and_state(self):
        t = T.territories(sheet([[2025, 1, "Utility A", "Y", "SC", "Abbeville"], [2025, 1, "Utility A", None, "GA", "Elbert"],
                                 [2025, 2, "Co-op #2", None, "SC", "Abbeville"]]), 2025, "Counties_States", "u", "r")
        self.assertEqual(list(t.columns), T.ENTITY_COLS + T.X_COLS)
        self.assertEqual(t["entity_id"].tolist(), ["eia861:1:SC:Abbeville", "eia861:1:GA:Elbert", "eia861:2:SC:Abbeville"])
        self.assertEqual(set(t["entity_type"]), {"utility"})
        self.assertEqual(t["geo"].tolist(), ["US-SC", "US-GA", "US-SC"])
        self.assertEqual(t["x_short_form"].tolist(), ["Y", "", ""])
        self.assertEqual(t["name"].iloc[2], "Co-op #2")

    def test_another_year_or_a_missing_county_stops_the_run(self):
        with self.assertRaises(RuntimeError):
            T.territories(sheet([[2024, 1, "A", None, "SC", "Abbeville"]]), 2025, "Counties_States", "u", "r")
        with self.assertRaises(RuntimeError):
            T.territories(sheet([[2025, 1, "A", None, "SC", None]]), 2025, "Counties_States", "u", "r")

    def test_headings_found_by_name(self):
        f = pd.DataFrame([["County", "State", "Utility Name", "Utility Number", "Data Year"], ["Elbert", "GA", "A", 7, 2025]])
        t = T.territories(f, 2025, "Counties_States", "u", "r")
        self.assertEqual(t["entity_id"].tolist(), ["eia861:7:GA:Elbert"])

    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of("utility_service_territories"), "power")
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as h:
            y = h.read()
        self.assertIn("  - utility_service_territories\n", y[y.index("catalogue_hold:"):])
        self.assertIn("upload.py utility_service_territories", R.STORAGE_HELD["utility_service_territories"])

    def test_no_em_dash(self):
        for f in ("tests/test_session667.py", "warehouse/connectors/eia861_territories.py"):
            with open(os.path.join(ROOT, f), encoding="utf-8") as h:
                self.assertNotIn(chr(0x2014), h.read())


if __name__ == "__main__":
    unittest.main()
