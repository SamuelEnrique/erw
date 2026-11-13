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
        held = self.ui[self.ui.index("export const statuteHeld"):]
        held = held[:held.index(";\n")]
        self.assertIn("(P.property.states[s]?.rules ?? []).some((r) => r.technologies.includes(t)", held)
        # the kinds that leave years or the choice to the reader keep the own rate offered: Iowa's optional valuation,
        # Kansas's exemption (session 4223, for the years after it), Oregon's agreement (session 4225)
        for kind in ("valuation", "exempt_years", "capacity_option"):
            self.assertIn(f'r.kind !== "{kind}"', held, kind)

    def test_9_a_tax_not_held_is_left_out_of_the_chart_and_an_empty_year_is_zero(self):
        # fault 17: a property tax held for some years is drawn (not only one held for every year)
        self.assertIn('...(r.years.some((y) => y.property !== null) ? [{ name: "Property"', self.page)
        self.assertIn('...(r.sales.held ? [{ name: "Sales and use"', self.page)
        self.assertIn("r.years[i].sales ?? 0", self.page)
        # an operating year with no rule (after an exemption or agreement) stays null: the chart says "not held" for it
        self.assertIn('(r.years[i].phase === "construction" ? 0 : r.years[i].property)', self.page)

    def test_10_the_chart_does_not_write_its_unit_twice(self):
        self.assertIn('const short = (v: number) => usd(v).replace(/^USD /, "");', self.page)
        self.assertRegex(self.page, r'unit="USD \(2025\)" kind="stacked" scale="linear" fmt=\{short\}')

    def test_11_the_table_of_a_and_b_fits_a_phone_and_its_missing_words_are_short(self):
        self.assertIn('sm:table sm:table-fixed" data-compare-table="1"', self.page)
        self.assertIn('className="grid grid-cols-2 border-b border-rule align-top sm:table-row" data-row={l.key}', self.page)
        self.assertNotIn("{why ?? \"not held\"}</span>", self.page, "the reason is the hover, not the cell's text")

    def test_12_a_charts_words_are_a_tip_not_part_of_its_title(self):
        self.assertNotRegex(self.page, r'tip="[^"]')
        # every chart's tip is a Tip (two charts by year, and since session 4221 the taxes in other states)
        self.assertGreaterEqual(len(re.findall(r"tip=\{<Tip id=", self.page)), 2)
        self.assertEqual(len(re.findall(r"(?<![\w-])tip=", self.page)), len(re.findall(r"tip=\{<Tip id=", self.page)))

class Fault15(unittest.TestCase):
    def test_15_the_trimmed_parameters_keep_every_field_of_a_rule(self):
        # the browser's parameters are trimmed by name (lib/forecastdata.ts); a field of PropertyRule left out of the trim
        # is undefined in the page while the node tests (the full files) pass: Kansas's years were
        src = read(SITE, "lib", "forecast.ts")
        block = src[src.index("export type PropertyRule = {"):]
        block = block[len("export type PropertyRule = {"):block.index("};")]
        block = re.sub(r"/\*.*?\*/", "", block, flags=re.S)  # comments
        block = re.sub(r"\{[^{}]*\}", "", block)  # nested types (a tier's own fields come with r.tiers)
        keys = set(re.findall(r"\b([a-z_]+)\??:", block))
        self.assertIn("years", keys)
        data = read(SITE, "lib", "forecastdata.ts")
        trim = data[data.index("rules: v.rules.map((r) => ({"):]
        trim = trim[:trim.index("})) }]));") + 1]
        for k in sorted(keys):
            self.assertRegex(trim, rf"\b{k}:", k)


if __name__ == "__main__":
    unittest.main()
