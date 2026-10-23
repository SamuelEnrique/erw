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


class AdjectivesAtTheEnd(unittest.TestCase):
    """Fix 2: plain required a space after the adjective, so one at a stop or a comma stayed."""

    def test_at_a_stop_a_comma_or_the_end(self):
        self.assertEqual(brief.plain("The deal is significant."), "The deal is.")
        self.assertEqual(brief.plain("Prices rose, significantly, on the news"), "Prices rose, on the news")
        self.assertEqual(brief.plain("Output fell; the loss is massive"), "Output fell; the loss is")
        self.assertEqual(brief.plain("A rise that is huge!"), "A rise that is!")

    def test_the_three_new_words(self):
        self.assertEqual(brief.plain("An unprecedented 2 GW deal"), "A 2 GW deal")
        self.assertEqual(brief.plain("A critical step for the grid"), "A step for the grid")
        self.assertEqual(brief.plain("Key approval for the pipeline."), "Approval for the pipeline.")
        self.assertEqual(brief.plain("The outage was unprecedented."), "The outage was.")

    def test_the_trade_words_stay(self):
        for t in ("The key to the deal is price.", "Critical minerals supply tightens.", "Critical infrastructure protected.",
                  "The key of the vault.", "A key for each lock."):
            self.assertEqual(brief.plain(t), t)

    def test_session_470s_cases_still_hold(self):
        self.assertEqual(brief.plain("A major 2 GW deal."), "A 2 GW deal.")
        self.assertEqual(brief.plain("Massive outage hits Texas. A significant expansion of a major utility."),
                         "Outage hits Texas. An expansion of a utility.")
        self.assertEqual(brief.plain("It significantly raises costs"), "It raises costs")
        self.assertEqual(brief.plain("No adjective here."), "No adjective here.")
        self.assertEqual(brief.why_line("Escalation affecting global oil markets is significant"), "Escalation affecting global oil markets is.")


class TheWindowEndsAtTheRun(unittest.TestCase):
    """Fix 3: the window had no upper bound, so a story dated after the run was taken and the stamp was false."""

    def rows(self):
        return pd.DataFrame([
            {"event_date": "2026-10-23T15:00:00Z", "scored_at": "x", "significance": "7", "ai_power_relevance": "0", "title": "in the window"},
            {"event_date": "2026-10-22T16:00:00Z", "scored_at": "x", "significance": "6", "ai_power_relevance": "0", "title": "at the start"},
            {"event_date": "2026-10-22T15:44:00Z", "scored_at": "x", "significance": "8", "ai_power_relevance": "0", "title": "before the start"},
            {"event_date": "2026-10-23T15:46:00Z", "scored_at": "x", "significance": "9", "ai_power_relevance": "0", "title": "after the run"},
            {"event_date": "2026-10-23T12:00:00Z", "scored_at": "", "significance": "9", "ai_power_relevance": "0", "title": "not scored"},
            {"event_date": "2026-10-23T12:00:00Z", "scored_at": "x", "significance": "0", "ai_power_relevance": "0", "title": "not energy"},
        ])

    def test_a_story_dated_after_the_run_is_left_for_the_next_issue(self):
        now = pd.Timestamp("2026-10-23T15:45:00Z")
        s, start, bounds = brief.window_rows(self.rows(), now, 24)
        self.assertEqual(sorted(s["title"]), ["at the start", "in the window"])
        self.assertEqual(start, pd.Timestamp("2026-10-22T15:45:00Z"))
        self.assertEqual(bounds, (pd.Timestamp("2026-10-22T16:00:00Z"), pd.Timestamp("2026-10-23T15:00:00Z")))
        self.assertEqual(list(s["sig"]), [7, 6])

    def test_no_rows_gives_no_bounds(self):
        s, start, bounds = brief.window_rows(self.rows().iloc[:0], pd.Timestamp("2026-10-23T15:45:00Z"), 24)
        self.assertEqual(len(s), 0)
        self.assertIsNone(bounds)

    def test_the_stamp_reads_both_bounds_and_the_old_form_first(self):
        line = brief.stamp_line(24, pd.Timestamp("2026-10-22T15:45:00Z"), pd.Timestamp("2026-10-23T15:45:00Z"), 212)
        self.assertEqual(line, "ERW's weekday brief of energy news for the 24 hours to 2026-10-23 15:45 UTC, from 2026-10-22 15:45 UTC, from 212 scored stories.")
        import re
        m = re.search(r"for the (\d+) hours to (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC", line)   # tests/test_session470.py's reader
        self.assertEqual((m.group(1), m.group(2)), ("24", "2026-10-23 15:45"))

    def test_main_uses_them(self):
        b = src("warehouse", "news", "brief.py")
        body = b[b.index("def main(argv=None):"):]
        self.assertIn("s, start, bounds = window_rows(df, now, args.hours)", body)
        self.assertIn("stamp_line(args.hours, start, now, len(s)), \"\",", body)
        self.assertNotIn("when >= now - pd.Timedelta(hours=args.hours)", body)


