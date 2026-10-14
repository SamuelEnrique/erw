"""Session 268: the chart palette and the small things (the chain of 14 October 2026).

Energy Research Warehouse (ERW). The owner's list: the eight-color colorblind-safe palette (Paul Tol) in docs/brand.md
and site/app/tokens.css for charts of many series, cardinal staying the highlight; a skip-to-content link; a custom
404 page; the eslint error of the battery page's Scenarios.tsx; check-values' floor; CLAUDE.md's line that named three
live pages when none is live.

What is held here: the eight tokens in the brand's token block, in order, and the brand document's table of them; the
skip link as the layout's first element, pointing at the main element's id; the not-found page in the brand's frame;
the revenue function made outside the component; the floor a page in check-values and its file's form; CLAUDE.md
naming no page as live. Nothing here sets the environment, reads a table or makes a request.
"""

import json
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TOL = ["4477AA", "66CCEE", "228833", "CCBB44", "EE6677", "AA3377", "BBBBBB", "EEAA44"]


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class ThePalette(unittest.TestCase):
    def test_the_eight_tokens_in_order_in_the_brand_block(self):
        css = src("site", "app", "tokens.css")
        block = css[css.index(".brand-a,\nbody:has(.brand-a) {"):]
        block = block[:block.index("}")]
        found = re.findall(r"--chart-series-(\d): #([0-9A-F]{6});", block)
        self.assertEqual([int(n) for n, _ in found], list(range(1, 9)))
        self.assertEqual([h for _, h in found], TOL)
        self.assertIn("--color-accent: #8C1515;", block)  # cardinal stays

    def test_the_brand_document_lists_them_and_keeps_cardinal_the_highlight(self):
        doc = src("docs", "brand.md")
        self.assertIn("### Many series (session 268)", doc)
        self.assertIn("**Cardinal stays the highlight:**", doc)
        for i, h in enumerate(TOL, 1):
            self.assertIn(f"| `--chart-series-{i}` | `#{h}` |", doc)


class TheSmallThings(unittest.TestCase):
    def test_the_skip_link_is_first_and_points_at_main(self):
        layout = src("site", "app", "layout.tsx")
        body = layout[layout.index("<body"):]
        # session 270: the first element of the header (the page's chrome), before the wordmark and the menu
        header = body[body.index("<header"):]
        self.assertLess(header.index('href="#content"'), header.index("<Wordmark"))
        self.assertLess(header.index('href="#content"'), header.index("<Nav"))
        self.assertIn(">Skip to content</a>", body)
        self.assertIn('<main id="content" tabIndex={-1}', body)

    def test_a_not_found_page_in_the_brand(self):
        page = src("site", "app", "not-found.tsx")
        self.assertIn("<Brand>", page)
        self.assertIn("No page at this address", page)
        self.assertIn("index: false", page)

    def test_the_battery_scenarios_make_no_function_that_changes_a_local_in_render(self):
        block = src("site", "app", "cost-of-power", "battery", "Scenarios.tsx")
        self.assertIn("function revenueAt(", block)
        self.assertIn("const revenue = useMemo(() => revenueAt(ms, need, state, stepCase), [ms, need, state, stepCase]);", block)
        self.assertLess(block.index("function revenueAt("), block.index("export function BatteryDecisions("))

    def test_check_values_has_a_floor_a_page(self):
        cv = src("site", "scripts", "check-values.mjs")
        self.assertIn('const FLOOR_FILE = path.join(here, "check-values-floor.json");', cv)
        self.assertIn("its floor is ${floor}", cv)
        self.assertIn("Math.min(10, count)", cv)
        self.assertIn("if (bad || n < 10) process.exit(1);", cv)
        path = os.path.join(ROOT, "site", "scripts", "check-values-floor.json")
        if os.path.exists(path):
            floor = json.loads(src("site", "scripts", "check-values-floor.json"))["floor"]
            self.assertGreater(len(floor), 20)
            for page, n in floor.items():
                self.assertTrue(page.startswith("/"), page)
                self.assertTrue(isinstance(n, int) and 0 <= n <= 10, page)

    def test_claude_md_names_no_page_live(self):
        text = src("CLAUDE.md")
        line = next(l for l in text.split("\n") if l.startswith("The pages open to visitors"))
        self.assertIn("none", line)
        self.assertNotIn("`/cost-of-power/battery`, `/network` and `/storage`. Every other page", line)

    def test_no_em_dash_in_what_the_session_wrote(self):
        for parts in (("tests", "test_session268.py"), ("site", "app", "not-found.tsx"), ("docs", "brand.md")):
            self.assertEqual(src(*parts).count(chr(0x2014)), 0, parts)


if __name__ == "__main__":
    unittest.main()
