"""Ruling alternative 3 of /battery/customer (session 7704, 17 November 2026, branch wip/alt-battery-customer-3; not a
default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-battery-customer-2026-11-17.md, line 3): "From
shaving the peak" takes the battery's whole power off every month's peak; should it apply NREL's about 85 percent
(Neubauer and Simpson, NREL/TP-5400-63162, January 2015, pages 9 and 16)? On this branch 85 percent of the kW the battery
could take reaches the bill (site/lib/customerbattery.ts SHAVE_SHARE; the replication and its do-file follow). Pinned with
the page's own arithmetic on the published cases (site/scripts/alt-battery-customer-figures.mjs): "From shaving the peak"
falls 15 percent in every case; "Saved a year": Austin Energy secondary voltage USD 8,931.16 to 7,549.66 (-15.5 percent),
SCE 2013 44,123.70 to 38,698.50 (-12.3 percent), Seattle City Light medium city 12,795.06 to 11,830.26 (-7.5 percent).

    python -m unittest tests.test_alt_battery_customer_3 -v
"""

import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")


class TheShare(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        p = subprocess.run(["node", "--import", "./scripts/tsx-register.mjs", "scripts/alt-battery-customer-figures.mjs"], cwd=SITE, capture_output=True, text=True, timeout=300)
        if p.returncode != 0:
            raise AssertionError(p.stderr[-2000:])
        cls.f = json.loads(p.stdout)

    def test_the_share(self):
        self.assertEqual(self.f["share"], 0.85)

    def test_the_year_on_the_published_cases(self):
        for cid, year in (("austin-sv2", 7549.66), ("sce-tou-gs-2-b-2013-summer", 38698.50), ("seattle-md-city-tou", 11830.26), ("seattle-md-downtown-tou", 19538.69), ("austin-sv3", 45086.72)):
            self.assertEqual(round(self.f[cid]["year"], 2), year, cid)

    def test_from_the_peak_is_85_percent_in_every_case(self):
        for cid, demand in (("austin-sv2", 652.375), ("sce-tou-gs-2-b-2013-summer", 2561.90), ("seattle-md-city-tou", 455.60)):
            self.assertAlmostEqual(self.f[cid]["demand"], demand, places=6, msg=cid)


if __name__ == "__main__":
    unittest.main()
