"""Session 10219 (chain 710, the conditions audit, finding 11): each operator's line on /conditions said "days and hours
in America/Chicago clock time for days and hours", while every hourly chart labels its instants in UTC
(site/components/TimeChart.tsx, the "minute" axis); and "the newest 35 days" run from the build's UTC day less 35 days
to that day, 36 days whose last holds EIA's forecast but no demand. Words only: the line names each clock and, where the
window's last days carry the forecast only, the last day of demand. docs/reviews/conditions-model-audit-2026-11-26.md.
"""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DIR = os.path.join(ROOT, "site", "data", "conditions")


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as fh:
        return fh.read()


class TheLineNamesEachClock(unittest.TestCase):
    def test_hourly_axes_are_utc(self):
        self.assertIn('minute: (t) => new Date(t).toISOString().slice(0, 16).replace("T", " ") + " UTC"', src("site", "components", "TimeChart.tsx"))

    def test_the_line_says_utc_for_the_hourly_charts(self):
        s = src("site", "app", "conditions", "page.tsx")
        self.assertNotIn("days and hours in {f.time}", s)
        # session 10201: merged with chain 750's clockWords(), which names the files' clock once
        self.assertIn('{clockWords(f.time)} in the files, the hourly charts labelled in UTC.{demandEnds(f, daily, w.end)}', s)
        self.assertIn("EIA's demand is held to ${last}; the days after it carry the forecast only.", s)

    @unittest.skipUnless(os.path.exists(os.path.join(DIR, "ercot.json")), "the conditions files are not in this checkout")
    def test_the_case_the_words_cover(self):
        with open(os.path.join(DIR, "ercot.json"), encoding="utf-8") as fh:
            f = json.load(fh)
        self.assertTrue(f["time"].startswith("America/Chicago "))
        rec = [w for w in f["windows"] if w["id"] == "recent"][0]
        dc = f["daily_columns"]
        i, j = dc.index("demand_peak"), dc.index("forecast_peak")
        last = [r for r in f["daily"] if r[0] == rec["end"]][0]
        self.assertIsNone(last[i], "the window's last day holds no demand")
        self.assertIsNotNone(last[j], "but holds the forecast")


if __name__ == "__main__":
    unittest.main()
