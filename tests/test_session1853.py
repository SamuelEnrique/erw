"""Session 1853 (chain 213): the deal tracker's faults 7 and 8 of docs/reviews/deals-faults-2026-11-11.md.

Energy Research Warehouse (ERW). The month bars of the tracker and the two charts by quarter of /deals?view=charts
take the brand's hover card (components/tool/BarsHover.tsx, session 2201): the fog card with the period and each
series' figure, by pointer and by the arrow keys. The SVG's own <title> stays for a reader with no script.
"""
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheMonthBars(unittest.TestCase):
    def test_the_tracker_wraps_its_month_bars_in_the_hover_card(self):
        v = src("site", "app", "deals", "v2", "view.tsx")
        self.assertIn('import { BarsHover } from "@/components/tool/BarsHover";', v)
        self.assertIn('<BarsHover id="deals-months" left={40} right={10} width={760}', v)
        # the card's edges are the SVG's own (MonthBars: W = 760, L = 40, R = 10)
        self.assertIn("const W = 760, H = 260, L = 40, R = 10", v)
        self.assertIn('lines: [{ name: m.n === 1 ? "deal" : "deals", color: "var(--color-accent)", text: whole(m.n) }]', v)
        self.assertIn("<MonthBars ms={months(all, shown)} />\n                </BarsHover>", v)
        # the <title> a month stays
        self.assertIn("<title>{`${monthWords(m.month)}: ${m.n} ${m.n === 1 ? \"deal\" : \"deals\"}`}</title>", v)


class TheChartsByQuarter(unittest.TestCase):
    def test_the_mw_stack_and_the_ai_share_take_the_card(self):
        c = src("site", "app", "deals", "charts", "view.tsx")
        self.assertIn('import { BarsHover } from "@/components/tool/BarsHover";', c)
        self.assertIn('<BarsHover id="deals-mw-quarter" left={56} right={12} width={W}', c)
        self.assertIn('<BarsHover id="deals-ai-share" left={56} right={12} width={W}', c)
        # the edges are the charts' own
        self.assertEqual(len(re.findall(r"const L = 56, R = 12, top = 10, H = 2[0-9]{2}, B = 24;", c)), 3)
        # one card a quarter: each kind of supply in its own color, the total, and the count that state no MW
        self.assertIn("name: `${g[1]} (${p.deals})`, color: g[2], text: `${whole(p.mw)} MW`", c)
        self.assertIn('{ name: "MW stated", color: T, text: `${whole(s.total)} MW` }', c)
        self.assertIn("sub: `${whole(s.without)} deals of the quarter state no MW`", c)
        self.assertIn('{ name: "AI-power share", color: "var(--color-accent)", text: `${s.share}%` }', c)
        self.assertIn('lines: s.share === null ? [{ name: "MW stated", color: T, text: "none" }]', c)
        # the point chart and the parties' bars keep their titles and their tables
        self.assertIn('data-chart="price"', c)
        self.assertIn('data-chart="party"', c)
        self.assertEqual(c.count("<BarsHover "), 2)

    def test_the_card_component_is_the_brands(self):
        b = src("site", "components", "tool", "BarsHover.tsx")
        self.assertIn('data-chart-card="1"', b)
        self.assertIn('e.key === "ArrowRight"', b)
        self.assertIn("border border-rule bg-paper", b)


if __name__ == "__main__":
    unittest.main()
