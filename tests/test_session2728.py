"""Session 2728: DESNZ's DUKES 5.10, the UK's maximum load, plant load factors and thermal efficiency a year.

Energy Research Warehouse (ERW). Tests warehouse/connectors/desnz_dukes_plant_loads.py on sheets built here (made up for the test,
not DESNZ's): the three tables read by their titles, note marks read off, the maximum load in MW and the rest as percentages, "[x]"
without a row and a zero kept; a row not in the map, a year out of turn, regions that miss their total and a percentage over 100
stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2728 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import desnz_dukes_plant_loads as A  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

L = "Simultaneous maximum load met, MW[note 2][note 3]"


def sheet_a(years=("1996", "1997"), gb=(50.0, 52.0), total=(51.0, 53.0)):
    return [("Table 5.10.A",), ("notes",), ("Indicator", "Region") + tuple(years),
            (L, "Total") + total, (L, "England and Wales", "[x]", 45.0), (L, "Scotland", "[x]", 7.0), (L, "Great Britain") + gb,
            (L, "Northern Ireland", 1.0, 1.0), ("Maximum demand as a percentage of major power producers' capacity", "UK", 80.0, 81.0)]


def sheet_bc(lf=50.0, extra=None, years=("1996", "1997")):
    rows = [("Tables 5.10.B and 5.10.C",), ("notes",), ("Table 5.10.B Plant load factor, per cent [note 2][note 4]",),
            ("Generator Type",) + tuple(years)]
    for name in ("Combined cycle gas turbine stations", "Nuclear stations", "Pumped storage hydro",
                 "Conventional thermal and other stations [note 5][note 6]", "of which coal-fired stations [note 7]",
                 "All plant [note 6][note 8]", "System load factor [note 9]"):
        rows.append((name, lf, 0))
    if extra:
        rows.append((extra, 1.0, 1.0))
    rows += [("Table 5.10.C Thermal efficiency, gross calorific value basis, per cent [note 10]",), ("Generator Type",) + tuple(years),
             ("Combined cycle gas turbine stations", 45.0, 46.0), ("Coal fired stations ", 36.0, "[x]"), ("Nuclear stations", 37.0, 38.0)]
    return rows


class Parse(unittest.TestCase):
    def test_rows(self):
        v = A.parse_a(sheet_a())
        v.update(A.parse_bc(sheet_bc()))
        A.check(v)
        self.assertEqual(v[(1997, "uk", "max_load")][:2], (53.0, "MW"))
        self.assertNotIn((1996, "scotland", "max_load"), v)
        self.assertEqual(v[(1996, "uk", "system_load_factor")][:2], (50.0, "pct"))
        self.assertEqual(v[(1997, "coal", "load_factor")][0], 0.0)
        self.assertNotIn((1997, "coal", "thermal_efficiency"), v)
        self.assertEqual(v[(1996, "ccgt", "thermal_efficiency")][0], 45.0)

    def test_stops(self):
        bad_row = sheet_a()
        bad_row.append(("Minimum load met, MW", "Total", 1.0, 1.0))
        cases = [lambda: A.parse_a(bad_row),
                 lambda: A.parse_a(sheet_a(years=("1996", "1998"))),
                 lambda: A.parse_bc(sheet_bc(extra="Wind stations")),
                 lambda: A.check(A.parse_a(sheet_a(total=(55.0, 53.0)))),                # 1996: GB and NI make 51, the total 55
                 lambda: A.check(A.parse_a(sheet_a(gb=(50.0, 58.0), total=(51.0, 59.0)))),  # 1997: E and W and Scotland make 52
                 lambda: A.check(A.parse_bc(sheet_bc(lf=150.0)))]
        for fn in cases:
            with self.assertRaises(RuntimeError):
                fn()


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(A.NAME), "power")
        self.assertIn(A.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {A.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
