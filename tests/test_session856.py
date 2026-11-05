"""Session 856: EIA-930's demand by sub-region for 2019, a table of its own (sessions 855 and 856, chain 046).

Energy Research Warehouse (ERW). The 2019 table is held from the live set and from Redivis until a person uploads it
(the two holds of chain 022), takes the sector of every yearly sub-region table, and is named by the sub-region note.
No network.

    python -m unittest tests.test_session856 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

T = "eia930_subba_demand_hourly_2019"


class The2019Table(unittest.TestCase):
    def test_holds_sector_note(self):
        self.assertIn(T, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {T}\n", f.read().replace("\r\n", "\n"))
        self.assertEqual(B.sector_of(T), "power")
        with open(os.path.join(ROOT, "docs", "methods", "eia930_subba_demand.md"), encoding="utf-8") as f:
            line = next(ln for ln in f if ln.startswith("Tables: "))
        self.assertIn(f"`{T}`", line)


if __name__ == "__main__":
    unittest.main()
