"""Session 2201 (chain 086, 23 October 2026): the demand growth explorer figure by figure, and the bar chart's hover card.
Every figure of /explore/demand-growth carries its source in its hover (components/Num.tsx `source`, from
lib/explore/source.ts and the figure's own key), each headline number a Tip with the same words; the brand's bar chart
(components/tool/GroupedBars.tsx) is wrapped in BarsHover, a client component that draws the brand's hover card for the
group under the pointer or the keyboard's arrows, the SVG and its figures as before. Energy Research Warehouse (ERW)."""
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
DASH = chr(0x2014)
FILES = [("site", "components", "tool", "BarsHover.tsx"), ("site", "components", "tool", "GroupedBars.tsx"),
         ("site", "app", "explore", "demand-growth", "page.tsx"), ("site", "scripts", "test-check-explorers.mjs"), ("tests", "test_session2201.py")]


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheBarChart(unittest.TestCase):
    def test_the_svg_is_wrapped_and_unchanged(self):
        s = src("site", "components", "tool", "GroupedBars.tsx")
        self.assertIn('import { BarsHover, type BarCard } from "./BarsHover";', s)
        self.assertIn("<BarsHover id={id} cards={cards} left={L} right={R} width={W}>", s)
        self.assertIn('<svg viewBox={`0 0 ${W} ${H}`} className="w-full" role="img" aria-label={label} data-bars={id}>', s)
        self.assertIn("{g.title ? <title>{g.title}</title> : null}", s, "the <title> a group stays for a reader with no script")
        # the card's words are written on the server: each group's label, and each series' figure through the chart's own fmt
        self.assertIn('text: g.values[k] === null ? "not held" : `${fmt(g.values[k] as number)} ${unit}`', s)
        self.assertNotIn('"use client"', s)

    def test_the_wrapper_is_a_client_component_with_the_brands_card_and_the_keyboard(self):
        s = src("site", "components", "tool", "BarsHover.tsx")
        self.assertTrue(s.startswith('"use client";'))
        self.assertIn('data-chart-card="1"', s)
        self.assertIn("border border-rule bg-paper px-3 py-2 text-xs", s, "fog with a rule-colored edge, as svgchart's Card")
        self.assertIn('className="font-mono text-ink"', s, "a figure in mono")
        for key in ("ArrowRight", "ArrowLeft", "Escape"):
            self.assertIn(key, s)
        self.assertIn("tabIndex={0}", s)
        self.assertIsNone(re.search(r"#[0-9a-fA-F]{3,6}\b", s), "no hex value in a component")
        self.assertNotIn("toFixed", s)
        self.assertNotIn("toLocaleString", s)

    def test_every_page_that_draws_the_chart_is_known(self):
        pages = sorted(p for p in ["site/app/cost-of-power/seller/page.tsx", "site/app/datacenters/GridsView.tsx", "site/app/explore/demand-growth/page.tsx"]
                       if "GroupedBars" in src(*p.split("/")))
        self.assertEqual(len(pages), 3)


class ThePage(unittest.TestCase):
    def test_every_figure_passes_its_source_and_each_headline_a_tip(self):
        p = src("site", "app", "explore", "demand-growth", "page.tsx")
        self.assertIn('import { sourceOf } from "@/lib/explore/source";', p)
        self.assertEqual(p.count("<Num "), 1, "every figure is drawn through the one n helper")
        self.assertIn("source={sourceOf(key(entity, v, y), gridName(entity))}", p)
        self.assertEqual(p.count("tip={"), 3)
        self.assertIn('tipOf("growth",', p)
        self.assertIn('tipOf("mw",', p)
        self.assertEqual(p.count('tipOf("third",'), 3)

    def test_the_check_fixture_holds_a_bar_chart(self):
        s = src("site", "scripts", "test-check-explorers.mjs")
        self.assertIn('data-bars="c"', s)
        self.assertIn("three charts read", s)

    def test_no_em_dash_in_the_files(self):
        for parts in FILES:
            self.assertNotIn(DASH, src(*parts), "/".join(parts))


if __name__ == "__main__":
    unittest.main()
