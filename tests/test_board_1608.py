"""Session 1608 (chain 165): the moves, the year to date among them, and none on a stale row.

Held here: the builder's year-to-date move is against the last value held of the year before, when it is no older
than a step's slack before 31 December (daily, weekly, monthly, quarterly), and there is none when the year before ends
without one; the window's date is the move's own; the page draws a YTD column from the same list of moves as the
others; a stale row's moves are blank with its status, and scripts/check-board.mjs expects no number there. The series
here are made in memory to place dates around a year's end: they test the rule, they are no one's prices. No network,
no model. Nothing here sets the environment at import.
"""
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DERIVED = os.path.join(ROOT, "warehouse", "derived")
SITE = os.path.join(ROOT, "site")


def builder():
    if DERIVED not in sys.path:
        sys.path.insert(0, DERIVED)
    import board_page  # noqa: E402
    return board_page


D = dt.date


class TheYearToDate(unittest.TestCase):
    def test_daily_against_the_last_trading_day_of_the_year_before(self):
        bp = builder()
        s = {D(2025, 12, 29): 10.0, D(2025, 12, 30): 11.0, D(2026, 1, 2): 12.0, D(2026, 3, 2): 15.0}
        m = bp.stats(s, "D")["moves"]["ytd"]
        self.assertEqual((m["t"], m["v"], m["ch"]), ("2025-12-30", 11.0, 4.0))

    def test_none_when_the_year_before_ends_too_early(self):
        bp = builder()
        s = {D(2025, 12, 20): 10.0, D(2026, 3, 2): 15.0}                  # 11 days before 31 December: past the 6 days' slack
        self.assertIsNone(bp.stats(s, "D")["moves"]["ytd"])
        self.assertIsNone(bp.stats({D(2026, 3, 2): 15.0}, "D")["moves"]["ytd"])

    def test_weekly_monthly_quarterly(self):
        bp = builder()
        w = bp.stats({D(2025, 12, 22): 5.0, D(2026, 2, 2): 6.0}, "W")["moves"]["ytd"]      # 9 days before: inside a week and six
        self.assertEqual((w["t"], w["ch"]), ("2025-12-22", 1.0))
        m = bp.stats({D(2025, 11, 1): 1.0, D(2025, 12, 1): 2.0, D(2026, 8, 1): 5.0}, "M")["moves"]["ytd"]
        self.assertEqual((m["t"], m["ch"]), ("2025-12-01", 3.0))
        self.assertIsNone(bp.stats({D(2025, 11, 1): 1.0, D(2026, 8, 1): 5.0}, "M")["moves"]["ytd"])
        q = bp.stats({D(2025, 11, 1): 30.0, D(2026, 8, 1): 31.5}, "Q")["moves"]["ytd"]
        self.assertEqual((q["t"], q["ch"]), ("2025-11-01", 1.5))
        self.assertEqual(set(bp.stats({D(2026, 8, 1): 1.0}, "M")["moves"]), {"d", "w", "m", "y", "ytd"})


class ThePage(unittest.TestCase):
    def test_the_column_and_the_stale_rows(self):
        exe = shutil.which("node")
        if not exe or not os.path.isdir(os.path.join(SITE, "node_modules")):
            raise unittest.SkipTest("node or the site's packages are not here")
        script = ("const b = await import('./lib/board.ts');"
                  "const mv = { t: '2025-12-30', v: 11, ch: 4, pct: 36.4 };"
                  "const fresh = { id: 'x', group: 'gas', freq: 'D', last: { t: '2026-10-20', v: 15 }, moves: { ytd: mv } };"
                  "const old = { ...fresh, last: { t: '2026-09-01', v: 15 } };"
                  "process.stdout.write(JSON.stringify({ keys: b.MOVES.map(([k]) => k), heads: b.MOVES.map(([, n]) => n), q: b.noMove('Q', 'ytd'),"
                  " fresh: b.shownMove(fresh, 'ytd', '2026-10-23T00:00:00Z'), old: b.shownMove(old, 'ytd', '2026-10-23T00:00:00Z'), none: b.shownMove(fresh, 'd', '2026-10-23T00:00:00Z') }));")
        r = subprocess.run([exe, "--import", "./scripts/alias-register.mjs", "--input-type=module", "-e", script], cwd=SITE,
                           capture_output=True, text=True, timeout=300, encoding="utf-8")
        if r.returncode != 0 and "Unknown file extension" in r.stderr:
            raise unittest.SkipTest("this node does not read TypeScript files")
        self.assertEqual(r.returncode, 0, r.stderr)
        got = json.loads(r.stdout)
        self.assertEqual(got["keys"], ["d", "w", "m", "y", "ytd"])
        self.assertEqual(got["heads"][-1], "YTD")
        self.assertFalse(got["q"])
        self.assertEqual(got["fresh"]["ch"], 4)
        self.assertIsNone(got["old"])          # 52 days before the build: stale, so blank
        self.assertIsNone(got["none"])

    def test_the_wiring(self):
        with open(os.path.join(SITE, "components", "board", "BoardView.tsx"), encoding="utf-8") as f:
            v = f.read()
        self.assertEqual(v.count("const cols = 7 + MOVES.length + (group.curve ? 1 : 0);"), 2)
        self.assertIn("<MoveCell row={row} k={k} built={file.built} />", v)
        self.assertIn(">stale</span>", v)
        for name in ("check-board.mjs", "check-board-v4.mjs"):
            with open(os.path.join(SITE, "scripts", name), encoding="utf-8") as f:
                self.assertIn("const mv = b.shownMove(r, k, file.built);", f.read(), name)


if __name__ == "__main__":
    unittest.main()
