"""The guard on the two scheduled page refreshes (warehouse/derived/page_keep.py, 6 October 2026): a scheduled build
never replaces a held row with a blank, an older or a shorter one, and a pause is never undone by a kept row."""
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
import page_keep as pk  # noqa: E402


def row(rid, status="ok", t="2026-10-05", source=0, group="g", **more):
    r = dict(id=rid, group=group, status=status, source=source, **more)
    if status == "ok":
        r["last"] = dict(t=t, v=1.0)
    return r


def body(rows, sources=("src a", "src b")):
    return dict(groups=[dict(id="g"), dict(id="h")], sources=list(sources), rows=rows)


class Choose(unittest.TestCase):
    def test_a_newer_row_of_the_same_length_is_taken(self):
        self.assertEqual(pk.choose(row("a", t="2026-10-04"), row("a", t="2026-10-05"), 100, 100)[0], "new")

    def test_an_equal_date_is_taken_so_revisions_arrive(self):
        self.assertEqual(pk.choose(row("a"), row("a"), 100, 100)[0], "new")

    def test_an_older_row_is_kept(self):
        self.assertEqual(pk.choose(row("a", t="2026-10-05"), row("a", t="2026-10-01"), 100, 100)[0], "old")

    def test_a_shorter_history_is_kept_out_and_a_rolling_day_is_not(self):
        self.assertEqual(pk.choose(row("a"), row("a"), 1000, 400)[0], "old")
        self.assertEqual(pk.choose(row("a"), row("a"), 1000, None)[0], "old")
        self.assertEqual(pk.choose(row("a"), row("a"), 1000, 990)[0], "new")

    def test_a_blank_never_replaces_a_value(self):
        for status in ("not_held", "working"):
            self.assertEqual(pk.choose(row("a"), row("a", status=status), 10, None)[0], "old", status)

    def test_a_pause_or_a_license_is_always_taken(self):
        for status in ("paused", "licensed"):
            self.assertEqual(pk.choose(row("a"), row("a", status=status), 10, None)[0], "new", status)

    def test_a_row_only_one_side_has(self):
        self.assertEqual(pk.choose(None, row("a"), None, 5)[0], "new")
        self.assertEqual(pk.choose(row("a"), None, 5, None)[0], "old")
        self.assertEqual(pk.choose(row("a", status="not_held"), row("a"), None, 5)[0], "new")


class Merge(unittest.TestCase):
    def merge(self, old, new, n_old=None, n_new=None):
        return pk.merge_rows(old, new, lambda i: (n_old or {}).get(i), lambda i: (n_new or {}).get(i), lambda s: None)

    def test_rows_are_whole_rows_of_one_build_and_sources_follow_them(self):
        old = body([row("a", t="2026-10-05", source=1, mark="held"), row("b", t="2026-10-01", source=0, mark="held")])
        new = body([row("a", status="working", source=None), row("b", t="2026-10-02", source=0, mark="built")], sources=("src c",))
        rows, sources, kept, taken = self.merge(old, new)
        by = {r["id"]: r for r in rows}
        self.assertEqual(by["a"]["mark"], "held")
        self.assertEqual(by["b"]["mark"], "built")
        self.assertEqual(sources[by["a"]["source"]], "src b")
        self.assertEqual(sources[by["b"]["source"]], "src c")
        self.assertEqual([k for k, _ in kept], ["a"])
        self.assertEqual(taken, ["b"])

    def test_a_row_that_left_the_build_stays_and_keeps_its_group(self):
        old = body([row("a", group="g"), row("z", group="h")])
        new = body([row("a", group="g")])
        rows, _, kept, _ = self.merge(old, new)
        self.assertEqual([r["id"] for r in rows], ["a", "z"])
        self.assertEqual(kept, [("z", "only the held file has it")])

    def test_a_first_build_takes_every_row(self):
        new = body([row("a"), row("b", status="paused", source=None)])
        rows, _, kept, taken = self.merge(dict(new, rows=[], sources=[]), new)
        self.assertEqual((len(rows), kept, taken), (2, [], ["a", "b"]))


class Scheduled(unittest.TestCase):
    def src(self, *parts):
        with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
            return f.read()

    def test_neither_refresh_reaches_a_builder_except_through_the_guard(self):
        board = self.src("warehouse", "refresh_board.sh")
        supply = self.src("warehouse", "refresh_supply.sh")
        code = lambda s: "\n".join(line for line in s.splitlines() if not line.lstrip().startswith("#"))
        self.assertNotIn("board_page.py", code(board))
        self.assertNotIn("supply_page.py", code(supply))
        self.assertIn("page_keep.py board", code(board))
        self.assertEqual(code(supply).count("page_keep.py supply"), 3)

    def test_the_mix_refresh_is_still_not_scheduled(self):
        self.assertNotIn("refresh_mix.sh", self.src("warehouse", "run_daily.sh"))


if __name__ == "__main__":
    unittest.main()
