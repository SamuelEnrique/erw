"""Ready branch for /equities (session 11408, chain 770 part C; weekend page 2026-11-28, part 3.5, "a year's revenue
beside a quarter's in Every company": the other choice, add). Not the default: it waits for Samuel's ruling.

warehouse/derived/equity_page_files.py newest_year: each company of index.json carries the newest 12 months of revenue
it filed; site/app/equities/view.tsx draws it as a third line of the newest period's cell ("Year to <end>"), unless the
newest period is that year. Measured with the builder's function on the series files now on main (their rows are the
builder's own): 223 of the 243 companies with filings carry a year; 216 show it beside a shorter newest period (none
does on main). site/data/equities/index.json rebuilt at landing by the desk.

1. newest_year on a fixture: the newest year, the later filing where filed twice, none without a year.
2. On the series files now on main.
3. The page draws it only where the list carries it."""
import glob
import json
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
import equity_page_files as ep  # noqa: E402


def row(start, end, months, form, filed, revenue, acc="a"):
    return [start, end, months, int(end[:4]), "FY" if months == 12 else "Q", form, filed, revenue, None, None, None, None, acc, None]


class AYearsRevenue(unittest.TestCase):
    def test_the_rule(self):
        q = [row("2026-07-01", "2026-09-30", 3, "10-Q", "2026-11-01", 8),
             row("2025-01-01", "2025-12-31", 12, "10-K", "2026-02-20", 30),
             row("2025-01-01", "2025-12-31", 12, "10-K/A", "2026-04-01", 31, "b"),
             row("2024-01-01", "2024-12-31", 12, "10-K", "2025-02-20", 28)]
        y = ep.newest_year(q)
        self.assertEqual((y["period_end"], y["revenue"], y["form"]), ("2025-12-31", 31, "10-K/A"))
        self.assertIsNone(ep.newest_year([row("2026-07-01", "2026-09-30", 3, "10-Q", "2026-11-01", 8)]))
        self.assertIsNone(ep.newest_year([]))

    def test_on_the_series_files(self):
        n = with_year = 0
        for p in glob.glob(os.path.join(ROOT, "site", "data", "equities", "series", "*.json")):
            with open(p, encoding="utf-8") as f:
                s = json.load(f)
            if s.get("kind") != "company" or not s.get("quarterly"):
                continue
            self.assertEqual(s["quarterly_columns"], ep.QCOLS)
            n += 1
            with_year += ep.newest_year(s["quarterly"]) is not None
        self.assertGreater(n, 0)
        self.assertGreater(with_year, n // 2)

    def test_the_page(self):
        with open(os.path.join(ROOT, "site", "app", "equities", "view.tsx"), encoding="utf-8") as f:
            view = f.read()
        self.assertIn("const y = c.newest_year;", view)
        self.assertIn('pfKey(LIST, ["companies", i, "newest_year", "revenue"])', view)
        with open(os.path.join(ROOT, "warehouse", "derived", "equity_page_files.py"), encoding="utf-8") as f:
            self.assertIn('"newest_year": newest_year(q)', f.read())


if __name__ == "__main__":
    unittest.main()
