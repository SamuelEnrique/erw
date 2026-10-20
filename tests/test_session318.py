"""Session 318: the rest of the chart ruling, part two: the finding cards (the owner's ruling of 13 October 2026, every
chart in SVG with direct labels; sessions 303 and 317 moved the rest). What is held to:

  the analysis files' chart options (lib/findingchart.ts, lib/chartforms.ts, MultiChart's small multiples, the weekly
    templates and charts of the week of warehouse/analysis/style.py) are read into the shared SVG set by one pure
    interpreter (lib/svgoption.ts): a category axis, a time axis, a value axis with a scatter, a multi-grid option; a
    reference line, a band of categories, a marked point; every color literal mapped to the brand's token;
  CardChart, FormChart's OptionChart, MultiChart's panels and one-grid view, EChartOption, the share bar, the thesis
    charts and the board's three charts draw through it or the set; no page file of the research tool, the grid's
    now view, the thesis or the board mounts the canvas library; the maps alone still do (they are not charts);
  the card's own page carries an h1 (session 270's finding); no number computed anywhere here; no em dash.

No request, no model call; the environment is read, never set."""
import json
import os
import re
import shutil
import subprocess
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EM = chr(0x2014)
MOVED = ["site/components/analysis/CardChart.tsx", "site/components/analysis/FormChart.tsx", "site/components/analysis/MultiChart.tsx", "site/components/EChartOption.tsx",
         "site/components/ShareBar.tsx", "site/components/thesis/ThesisCharts.tsx", "site/components/board/Workbench.tsx"]
FILES = ["site/lib/svgoption.ts", "site/components/SvgOption.tsx", "site/components/svgchart.tsx", "site/components/TimeChart.tsx", "site/components/echarts.ts",
         "site/app/research/card/[id]/page.tsx", *MOVED, "tests/test_session318.py"]


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def node(js):
    exe = shutil.which("node")
    if not exe:
        raise unittest.SkipTest("node is not on this machine")
    if not os.path.isdir(os.path.join(ROOT, "site", "node_modules")):
        raise unittest.SkipTest("the site's packages are not here (the interpreter reaches react through components/echarts.ts)")
    r = subprocess.run([exe, "--import", "./scripts/alias-register.mjs", "--input-type=module", "-e", js], cwd=os.path.join(ROOT, "site"), capture_output=True, text=True, timeout=180)
    if r.returncode != 0:
        if "ERR_UNKNOWN_FILE_EXTENSION" in r.stderr or "Unknown file extension" in r.stderr:
            raise unittest.SkipTest("this node does not read TypeScript files")
        raise AssertionError(r.stderr[-2000:])
    return json.loads(r.stdout.strip().splitlines()[-1])


