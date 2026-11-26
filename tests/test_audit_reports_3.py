"""Session 10232, the report library audit (docs/reviews/reports-model-audit-2026-11-26.md), finding 3.

Sentences of /reports/draft/shape-premium that the rows contradict, drawn from the warehouse's copy of 4 October 2026:
"What the six agree on is the sign: in every hub, the grid's own load paid more" beside CAISO's premium of -0.38;
"nearly every hour of the month" on 48 of 744 hours; "a summer story" when 2024's largest month was January; "it has
shrunk" from 2021, a year whose February (Uri) was 90.8 percent of its premium; "its recent shrinking shows it can fade
as storage and solar reshape the day" against the page's own "the warehouse does not say why"; 2025 left out of the
complete years without a word; "draft of 2026-10-01" over figures read live; "the month is in progress" written whatever
the month. The fix is words only: each sentence now follows the rows it describes. No figure moves.
"""
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PAGE = os.path.join(ROOT, "site", "app", "reports", "draft", "shape-premium", "page.tsx")


def src():
    with open(PAGE, encoding="utf-8") as f:
        return f.read()


class TheSentencesFollowTheRows(unittest.TestCase):
    def test_the_sign_is_said_only_when_every_premium_is_above_zero(self):
        s = src()
        self.assertIn("const nonPos = six.filter((s) => s.pr.v <= 0);", s)
        self.assertIn("{nonPos.length === 0", s)
        self.assertIn("They do not agree on the sign", s)

    def test_nearly_every_hour_only_when_the_month_is_whole(self):
        s = src()
        self.assertIn("const allWhole = six.every((s) => s.hrs.v === s.inMonth.v);", s)
        self.assertIn("this month is held only in part, so the ranking rests on the hours held", s)

    def test_no_season_or_cause_the_rows_do_not_hold(self):
        s = src()
        self.assertNotIn("the premium is a summer story", s)
        self.assertIn("the latest complete year, the largest was {month(lastBig.ts)}", s)
        self.assertNotIn("shows it can fade as storage and solar", s)
        self.assertIn("which the warehouse does not explain", s)

    def test_the_uri_year_is_named_as_a_base(self):
        s = src()
        self.assertIn("(big[0].premium * big[0].hours) / y21.usd.v > 0.5", s)
        self.assertIn("a poor base: Uri's February alone was most of that year's premium", s)

    def test_the_years_left_out_are_named(self):
        s = src()
        self.assertIn("filter((y) => !years.includes(y))", s)
        self.assertIn("left out: a month short of hours, or not yet over", s)

    def test_the_dates_say_what_they_are(self):
        s = src()
        self.assertNotIn("draft of 2026-10-01", s)
        self.assertIn("words of 2026-10-01", s)
        self.assertIn("{pmInProgress ? \" (the days held; the month is in progress)\" : \"\"}", s)

    def test_no_em_dash(self):
        self.assertNotIn(chr(0x2014), src())
        with open(__file__, encoding="utf-8") as f:
            self.assertNotIn(chr(0x2014), f.read())


if __name__ == "__main__":
    unittest.main()
