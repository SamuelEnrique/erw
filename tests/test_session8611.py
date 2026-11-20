"""Session 8611 (chain 504, 19 November 2026): the new pieces of the Grid tool set against the brand (docs/brand.md).

Energy Research Warehouse (ERW). The brand is the one design document. Read against it, the map and the region tabs
kept most of it by the site's own stylesheet (a region's tables take the dark rule under the header, the mono figures,
the first column kept in place and the fade at the edge from app/tokens.css). Three things did not, and are held here:
- section 6, direct labels: the region's hour by hour chart had a row of swatches above the plot. Each source is now
  named at the right end of its columns in its own color, as the site's other charts name their series;
- section 6, the hover card: each series named in its color with its figure in the mono face;
- section 3, a target on a phone is 44 px tall: the map's three zoom buttons (they were 32) and the names under the
  map (24), each 44 px below the small breakpoint and as they were above it.
The browser's proof is site/scripts/check-grid-map.mjs (the sizes at 390 px). Nothing here makes a request.
"""

import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EM = chr(0x2014)


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheBrandItself(unittest.TestCase):
    def test_the_three_rules_are_the_documents(self):
        b = src("docs", "brand.md")
        self.assertIn("**Direct labels:** a series is named at the end of its line, or on its bar, in its own color. No legend box.", b)
        self.assertIn("each series named in sans with its figure in mono", b)
        self.assertIn("44 px tall on a phone", b)


class TheHourByHourChart(unittest.TestCase):
    def setUp(self):
        self.c = src("site", "components", "grid", "RegionHours.tsx")

    def test_each_source_is_named_at_the_right_in_its_own_color(self):
        self.assertIn('import { LINE, stackNames, wrapName } from "@/lib/chartwrap";', self.c)
        self.assertIn("return stackNames(out, height - 6);", self.c)
        self.assertIn('<text key={e.key} x={L + plotW + 6} y={e.y + 4} fontSize="12" fill={e.color} data-hours-name={e.key}>', self.c)
        self.assertIn('out.push({ key: "demand", name: "Demand", color: "var(--color-ink)"', self.c)

    def test_there_is_no_row_of_swatches_above_the_plot(self):
        self.assertNotIn('aria-hidden="true"', self.c)
        self.assertNotIn("inline-block h-2.5 w-2.5", self.c)

    def test_room_is_kept_at_the_right_for_the_names_narrower_on_a_phone(self):
        self.assertIn("R = W < 520 ? 78 : 104", self.c)

    def test_the_card_names_each_series_in_its_color_with_its_figure_in_mono(self):
        self.assertIn('<span style={{ color: l.color }}>{l.label}: </span><span className="font-mono text-ink">{show(l.values[at])}</span>', self.c)
        self.assertIn('data-chart-card="1"', self.c)
        self.assertIn("border border-rule bg-paper", self.c)                 # the shared card's own classes: no shadow, a rule-colored edge
        self.assertNotIn("shadow", self.c)

    def test_no_color_is_written_as_a_hex_value(self):
        import re
        self.assertEqual(re.findall(r"#[0-9A-Fa-f]{6}\b", self.c), [])
        self.assertEqual(re.findall(r"#[0-9A-Fa-f]{6}\b", src("site", "app", "network", "MapDecisions.tsx")), [])


class TheTargetsOnAPhone(unittest.TestCase):
    def setUp(self):
        self.m = src("site", "app", "network", "NetworkMap.tsx")

    def test_the_zoom_buttons(self):
        self.assertEqual(self.m.count('className="h-11 w-11 border border-rule bg-panel text-ink disabled:text-muted sm:h-8 sm:w-8"'), 2)
        self.assertIn('className="h-11 border border-rule bg-panel px-2 text-ink disabled:text-muted sm:h-8"', self.m)

    def test_the_names_under_the_map(self):
        self.assertIn("inline-flex min-h-11 items-center text-left underline decoration-dotted underline-offset-2 sm:min-h-6", self.m)

    def test_the_check_reads_forty_four_at_390(self):
        s = src("site", "scripts", "check-grid-map.mjs")
        self.assertIn("sizes.every((s) => s[0] >= 44 && s[1] >= 44)", s)
        self.assertIn("kbd.listed.every((h) => h >= 44)", s)


class TheTablesTakeTheBrandFromTheStylesheet(unittest.TestCase):
    def test_a_regions_table_is_in_the_frame_the_stylesheet_styles(self):
        v = src("site", "components", "grid", "RegionViews.tsx")
        self.assertIn('<div className="overflow-x-auto" data-region-table={name}>', v)
        self.assertIn('<th key={i} scope="row" className="py-1 pr-3 text-left font-normal">{c}</th>', v)
        self.assertIn('<td key={i} className="py-1 pr-3 text-right">{c}</td>', v)
        css = src("site", "app", "tokens.css")
        self.assertIn(".brand-a .overflow-x-auto table:not([data-scenario-table]) th:first-child,", css)    # the first column kept in place
        self.assertIn(".brand-a tbody td.text-right,", css)                                                  # the mono figures
        self.assertIn("border-bottom: 1px solid var(--color-ink);", css)                                     # the one dark rule under the header

    def test_no_em_dash(self):
        for p in (("site", "components", "grid", "RegionHours.tsx"), ("site", "app", "network", "NetworkMap.tsx"), ("tests", "test_session8611.py")):
            self.assertNotIn(EM, src(*p), p)


if __name__ == "__main__":
    unittest.main()
