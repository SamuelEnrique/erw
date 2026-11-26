"""Session 10214 (chain 710, part D: the demand page audited, docs/reviews/demand-model-audit-2026-11-26.md, finding 3).

The summary of /demand said "The growth is largest in January at 02:00 (+42.55 percent)" for ERCOT: the largest of 288
cells, one month of 2025 against the same month of 2019. The same rule with another last year names another cell, from
the page's own file (each whole year's month-and-hour means are in it): July at 02:00 to 2023, October at 16:00 to 2024.
"""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def largest(years, last):
    b, r = years["2019"], years[last]
    cs = [(round(100 * (r[k] - b[k]) / b[k], 2), k) for k in b if k.startswith("avg_demand_mw_m") and "_h" in k and k in r]
    return max(cs)


class TheCellThatGrewMost(unittest.TestCase):
    def test_the_cell_moves_from_year_to_year(self):
        y = json.loads(src("site", "data", "demand_growth.json"))["areas"]["ERCO"]["years"]
        self.assertEqual(largest(y, "2025"), (42.55, "avg_demand_mw_m01_h02"))
        self.assertEqual(largest(y, "2024")[1], "avg_demand_mw_m10_h16")
        self.assertEqual(largest(y, "2023")[1], "avg_demand_mw_m07_h02")
        self.assertEqual(y["2025"]["growth_pct_m01_h02"], 42.55)

    def test_the_summary_says_what_the_cell_is(self):
        page = src("site", "app", "demand", "page.tsx")
        self.assertNotIn("The growth is largest in {monthName(ex.most.month)}", page)
        self.assertIn("one month of {file.last_year} against the same month of {file.base}: a cold or hot month can make it, and the cell that grows most moves from year to year.", page)
        self.assertIn("**The cell that grew most (session 10214).**", src("docs", "methods", "demand_growth.md"))


if __name__ == "__main__":
    unittest.main()
