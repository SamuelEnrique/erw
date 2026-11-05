"""Session 2743: DESNZ's DUKES 5.8, the major power producers' capacity by UK country a year.

Energy Research Warehouse (ERW). Tests warehouse/connectors/desnz_dukes_mpp_countries.py on a sheet built here (made up for the
test, not DESNZ's): three tables read by their titles, "[x]" years without a row, shares stated as a ratio; each country's parts
checked against its totals, the shares against 1 and against the totals; a country not in the map stopping the run; the sector
rule and the holds. No network.

    python -m unittest tests.test_session2743 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import desnz_dukes_mpp_countries as A  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

YEARS = ("1996", "1997")


def sheet(ew_gas=60.0, shares=(0.6, 0.3, 0.1), country="Scotland"):
    a = [("Table 5.8.A Major Power Producer Capacity by fuel [note 1], MW",), ("Region", "Fuel") + YEARS,
         ("England and Wales [note 2]", "Total MPP capacity [note 3]", "[x]", 60.0), ("England and Wales", "Gas fired", "[x]", ew_gas),
         (country + " [note 2]", "Total MPP capacity [note 3]", "[x]", 30.0), (country, "Onshore wind [note 5][note 6]", "[x]", 30.0),
         ("Northern Ireland [note 2]", "Total MPP capacity [note 3]", "[x]", 10.0), ("Northern Ireland", "Gas fired", "[x]", 10.0), ()]
    b = [("Table 5.8.B Shares of major power producer capacity by country, per cent",), ("Generator Type", "Region") + YEARS,
         ("Major Power Producer", "England and Wales", "[x]", shares[0]), ("Major Power Producer", "Scotland", "[x]", shares[1]),
         ("Major Power Producer", "Northern Ireland", "[x]", shares[2])]
    c = [("Table 5.8.C Capacity by type of plant [note 1], MW",), ("Region", "Fuel") + YEARS,
         ("England and Wales [note 2]", "Total capacity of thermal stations [note 3]", "[x]", 60.0),
         ("England and Wales", "CCGT stations", "[x]", 60.0)]
    return [("Table 5.8",), ("notes",)] + a + b + c


class Parse(unittest.TestCase):
    def test_rows(self):
        vals, nodes = A.parse_sheet(sheet())
        self.assertEqual(vals[(1997, "scotland:total", "capacity_share")], 0.3)
        self.assertEqual(vals[(1997, "england_wales:total_thermal", "thermal_capacity")], 60.0)
        self.assertNotIn((1996, "england_wales:total", "derated_capacity"), vals)
        self.assertEqual(nodes[("northern_ireland:gas_fired", "derated_capacity")][1], "GB-NIR")

    def test_stops(self):
        for rows in (sheet(ew_gas=55.0),                    # England and Wales's fuels make 55, its total 60
                     sheet(shares=(0.6, 0.3, 0.2)),         # the shares add to 1.1
                     sheet(shares=(0.5, 0.4, 0.1)),         # add to 1, but not each total over the three
                     sheet(country="Wales")):
            with self.assertRaises(RuntimeError):
                A.parse_sheet(rows)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(A.NAME), "power")
        self.assertIn(A.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {A.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
