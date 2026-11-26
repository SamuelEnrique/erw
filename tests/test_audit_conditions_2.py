"""Session 10219 (chain 710, the conditions audit, finding 2): /conditions headed its alerts "Alerts and notices in
force (N)", where N counts rows and a row is one notice, region and day it covers, with CAISO's reissues listed again
and ERCOT's releases that end a notice or announce none among them. The August 2020 heat wave's 79 rows are 23 notices.
Words only: the heading says rows and a line says what a row is; the count is unchanged (counting notices is finding 3,
the owner's ruling). docs/reviews/conditions-model-audit-2026-11-26.md.
"""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DIR = os.path.join(ROOT, "site", "data", "conditions")


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as fh:
        return fh.read()


class TheHeadingSaysRows(unittest.TestCase):
    def test_the_page_no_longer_says_in_force(self):
        s = src("site", "app", "conditions", "page.tsx")
        self.assertNotIn("Alerts and notices in force", s)
        self.assertNotIn("the alerts in force", s)
        self.assertIn("Alerts and notices listed, {w.start} to {w.end} ({alerts.length} rows)", s)

    def test_a_line_says_what_a_row_is(self):
        s = src("site", "app", "conditions", "page.tsx")
        self.assertIn("data-alerts-rows={tag}>{ALERT_ROW_WORDS}", s)
        for w in ["one notice, region and day it covers", "reissued is listed again", "the region is not shown",
                  "end a notice or announce none", "the count is of rows, not of separate notices"]:
            self.assertIn(w, s)
        self.assertNotIn("export const ALERT_ROW_WORDS", s, "a page file exports only what Next allows")

    def test_the_note_says_it_too(self):
        n = src("docs", "methods", "grid_conditions.md")
        self.assertIn("one row for each notice, region and day it covers", n)
        self.assertNotIn("each notice with its date", n)

    @unittest.skipUnless(os.path.exists(os.path.join(DIR, "caiso.json")), "the conditions files are not in this checkout")
    def test_the_case_the_words_cover(self):
        with open(os.path.join(DIR, "caiso.json"), encoding="utf-8") as fh:
            f = json.load(fh)
        w = [x for x in f["windows"] if x["id"] == "caiso_heat_2020"][0]
        rows = [a for a in f["alerts"] if w["start"] <= a[0] <= w["end"]]
        self.assertEqual(len(rows), 79)
        self.assertLess(len({(a[1], a[2], a[3]) for a in rows}), 30)


if __name__ == "__main__":
    unittest.main()
