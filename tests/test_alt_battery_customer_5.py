"""Ruling alternative 5 of /battery/customer (session 7704, 17 November 2026, branch wip/alt-battery-customer-5; not a
default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-battery-customer-2026-11-17.md, line 5): lower
the energy rates' limit from USD 5 to USD 1 per kWh? On this branch it is USD 1 (site/lib/customerbattery.ts FIELDS; the
replication's field table follows). Pinned with the page's own arithmetic (site/scripts/alt-battery-customer-figures.mjs):
every published case is still read (the highest rate typed is USD 0.1924) and its year does not move; the read's store
with 4.9 and 2.5 typed for cents is refused and shows no figure (main reads them as dollars, USD 62,332 to 76,446 a year
on the demand charges tried; 70,169 in the read's own case); typed in dollars the same store is read.

    python -m unittest tests.test_alt_battery_customer_5 -v
"""

import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")


class TheLimit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        p = subprocess.run(["node", "--import", "./scripts/tsx-register.mjs", "scripts/alt-battery-customer-figures.mjs"], cwd=SITE, capture_output=True, text=True, timeout=300)
        if p.returncode != 0:
            raise AssertionError(p.stderr[-2000:])
        cls.f = json.loads(p.stdout)

    def test_the_limit(self):
        self.assertEqual(self.f["limit"], 1)

    def test_every_published_case_is_read_and_does_not_move(self):
        for cid, year in (("seattle-md-city-tou", 12795.06), ("austin-sv2", 8931.16), ("sce-tou-gs-2-b-2013-summer", 44123.70), ("srp-e32-summer-peak", 13376.42)):
            self.assertEqual(round(self.f[cid]["year"], 2), year, cid)

    def test_rates_typed_in_cents_are_refused(self):
        self.assertEqual(self.f["store_cents"], {"missing": ["peakRate", "offPeakRate"]})
        self.assertIn("year", self.f["store_dollars"])


if __name__ == "__main__":
    unittest.main()
