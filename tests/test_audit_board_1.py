"""Audit of the price board, finding 1 (session 10206, docs/reviews/board-model-audit-2026-11-26.md): the page keeper
(warehouse/derived/page_keep.py) keeps a row from an earlier build when the new build's history is shorter, even when
the new build's values are newer. On the board of 25 November 2026 ERCOT Hub average's day-ahead row (a tile of the top
twelve) reads 16.18 USD/MWh on 20 November, marked stale, while the week table of the same file reads 46.31 on
25 November as "Day-ahead, latest"; 98 public rows are marked stale that the new build held current.

A figure would move if the rule changed, so this branch carries the test only and is not for landing.
1. The rule: a newer but shorter build loses to the held row. Passes on main.
2. On the file of 25 November (skipped on any other build): the kept ERCOT row is older than the week table's day-ahead
   for the same hub, is past the board's 3 days, and carries the keeper's mark that a newer value was held."""
import datetime as dt
import json
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
import page_keep as pk  # noqa: E402


class KeptRowsAreOlderThanTheFile(unittest.TestCase):
    def test_a_newer_shorter_build_loses_to_the_held_row(self):
        old = {"status": "ok", "last": {"t": "2026-11-20", "v": 16.1825}}
        new = {"status": "ok", "last": {"t": "2026-11-25", "v": 46.3104}}
        side, why = pk.choose(old, new, 2879, 90)
        self.assertEqual(side, "old")
        self.assertIn("shorter", why)

    def test_on_the_file_of_25_november_the_tile_is_older_than_the_week_table(self):
        with open(os.path.join(ROOT, "site", "data", "board.json"), encoding="utf-8") as f:
            b = json.load(f)
        if not b["built"].startswith("2026-11-25"):
            self.skipTest(f"the measured file was built on 25 November 2026; this one {b['built']}")
        built = dt.date.fromisoformat(b["built"][:10])
        row = next(r for r in b["rows"] if r["id"] == "ercot-hb-hubavg-da")
        week = next(w for w in b["week"] if w["hub"] == "ercot-hb-hubavg")
        self.assertEqual((row["last"]["t"], row["last"]["v"]), ("2026-11-20", 16.1825))
        self.assertEqual((week["last_da"]["t"], round(week["last_da"]["v"], 2)), ("2026-11-25", 46.31))
        self.assertGreater((built - dt.date.fromisoformat(row["last"]["t"])).days, 3)        # stale on the page
        self.assertGreater(row["held"]["newest"], row["last"]["t"])                           # a newer value was held
        # every public row the keeper kept with a newer value, marked stale though the new build's newest is not
        power = {"power", "peak", "spark", "da_rt", "battery", "as", "hubspread"}
        limit = {"D": 10, "W": 17, "M": 132, "Q": 135}
        n = 0
        for r in b["rows"]:
            if r.get("status") != "ok" or "held" not in r or r["id"].startswith(("nyiso", "isone", "miso", "pjm")):
                continue
            lim = 3 if r["freq"] == "D" and r["group"] in power else limit[r["freq"]]
            last, newest = dt.date.fromisoformat(r["last"]["t"]), dt.date.fromisoformat(r["held"]["newest"][:10])
            if newest > last and (built - last).days > lim and (built - newest).days <= lim:
                n += 1
        self.assertEqual(n, 98)


if __name__ == "__main__":
    unittest.main()
