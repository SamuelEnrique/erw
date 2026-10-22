"""Session 801: the why line says the consequence (docs/reviews/periodicals-plan-2026-10-23.md, Digest change 1).

One sentence, the consequence for the energy system or the market, no adjective of the list (massive, unprecedented,
significant, major, critical, key, huge), no figure the headline already gives, the stop before the figures kept
(session 577). The scorer's prompt asks for it; the brief's check (brief.why_check) is the gate, and a line that fails is
rewritten by brief.why_line: the first sentence, the headline's figure taken out where the sentence still reads, else the
headline's own clause (brief.why_fallback), never an invented fact. The figures line (brief.detail) prints no MW or price the
headline holds. Fixture: tests/fixtures/periodicals/why_lines.json, 20 saved items of the 13 issues from
warehouse/output/news_stories.csv, each with the line the session read and pinned. No model, no network.
"""

import inspect
import json
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in ("warehouse", os.path.join("warehouse", "news")):
    if os.path.join(ROOT, p) not in sys.path:
        sys.path.insert(0, os.path.join(ROOT, p))

import brief  # noqa: E402
import roundup  # noqa: E402
import score  # noqa: E402

FIXTURE = os.path.join(ROOT, "tests", "fixtures", "periodicals", "why_lines.json")


def items():
    with open(FIXTURE, encoding="utf-8") as f:
        return json.load(f)["items"]


class TheRule(unittest.TestCase):
    """why_check names each fault; a line that passes is left as it is."""

    def test_the_21_october_top_1(self):
        why = "Massive AI compute capex signals unprecedented power demand growth and infrastructure investment scale."
        head = "Anthropic may spend $750 Billion on computing costs, Bloomberg reports"
        self.assertEqual(brief.why_check(why, head), ["adjective: massive", "adjective: unprecedented"])
        out = brief.why_line(why, head)
        self.assertEqual(out, "AI compute capex signals power demand growth and infrastructure investment scale.")
        self.assertEqual(brief.why_check(out, head), [])
        # the figures line prints no USD 750 billion again: the headline holds it
        self.assertEqual(brief.detail({"mw": "", "price": "$750 Billion", "parties": "Anthropic"}, head), "parties: Anthropic. ")

    def test_every_adjective_of_the_list_is_named(self):
        for adj in brief.WHY_ADJECTIVES:
            self.assertEqual(brief.why_check(f"A {adj} deal for the grid.", "A deal"), [f"adjective: {adj}"])
            self.assertNotRegex(brief.why_line(f"A {adj} deal for the grid.", "A deal"), rf"(?i)\b{adj}\b")

    def test_a_figure_the_headline_gives(self):
        self.assertEqual(brief.why_check("A 600 MW load adds demand to the grid.", "Sesterce plans a 600MW campus"),
                         ["figure of the headline: 600"])
        self.assertEqual(brief.why_line("A 600 MW load adds demand to the grid.", "Sesterce plans a 600MW campus"),
                         "A load adds demand to the grid.")
        # a year is not a figure the headline gives
        self.assertEqual(brief.why_check("Capacity arrives by 2032.", "A plan to 2032"), [])

    def test_two_sentences_keep_the_first(self):
        self.assertEqual(brief.why_check("The U.S. Department of Energy funds it. Prices will rise.", "DOE"), ["two sentences"])
        self.assertEqual(brief.why_line("The U.S. Department of Energy funds it. Prices will rise.", "DOE"),
                         "The U.S. Department of Energy funds it.")
        # an abbreviation's stop is not a sentence's end
        self.assertEqual(brief.why_check("A factory opening on Oct. 6 adds US supply.", "Toyo"), [])
        self.assertEqual(brief.why_check("Acme Inc. and Beta Corp. agree.", "Deal"), [])

    def test_a_line_that_cannot_lose_its_figure_falls_back_to_the_headline(self):
        head = "PJM approves fast-track interconnection for 2.1 GW from Engie, LS Power"
        why = "Storage and a gas uprate totaling 2.1 GW expected online by mid-2029 show the expedited track working."
        self.assertEqual(brief.why_line(why, head), brief.why_fallback(head))
        self.assertEqual(brief.why_fallback(head), head + ".")

    def test_the_fallback_is_the_title_s_own_clause(self):
        self.assertEqual(brief.why_fallback("NTT to build $6.3bn data center for Anthropic in Japan - report"),
                         "NTT to build USD 6.3 billion data center for Anthropic in Japan.")
        self.assertEqual(brief.why_fallback("Anthropic may spend $750 Billion on computing costs, Bloomberg reports"),
                         "Anthropic may spend USD 750 billion on computing costs.")
        self.assertEqual(brief.why_fallback("Exclusive: BP sells assets - Reuters"), "BP sells assets.")
        self.assertEqual(brief.why_fallback(""), "")

    def test_an_article_follows_its_noun_once_the_figure_is_gone(self):
        self.assertEqual(brief.why_line("Adds a 1,200 MW uprate to the fleet.", "BKV adds 1,200 MW"), "Adds an uprate to the fleet.")
        self.assertEqual(brief.why_line("An $800MM loan funds the plant.", "DOE lends $800 million"), "A loan funds the plant.")

    def test_without_a_headline_the_session_577_behaviour_holds(self):
        out = brief.why_line("Major AI datacenter infrastructure deal signals massive power demand and capital commitment")
        self.assertEqual(out, "AI datacenter infrastructure deal signals power demand and capital commitment.")
        self.assertEqual(brief.why_line("Prices rose  "), "Prices rose.")
        self.assertEqual(brief.why_line(""), "")

    def test_the_detail_keeps_what_the_headline_does_not_give(self):
        r = {"mw": "8200", "price": "$12.5 billion", "parties": "CFE"}
        self.assertEqual(brief.detail(r, "Mexico set to approve 60 projects, 8,200 MW"), "USD 12.5 billion; parties: CFE. ")
        self.assertEqual(brief.detail(r, "Mexico set to approve 60 projects"), "8,200 MW; USD 12.5 billion; parties: CFE. ")
        self.assertEqual(brief.detail(r), "8,200 MW; USD 12.5 billion; parties: CFE. ")


