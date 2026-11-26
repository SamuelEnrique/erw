"""Session 10224 (chain 710, the industry page audit, finding 6): the MECS note's cross-check names end use as total.

docs/methods/eia_mecs_manufacturing.md set MECS 2022 against "total primary energy 26,076"; 26,076 is the Monthly Energy
Review's industrial end use (TNICBUS), the total with losses (TEICBUS) being 31,169. docs/reviews/industry-model-audit-2026-11-26.md.
"""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheCrossCheck(unittest.TestCase):
    """The 2022 sums in the page file (passes on main)."""

    def setUp(self):
        self.m = json.loads(src("site", "data", "industry.json"))["monthly"]

    def year(self, key):
        return sum(self.m["by_source"][key][self.m["months"].index(f"2022-{x:02d}")] for x in range(1, 13))

    def test_26076_is_end_use_and_the_total_is_31169(self):
        self.assertEqual(round(self.year("end_use_total")), 26076)
        self.assertEqual(round(self.year("total")), 31169)
        self.assertEqual(round(self.year("natural_gas")), 10781)
        self.assertEqual(round(self.year("coal")), 987)
        self.assertEqual(round(self.year("electricity_retail_sales")), 3482)


class TheWords(unittest.TestCase):
    """The note (fails on main, passes on the branch)."""

    def test_the_note_names_end_use(self):
        note = src("docs", "methods", "eia_mecs_manufacturing.md")
        self.assertNotIn("against total primary energy 26,076", note)
        self.assertIn("against the sector's end-use energy 26,076 (TNICBUS", note)
        self.assertNotIn(chr(0x2014), note)


if __name__ == "__main__":
    unittest.main()
