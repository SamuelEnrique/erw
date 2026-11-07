"""Session 3297 (the Ask evaluation's second pass, 6 November 2026): the query tool's value threshold, asked for by the
trader set's tr15 ("how many 15-minute intervals at ERCOT West were above 100 USD/MWh"), which the loop could not count.

The Python side (warehouse/chat/tools.py query, threshold={"above": x, "below": y}) over session 1300's fixture rows; the
site's side (site/lib/chat/threshold.ts) by `node --test site/scripts/test-ask-threshold.test.mjs`; both loops turn by turn
in tests/test_session1300.py's scenario a_threshold_count. And the shared prompt's rule 3 (iv14): a table covering every
grid is listed with no filter first. No network, no warehouse table, no model.
"""
import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tests"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "chat"))
import test_session1300 as T  # noqa: E402  the fixture's frames
import ask  # noqa: E402
import tools  # noqa: E402

Q = dict(table="ercot_peak_premium_annual", entity="ercot:HB_HUBAVG", variable="peak_minus_midday_median")
# the fixture's twelve yearly rows, 2015 to 2026: -0.16, 0.03, 0.09, 0.255, 0.49, 0.57, 3.135, 13.65, 6.495, 8.93, 14.52, 12.29


def query(**kw):
    with T.Frames() as frames:
        frames.load()
        return tools.query(**{**Q, **kw})


class TheThreshold(unittest.TestCase):
    def test_count_above(self):
        out = query(aggregation="count", threshold={"above": 10})
        self.assertEqual(out["result"], [{"count": 3}])
        self.assertEqual(out["rows_matched"], 3)
        self.assertEqual(out["threshold"]["rows_in_window"], 12)
        self.assertEqual(out["threshold"]["rows_kept"], 3)
        self.assertEqual(out["threshold"]["column"], "value")
        self.assertEqual(out["threshold"]["above"], 10)
        self.assertNotIn("below", out["threshold"])
        self.assertEqual(out["filters"]["threshold"], {"above": 10})

    def test_count_below_and_a_band(self):
        self.assertEqual(query(aggregation="count", threshold={"below": 0})["result"], [{"count": 1}])
        band = query(aggregation="count", threshold={"above": 1, "below": 10})
        self.assertEqual(band["result"], [{"count": 3}])   # 3.135, 6.495, 8.93
        self.assertEqual((band["threshold"]["above"], band["threshold"]["below"]), (1, 10))

    def test_strictly_past_the_figure(self):
        self.assertEqual(query(aggregation="count", threshold={"above": 14.52})["result"], [{"count": 0}])
        self.assertEqual(query(aggregation="count", threshold={"below": -0.16})["result"], [{"count": 0}])
        none = query(aggregation="count", threshold={"above": 100})
        self.assertEqual((none["rows_matched"], none["threshold"]["rows_in_window"], none["threshold"]["rows_kept"]), (0, 12, 0))
        self.assertEqual(none["note"], tools.THRESHOLD_NONE)
        self.assertEqual(query(aggregation="mean", threshold={"above": 100})["result"], [])
        # no row in the window at all is still "no rows match"
        empty = query(aggregation="count", threshold={"above": 1}, start="2030-01-01")
        self.assertEqual((empty["result"], empty["note"]), ([], "no rows match these filters"))

    def test_the_note_is_the_sites(self):
        with open(os.path.join(ROOT, "site", "lib", "chat", "threshold.ts"), encoding="utf-8") as f:
            self.assertIn(json.dumps(tools.THRESHOLD_NONE), f.read())

    def test_other_aggregations_over_the_rows_kept(self):
        out = query(aggregation="mean", threshold={"above": 10})
        self.assertAlmostEqual(out["result"][0]["value"], round((13.65 + 14.52 + 12.29) / 3, tools.DIGITS))
        self.assertEqual(out["result"][0]["n"], 3)
        g = query(aggregation="count", threshold={"above": 10}, group_by="year")
        self.assertEqual([r["year"] for r in g["result"]], ["2022", "2025", "2026"])

    def test_no_threshold_leaves_the_answer_as_it_was(self):
        out = query(aggregation="count")
        self.assertEqual(out["result"], [{"count": 12}])
        self.assertNotIn("threshold", out)
        self.assertNotIn("threshold", out["filters"])

    def test_bad_thresholds_are_refused_with_words(self):
        with T.Frames() as frames:
            frames.load()
            for bad in ({}, {"over": 1}, {"above": "100"}, {"above": True}, {"above": 5, "below": 5}, {"above": None}, [100]):
                res, err = tools.run("query", {**Q, "aggregation": "count", "threshold": bad})
                self.assertTrue(err, bad)
                self.assertIn("threshold", res["error"], bad)

    def test_the_tool_definition_both_loops_read(self):
        props = tools.QUERY_PROPS["threshold"]
        self.assertEqual(set(props["properties"]), {"above", "below"})
        with open(os.path.join(ROOT, "site", "lib", "chat", "spec.json"), encoding="utf-8") as f:
            spec = json.load(f)
        q = next(t for t in spec["tools"] if t["name"] == "query")
        self.assertEqual(q["input_schema"]["properties"]["threshold"], json.loads(json.dumps(props)))
        cmp_ = next(t for t in spec["tools"] if t["name"] == "compare")
        self.assertIn("threshold", cmp_["input_schema"]["properties"]["a"]["properties"])

    def test_the_site_reads_the_same_argument(self):
        with open(os.path.join(ROOT, "site", "lib", "chat", "tools.ts"), encoding="utf-8") as f:
            ts = f.read()
        self.assertIn("threshold?: Threshold;", ts)
        self.assertIn("readThreshold(a.threshold)", ts)
        self.assertIn("out.threshold = thrField", ts)


class RuleThree(unittest.TestCase):
    """iv14 (months to in-service by grid): the loop listed tables only under CAISO's iso filter and a sector, never saw
    interconnection_durations_summary (a table of every grid) and stopped at the 12-call limit."""

    def test_list_with_no_filter_first_in_both_loops(self):
        words = ("A table that covers every grid (a summary by grid, a national table) is not listed under one grid's iso filter: "
                 "list_tables with no filter first, then narrow.")
        self.assertIn(words, ask.SYSTEM)
        self.assertNotIn("Call list_tables (with a filter) to find the table", ask.SYSTEM)
        with open(os.path.join(ROOT, "site", "lib", "chat", "spec.json"), encoding="utf-8") as f:
            self.assertEqual(json.load(f)["system"], ask.SYSTEM)


if __name__ == "__main__":
    unittest.main()
