"""Session 7549 (chain 304, part B): /events read as an operator's or a regulator's analyst
(docs/reviews/events-read-2026-11-16.md). The site fixes are held by site/scripts/test-events-read.mjs (the pages drawn
with the site's own code); this file holds the read's written part: its rows and counts, no em dash, and no figure or
entity of a license-held grid's rows (ISO-NE, MISO, NYISO: event_window_daily and event_study_estimates are held by grid)."""
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
READ = os.path.join(ROOT, "docs", "reviews", "events-read-2026-11-16.md")


def text():
    with open(READ, encoding="utf-8") as f:
        return f.read()


class TheRead(unittest.TestCase):
    def test_no_dashes(self):
        for p in (READ, os.path.join(ROOT, "site", "scripts", "test-events-read.mjs"), __file__):
            with open(p, encoding="utf-8") as f:
                self.assertNotIn(chr(0x2014), f.read(), p)

    def test_reader_and_five_cases_first(self):
        t = text()
        self.assertIn("**The reader:**", t.split("## ")[0])
        self.assertIn("**The five cases:**", t.split("## ")[0])
        for case in range(1, 6):
            self.assertRegex(t, rf"\n\| {case}\. ")

    def test_rows_and_counts(self):
        rows = re.findall(r"^\| (\d+) \| [^|]+ \| [^|]+ \| [^|]+ \| (site|data machine|browser|ruling) \| ", text(), re.M)
        self.assertEqual([int(n) for n, _ in rows], list(range(1, 16)))
        kinds = [k for _, k in rows]
        self.assertEqual((kinds.count("site"), kinds.count("data machine"), kinds.count("browser"), kinds.count("ruling")), (5, 0, 4, 6))
        self.assertIn("Site, fixed: 5 (rows 1, 2, 4, 5, 7). Data machine: 0. Browser: 4 (rows 12 to 15). Ruling: 6", text())

    def test_no_held_grid_row(self):
        # no entity of a held grid ("isone:", "miso:", "nyiso:", their queues, "iso:<grid>") and no hub name of theirs
        t = text()
        self.assertIsNone(re.search(r"\b(isone|miso|nyiso)(_load)?(_queue)?:|\biso:(isone|miso|nyiso)\b", t))  # entities are lower case; "NYISO:" in the hover's words is a name
        for hub in ("INDIANA.HUB", "N.Y.C.", ".H.INTERNAL_HUB"):
            self.assertNotIn(hub, t)


if __name__ == "__main__":
    unittest.main()
