"""Session 913: the Annual Energy Outlook's Table 54 by Electricity Market Module region.

Energy Research Warehouse (ERW). Tests warehouse/connectors/eia_aeo_regions.py on records built here in the API's form
(figures made up for the test, not EIA's): GW as MW, billion kWh as MWh, real and nominal cents and dollars with their
dollar year, quads as TBtu, short tons not taken, a unit not in the map stopping the run, geo US only for the U.S. row;
the sector rule and the holds. No network.

    python -m unittest tests.test_session913 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia_aeo_regions as A  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402


def rec(unit="GW", value="1.5", region="5-1", sid="cap_NA_elep_NA_NA_NA_texr_gw"):
    return {"period": "2030", "history": "PROJECTION", "scenario": "cb2026", "scenarioDescription": "Counterfactual Baseline case",
            "tableId": "62", "seriesId": sid, "seriesName": "Electricity : Capacity", "regionId": region,
            "regionName": "Texas Reliability Entity", "value": value, "unit": unit}


class Table54(unittest.TestCase):
    def test_units(self):
        out, skipped = A.rows([rec(), rec("BkWh", "2", sid="g"), rec("2025 cents/kWh", "12", sid="p"), rec("nom $/MMBtu", "3", sid="f"),
                               rec("2025 $/MMBtu", "2.5", sid="f2"), rec("quads", "0.5", sid="q"), rec("MMst", "1", sid="e"),
                               rec(region="5-0", sid="u")], "u", "r")
        got = {o["entity"].split(":")[2]: (o["value"], o["unit"], o["x_dollar_year"], o["geo"]) for o in out}
        self.assertEqual(got["cap_NA_elep_NA_NA_NA_texr_gw"], (1500.0, "MW", "", ""))
        self.assertEqual(got["g"], (2e6, "MWh", "", ""))
        self.assertEqual(got["p"], (0.12, "USD/kWh", "2025", ""))
        self.assertEqual(got["f"][1:3], ("USD/MMBtu", "nominal"))
        self.assertEqual(got["f2"][1:3], ("USD/MMBtu", "2025"))
        self.assertEqual(got["q"][:2], (500.0, "TBtu"))
        self.assertEqual(got["u"][3], "US")
        self.assertEqual(skipped, {"MMst": 1})
        self.assertEqual(out[0]["entity"], "eia_aeo_2026_emm:5-1:cap_NA_elep_NA_NA_NA_texr_gw")

    def test_unknown_unit_stops(self):
        with self.assertRaises(RuntimeError):
            A.rows([rec("furlongs")], "u", "r")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        name = "eia_aeo_emm_regions"
        self.assertEqual(B.sector_of(name), "power")
        self.assertIn(name, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {name}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
