"""Session 472: the explorers' second charts (archive/sessions/SESSION_472_REPORT.md).

The chain asked for each explorer's second chart, the one its README names next, and none where no README names one.
No document names one, so the session added none; these tests hold its report to that and to the project's rules.
"""

import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
REPORT = os.path.join(ROOT, "archive", "sessions", "SESSION_472_REPORT.md")
EXPLORERS = ("/explore/ercot-peak-premium", "/explore/demand-growth", "/explore/interconnection")


def _report():
    with open(REPORT, encoding="utf-8") as f:
        return f.read()


class TheReport(unittest.TestCase):
    def test_no_em_or_en_dash(self):
        text = _report()
        self.assertNotIn("—", text)
        self.assertNotIn("–", text)

    def test_it_names_the_three_explorers(self):
        text = _report()
        for address in EXPLORERS:
            self.assertIn(address, text)

    def test_it_says_none_was_added_and_why(self):
        text = _report()
        self.assertIn("No second chart was added", text)
        self.assertIn("no README", text)
        self.assertIn("For Samuel's ruling", text)

    def test_every_method_note_it_cites_exists(self):
        for note in ("ercot_peak_premium.md", "demand_growth.md", "energy_projects.md"):
            self.assertIn(f"docs/methods/{note}", _report())
            self.assertTrue(os.path.exists(os.path.join(ROOT, "docs", "methods", note)), note)


if __name__ == "__main__":
    unittest.main()
