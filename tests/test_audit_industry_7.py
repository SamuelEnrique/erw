"""Session 10224 (chain 710, the industry page audit, finding 7, for Samuel's ruling): one month against twelve.

/industry's only change figure for the sector is the newest month against the same month a year before. On the page file
of 19 November 2026 that is July 2026: total -1.9 percent, petroleum -6.6, coal -8.7; the twelve months to July 2026
against the twelve before are +0.4, +0.8 and -6.0. A test that shows it, not a fix: the figure is the owner's to change.
docs/reviews/industry-model-audit-2026-11-26.md.
"""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class OneMonthAgainstTwelve(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(ROOT, "site", "data", "industry.json"), encoding="utf-8") as f:
            m = json.load(f)["monthly"]
        self.m, self.i = m, {x: n for n, x in enumerate(m["months"])}
        self.last = [x for x in m["months"] if m["by_source"]["total"][self.i[x]] is not None][-1]

    def v(self, key, month):
        return self.m["by_source"][key][self.i[month]]

    def twelve(self, key, y, mo):
        out = 0.0
        for k in range(12):
            mm, yy = mo - k, y
            while mm <= 0:
                mm, yy = mm + 12, yy - 1
            out += self.v(key, f"{yy}-{mm:02d}")
        return out

    def changes(self, key):
        y, mo = int(self.last[:4]), int(self.last[5:])
        one = 100 * (self.v(key, self.last) / self.v(key, f"{y - 1}-{mo:02d}") - 1)
        roll = 100 * (self.twelve(key, y, mo) / self.twelve(key, y - 1, mo) - 1)
        return round(one, 1), round(roll, 1)

    def test_the_file_of_19_november(self):
        if self.last != "2026-07":
            self.skipTest(f"the page file now ends {self.last}; the figures below are those of the file ending 2026-07")
        self.assertEqual(self.changes("total"), (-1.9, 0.4))
        self.assertEqual(self.changes("petroleum"), (-6.6, 0.8))
        self.assertEqual(self.changes("coal"), (-8.7, -6.0))

    def test_the_two_can_differ_in_sign(self):
        one, roll = self.changes("total")
        self.assertIsInstance(one, float)
        self.assertIsInstance(roll, float)


if __name__ == "__main__":
    unittest.main()
