"""Session 2435: EEHC's annual reports, the table "Electricity in <year>" (Egypt's capacity, peak load and generation).

Energy Research Warehouse (ERW). Tests warehouse/connectors/eehc_egypt_electricity.py on page text built here in the
reports' forms (made up for the test, not EEHC's): the table read between its "Description" line and its fuel line, each
line by its label, unit and two figures, a footnote mark before the unit, thousands written with a typographic apostrophe,
a label whose figures stand on the next line, a dash with no row, the peak load in MW whatever unit is printed beside it,
the fiscal year's first day; a report without its table, a line expected and missing and a figure that is not a number
stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2435 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eehc_egypt_electricity as S  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}
PAGE = "\n".join([
    "Objectives text on the left column",
    "Description 2014/2015 2015/2016 Variation%",
    "Total Installed Capacity (1)",
    "MW 35220 38857 10.3",
    "− Hydro MW 2800 2800 0",
    "− Thermal Affiliated Companies MW 29685 29486 (0.7)",
    "− Fast Track Plan MW - 3636 0",
    "− New and Renewable Energy (Wind & Solar) (2) MW 687 887 29.1",
    "− Private sector BOOT’s (Thermal) MW 2048 2048 0",
    "and selling it on the networks. Peak load GWh 28’015 29200 4.2",
    "Total power generated *: GWh 174875 186320 6.5",
    "− Hydro GWh 13822 13545 (2)",
    "− Thermal (3) GWh 144995 157056 8.3",
    "− New and Renewable Energy (4) GWh 1444 2225.5 54.1",
    "− Energy Purchased from (IPPs) GWh 32 42.4 32.5",
    "− Power generated from private sector (BOOT) GWh 14338 13307 (7.2)",
    "− Power generated from Isolated Plants GWh 244 144.1 (40.9)",
    "Total Fuel Consumption (6) Ktoe 36487 37335 2.3",
    "− Hydro MW 9999 9999 0",
])


class Parse(unittest.TestCase):
    def test_rows(self):
        rows = {(r["variable"], r["entity"], r["ts_utc"]): r for r in S.parse(["a page without the table", PAGE], "2015-2016en.pdf", BASE)}
        self.assertEqual(rows[("capacity", "eehc:eg:total", "2014-07-01T00:00:00Z")]["value"], 35220.0)
        self.assertEqual(rows[("capacity", "eehc:eg:hydro", "2015-07-01T00:00:00Z")]["value"], 2800.0)
        self.assertNotIn(("capacity", "eehc:eg:fast_track", "2014-07-01T00:00:00Z"), rows)
        self.assertEqual(rows[("capacity", "eehc:eg:fast_track", "2015-07-01T00:00:00Z")]["value"], 3636.0)
        self.assertEqual(rows[("capacity", "eehc:eg:renewable", "2015-07-01T00:00:00Z")]["value"], 887.0)
        p = rows[("peak_load", "eehc:eg", "2014-07-01T00:00:00Z")]
        self.assertEqual((p["value"], p["unit"], p["freq"], p["geo"], p["x_fiscal_year"]), (28015.0, "MW", "P1Y", "EG", "2014/2015"))
        g = rows[("generation", "eehc:eg:renewable", "2015-07-01T00:00:00Z")]
        self.assertEqual((g["value"], g["unit"]), (2225500.0, "MWh"))
        self.assertEqual(rows[("generation", "eehc:eg:thermal", "2014-07-01T00:00:00Z")]["value"], 144995000.0)
        self.assertEqual(rows[("generation", "eehc:eg:private_boot", "2014-07-01T00:00:00Z")]["value"], 14338000.0)
        self.assertEqual(len(rows), 27)

    def test_stops(self):
        with self.assertRaises(RuntimeError):
            S.parse(["no table here"], "2015-2016en.pdf", BASE)
        with self.assertRaises(RuntimeError):
            S.parse([PAGE.replace("− Hydro GWh 13822 13545 (2)\n", "")], "2015-2016en.pdf", BASE)
        with self.assertRaises(RuntimeError):
            S.parse([PAGE.replace("GWh 174875 186320", "GWh 174875 1.8.6")], "2015-2016en.pdf", BASE)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(S.NAME), "power")
        self.assertIn(S.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {S.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
