"""Session 889: the Federal Reserve's G.17, utilities' output and capacity utilization; Decision 53, the unit index.

Energy Research Warehouse (ERW). Tests warehouse/connectors/frb_utility_output.py on a text built here in the G.17
ipdisk form (figures made up for the test, not the Board's): the utilities' series and the two totals kept, every other
series left out, a short last year read to its last month, an index in unit index and utilization in pct, a line not in
the form read stopping the run, the unit in the validator, the sector rule and the holds. No network.

    python -m unittest tests.test_session889 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
sys.path.append(os.path.join(ROOT, "warehouse", "validate"))
import frb_utility_output as F  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402
import erw_validate as V  # noqa: E402

TEXT = """"B50001: Total index"
"B50001"        2025       100.0     101.0     102.0     103.0     104.0     105.0     106.0     107.0     108.0     109.0     110.0     111.0
"G335: Electrical equipment, appliance, and component  NAICS=335"
"G335"          2025       90.0      90.0      90.0      90.0      90.0      90.0      90.0      90.0      90.0      90.0      90.0      90.0
"N22112R: Residential electricity sales  NAICS=22112pt."
"N22112R"       2025       98.5      99.5      97.0      96.0      95.0      94.0      93.0      92.0      91.0      90.0      89.0      88.0
"N22112R"       2026       110.5     111.1
"N22112R"       1971
"""


class G17(unittest.TestCase):
    def test_series_kept_and_months(self):
        t = F.parse(TEXT, "production", "index", "u", "r")
        self.assertEqual(sorted(t.entity.unique()), ["frb_g17:B50001", "frb_g17:N22112R"])
        r = t[t.entity == "frb_g17:N22112R"].set_index("ts_utc")
        self.assertEqual(len(r), 14)
        self.assertEqual(r.loc["2026-02-01T00:00:00Z", "value"], 111.1)
        self.assertEqual(r.loc["2025-01-01T00:00:00Z", "node"], "Residential electricity sales NAICS=22112pt.")
        self.assertEqual(set(t.unit), {"index"})

    def test_a_line_not_in_the_form_stops(self):
        with self.assertRaises(RuntimeError):
            F.parse(TEXT + "garbage line\n", "production", "index", "u", "r")

    def test_the_unit_and_registration(self):
        self.assertIn("index", V.UNITS)
        name = "frb_utility_output_monthly"
        self.assertEqual(B.sector_of(name), "power")
        self.assertIn(name, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {name}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