class TheInterpreter(unittest.TestCase):
    def test_every_committed_card_and_analysis_file_is_read_into_a_kind_the_set_draws(self):
        out = node("""const { readOption } = await import('./lib/svgoption.ts'); const { optionFor } = await import('./lib/findingchart.ts'); const { multiOption } = await import('./components/analysis/MultiChart.tsx').catch(() => ({}));
          const fs = await import('node:fs'); const path = await import('node:path');
          const kinds = {}; const unread = [];
          for (const f of fs.readdirSync('data/findings')) { if (!f.endsWith('.json') || f === 'catalogue.json') continue; const c = JSON.parse(fs.readFileSync(path.join('data/findings', f), 'utf8'));
            if (c.chart.kind === 'multiples') { kinds['multiples'] = (kinds['multiples'] ?? 0) + 1; continue; }
            const r = readOption(optionFor(c.chart)); kinds[r.kind] = (kinds[r.kind] ?? 0) + 1; if (r.kind === 'unread') unread.push([f, r.why]);
            for (const m of c.more_charts ?? []) { const r2 = readOption(optionFor(m.spec)); kinds[r2.kind] = (kinds[r2.kind] ?? 0) + 1; if (r2.kind === 'unread') unread.push([f, r2.why]); } }
          const walk = (d) => fs.readdirSync(d, { withFileTypes: true }).flatMap((e) => e.isDirectory() ? walk(path.join(d, e.name)) : e.name.endsWith('.json') ? [path.join(d, e.name)] : []);
          let files = 0;
          const roots = ['public/analysis-files', '../docs/analysis'].filter((d) => fs.existsSync(d));   // the gallery is the data machine's, not in git
          for (const f of roots.flatMap(walk)) { let d; try { d = JSON.parse(fs.readFileSync(f, 'utf8')); } catch { continue; } const o = d && d.option; if (!o || !o.series) continue; files += 1;
            const r = readOption(o); kinds[r.kind] = (kinds[r.kind] ?? 0) + 1; if (r.kind === 'unread') unread.push([f, r.why]); }
          console.log(JSON.stringify({ kinds, unread: unread.slice(0, 5), files }));""")
        self.assertEqual(out["unread"], [])
        self.assertGreaterEqual(out["files"], 3)   # the three charts of the week at least; the gallery when held
        for k in ("category", "scatter"):
            self.assertGreater(out["kinds"].get(k, 0), 0, k)

    def test_the_readings_keep_the_options_own_values_and_map_the_literals_to_tokens(self):
        out = node("""const { readOption, colorOf } = await import('./lib/svgoption.ts');
          const cat = readOption({ xAxis: { type: 'category', data: ['2019', '2020'], name: 'year' }, yAxis: [{ name: 'MW' }, { name: 'USD' }],
            series: [{ type: 'bar', name: 'a', data: [1, 2], stack: 'x', itemStyle: { color: '#8C1515' } }, { type: 'line', name: 'b', data: [3, null], yAxisIndex: 1, markLine: { data: [{ yAxis: 2.5, name: 'ref' }], lineStyle: { type: 'dashed' } }, markArea: { data: [[{ xAxis: '2020', name: 'after' }, { xAxis: '2020' }]] }, markPoint: { data: [{ coord: ['2019', 3], name: 'flag' }] } }] });
          const time = readOption({ xAxis: { type: 'time' }, yAxis: { name: 'percent' }, series: [{ type: 'line', name: 't', data: [['2026-09-11T00:00:00Z', 5.5], ['2026-09-12T00:00:00Z', 7.8]] }] });
          const sc = readOption({ xAxis: { type: 'value', name: 'MWh' }, yAxis: { name: 'USD/MWh' }, series: [{ type: 'scatter', name: 'days', data: [[1, 2], [3, 4]] }, { type: 'line', name: 'fit', data: [[1, 2], [3, 4]] }] });
          const panels = readOption({ grid: [{}, {}], title: [{ text: 'A' }, { text: 'B' }], xAxis: [{ type: 'category', gridIndex: 0, data: ['x'] }, { type: 'category', gridIndex: 1, data: ['x'] }], yAxis: [{ gridIndex: 0 }, { gridIndex: 0, position: 'right' }, { gridIndex: 1 }, { gridIndex: 1, position: 'right' }],
            series: [{ type: 'line', name: 'a', data: [1], xAxisIndex: 0, yAxisIndex: 0 }, { type: 'line', name: 'f', data: [2], xAxisIndex: 0, yAxisIndex: 1 }, { type: 'line', name: 'b', data: [3], xAxisIndex: 1, yAxisIndex: 2 }] });
          console.log(JSON.stringify({ cat, time: { kind: time.kind, x: time.x, n: time.series[0].points.length, first: time.series[0].points[0] }, sc, panels: { kind: panels.kind, titles: panels.titles, n: panels.panels.length, axes: panels.panels[0].series.map((s) => s.axis) },
            colors: [colorOf('#8C1515', 0), colorOf('#1f5f8b', 0), colorOf('var(--color-ink)', 0), colorOf(undefined, 3), colorOf('#123456', 9)] }));""")
        c = out["cat"]
        self.assertEqual(c["kind"], "category")
        self.assertEqual(c["x"], ["2019", "2020"])
        self.assertEqual([s["values"] for s in c["series"]], [[1, 2], [3, None]])
        self.assertEqual([s["kind"] for s in c["series"]], ["bar", "line"])
        self.assertEqual(c["series"][1]["axis"], 1)
        self.assertEqual(c["refLines"], [{"value": 2.5, "name": "ref", "dashed": True}])
        self.assertEqual(c["shade"], {"from": 1, "to": 1, "label": "after"})
        self.assertEqual(c["marks"], [{"i": 0, "value": 3, "label": "flag"}])
        self.assertEqual((c["unit"], c["unit2"]), ("MW", "USD"))
        self.assertEqual(out["time"]["kind"], "time")
        self.assertEqual(out["time"]["n"], 2)
        self.assertEqual(out["time"]["first"][1], 5.5)
        self.assertEqual(out["sc"]["kind"], "scatter")
        self.assertEqual(len(out["sc"]["points"]), 2)
        self.assertEqual(out["sc"]["fit"]["name"], "fit")
        self.assertEqual((out["panels"]["kind"], out["panels"]["titles"], out["panels"]["n"], out["panels"]["axes"]), ("panels", ["A", "B"], 2, [0, 1]))
        self.assertEqual(out["colors"], ["var(--color-accent)", "var(--chart-ink)", "var(--color-ink)", "series-4", "series-2"])

    def test_the_interpreter_is_pure_and_the_literal_map_is_the_brands(self):
        s = src("site", "lib", "svgoption.ts")
        self.assertNotIn("from \"react\"", s)
        self.assertNotIn("node:fs", s)
        self.assertIn('import { LITERAL_TOKENS } from "@/components/echarts";', s)
        self.assertIn("export const LITERAL_TOKENS", src("site", "components", "echarts.ts"))


