"""Session 10210 (curtailment audit, finding 5): two sentences say ISO-NE's curtailment figure is not pulled or not held.

The page's decision 11 (site/lib/decisions.ts, word for word docs/methods/curtailment.md) said "ISO-NE's monthly
undelivered energy is not pulled under its legal notice", and the where-when view's hover (warehouse/derived/where_when.py,
curtailment_not_held) says "no curtailment figure of ISO-NE is held". The owner ruled on 7 October 2026 that it be pulled
and held internal, not shown; session 149 pulled it into isone_ddg_undelivered_monthly, and the page's own face line says
"Held, not shown". Words only: the decision and its note say it is held internal and not shown; the builder's hover says
the same from the view file's next build (the committed where_when.json is the data machine's to rebuild).
"""
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def read(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class IsoNeHeld(unittest.TestCase):
    def test_the_note_records_the_pull_and_the_face_says_held(self):
        n = read("docs", "methods", "curtailment.md")
        self.assertIn("Ruled on 7 October 2026 (the owner): pulled and held internal, not shown.", n)
        self.assertIn("isone_ddg_undelivered_monthly", n)
        self.assertIn("Held, not shown.", read("site", "lib", "freeenergy.ts"))

    def test_decision_11_says_held_internal_in_the_list_and_the_note(self):
        d, n = read("site", "lib", "decisions.ts"), read("docs", "methods", "curtailment.md")
        for s in (d, n):
            self.assertNotIn("ISO-NE's monthly undelivered energy is not pulled", s)
            self.assertIn("ISO-NE's monthly undelivered energy is held internal and not shown under its legal notice (pulled on the owner's ruling of 7 October 2026)", s)

    def test_the_where_when_builder_says_held_not_shown(self):
        w = read("warehouse", "derived", "where_when.py")
        self.assertNotIn('"isone": "no curtailment figure of ISO-NE is held"', w)
        self.assertTrue(re.search(r'"isone": "ISO-NE\'s monthly undelivered energy is held internal under its legal notice and not shown"', w))
        for s in (w, read("site", "lib", "decisions.ts")):
            self.assertNotIn(chr(0x2014), s)


if __name__ == "__main__":
    unittest.main()
