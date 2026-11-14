"""Session 5503 (chain 269, portable laptop window P1): two of chain 243's open rulings built on their defaults.

- Ruling 5, Research's final form (default: final as the note describes). The page says under each chart what makes it
  and when, in the words of docs/methods/automated_analysis.md "Final form", and the note records that the page is
  built as final on the default, with what "final" does not promise (today's chart follows the Digest).
- Ruling 6, the words for a negative coverage (default: as written by session 5078). The battery note now states them,
  and this test holds the note and the page's two sentences to the same words.
"""
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class ResearchFinalForm(unittest.TestCase):
    def test_each_chart_says_what_makes_it_and_when(self):
        page = read("site", "app", "research", "page.tsx")
        self.assertIn('<ToolSection title="Today\'s chart" id="today" note={TODAY_NOTE}>', page)
        self.assertIn('<ToolSection title={week ? `This week\'s chart, ${week}` : "This week\'s chart"} id="week" note={WEEK_NOTE}>', page)
        today = re.search(r'const TODAY_NOTE = "([^"]+)";', page).group(1)
        week = re.search(r'const WEEK_NOTE = "([^"]+)";', page).group(1)
        self.assertIn("by code with each Digest", today)
        self.assertIn("No person chooses it.", today)
        self.assertIn("the newest is shown with its date", today)
        self.assertIn("every Sunday at 23:00 UTC", week)
        self.assertIn("No person chooses it.", week)

    def test_the_clock_on_the_page_is_the_note_s_and_the_workflow_s(self):
        note = read("docs", "methods", "automated_analysis.md")
        self.assertIn("**Final, on the default (session 5503, 14 November 2026).**", note)
        self.assertIn("`.github/workflows/roundup.yml`, Sundays at 23:00 UTC", note)
        self.assertIn("**What \"final\" does not promise.**", note)
        wf = read(".github", "workflows", "roundup.yml")
        self.assertRegex(wf, r"cron:\s*['\"]0 23 \* \* 0['\"]")
        # the daily chart is drawn by the Digest's writer
        self.assertIn("warehouse/news/brief.py asks for the day's candidates, chooses one, draws it", read("warehouse", "analysis", "findings", "daily_chart.py"))
        faults = read("docs", "reviews", "analysis-faults-2026-11-13.md")
        self.assertIn("Since session 5503 built as final on the default of chain 243's ruling 5", faults)


class NegativeCoverage(unittest.TestCase):
    WORDS = "did not earn its fixed O&M, so nothing was left for its debt (coverage"

    def test_the_note_and_the_page_say_the_same(self):
        note = read("docs", "methods", "battery_earns_algorithm.md")
        self.assertIn(f'"{self.WORDS} Z times)."', note)
        self.assertIn("kept on the default of the owner's open ruling 6, session 5503", note)
        page = read("site", "app", "cost-of-power", "battery", "Scenarios.tsx")
        jsx = self.WORDS.replace("&", "&amp;")
        self.assertEqual(page.count(f'<span data-cover-negative="1">{jsx}'), 2)


class NoDash(unittest.TestCase):
    def test_no_dash(self):
        for rel in (("tests", "test_session5503.py"), ("site", "app", "research", "page.tsx"), ("docs", "methods", "automated_analysis.md"),
                    ("docs", "methods", "battery_earns_algorithm.md"), ("docs", "reviews", "analysis-faults-2026-11-13.md")):
            text = read(*rel)
            self.assertNotIn(chr(0x2014), text, rel)
            self.assertNotIn(chr(0x2013), text, rel)


if __name__ == "__main__":
    unittest.main()
