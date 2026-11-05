"""Session 2141: AFDC's alternative fueling station counts by state.

Energy Research Warehouse (ERW). Tests warehouse/connectors/afdc_stations.py on sheets built here in AFDC's two forms
(made up for the test, not AFDC's): from 2014 the pairs and triples under Electric, Hydrogen and Propane and the level row
under each state; before, one number a fuel under a header split over two rows, the Electric column read as locations to
2010 and as ports after; the Total row as the United States; a place not known, a count not a whole number, a pair that
is not one and a header of neither form stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2141 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import afdc_stations as A  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

N = None
NEW = [("Station Counts by State and Fuel Type",) + (N,) * 9, tuple(A.NEW_HEAD),
       (N, N, N, N, "(stations / charging outlets", "(retail / non-retail / total)", N, "(primary / secondary / total)", N, N),
       (N, N, N, N, "Level 1 / Level 2 / DC Fast)", N, N, N, N, N),
       ("Alabama", 10, 23, 44, "659 | 2,119", "0 | 0 | 0", 2, "13 | 46 | 59", 0, 2257),
       (N, N, N, N, "21 | 1,229 | 869", N, N, N, N, N),
       ("Total", 10, 23, 44, "659 | 2,119", "0 | 0 | 0", 2, "13 | 46 | 59", 0, 2257),
       (N, N, N, N, "21 | 1,229 | 869", N, N, N, N, N),
       (N,) * 10, ("(a) Includes legacy chargers",) + (N,) * 9]
OLD = [("Station Counts by State and Fuel Type",) + (N,) * 8, ("State", "Biodiesel", "CNG", "E85", N, N, "LNG", N, "Total"), (N,) * 9,
       (N, N, N, N, "Electric", "Hydrogen", N, "Propane", N), ("Alabama", 5, 4, 15, 3, 0, 1, 128, 156), (N,) * 9,
       ("Total", 5, 4, 15, 3, 0, 1, 128, 156)]


def as_dict(tuples):
    return {(st, var): n for st, var, node, n in tuples}


class Sheets(unittest.TestCase):
    def test_new_form(self):
        t, layout = A.parse_sheet(NEW, 2025)
        d = as_dict(t)
        self.assertEqual(layout, "2014_on")
        self.assertEqual(d[("AL", "ev_locations")], 659)
        self.assertEqual(d[("AL", "ev_ports")], 2119)
        self.assertEqual(d[("AL", "ev_ports_level2")], 1229)
        self.assertEqual(d[("AL", "ev_ports_dc_fast")], 869)
        self.assertEqual(d[("AL", "stations_propane_secondary")], 46)
        self.assertEqual(d[("AL", "stations_total")], 2257)
        self.assertEqual(d[("US", "stations_e85")], 44)
        self.assertEqual(len(t), 2 * 17)

    def test_old_form(self):
        d10, d11 = as_dict(A.parse_sheet(OLD, 2010)[0]), as_dict(A.parse_sheet(OLD, 2011)[0])
        self.assertEqual(d10[("AL", "ev_locations")], 3)
        self.assertNotIn(("AL", "ev_ports"), d10)
        self.assertEqual(d11[("AL", "ev_ports")], 3)
        self.assertEqual(d10[("AL", "stations_propane")], 128)
        self.assertEqual(d10[("US", "stations_total")], 156)

    def test_stops(self):
        bad_place = list(NEW)
        bad_place[4] = ("Atlantis",) + NEW[4][1:]
        bad_count = list(NEW)
        bad_count[4] = NEW[4][:1] + ("ten",) + NEW[4][2:]
        bad_pair = list(NEW)
        bad_pair[4] = NEW[4][:4] + ("659",) + NEW[4][5:]
        bad_head = list(OLD)
        bad_head[1] = ("State", "Biodiesel", "CNG", "Ethanol", N, N, "LNG", N, "Total")
        for rows, y in ((bad_place, 2025), (bad_count, 2025), (bad_pair, 2025), (bad_head, 2010)):
            with self.assertRaises(RuntimeError):
                A.parse_sheet(rows, y)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(A.TABLE), "power")
        self.assertIn(A.TABLE, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {A.TABLE}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
