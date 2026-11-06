"""Session 1621 (chain 165): the second read, part two: the keys the periodicals and Ask read from the board.

Held here: the Digest's day move (warehouse/news/brief.py day_move, which calls board_page.stats on a two-point series)
is the board's day move after this chain's changes to stats, and its own fallback formula agrees; every key Ask's board
panel reads from a row (the four moves, the range, the trend) is still written by the builder under the same name; this
chain added keys (ytd, avg365, ext, basis) and renamed none. No network, no model. Nothing here sets the environment at
import.
"""
import datetime as dt
import os
import re
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DERIVED = os.path.join(ROOT, "warehouse", "derived")
NEWS = os.path.join(ROOT, "warehouse", "news")
SITE = os.path.join(ROOT, "site")


def builder():
    if DERIVED not in sys.path:
        sys.path.insert(0, DERIVED)
    import board_page  # noqa: E402
    return board_page


class TheDigestsDayMove(unittest.TestCase):
    def test_brief_day_move_is_the_boards(self):
        if NEWS not in sys.path:
            sys.path.insert(0, NEWS)
        try:
            import brief  # noqa: E402
        except Exception as exc:                       # the model's client may be absent on a machine
            raise unittest.SkipTest(f"brief does not import here: {exc}")
        bp = builder()
        for newest, prev, gap in ((3.31, 3.18, 1), (-4.5, 10.0, 3), (12.0, -2.0, 1), (40.0, 40.0, 7)):
            d1 = dt.date(2026, 10, 20)
            d0 = d1 - dt.timedelta(days=gap)
            got = brief.day_move(newest, d1.isoformat(), prev, d0.isoformat())
            m = bp.stats({d0: prev, d1: newest})["moves"]["d"]
            self.assertEqual(got, {"ch": m["ch"], "pct": m["pct"]})
            self.assertEqual(got["ch"], round(newest - prev, 4))
            self.assertEqual(got["pct"], round(100 * (newest - prev) / prev, 2) if prev > 0 and newest >= 0 else None)
        self.assertEqual(bp.LICENSED, "licensed source needed")          # brief.py names it (its comment of the board's words)


class AsksKeys(unittest.TestCase):
    def test_every_key_the_panel_reads_is_written(self):
        with open(os.path.join(SITE, "lib", "chat", "panel.ts"), encoding="utf-8") as f:
            panel = f.read()
        for key in ('d: "change_on_the_day_before"', 'w: "change_on_a_week_before"', 'm: "change_on_a_month_before"', 'y: "change_on_a_year_before"',
                    "r.range.lo", "r.range.hi", "r.spark!.d", "r.last.t"):
            self.assertIn(key, panel)
        bp = builder()
        s = bp.stats({dt.date(2026, 1, 1) + dt.timedelta(days=i): float(i) for i in range(400)}, "D")
        self.assertTrue({"d", "w", "m", "y"} <= set(s["moves"]))
        for k in ("last", "range", "spark", "avg7", "avg30"):
            self.assertIn(k, s)
        self.assertEqual(set(s["spark"]), {"t0", "d", "v"})
        self.assertEqual(set(s["range"]), {"lo", "hi", "n", "pos"})

    def test_no_key_renamed(self):
        with open(os.path.join(DERIVED, "board_page.py"), encoding="utf-8") as f:
            src = f.read()
        out = re.search(r"out = dict\(last=dict\(t=d0\.isoformat\(\), v=round\(v0, 4\)\), moves=moves, range=rng\)", src)
        self.assertIsNotNone(out)
        self.assertIn('moves = {"d": move(prev), "w": move(back(7))', src)
        self.assertIn('"y": move(back(365)), "ytd": move(year_end(days, d0, freq))}', src)


if __name__ == "__main__":
    unittest.main()
