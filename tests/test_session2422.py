"""Session 2422: the Energy Regulatory Commission of Mongolia's Statistics on Energy Performance (2020 edition):
generation by type and imports, installed capacity, and sales by grid and class, 2015 to 2020.

Energy Research Warehouse (ERW). Tests warehouse/connectors/erc_mongolia.py's reader on tables built here in the form
pdfplumber gives the report (figures made up for the test, not ERC's): GWh written as MWh, capacity as MW, the percentage
rows passed over, the sales table told from the other tables headed "Grid", a figure printed with a space read, a gap
in the generation total within 1 GWh named; a row not in the map, a grid's classes not adding to its total and a value
that is not a number stopping the run; the sector rule and the live-set hold. No network, no PDF.

    python -m unittest tests.test_session2422 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
import erc_mongolia as E  # noqa: E402
import build_coverage as B  # noqa: E402


def tables(total_2020="10.7", cripg_total="5 .0", wind="Wind power plant"):
    gen = [["Generation set", "2019", "2020"],
           ["Combined heat and\npower plant", "6.0", "7.0"], ["Diesel station", "0.5", "0.5"], ["Solar photovoltaic", "1.0", "1.0"],
           ["Hydro power plant", "0.5", "0.5"], [wind, "2.0", "1.0"], ["Total generation", "10.0", total_2020], ["Import", "1.5", "2.0"]]
    cap = [["Generation sets", "2019", "2020"], ["Here of CHPPs", "100.0", "110.0"], ["Percentage", "90%", "90%"],
           ["RE sources", "10.0", "11.0"], ["Percentage", "9%", "9%"], ["Diesel stations", "1.0", "1.0"],
           ["Percentage", "1%", "1%"], ["Installed capacity", "111.0", "122.0"]]
    rows = [["Grid", "Classification", "2019", "2020"]]
    for g in ("CRIPG", "WRIPG", "ERIPG", "AUIPG", "SRPDG"):
        rows += [[g, "E&I", "2.0", "3.0"], [None, "Ap", "1.0", "1.0"], [None, "GD", "2.0", "1.0"],
                 [None, "Total", cripg_total if g == "CRIPG" else "5.0", "5.0"]]
    rows += [["Total for\nthe\nSector", "E&I", "10.0", "15.0"], [None, "Ap", "5.0", "5.0"], [None, "GD", "10.0", "5.0"],
             [None, "Total", "25.0", "25.0"]]
    other = [["Grid", "2015", "2016"], ["CRIPG", "1", "2"]]
    return [gen, cap, other, rows, other]


class Rows(unittest.TestCase):
    def test_rows(self):
        rows, gaps = E.parse(tables())
        got = {(e, v, y): (x, u) for e, n, v, y, x, u in rows}
        self.assertEqual(got[("MN", "generation_wind", 2020)], (1000.0, "MWh"))
        self.assertEqual(got[("MN", "imports", 2019)], (1500.0, "MWh"))
        self.assertEqual(got[("MN", "capacity_total", 2020)], (122.0, "MW"))
        self.assertEqual(got[("cripg", "sales_total", 2019)], (5000.0, "MWh"))
        self.assertEqual(got[("MN", "sales_ger_district", 2020)], (5000.0, "MWh"))
        self.assertNotIn(("MN", "capacity_percentage", 2020), got)
        self.assertEqual(gaps, {2020: (10.0, 10.7)})

    def test_stops(self):
        for t in (tables(total_2020="11.5"), tables(cripg_total="6.0"), tables(cripg_total="x"), tables(wind="Wind farm")):
            with self.assertRaises(RuntimeError):
                E.parse(t)


class Registered(unittest.TestCase):
    def test_sector_and_hold(self):
        self.assertEqual(B.sector_of(E.NAME), "power")
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {E.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
