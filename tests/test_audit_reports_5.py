"""Session 10232, the report library audit (docs/reviews/reports-model-audit-2026-11-26.md), finding 5.

/reports/draft/ai-gigawatts leads its fifth finding with California's net imports by EIA's balance, 27.02 percent, the
figure its own banner (components/CaisoBreakNote.tsx, kind "imports") says reads high from 16 December 2025. Restated
from the extract and the daily interchange: on the year's complete days the balance and the pair sums differ by 1.10
points before 16 December 2025 (19.15 against 18.05 percent) and by 12.88 after (29.13 against 16.25). The ranking holds
(California imports the most either way). The fix is words only: where the region named is California, the sentence
says so at the figure and gives the pair sums the table already shows. No figure moves.
"""
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PAGE = os.path.join(ROOT, "site", "app", "reports", "draft", "ai-gigawatts", "page.tsx")


def src():
    with open(PAGE, encoding="utf-8") as f:
        return f.read()


class CaliforniasBalanceIsQualifiedAtTheFigure(unittest.TestCase):
    def test_the_banner_is_on_the_page(self):
        self.assertIn('<CaisoBreakNote kind="imports" />', src())

    def test_the_date_is_the_one_constant(self):
        # tests/test_session78.py: the join's date is written in lib/caisoJoin.ts and nowhere else in the site's code
        s = src()
        self.assertIn('import { caisoJoinDay } from "@/lib/caisoJoin";', s)
        self.assertIn("const joinDay = caisoJoinDay();", s)
        self.assertNotIn("16 December 2025", s)

    def test_the_fifth_finding_qualifies_californias_balance(self):
        s = src()
        self.assertIn('{imp1.id === "caiso" ? <>, which reads high for California from {joinDay}', s)
        self.assertIn("the pair sums give <N x={imp1.pair} /> percent", s)

    def test_section_six_qualifies_it_twice(self):
        s = src()
        self.assertIn("a balance that reads high from ${joinDay}, when EIA's generation total for California fell below CAISO's own supply", s)
        self.assertIn('{gapReg.id === "caiso" ? ` (in California, most of it is the break of ${joinDay}', s)

    def test_no_em_dash(self):
        self.assertNotIn(chr(0x2014), src())
        with open(__file__, encoding="utf-8") as f:
            self.assertNotIn(chr(0x2014), f.read())


if __name__ == "__main__":
    unittest.main()
