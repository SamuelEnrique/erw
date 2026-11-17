"""Ruling alternative 3 of /prices (session 7723, 17 November 2026, branch wip/alt-prices-3; not a default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-prices-2026-11-17.md, line 3): a second hub (A and
B) and A less B over the hours both hold, such as ERCOT West less Houston? On this branch /prices/<hub> takes ?b= (a hub of
the same grid) and draws, under its table, A less B for real time and day-ahead over the hours both hold whole
(site/lib/pricehub.ts hubLessHub): count, low, mean, median, high and the hours A was below B. No figure that stands moves.
Pinned with the page's own library on the local public tables, over the impact file's rolling 30 days: ERCOT West less
Houston, real time over 598 hours mean +1.14 USD/MWh, median 0.00, from -217.67 (2 November, 22:00 UTC) to +407.81 (12
November, 03:00 UTC), West below Houston in 297 hours; day-ahead over 672 hours mean +0.14, median +1.22, -51.48 to +50.08.

    python -m unittest tests.test_alt_prices_3 -v
"""

import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
TABLES = os.environ.get("ERW_TABLES_DIR") or os.path.join(ROOT, "warehouse", "output")


@unittest.skipUnless(all(os.path.exists(os.path.join(TABLES, f"{t}.csv")) for t in ("iso_dam_hub_prices", "iso_rtm_hub_prices")), "the hub price tables are not on this machine")
class WestLessHouston(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        p = subprocess.run(["node", "--import", "./scripts/tsx-register.mjs", "scripts/alt-prices-figures.mjs", TABLES], cwd=SITE, capture_output=True, text=True, timeout=300)
        if p.returncode != 0:
            raise AssertionError(p.stderr[-2000:])
        cls.f = json.loads(p.stdout)

    def test_real_time(self):
        r = self.f["rt"]
        self.assertEqual((r["n"], round(r["mean"], 2), round(r["median"], 2), round(r["min"], 2), r["minAt"], round(r["max"], 2), r["maxAt"], r["below"]),
                         (598, 1.14, 0.0, -217.67, "2026-11-02T22:00:00Z", 407.82, "2026-11-12T03:00:00Z", 297))   # 407.815 exactly: the impact file prints 407.81

    def test_day_ahead(self):
        d = self.f["da"]
        self.assertEqual((d["n"], round(d["mean"], 2), round(d["median"], 2), round(d["min"], 2), round(d["max"], 2)), (672, 0.14, 1.22, -51.48, 50.08))


class ThePage(unittest.TestCase):
    def test_the_page_takes_a_second_hub(self):
        with open(os.path.join(SITE, "app", "prices", "[entity]", "page.tsx"), encoding="utf-8") as fh:
            s = fh.read()
        self.assertIn("hubLessHub(rtRows, bRt.data, m.rt.freq)", s)
        self.assertIn('data-ab-mean={market}', s)


if __name__ == "__main__":
    unittest.main()
