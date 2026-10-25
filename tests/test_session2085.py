"""Session 2085: IRENA's installed electricity capacity by country and technology (IRENASTAT).

Energy Research Warehouse (ERW). Tests warehouse/connectors/irena_capacity.py on metadata and an answer built here in
PxWeb's form (made up for the test, not IRENA's): the query picks the capacity type, All and the years asked; the answer's
cells read into rows, an empty cell left out and counted, a 0 kept; a table whose variables differ, a code not in the
metadata and a value not a number stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2085 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import irena_capacity as I  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}
META = {"variables": [
    {"code": "Country/area", "values": ["USA", "MEX"], "valueTexts": ["United States", "Mexico"]},
    {"code": "Technology", "values": ["4", "5"], "valueTexts": ["Solar photovoltaic", "Onshore wind energy"]},
    {"code": "Data Type", "values": ["0", "1"], "valueTexts": ["Electricity Generation (GWh)", "Electrical Installed Capacity (MW)"]},
    {"code": "Grid connection", "values": ["0", "1", "2"], "valueTexts": ["All", "On-grid", "Off-grid"]},
    {"code": "Year", "values": ["0", "1", "2"], "valueTexts": ["2023", "2024", "2025"]}]}


def answer(cells):
    return {"columns": [{"code": c} for c in I.VARS] + [{"code": "value"}],
            "data": [{"key": k, "values": [v]} for k, v in cells]}


class Query(unittest.TestCase):
    def test_query(self):
        q = I.query(META, 2024, 2025)
        sel = {x["code"]: x["selection"]["values"] for x in q["query"]}
        self.assertEqual((sel["Data Type"], sel["Grid connection"], sel["Year"]), (["1"], ["0"], ["1", "2"]))
        self.assertEqual(sel["Country/area"], ["USA", "MEX"])
        with self.assertRaises(RuntimeError):
            I.query({"variables": META["variables"][:4]}, 2024, 2025)
        with self.assertRaises(RuntimeError):
            I.query(META, 2020, 2025)


class Parse(unittest.TestCase):
    def test_rows(self):
        s, empty = I.parse(answer([(["USA", "4", "1", "0", "1"], "176843.2"), (["MEX", "5", "1", "0", "1"], "0"),
                                   (["MEX", "4", "1", "0", "2"], "..")]), META, BASE)
        s = s.set_index(["entity", "variable", "ts_utc"])
        a = s.loc[("irena:USA", "capacity_solar_photovoltaic", "2024-01-01T00:00:00Z")]
        self.assertEqual((a.value, a.unit, a.freq, a.node, a.x_technology_code), (176843.2, "MW", "P1Y", "United States", "4"))
        self.assertEqual(s.loc[("irena:MEX", "capacity_onshore_wind_energy", "2024-01-01T00:00:00Z")].value, 0.0)
        self.assertEqual((len(s), empty), (2, 1))

    def test_stops(self):
        with self.assertRaises(RuntimeError):
            I.parse(answer([(["CAN", "4", "1", "0", "1"], "1")]), META, BASE)
        with self.assertRaises(RuntimeError):
            I.parse(answer([(["USA", "4", "1", "0", "1"], "about 5")]), META, BASE)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(I.TABLE), "power")
        self.assertIn(I.TABLE, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {I.TABLE}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
