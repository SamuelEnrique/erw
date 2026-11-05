"""Session 510: Form EIA-923, each plant's net generation and fuel consumed, by fuel, a year.

Energy Research Warehouse (ERW). Held on real rows of EIA's API (the 2023 page of session 510's probe): the key takes
fuelType beside fuel2002 (a pumped-storage and a conventional hydro unit share WAT), MMBtu become TBtu, the plant's own
total keeps its own entity, a blank has no row, and an unknown unit or a key given twice stops the run.
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import eia923_plant_fuel as E  # noqa: E402


def row(plant, name, f2002, ftype, fdesc, state, gen, btu):
    return {"period": "2023", "plantCode": plant, "plantName": name, "fuel2002": f2002, "fuelType": ftype,
            "fuelTypeDescription": fdesc, "state": state, "primeMover": "ALL", "generation": gen,
            "total-consumption-btu": btu, "generation-units": "megawatthours", "total-consumption-btu-units": "MMBtu"}


REAL = [row("1", "Sand Point", "ALL", "ALL", "Total", "AK", "3301", "33226"),
        row("1", "Sand Point", "DFO", "DFO", "Distillate Fuel Oil", "AK", "3067", "32380"),
        row("1", "Sand Point", "WND", "WND", "Wind", "AK", "234", "846"),
        row("145", "Horse Mesa", "ALL", "ALL", "Total", "AZ", "127574", "75950"),
        row("145", "Horse Mesa", "WAT", "HPS", "Hydroelectric Pumped Storage", "AZ", "105367", "0"),
        row("145", "Horse Mesa", "WAT", "HYC", "Hydroelectric Conventional", "AZ", "22207", "75950")]


class TheRows(unittest.TestCase):
    def setUp(self):
        self.t = E.rows(REAL, "https://api.eia.gov/v2/electricity/facility-fuel/data/", "2026-10-21T19:24:00Z")

    def test_two_hydro_units_under_one_fuel_are_two_entities(self):
        self.assertIn("eia923:145:WAT:HPS", set(self.t["entity"]))
        self.assertIn("eia923:145:WAT:HYC", set(self.t["entity"]))
        self.assertEqual(len(self.t), 12)

    def test_units_and_values(self):
        g = self.t[(self.t["entity"] == "eia923:1:DFO:DFO") & (self.t["variable"] == "net_generation")].iloc[0]
        self.assertEqual((g["value"], g["unit"], g["ts_utc"], g["freq"], g["geo"]), (3067.0, "MWh", "2023-01-01T00:00:00Z", "P1Y", "US-AK"))
        f = self.t[(self.t["entity"] == "eia923:1:DFO:DFO") & (self.t["variable"] == "fuel_consumed")].iloc[0]
        self.assertEqual(f["unit"], "TBtu")
        self.assertAlmostEqual(f["value"], 0.03238)
        self.assertEqual(g["node"], "Sand Point: Distillate Fuel Oil")

    def test_the_plant_total_equals_its_fuels(self):
        g = self.t[self.t["variable"] == "net_generation"].set_index("entity")["value"]
        self.assertEqual(g["eia923:1:ALL:ALL"], g["eia923:1:DFO:DFO"] + g["eia923:1:WND:WND"])
        self.assertEqual(g["eia923:145:ALL:ALL"], g["eia923:145:WAT:HPS"] + g["eia923:145:WAT:HYC"])

    def test_a_blank_has_no_row(self):
        t = E.rows([row("1", "Sand Point", "WND", "WND", "Wind", "AK", None, "846")], "u", "r")
        self.assertEqual(list(t["variable"]), ["fuel_consumed"])

    def test_an_unknown_unit_stops(self):
        r = dict(REAL[0], **{"generation-units": "gigawatthours"})
        with self.assertRaises(RuntimeError):
            E.rows([r], "u", "r")

    def test_a_key_given_twice_stops(self):
        with self.assertRaises(RuntimeError):
            E.rows([REAL[1], REAL[1]], "u", "r")

    def test_no_em_dash(self):
        for f in ("warehouse/connectors/eia923_plant_fuel.py", "tests/test_session510.py"):
            with open(os.path.join(ROOT, *f.split("/")), encoding="utf-8") as h:
                self.assertNotIn(chr(0x2014), h.read(), f)


if __name__ == "__main__":
    unittest.main()
