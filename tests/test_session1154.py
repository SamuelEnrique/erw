"""Session 1154 (chain 077): the scarcity hours on the Grid tool's Mix tab, grid_scarcity_<grid>.

The panel (site/components/grid/ScarcityPanel.tsx) stands after the mix blocks and before "Generation mix, as a
table", draws scarcity_hours_by_grid for ERCOT and CAISO through the shared HeatChart, and says in one line why every
other grid is not in the table. Its figures are lib/scarcityStrip.ts's, each a check key; the hours held are a new key
kind, series_n, recomputed in check-values by the page's own function. The node test runs the function on a committed
fixture of real rows.
"""

import os
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class ThePanel(unittest.TestCase):
    def test_after_the_mix_blocks_before_the_table_of_every_region(self):
        page = src("site", "app", "grid", "page.tsx")
        mix = page.index("<GridMixParts g={cfg} d={data} />")
        panel = page.index('<ScarcityPanel grid={grid.slug} label={grid.label} />')
        table = page.index("<MixTable />")
        self.assertLess(mix, panel)
        self.assertLess(panel, table)
        self.assertLess(page.index('{view === "mix" ?'), panel)
        self.assertLess(panel, page.index('{view === "clean" ?'))

    def test_named_drawn_by_the_shared_chart_and_keyed(self):
        p = src("site", "components", "grid", "ScarcityPanel.tsx")
        self.assertIn("data-grid-panel={`grid_scarcity_${grid}`}", p)
        self.assertIn('import { HeatChart } from "@/components/svgchart";', p)
        self.assertIn("<Num check={f.check} raw={f.raw}>", p)
        self.assertEqual(p.count("check="), 1)
        self.assertNotIn(chr(0x2014), p)

    def test_every_other_grid_says_why(self):
        p = src("site", "components", "grid", "ScarcityPanel.tsx")
        self.assertIn('if (grid === "pjm") return { words: LICENSE_NEEDED', p)
        self.assertIn('if (grid === "miso") return { words: "paused"', p)
        self.assertIn("if (licenseHeldGrid(grid)) return { words: LICENSE_NEEDED", p)
        self.assertIn('return { words: "not in the table yet"', p)
        self.assertIn('gridHref("ercot", "mix")}#scarcity', p)
        self.assertIn('gridHref("caiso", "mix")}#scarcity', p)

    def test_the_window_is_the_tables_latest_30_days_not_todays(self):
        lib = src("site", "lib", "scarcityStrip.ts")
        self.assertIn("export const SCARCITY_DAYS = 30;", lib)
        self.assertIn("export function windowOf(newest: string, behind: number, days = SCARCITY_DAYS): Window {", lib)
        self.assertIn("so these are not the 30 days before today", src("site", "components", "grid", "ScarcityPanel.tsx"))


class TheKeys(unittest.TestCase):
    def test_series_n_is_recomputed_by_the_pages_function(self):
        cv = src("site", "scripts", "check-values.mjs")
        self.assertIn('if (p[0] === "series_n") {', cv)
        self.assertIn('const S = await import("../lib/scarcityStrip.ts");', cv)
        self.assertIn("return S.heldHours(rows);", cv)
        self.assertIn("series_n: [1, 2]", src("site", "scripts", "check-methods.mjs"))

    def test_the_method_note_names_the_panels_figures(self):
        note = src("docs", "methods", "scarcity_hours_by_grid.md")
        for word in ("## On the Grid tool (session 1154", "series_n|scarcity_hours_by_grid|", "spp_rtm", "lmp_rtm_15m_mean", "ercot_hub_prices_daily", "rt_max"):
            self.assertIn(word, note)

    def test_the_mix_views_list_names_the_three_tables(self):
        t = src("site", "lib", "gridtables.ts")
        for table in ("scarcity_hours_by_grid", "iso_rtm_hub_prices", "ercot_hub_prices_daily"):
            self.assertIn(f'"{table}"', t)


@unittest.skipUnless(NODE, "node is not installed")
class TheNodeTest(unittest.TestCase):
    def test_the_strip_on_the_fixture(self):
        r = subprocess.run([NODE, "scripts/test-scarcity-strip.mjs"], cwd=SITE, capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 0, r.stdout[-2000:] + r.stderr[-2000:])
        self.assertIn("10 of 10 passed", r.stdout)


if __name__ == "__main__":
    unittest.main()
