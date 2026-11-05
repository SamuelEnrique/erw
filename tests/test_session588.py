"""Session 588: the tall render frame of the five-grid cards in two columns.

Session 497 stood the five panels of the two five-grid research cards side by side in the wide render frame (1600 x
900); session 506's shots (docs/brand/review-497/after/) showed the tall frame (1080 x 1350) still drawing them in one
column to 870 px, the fifth (SPP) over the callouts' boxes. In the tall frame the panels now stand in two columns and
the box is as tall as its panels (site/app/research/card/render.css, the frame only). The shared chart keeps an area's
shading inside its panel when the axis's floor is above zero (components/svgchart.tsx; no value moves). The check of
the frames (scripts/check-findings-grids.mjs) measures that the lowest chart text ends above the callouts' top.
The measures are the browser's (docs/brand/review-588/); these tests hold the rules in the files."""

import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SITE = os.path.join(ROOT, "site")
RENDER = os.path.join(SITE, "app", "research", "card", "render.css")
CHART = os.path.join(SITE, "components", "svgchart.tsx")
OPTION = os.path.join(SITE, "components", "SvgOption.tsx")
CHECK = os.path.join(SITE, "scripts", "check-findings-grids.mjs")
REPORT = os.path.join(ROOT, "archive", "sessions", "SESSION_588_REPORT.md")


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


class TallFrame(unittest.TestCase):
    def setUp(self):
        css = read(RENDER)
        self.s588 = css[css.index("Session 588"):]

    def test_the_tall_frame_stands_the_panels_in_two_columns(self):
        m = re.search(r"@media \(max-aspect-ratio: 3/2\) \{\s*\.finding-render \[data-finding-chart=\"multiples\"\]\[data-option-kind=\"panels\"\] \{([^}]*)\}", self.s588)
        self.assertTrue(m)
        body = m.group(1)
        for rule in ("display: grid;", "grid-template-columns: repeat(2, minmax(0, 1fr));", "height: auto !important;"):
            self.assertIn(rule, body)

    def test_nothing_is_cut_or_hidden(self):
        self.assertNotIn("overflow", self.s588)
        self.assertNotIn("display: none", self.s588)

    def test_the_wide_frame_and_the_boxes_of_session_182_are_untouched(self):
        css = read(RENDER)
        for line in ('.finding-render [data-finding-chart="multiples"] { height: 430px !important; }',
                     '.finding-render [data-finding="peak_hour_grids"] [data-finding-chart="multiples"] { height: 620px !important; }',
                     '.finding-render [data-finding-chart="multiples"] { height: 250px !important; }',
                     "grid-auto-flow: column;"):
            self.assertEqual(css.count(line), 1, line)

    def test_the_card_page_and_the_panels_are_unchanged(self):
        # the frame only: the panels' height rule in the shared component is session 318's
        self.assertIn("height={Math.max(120, Math.round(height / r.panels.length))}", read(OPTION))


class WideFrameOneChart(unittest.TestCase):
    # the check's finding: every card of one chart drew its 420 px SVG in a 280 px box in the wide frame
    def test_the_wide_frame_scales_the_one_chart_whole(self):
        css = read(RENDER)
        s = css[css.index("the check's finding"):]
        m = re.search(r"@media \(min-aspect-ratio: 3/2\) \{(.*?)\n\}", s, re.S)
        self.assertTrue(m)
        body = m.group(1)
        self.assertIn('.finding-render [data-finding-chart]:not([data-option-kind="panels"]) { height: auto !important; }', body)
        self.assertIn('.finding-render [data-finding-chart]:not([data-option-kind="panels"]) svg { width: auto; height: auto; max-height: 340px; }', body)
        self.assertNotIn("max-aspect-ratio", s)

    def test_the_card_draws_the_same_svg(self):
        self.assertIn("<CardChart spec={card.chart} label={card.title} height={420} />", read(os.path.join(SITE, "components", "analysis", "FindingCard.tsx")))


class AreaInsideThePanel(unittest.TestCase):
    def test_the_area_base_is_held_between_the_plot_top_and_floor(self):
        s = read(CHART)
        self.assertIn("const base = (i: number) => Math.min(height - BOT, Math.max(TOP, py(stacked[k].from[i], b)));", s)
        area = s[s.index("const base = (i: number)"):s.index('" Z";', s.index("const base = (i: number)"))]
        self.assertNotIn("py(stacked[k].from", area.split("\n", 1)[1])

    def test_the_line_and_the_points_keep_the_values(self):
        s = read(CHART)
        self.assertIn("const pts = stacked[k].to.map((v, i) => (v === null ? null : [cx(i), py(v, b)] as [number, number]));", s)
        self.assertIn("data-points={n <= 100 ? JSON.stringify(series.map((s) => s.values)) : undefined}", s)


class TheCheck(unittest.TestCase):
    def test_every_frame_measures_the_lowest_chart_text_against_the_callouts(self):
        s = read(CHECK)
        loop = s[s.index('for (const id of ["batteries_lunch_grids", "peak_hour_grids", "batteries_curtailment_hourly", "batteries_curtailment"])'):]
        self.assertIn("[data-finding-chart] svg text", loop)
        self.assertIn(".finding-callouts", loop)
        self.assertIn("low.text <= low.top", loop)


class NoDash(unittest.TestCase):
    def test_no_dash(self):
        dash = re.compile("[" + chr(0x2013) + chr(0x2014) + "]")
        css = read(RENDER)
        mine = [css[css.index("Session 588"):], read(__file__), read(CHECK), read(CHART)]
        if os.path.exists(REPORT):
            mine.append(read(REPORT))
        for text in mine:
            self.assertIsNone(dash.search(text))


if __name__ == "__main__":
    unittest.main()
