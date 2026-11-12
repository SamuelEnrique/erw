"""Session 1882: the Roundup's faults of W45 (docs/reviews/periodicals-faults-2026-11-05.md, rows 59 to 76), each fix proved
on a fixture: the faulted line is built from the fixture and the replacement asserted. No model call, no network, no
warehouse table read (each table read is patched)."""

import json
import os
import sys
import tempfile
import unittest
from unittest import mock

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "news"))
import brief  # noqa: E402
import roundup  # noqa: E402

UTC = "UTC"
START = pd.Timestamp("2026-11-02", tz=UTC)
END = pd.Timestamp("2026-11-09", tz=UTC)
CUT = pd.Timestamp("2026-11-08 23:26", tz=UTC)
NEWEST = pd.Timestamp("2026-11-05 23:08", tz=UTC)      # the newest story the W45 run held
RT_REACH = pd.Timestamp("2026-11-05 07:45", tz=UTC)    # the real-time tables' reach in W45


def quiet(*_a, **_k):
    pass


class Row59TheMastheadAndTheSpan(unittest.TestCase):
    def test_the_masthead_says_where_the_stories_stop(self):
        L = roundup.masthead_lines("2026-W45", END, CUT, None, "A head.", "", NEWEST, RT_REACH)
        self.assertEqual(L[2], "**Week ending 8 November 2026.** Stories through 5 November, 18:08 ET, 23:08 UTC; the week's "
                               "tables reach 5 November (each table's reach is under ERW's Numbers This Week).")
        self.assertNotIn("Sources through 18:26 ET", "\n".join(L))

    def test_stories_to_the_cut_keep_the_old_line(self):
        L = roundup.masthead_lines("2026-W45", END, CUT, None, "A head.", "", CUT - pd.Timedelta(minutes=30), CUT)
        self.assertEqual(L[2], "**Week ending 8 November 2026.** Sources through 18:26 ET, 23:26 UTC.")
        L = roundup.masthead_lines("2026-W45", END, CUT, None, "A head.", "")
        self.assertEqual(L[2], "**Week ending 8 November 2026.** Sources through 18:26 ET, 23:26 UTC.")

    def test_stories_short_the_same_day_name_no_date(self):
        line = roundup.cutoff_line(CUT, CUT - pd.Timedelta(hours=5), CUT)
        self.assertEqual(line, "Stories through 13:26 ET, 18:26 UTC; cut at 18:26 ET, 23:26 UTC.")

    def test_the_intro_span(self):
        self.assertEqual(roundup.intro_span(START, END, CUT, NEWEST), "2026-11-02 to 2026-11-08 (no story after 2026-11-05 is held)")
        self.assertEqual(roundup.intro_span(START, END, CUT, CUT), "2026-11-02 to 2026-11-08, cut at 2026-11-08 23:26 UTC")
        self.assertEqual(roundup.intro_span(START, END, END, END - pd.Timedelta(hours=1)), "2026-11-02 to 2026-11-08")
        self.assertNotIn(" to 2026-11-08 23:26", roundup.intro_span(START, END, CUT, NEWEST))

    def test_main_passes_the_newest_story_and_the_tables_reach(self):
        src = open(roundup.__file__, encoding="utf-8").read()
        self.assertIn("masthead_lines(label, end, cut, op, heads[recs[0][\"cluster_id\"]] if recs else \"\", missed, newest, tables_to)", src)
        self.assertIn("span = intro_span(start, end, cut, newest)", src)


class Row60TheWeekendLine(unittest.TestCase):
    def test_no_story_held_says_the_newest(self):
        self.assertEqual(roundup.weekend_empty_line(START + pd.Timedelta(days=5), NEWEST),
                         "- No story of 7 or 8 November is held: the newest story the warehouse holds is of 5 November, 23:08 UTC.")

    def test_weekend_stories_shown_above(self):
        self.assertEqual(roundup.weekend_empty_line(START + pd.Timedelta(days=5), pd.Timestamp("2026-11-08 10:00", tz=UTC)),
                         "- No other story of 7 or 8 November is held.")

    def test_a_weekend_across_two_months(self):
        self.assertEqual(roundup.weekend_empty_line(pd.Timestamp("2026-10-31", tz=UTC), pd.Timestamp("2026-10-29 12:00", tz=UTC)),
                         "- No story of 31 October or 1 November is held: the newest story the warehouse holds is of 29 October, 12:00 UTC.")


class Row62TheSubject(unittest.TestCase):
    OP = {"move": {"label": "Brent crude", "pct": -13.05, "text": "Brent moved"}, "key": "move"}
    HEAD = "AEP and Google advance a $4 Billion, 702 MW Bloom Energy fuel-cell project in Cheyenne"

    def test_w45_subject(self):
        got = roundup.subject_line(self.OP, self.HEAD)
        self.assertEqual(got, "ERW Weekly | Brent down 13.1% on the week; AEP and Google advance a Bloom Energy fuel-cell")
        self.assertLessEqual(len(got), roundup.SUBJECT_MAX)
        self.assertNotIn("...", got)
        self.assertNotIn("702", got)
        self.assertNotIn("USD", got)

    def test_a_cut_never_ends_on_a_small_word(self):
        got = roundup.subject_line(self.OP, "Utility signs a contract with the state of Texas for the supply of power to a new hub in the north")
        self.assertLessEqual(len(got), 90)
        self.assertFalse(got.endswith((" the", " of", " a", " to", " for", " in")), got)
        self.assertNotIn("...", got)

    def test_no_move_keeps_the_old_rule(self):
        self.assertEqual(roundup.subject_line(None, "Six reactors eyed."), "ERW Weekly | Six reactors eyed")


