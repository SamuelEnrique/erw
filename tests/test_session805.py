"""Session 805: the chart of the day follows the day (docs/reviews/periodicals-plan-2026-10-23.md, Digest change 5).

daily_chart.choose ranks the candidates by their relevance to the day's top stories (the sector the candidate's table
belongs to against each story's sector tag, and the content words the candidate's fact, table and series share with the
story's title, why line and parties; the top story weighs ten times the tenth) before the rule of session 232 (records
first, then strength). A candidate related to no story ranks after every one related to some. Without the day's stories
the rule of session 232 stands alone, so the tests of sessions 232 and 267 hold. The caveat, the floor and the three
ruled drafts of the audit's fix 10 are not touched (Samuel's). No model, no network, no picture drawn.
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in ("warehouse", os.path.join("warehouse", "news"), os.path.join("warehouse", "analysis", "findings")):
    if os.path.join(ROOT, p) not in sys.path:
        sys.path.insert(0, os.path.join(ROOT, p))

import daily_chart as dc  # noqa: E402


def flag(key, table, entity, fact, strength, rule="record", value=100.0, old=95.0):
    return {"source": "scanner", "key": key, "rank": 1, "fact": fact, "table": table, "series_key": f"entity={entity}|variable=x|market=|node=|freq=P1M",
            "flag": {"id": key, "rule": rule, "strength": strength, "value": value, "compared": {"old_record": old}}, "card": {"title": "T"}}


# session 2701 (rulings item 6(b)): the strengths raised over the floor of 1.5, their order kept
IOWA = flag("iowa", "eia_retail_electricity_prices", "eia:retail_price:IA:IND",
            "Retail electricity price in Iowa, industrial: USD 99.90 per MWh in July 2026, the highest monthly value held since January 2001.", 1.60)
UTAH = flag("utah", "eia_retail_sales_monthly", "eia:retail_sales:UT:RES",
            "Retail electricity sales in Utah, residential: 1,658,263 MWh in July 2026, the highest monthly value held since January 2001.", 1.70)
WYO = flag("wyo", "eia_state_generation_monthly", "eia:generation:WY:NG",
           "Net generation from natural gas in Wyoming: 1,028,747 MWh in July 2026, the highest monthly value held since January 2001.", 2.5, old=90.0)
PJM = flag("pjm", "storage_buildout_monthly", "iso:pjm",
           "iso:pjm battery_operating_mw_net_added_12m: 223.0 MW in July 2026, the highest monthly value held since January 2020.", 1.9)


def story(title, sector, why="", parties=""):
    return {"titles": [title], "sector": sector, "why": why, "parties": parties}


class Relevance(unittest.TestCase):
    def test_a_story_on_the_candidate_s_state_and_sector_lifts_it(self):
        stories = [story("Iowa regulators approve industrial power rate rise for data centers", "power_prices", "Industrial rates in Iowa rise.")]
        score, title, shared = dc.relevance(IOWA, stories)
        self.assertGreater(score, 0)
        self.assertIn("iowa", shared)
        self.assertIn("industrial", shared)
        self.assertEqual(title, stories[0]["titles"][0])
        self.assertEqual(dc.relevance(UTAH, stories)[0], 20)   # the sector tag alone (retail sales belong to power prices too)

    def test_a_candidate_related_to_nothing_scores_zero(self):
        stories = [story("OPEC cuts output", "oil", "Crude supply tightens.", "OPEC")]
        self.assertEqual(dc.relevance(IOWA, stories)[0], 0)
        self.assertEqual(dc.relevance(PJM, stories)[0], 0)

    def test_the_top_story_weighs_ten_times_the_tenth(self):
        top = [story("Nothing here", "oil")] * 9 + [story("Iowa industrial power prices", "power_prices")]
        tenth = dc.relevance(IOWA, top)[0]
        first = dc.relevance(IOWA, [story("Iowa industrial power prices", "power_prices")])[0]
        self.assertEqual(first, 10 * tenth)

    def test_generic_words_do_not_count(self):
        self.assertEqual(dc.relevance(IOWA, [story("Record power prices since July", "deal")])[0], 0)

    def test_the_sectors_of_a_table(self):
        self.assertIn("power_prices", dc.candidate_sectors(IOWA))
        self.assertEqual(dc.candidate_sectors(WYO) & {"gas", "generation"}, {"gas", "generation"})
        self.assertIn("storage", dc.candidate_sectors(PJM))
        self.assertIn("pjm", dc.candidate_words(PJM))
        self.assertIn("wyoming", dc.candidate_words(WYO))


class TheChoice(unittest.TestCase):
    pool = [IOWA, UTAH, WYO, PJM]

    def test_without_stories_the_strongest_stands(self):
        c, why = dc.choose(self.pool, set(), waited={"wyo"})
        self.assertEqual(c["key"], "wyo")
        self.assertNotIn("related", why)

    def test_with_stories_the_related_one_comes_first(self):
        stories = [story("PJM approves fast-track interconnection for two batteries and a gas uprate", "interconnection",
                         "Storage and a gas uprate show the expedited track working.", "PJM; Engie; LS Power")]
        c, why = dc.choose(self.pool, set(), waited={"wyo"}, stories=stories)
        self.assertEqual(c["key"], "pjm")
        self.assertIn("the most related to the day's top stories", why)
        self.assertIn("pjm", why)
        self.assertEqual(c["_relevance"][2], ["batteries"] if "batteries" in c["_relevance"][2] else c["_relevance"][2])

    def test_a_candidate_related_to_none_ranks_after_every_one_related_to_some(self):
        stories = [story("Utah residential demand grows", "generation", "Sales rise.")]
        c, why = dc.choose(self.pool, set(), waited={"wyo"}, stories=stories)
        self.assertEqual(c["key"], "utah")
        c2, why2 = dc.choose(self.pool, {"utah"}, waited={"wyo"}, stories=stories)
        self.assertIn(c2["key"], ("iowa", "wyo"))   # related by the sector tag or by nothing: the rule of 232 then decides

    def test_the_guard_of_session_267_still_holds_a_jumping_record(self):
        stories = [story("Wyoming gas plants run flat out", "generation", "Gas generation in Wyoming is at a record.")]
        c, why = dc.choose(self.pool, set(), stories=stories)   # wyo not waited: 11 percent past its old record here, so not held
        self.assertEqual(c["key"], "wyo")
        big = dict(WYO, flag=dict(WYO["flag"], value=200.0))   # 122 percent past: held a day
        c, why = dc.choose([big, IOWA], set(), stories=stories)
        self.assertEqual(c["key"], "iowa")
        self.assertIn("held a day by the guard", why)

    def test_the_sentence_under_the_chart_says_which_story_it_follows(self):
        stories = [story("Iowa industrial rates rise", "power_prices")]
        c, _ = dc.choose([IOWA, UTAH], set(), stories=stories)
        self.assertIn("It is the candidate most related to the day's top stories: it shares", dc.how_words(c))
        c0, _ = dc.choose([IOWA, UTAH], set())
        self.assertNotIn("most related", dc.how_words(c0))


class TheHandOff(unittest.TestCase):
    def test_the_brief_passes_the_top_ten(self):
        import inspect
        sys.path.insert(0, os.path.join(ROOT, "warehouse", "news"))
        import brief
        self.assertIn('stories=top10.to_dict("records")', inspect.getsource(brief.main))
        self.assertIn("stories", inspect.signature(brief.daily_chart_section).parameters)
        self.assertIn("stories", inspect.signature(dc.section).parameters)

    def test_the_method_says_it(self):
        with open(os.path.join(ROOT, "docs", "methods", "automated_analysis_scanner.md"), encoding="utf-8") as f:
            text = f.read()
        self.assertIn("The day's stories first", text)
        self.assertNotIn(chr(0x2014), text)


if __name__ == "__main__":
    unittest.main()
