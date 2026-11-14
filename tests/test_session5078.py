"""Session 5078 (chain 243, portable laptop window P1): battery faults row 11. The battery page's summary sentence read
"covered its debt -0.14 times" when the last twelve months did not pay the fixed O&M (CAISO, 8 hours, the day-ahead
schedule, on 13 November 2026: USD 85.65 per kW earned against a fixed O&M of 92). A negative coverage now says what it
means, and the keyed figure (bs|...|cover, read by check-values) stays in the sentence in both forms. No network, no
build: the source is read, as the tests of this page's words do.
"""
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "site", "app", "cost-of-power", "battery", "Scenarios.tsx")


class NegativeCoverage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(SRC, encoding="utf-8") as f:
            cls.src = f.read()

    def test_both_sentences_say_a_negative_coverage_in_words(self):
        branches = re.findall(r'cover !== null && cover < 0 \? <span data-cover-negative="1">did not earn its fixed O&amp;M, so nothing '
                              r'was left for its debt \(coverage <V pre=\{key\} s="cover" v=\{cover\} keyed=\{(keyed|false)\} /> times\)\.</span> '
                              r': <>covered its debt <V pre=\{key\} s="cover" v=\{cover\} keyed=\{(keyed|false)\} /> times\.</>', self.src)
        self.assertEqual(sorted(b[0] for b in branches), ["false", "keyed"])
        for a, b in branches:
            self.assertEqual(a, b)                      # the same key setting in both words

    def test_no_debt_still_comes_first(self):
        self.assertEqual(self.src.count('{noDebt ? <span data-no-debt="1">has no debt to cover.</span> : cover !== null && cover < 0 ?'), 2)

    def test_the_case_that_found_it(self):
        # coverage = (revenue - fixed O&M) / debt payment, per kW: 8 hours, USD 2,300 a kW, 20 percent debt at 8 percent, 20 years
        annuity = 0.08 / (1 - 1.08 ** -20)
        debt_kw = 2300 * 0.2 * annuity
        self.assertAlmostEqual(annuity, 0.101852, places=6)
        self.assertAlmostEqual((85.65 - 92) / debt_kw, -0.14, delta=0.005)

    def test_the_faults_file_has_the_row(self):
        with open(os.path.join(ROOT, "docs", "reviews", "battery-faults-2026-11-13.md"), encoding="utf-8") as f:
            text = f.read()
        self.assertRegex(text, r"\| 11 \|.*covered its debt -0\.14 times.*\| fixed \(session 5078\) \|")


if __name__ == "__main__":
    unittest.main()
