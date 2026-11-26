"""Session 10219 (chain 710, the conditions audit, finding 9): /conditions counts "constraints binding" and
"constraint-hours" as the rows of constraints_binding_hourly, whose key is constraint and contingency
(docs/methods/grid_congestion.md, decision 2), and its hover said "(constraint, hour) pairs". A constraint binding under
two contingencies in an hour counts twice. Words only: both constraint charts say what the count holds. How far the
count stands above distinct constraints needs the table (a data request). docs/reviews/conditions-model-audit-2026-11-26.md.
"""
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as fh:
        return fh.read()


class TheCountIsOfPairs(unittest.TestCase):
    def test_the_builder_counts_rows_of_a_table_keyed_by_contingency(self):
        b = src("warehouse", "derived", "conditions_page.py")
        self.assertIn('g = c.groupby("ts_utc")["abs"].agg(cons_n="count", cons_max="max")', b)
        self.assertIn("so a CAISO entity is `caiso:<NOMOGRAM_ID_XML>|<CONSTRAINT_CAUSE>`", src("docs", "methods", "grid_congestion.md"))

    def test_the_page_says_contingency_pairs(self):
        s = src("site", "app", "conditions", "page.tsx")
        self.assertNotIn("The number of (constraint, hour) pairs", s)
        self.assertIn("The number of (constraint, contingency, hour) rows", s)
        self.assertEqual(s.count("${CONS_COUNT_WORDS}`} />}>"), 2)
        self.assertIn("binds under two contingencies in the same hour counts twice", s)
        self.assertNotIn("export const CONS_COUNT_WORDS", s)

    def test_the_note_says_it(self):
        self.assertIn("the (constraint, contingency) pairs that bound in the hour", src("docs", "methods", "grid_conditions.md"))


if __name__ == "__main__":
    unittest.main()