class TheTwentySavedItems(unittest.TestCase):
    """The fixture: each item's printed line is what the session read and pinned, and passes the check."""

    def test_twenty_items(self):
        self.assertEqual(len(items()), 20)

    def test_each_item_prints_its_pinned_line_and_passes_the_check(self):
        for it in items():
            with self.subTest(it["event_id"]):
                out = brief.why_line(it["why"], it["head"])
                self.assertEqual(out, it["expected_why"])
                self.assertEqual(brief.detail(it, it["head"]), it["expected_detail"])
                if not it["fallback"]:
                    self.assertEqual(brief.why_check(out, it["head"]), [])
                self.assertNotIn(chr(0x2014), out)
                self.assertNotIn(chr(0x2013), out)

    def test_the_problems_the_check_found_are_as_pinned(self):
        for it in items():
            with self.subTest(it["event_id"]):
                self.assertEqual(brief.why_check(it["why"], it["head"]), it["problems"])

    def test_the_fixture_holds_each_kind_of_fault(self):
        kinds = {p.split(":")[0] for it in items() for p in it["problems"]}
        # no saved why line of the twenty has two sentences; that fault is pinned by TheRule above
        self.assertEqual(kinds, {"adjective", "figure of the headline"})


class WhereTheRuleLives(unittest.TestCase):
    """The scorer's prompt, the rubric, and every printed why line of the Digest and the Roundup."""

    def test_the_prompt_and_the_rubric_carry_the_rule(self):
        for text in (score.SYSTEM, score.RUBRIC):
            self.assertIn("consequence", text)
            for adj in brief.WHY_ADJECTIVES:
                self.assertIn(adj, text)
            self.assertIn("no figure the title already gives", text)

    def test_every_why_line_goes_with_its_headline(self):
        src = inspect.getsource(brief.main)
        self.assertGreaterEqual(src.count("why_line(r['why'], heads[r['cluster_id']])"), 3)
        self.assertNotIn("why_line(r['why'])", src)
        self.assertIn("why_line(r['why'], r['title'])", inspect.getsource(brief.policy_actions_lines))
        rsrc = inspect.getsource(roundup)
        self.assertNotIn("why_line(r['why'])", rsrc)
        self.assertGreaterEqual(rsrc.count("why_line(r['why'], heads[r['cluster_id']])"), 2)
        self.assertIn('top["title"]', inspect.getsource(roundup.policy_of_the_week))


if __name__ == "__main__":
    unittest.main()
