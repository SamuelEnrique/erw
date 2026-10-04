"""Session 101: the early years. Why the battery model earns so much in ERCOT before 2024: analysis only.

Energy Research Warehouse (ERW). warehouse/analysis/battery_early_years.py takes the page's ERCOT figure down a ladder,
one assumption at a time, with the page's own program. These tests hold what must be true of any such ladder (a rung
that only adds a limit cannot earn more than the rung above it; the first rung is the page's table), that the analysis
writes no table and changes no page, and that the method note's figures are the analysis's.

    python -m unittest tests.test_session101 -v
"""

import os
import re
import subprocess
import sys
import unittest

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "analysis"))
import battery_early_years as ey  # noqa: E402

YEARLY = ey.OUT.format("yearly")
DAILY = ey.OUT.format("daily")
RUNGS = ["page_dayahead_4h", "dayahead_fleet", "dayahead_fleet_no_regulation", "energy_only_fleet"]


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheLadder(unittest.TestCase):
    def test_a_rung_that_adds_a_limit_cannot_earn_more(self):
        bs = ey.bs
        rng = np.random.default_rng(101)
        energy = 30 + 25 * np.sin(np.arange(24) / 24 * 2 * np.pi) + rng.normal(0, 3, 24)
        prices = [np.full(24, 9.0) + rng.normal(0, 1, 24), np.full(24, 6.0), np.full(24, 14.0) + rng.normal(0, 2, 24)]
        spec = ((True, 1.0), (False, 1.0), (True, 1.0))                                      # regulation up, regulation down, a reserve
        four = bs.solve_day(energy, prices, spec, 4)["total"]
        ones, no_reg, none = [np.ones(24)] * 3, [np.zeros(24), np.zeros(24), np.ones(24)], [np.zeros(24)] * 3
        short = bs.solve_day(energy, prices, spec, 0.54, caps=ones)
        self.assertEqual(bs.check_day(short, spec, 0.54), [])                                # the page's program holds at half an hour too
        a, b, c = short["total"], bs.solve_day(energy, prices, spec, 0.54, caps=no_reg)["total"], bs.solve_day(energy, prices, spec, 0.54, caps=none)
        self.assertGreaterEqual(four + 1e-6, a)
        self.assertGreaterEqual(a + 1e-6, b)
        self.assertGreaterEqual(b + 1e-6, c["total"])
        self.assertAlmostEqual(sum(c["reserve"]), 0.0, places=6)                             # energy only: no reserve is paid
        self.assertAlmostEqual(bs.solve_day(energy, prices, spec, 4, caps=ones)["total"], four, places=6)   # a cap of 1 is no cap

    def test_the_fleets_duration_is_its_mwh_over_its_mw(self):
        if not os.path.exists(os.path.join(ROOT, "warehouse", "output", "storage_buildout_monthly.csv")):
            self.skipTest("storage_buildout_monthly is not on this machine")
        fd = ey.fleet_duration()
        self.assertTrue(all(0.2 < h < 3 for h, _, _ in fd.values()))
        self.assertLess(fd[2018][0], fd[2023][0])                                            # the fleet grew longer
        self.assertLess(fd[2023][0], 2.0)                                                    # and was still under the page's shortest battery
        self.assertLess(fd[2018][1], fd[2023][1])

    def test_it_is_analysis_only(self):
        code = src("warehouse", "analysis", "battery_early_years.py")
        self.assertIn("analysis_internal", code)
        self.assertNotIn("ip.write_csv", code)
        self.assertNotIn("requests", code)
        base = "origin/wip/100-reserves"                                                     # the chain's branch before this session
        if subprocess.run(["git", "rev-parse", "--verify", "--quiet", base], cwd=ROOT, capture_output=True).returncode != 0:
            self.skipTest(f"{base} is not on this machine")
        r = subprocess.run(["git", "diff", "--stat", base, "--", "site", "warehouse/derived", "warehouse/connectors", "docs/methods/battery_stack.md"],
                           cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(r.stdout.strip(), "")                                               # the site, the model and the page's method note are as they were


class TheResult(unittest.TestCase):
    def yearly(self):
        if not os.path.exists(YEARLY):
            self.skipTest("the analysis has not been run on this machine")
        return pd.read_csv(YEARLY, comment="#")

    def test_the_rungs_of_every_year_go_down_and_cover_the_same_days(self):
        y = self.yearly()
        for a, b in zip(RUNGS, RUNGS[1:]):
            self.assertTrue((y[a] + 1e-6 >= y[b]).all(), (a, b))
        self.assertTrue((y["energy_only_fleet"] > 0).all())
        d = pd.read_csv(DAILY, comment="#")
        self.assertEqual(d.groupby("year").size().to_dict(), dict(zip(y["year"], y["days"])))
        self.assertFalse(d.isna().any().any())
        self.assertEqual(int(y[y["year"] == 2019]["days"].iloc[0]), 365)

    def test_the_first_rung_is_the_pages_table(self):
        y = self.yearly()
        self.assertLess((y["table_foresight_4h"] - y["page_foresight_4h"]).abs().max(), 1.0)   # USD per MW over a year
        streams = y[["page_regup", "page_regdn", "page_rrs", "page_ecrs", "page_nspin", "page_energy"]].sum(axis=1)
        self.assertLess((streams - y["page_foresight_4h"]).abs().max(), 1.0)                 # the streams are the figure

    def test_what_the_note_says_is_what_the_analysis_found(self):
        y = self.yearly().set_index("year")
        note = src("docs", "methods", "battery_early_years.md")
        k = lambda v: f"{v / 1000:,.1f}"
        for year in (2018, 2019, 2020, 2021, 2022, 2023):
            row = re.search(rf"^\| {year} \|.*$", note, re.M)
            self.assertIsNotNone(row, year)
            for col in ("page_foresight_4h", "page_dayahead_4h", "dayahead_fleet", "dayahead_fleet_no_regulation", "energy_only_fleet"):
                self.assertIn(f" {k(y.loc[year, col])} ", row.group(0), (year, col))
            self.assertIn(f" {y.loc[year, 'fleet_hours']:.2f} ", row.group(0))
        self.assertIn(k(y.loc[2021, "page_storm_week"]), note)
        self.assertIn("The warehouse holds no measure of what real batteries earned", note)

    def test_no_em_dash_in_what_the_session_wrote(self):
        for parts in (("warehouse", "analysis", "battery_early_years.py"), ("docs", "methods", "battery_early_years.md"), ("tests", "test_session101.py")):
            self.assertNotIn(chr(0x2014), src(*parts), parts)


if __name__ == "__main__":
    unittest.main()
