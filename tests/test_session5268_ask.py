"""Session 5268 (chain 256): rule 11, to stop, and the query tool's words for the window field.

Energy Research Warehouse (ERW). The chat's ten rules said nothing about stopping: of the 463 tool calls the platform
set's 80 figure answers made on 13 November 2026, 257 came after a result already held the figure
(warehouse/chat/eval/calls_after.py). Rule 11 says when to stop, and what the window field of session 5267 settles; it
keeps the one check a window cannot make (a row of a table of days or longer that covers part of its period). The rule
is the shared prompt's, so it is in both loops; Ask ERCOT's own rules are not changed.

No model, no network: the sources and the exported spec.
"""
import json
import os
import re
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "chat"))
import ask  # noqa: E402
import tools  # noqa: E402


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheRule(unittest.TestCase):
    def rule(self):
        m = re.search(r"^11\. (.*)$", ask.RULES, re.M)
        self.assertIsNotNone(m)
        return m.group(1)

    def test_eleven_rules_in_order_and_the_last_line_as_it_was(self):
        self.assertEqual(re.findall(r"^(\d+)\. ", ask.RULES, re.M), [str(n) for n in range(1, 12)])
        self.assertTrue(ask.RULES.rstrip().endswith("not_in_warehouse (true or false)."))
        self.assertIn("6. You have at most 12 tool calls.", ask.RULES)          # the limit is not changed
        self.assertEqual(ask.MAX_TOOL_CALLS, 12)

    def test_it_says_when_to_stop_and_what_is_not_a_second_source(self):
        r = self.rule()
        self.assertTrue(r.startswith("Stop when you have the answer. When a tool result holds the figure the question asks for, write the answer."))
        self.assertIn("Do not ask the same rows again with another grouping, time zone, aggregation or filter to confirm a figure you already have", r)
        self.assertIn("the same rows read another way are not a second source", r)
        self.assertIn("Make any other further call only for something you can name: a figure the results do not hold, or a second figure the question asks for.", r)

    def test_it_names_the_window_field_and_what_a_short_window_obliges(self):
        r = self.rule()
        self.assertIn("a query of a series with start and end returns window (steps_held, steps_in_window, whole, and the runs of steps missing)", r)
        self.assertIn("no count and no regrouping is needed for it", r)
        self.assertIn("when window.whole is false, say which part is held and give a figure only as the figure of the steps held, never as the whole period's", r)

    def test_it_keeps_the_check_a_window_cannot_make(self):
        r = self.rule()
        self.assertIn("a row of a table of days, months or years may cover only part of its period", r)
        self.assertIn("da_hours or days_held", r)
        self.assertIn("read it once before giving the row's figure as the period's", r)

    def test_the_rules_before_it_are_word_for_word_what_they_were(self):
        # rules 1 to 10 as main held them before this session (the stored spec of the session before is not kept: their
        # first words and the rule that every number comes from a tool are what a reader would miss first)
        for words in ("1. Answer only from tool results. Every number you write", "2. Cite every number.", "3. If the warehouse does not hold what the question asks",
                      "7. Keep the answer short", "10. USD per kW: a query of battery_stack_monthly"):
            self.assertIn(words, ask.RULES)
        self.assertNotIn(chr(0x2014), ask.RULES)
        self.assertNotIn(chr(0x2013), ask.RULES)


class TheToolAndTheSpec(unittest.TestCase):
    def test_the_query_tool_says_what_window_is(self):
        q = next(t for t in tools.TOOLS if t["name"] == "query")
        self.assertIn("With both start and end, a series result also says under window whether the window is whole: the steps held, the steps the window has at the table's step, and the runs of steps missing.", q["description"])
        self.assertNotIn("window", q["input_schema"]["properties"])              # a field of the answer, not an argument

    def test_the_sites_spec_is_the_export_of_both(self):
        spec = json.loads(src("site", "lib", "chat", "spec.json"))
        self.assertEqual(spec["system"], ask.SYSTEM)
        self.assertIn("\n11. Stop when you have the answer.", spec["system"])
        self.assertEqual(next(t for t in spec["tools"] if t["name"] == "query")["description"], next(t for t in tools.TOOLS if t["name"] == "query")["description"])
        self.assertEqual(spec["max_tool_calls"], 12)

    def test_ask_ercots_own_rules_are_not_changed(self):
        ercot = json.loads(src("site", "lib", "chat", "spec_ercot.json"))
        self.assertNotIn("Stop when you have the answer", ercot["system"])
        self.assertNotIn("Stop when you have the answer", src("warehouse", "chat", "ercot.py"))

    def test_the_method_note_says_it(self):
        note = src("docs", "methods", "ask.md")
        self.assertIn("## A window says whether it is whole, and the chat is told to stop (14 November 2026, sessions 5266 to 5268)", note)
        self.assertIn("**Rule 11, to stop.**", note)


if __name__ == "__main__":
    unittest.main()
