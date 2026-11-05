"""Session 2734: DESNZ's DUKES 5.7, the UK's de-rated plant capacity a year.

Energy Research Warehouse (ERW). Tests warehouse/connectors/desnz_dukes_capacity.py on a sheet built here (made up for the test,
not DESNZ's): two tables read by their titles, the groups and items made entities, "Mixed or dual fuelled" read as mixed or dual
fired; every total checked against its parts, the groups against all companies, and the renewables, low carbon and fossil totals;
DESNZ's own 99 MW of 2015 passing only at that amount and that year; a group not in the map stopping the run; the sector rule and
the holds. No network.

    python -m unittest tests.test_session2734 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import desnz_dukes_capacity as A  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

M, O, L = "Major power producers [note 2]", "Other generators [note 4]", "All generating companies"


def sheet(year="2014", all_total=None, fossil=None, group=None):
    gas_m, gas_o, nuc, pump, wind_m, wind_o = 30.0, 3.0, 9.0, 2.0, 2.0, 1.0
    a_total = all_total if all_total is not None else gas_m + gas_o + nuc + pump + wind_m + wind_o
    fos = fossil if fossil is not None else gas_m + gas_o
    ren = wind_m + wind_o
    years = tuple(str(y) for y in range(1996, int(year) + 1))
    pad = (None,) * (len(years) - 1)
    r = lambda g, n, v: (g, n) + pad + (v,)
    return [("Table 5.7 de-rated plant capacity",), ("notes",),
            ("Table 5.7.A Capacity by fuel [note 1], MW",), ("Generator Type", "Fuel") + years,
            r(group or M, "Total transmission entry capacity [note 3] [note 4]", gas_m + nuc + pump + wind_m),
            r(M, "Gas fired", gas_m), r(M, "Mixed or dual fired [note 5]", 0), r(M, "Nuclear stations", nuc),
            r(M, "Pumped hydro", pump), r(M, "Onshore wind", wind_m),
            r(O, "Total capacity of own generating plant [note 9]", gas_o + wind_o), r(O, "Gas fired", gas_o), r(O, "Onshore wind", wind_o),
            r(L, "Total capacity ", a_total), r(L, "Gas fired", gas_m + gas_o), r(L, "Mixed or dual fuelled", 0),
            r(L, "Nuclear stations", nuc), r(L, "Pumped hydro", pump), r(L, "Onshore wind", ren),
            r(L, "Total renewables capacity [note 9]", ren), r(L, "Total low carbon capacity [note 10]", ren + nuc),
            r(L, "Total fossil fuels capacity [note 11]", fos),
            ("Table 5.7.B Capacity of Thermal Stations by Type [note 1], MW",), ("Generator Type", "Technology") + years,
            r("Major power producers", "Total capacity of MPP thermal stations", gas_m), r("Major power producers", "CCGT stations", gas_m),
            r("Other generators", "Total capacity of other thermal stations", gas_o), r("Other generators", "CCGT stations", gas_o),
            r(L, "Total capacity of all thermal stations", gas_m + gas_o), r(L, "CCGT stations", gas_m + gas_o)]


class Parse(unittest.TestCase):
    def test_rows(self):
        vals, nodes = A.parse_sheet(sheet())
        self.assertEqual(vals[(2014, "all:mixed_or_dual_fired", "derated_capacity")], 0.0)
        self.assertEqual(vals[(2014, "all:total", "derated_capacity")], 47.0)
        self.assertEqual(vals[(2014, "other:ccgt_stations", "thermal_capacity")], 3.0)
        self.assertEqual(nodes[("all:mixed_or_dual_fired", "derated_capacity")], "All generating companies: Mixed or dual fuelled")
        self.assertNotIn((2013, "all:total", "derated_capacity"), vals)

    def test_known_difference_only_where_named(self):
        vals, _ = A.parse_sheet(sheet(year="2015", all_total=47.0 + 99.0, fossil=33.0 + 99.0))
        self.assertEqual(vals[(2015, "all:total", "derated_capacity")], 146.0)
        for rows in (sheet(year="2014", all_total=47.0 + 99.0, fossil=33.0 + 99.0),     # 99 MW off in a year not named
                     sheet(year="2015", all_total=47.0 + 50.0, fossil=33.0 + 99.0)):    # another amount in a named year
            with self.assertRaises(RuntimeError):
                A.parse_sheet(rows)

    def test_stops(self):
        for rows in (sheet(group="Independent producers"), sheet(all_total=48.0), sheet(fossil=40.0)):
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
