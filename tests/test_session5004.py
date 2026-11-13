"""Session 5004 (chain 233): Research (Automated Analysis, /research), its note and its width at 390.

Energy Research Warehouse (ERW). What is held to:

  the chart archive's entries may shrink and break a long word (an entry's raw id made /research 563 px wide at 390);
  the method note names /research, has a section "Final form" (each part, what makes it, its clock) before
    "Replication", and ends with a sign-off block for the owner;
  no em or en dash in what the session wrote.

    python -m unittest tests.test_session5004 -v
"""

import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
DASHES = (chr(0x2014), chr(0x2013))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheArchive(unittest.TestCase):
    def test_an_entry_may_shrink_and_break(self):
        css = src("site", "app", "tokens.css")
        rule = re.search(r"\.brand-a \.chart-archive li \{([^}]*)\}", css).group(1)
        self.assertIn("min-width: 0;", rule)
        self.assertIn("overflow-wrap: anywhere;", rule)


class TheNote(unittest.TestCase):
    def setUp(self):
        self.note = src("docs", "methods", "automated_analysis.md")

    def test_the_route(self):
        self.assertIn("on the site's `/research` (Research since session 238; `/analysis` redirects there).", self.note)

    def test_the_final_form(self):
        n = self.note
        self.assertLess(n.index("## Final form: what runs by itself, and what waits for a person (session 5004)"), n.index("## Replication (session 3701)"))
        for words in ("`.github/workflows/roundup.yml`", "Sundays 23:00 UTC", "`warehouse/analysis/findings/daily_chart.py`",
                      "`register_weekly_hunt.ps1`", "`/internal/findings`", "Whether this is the final form is the owner's word."):
            self.assertIn(words, n)

    def test_the_sign_off_ends_the_note(self):
        n = self.note.rstrip()
        parts = n.split("\n## ")
        self.assertTrue(parts[-1].startswith("Sign-off\n"))
        for line in ("- Signed off by:", "- Date:", "- Items left open, ruled, and how:"):
            self.assertIn(line, parts[-1])

    def test_no_dash(self):
        for d in DASHES:
            self.assertNotIn(d, self.note)
            self.assertNotIn(d, src("tests", "test_session5004.py"))


if __name__ == "__main__":
    unittest.main()
