"""Session 2073: NOAA's billion-dollar disasters.

Energy Research Warehouse (ERW). Tests warehouse/connectors/noaa_billion_disasters.py on a file built here in NCEI's
form (made up for the test, not NCEI's): the title lines skipped, the dates, the millions written as dollars, the type in
snake case; a header not NCEI's, a date not YYYYMMDD, a cost that is not a number and an event given twice stopping the
run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2073 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import noaa_billion_disasters as N  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

HEAD = "Weather and Climate Billion-Dollar Disasters\nCost values are in millions of dollars\nName,Disaster,Begin Date,End Date,CPI-Adjusted Cost,Unadjusted Cost,Deaths\n"
ROW = '"Hurricane Z (October 2024)",Tropical Cyclone,20241009,20241010,34250,34000.5,32\n'


class Build(unittest.TestCase):
    def test_rows(self):
        t = N.build(HEAD + ROW + '"Freeze Y (2023)",Freeze,20230101,20230105,1000,900,\n', "u", "r")
        a = t[t.x_name == "Hurricane Z (October 2024)"].iloc[0]
        self.assertEqual((a.event_date, a.x_end_date, a.event_type), ("2024-10-09", "2024-10-10", "tropical_cyclone"))
        self.assertEqual((a.x_cost_cpi_adjusted_usd, a.x_cost_unadjusted_usd, a.x_deaths), ("34250000000", "34000500000", "32"))
        self.assertTrue(a.event_id.startswith("noaa_billion:2024-10-09:"))
        self.assertEqual(t[t.event_type == "freeze"].iloc[0].x_deaths, "")

    def test_stops(self):
        for bad in (HEAD.replace("Deaths", "Fatalities") + ROW, HEAD + ROW.replace("20241009", "2024-10-09"),
                    HEAD + ROW.replace("34250", "lots"), HEAD + ROW + ROW, HEAD.replace("millions", "billions") + ROW):
            with self.assertRaises(RuntimeError):
                N.build(bad, "u", "r")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(N.NAME), "power")
        self.assertIn(N.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {N.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
