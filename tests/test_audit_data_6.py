"""Audit of the data pages, finding 7 (session 10233, docs/reviews/data-model-audit-2026-11-26.md): /data/faults states
the rule for impossible values and says "A value that fails is used for nothing, and nothing is filled." The rule's own
code (warehouse/derived/impossible_hours.py) holds it for the tables in HELD: their builders write what they wrote
before until a person approves, so those tables still hold values the rule would leave out (docs/methods/
impossible_hours.md marks them Held and gives what applying the rule would change).

1. HELD names tables, and the method marks each of them Held. Passes on main.
2. The fix on this branch, words only: the page says a failing value is used for nothing in a table the rule is applied
   to, that a table the method marks Held still holds such values until a person approves, and that the method says
   what applying it would change. No figure moves. Fails on main."""
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def flat(s):
    return " ".join(s.split())


class TheRuleIsHeldForSomeTables(unittest.TestCase):
    def test_held_tables_are_built_without_the_rule(self):
        import impossible_hours
        self.assertEqual(len(impossible_hours.HELD), 0)   # wip/ready-data-impossible: the rule applied to all nine
        self.assertEqual(len(impossible_hours.HELD_UNTIL_RULED), 9)
        note = src("docs", "methods", "impossible_hours.md")
        section = note[note.index("## Every table that reads these values"):note.index("## What the held builds would change")]
        for t in impossible_hours.HELD_UNTIL_RULED:
            key = "carbon_intensity_hourly" if t.startswith("carbon_intensity_") else t   # the note writes `_daily`, `_monthly`
            line = next(l for l in section.splitlines() if l.startswith("| ") and f"`{key}`" in l)
            self.assertIn("**Applied** (held until the ruling", line, t)

    def test_the_page_says_so(self):
        page = flat(src("site", "app", "data", "faults", "page.tsx"))
        self.assertNotIn("5,000 MWh. A value that fails is used for nothing", page)
        self.assertIn("In a table the rule is applied to, a value that fails is used for nothing, and nothing is filled.", page)
        self.assertIn("rule applied from its next build (none is held for approval any longer)", page)   # wip/ready-data-impossible
        self.assertIn("the method says what applying it changes.", page)


if __name__ == "__main__":
    unittest.main()
