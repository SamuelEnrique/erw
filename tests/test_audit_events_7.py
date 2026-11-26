"""Session 10225 (chain 710, the events audit, finding 7): the decisions block's "window" line said a window moves every
estimate, and its source said "the dates the pages cite are the operators' and the government's accounts", without
saying who chose the edges. They are the ERW's: no account names them, and three windows (the January 2025 cold, the
June 2025 heat, the January 2026 cold) were chosen from EIA's data around the highest hours, so their estimates are
larger than for a window fixed before looking. Cut to the days its own account names, Uri's pooled effect on demand
served is +269,649 MWh a day against the page's +155,795. Words only: the decisions block and docs/methods/events.md
say so; no figure moves. docs/reviews/events-model-audit-2026-11-26.md.
"""
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as fh:
        return fh.read()


class WhoChoseTheWindows(unittest.TestCase):
    def test_the_decisions_say_it(self):
        s = src("site", "app", "events", "Decisions.tsx")
        for w in ["The edges are the ERW's own choice: no operator's or government's account names them.",
                  "so their days were picked because demand was high", "their intervals do not allow for the choice",
                  "while the windows' edges are the ERW's",
                  "the ERW's own choice (session 39), around the rotating outages of 14 and 15 August",
                  "the ERW's own choice (session 39), around the days FERC and NERC give for the storm, 21 to 26 December",
                  "the week before the storm, the storm and the week after, the ERW's own choice (session 36B)"]:
            self.assertIn(w, s)
        self.assertIn("chosen from EIA's hourly data: the days of the highest hours", s, "the data-chosen windows keep their words")

    def test_the_note_says_it(self):
        n = src("docs", "methods", "events.md")
        self.assertIn("**Who chose the windows (session 10225, 26 November 2026).**", n)
        self.assertIn("the edges the ERW's own, and three windows chosen from the data around the highest hours (session 10225)", n)


if __name__ == "__main__":
    unittest.main()
