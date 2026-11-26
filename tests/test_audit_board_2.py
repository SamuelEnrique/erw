"""Audit of the price board, finding 2 (session 10206, docs/reviews/board-model-audit-2026-11-26.md): the builder's week
table and spikes (warehouse/derived/board_page.py, build_week, from iso_trader_daily and iso_rt_top_intervals) are
written for every grid but MISO, the grids held for a license included, while every other part of the builder asks
ls.held_grids(). site/data/board.json, committed to the public repository, so holds NYISO's and ISO-NE's week lines
and spikes dated a month after the hold of 21 October 2026. The page drops them on the server (site/lib/board.ts,
holdRows), so no reader sees one on the page.

The fix is the builder's, run on the data machine (a data request): build_week writes no week line and no spike for a
grid in ls.held_grids(), as build_power already does for the hub rows. This branch carries the test only.
1. On the file of 25 November (skipped on any other build): held grids' week lines and spikes are in the file, dated
   after the hold. Only counts and dates are read; no value.
2. The page's hold drops them (holdRows filters week and spikes by the held grids). Passes on main.
3. build_week names no held grid. Passes on main: it is the fault."""
import json
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
HELD = ("nyiso", "isone")


class HeldWeekLinesInThePublicFile(unittest.TestCase):
    def test_the_file_holds_held_grids_week_lines_after_the_hold(self):
        with open(os.path.join(ROOT, "site", "data", "board.json"), encoding="utf-8") as f:
            b = json.load(f)
        if not b["built"].startswith("2026-11-25"):
            self.skipTest(f"the measured file was built on 25 November 2026; this one {b['built']}")
        week = [w for w in b["week"] if w["hub"].startswith(HELD)]
        spikes = [s for s in b["spikes"] if s["hub"].startswith(HELD)]
        self.assertEqual(len(week), 20)
        self.assertEqual(len(spikes), 20)
        self.assertTrue(all(w.get("last_da", {}).get("t", "") > "2026-10-21" for w in week))
        self.assertTrue(all(s["t"][:10] > "2026-10-21" for s in spikes))

    def test_the_page_drops_them_on_the_server(self):
        with open(os.path.join(ROOT, "site", "lib", "board.ts"), encoding="utf-8") as f:
            src = f.read()
        self.assertIn("week: file.week.filter((w) => !held.has(w.grid)), spikes: file.spikes.filter((x) => !held.has(x.grid))", src)
        with open(os.path.join(ROOT, "site", "app", "board", "page.tsx"), encoding="utf-8") as f:
            self.assertIn("holdRows(raw, licenseHeldGrids().map(gridName))", f.read())

    def test_build_week_asks_no_held_grid(self):
        with open(os.path.join(ROOT, "warehouse", "derived", "board_page.py"), encoding="utf-8") as f:
            src = f.read()
        body = re.search(r"\ndef build_week\(log\):(.*?)\n(?=\S)", src, re.S).group(1)
        self.assertNotIn("held_grids", body)
        self.assertIn("spikes = [dict(hub=slug(e)", body)


if __name__ == "__main__":
    unittest.main()
