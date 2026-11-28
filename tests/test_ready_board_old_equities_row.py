"""Ready branch for the price board (session 11408, chain 770 part C; weekend page 2026-11-28, part 3.5, "the board's
older 'Energy equities' row: keep until a first price is shown, or remove": the other choice). Not the default: it
waits for Samuel's ruling.

warehouse/derived/board_page.py no longer writes the row (id "equities", group "other", "licensed"), and
warehouse/derived/page_keep.py RETIRED drops it although the held board.json still holds it (rule 4 would keep it).
Measured with page_keep's own merge on the board.json now on main against a build without the row: the board's rows
one fewer, the row gone, every other row as it was. site/data/board.json rebuilt at landing by the desk.

1. The builder writes no such row; RETIRED names it.
2. merge_rows on the real board.json: the held row is dropped, nothing else moves."""
import json
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
import page_keep as pk  # noqa: E402


class TheOlderRowIsRetired(unittest.TestCase):
    def test_the_builder_and_the_list(self):
        with open(os.path.join(ROOT, "warehouse", "derived", "board_page.py"), encoding="utf-8") as f:
            src = f.read()
        self.assertNotIn('b.grey("other", "equities", "Energy equities"', src)
        self.assertIn("equities", pk.RETIRED)

    def test_the_merge_drops_it(self):
        with open(os.path.join(ROOT, "site", "data", "board.json"), encoding="utf-8") as f:
            old = json.load(f)
        if not any(r["id"] == "equities" for r in old["rows"]):
            self.skipTest("the board's file no longer holds the row (rebuilt)")
        new = dict(old, rows=[r for r in old["rows"] if r["id"] != "equities"])
        rows, _sources, kept, _taken = pk.merge_rows(old, new, lambda rid: 0, lambda rid: 0, lambda s: None)
        ids = [r["id"] for r in rows]
        self.assertNotIn("equities", ids)
        self.assertEqual(len(ids), len(old["rows"]) - 1)
        self.assertNotIn("equities", dict(kept))
        self.assertEqual(sorted(ids), sorted(r["id"] for r in new["rows"]))


if __name__ == "__main__":
    unittest.main()
