"""Session 2552: GASTAT's Electrical Energy Statistics 2024 (Saudi Arabia, the Ministry of Energy's figures).

Energy Research Warehouse (ERW). Tests warehouse/connectors/gastat_saudi_electricity.py on sheets built here (made up for
the test, not GASTAT's): each sheet found by its name and the words of its title (the connector's own words), columns by
their headers' words, years as numbers or text, figures with commas and an approximation sign (kept in x_approx), GW to
MW and GWh to MWh, sheet 7's regions and the year in its title; a sheet missing, a column not found, a region not in the
map, a figure that is not a number and consumption by category not summing to the energy consumed stopping the run; the
sector rule and the holds. No network.

    python -m unittest tests.test_session2552 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import gastat_saudi_electricity as G  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}
AP = G.APPROX


def sheet(name, cells_by_year):
    """A sheet as GASTAT lays it out: a title, the header rows, then a year a row, values from the third column."""
    words, var, unit, scale, specs = G.SHEETS[name]
    title = ("T " + " ".join(words) + " T",)
    head1 = (None, None, "H")
    head2 = (None, None) + tuple(f"w {w} w" if w else "total" for w, _ in specs)
    rows = [(None,), title, head1, head2]
    for year, values in cells_by_year:
        rows.append((year, None) + tuple(values))
    rows.append(("source",))
    return rows


def sheet7(regions=None, year_in_title="2024"):
    words, cats = G.SHEET7
    rows = [(None,), ("T " + words + " " + year_in_title,), ("R", "U", "H"), (None, None) + tuple(f"x {w} x" for w, _ in cats)]
    for name in (regions if regions is not None else G.REGIONS):
        rows.append((name, None, 10, 5, 3, 2, 1))
    rows.append(("source",))
    return rows


def sheets(**over):
    s = {"1 ": sheet("1", [("2023", ["91.1"]), ("2024", [f"92.5 {AP}"])]),
         "2": sheet("2", [(2024, [41.8, 29.3, 17.1, 0.2, 6.55])]),
         "3": sheet("3", [("2024", [f"74.8 {AP}"])]),
         "4": sheet("4", [(2024, [24.7, 22.1, 19.3, 8.2])]),
         "5": sheet("5", [(2023, [380878]), (2024, [402628.5])]),
         "6": sheet("6", [(2023, [f"327,002 {AP}"]), (2024, [f" 340,430 {AP}"])]),
         "7": sheet7(),
         "8": sheet("8", [(2023, [152782, 59134, 35861, 60531, 18694]), (2024, [161207, 58821, 37520, 63446, 19436])])}
    s.update(over)
    return s


class Parse(unittest.TestCase):
    def test_rows(self):
        t = G.parse_sheets(sheets(), BASE)
        r = {(e.split(":")[-1], v, ts[:4]): (x, a) for e, v, ts, x, a in zip(t.entity, t.variable, t.ts_utc, t.value, t.x_approx)}
        self.assertEqual(r[("total", "licensed_capacity", "2024")], (92500.0, "true"))
        self.assertEqual(r[("total", "licensed_capacity", "2023")], (91100.0, ""))
        self.assertEqual(r[("combined_cycle", "licensed_capacity", "2024")][0], 17100.0)
        self.assertEqual(r[("southern", "peak_load", "2024")][0], 8200.0)
        self.assertEqual(r[("total", "energy_consumed", "2024")], (340430000.0, "true"))
        self.assertEqual(r[("industrial", "consumption", "2024")][0], 63446000.0)
        self.assertEqual(r[("jawf", "sales_other", "2024")][0], 1000.0)
        self.assertEqual(len(t), 2 + 5 + 1 + 4 + 2 + 2 + 13 * 5 + 10)
        self.assertEqual(set(t.unit), {"MW", "MWh"})

    def test_stops(self):
        bad = [{k: v for k, v in sheets().items() if k != "4"},
               sheets(**{"2": [r if i != 3 else (None, None, "a", "b", "c", "d", "e") for i, r in enumerate(sheet("2", [(2024, [1, 2, 3, 4, 5])]))]}),
               sheets(**{"7": sheet7(regions=list(G.REGIONS) + ["X"])}),
               sheets(**{"5": sheet("5", [(2024, ["n.a."])])}),
               sheets(**{"8": sheet("8", [(2024, [161207, 58821, 37520, 63446, 19496])])}),
               sheets(**{"7": sheet7(year_in_title="")})]
        for s in bad:
            with self.assertRaises(RuntimeError):
                G.parse_sheets(s, BASE)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(G.NAME), "power")
        self.assertIn(G.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {G.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
