"""Session 886: EIA's international electricity statistics for the U.S., Canada and Mexico.

Energy Research Warehouse (ERW). Tests warehouse/connectors/eia_international_electricity.py on records built here in
the API's form (figures made up for the test, not EIA's): billion kWh as MWh and million kW as MW, the countries as ISO
codes, EIA's marks having no row, the flag kept, an activity or unit not in the map stopping the run, a key given twice
stopping it, the sector rule and the holds. No network.

    python -m unittest tests.test_session886 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia_international_electricity as E  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402


def rec(country="CAN", product="2", activity="12", unit="BKWH", value="600.5", period="2024", flag=None):
    return {"period": period, "productId": product, "productName": "Electricity", "activityId": activity,
            "countryRegionId": country, "countryRegionName": "Canada", "unit": unit, "value": value,
            "dataFlagDescription": flag}


class International(unittest.TestCase):
    def test_units_and_codes(self):
        t = E.rows([rec(), rec(activity="7", unit="MK", value="161.9"), rec(country="MEX", product="37", value="20")], "u", "r")
        g = t.set_index(["entity", "variable"])
        self.assertEqual((g.loc[("eia_intl:CAN:2", "generation"), "value"], g.loc[("eia_intl:CAN:2", "generation"), "unit"]), (600.5e6, "MWh"))
        self.assertEqual((g.loc[("eia_intl:CAN:2", "capacity"), "value"], g.loc[("eia_intl:CAN:2", "capacity"), "unit"]), (161900.0, "MW"))
        self.assertEqual(g.loc[("eia_intl:MEX:37", "generation"), "geo"], "MX")
        self.assertEqual(t.ts_utc.iloc[0], "2024-01-01T00:00:00Z")

    def test_marks_have_no_row_and_flags_are_kept(self):
        t = E.rows([rec(value="NA"), rec(value="--", activity="4"), rec(activity="3", value="0", flag="rounds to zero")], "u", "r")
        self.assertEqual(t.variable.tolist(), ["imports"])
        self.assertEqual(t.x_data_flag.iloc[0], "rounds to zero")

    def test_not_in_the_map_stops(self):
        for bad in (rec(activity="99"), rec(unit="QBTU"), rec(country="BRA")):
            with self.assertRaises(RuntimeError):
                E.rows([bad], "u", "r")
        with self.assertRaises(RuntimeError):
            E.rows([rec(), rec(value="1")], "u", "r")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        name = "eia_international_electricity_annual"
        self.assertEqual(B.sector_of(name), "power")
        self.assertIn(name, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {name}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
