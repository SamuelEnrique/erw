"""The problem sets' lookbacks outlast a gap and a month boundary (session 4051, chain 230, the landing desk).

At midnight on 14 November 2026 every build printed errors on /learn/problems/know-your-grid ("Cannot read properties of
undefined") and /learn/problems/storage-and-taxes (a timestamp "undefined-01"), and check-routes failed every landing:
set A looked for "the latest day both grids are held" in the last 10 days, and the live set lacked 5 to 8 November of
EIA-930, so when 4 November left the window there was none; set D read WTI's months over 75 days, and when 31 August
left the window no held month had a certified Texas gas price. The windows are now 45 and 400 days: "latest" means what
it meant, and a gap of a few days or a month's turn no longer empties the answer. Run under node on 14 November at 00:40
UTC against the live set: both sets built, 5 questions each."""

import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class TheLookbacks(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(ROOT, "site", "lib", "problems.ts"), encoding="utf-8") as f:
            self.s = f.read()

    def test_the_latest_day_both_grids_hold_is_looked_for_over_45_days(self):
        self.assertIn("const LOOK = 45 * DAY;", self.s)
        self.assertIn('variable: "mwh_discharged", since: iso(Date.now() - LOOK)', self.s)
        self.assertIn('variable: "intensity_generation", since: iso(Date.now() - LOOK)', self.s)

    def test_the_held_months_reach_a_certified_month(self):
        m = re.search(r'entity: "eia:wti_cushing", variable: "spot_price", since: iso\(Date\.now\(\) - (\d+) \* DAY\)', self.s)
        self.assertIsNotNone(m)
        self.assertGreaterEqual(int(m.group(1)), 400)


if __name__ == "__main__":
    unittest.main()
