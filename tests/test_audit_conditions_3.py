"""Session 10219 (chain 710, the conditions audit, finding 3): the alerts heading of /conditions counts rows of the
alerts list, and a row is one notice, region and day it covers, with each reissue of a CAISO notice listed again and
ERCOT's releases that end a notice or announce none among them. The August 2020 heat wave's "(79)" is 23 notices of
CAISO's (kind, start, end). Counting notices would move the figure, so the ruling is the owner's
(docs/reviews/conditions-model-audit-2026-11-26.md). These tests pass on main: they show the finding, not a fix.
"""
import csv
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DIR = os.path.join(ROOT, "site", "data", "conditions")
OUT = os.path.join(ROOT, "warehouse", "output")


def load(op):
    with open(os.path.join(DIR, op + ".json"), encoding="utf-8") as fh:
        return json.load(fh)


def window(f, wid):
    w = [x for x in f["windows"] if x["id"] == wid][0]
    return [a for a in f["alerts"] if w["start"] <= a[0] <= w["end"]]


@unittest.skipUnless(os.path.exists(os.path.join(DIR, "caiso.json")), "the conditions files are not in this checkout")
class TheHeadingCountsRows(unittest.TestCase):
    def test_the_page_counts_every_row_of_the_window(self):
        with open(os.path.join(ROOT, "site", "app", "conditions", "page.tsx"), encoding="utf-8") as fh:
            s = fh.read()
        self.assertIn("const alerts = f.alerts.filter((a) => a[0] >= w.start && a[0] <= w.end);", s)
        self.assertIn("({alerts.length})", s)

    def test_the_heat_wave_of_2020_is_79_rows_and_far_fewer_notices(self):
        rows = window(load("caiso"), "caiso_heat_2020")
        self.assertEqual(len(rows), 79)
        notices = {(a[1], a[2], a[3]) for a in rows}
        self.assertLessEqual(len(notices), 25)
        # the same notice, start and end printed four times on one day: CAISO's reissues
        day = [tuple(a[:4]) for a in rows if a[0] == "2020-08-14" and a[1] == "RMO"]
        self.assertEqual(len(day), 4)
        self.assertEqual(len(set(day)), 1)

    def test_uri_in_california_is_26_rows_of_3_notices(self):
        rows = window(load("caiso"), "uri_2021")
        self.assertEqual(len(rows), 26)
        self.assertEqual(len({(a[1], a[2], a[3]) for a in rows}), 3)

    @unittest.skipUnless(os.path.exists(os.path.join(OUT, "ercot_grid_notices.csv")), "ercot_grid_notices is not on this machine")
    def test_ercot_rows_include_releases_that_end_a_notice_or_announce_none(self):
        with open(os.path.join(OUT, "ercot_grid_notices.csv"), encoding="utf-8", newline="") as fh:
            rows = list(csv.DictReader(ln for ln in fh if not ln.startswith("#")))
        ended = [r for r in rows if r["event_type"] in ("update", "statement")]
        self.assertGreaterEqual(len(ended), 30)
        page_ids = {(a[0], a[1], a[4]) for a in load("ercot")["alerts"]}
        self.assertTrue(any((r["event_date"], r["x_label"], r["source_url"]) in page_ids for r in ended), "they reach the page's list")


if __name__ == "__main__":
    unittest.main()
