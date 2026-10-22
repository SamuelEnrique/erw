"""Sessions 570 to 573: meters by state, power plants' CO2 by state and fuel, coal prices by rank, coal exports' and
imports' prices. Held on real records of EIA's API (2024 for 570 and 571; 2001 and 2000 for 572 and 573): each entity's
codes, the units the vocabulary holds (count; tCO2 from thousand metric tons; kgCO2/MWh from pounds per MWh;
USD/short_ton), a withheld price ("w") with no row, an unknown unit stops; the four tables are held from /data and
Redivis v1 until uploaded.
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia_coal_price_rank as K  # noqa: E402
import eia_coal_trade_price as X  # noqa: E402
import eia_meters as M  # noqa: E402
import eia_power_co2_state as P  # noqa: E402
import release_v1 as R  # noqa: E402

METERS = {"period": "2024", "state": "AK", "stateName": "Alaska", "technology": "All meters", "sector": "COM", "sectorName": "commercial",
          "meters": "57259", "meters-units": "number of meters"}
CO2 = {"period": "2024", "stateid": "AK", "stateDescription": "Alaska", "fuelid": "ALL", "fuelDescription": "Total",
       "co2-rate-lbs-mwh": "1196", "co2-thousand-metric-tons": "3636", "co2-rate-lbs-mwh-units": "pounds per megawatthour",
       "co2-thousand-metric-tons-units": "thousand metric tons"}
RANK = {"period": "2001", "stateRegionId": "AK", "stateRegionDescription": "Alaska", "coalRankId": "SUB", "coalRankDescription": "Subbituminous",
        "price": "w", "price-units": "dollars per short ton"}
TRADE = {"period": "2000", "exportImportType": "Exports", "coalRankId": "STM", "coalRankDescription": "Steam Coal", "countryId": "AD",
         "countryDescription": "Andorra", "customsDistrictId": "NY_NY", "customsDistrictDescription": "New York City, NY", "price": "640",
         "price-units": "dollars per short ton"}
TABLES = ["eia_meters_state_annual", "eia_power_co2_state_annual", "eia_coal_price_rank_annual", "eia_coal_trade_price_annual"]


class TheRows(unittest.TestCase):
    def test_meters(self):
        r = M.rows([METERS], "u", "r").iloc[0]
        self.assertEqual((r["entity"], r["variable"], r["value"], r["unit"]), ("eia_meters:AK:all_meters:COM", "meters", 57259.0, "count"))

    def test_co2(self):
        t = P.rows([CO2], "u", "r").set_index("variable")
        self.assertEqual((t.loc["co2", "entity"], t.loc["co2", "value"], t.loc["co2", "unit"]), ("eia_power_co2:AK:ALL", 3636000.0, "tCO2"))
        self.assertAlmostEqual(t.loc["co2_rate", "value"], 1196 * 0.453592)
        self.assertEqual(t.loc["co2_rate", "unit"], "kgCO2/MWh")

    def test_a_withheld_price_has_no_row(self):
        self.assertEqual(len(K.rows([RANK], "u", "r")), 0)
        r = K.rows([dict(RANK, price="38.9")], "u", "r").iloc[0]
        self.assertEqual((r["entity"], r["unit"], r["geo"]), ("eia_coal_price_rank:AK:SUB", "USD/short_ton", "US-AK"))

    def test_trade(self):
        r = X.rows([TRADE], "u", "r").iloc[0]
        self.assertEqual((r["entity"], r["value"], r["unit"], r["ts_utc"]), ("eia_coal_trade:Exports:STM:AD:NY_NY", 640.0, "USD/short_ton", "2000-01-01T00:00:00Z"))

    def test_an_unknown_unit_stops(self):
        with self.assertRaises(RuntimeError):
            X.rows([dict(TRADE, **{"price-units": "dollars per metric ton"})], "u", "r")

    def test_held_until_uploaded(self):
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as h:
            y = h.read()
        for t in TABLES:
            self.assertIn(f"  - {t}\n", y[y.index("catalogue_hold:"):])
            self.assertIn(f"upload.py {t}", R.STORAGE_HELD[t])

    def test_no_em_dash(self):
        for f in ("eia_meters.py", "eia_power_co2_state.py", "eia_coal_price_rank.py", "eia_coal_trade_price.py"):
            with open(os.path.join(ROOT, "warehouse", "connectors", f), encoding="utf-8") as h:
                self.assertNotIn(chr(0x2014), h.read(), f)


if __name__ == "__main__":
    unittest.main()
