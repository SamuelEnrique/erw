"""Session 3819 (chain 216): the suite gate names a subtest's failure.

unittest writes a failing subtest as "FAIL: test_x (tests.test_mod.Class.test_x) (table='...')". The suite gate's pattern
required the line to end after the first parenthesis, so on 12 November 2026 the push guard refused the daily commit with
"the suite stopped before naming a test" while the suite had in fact run to its end with one failing subtest (test 410).
No network, no warehouse table, no model.
"""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import suite_gate as S  # noqa: E402


class TheNames(unittest.TestCase):
    def test_a_subtest_failure_is_named(self):
        lines = ["FAIL: test_every_listed_table_has_a_draft (test_session410.TheHoldsAndRedivis.test_every_listed_table_has_a_draft) (table='iso_reserve_margin_reports')"]
        self.assertEqual(S.failing(lines), [("FAIL", "test_session410.TheHoldsAndRedivis.test_every_listed_table_has_a_draft")])

    def test_the_plain_forms_still_are(self):
        lines = ["FAIL: test_a (tests.test_m.C.test_a)", "ERROR: setUpClass (tests.test_m.D)",
                 "ERROR: test_gone (unittest.loader._FailedTest.test_gone)", "FAIL: test_a (tests.test_m.C.test_a)"]
        self.assertEqual(S.failing(lines), [("FAIL", "tests.test_m.C.test_a"), ("ERROR", "tests.test_m.D.setUpClass"),
                                            ("ERROR", "test_gone (the module could not be imported)")])

    def test_a_printed_line_that_is_not_a_failure_is_not_named(self):
        self.assertEqual(S.failing(["FAILED request 1 of 30: https://www.ercot.com/x: HTTP 403 Forbidden (recorded, left)"]), [])


if __name__ == "__main__":
    unittest.main()
