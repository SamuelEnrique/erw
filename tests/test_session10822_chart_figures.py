"""Session 10822 (chain 740): the shared chart writes a bar's figure only where the one before it is not at the same height.

A figure may run a quarter into each neighbour's column (session 314's rule, kept), which on /impact's datacenter put two
equal construction years side by side as "10,00010,000". The chart now decides, before drawing, which figures to write:
one wider than its column gives way to the written figure before it when both sit within a line's height. The hover and
the table keep every value. No request, no model call."""
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHART = os.path.join(ROOT, "site", "components", "tool", "SeriesChart.tsx")


class FiguresGiveWay(unittest.TestCase):
    def setUp(self):
        with open(CHART, encoding="utf-8") as f:
            self.src = f.read()

    def test_the_quarter_rule_is_kept(self):
        self.assertIn("textWidth(figure) <= bw * 1.5", self.src)

    def test_a_figure_gives_way_to_the_one_before_at_the_same_height(self):
        self.assertIn("const figureShown: boolean[] = [];", self.src)
        self.assertIn("Math.abs(figureY[i] - figureY[i - 1]) < LINE", self.src)
        self.assertIn("(tw + prev) / 2 > bw - 2", self.src)
        self.assertIn("textWidth(figure) <= bw * 1.5 && figureShown[i]", self.src)

    def test_the_figure_height_is_the_drawn_one(self):
        # the height decided on is the one the figure is drawn at: the top of the positive stack, or the break line
        self.assertIn("(broken && totals[i] > hi ? TOP : y(capped(Math.max(up, useLog ? lo : 0)))) - 6", self.src)
        self.assertIn("y={(over ? TOP : y(capped(Math.max(up, useLog ? lo : 0)))) - 6}", self.src)

    def test_no_em_dash(self):
        with open(__file__, encoding="utf-8") as f:
            self.assertNotIn(chr(0x2014), f.read())
        self.assertNotIn(chr(0x2014), self.src)


if __name__ == "__main__":
    unittest.main()
