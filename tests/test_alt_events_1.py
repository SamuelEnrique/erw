"""Ruling alternative 1 of /events (session 7712, 17 November 2026, branch wip/alt-events-1; not a default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-events-2026-11-17.md, line 1): EIA-930's figures
are drawn "license needed" by the hold on ISO-NE, MISO and NYISO because an EIA-930 entity names no grid, so a table held
by grid (event_window_daily) holds them all. Show them by (a) naming EIA-930's entities to their grids, (b) reading them
as rows of no grid, or (c) as now? This branch builds (a): site/lib/license.ts gridOfEntity names eia930:CISO to CAISO,
eia930:ISNE to ISO-NE and so on, an EIA-930 entity of no grid (the Lower 48) is a row of no grid, and
components/Num.tsx heldBy reads it so; warehouse/chat/license_hold.py grid_of_entity follows. (b) would show the held
grids' own figures and is not built: a license hold is never worked around.

Pinned with the site's own code on the replication's file of the ten pages' 1,100 figures
(site/scripts/alt-events-figures.mjs): main holds 1,041 of them (every EIA-930 figure); the other choice holds the 133
of ISO-NE, MISO and NYISO and draws the 908 of CAISO, ERCOT, PJM, SPP and the Lower 48, the index card's CAISO peak
(51,104 MW on 6 September 2022) among them. ERCOT's and SPP's own prices (59) are drawn either way.

    python -m unittest tests.test_alt_events_1 -v
"""

import json
import os
import subprocess
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
sys.path.insert(0, os.path.join(ROOT, "warehouse", "chat"))


class TheHold(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        p = subprocess.run(["node", "--import", "./scripts/tsx-register.mjs", "scripts/alt-events-figures.mjs"], cwd=SITE, capture_output=True, text=True, timeout=300)
        if p.returncode != 0:
            raise AssertionError(p.stderr[-2000:])
        cls.f = json.loads(p.stdout)

    def test_the_ten_pages(self):
        f = self.f
        self.assertEqual((f["figures"], f["held"], f["drawn"]), (1100, 133, 967))
        self.assertEqual(f["byKind"], {"ercot_own": {"held": 0, "drawn": 53}, "eia930_other": {"held": 0, "drawn": 908},
                                       "eia930_held_grid": {"held": 133, "drawn": 0}, "spp_own": {"held": 0, "drawn": 6}})

    def test_the_index_cards_caiso_peak(self):
        self.assertEqual(self.f["caiso"], {"shown": "51,104", "held": False})

    def test_the_python_loop_names_the_same_grids(self):
        import license_hold as hold
        self.assertEqual([hold.grid_of_entity(e) for e in ("eia930:CISO", "eia930:ERCO", "eia930:ISNE", "eia930:NYIS", "eia930:MISO", "eia930:US48", "eia930:BPAT")],
                         ["caiso", "ercot", "isone", "nyiso", "miso", "", ""])


if __name__ == "__main__":
    unittest.main()
