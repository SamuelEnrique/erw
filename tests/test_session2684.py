"""Session 2684: DESNZ's Regional Renewable Statistics, renewable generation a year by UK region and technology, 2003 to 2025.

Energy Research Warehouse (ERW). Tests warehouse/connectors/desnz_regional_renewables.py on sheets built here (made up for the
test, not DESNZ's): each column kept as its own technology and stated in MWh, "[x]" not written and its region's sum allowed to
fall short; a column or region not in the map, a region's technologies that miss its total, England's regions that miss England
and a wrong title stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2684 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import desnz_regional_renewables as A  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

REG = list(A.REGIONS)


def sheet(year=2010, cols=("Wind [note 4]", "Hydro"), london=(1.0, 2.0), title=None, regions=None, england_total=None):
    rows = [(title or f"Generation of electricity from renewable sources, {year}",), ("one table",), ("GWh generated [note 1]",),
            ("Region", *cols, "Total")]
    vals = {}
    for r in REG:
        vals[r] = (1.0, 2.0)
    vals["London"] = london
    vals["England"] = (9.0, 18.0)  # the nine regions
    vals["UK Total"] = (13.0, 26.0)  # England, Wales, Scotland, Northern Ireland and the other sites
    for r in (regions or REG):
        a, b = vals.get(r, (1.0, 2.0))
        tot = (a if isinstance(a, float) else 0.0) + b
        if r == "London" and london[0] == " [x]":
            tot = 3.0
        if r == "England" and england_total is not None:
            tot = england_total
        rows.append((r, a, b, tot))
    return rows


class Parse(unittest.TestCase):
    def test_rows(self):
        v = A.parse_sheet(sheet(), 2010)
        self.assertEqual(v[("scotland", "wind")][0], 1.0)
        self.assertEqual(v[("uk", "total")][0], 39.0)
        self.assertEqual(v[("north_east", "hydro")][1], "North East: Hydro")

    def test_hidden(self):
        v = A.parse_sheet(sheet(london=(" [x]", 2.0)), 2010)
        self.assertNotIn(("london", "wind"), v)
        self.assertEqual(v[("london", "total")][0], 3.0)

    def test_stops(self):
        for rows in (sheet(cols=("Wind", "Peat")), sheet(regions=REG[:-2] + ["Isle of Man", "UK Total"]),
                     sheet(london=(1.0, 5.0)), sheet(england_total=40.0), sheet(title="Generation of electricity, 2010")):
            with self.assertRaises(RuntimeError):
                A.parse_sheet(rows, 2010)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(A.NAME), "power")
        self.assertIn(A.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {A.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
