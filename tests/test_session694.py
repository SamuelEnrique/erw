"""Session 694: EIA's coal production and employees by mine, a year (chain 045, a public source the ERW did not hold).

Energy Research Warehouse (ERW). Tests warehouse/connectors/eia_coal_mine_production.py's reshaping on records built here
in the form of EIA's route coal/mine-production (test fixtures, not EIA's values), the unit, the region mapping, the sector
rule and the holds. No network.

    python -m unittest tests.test_session694 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia_coal_mine_production as C  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402


def rec(**k):
    r = {"period": "2024", "mineMSHAId": "4800677", "mineName": "A Test Mine", "stateId": "WY", "mineCountyName": "Campbell",
         "supplyRegionDescription": "Powder River Basin", "coalRankId": "SUB", "coalRankDescription": "Subbituminous",
         "mineTypeId": "SUR", "mineTypeDescription": "Surface", "mineStatusDescription": "Active", "production": "1000",
         "average-employees": "10", "latitude": "43.5", "longitude": "-105.2", "operating-company": "A Test Company Llc",
         "refuse-flag": None, "production-units": "short tons", "average-employees-units": "number of employees"}
    r.update(k)
    return r


class Reshape(unittest.TestCase):
    def test_a_record_gives_two_rows(self):
        t = C.rows([rec()], "u", "2026-10-23T00:00:00Z")
        self.assertEqual(len(t), 2)
        p = t[t.variable == "production"].iloc[0]
        self.assertEqual((p.entity, p.unit, p.value, p.geo, p.ts_utc), ("eia_coal_mine:4800677:SUB:SUR", "short_ton", 1000.0, "US-WY", "2024-01-01T00:00:00Z"))
        self.assertEqual((p.x_county, p.x_operator, p.x_latitude), ("Campbell", "A Test Company Llc", "43.5"))
        self.assertEqual(t[t.variable == "employees"].iloc[0].unit, "count")

    def test_an_empty_figure_has_no_row_and_zero_is_kept(self):
        t = C.rows([rec(**{"production": "0", "average-employees": None})], "u", "r")
        self.assertEqual(t.variable.tolist(), ["production"])
        self.assertEqual(t.value.tolist(), [0.0])

    def test_eias_regions_inside_a_state(self):
        for code, state in (("PAA", "PA"), ("KYE", "KY"), ("WVS", "WV")):
            t = C.rows([rec(stateId=code)], "u", "r")
            self.assertEqual((t.geo.iloc[0], t.x_state.iloc[0]), (f"US-{state}", code))

    def test_a_plant_as_surface_and_underground_is_two_series(self):
        t = C.rows([rec(coalRankId="PRP", mineTypeId="SUR"), rec(coalRankId="PRP", mineTypeId="UND")], "u", "r")
        self.assertEqual(t.entity.nunique(), 2)

    def test_a_key_twice_or_an_unknown_unit_stops(self):
        with self.assertRaises(RuntimeError):
            C.rows([rec(), rec()], "u", "r")
        with self.assertRaises(RuntimeError):
            C.rows([rec(**{"production-units": "thousand short tons"})], "u", "r")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of("eia_coal_mine_production_annual"), "coal")
        self.assertIn("eia_coal_mine_production_annual", R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn("  - eia_coal_mine_production_annual", f.read())


if __name__ == "__main__":
    unittest.main()
