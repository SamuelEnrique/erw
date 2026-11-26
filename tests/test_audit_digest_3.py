"""Audit of the Digest and the Roundup, finding 3 (session 10235, docs/reviews/digest-model-audit-2026-11-26.md): the
literal-number check that every model sentence of the Digest passes (warehouse/chat/ask.py unverified: the headlines,
the summary above the numbers, the fun fact's numbers) exercised on crafted text, no model, no network.

It does what it says at its core: a number that stands in no source is stopped (the first test). It reads a number's
magnitude alone, anywhere in the sources, so each of the other tests passes a sentence a reader would call unsupported:
a scale word that differs (million for billion), a unit that differs (homes for MW), a day of a date in a source lent
as a figure, a list marker lent as a figure, the opposite direction, and a number written in words. These tests pass on
main: they show the check as it stands. Making it read units, scales, dates and markers changes what the check passes,
so it is for Samuel's ruling, not done here."""
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CHAT = os.path.join(ROOT, "warehouse", "chat")


def check():
    if CHAT not in sys.path:
        sys.path.insert(0, CHAT)
    try:
        import ask  # noqa: E402
    except ImportError as exc:   # anthropic not installed on this copy
        raise unittest.SkipTest(f"warehouse/chat/ask.py does not import here: {exc}")
    return ask.unverified


class TheCheckStopsANumberInNoSource(unittest.TestCase):
    def test_a_number_in_no_source_is_stopped(self):
        self.assertEqual(check()("Henry Hub rose 7.3 percent.", ["Henry Hub closed higher on Tuesday."]), ["7.3"])

    def test_a_number_at_a_finer_precision_than_its_source_is_stopped(self):
        self.assertEqual(check()("Brent closed at 92.14 USD/bbl.", ["Brent closed at 92.1 USD/bbl."]), ["92.14"])


class WhatTheCheckDoesNotRead(unittest.TestCase):
    """Each passes: the sentence is not stopped although no source supports it as written."""

    def test_the_scale_word_is_not_read(self):
        self.assertEqual(check()("SpaceX plans USD 74 million in data center projects.", ["SpaceX plans $74 billion in data center projects"]), [])

    def test_the_unit_is_not_read(self):
        self.assertEqual(check()("Sunrun and Tesla built 580 MW of storage.", ["Sunrun and Tesla enrolled 580 homes."]), [])

    def test_a_dates_day_is_lent_as_a_figure(self):
        # "26" stands in the source only as the day of a date
        self.assertEqual(check()("Saudi output climbed 26 percent.", ["Published 2026-11-26: Saudi output climbed in October."]), [])

    def test_a_dates_month_is_lent_as_a_figure(self):
        self.assertEqual(check()("PJM had 11 GW offline.", ["Posted 2026-11-04: PJM had generation offline."]), [])

    def test_a_list_marker_is_lent_as_a_figure(self):
        # any number of the sentence equal to one of its own list markers is passed, wherever it stands
        self.assertEqual(check()("1. Gas rose.\n2. Oil rose 2 percent.", ["Gas rose.", "Oil rose."]), [])

    def test_the_direction_is_not_read(self):
        self.assertEqual(check()("Brent fell 5.0% on the week.", ["Brent rose 5.0% on the week."]), [])

    def test_a_number_in_words_is_not_read(self):
        self.assertEqual(check()("New gas plants would expand generation capacity by one-third.", ["Families pay more for gas."]), [])

    def test_a_number_from_another_story_of_the_pool_is_lent(self):
        # the headline check's pool is the cluster's titles, summary and why line together; any of them lends its numbers
        self.assertEqual(check()("Oil settles USD 3 higher.", ["Oil settles higher on attacks", "3 tankers were hit last week"]), [])


if __name__ == "__main__":
    unittest.main()
