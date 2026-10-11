"""Session 192: the Roundup's policy section drops a repeat of a story above, and is still written.

The dry run of week 2026-W41 was not written: a Department of Energy release was one of the week's five stories and,
as a policy action, a line under "Also this week", and the hard check (brief.assert_unique) refuses two items that
share a headline or a source address. The daily digest has dropped such a line since session 176
(brief.without_repeats); the Roundup now does the same (roundup.policy_section). No test reaches the network or a model.
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
URL = "https://www.energy.gov/articles/energy-department-announces-an-investment"

ABOVE = ["# ERW's Roundup, 2026-W41", "", "## The five stories of the week", "",
         "1. **Energy Department Announces an Investment to Boost Nuclear Power** (nuclear, 3 stories)  ",
         f"   Why it matters. Sources: [DOE]({URL}), [Reuters](https://www.reuters.com/x)",
         "2. **Another story** (power, 1 story)  ",
         "   Why. Sources: [AP](https://apnews.com/y)"]
TOP = ["**A permit for a reactor** (NRC notice, 2026-10-05; docket 50-615)", "",
       "The NRC has given a permit. [Source](https://www.federalregister.gov/d/1)", "",
       "Timeline: effective at once."]
TABLE = ["", "Table: `policy_actions` (scored with the news rubric) and `policy_reads`; every action is on [/policy](/policy)."]


def also(*lines):
    return ["", "Also this week:", ""] + list(lines)


class PolicySection(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, os.path.join(ROOT, "warehouse", "news"))
        try:
            import brief
            import roundup
        except Exception as exc:  # a machine without the Roundup's own imports
            raise unittest.SkipTest(f"roundup not importable here: {type(exc).__name__}")
        cls.brief, cls.roundup = brief, roundup

    def test_the_repeat_is_what_the_hard_check_refuses_whatever_the_headline(self):
        same_title = f"- Energy Department Announces an Investment to Boost Nuclear Power (DOE news release, 2026-10-08): why [source]({URL})"
        other_title = f"- DOE puts money into reactors in two states (DOE news release, 2026-10-08): why [source]({URL})"
        for line in (same_title, other_title):     # the publishers' own title (--no-model) and a headline a model wrote
            with self.assertRaises(RuntimeError) as e:
                self.brief.assert_unique(ABOVE + TOP + also(line) + TABLE)
            self.assertIn(URL, str(e.exception))

    def test_a_repeat_under_also_this_week_is_dropped_and_named(self):
        said = []
        rep = f"- Energy Department Announces an Investment to Boost Nuclear Power (DOE news release, 2026-10-08): why [source]({URL})"
        kept = "- A draft statement for four reactors (NRC notice, 2026-10-09): why [source](https://www.federalregister.gov/d/2)"
        out = self.roundup.policy_section(TOP + also(rep, kept) + TABLE, ABOVE, said.append)
        self.assertEqual(out, TOP + also(kept) + TABLE)
        self.assertEqual(len(said), 1)
        self.assertIn("dropped a repeat", said[0])
        self.assertEqual(self.brief.assert_unique(ABOVE + out), 3)

    def test_when_every_also_line_is_a_repeat_the_heading_goes_with_them(self):
        rep = f"- A second title for the same release (DOE news release, 2026-10-08): why [source]({URL})"
        out = self.roundup.policy_section(TOP + also(rep) + TABLE, ABOVE, lambda m: None)
        self.assertEqual(out, TOP + TABLE)
        self.assertNotIn("Also this week:", out)
        self.assertEqual(self.brief.assert_unique(ABOVE + out), 2)

    def test_a_section_without_a_repeat_is_unchanged(self):
        said = []
        lines = TOP + also("- A rule (FERC final rule, 2026-10-07): why [source](https://www.ferc.gov/r)") + TABLE
        self.assertEqual(self.roundup.policy_section(list(lines), ABOVE, said.append), lines)
        self.assertEqual(said, [])
        for plain in (["- no scored policy action is dated this week."], ["- policy_actions is not in the warehouse on this machine."], TOP + TABLE):
            self.assertEqual(self.roundup.policy_section(list(plain), ABOVE, said.append), plain)

    def test_the_roundup_writes_its_policy_section_through_it(self):
        src = open(os.path.join(ROOT, "warehouse", "news", "roundup.py"), encoding="utf-8").read()
        self.assertIn("policy_section(policy_of_the_week(start, cut, log), L, log)", src)
        self.assertEqual(src.count("+ policy_of_the_week(start, cut, log)"), 0)
        self.assertLess(src.index("policy_section(policy_of_the_week("), src.index("brief.assert_unique(L)"))

    def test_no_em_dash_in_this_sessions_files(self):
        for p in (os.path.join(ROOT, "warehouse", "news", "roundup.py"), os.path.abspath(__file__)):
            self.assertNotIn(chr(0x2014), open(p, encoding="utf-8").read(), p)


if __name__ == "__main__":
    unittest.main()
