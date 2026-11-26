"""Audit of "Energy per AI query, as published" (/ai-energy), finding 5 (session 10221,
docs/reviews/ai-energy-model-audit-2026-11-26.md): the headline "Newest" printed July 9, 2026, the date of Microsoft's
fact sheet. The fact sheet prints no date: the ERW took it from the address of Microsoft's post that launched the report.
Meta's index is dated the same way, from Meta's news page. 2 of the 9 dates are the ERW's reading, and the headline did not
say so (each figure's hover does, in its basis).

1. The page's file: the newest row is Microsoft's, and its basis says the fact sheet prints no date; Meta's basis says its
   date is the launch's. Passes on main.
2. The fix on this branch, words only: the headline's note says how a date is taken. Fails on main."""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheNewestSaysWhoseDate(unittest.TestCase):
    def test_two_dates_are_not_printed_by_the_publication(self):
        rows = json.loads(src("site", "data", "ai_energy.json"))["rows"]
        newest = sorted(rows, key=lambda r: r["event_date"], reverse=True)[0]
        self.assertEqual((newest["event_id"], newest["event_date"]), ("ai_energy:microsoft_2026_1", "2026-07-09"))
        self.assertIn("the fact sheet prints no date of its own", newest["x_basis"])
        self.assertEqual(sorted({r["parties"] for r in rows if "the date is" in r["x_basis"]}), ["Meta", "Microsoft"])

    def test_the_headline_says_how_a_date_is_taken(self):
        self.assertIn("note={`${newest.parties}: ${newest.x_title}. A date is the one the publication prints, or, for a company report that prints "
                      "none, the date of the post that launched it (the figure's hover says which)`}", src("site", "app", "ai-energy", "page.tsx"))


if __name__ == "__main__":
    unittest.main()
