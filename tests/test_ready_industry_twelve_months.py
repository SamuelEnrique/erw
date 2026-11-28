"""Session 11407 (chain 770, part C): the industry page's finding 7 readied for Samuel's ruling, twelve months beside one.

Carried over from session 10224's tests/test_audit_industry_7.py (branch wip/audit-industry-7), which showed that
/industry's only change figure for the sector was the newest month against the same month a year before. On this
branch the table "The latest month beside the same month a year before" gains a column: the twelve months to the newest
month against the twelve before. On the page file ending July 2026: total -1.9 percent on the month, +0.4 on the twelve
months; petroleum -6.6 and +0.8; coal -8.7 and -6.0. docs/reviews/industry-model-audit-2026-11-26.md, finding 7.
"""
import json
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class OneMonthAndTwelve(unittest.TestCase):
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

    def test_the_file_ending_july_2026(self):
        if self.last != "2026-07":
            self.skipTest(f"the page file now ends {self.last}; the figures below are those of the file ending 2026-07")
        self.assertEqual(self.changes("total"), (-1.9, 0.4))
        self.assertEqual(self.changes("petroleum"), (-6.6, 0.8))
        self.assertEqual(self.changes("coal"), (-8.7, -6.0))


class ThePageDrawsTheTwelveMonths(unittest.TestCase):
    def setUp(self):
        self.page = src("site", "app", "industry", "page.tsx")
        self.lib = src("site", "lib", "industry.ts")

    def test_the_lib_sums_twelve_months_or_none(self):
        self.assertIn("export function twelveMonthSum(f: IndustryFile, key: string, month: string): number | null", self.lib)
        body = self.lib.split("export function twelveMonthSum")[1].split("\n}\n")[0]
        self.assertIn("if (v === null) return null;", body)
        self.assertIn("k < 12", body)

    def test_the_table_has_the_twelve_month_column(self):
        self.assertIn("twelveMonthSum(F, k, last), tb = twelveMonthSum(F, k, yearAgo)", self.page)
        self.assertIn("k={`m12c-${k}`}", self.page)
        self.assertIn("`Twelve months to ${monthWords(last)}, change`", self.page)
        self.assertIn("the twelve months to it beside the twelve before", self.page)
        # the one-month change stays as it was
        self.assertIn("k={`mc-${k}`}", self.page)

    def test_the_note_and_the_replication_say_so(self):
        note = src("docs", "methods", "industry_page.md")
        self.assertIn("the twelve months to the newest month against the twelve months before them", note)
        rep = src("replication", "industry", "replicate.py")
        self.assertRegex(rep, re.escape('want[f"m12c-{k}"]'))

    def test_no_em_dash(self):
        for p in (("site", "app", "industry", "page.tsx"), ("site", "lib", "industry.ts"), ("docs", "methods", "industry_page.md")):
            self.assertNotIn(chr(0x2014), src(*p))


if __name__ == "__main__":
    unittest.main()
