"""Chain 252 (sessions 3456 to 3471, 13 November 2026): the faults of the Digest of 13 November 2026 as stored, read as
a reader against a dry run of the same hour (docs/reviews/periodicals-faults-2026-11-05.md, rows 151 onward). One class
a row, on fixtures: no model, no network, no warehouse write."""

import copy
import json
import os
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in ("warehouse", os.path.join("warehouse", "news"), os.path.join("warehouse", "analysis", "findings"), "scripts"):
    if os.path.join(ROOT, p) not in sys.path:
        sys.path.insert(0, os.path.join(ROOT, p))

import brief  # noqa: E402
import daily_chart  # noqa: E402


def fixture_candidates():
    with open(os.path.join(ROOT, "tests", "fixtures", "session232", "candidates.json"), encoding="utf-8") as f:
        return {c["key"]: c for c in json.load(f)["candidates"]}


def monthly_watch_card():
    """The fixture's weekly watch card made monthly, as the watch list writes a monthly measure's axis ("2026-08"): the
    shape of 13 November 2026's chart, US retail electricity sales."""
    c = copy.deepcopy(fixture_candidates()["watch|watch_caiso_regup|2026-10-05 to 2026-10-11"])
    ch = c["card"]["chart"]
    months = [f"{2021 + (i + 8) // 12}-{(i + 8) % 12 + 1:02d}" for i in range(len(ch["x"]))]
    ch["x"] = months
    ch["x_label"] = "month; the newest complete period is marked"
    for s in ch["series"]:
        s["values"] = s["values"][:len(months)]
    c["card"]["numbers"]["periods"] = 308
    c["key"] = f"watch|watch_retail_sales|{months[-1]}"
    return c, months[-1]


class Row151AMonthlyWatchChartIsShown(unittest.TestCase):
    """Row 151: a watch card's month ("2026-08") broke the caption's last period, so the section was omitted, and the
    picture and record were written anyway (13 November 2026: "No chart is shown today" beside a chart record)."""

    def test_a_month_alone_is_read_as_its_first_day(self):
        self.assertEqual(daily_chart.day_words("2026-08", monthly=True), "August 2026")
        self.assertEqual(daily_chart.day_words("2026-08-01", monthly=True), "August 2026")
        self.assertEqual(daily_chart.day_words("2026-10-06"), "6 October 2026")

    def test_the_caption_of_a_monthly_watch_card(self):
        c, last = monthly_watch_card()
        self.assertEqual(daily_chart.periods_held(c), (308, last, "months"))
        self.assertEqual(daily_chart.held_words(c), f"The table holds 308 months of this series; the last is "
                                                    f"{daily_chart.day_words(last, monthly=True)}.")
        lines = daily_chart.markdown("2026-11-13", c)
        self.assertIn(c["fact"], lines)
        self.assertIn(daily_chart.HEADING, lines)

    def test_a_section_that_cannot_be_written_leaves_no_picture_and_no_record(self):
        c, _ = monthly_watch_card()
        real = daily_chart.markdown

        def broken(day, cand):
            raise ValueError("not enough values to unpack (expected 3, got 2)")

        logged = []
        with tempfile.TemporaryDirectory() as d:
            daily_chart.markdown = broken
            try:
                out = daily_chart.section("2026-11-13", logged.append, chart_dir=d, candidates=[c], used=set(), waited=set(),
                                          dismissed=set())
            finally:
                daily_chart.markdown = real
            self.assertEqual(out, [])
            self.assertEqual(sorted(os.listdir(d)), [], "a picture or a record of a chart the issue does not show")
        self.assertTrue(any("omitted (ValueError" in line for line in logged), logged)


if __name__ == "__main__":
    unittest.main()
