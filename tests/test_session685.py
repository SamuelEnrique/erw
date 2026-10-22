"""Session 685: EIA's coal production by state, rank and mine type, a year (chain 044), and the unit short_ton.

Energy Research Warehouse (ERW). Tests warehouse/connectors/eia_coal_production.py's reshaping on records built here
(test fixtures, not EIA's values), the unit, the sector rule and the holds. No network.

    python -m unittest tests.test_session685 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
sys.path.append(os.path.join(ROOT, "warehouse", "validate"))  # last: its build_coverage.py is a shim
import eia_coal_production as C  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402
import erw_validate as V  # noqa: E402


def rec(**k):
    r = {"period": "2023", "stateRegionId": "WY", "stateRegionDescription": "Wyoming", "coalRankId": "SUB",
         "coalRankDescription": "Subbituminous", "mineTypeId": "SUR", "mineTypeDescription": "Surface",
         "production": "100", "production-units": "short tons", "number-of-mines": "2", "number-of-mines-units": "number of mines",
         "average-employees": "30", "average-employees-units": "number of employees"}
    r.update(k)
    return r


class Production(unittest.TestCase):
    def test_three_variables_a_record(self):
        t = C.rows([rec()], "u", "r")
        self.assertEqual(sorted(t["variable"]), ["employees", "mines", "production"])
        p = t[t.variable == "production"].iloc[0]
        self.assertEqual((p.entity, p.unit, p.geo, p.ts_utc), ("eia_coal_production:WY:SUB:SUR", "short_ton", "US-WY", "2023-01-01T00:00:00Z"))
        self.assertEqual(set(t["unit"]) - {"short_ton", "count"}, set())

    def test_a_withheld_figure_has_no_row_and_an_unknown_unit_stops(self):
        t = C.rows([rec(production=None)], "u", "r")
        self.assertNotIn("production", set(t["variable"]))
        with self.assertRaises(RuntimeError):
            C.rows([rec(**{"production-units": "thousand short tons"})], "u", "r")
        with self.assertRaises(RuntimeError):
            C.rows([rec(), rec()], "u", "r")

    def test_a_region_is_us(self):
        t = C.rows([rec(stateRegionId="PRB")], "u", "r")
        self.assertEqual(set(t["geo"]), {"US"})

    def test_unit_sector_and_holds(self):
        self.assertIn("short_ton", V.UNITS)
        with open(os.path.join(ROOT, "docs", "datastandard.md"), encoding="utf-8") as h:
            self.assertIn("50. **Session 685: short_ton.**", h.read())
        self.assertEqual(B.sector_of("eia_coal_production_annual"), "coal")
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as h:
            y = h.read()
        self.assertIn("  - eia_coal_production_annual\n", y[y.index("catalogue_hold:"):y.index("review_hold:")])
        self.assertIn("upload.py eia_coal_production_annual", R.STORAGE_HELD["eia_coal_production_annual"])

    def test_no_em_dash(self):
        for f in ("tests/test_session685.py", "warehouse/connectors/eia_coal_production.py"):
            with open(os.path.join(ROOT, f), encoding="utf-8") as h:
                self.assertNotIn(chr(0x2014), h.read())


if __name__ == "__main__":
    unittest.main()
