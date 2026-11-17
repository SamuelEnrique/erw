"""Session 7052 (chain 370, the data machine): done-line request 122.

iso_prices.py --only-days asks the named operating days of a per-day market and no other (SPP's daily RTBM files are
about 50 MB each: ten missing days no longer mean the whole 45-day window), and does not run a market whose
completeness rule is the whole window. No request is made here.
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))


class TheOption(unittest.TestCase):
    def setUp(self):
        import iso_prices as ip
        self.ip = ip
        self.lines = []

    def tearDown(self):
        self.ip.ONLY_DAYS = None

    def test_a_whole_window_market_is_not_run(self):
        ip = self.ip
        ip.ONLY_DAYS = {__import__("datetime").date(2026, 10, 7)}
        called = []
        ctx = dict(log=self.lines.append, results=[], iso="spp")
        spec = dict(name="DAM", file="spp_dam_hub_prices", fetch=lambda d: called.append(d))
        self.assertEqual(ip.run_iso(ctx, [spec]), 0)
        self.assertEqual(called, [])
        self.assertEqual(ctx["results"][0]["status"], "skipped")

    def test_the_per_day_loop_reads_the_named_days_only(self):
        src = open(os.path.join(ROOT, "warehouse", "connectors", "iso_prices.py"), encoding="utf-8").read()
        self.assertIn("if ONLY_DAYS and day.date() not in ONLY_DAYS:", src)
        self.assertIn('ap.add_argument("--only-days"', src)
        self.assertIn("an operating day must be complete (before today)", src)


if __name__ == "__main__":
    unittest.main()
