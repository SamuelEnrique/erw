"""Session 4219 (chain 239): the forecast page's faults found on the local production build, each held by a test.

Energy Research Warehouse (ERW). No network, no build. docs/reviews/forecast-faults-2026-11-13.md, rows 6 to 12: the page
was read in headless Chrome at 1280 and 390 px (runs/w4/read_page.mjs, not in git); these tests read the code that each
fix changed, so the fault cannot come back unnoticed.
"""

import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")


def read(*p):
    with open(os.path.join(*p), encoding="utf-8") as f:
        return f.read()


class TheFaults(unittest.TestCase):
    def setUp(self):
        self.page = read(SITE, "app", "impact", "Forecast.tsx")
        self.ui = read(SITE, "lib", "forecastui.ts")

    def test_6_a_year_has_no_thousands_separator(self):
        self.assertIn('if (f.key === "start") return String(val);', self.page)

    def test_7_the_readers_own_rate_only_where_no_statute_is_held(self):
        for key in ("own", "ownyears"):
            line = next(l for l in self.ui.splitlines() if l.strip().startswith(f'{{ key: "{key}",'))
            self.assertIn("applies: (t, s, P) => !statuteHeld(t, s, P)", line, key)
        self.assertRegex(self.ui, r'statuteHeld = \(t: TechKey, s: string, P: Params\) =>\s*\n\s*\(P\.property\.states\[s\]\?\.rules \?\? \[\]\)\.some\(\(r\) => r\.technologies\.includes\(t\) && r\.kind !== "valuation"\)')

    def test_9_a_tax_not_held_is_left_out_of_the_chart_and_an_empty_year_is_zero(self):
        self.assertIn('...(r.property.held ? [{ name: "Property"', self.page)
        self.assertIn('...(r.sales.held ? [{ name: "Sales and use"', self.page)
        self.assertIn("r.years[i].sales ?? 0", self.page)

    def test_10_the_chart_does_not_write_its_unit_twice(self):
        self.assertIn('const short = (v: number) => usd(v).replace(/^USD /, "");', self.page)
        self.assertRegex(self.page, r'unit="USD \(2025\)" kind="stacked" scale="linear" fmt=\{short\}')

    def test_11_the_table_of_a_and_b_fits_a_phone_and_its_missing_words_are_short(self):
        self.assertIn('sm:table sm:table-fixed" data-compare-table="1"', self.page)
        self.assertIn('className="grid grid-cols-2 border-b border-rule align-top sm:table-row" data-row={l.key}', self.page)
        self.assertNotIn("{why ?? \"not held\"}</span>", self.page, "the reason is the hover, not the cell's text")

    def test_12_a_charts_words_are_a_tip_not_part_of_its_title(self):
        self.assertNotRegex(self.page, r'tip="[^"]')
        self.assertEqual(len(re.findall(r"tip=\{<Tip id=", self.page)), 2)


if __name__ == "__main__":
    unittest.main()
