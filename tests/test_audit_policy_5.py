"""Audit of the policy monitor, finding 7 (session 10217, docs/reviews/policy-model-audit-2026-11-26.md): the method
note's section 16 said the monitor's charts show "the MW and USD the records state as their own summed by month" and
that each sum carries a `policysum` key. Since session 1876 (policy faults row 28) the table by month adds nothing: it
shows, for each month and unit, how many records state a figure and the largest (lib/policymonitor.ts, figureMonths;
app/policy/MonitorCharts.tsx, "the largest of each unit"), and keysOf gives no sum key.

1. Through the page's library source: the table by month is the largest of each unit, and no sum key is made. Passes
   on main.
2. The fix on this branch, words only: the note says so. Fails on main."""
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheNoteSaysTheChartsAddNothing(unittest.TestCase):
    def test_the_table_by_month_is_the_largest_of_each_unit(self):
        lib = src("site", "lib", "policymonitor.ts")
        self.assertIn("export function figureMonths(rows: MonitorRow[]): MonthFigure[]", lib)
        self.assertNotIn("policysum|", lib)
        self.assertIn("the largest of each unit", src("site", "app", "policy", "MonitorCharts.tsx"))

    def test_the_note_says_it(self):
        note = src("docs", "methods", "policy_monitor.md")
        self.assertNotIn("the MW and USD the records state as their own summed\nby month", note)
        self.assertIn("Since session 1876\n(policy faults row 28) that table adds nothing", note)
        self.assertIn("key of\nsession 3062 is no longer drawn", note)


if __name__ == "__main__":
    unittest.main()
