"""Session 11200 (chain 760, part E): a step's recorded reason is not a line of a publisher's HTML error page.

On 26 November the hourly network's failures were recorded as "<P>https&#58;&#47;&#47;errors&#46;edgesuite..." (EIA's
error page, printed by the step) twelve times, which the health page and summaries showed as the reason.
"""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "warehouse"))
import health  # noqa: E402


class TheReason(unittest.TestCase):
    def test_markup_lines_are_passed_over(self):
        lines = ["network_hourly FAILED: RuntimeError: EIA electricity/rto/region-data offset 0: HTTP 504: <html>",
                 "<HEAD><TITLE>Error</TITLE></HEAD>",
                 "<P>https&#58;&#47;&#47;errors&#46;edgesuite&#46;net&#47;18&#46;5d</P>",
                 "</BODY></HTML>"]
        got = health.reason_of(lines, failed=True)
        self.assertTrue(got.startswith("network_hourly FAILED: RuntimeError: EIA electricity/rto/region-data offset 0"))
        self.assertNotIn("<", got)
        self.assertNotIn("&#", got)

    def test_plain_lines_are_kept(self):
        self.assertEqual(health.reason_of(["a", "b FAILED (failures=1)"], failed=True), "b FAILED (failures=1)")
        self.assertEqual(health.reason_of(["done: 3 rows"], failed=False), "done: 3 rows")


if __name__ == "__main__":
    unittest.main()
