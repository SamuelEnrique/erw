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
        # session 2701 (rulings item 3): the window opens at the previous issue's end; its hours are the stamp's
        self.assertIn("s, start, bounds = window_rows(df, now, hours, start)", body)
        self.assertIn("stamp_line(hours, start, now, len(s)), \"\",", body)
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


class RevisedNotFailed(unittest.TestCase):
    """Fix 5: a figure the publisher revised after the issue was written, within its revision window, is "revised"."""

    COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "market", "node", "source", "source_url", "retrieved_at", "vintage"]

    def setUp(self):
        spec = importlib.util.spec_from_file_location("check_digest", os.path.join(ROOT, "scripts", "check_digest.py"))
        self.cd = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.cd)

    def csvs(self, d, rows):
        for table, rs in rows.items():
            with open(os.path.join(d, f"{table}.csv"), "w", encoding="utf-8", newline="") as f:
                f.write("# a test table\n")
                w = csv.DictWriter(f, self.COLS)
                w.writeheader()
                for e, v, ts, val, got in rs:
                    w.writerow({"entity": e, "variable": v, "ts_utc": ts, "value": val, "retrieved_at": got})

    def test_the_four_outcomes_of_a_fuel_close(self):
        cd = self.cd
        written = "2026-10-14T15:30:00Z"
        rows = {"eia_fuel_spot_prices": [
            ("eia:wti_cushing", "close", "2026-10-13T00:00:00Z", "101.91", "2026-10-14T06:00:00Z"),   # as printed
            ("eia:wti_cushing", "close", "2026-10-12T00:00:00Z", "99.50", "2026-10-21T06:00:00Z"),    # revised a week later, inside 14 days
            ("eia:wti_cushing", "close", "2026-10-11T00:00:00Z", "98.00", "2026-10-14T06:00:00Z"),    # differs, retrieved before the issue: a fault
            ("eia:wti_cushing", "close", "2026-09-01T00:00:00Z", "80.00", "2026-10-21T06:00:00Z"),    # differs, the issue written 43 days after the period: outside the window
        ]}
        with tempfile.TemporaryDirectory() as d:
            self.csvs(d, rows)
            src = cd.Csv(d)
            fig = lambda day, raw: {"key": f"digest_fuel|eia_fuel_spot_prices|eia:wti_cushing|{day}", "raw": raw, "text": raw, "entity": "eia:wti_cushing", "table": "eia_fuel_spot_prices", "held": False}
            self.assertEqual(cd.check_figure(src, "2026-10-14", fig("2026-10-13", "101.91"), {}, written=written)[0], "ok")
            st, why = cd.check_figure(src, "2026-10-14", fig("2026-10-12", "99.10"), {}, written=written)
            self.assertEqual(st, "revised")
            self.assertIn("99.50 (row retrieved 2026-10-21T06:00:00Z, after the issue was written 2026-10-14T15:30:00Z, both within 14 days of 2026-10-12", why)
            self.assertEqual(cd.check_figure(src, "2026-10-14", fig("2026-10-11", "97.00"), {}, written=written)[0], "FAIL")
            self.assertEqual(cd.check_figure(src, "2026-10-14", fig("2026-09-01", "79.00"), {}, written=written)[0], "FAIL")
            # a table with no revision window: a differing row retrieved later is still a fault
            self.csvs(d, {"some_table": [("eia:x", "close", "2026-10-12T00:00:00Z", "5.00", "2026-10-21T06:00:00Z")]})
            st, _ = cd.compare(src, "4.00", "5.00", written, "some_table", "eia:x", "2026-10-12T00:00:00Z")
            self.assertEqual(st, "FAIL")

    def test_a_real_time_interval_resettled(self):
        cd = self.cd
        rows = {"iso_rtm_hub_prices": [("ercot:HB_WEST", "spp_rtm", "2026-10-07T22:00:00Z", "512.30", "2026-10-09T01:00:00Z"),
                                       ("ercot:HB_WEST", "spp_rtm", "2026-10-07T22:15:00Z", "480.00", "2026-10-30T01:00:00Z")]}
        with tempfile.TemporaryDirectory() as d:
            self.csvs(d, rows)
            src = cd.Csv(d)
            f = {"key": "digest_rt|ercot_rtm_hub_prices|HB_WEST|spp_rtm|2026-10-07T22:00:00Z", "raw": "512.30", "text": "512.30", "entity": "ercot:HB_WEST", "table": "ercot_rtm_hub_prices", "held": False}
            self.assertEqual(cd.check_figure(src, "2026-10-08", f, {}, written="2026-10-08T15:40:00Z")[0], "ok")
            f2 = dict(f, key="digest_rt|ercot_rtm_hub_prices|HB_WEST|spp_rtm|2026-10-07T22:15:00Z", raw="500.00", text="500.00")
            self.assertEqual(cd.check_figure(src, "2026-10-08", f2, {}, written="2026-10-08T15:40:00Z")[0], "revised")

    def test_the_issues_written_time_is_read_from_its_foot(self):
        cd = self.cd
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "2026-10-14.md"), "w", encoding="utf-8") as f:
                f.write("# x\n\n<!-- Generated by warehouse/news/brief.py at 2026-10-14 16:18 UTC; run log x -->\n")
            self.assertEqual(cd.written_at("2026-10-14", d), "2026-10-14T16:18:00Z")
            self.assertIsNone(cd.written_at("2026-10-15", d))

    def test_main_counts_revised_and_does_not_fail_on_it(self):
        text = src("scripts", "check_digest.py")
        self.assertIn('n = {"ok": 0, "FAIL": 0, "revised": 0, "not here": 0, "record": 0, "source": 0}', text)
        self.assertIn("revised by the publisher after the issue was written", text)
        self.assertIn('if n["FAIL"]:\n        return 1', text)
        self.assertIn('if not n["ok"] and not n["revised"]:', text)
        self.assertIn("REVISION_DAYS = {", text)


class NoDash(unittest.TestCase):
    def test_no_em_dash_in_the_files(self):
        for parts in (("warehouse", "news", "brief.py"), ("scripts", "check_digest.py"), ("warehouse", "analysis", "findings", "daily_chart.py"),
                      ("tests", "test_session2206.py")):
            self.assertNotIn(DASH, src(*parts), "/".join(parts))


if __name__ == "__main__":
    unittest.main()
