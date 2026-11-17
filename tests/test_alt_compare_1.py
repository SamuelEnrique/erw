"""Ruling alternative 1 of /prices/compare (session 7724, 17 November 2026, branch wip/alt-compare-1; not a default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-compare-2026-11-17.md, line 1): show ISO-NE's and
NYISO's grid carbon intensity, EIA's public figure, while their prices stay held? On this branch the builder writes
held_carbon to the site's copy (warehouse/derived/price_compare.py held_carbon, from the public table
carbon_intensity_daily, which the Grid tool draws) and the page names it in "Held, not shown" for the window chosen. Never
MISO (paused). No price of a held grid is written. Pinned with the builder's own function on the local table where it is
on the machine (warehouse/output, or the folder ERW_TABLES_DIR names): four figures added, kg CO2 per MWh generated,
ISO-NE 227.6 over the twelve months to October 2026 (363 of 365 days) and 210.5 in October 2026; NYISO 247.3 and 216.3.

    python -m unittest tests.test_alt_compare_1 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import price_compare as pc  # noqa: E402

TABLES = os.environ.get("ERW_TABLES_DIR") or os.path.join(ROOT, "warehouse", "output")
WINDOWS = {"year": ("2025-11-01", "2026-11-01", "P1Y"), "month": ("2026-10-01", "2026-11-01", "P1M")}


class TheRule(unittest.TestCase):
    def test_never_miso_and_only_held_grids(self):
        self.assertEqual(pc.HELD_CARBON_SHOWN, {"isone": "ISO-NE", "nyiso": "NYISO"})
        self.assertEqual(pc.held_carbon(TABLES, WINDOWS, set()), {})

    def test_the_site_copy_carries_it(self):
        with open(os.path.join(ROOT, "warehouse", "derived", "price_compare.py"), encoding="utf-8") as f:
            self.assertIn("held_carbon=held_carbon(inputs, windows, ls.held_grids())", f.read())


@unittest.skipUnless(os.path.exists(os.path.join(TABLES, "carbon_intensity_daily.csv")), "carbon_intensity_daily is not on this machine")
class OnTheLocalTable(unittest.TestCase):
    def test_the_four_figures(self):
        got = pc.held_carbon(TABLES, WINDOWS, {"ISO-NE", "NYISO", "MISO"})
        self.assertEqual(sorted(got), ["ISO-NE", "NYISO"])
        flat = {(g, w): (round(v["intensity"], 1), v["days_held"], v["days_due"]) for g, ws in got.items() for w, v in ws.items()}
        self.assertEqual(flat[("ISO-NE", "year")], (227.6, 363, 365))
        self.assertEqual((flat[("ISO-NE", "month")][0], flat[("NYISO", "year")][0], flat[("NYISO", "month")][0]), (210.5, 247.3, 216.3))


if __name__ == "__main__":
    unittest.main()
