"""Session 860: EIA's U.S. exports of crude oil and petroleum products by destination, as eia_petroleum_exports_by_destination.

Energy Research Warehouse (ERW). Tests warehouse/connectors/eia_petroleum_exports.py on records built here in the form of
EIA's route petroleum/move/expc (figures made up for the test, not EIA's): the two units, an empty value, an unknown unit,
a key given twice, the sector rule and the holds. No network.

    python -m unittest tests.test_session860 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia_petroleum_exports as E  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402


def rec(units, value="10", area="NUS-NCA", product="EPC0", period="2026-07"):
    return {"period": period, "duoarea": area, "area-name": "CAN", "product": product, "product-name": "Crude Oil",
            "process": "EEX", "series": "X", "value": value, "units": units}


class Reshape(unittest.TestCase):
    def test_units_and_rows(self):
        t = E.rows([rec("MBBL", "310"), rec("MBBL/D", "10"), rec("MBBL", None, period="2026-06")], "u", "r")
        g = t.set_index("variable")
        self.assertEqual((g.loc["exports", "value"], g.loc["exports", "unit"]), (310.0, "kbbl"))
        self.assertEqual((g.loc["exports_per_day", "value"], g.loc["exports_per_day", "unit"]), (10.0, "kbbl/d"))
        self.assertEqual(t.entity.unique().tolist(), ["eia_petroleum_exports:NUS-NCA:EPC0"])
        self.assertEqual(t.ts_utc.unique().tolist(), ["2026-07-01T00:00:00Z"])

    def test_stops(self):
        with self.assertRaises(RuntimeError):
            E.rows([rec("TBBL")], "u", "r")
        with self.assertRaises(RuntimeError):
            E.rows([rec("MBBL"), rec("MBBL")], "u", "r")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of("eia_petroleum_exports_by_destination"), "oil;products")
        self.assertIn("eia_petroleum_exports_by_destination", R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn("  - eia_petroleum_exports_by_destination", f.read())


if __name__ == "__main__":
    unittest.main()
