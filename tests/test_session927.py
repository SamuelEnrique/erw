"""Session 927: fuel stocks at power plants (EIA's electric power operational data).

Energy Research Warehouse (ERW). Tests warehouse/connectors/eia_power_fuel_stocks.py on records built here in the API's
form (figures made up for the test, not EIA's): thousand short tons as short tons, thousand barrels as kbbl, geo for a
state, the U.S. and a census region, a record without a stocks figure having no row, a unit not in the map stopping the
run; the sector rule and the holds. No network.

    python -m unittest tests.test_session927 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia_power_fuel_stocks as F  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402


def rec(loc="IN", fuel="COL", value="1500", unit="thousand short tons"):
    return {"period": "2026-07", "location": loc, "stateDescription": loc, "sectorid": "98", "sectorDescription": "Electric Power",
            "fueltypeid": fuel, "fuelTypeDescription": fuel, "stocks": value, "stocks-units": unit}


class Stocks(unittest.TestCase):
    def test_units_and_geo(self):
        out = F.rows([rec(), rec("US", "PEL", "19700", "thousand barrels"), rec("ENC"), rec("TX", value=None)], "u", "r")
        got = {o["entity"]: (o["value"], o["unit"], o["geo"]) for o in out}
        self.assertEqual(got["eia_power_stocks:IN:98:COL"], (1.5e6, "short_ton", "US-IN"))
        self.assertEqual(got["eia_power_stocks:US:98:PEL"], (19700.0, "kbbl", "US"))
        self.assertEqual(got["eia_power_stocks:ENC:98:COL"][2], "")
        self.assertEqual(len(out), 3)
        self.assertEqual(out[0]["ts_utc"], "2026-07-01T00:00:00Z")

    def test_unknown_unit_stops(self):
        with self.assertRaises(RuntimeError):
            F.rows([rec(unit="tonnes")], "u", "r")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        name = "eia_power_fuel_stocks_monthly"
        self.assertEqual(B.sector_of(name), "power;coal;oil")
        self.assertIn(name, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {name}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
