"""Ruling alternative 4 of /battery/customer (session 7704, 17 November 2026, branch wip/alt-battery-customer-4; not a
default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-battery-customer-2026-11-17.md, line 4): should
the energy moved each day be capped by the building's use in the peak-rate hours? On this branch it is capped at the peak
kW times the peak hours (site/lib/customerbattery.ts saving: capped, capKwh), the most a building that never draws over
its peak can take. Pinned with the page's own arithmetic (site/scripts/alt-battery-customer-figures.mjs): no published
case moves (no battery there is larger than its cap); the faults file's oversized case (a 50 kW peak, a 200 kW and 800
kWh battery, the browser proof's rates) reads "From shifting energy" USD 502.12 a month instead of 2,008.47 (-75.0
percent) and "Saved a year" USD 16,825.41 instead of 34,901.65 (-51.8 percent).

    python -m unittest tests.test_alt_battery_customer_4 -v
"""

import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")


class TheCap(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        p = subprocess.run(["node", "--import", "./scripts/tsx-register.mjs", "scripts/alt-battery-customer-figures.mjs"], cwd=SITE, capture_output=True, text=True, timeout=300)
        if p.returncode != 0:
            raise AssertionError(p.stderr[-2000:])
        cls.f = json.loads(p.stdout)

    def test_the_oversized_case(self):
        o = self.f["oversized"]
        self.assertEqual((o["capped"], o["cap"]), (True, 200))
        self.assertEqual((round(o["energy"], 2), round(o["year"], 2)), (502.12, 16825.41))

    def test_no_published_case_moves(self):
        for cid, c in self.f.items():
            if cid != "oversized" and c is not None:
                self.assertFalse(c["capped"], cid)
        self.assertEqual(round(self.f["seattle-md-city-tou"]["year"], 2), 12795.06)


if __name__ == "__main__":
    unittest.main()
