"""Session 9203 (chain 620, the desktop's second window, 20 November 2026): the COVID-19 page keeps to a phone's width
with a grid's chart switched to its table.

Energy Research Warehouse (ERW). Read on production at 390 px (`runs/c620w2/probe_wide.mjs`): `/events/covid-2020` is
390 px wide as it opens, and 392 px wide once CAISO's chart under "Each grid: daily demand served" is switched to its
table. The block of each grid is an item of a two-column grid with no `min-w-0`, so it grew to its table's width. The
block now carries `min-w-0`, as the site's other grid items do; the table scrolls inside its own frame.

Held here, on the source: the class on the block. The proof in a browser is the page at 390 px on a build. Nothing here
makes a request.
"""
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheBlock(unittest.TestCase):
    def setUp(self):
        self.page = src("site", "app", "events", "covid-2020", "page.tsx")

    def test_each_grid_block_keeps_to_its_column(self):
        self.assertIn('<div key={g.entity} className="min-w-0">', self.page)
        self.assertRegex(self.page, r'<div className="grid gap-6 md:grid-cols-2">\s*\{GRIDS\.map')

    def test_the_figures_are_unchanged(self):
        self.assertIn("Deepest weekly drop against the baseline: <N r={deep} />% in the week of {day(deep)}", self.page)

    def test_no_em_dash(self):
        self.assertNotIn(chr(0x2014), self.page)


if __name__ == "__main__":
    unittest.main()
