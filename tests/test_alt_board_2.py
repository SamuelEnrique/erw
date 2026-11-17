"""Ruling alternative 2 of /board (session 7722, 17 November 2026, branch wip/alt-board-2; not a default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-board-2026-11-17.md, line 2): on a row marked
stale, blank the 7-day and 30-day averages and the 30-day low to high too? On main they are drawn, each stating its days
on hover. On this branch they read "stale", as the moves and the 12-month average already do (site/lib/board.ts
windowsShown; site/components/board/BoardView.tsx). Pinned with the board's own library on its committed file
(site/data/board.json, built 17 November 2026; site/scripts/alt-board-figures.mjs): 116 rows past their stale age draw a
7-day average, and their 464 window figures (the two averages, the 30-day low and the high) go blank; 157 fresh rows keep
theirs. No held value is read or printed.

    python -m unittest tests.test_alt_board_2 -v
"""

import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")


class StaleWindows(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        p = subprocess.run(["node", "--import", "./scripts/tsx-register.mjs", "scripts/alt-board-figures.mjs"], cwd=SITE, capture_output=True, text=True, timeout=300)
        if p.returncode != 0:
            raise AssertionError(p.stderr[-2000:])
        cls.f = json.loads(p.stdout)

    def test_on_the_committed_file(self):
        f = self.f
        self.assertEqual((f["rows"], f["ok"]), (1315, 1204))
        self.assertEqual((f["stale_with_avg7"], f["cells_blanked"], f["fresh_drawn"]), (116, 464, 157))

    def test_the_view_blanks_them(self):
        with open(os.path.join(SITE, "components", "board", "BoardView.tsx"), encoding="utf-8") as fh:
            s = fh.read()
        for cell in ("row.avg7 ? staleCell", "row.avg30 ? staleCell", "row.lo30 !== undefined ? (!windowsShown(row, file.built) ? staleCell"):
            self.assertIn(cell, s)


if __name__ == "__main__":
    unittest.main()
