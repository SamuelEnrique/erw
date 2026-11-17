"""Ruling alternative 1 of /battery/customer (session 7704, 17 November 2026, branch wip/alt-battery-customer-1; not a
default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-battery-customer-2026-11-17.md, line 1): the
starting value of "How long your peak lasts", 2 hours, has no source; should it be a tariff's peak-rate window? On this
branch the field starts at 4 hours, Seattle City Light's peak-rate hours (5 p.m. to 9 p.m.), the shortest window of the
tariffs the replication reads (docs/methods/battery_customer.md). The figure is pinned with the page's own arithmetic on
the published cases (site/scripts/alt-battery-customer-figures.mjs): for a reader who leaves the field as it opens,
Austin Energy's secondary voltage case (a 2-hour battery, 50 kW and 100 kWh) reads USD 4,326 a year instead of 8,931
(-51.6 percent), its third case 25,956 instead of 53,286 (-51.3 percent); a 4-hour battery's year does not move (Seattle
City Light's medium city case, USD 12,795 either way).

    python -m unittest tests.test_alt_battery_customer_1 -v
"""

import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")


class TheStartingValue(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        p = subprocess.run(["node", "--import", "./scripts/tsx-register.mjs", "scripts/alt-battery-customer-figures.mjs"], cwd=SITE, capture_output=True, text=True, timeout=300)
        if p.returncode != 0:
            raise AssertionError(p.stderr[-2000:])
        cls.f = json.loads(p.stdout)

    def test_the_field_starts_at_4_hours(self):
        self.assertEqual(self.f["start"], "4")

    def test_a_two_hour_battery_left_at_the_start(self):
        self.assertEqual((round(self.f["austin-sv2"]["typed"]), round(self.f["austin-sv2"]["at_start"])), (8931, 4326))
        self.assertEqual((round(self.f["austin-sv3"]["typed"]), round(self.f["austin-sv3"]["at_start"])), (53286, 25956))

    def test_a_four_hour_battery_does_not_move(self):
        for cid, year in (("seattle-md-city-tou", 12795), ("seattle-lg-city", 62059), ("sce-tou-gs-2-b-2013-summer", 44124)):
            self.assertEqual(round(self.f[cid]["at_start"]), year, cid)

    def test_the_decision_names_its_source(self):
        with open(os.path.join(SITE, "app", "battery", "customer", "Decisions.tsx"), encoding="utf-8") as f:
            s = f.read()
        self.assertIn('def: "4 hours (2 hours on the site).",', s)
        self.assertIn("Seattle City Light's peak-rate hours, 5 p.m. to 9 p.m.", s)


if __name__ == "__main__":
    unittest.main()
