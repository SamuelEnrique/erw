"""Ruling alternative 4 of /prices (session 7723, 17 November 2026, branch wip/alt-prices-4; not a default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-prices-2026-11-17.md, line 4): name SPP's
real-time table in the site's market file? On this branch site/data/markets.json names it (iso_rtm_hub_prices, market
spp_rtm, variable lmp_rtm_15m_mean, every fifteen minutes): SPP's hub pages draw a real-time history and a real time
less day-ahead line, and every reader of the file that prefers real time (/network's SPP price) moves from day-ahead to
real time. Pinned with the page's own library (realLessDayAhead) on the local public tables where they are on the
machine, over the impact file's rolling 30 days: SPP North over the 360 hours both hold, real time less day-ahead -2.21
USD/MWh on average (day-ahead 28.33, real time 26.13: -7.8 percent), from -61.48 to +177.51; SPP South -0.62 (20.68
against 20.06), from -40.25 to +82.62; each hub gains 768 hours of real-time history (24 September to 13 November 2026).

    python -m unittest tests.test_alt_prices_4 -v
"""

import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
TABLES = os.environ.get("ERW_TABLES_DIR") or os.path.join(ROOT, "warehouse", "output")


class TheMarketFile(unittest.TestCase):
    def test_spp_names_its_real_time_table(self):
        with open(os.path.join(SITE, "data", "markets.json"), encoding="utf-8") as fh:
            m = json.load(fh)
        spp = next(x for x in m["isos"] if x["iso"] == "SPP")
        self.assertEqual(spp["rt"], {"table": "iso_rtm_hub_prices", "variable": "lmp_rtm_15m_mean", "freq": "PT15M", "market": "spp_rtm"})
        self.assertIn("wip/alt-prices-4", m["_about"])


@unittest.skipUnless(all(os.path.exists(os.path.join(TABLES, f"{t}.csv")) for t in ("iso_dam_hub_prices", "iso_rtm_hub_prices")), "the hub price tables are not on this machine")
class OnTheLocalTables(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        p = subprocess.run(["node", "--import", "./scripts/tsx-register.mjs", "scripts/alt-prices-figures.mjs", TABLES], cwd=SITE, capture_output=True, text=True, timeout=300)
        if p.returncode != 0:
            raise AssertionError(p.stderr[-2000:])
        cls.f = json.loads(p.stdout)

    def test_spp_north(self):
        g = self.f["spp:SPPNORTH_HUB"]
        self.assertEqual((g["both"], round(g["mean_rt_less_da"], 2), round(g["min"], 2), round(g["max"], 2), g["rt_hours_held"]), (360, -2.21, -61.48, 177.51, 768))

    def test_spp_south(self):
        g = self.f["spp:SPPSOUTH_HUB"]
        self.assertEqual((g["both"], round(g["mean_rt_less_da"], 2), round(g["min"], 2), round(g["max"], 2)), (360, -0.62, -40.25, 82.62))


if __name__ == "__main__":
    unittest.main()