class ThePagesDrawThroughIt(unittest.TestCase):
    def test_no_moved_file_mounts_the_canvas_and_each_keeps_its_names(self):
        kept = {"site/components/analysis/CardChart.tsx": ["export function CardChart("], "site/components/analysis/FormChart.tsx": ["export function OptionChart(", "export function FormChart("],
                "site/components/analysis/MultiChart.tsx": ["export function multiOption(", "export function MultiChart("], "site/components/EChartOption.tsx": ["export function EChartOption("],
                "site/components/ShareBar.tsx": ["export function ShareBar("], "site/components/thesis/ThesisCharts.tsx": ["export function TrendChart(", "export function FunnelChart("],
                "site/components/board/Workbench.tsx": ["function PriceChart(", "function SeasonChart(", "function HistChart(", "export function Workbench("]}
        for f in MOVED:
            s = src(*f.split("/"))
            self.assertNotIn("useEChart", s, f)
            self.assertTrue("SvgOption" in s or "svgchart" in s or "TimeChart" in s, f)
            for name in kept[f]:
                self.assertIn(name, s, (f, name))
        # the maps alone still mount the library (they draw a map, not a chart)
        left = [f for f in ("site/app/map/ProjectMap.tsx", "site/app/resources/ResourceMap.tsx") if "echarts" in src(*f.split("/"))]
        self.assertTrue(left)
        self.assertNotIn("useEChart", src("site", "app", "research", "page.tsx"))

    def test_the_shared_set_grew_what_the_cards_need(self):
        s = src("site", "components", "svgchart.tsx")
        for bit in ("shade?: { from: number; to: number; label: string }", "marks?: { i: number; value: number; label: string }[]", "band?: { lo: (number | null)[]; hi: (number | null)[]; name: string }",
                    "export function HorizontalBars(", "export function ShareSegments(", "fit?: { x0: number; y0: number; x1: number; y1: number; name: string }"):
            self.assertIn(bit, s, bit)
        self.assertIn("refLines?: { value: number; name: string; dashed?: boolean }[];", src("site", "components", "TimeChart.tsx"))
        self.assertIsNone(re.search(r"#[0-9A-Fa-f]{3,8}\b(?![\w-])", re.sub(r"//.*", "", s)))
        so = src("site", "components", "SvgOption.tsx")
        for kind in ("panels", "time", "scatter", "category"):
            self.assertIn(f'data-option-kind="{kind}"', so)
        self.assertIn('data-option-unread="1"', so)

    def test_the_card_page_has_its_h1(self):
        page = src("site", "app", "research", "card", "[id]", "page.tsx")
        self.assertIn('<h1 className="sr-only">{c.title}</h1>', page)


class NoEmDash(unittest.TestCase):
    def test_no_em_dash_in_what_the_session_wrote(self):
        for f in FILES:
            self.assertNotIn(EM, src(*f.split("/")), f)


if __name__ == "__main__":
    sys.exit(unittest.main())
