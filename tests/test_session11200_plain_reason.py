"""Session 11200 (chain 760, done-line request 587): a run's reason holds no publisher's HTML error page.

The Grid tool printed run 20261127T144844Z's reason for eia930_all_demand whole: EIA's 504 page, tags and entities.
write_status now keeps the words before the markup and says what followed; the body stays in the run's log.
"""
import json
import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import iso_prices as ip  # noqa: E402

SEEN = ("RuntimeError: EIA electricity/rto/region-data offset 0 failed after 4 attempts: RuntimeError('EIA "
        "electricity/rto/region-data HTTP 504: <HTML><HEAD><TITLE>Error</TITLE></HEAD><BODY> An error occurred while "
        "processing your request.<p> Reference&#32;&#35;97&#46;350c2d17')")


class ThePlainReason(unittest.TestCase):
    def test_the_markup_is_replaced(self):
        got = ip.plain_reason(SEEN)
        self.assertNotIn("<", got)
        self.assertNotIn("&#", got)
        self.assertTrue(got.startswith("RuntimeError: EIA electricity/rto/region-data offset 0 failed after 4 attempts"))
        self.assertIn("HTTP 504", got)
        self.assertIn("HTML error page", got)

    def test_plain_words_are_kept(self):
        for s in ("publisher did not answer within the budget", "HTTP 404 for https://example.org/a.csv", "", None, 3):
            self.assertEqual(ip.plain_reason(s), s)

    def test_write_status_records_the_plain_reason(self):
        with tempfile.TemporaryDirectory() as d:
            old = ip.STATUS_DIR
            ip.STATUS_DIR = d
            try:
                ip.write_status("t11200", "run", [{"table": "x", "status": "failed", "detail": SEEN}])
                with open(os.path.join(d, "t11200.json"), encoding="utf-8") as fh:
                    rec = json.load(fh)
            finally:
                ip.STATUS_DIR = old
        self.assertNotIn("<HTML>", rec["results"][0]["detail"])


if __name__ == "__main__":
    unittest.main()
