"""Ruling alternative 1 of /prices (session 7723, 17 November 2026, branch wip/alt-prices-1; not a default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-prices-2026-11-17.md, line 1): split a hub's
table into on-peak and off-peak hours, as the price board does? On this branch each market's row of /prices/<hub> is
followed by an on-peak row (06:00 to 22:00 local, Monday to Friday) and an off-peak row, with their count, low, mean and
high (site/lib/pricehub.ts splitPeak). Pinned with the page's own library on the local public tables where they are on
the machine (warehouse/output, or the folder ERW_TABLES_DIR names), over the impact file's rolling 30 days (to the newest
real-time hour, 13 November 2026 07:00 UTC): day-ahead SPP North 30.29 becomes 39.10 on-peak (+29.1 percent) and 20.79
off-peak; SPP South 22.85 to 30.23 and 14.91; ERCOT Houston 36.15 to 39.42 and 32.56; CAISO SP15 41.95 to 37.31 on-peak
and 47.04 off-peak (the solar day: on-peak is the cheaper).

    python -m unittest tests.test_alt_prices_1 -v
"""

import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
TABLES = os.environ.get("ERW_TABLES_DIR") or os.path.join(ROOT, "warehouse", "output")


@unittest.skipUnless(all(os.path.exists(os.path.join(TABLES, f"{t}.csv")) for t in ("iso_dam_hub_prices", "iso_rtm_hub_prices")), "the hub price tables are not on this machine")
class OnPeakAndOffPeak(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        p = subprocess.run(["node", "--import", "./scripts/tsx-register.mjs", "scripts/alt-prices-figures.mjs", TABLES], cwd=SITE, capture_output=True, text=True, timeout=300)
        if p.returncode != 0:
            raise AssertionError(p.stderr[-2000:])
        cls.f = json.loads(p.stdout)

    def test_the_window(self):
        self.assertEqual(self.f["newest_rt_hour"], "2026-11-13T07")

    def test_day_ahead(self):
        for e, all_, on, off in (("spp:SPPNORTH_HUB", 30.29, 39.10, 20.79), ("spp:SPPSOUTH_HUB", 22.85, 30.23, 14.91),
                                 ("ercot:HB_HOUSTON", 36.15, 39.42, 32.56), ("caiso:TH_SP15_GEN-APND", 41.95, 37.31, 47.04)):
            g = self.f[e]
            self.assertEqual((round(g["all"], 2), round(g["on"], 2), round(g["off"], 2)), (all_, on, off), e)


class ThePage(unittest.TestCase):
    def test_the_page_draws_the_rows(self):
        with open(os.path.join(SITE, "app", "prices", "[entity]", "page.tsx"), encoding="utf-8") as fh:
            s = fh.read()
        self.assertIn("pk: splitPeak(daRows, m.iso)", s)
        self.assertIn("data-peak-mean=", s)


if __name__ == "__main__":
    unittest.main()
