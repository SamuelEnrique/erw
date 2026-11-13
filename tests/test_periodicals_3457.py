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


class Row152TheRealTimeLineInWords(unittest.TestCase):
    """Row 152: the Digest's real-time line printed "interval starting 2026-11-12 19:00 local (2026-11-13 01:00 UTC),
    PT15M `spp_rtm`, ERCOT's ..." (the Roundup's twin was row 71): the interval in words and in the grid's zone, the
    variable on the Tables line."""

    @classmethod
    def setUpClass(cls):
        from unittest import mock
        import test_periodicals as tp
        with mock.patch.object(brief.erw, "fetch", side_effect=tp.fake_fetch), \
                mock.patch.object(brief, "held_grids", return_value={"NYISO", "ISO-NE"}), \
                mock.patch.object(brief, "rt_parts", return_value=[("spp", "iso_rtm_hub_prices", "spp_rtm")]), \
                mock.patch.object(brief, "cite_short", side_effect=lambda t: f"`{t}`"), \
                mock.patch.object(brief, "paused_row", return_value=None), tp.no_hold():
            cls.lines = brief.numbers_today("2026-10-21", tp.quiet, None)
        cls.rt = next(ln for ln in cls.lines if ln.startswith("**Highest real-time price"))
        cls.tables = next(ln for ln in cls.lines if ln.startswith("Tables: ") and "real-time tables read" in ln)

    def test_the_line_names_the_interval_in_words_and_the_zone(self):
        self.assertEqual(self.rt, "**Highest real-time price, yesterday:** 276.41 USD/MWh at SPPNORTH_HUB (SPP), the 15-minute "
                                  "interval starting 2026-10-20 23:45 Central (2026-10-21 04:45 UTC) [4], SPP's real-time "
                                  "locational marginal price (a 15-minute mean of 5-minute prices).")
        for gone in ("local", "PT15M", "`"):
            self.assertNotIn(gone, self.rt)

    def test_the_variable_is_on_the_tables_line(self):
        self.assertIn("real-time tables read: iso_rtm_hub_prices; yesterday's highest real-time price is variable "
                      "`lmp_rtm_15m_mean`", self.tables)

    def test_the_zone_and_the_utc_date(self):
        import pandas as pd
        self.assertEqual(brief.rt_when(pd.Timestamp("2026-11-13T01:00Z"), "America/Chicago"),
                         "2026-11-12 19:00 Central (2026-11-13 01:00 UTC)")
        self.assertEqual(brief.rt_when(pd.Timestamp("2026-11-12T23:45Z"), "America/Chicago"), "2026-11-12 17:45 Central (23:45 UTC)")
        self.assertEqual(brief.rt_when(pd.Timestamp("2026-11-12T23:45Z"), "UTC"), "2026-11-12 23:45 UTC")

    def test_the_roundup_writes_with_the_same_helpers(self):
        import roundup
        self.assertIs(roundup.rt_when, brief.rt_when)
        self.assertIs(roundup.interval_words, brief.interval_words)
        self.assertIs(roundup.ZONE_WORDS, brief.ZONE_WORDS)


if __name__ == "__main__":
    unittest.main()
