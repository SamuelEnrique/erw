"""Session 2306: the Digest's chart of the day reads the held grids from the license file, not from a fixed line.

Until this session warehouse/analysis/findings/daily_chart.py held HELD = ("nyiso", "spp") (the roadmap's ruling of
12 October 2026), while warehouse/metadata/license_status.csv marked ISO-NE's, MISO's and NYISO's tables "license needed"
and no SPP table: the two disagreed. Now held_grids(meta_dir) reads the file (a grid is held when a table whose name
begins with it is marked "license needed"), public_tables and held_series read it, and HELD is held_grids() of the
repository's own file. Fixtures only; no network, no warehouse table.
"""
import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "analysis", "findings"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "news"))
import daily_chart  # noqa: E402

LICENSE = ("table,status,from,publishers\n"
           "nyiso_dam_zone_prices,license needed,2026-10-21,NYISO\n"
           "spp_rtm_hub_prices,license needed,2026-10-21,SPP\n"
           "ercot_dam_hub_prices,public,2026-10-21,ERCOT\n"
           "some_other_table,license needed,2026-10-21,A publisher\n")
COVERAGE = ("table,iso,license\n"
            "ercot_dam_hub_prices,ERCOT,public\n"
            "spp_dam_hub_prices,SPP,public\n"
            "nyiso_load_queue,NYISO,public\n"
            "iso_dam_hub_prices,,public\n"
            "some_other_table,EIA,public\n")


class HeldGridsFromTheLicenseFile(unittest.TestCase):
    def meta(self, d):
        with open(os.path.join(d, "license_status.csv"), "w", encoding="utf-8") as f:
            f.write(LICENSE)
        with open(os.path.join(d, "coverage.csv"), "w", encoding="utf-8") as f:
            f.write(COVERAGE)

    def test_the_held_grids_are_the_file_s(self):
        with tempfile.TemporaryDirectory() as d:
            self.meta(d)
            self.assertEqual(daily_chart.held_grids(d), ("nyiso", "spp"))

    def test_a_held_grid_s_public_table_and_its_series_are_never_candidates(self):
        with tempfile.TemporaryDirectory() as d:
            self.meta(d)
            held = daily_chart.held_grids(d)
            # SPP's and NYISO's tables go, the table marked by name goes, ERCOT's and the consolidated table stay
            self.assertEqual(daily_chart.public_tables(d), {"ercot_dam_hub_prices", "iso_dam_hub_prices"})
            self.assertTrue(daily_chart.held_series("spp:SPPNORTH_HUB", held))
            self.assertTrue(daily_chart.held_series("nyiso:N.Y.C.", held))
            self.assertFalse(daily_chart.held_series("ercot:HB_HUBAVG", held))
            self.assertFalse(daily_chart.held_series("isone:.H.INTERNAL_HUB", held))   # not marked in this fixture

    def test_a_file_that_holds_no_grid_holds_none(self):
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "license_status.csv"), "w", encoding="utf-8") as f:
                f.write("table,status\nsome_other_table,license needed\nercot_dam_hub_prices,public\n")
            self.assertEqual(daily_chart.held_grids(d), ())

    def test_the_module_s_held_is_the_repository_s_own_file(self):
        self.assertEqual(daily_chart.HELD, daily_chart.held_grids())
        # the file of 21 October 2026 marks ISO-NE's, MISO's and NYISO's tables; a later edit of the file moves this, not a line of code
        self.assertIn("nyiso", daily_chart.HELD)
        with open(os.path.join(ROOT, "warehouse", "analysis", "findings", "daily_chart.py"), encoding="utf-8") as f:
            src = f.read()
        self.assertNotIn('HELD = ("nyiso", "spp")', src)
        self.assertNotIn(chr(0x2014), src)


if __name__ == "__main__":
    unittest.main()
