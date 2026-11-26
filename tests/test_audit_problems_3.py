"""Session 10229 (the problems audit, finding 3): "Who trades with whom" asks its ratios in the order a student reads,
"A was how many times B?" for A / B, as ruling 7a of 14 October 2026 has the other sets ask. Three questions read "how
many times B was A?" for A / B: read in statement order the answer is the inverse. The facts from the committed page
files (site/data/regions/trade/ten.json and trade_matrix.json); the words from site/lib/problemsets/who-trades-with-whom.ts.
"""
import json
import os
import re
import unittest

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
DATA = os.path.join(ROOT, "site", "data", "regions")
SRC = os.path.join(ROOT, "site", "lib", "problemsets", "who-trades-with-whom.ts")


class TheTwoReadingsDiffer(unittest.TestCase):
    def test_the_growth_read_either_way(self):
        mx = json.load(open(os.path.join(DATA, "trade_matrix.json"), encoding="utf-8"))
        whole = sorted((p for p in mx["region_pairs"] if p["a"] == "MIDW" and p["b"] == "TEN" and p["months_held"] == 12 and p["months_in_year"] == 12
                        and None not in (p["a_report_mwh"], p["b_report_mwh"], p["gap_mwh"])), key=lambda p: p["year"])
        y0, y1 = whole[0], whole[-1]
        later_over_earlier = y1["b_report_mwh"] / y0["b_report_mwh"]
        self.assertEqual(round(later_over_earlier, 2), 1.66)            # the key
        self.assertEqual(round(1 / later_over_earlier, 2), 0.60)       # the question read in order, until this session

    def test_the_midwest_read_either_way(self):
        t = json.load(open(os.path.join(DATA, "trade", "ten.json"), encoding="utf-8"))
        i = max(k for k, m in enumerate(t["months"]) if m < t["built"][:7])
        own, their = t["neighbors"]["MIDW"]["net_imports_mwh"][i], t["neighbors"]["MIDW"]["their_report_mwh"][i]
        self.assertNotEqual(round(own / their, 2), round(their / own, 2))


class TheWords(unittest.TestCase):
    def setUp(self):
        self.src = open(SRC, encoding="utf-8").read()

    def test_in_the_order_read(self):
        self.assertIn("and Tennessee's report was how many times the Southeast's?", self.src)
        self.assertIn("and Tennessee's report was how many times the Midwest's?", self.src)
        self.assertIn("its ${y1} flow was how many times its ${y0} flow?", self.src)
        self.assertIsNone(re.search(r"how many times the (Southeast|Midwest)'s report was Tennessee's", self.src))
        self.assertNotIn("how many times its ${y0} flow was its ${y1} flow", self.src)

    def test_no_typed_count(self):
        self.assertNotIn("the sum of the four", self.src)
        self.assertNotIn(chr(0x2014), self.src)


if __name__ == "__main__":
    unittest.main()
