"""Session 478: page_keep.py keeps a held board row when the new build's is shorter; on 20 October 2026 the ERCOT tiles
were held at 15 October while the other grids read 20 October, all with status "ok". A held row two or more days behind
the newest of its group and frequency is now marked held = {since, newest, why}; its status stays "ok", so the site
(site/lib/board.ts, which keeps only rows with status "ok") shows it as before until it reads the mark."""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
import page_keep as pk  # noqa: E402


def row(rid, day, freq="D", group="power", status="ok"):
    return {"id": rid, "group": group, "freq": freq, "status": status, "last": {"t": day, "v": 1.0}, "source": 0}


def body(rows):
    return {"groups": [{"id": "power"}, {"id": "gas"}], "sources": ["s"], "rows": rows}


class Held(unittest.TestCase):
    def merge(self, old_rows, new_rows, points_old, points_new):
        return pk.merge_rows(body(old_rows), body(new_rows), lambda i: points_old.get(i), lambda i: points_new.get(i), lambda s: None)

    def test_a_held_row_days_behind_its_group_is_marked_and_stays_ok(self):
        old = [row("ercot-da", "2026-10-15"), row("caiso-da", "2026-10-15")]
        new = [row("ercot-da", "2026-10-20"), row("caiso-da", "2026-10-20")]
        rows, _, kept, _ = self.merge(old, new, {"ercot-da": 365, "caiso-da": 365}, {"ercot-da": 30, "caiso-da": 365})
        by = {r["id"]: r for r in rows}
        self.assertEqual([k for k, _ in kept], ["ercot-da"])
        self.assertEqual(by["ercot-da"]["status"], "ok")
        self.assertEqual(by["ercot-da"]["held"]["since"], "2026-10-15")
        self.assertEqual(by["ercot-da"]["held"]["newest"], "2026-10-20")
        self.assertIn("shorter", by["ercot-da"]["held"]["why"])
        self.assertNotIn("held", by["caiso-da"])

    def test_a_day_behind_is_not_marked(self):
        old = [row("ercot-da", "2026-10-19"), row("caiso-da", "2026-10-19")]
        new = [row("ercot-da", "2026-10-20"), row("caiso-da", "2026-10-20")]
        rows, _, _, _ = self.merge(old, new, {"ercot-da": 365}, {"ercot-da": 30})
        self.assertNotIn("held", {r["id"]: r for r in rows}["ercot-da"])

    def test_another_frequency_is_not_the_measure(self):
        old = [row("rgg-q", "2026-09-01", freq="Q"), row("caiso-da", "2026-10-20")]
        new = [row("rgg-q", "2026-09-01", freq="Q"), row("caiso-da", "2026-10-20")]
        rows, _, _, _ = self.merge(old, new, {"rgg-q": 40}, {"rgg-q": 10})
        self.assertNotIn("held", {r["id"]: r for r in rows}["rgg-q"])

    def test_a_row_taken_new_loses_an_old_mark(self):
        old = [dict(row("ercot-da", "2026-10-15"), held={"since": "2026-10-15", "newest": "2026-10-20", "why": "x"}),
               row("caiso-da", "2026-10-21")]
        new = [row("ercot-da", "2026-10-21"), row("caiso-da", "2026-10-21")]
        rows, _, kept, _ = self.merge(old, new, {"ercot-da": 365}, {"ercot-da": 365})
        self.assertEqual(kept, [])
        self.assertNotIn("held", {r["id"]: r for r in rows}["ercot-da"])

    def test_a_held_row_still_counts_as_held_next_time(self):
        # its status stays "ok", so choose() keeps judging it by its days and its history, as before
        marked = dict(row("ercot-da", "2026-10-15"), held={"since": "2026-10-15", "newest": "2026-10-20", "why": "x"})
        self.assertEqual(pk.choose(marked, row("ercot-da", "2026-10-20"), 365, 30)[0], "old")


if __name__ == "__main__":
    unittest.main()
