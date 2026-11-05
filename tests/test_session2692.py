"""Session 2692: DESNZ's Regional Renewable Statistics, installed renewable capacity a year by UK region and technology.

Energy Research Warehouse (ERW). Tests warehouse/connectors/desnz_regional_renewable_capacity.py on sheets built here (made up
for the test, not DESNZ's): each column kept as its own technology in MW, "[x]" and "[y]" not written, the 2022 sheet's region
names read, the co-firing row kept and the footnote rows after it skipped; a column or region not in the map, a region's
technologies that miss its total, England's regions that miss England, a row after co-firing not a footnote and a wrong title
stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2692 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import desnz_regional_renewable_capacity as A  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

REG = list(A.REGIONS)


NAMES_2022 = [{"East of England": "Eastern", "Other Sites": "Other", "UK Total": "Total"}.get(r, r) for r in REG]


def sheet(year=2010, cols=("Wind [note 4]", "Hydro"), london=(1.0, 2.0), title=None, regions=None, england_total=None, tail=None):
    rows = [(title or f"Installed capacity of sites generating electricity from renewable sources, {year}",), ("one table",),
            ("MW installed capacity [note 1]",), ("Region", *cols, "Total")]
    vals = {r: (1.0, 2.0) for r in REG}
    vals["London"] = london
    vals["England"] = (9.0, 18.0)
    vals["UK Total"] = (13.0, 26.0)
    for r, shown in zip(REG, regions or REG):
        a, b = vals[r]
        tot = (a if isinstance(a, float) else 0.0) + b
        if r == "London" and isinstance(london[0], str):
            tot = 3.0 if "[x]" in london[0] else b  # an [x] cell is in the total; a [y] cell is not
        if r == "England" and england_total is not None:
            tot = england_total
        rows.append((shown, a, b, tot))
    rows.append(("Co-firing [note 6]", "[y]", 5.0, 5.0))
    rows += tail if tail is not None else [("Other bioenergy = AD + Biomass and waste",)]
    return rows


class Parse(unittest.TestCase):
    def test_rows(self):
        v = A.parse_sheet(sheet(), 2010)
        self.assertEqual(v[("scotland", "wind")][0], 1.0)
        self.assertEqual(v[("uk", "total")][0], 39.0)
        self.assertEqual(v[("co_firing", "hydro")][0], 5.0)
        self.assertNotIn(("co_firing", "wind"), v)

    def test_2022_names_and_hidden(self):
        v = A.parse_sheet(sheet(year=2022, regions=NAMES_2022, london=(" [y]", 2.0)), 2022)
        self.assertIn(("east_of_england", "total"), v)
        self.assertIn(("other_sites", "hydro"), v)
        self.assertNotIn(("london", "wind"), v)

    def test_stops(self):
        for rows in (sheet(cols=("Wind", "Peat")), sheet(regions=REG[:-2] + ["Isle of Man", "UK Total"]), sheet(london=(1.0, 5.0)),
                     sheet(england_total=40.0), sheet(title="Generation of electricity from renewable sources, 2010"),
                     sheet(tail=[("Isle of Man", 1.0, 1.0, 2.0)])):
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
