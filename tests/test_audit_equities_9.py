"""Audit of /equities, finding 9 (session 11403, docs/reviews/equities-model-audit-2026-11-28.md): the method note's
first section, "What the files hold today", said the list holds "no company or index" and "no company, index or
segment file is written"; since 27 November the files hold 307 companies, 243 with filed statements, one series file
each. The page links this note as "the method note".

Also shown here (passes on main): the page's source line names two tables no machine has written,
equity_prices_daily and equity_index_daily (the builder's `tables` list): a data request, since the list is the data
machine's file.

1. The files hold the companies (passes on main).
2. The fix on this branch (fails on main): the note's first section says what changed on 27 November, and keeps the
   first build's words marked as such. No figure moves."""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
D = os.path.join(ROOT, "site", "data", "equities")
NOTE = os.path.join(ROOT, "docs", "methods", "equities.md")


class NoteToday(unittest.TestCase):
    def test_files_hold_companies(self):
        with open(os.path.join(D, "index.json"), encoding="utf-8") as f:
            idx = json.load(f)
        self.assertEqual(len(idx["companies"]), 307)
        self.assertEqual(sum(1 for c in idx["companies"] if c["fundamentals_status"] == "shown"), 243)
        self.assertTrue(all(os.path.exists(os.path.join(D, c["file"])) for c in idx["companies"]))
        # the source line's tables: two of them no machine has written
        self.assertIn("equity_prices_daily", idx["tables"])
        self.assertIn("equity_index_daily", idx["tables"])

    def test_note_says_what_changed(self):
        note = open(NOTE, encoding="utf-8").read()
        first = note.split("## What the files hold today", 1)[1].split("\n## ", 1)[0]
        self.assertIn("What changed on 27 November 2026", first)
        self.assertIn("307 companies", first)
        self.assertIn("(26 November 2026, the first build)", first)
        self.assertNotIn(chr(0x2014), note)


if __name__ == "__main__":
    unittest.main()
