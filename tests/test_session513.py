"""Session 513: EIA's U.S. nuclear outages, a day (a public source probed in place of DOE's OE-417, which has no file).

Energy Research Warehouse (ERW). Held on real records of EIA's API (21 October 2026 and 9 September 2020): MW kept, the
percent as a ratio, a blank with no row, an unknown unit or a day given twice stops the run; the table is held from /data
and Redivis v1 until uploaded.
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia_nuclear_outages as N  # noqa: E402
import release_v1 as R  # noqa: E402

UNITS = {"capacity-units": "megawatts", "outage-units": "megawatts", "percentOutage-units": "percent"}
REAL = [dict(period="2020-09-09", capacity="97082", outage="6945.393", percentOutage="7.15", **UNITS),
        dict(period="2026-10-21", capacity="100056.7", outage="19936.436", percentOutage="19.93", **UNITS)]


class TheRows(unittest.TestCase):
    def setUp(self):
        self.t = N.rows(REAL, "https://api.eia.gov/v2/nuclear-outages/us-nuclear-outages/data/", "2026-10-21T19:38:00Z")

    def test_three_variables_a_day(self):
        self.assertEqual(len(self.t), 6)
        d = self.t[self.t["ts_utc"] == "2026-10-21T00:00:00Z"].set_index("variable")
        self.assertEqual((d.loc["capacity", "value"], d.loc["capacity", "unit"]), (100056.7, "MW"))
        self.assertEqual((d.loc["outage", "value"], d.loc["outage", "unit"]), (19936.436, "MW"))
        self.assertAlmostEqual(d.loc["outage_share", "value"], 0.1993)
        self.assertEqual(d.loc["outage_share", "unit"], "ratio")
        self.assertEqual(set(self.t["freq"]), {"P1D"})

    def test_a_blank_has_no_row(self):
        self.assertEqual(len(N.rows([dict(REAL[0], outage=None)], "u", "r")), 2)

    def test_an_unknown_unit_or_a_day_twice_stops(self):
        with self.assertRaises(RuntimeError):
            N.rows([dict(REAL[0], **{"capacity-units": "gigawatts"})], "u", "r")
        with self.assertRaises(RuntimeError):
            N.rows([REAL[0], REAL[0]], "u", "r")

    def test_held_until_uploaded(self):
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as h:
            y = h.read()
        self.assertIn("  - eia_nuclear_outages_daily\n", y[y.index("catalogue_hold:"):])
        self.assertIn("upload.py eia_nuclear_outages_daily", R.STORAGE_HELD["eia_nuclear_outages_daily"])

    def test_no_em_dash(self):
        for f in ("warehouse/connectors/eia_nuclear_outages.py", "tests/test_session513.py"):
            with open(os.path.join(ROOT, *f.split("/")), encoding="utf-8") as h:
                self.assertNotIn(chr(0x2014), h.read(), f)


if __name__ == "__main__":
    unittest.main()
