"""Session 2200 (chain 086, 23 October 2026): the ERCOT peak premium explorer figure by figure and chart by chart. Every
figure of /explore/ercot-peak-premium and of the ERCOT tab of /prices carries its source in its hover (components/Num.tsx,
`source`, the words of lib/explore/source.ts read from the figure's own key), each headline number a Tip with the same
words, and scripts/check-explorers.mjs reads the explorers in a browser for the tips, the charts' hover cards and the
width as a phone. Energy Research Warehouse (ERW)."""
import json
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SITE = os.path.join(ROOT, "site")
DASH = chr(0x2014)
NEW = [("site", "lib", "explore", "source.ts"), ("site", "scripts", "check-explorers.mjs"), ("site", "scripts", "test-check-explorers.mjs")]
CHANGED = [("site", "components", "Num.tsx"), ("site", "components", "tool", "ToolPage.tsx"),
           ("site", "app", "explore", "ercot-peak-premium", "page.tsx"), ("site", "app", "explorer", "ercot-peak-premium", "Explorer.tsx")]


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def node_eval(code):
    """Run a module snippet with node from site/ (node strips the types of a .ts file that imports nothing)."""
    node = shutil.which("node")
    if not node:
        raise unittest.SkipTest("node is not on the path")
    out = subprocess.run([node, "--no-warnings", "--input-type=module", "-e", code], cwd=SITE, capture_output=True, text=True, timeout=60)
    if out.returncode != 0:
        raise AssertionError(out.stderr[-2000:])
    return json.loads(out.stdout)


class TheSourceWords(unittest.TestCase):
    def test_a_key_of_each_explorer_table_reads_as_its_table_entity_variable_period_report_and_method(self):
        r = node_eval(
            'const m = await import("./lib/explore/source.ts");'
            'console.log(JSON.stringify(['
            ' m.sourceOf("series|ercot_peak_premium_annual|ercot:HB_HUBAVG|peak_iqr|2025-01-01T00:00:00Z"),'
            ' m.sourceOf("series|ercot_peak_premium_monthly|ercot:HB_WEST|peak_median|2025-08-01T00:00:00Z", "HB_WEST"),'
            ' m.sourceOf("series|eia930_demand_growth|eia930:ERCO|avg_demand_growth_since_2019_pct|2025-01-01T00:00:00Z", "ERCOT"),'
            ' m.sourceOf("series|iso_queue_statistics|ercot:queue_2024|positions_entered|2024-01-01T00:00:00Z"),'
            ' m.sourceOf("series|some_other_table|x|y|2024-01-01T00:00:00Z"), m.sourceOf("deals|count"), m.sourceOf("series|ercot_peak_premium_annual|x"),'
            ' m.entityWords("ercot:HB_NORTH"), m.entityWords("spp:queue_2019"), m.periodWords("2025-08-01T00:00:00Z", "P1M"), m.periodWords("2025-08-01T00:00:00Z", "P1Y"),'
            ']))')
        annual, monthly, growth, queue, other, deals, short, hub, q, pm, py = r
        self.assertEqual(annual, "ercot_peak_premium_annual: HB_HUBAVG, peak_iqr, 2025. Source: ERCOT real-time settlement point prices "
                                 "(NP6-785-ER, NP6-905-CD), every 15-minute interval, computed by the ERW. Method: ERCOT peak premium.")
        self.assertTrue(monthly.startswith("ercot_peak_premium_monthly: HB_WEST, peak_median, August 2025. Source: ERCOT"))
        self.assertTrue(growth.startswith("eia930_demand_growth: ERCOT, avg_demand_growth_since_2019_pct, 2025. Source: EIA Form EIA-930"))
        self.assertIn("Method: Demand growth since 2019.", growth)
        self.assertTrue(queue.startswith("iso_queue_statistics: ERCOT's queue, entry year 2024, positions_entered, 2024. Source: the ISO's own interconnection queue"))
        self.assertIn("(ercot_interconnection_queue)", queue)
        self.assertIn("Method: Energy projects, Queue statistics.", queue)
        # a key of no explorer table, a key that is not a series key, and a short key give no words (the figure carries no tip)
        self.assertIsNone(other)
        self.assertIsNone(deals)
        self.assertIsNone(short)
        self.assertEqual([hub, q, pm, py], ["HB_NORTH", "SPP's queue, entry year 2019", "August 2025", "2025"])

    def test_the_source_file_imports_nothing_and_computes_no_number(self):
        s = src("site", "lib", "explore", "source.ts")
        self.assertIsNone(re.search(r"^import ", s, re.M))
        self.assertNotIn("fetch(", s)


class TheNumber(unittest.TestCase):
    def test_num_draws_the_source_as_its_title_and_only_when_given(self):
        s = src("site", "components", "Num.tsx")
        self.assertIn("source?: string", s)
        self.assertIn('<span data-check={check} data-raw={String(raw)} className={className} title={source}>', s)
        # the held branch is as it was: the license's words and title, no data-check
        self.assertIn('<span data-license-held={held.table} className={`text-muted ${className ?? ""}`.trim()} title={held.title}>', s)

    def test_the_headline_number_takes_a_tip_after_its_label(self):
        s = src("site", "components", "tool", "ToolPage.tsx")
        self.assertIn("tip?: ReactNode", s)
        self.assertIn('{label}{tip ? <span className="normal-case tracking-normal">{tip}</span> : null}', s)


class ThePages(unittest.TestCase):
    def test_the_explorer_passes_every_figure_its_source_and_each_headline_a_tip(self):
        p = src("site", "app", "explore", "ercot-peak-premium", "page.tsx")
        self.assertIn('import { sourceOf } from "@/lib/explore/source";', p)
        self.assertIn("<Num check={key(v, y)} raw={x} source={sourceOf(key(v, y), node(hub))}>", p)
        self.assertEqual(p.count("<Num "), 1, "every figure of the page is drawn through the one N helper")
        self.assertIn("tip={<Tip id={`source-${v}`}", p)
        self.assertIn("{sourceOf(key(v, to), name)}</Tip>", p)

    def test_the_ercot_tab_passes_every_figure_its_source(self):
        p = src("site", "app", "explorer", "ercot-peak-premium", "Explorer.tsx")
        self.assertIn('import { sourceOf } from "@/lib/explore/source";', p)
        self.assertEqual(p.count("<Num "), 2)
        self.assertEqual(p.count("source={sourceOf(`series|ercot_peak_premium_annual|${hub}|"), 2)

    def test_the_check_reads_the_explorers_views_of_check_values_list(self):
        s = src("site", "scripts", "check-explorers.mjs")
        self.assertIn('p.startsWith("/explore/") || p === "/prices?tab=ercot"', s)
        for kind in ("tip", "hover", "width"):
            self.assertIn(f'kind: "{kind}"', s)
        self.assertIn("[data-chart-card]", s)
        self.assertIn("[data-svg-chart], [data-time-chart], [data-series-chart], [data-bars]", s)

    def test_no_em_dash_in_the_files(self):
        for parts in NEW + CHANGED + [("tests", "test_session2200.py")]:
            self.assertNotIn(DASH, src(*parts), "/".join(parts))


if __name__ == "__main__":
    unittest.main()
