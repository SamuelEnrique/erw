"""Session 11600 (chain 780): on a phone the bar chart keeps a width at which its figures can be read.

The read of 28 November (docs/reviews/browser-read-2026-11-28.md, row CH4) found, at 390 px, the bar chart of
/datacenters?view=grids drawn 358 px wide, a figure's line 8 px tall: its text under 6 px.

site/app/tokens.css keeps a year chart 600 px wide on a phone and scrolls it sideways inside its frame, "where shrunk
to the screen [its labels] were under 6". The rule names the figure's own child (`figure > svg[role="img"]`). Since
session 2201 the bar chart's drawing (site/components/tool/GroupedBars.tsx) stands inside its hover's box
(site/components/tool/BarsHover.tsx, `data-bars-hover`), so the rule passed it by. Three rules beside the three that
stand give the box the readable width, let the figure scroll it and keep the title and the note in place. The three
older rules are as they were (tests/test_session314.py reads two of them).

    python -m pytest tests/test_session11600_bars_phone.py
"""
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EM = chr(0x2014)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class ThePhonesRule(unittest.TestCase):
    def setUp(self):
        self.css = src("site", "app", "tokens.css")
        m = re.search(r"@media \(max-width: 639px\) \{\n  \.brand-a figure:not\(\[data-chart-width\]\):has\(> svg\[role=\"img\"\]\) \{.*?\n\}\n", self.css, re.S)
        self.assertIsNotNone(m, "the phone's block of the chart rules")
        self.block = m.group(0)

    def test_the_three_older_rules_stand(self):
        self.assertIn('  .brand-a figure:not([data-chart-width]):has(> svg[role="img"]) {\n    overflow-x: auto;\n  }', self.block)
        self.assertIn('  .brand-a figure:not([data-chart-width]) > svg[role="img"] {\n    min-width: 600px;\n  }', self.block)
        self.assertIn('  .brand-a figure:not([data-chart-width]):has(> svg[role="img"]) > :not(svg) {\n    position: sticky;\n    left: 0;\n  }', self.block)

    def test_the_same_three_for_the_chart_inside_its_hovers_box(self):
        self.assertIn('  .brand-a figure:not([data-chart-width]):has(> [data-bars-hover] > svg[role="img"]) {\n    overflow-x: auto;\n  }', self.block)
        self.assertIn('  .brand-a figure:not([data-chart-width]) > [data-bars-hover]:has(> svg[role="img"]) {\n    min-width: 600px;\n  }', self.block)
        self.assertIn('  .brand-a figure:not([data-chart-width]):has(> [data-bars-hover] > svg[role="img"]) > :not([data-bars-hover]) {\n    position: sticky;\n    left: 0;\n  }', self.block)

    def test_the_file_is_whole(self):
        self.assertEqual(self.css.count("{"), self.css.count("}"))
        self.assertNotIn(EM, self.css)


class TheChartTheRuleNames(unittest.TestCase):
    """The rule holds only while the drawing is the box's own child and the box is the figure's."""

    def test_the_hovers_box_is_marked_and_holds_the_drawing(self):
        hover = src("site", "components", "tool", "BarsHover.tsx")
        self.assertIn('<div className="relative" data-bars-hover={id} tabIndex={0} role="group"', hover)
        self.assertIn("{children}", hover)
        bars = src("site", "components", "tool", "GroupedBars.tsx")
        self.assertIn("<BarsHover id={id} cards={cards} left={L} right={R} width={W}>", bars)
        self.assertIn('className="w-full" role="img" aria-label={label} data-bars={id}>', bars)

    def test_the_frame_is_a_figure_whose_child_is_the_chart(self):
        frame = src("site", "components", "tool", "ToolPage.tsx")
        self.assertIn('<figure className="mb-10">', frame)


if __name__ == "__main__":
    unittest.main()
