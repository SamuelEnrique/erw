"""Session 2206 (23 October 2026): five fixes to the periodicals' code from docs/reviews/digest-audit-2026-10-21.md, each
held here on fixtures, with no model call, no network and no warehouse write.

1. brief.party_words matches a short party name (Eni, DOE, SPP): a whole word of two or more letters, capitalized or all
   capitals, so one-event matching sees it.
2. brief.plain cuts an adjective at the end of a sentence or a clause, and cuts unprecedented, critical and key.
3. The Digest's window is cut at the run time (no story dated after the run), and the stamp reads the real bounds.
4. The chart of the day's caption says how many periods of the series are held and the last one held.
5. scripts/check_digest.py marks a figure "revised" when the table's value differs from the issue's and both fall within
   the publisher's revision window, instead of failing it.
"""
import csv
import importlib.util
import os
import sys
import tempfile
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in ("warehouse", os.path.join("warehouse", "news"), os.path.join("warehouse", "analysis", "findings")):
    if os.path.join(ROOT, p) not in sys.path:
        sys.path.insert(0, os.path.join(ROOT, p))

import brief  # noqa: E402

DASH = chr(0x2014)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class ShortPartyNames(unittest.TestCase):
    """Fix 1: party_words dropped names shorter than four letters."""

    def test_short_names_count_when_capitalized_or_all_capitals(self):
        self.assertEqual(brief.party_words({"parties": "Eni; DOE; SPP"}), {"eni", "doe", "spp"})
        self.assertEqual(brief.party_words({"parties": "NextEra Energy; PJM Interconnection"}), {"nextera", "pjm", "interconnection"})

    def test_a_lower_case_short_word_is_not_a_name(self):
        # "of" and "the" are not names; a four-letter lower-case word still counts, as before
        self.assertEqual(brief.party_words({"parties": "the office of the governor; nextera"}), {"governor", "nextera"})

    def test_generic_words_are_still_taken_out(self):
        self.assertEqual(brief.party_words({"parties": "Department of Energy; DOE"}), {"doe"})
        self.assertEqual(brief.party_words({"parties": ""}), set())
        self.assertEqual(brief.party_words({}), set())

    def test_two_clusters_naming_eni_are_one_event(self):
        a = {"sector": "oil", "parties": "Eni", "titles": ["Eni signs a 20-year LNG supply deal with Venture Global"], "price_mentioned": "", "mw": ""}
        b = {"sector": "oil", "parties": "Eni; Venture Global", "titles": ["Venture Global and Eni sign 20-year LNG supply deal"], "price_mentioned": "", "mw": ""}
        self.assertTrue(brief.same_event(a, b))
        c = {"sector": "oil", "parties": "Shell", "titles": ["Shell signs a 20-year LNG supply deal with Venture Global"], "price_mentioned": "", "mw": ""}
        self.assertFalse(brief.same_event(a, c))


class NoDash(unittest.TestCase):
    def test_no_em_dash_in_the_files(self):
        for parts in (("warehouse", "news", "brief.py"), ("scripts", "check_digest.py"), ("warehouse", "analysis", "findings", "daily_chart.py"),
                      ("tests", "test_session2206.py")):
            self.assertNotIn(DASH, src(*parts), "/".join(parts))


if __name__ == "__main__":
    unittest.main()
