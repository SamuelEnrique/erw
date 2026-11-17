"""Ruling alternative 4 of /board (session 7722, 17 November 2026, branch wip/alt-board-4; not a default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-board-2026-11-17.md, line 4): the strip's
highest and lowest in their year's range from daily series only? On main any step can stand there; on this branch only a
daily series (site/lib/board.ts rangeExtremes, r.freq "D"), and the cells' hover says so. Pinned with the board's own
library on its committed file (site/data/board.json, built 17 November 2026; site/scripts/alt-board-figures.mjs): main,
30 candidates, highest the IMF's uranium price, October 2026's monthly average (72.89, position 1.000), lowest the IMF's
cobalt price (36,288.27, position 0.000); daily only, 21 candidates, highest the 2-year Treasury yield (4.86 percent on
12 November, position 0.961), lowest Henry Hub spot (USD 3.00 on 11 November, position 0.021). Both cells change.

    python -m unittest tests.test_alt_board_4 -v
"""

import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")


class DailyOnly(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        p = subprocess.run(["node", "--import", "./scripts/tsx-register.mjs", "scripts/alt-board-figures.mjs"], cwd=SITE, capture_output=True, text=True, timeout=300)
        if p.returncode != 0:
            raise AssertionError(p.stderr[-2000:])
        cls.f = json.loads(p.stdout)

    def test_main_rule(self):
        m = self.f["main"]
        self.assertEqual((m["candidates"], m["top"]["id"], round(m["top"]["v"], 2), m["top"]["pos"]), (30, "imf-pcps-puran", 72.89, 1))
        self.assertEqual((m["bottom"]["id"], round(m["bottom"]["v"], 2), m["bottom"]["pos"]), ("imf-pcps-pcoba", 36288.27, 0))

    def test_daily_only(self):
        b = self.f["branch"]
        self.assertEqual((b["candidates"], b["top"]["id"], b["top"]["v"], b["top"]["t"], round(b["top"]["pos"], 3)), (21, "fred-dgs2", 4.86, "2026-11-12", 0.961))
        self.assertEqual((b["bottom"]["id"], b["bottom"]["v"], b["bottom"]["t"], round(b["bottom"]["pos"], 3)), ("eia-henry-hub-spot", 3, "2026-11-11", 0.021))
        self.assertEqual({b["top"]["freq"], b["bottom"]["freq"]}, {"D"})


if __name__ == "__main__":
    unittest.main()
