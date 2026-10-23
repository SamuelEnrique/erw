"""Session 303: one chart library, the first step (Samuel's ruling of 13 October 2026, the chain prompt of 19 October).
What is held to:

  the time-series chart every page draws through (components/TimeChart.tsx: LineChart, StackedArea, Sparkline and the
    pages that call it by name) is plain SVG in the brand's manner: no chart library, every color a token, lines of
    1.5 px, each series named at the end of its line (direct labels, no legend box), the zero line in ink and the grid
    lines in the rule color, axis text 12 px, a hover card on fog, a Chart | Table toggle, and a table of every value;
  its props are session 22's, so no page changed its data or its numbers (the wrappers LineChart and StackedArea are
    untouched; the hour-of-day axis of session 161 is still one branch);
  the pages that drew only through it carry no canvas any more (the event pages, /storage, /datacenters, a hub's price
    page): the detector's counts are in the session report; the pages still on the chart library are named there;
  the two Ask checks read the SVG chart; no em dash in any file the session wrote."""
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EM = chr(0x2014)
FILES = ["site/components/TimeChart.tsx", "site/scripts/check-ask-panel.mjs", "site/scripts/check-ask-hours.mjs", "docs/brand/review-303/README.md",
         "tests/test_session303.py", "tests/test_session161.py"]


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def visible(text):
    return re.sub(r"^\s*//.*$", "", text, flags=re.M)


class TheChart(unittest.TestCase):
    def setUp(self):
        self.c = src("site", "components", "TimeChart.tsx")

    def test_plain_svg_in_the_brands_manner(self):
        c = visible(self.c)
        self.assertNotIn("echarts", c.lower())
        self.assertNotIn("<canvas", c)
        self.assertNotRegex(c, r"#[0-9a-fA-F]{3,6}\b")                     # no hex value: the tokens only
        for words in ('strokeWidth="1.5"', 'stroke={v === 0 ? "var(--color-ink)" : "var(--color-rule)"}', 'fontSize="12" fill="var(--color-muted)"',
                      '<g data-direct-labels="1">', 'data-chart-card="1"', 'data-chart-table="1"', 'data-chart-as-table="1"', 'className="pointer-events-none absolute top-6 z-10 border border-rule bg-paper px-3 py-2 text-xs"'):
            self.assertIn(words, c, words)
        self.assertNotIn("legend", c.lower().replace("no legend box", ""))
        self.assertIn('export const tokenColor = (c: string) => (c.startsWith("var(") ? c : c.startsWith("series-") ? `var(--chart-${c})` : `var(--color-${c})`);', c)

    def test_the_props_are_session_22s(self):
        c = self.c
        for words in ("export type TimeSeries = {", "points: [number, number | null][];", "step?: boolean;", "dashed?: boolean;", "y2?: boolean;",
                      "series: TimeSeries[];", "unit: string;", "ariaLabel: string;", "height?: number;", "stack?: boolean;",
                      'x?: "minute" | "day" | "month" | "year" | "hour_of_day";', "mini?: boolean;", "file?: string;", "unit2?: string;",
                      "export function TimeChart({ series, unit, ariaLabel, height = 260, stack = false, x = \"minute\", mini = false, unit2 = \"\", refLines, share = false, marks }: Props) {"):   # session 318: refLines, a named line; session 1152: share (the hover card's share of the stack) and marks (a named time), both off by default
            self.assertIn(words, c, words)
        self.assertIn('const hod = x === "hour_of_day";', c)
        # session 1152: the two props are optional and off by default, so no chart drawn before changes
        self.assertIn("share?: boolean;", c)
        self.assertIn("marks?: { t: number; name: string }[];", c)
        self.assertIn("const xTicks = hod ? [0, 4, 8, 12, 16, 20, 23] :", c)
        for wrapper in (("site", "components", "LineChart.tsx"), ("site", "components", "StackedArea.tsx"), ("site", "components", "Sparkline.tsx")):
            self.assertIn('from "./TimeChart"', src(*wrapper), wrapper)

    def test_every_value_is_reachable_as_a_table_and_the_chart_is_measured_not_shrunk(self):
        c = self.c
        self.assertIn("const PAGE = 500;", c)
        self.assertIn("xs.slice(page * PAGE, (page + 1) * PAGE).map((t) => (", c)
        self.assertIn("new ResizeObserver((es) => { const w = Math.round(es[0].contentRect.width); if (w > 0) setWidth(w); });", c)
        self.assertIn("function thin(points: Pt[], columns: number): Pt[] {", c)      # a spike is kept: the lowest and the highest point of each column stand
        self.assertIn("if (points.length <= columns * 2) return points;", c)


class TheChecks(unittest.TestCase):
    def test_the_ask_checks_read_the_svg_chart(self):
        for name in ("check-ask-panel.mjs", "check-ask-hours.mjs"):
            s = src("site", "scripts", name)
            self.assertNotIn("_echarts_instance_", s, name)
            self.assertIn("svg[role=img]", s, name)
            self.assertIn("[data-chart-card]", s, name)

    def test_the_review_folder(self):
        folder = os.path.join(ROOT, "docs", "brand", "review-303")
        shots = sorted(f for f in os.listdir(folder) if f.endswith(".png"))
        self.assertEqual(len(shots), 24)
        for state in ("before", "after"):
            for name in ("events_uri", "events_covid", "grid_mix", "grid_clean", "explorer", "storage"):
                for w in ("1280", "390"):
                    self.assertIn(f"{state}_{name}_{w}.png", shots)

    def test_no_em_dash_in_any_file_the_session_wrote(self):
        for f in FILES:
            self.assertNotIn(EM, src(*f.split("/")), f)


if __name__ == "__main__":
    unittest.main()