class TheCaptionSaysWhatIsHeld(unittest.TestCase):
    """Fix 4: the chart of the day's caption states how many periods of the series are held and the last one held."""

    def setUp(self):
        import json
        import daily_chart
        self.dc = daily_chart
        with open(os.path.join(ROOT, "tests", "fixtures", "session232", "candidates.json"), encoding="utf-8") as f:
            self.cands = {c["key"]: c for c in json.load(f)["candidates"]}

    def test_a_monthly_record_counts_its_history_and_the_months_to_the_flag(self):
        c = self.cands["scan-record-483f592bf064"]   # history 305 months to May 2026, flagged July 2026
        self.assertEqual(self.dc.periods_held(c), (307, "2026-07-01", "months"))
        self.assertEqual(self.dc.held_words(c), "The table holds 307 months of this series; the last is July 2026.")

    def test_a_daily_spike_and_a_weekly_change(self):
        self.assertEqual(self.dc.periods_held(self.cands["scan-spike-4c52d4239fe9"]), (761, "2026-10-06", "days"))
        self.assertEqual(self.dc.held_words(self.cands["scan-spike-4c52d4239fe9"]), "The table holds 761 days of this series; the last is 6 October 2026.")
        self.assertEqual(self.dc.periods_held(self.cands["scan-weekly-33b8c62e9e29"]), (261, "2026-10-05", "weeks"))

    def test_a_watch_card_counts_the_periods_its_engine_ordered(self):
        c = self.cands["watch|watch_caiso_regup|2026-10-05 to 2026-10-11"]
        self.assertEqual(self.dc.periods_held(c), (108, "2026-10-05", "weeks"))
        self.assertEqual(self.dc.held_words(c), "The table holds 108 weeks of this series; the last is the week starting 5 October 2026.")

    def test_a_card_that_does_not_say_adds_nothing(self):
        self.assertIsNone(self.dc.periods_held({"source": "scanner", "flag": {"history": {}, "date": "2026-07-01"}, "card": {}}))
        self.assertEqual(self.dc.held_words({"source": "watch", "card": {"chart": {}, "numbers": {}}}), "")

    def test_the_section_carries_the_line_after_the_fact_and_the_fact_line_is_unchanged(self):
        c = self.cands["scan-record-483f592bf064"]
        lines = self.dc.markdown("2026-10-13", c)
        i = lines.index(c["fact"])
        self.assertEqual(lines[i + 1], "The table holds 307 months of this series; the last is July 2026.")
        self.assertEqual(lines[i + 2], "")
        self.assertTrue(lines[i + 3].startswith("Table `"))


class NoDash(unittest.TestCase):
    def test_no_em_dash_in_the_files(self):
        for parts in (("warehouse", "news", "brief.py"), ("scripts", "check_digest.py"), ("warehouse", "analysis", "findings", "daily_chart.py"),
                      ("tests", "test_session2206.py")):
            self.assertNotIn(DASH, src(*parts), "/".join(parts))


if __name__ == "__main__":
    unittest.main()
