"""Session 317: the rest of the chart ruling, part one (the owner's ruling of 13 October 2026: every chart in SVG with
direct labels; session 303 moved the time-series chart, this session the heat maps, the bands, the scatter, the box
plot and the category charts of the curtailment, supply, cost-of-power and Mix pages). What is held to:

  one shared SVG set (site/components/svgchart.tsx): CategoryChart, HeatChart, BandChart, ScatterChart, BoxPlot, each
    with direct labels, a Chart | Table toggle, a hover card, the brand's tokens only (no hex value), drawn for the
    width it measures;
  the pages' chart files keep their names and props and draw through the set, so no page changed its data: no chart
    file of the moved pages reads the canvas library any more;
  the canvas library is left to the pages the next session moves (the finding cards) and the maps;
  no em dash in any file the session wrote.

No request, no model call; the environment is read, never set."""
import os
import re
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EM = chr(0x2014)
MOVED = ["site/app/curtailment/Charts.tsx", "site/components/mix/Charts.tsx", "site/components/supply/SupplyCharts.tsx", "site/components/BoxChart.tsx",
         "site/app/cost-of-power/charts.tsx", "site/app/cost-of-power/LoadCharts.tsx", "site/app/cost-of-power/seller/SellerCharts.tsx"]
FILES = ["site/components/svgchart.tsx", *MOVED, "tests/test_session144_page.py", "tests/test_session145.py", "tests/test_session194.py",
         "tests/test_session236.py", "tests/test_session241a.py", "docs/brand/review-317/README.md", "tests/test_session317.py"]


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheSharedSet(unittest.TestCase):
    def setUp(self):
        self.s = src("site", "components", "svgchart.tsx")

    def test_five_kinds_each_with_direct_labels_a_table_toggle_and_a_hover_card(self):
        for name in ("CategoryChart", "HeatChart", "BandChart", "ScatterChart", "BoxPlot"):
            self.assertIn(f"export function {name}(", self.s, name)
        # session 318 added two (HorizontalBars and ShareSegments: labelled, measured; the bars with a table toggle)
        self.assertEqual(self.s.count('data-direct-labels="1"'), 7)
        self.assertEqual(self.s.count("<Toggle label={label} table={table} setTable={setTable} id={id} />"), 6)
        self.assertEqual(self.s.count("<DataTable label={label} id={id}"), 6)
        self.assertGreaterEqual(self.s.count("<Card left="), 6)
        self.assertEqual(self.s.count("useWidth<HTMLDivElement>()"), 7)   # drawn for the width measured
        for kind in ("category", "heat", "band", "scatter", "box"):
            self.assertIn(f'data-svg-chart="{kind}"', self.s)

    def test_the_tokens_only_and_no_canvas(self):
        body = re.sub(r"//.*", "", self.s)
        self.assertIsNone(re.search(r"#[0-9A-Fa-f]{3,8}\b(?![\w-])", body))
        for token in ("var(--color-accent)", "var(--color-ink)", "var(--color-muted)", "var(--color-rule)", "var(--color-surface)", "var(--color-panel)", "var(--color-fuel-gas)"):
            self.assertIn(token, self.s, token)
        self.assertNotIn("echarts", self.s)
        self.assertNotIn("<canvas", self.s)
        self.assertIn("for (const m of [1, 2, 2.5, 5, 10]) if (span / (m * p) <= 5) return m * p;", self.s)   # the axis step by magnitude (session 314)

    def test_a_heat_cell_is_one_color_at_a_strength_and_a_blank_cell_is_hatched(self):
        self.assertIn("const strength = (v: number) => (hi > lo ? 0.08 + 0.92 * ((v - lo) / (hi - lo)) : 0.6);", self.s)
        # session 351 (the owner's ruling of 20 October 2026): one color for a magnitude, two hues where the figure is signed
        self.assertIn("fill={v === null || v === undefined ? `url(#${id}-blank)` : fillOf(v)}", self.s)
        self.assertIn('(signed ? (v < 0 ? "var(--chart-blue)" : "var(--color-accent)") : "var(--color-accent)")', self.s)


class ThePagesDrawThroughIt(unittest.TestCase):
    def test_no_moved_chart_file_reads_the_canvas_library_and_each_keeps_its_names(self):
        kept = {"site/app/curtailment/Charts.tsx": ["export function XY(", "export function Heat("],
                "site/components/mix/Charts.tsx": ["export function HourStack(", "export function Lines(", "export function Bars(", "export function Heat("],
                "site/components/supply/SupplyCharts.tsx": ["export function Band(", "export function Trend("],
                "site/components/BoxChart.tsx": ["export function BoxChart("],
                "site/app/cost-of-power/charts.tsx": ["export function RankBars(", "export function HeatGrid(", "export function CostCarbon(", "export function Calculator("],
                "site/app/cost-of-power/LoadCharts.tsx": ["export function YearCost("],
                "site/app/cost-of-power/seller/SellerCharts.tsx": ["export function PremiumYears(", "export function RevenueYears(", "export function MonthlyRevenue(", "export function CoverageLine("]}
        for f in MOVED:
            s = src(*f.split("/"))
            self.assertNotIn("@/components/echarts", s, f)
            self.assertNotIn("useEChart", s, f)
            self.assertIn("svgchart", s, f)
            for name in kept[f]:
                self.assertIn(name, s, (f, name))

    def test_the_callers_did_not_change(self):
        # the pages hand the same arrays through the same names: the calls of session 303's report are still these
        self.assertEqual(src("site", "app", "curtailment", "page.tsx").count("<XY "), 6)
        self.assertEqual(src("site", "app", "curtailment", "Sections.tsx").count("<XY "), 4)
        self.assertEqual(src("site", "app", "curtailment", "Sections.tsx").count("<Heat "), 1)
        self.assertEqual(src("site", "app", "supply", "page.tsx").count("<Band "), 2)
        self.assertEqual(src("site", "app", "explorer", "ercot-peak-premium", "Explorer.tsx").count("<BoxChart"), 1)
        gv = src("site", "app", "cost-of-power", "GridsView.tsx")
        for name in ("<RankBars", "<HeatGrid", "<CostCarbon"):
            self.assertEqual(gv.count(name), 1, name)
        self.assertEqual(src("site", "app", "cost-of-power", "page.tsx").count("<YearCost"), 1)

    def test_the_canvas_library_stays_for_what_is_not_moved_yet(self):
        # the maps still draw on it; the finding cards moved in session 318; the library itself is untouched
        self.assertNotIn("useEChart", src("site", "components", "analysis", "CardChart.tsx"))
        self.assertIn("export function useEChart", src("site", "components", "echarts.ts"))


class NoEmDash(unittest.TestCase):
    def test_no_em_dash_in_what_the_session_wrote(self):
        for f in FILES:
            self.assertNotIn(EM, src(*f.split("/")), f)


if __name__ == "__main__":
    sys.exit(unittest.main())
