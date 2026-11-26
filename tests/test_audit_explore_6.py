"""Session 10231 (chain 710, part D: the signature explorers audited, docs/reviews/explore-model-audit-2026-11-26.md,
finding 5).

/explore/demand-growth's decision "base-year" called 2019 "the first whole year the warehouse holds for every area".
The table's builder reads 2018's hours (for its test of each hour), and EIA's workbooks the warehouse holds are whole
for 2018 in all eight areas (docs/reviews/demand-model-audit-2026-11-26.md, finding 7, where the base itself is left
to the owner). Words only; no figure moves. Both tests run everywhere.
"""
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TwentyNineteenIsNotTheFirstYearHeld(unittest.TestCase):
    def test_the_builder_reads_the_year_before_the_base(self):
        b = src("warehouse", "derived", "demand_growth.py")
        self.assertRegex(b, r"(?m)^BASE = 2019$")
        self.assertIn(".year >= BASE - 1]", b)
        self.assertIn('x = x[x["year"] >= BASE]', b)

    def test_the_decision_says_2018_is_held(self):
        d = src("site", "app", "explore", "demand-growth", "Decisions.tsx")
        self.assertNotIn("the first whole year the warehouse holds for every area.", d)
        self.assertIn("2019, the last whole year before the pandemic and the first year the table writes. It is not the first whole year the warehouse holds: EIA's workbooks are whole for 2018 in every area, and the table's builder reads 2018's hours for its test of each hour.", d)
        self.assertIn("on 2018, CAISO's 2025 growth is -0.74 percent (+4.45 on 2019) and MISO's -0.63 (+2.20).", d)
        self.assertNotIn(chr(0x2014), d)


if __name__ == "__main__":
    unittest.main()
