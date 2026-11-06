"""Session 1618 (chain 165): the board's file, measured against its budget.

Held here: the builder's figures for every row of the site's file, made again from each row's own series file with
this chain's stats() (the YTD move, the twelve-month mean, the 90-day trend), keep board.json within the budget the
method note sets for a file that is not paged: 2.5 MB as written, 400 KB compressed. A build that would pass it is a
decision for the note, not a quiet growth. No network, no model. Nothing here sets the environment at import.
"""
import datetime as dt
import gzip
import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DERIVED = os.path.join(ROOT, "warehouse", "derived")
SITE = os.path.join(ROOT, "site")
BUDGET_RAW, BUDGET_GZIP = 2_500_000, 400_000


def builder():
    if DERIVED not in sys.path:
        sys.path.insert(0, DERIVED)
    import board_page  # noqa: E402
    return board_page


class TheBudget(unittest.TestCase):
    def test_the_file_with_this_chains_figures_stays_in_budget(self):
        bp = builder()
        with open(os.path.join(SITE, "data", "board.json"), encoding="utf-8") as f:
            board = json.load(f)
        redone = 0
        for r in board["rows"]:
            if r.get("status") != "ok" or r.get("freq") not in ("D", "W", "M", "Q"):
                continue
            p = os.path.join(SITE, "public", "board", "s", r["id"] + ".json")
            if not os.path.exists(p):
                continue
            with open(p, encoding="utf-8") as f:
                s = json.load(f)
            d0 = dt.date.fromisoformat(s["t0"])
            r.update(bp.stats({d0 + dt.timedelta(days=d): v for d, v in zip(s["d"], s["v"])}, r["freq"]))
            redone += 1
        if redone < 500:
            raise unittest.SkipTest(f"the site's series files are not in this copy ({redone} rows)")
        raw = json.dumps(board, separators=(",", ":")).encode("utf-8")
        self.assertLess(len(raw), BUDGET_RAW, len(raw))
        self.assertLess(len(gzip.compress(raw, 9)), BUDGET_GZIP)
        self.assertTrue(all(len(r["spark"]["v"]) <= bp.SPARK_POINTS for r in board["rows"] if r.get("spark")))


if __name__ == "__main__":
    unittest.main()
