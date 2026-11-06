"""Session 3021 (chain 164): every reproduce.do read against its reproduce.py and the owner's Stata rules (deep/check_do.py).

Energy Research Warehouse (ERW). No warehouse file, no network, no database.
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "analysis", "findings"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "analysis", "findings", "deep"))
import check_do  # noqa: E402
import demand  # noqa: E402
import prices  # noqa: E402
import prices_markets  # noqa: E402
import cross  # noqa: E402

PY = "# Expected: 2015 1.0, 2025 2.0, change 1.0 (MW); tolerance 0.5 percent of the change.\nprint(1)\n"
GOOD = ('* Expected: 2015 1.0, 2025 2.0, change 1.0 (MW); tolerance 0.5 percent of the change.\n\nclear all\n\n'
        'import delimited "t.csv", varnames(1) stringcols(_all) clear\n\ndestring value, replace force\n\nlist year measure n, noobs\n')


class StataRead(unittest.TestCase):
    def test_a_file_that_holds_and_the_faults_named(self):
        self.assertEqual(check_do.problems(GOOD, PY), [])
        self.assertIn("gsort with a descending key", check_do.problems(GOOD.replace("clear all", "gsort year -value"), PY))
        self.assertIn("a destring without force", check_do.problems(GOOD.replace("replace force", "replace"), PY))
        self.assertIn("the expected line is not the Python script's", check_do.problems(GOOD, PY.replace("2.0,", "2.5,")))
        self.assertIn("a block holds two lines", check_do.problems(GOOD.replace("clear all\n\n", "clear all\n"), PY))

    def test_no_generator_sorts_descending_before_by(self):
        files = [prices.reproduce("top_days_share")("ercot_HB_WEST")["do"], prices.reproduce("top_hours_share")("ercot_HB_WEST")["do"],
                 prices_markets.reproduce("winter_top_share")("ercot_LZ_WEST")["do"], demand.reproduce("top_days")("ercot_ba")["do"],
                 demand.reproduce("winter_vs_summer")("ba_soco")["do"], cross.reproduce("battery_per_peak")("ercot_bat_peak")["do"]]
        for do in files:
            self.assertNotIn("gsort", do)
            self.assertIn("bysort year", do)


if __name__ == "__main__":
    unittest.main()
