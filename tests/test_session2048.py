"""Session 2048: Oak Ridge's Transportation Energy Data Book.

Energy Research Warehouse (ERW). Tests warehouse/connectors/ornl_tedb.py on sheets built here in TEDB's form (made up
for the test, not ORNL's), beginning in column B as TEDB's do: the sectors' quads written as TBtu, the shares in
percent, the modes' paths from their capitals and indentation, a footnote letter dropped from a label, the sales in
thousands written as a count, a dash no row; a label not in the map and a key given twice stopping the run; the sector
rule and the holds. No network.

    python -m unittest tests.test_session2048 -v
"""

import io
import os
import sys
import unittest

import openpyxl

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import ornl_tedb as T  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402


def book(rows):
    wb = openpyxl.Workbook()
    ws = wb.active
    for r in rows:
        ws.append([None] + list(r))
    out = io.BytesIO()
    wb.save(out)
    return out.getvalue()


T22 = book([["Table 2.2"], ["Year", "Transportation", "Percentage transportation", "Industrial", "Commercial", "Residential", "Totala"],
            [2023, 28.1, 0.3, 31.0, 16.3, 20.0, 93.6], [2024, 28.2, 0.3, 31.2, 16.5, 20.1, 94.2], ["Average annual percentage change"]])
T24 = book([["Table 2.4"], ["Year", "Petroleuma", "Natural gasb", "Coal", "Renewables", "Electricityc", "Total"],
            ["", "", "", "", "", "", "(trillion Btu)"], [2024, 0.882, 0.049, 0, 0.068, 0.002, 28150.9]])
MODES = [["HIGHWAY", 20981.4, 1], ["Light-duty vehicles", 14373.1, 1], ["   Cars", 4786, 1], ["   Light-duty trucksb", 9529.7, 1],
         ["NONHIGHWAY", 5120.3, 1], ["Rail", 470.4, 1], ["   Passenger", 42.7, 1], ["          Transit", 14.6, 1],
         ["HWY & NONHWY TOTAL", 26101.6, 1], ["Off-highwayc", 2326.8, None]]
T27 = book([["Table 2.7"], ["Domestic Consumption of Transportation Energy by Mode and Fuel Type, 2023"], ["", "Gasoline", "Electricityb", "Totalc"]]
           + [[m, "-", 1.0, v] for m, v, _ in MODES[:-1]] + [["Source:"]])
T28 = book([["Table 2.8"], ["", 2022, 2023]] + [[m, v - 10, v] for m, v, _ in MODES] + [[""], ["Source:"]])
T62 = book([["Table 6.2"], ["Calendar", "Hybrid vehicle sales (thousands)", "Plug-in hybrid vehicle sales (thousands)", "All-electric vehicle sales (thousands)",
                            "All light-duty vehicle salesa (thousands)", "Hybrid share"], ["year"], [2024, 1609, 321.8, 1247.7, 15436, 0.104]])
FILES = {"2_02": T22, "2_04": T24, "2_07": T27, "2_08": T28, "6_02": T62}


class Build(unittest.TestCase):
    def test_rows(self):
        t = T.build(FILES, "u", "r", "v", "Edition 41").set_index(["entity", "variable", "ts_utc"])
        v = lambda e, var, y: t.loc[(f"ornl_tedb:{e}", var, f"{y}-01-01T00:00:00Z"), "value"]
        self.assertEqual(v("t2_2:total", "energy_consumption", 2024), 94200.0)
        self.assertNotIn(("ornl_tedb:t2_2:percentage", "energy_consumption", "2024-01-01T00:00:00Z"), t.index)
        self.assertEqual((v("t2_4:transportation", "share_petroleum", 2024), v("t2_4:transportation", "energy_use", 2024)), (88.2, 28150.9))
        self.assertEqual(v("t2_8:highway.light_duty.trucks", "energy_use", 2023), 9529.7)
        self.assertEqual(v("t2_8:nonhighway.rail.passenger.transit", "energy_use", 2022), 4.6)
        self.assertEqual(v("t2_7:highway.light_duty.cars", "energy_use_electricity", 2023), 1.0)
        self.assertNotIn(("ornl_tedb:t2_7:highway.light_duty.cars", "energy_use_gasoline", "2023-01-01T00:00:00Z"), t.index)
        self.assertEqual(v("t6_2:light_duty", "sales_plugin_hybrid", 2024), 321800.0)

    def test_stops(self):
        bad = dict(FILES, **{"2_08": book([["Table 2.8"], ["", 2022, 2023], ["Hovercraft", 1, 2]])})
        with self.assertRaises(RuntimeError):
            T.build(bad, "u", "r", "v", "Edition 41")
        twice = dict(FILES, **{"2_02": book([["Year", "Transportation", "Total"], [2024, 1, 2], [2024, 1, 2]])})
        with self.assertRaises(RuntimeError):
            T.build(twice, "u", "r", "v", "Edition 41")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(T.NAME), "oil;products;power")
        self.assertIn(T.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {T.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
