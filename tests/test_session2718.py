"""Session 2718: every row of the committed coverage passes the validator, as the package's test asks.

Energy Research Warehouse (ERW). From 23 October 2026 the daily run's step "package tests" failed on
package/tests/test_erw.py::test_coverage_has_one_row_per_table_and_the_documented_columns: seven tables written by chains on
23 and 24 October kept "blocked (1 errors)" in warehouse/metadata/coverage.csv (their writes were validated by main's validator
before their units reached it, and the status was not set back), though each passes the validator now. The package's test runs
only in the daily job, after a landing; this one runs in the check run of every branch, so a branch that carries a blocked row
fails before it reaches main. The rule is the package test's: "pass", or "pass, N warning(s)". No network, no warehouse table.

    python -m unittest tests.test_session2718 -v
"""

import csv
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
COVERAGE = os.path.join(ROOT, "warehouse", "metadata", "coverage.csv")
PASS = re.compile(r"^pass(, \d+ warnings?)?$")


class CoveragePasses(unittest.TestCase):
    def test_every_row_passes(self):
        with open(COVERAGE, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.assertGreater(len(rows), 500)
        bad = [(r["table"], r["validator_status"]) for r in rows if not PASS.match(r["validator_status"])]
        self.assertEqual(bad, [], "coverage rows not passing the validator: rebuild them with build_coverage.py --only "
                                  "(runs/c057/method_cells_locked.sh) once the table passes")

    def test_the_rule_is_the_package_test_s(self):
        with open(os.path.join(ROOT, "package", "tests", "test_erw.py"), encoding="utf-8") as f:
            self.assertIn(r'str.match(r"^pass(, \d+ warnings?)?$")', f.read())
        for ok in ("pass", "pass, 1 warning", "pass, 3 warnings"):
            self.assertTrue(PASS.match(ok))
        for no in ("blocked (1 errors)", "pass (1 errors)", ""):
            self.assertFalse(PASS.match(no))


if __name__ == "__main__":
    unittest.main()
