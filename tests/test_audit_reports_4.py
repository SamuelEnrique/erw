"""Session 10232, the report library audit (docs/reviews/reports-model-audit-2026-11-26.md), finding 4.

Sentences of /reports/draft/ai-gigawatts that its own table contradicts or does not hold (ai_power_regions as the live
set holds it, built 2 October 2026): "the gap between regions [in carbon] is still the largest of the five measures",
when hours at or above USD 200/MWh differ 8.42 times across the regions shown (21.47 across all seven) against
carbon's 2.88 (3.05); "Day-ahead prices ran above real time in every region but none"; "CAISO had the most [hours
above USD 1,000], 1", a tie with ERCOT; "CAISO is in the better half on 3 of its 5 measures, the most of any region", a
three-way tie with ERCOT and SPP; "which still burns more coal and gas in its mix" and "usually gas almost everywhere",
which no table the draft cites holds; "the worst weather the warehouse has measured", when the event table has held
cold_2026 since 19 October and the draft's table was built before it. The fix is words only. No figure moves.
"""
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PAGE = os.path.join(ROOT, "site", "app", "reports", "draft", "ai-gigawatts", "page.tsx")


def src():
    with open(PAGE, encoding="utf-8") as f:
        return f.read()


class TheSentencesFollowTheTable(unittest.TestCase):
    def test_the_widest_gap_is_named_not_asserted(self):
        s = src()
        self.assertNotIn("The gap between regions is still the largest of the five measures.", s)
        self.assertIn("const widest = [...gaps].sort((a, b) => b[1] - a[1])[0][0];", s)
        self.assertIn("carbon's gap is the widest", s)
        self.assertIn("the gap in ${widest} is wider than carbon's", s)

    def test_no_but_none(self):
        s = src()
        self.assertNotIn('|| "none"}: a buyer', s)
        self.assertIn("Day-ahead prices ran above real time in every region priced: </>", s)

    def test_ties_are_named_as_ties(self):
        s = src()
        self.assertIn("const topS1000 = s1000.filter((r) => r.s1000!.v === s1000[0].s1000!.v);", s)
        self.assertIn('{topS1000.length > 1 ? " each" : ""}', s)
        self.assertIn("const topTally = tally.filter((t) => t.n === tally[0].n);", s)
        self.assertIn("share the most: each is in the better half on", s)

    def test_no_claim_the_tables_do_not_hold(self):
        s = src()
        self.assertNotIn("which still burns more coal and gas in its mix", s)
        self.assertNotIn("which is usually gas almost everywhere", s)
        self.assertNotIn("pays a small premium for certainty", s)
        self.assertNotIn("the worst weather the warehouse has measured", s)
        self.assertIn("as they stood when the table was built (an event studied since is not in it)", s)

    def test_no_em_dash(self):
        self.assertNotIn(chr(0x2014), src())
        with open(__file__, encoding="utf-8") as f:
            self.assertNotIn(chr(0x2014), f.read())


if __name__ == "__main__":
    unittest.main()