class Row72TheAlsoLines(unittest.TestCase):
    X = dict(title="Last Energy, Inc; Phased Construction Permit Application-Limited Work Authorization", agency="NRC",
             action_type="notice", event_date="2026-11-05", why="", source_url="https://www.federalregister.gov/d/2026-1")

    def test_a_failed_why_line_leaves_no_colon(self):
        got = roundup.also_policy_line(self.X)
        self.assertEqual(got, "- Last Energy, Inc.; Phased Construction Permit Application-Limited Work Authorization (NRC notice, "
                              "published 2026-11-05). [Source](https://www.federalregister.gov/d/2026-1)")
        self.assertNotIn(":  ", got)
        self.assertNotIn("):", got)

    def test_a_why_line_that_passes_is_kept(self):
        got = roundup.also_policy_line(dict(self.X, why="Site work at the Texas plant may start before the full permit is granted."))
        self.assertIn("(NRC notice, published 2026-11-05): Site work at the Texas plant", got)
        self.assertTrue(got.endswith("[source](https://www.federalregister.gov/d/2026-1)"))

    def test_policy_of_the_week_uses_it(self):
        acts = pd.DataFrame([
            {"event_id": "a1", "event_date": "2026-11-04", "significance": "7", "title": "A final rule", "agency": "NRC",
             "action_type": "rule", "docket": "", "why": "Opens hearings to 2027 challengers in Ohio.", "source_url": "https://example.org/1"},
            dict(self.X, event_id="a2", significance="6", docket="")])
        with mock.patch.object(roundup, "read_table", lambda n: acts if n == "policy_actions" else None):
            L = roundup.policy_of_the_week(START, CUT, quiet)
        line = next(ln for ln in L if ln.startswith("- Last Energy"))
        self.assertTrue(line.endswith("(NRC notice, published 2026-11-05). [Source](https://www.federalregister.gov/d/2026-1)"))


class Row73TheChartNote(unittest.TestCase):
    NOTE = ("The chart shows the Lower 48 battery discharge, daily mean of the week, for each of the 104 weeks held, which ran from "
            "9188.86 MWh a day (2024-11-04 to 2024-11-10) to 56102.57 MWh a day (2026-08-31 to 2026-09-06). In the week of "
            "2026-10-26 to 2026-11-01 it was 47682.14 MWh a day, down 6,317.57 from 53,999.71 the week before, and 8 of the 102 "
            "earlier week-to-week moves were as large.")

    def test_one_style(self):
        self.assertEqual(roundup.note_style(self.NOTE),
                         "The chart shows the Lower 48 battery discharge, daily mean of the week, for each of the 104 weeks held, which "
                         "ran from 9,189 MWh a day (2024-11-04 to 2024-11-10) to 56,103 MWh a day (2026-08-31 to 2026-09-06). In the "
                         "week of 2026-10-26 to 2026-11-01 it was 47,682 MWh a day, down 6,318 from 54,000 the week before, and 8 of "
                         "the 102 earlier week-to-week moves were as large.")

    def test_years_small_figures_and_ids_left(self):
        self.assertEqual(roundup.note_style("In 2026 it was 12.34 USD/MWh, 1500 MW, template watch_2024 and 45000 MWh."),
                         "In 2026 it was 12.34 USD/MWh, 1500 MW, template watch_2024 and 45,000 MWh.")

    def test_the_section_prints_the_styled_note(self):
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "2026-W45"))
            with open(os.path.join(d, "2026-W45", "chart_of_the_week.json"), "w", encoding="utf-8") as f:
                json.dump({"title": "Batteries discharging, Lower 48", "files": {"email": "chart_email.png"}, "note": self.NOTE,
                           "headline": {}, "source_line": "Source: EIA-930.", "template": "watch_battery_discharge_us"}, f)
            with mock.patch.object(roundup, "ANALYSIS_DIR", d), \
                    mock.patch.dict(sys.modules, {"roundup_pick": mock.Mock(chosen=lambda *a: None)}):
                L = roundup.chart_of_the_week("2026-W45", quiet)
        text = "\n".join(L)
        self.assertIn("down 6,318 from 54,000 the week before", text)
        self.assertNotIn("47682.14", text)


class Row71TheHoursHeld(unittest.TestCase):
    def test_the_roundup_cell(self):
        def dam(label, table, node, tz, start, log):
            return (33.19, 168, 168) if start < START else (None, 120, 168)

        def nothing(*a, **k):
            raise RuntimeError("not on this machine")
        with mock.patch.object(roundup, "dam_week", dam), mock.patch.object(roundup.erw, "fetch", nothing), \
                mock.patch.object(brief, "held_grids", lambda *a: set()), mock.patch.object(brief, "paused_row", lambda *a: None), \
                mock.patch.object(brief, "rt_parts", lambda: []):
            L = roundup.numbers(START, CUT, quiet, {})
        row = next(ln for ln in L if ln.startswith("| ERCOT |"))
        self.assertIn("| 120 of 168 hours held, no weekly mean | 33.19 | not computed |", row)
        self.assertNotIn("not in the warehouse (120", "\n".join(L))

    def test_the_digest_cell(self):
        src = open(brief.__file__, encoding="utf-8").read()
        self.assertIn("hours held, no daily mean", src)
        self.assertNotIn("not in the warehouse ({h['n1']} of {h['x1']} hours)", src)


if __name__ == "__main__":
    unittest.main()
