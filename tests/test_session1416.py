"""Session 1416 (chain 107): "Yesterday" and the mix table at 390 pixels and on hover.

site/components/grid/Conditions.tsx draws two blocks of the Grid tool's Mix tab older than chain 077: "<grid>: yesterday"
(GridYesterday) and "Generation mix, as a table" (MixTable). Session 1166 keyed their figures. Now each is a named panel
(grid_yesterday_<grid>, grid_mixtable_all) with its file (components/grid/PanelFile.tsx), its anchor (the ids the two
sections always had, lib/gridAnchors.ts CONDITIONS_ANCHOR and yesterdayAnchor) and its method line (METHOD_CONDITIONS, a
section of docs/methods/generation_mix_hourly.md). The mix table scrolls at 390 px in a frame a keyboard reaches (session
1158's rules: lib/cells.ts scrollRegion, a caption, header cells). The two small charts of "Yesterday" already answered a
hover and a tap through the shared charts (LineChart over TimeChart, ShareBar over ShareSegments); their drawing is
unchanged, and one sentence says so. No figure's key, value or text moved: same-figures.mjs on the Mix tab of ERCOT,
CAISO and the Lower 48 gave the same 203, 358 and 121 figures, two panel names added on each. The node tests hold the
blocks as the server draws them (test-grid-render.mjs, six cases) and every figure of each block to its file
(test-grid-files.mjs).
"""

import os
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")
MODULES = all(os.path.isdir(os.path.join(SITE, "node_modules", p)) for p in ("typescript", "react"))
EM = chr(0x2014)
CHANGED = [("site", "components", "grid", "Conditions.tsx"), ("site", "lib", "gridAnchors.ts"), ("site", "scripts", "test-grid-render.mjs"),
           ("site", "scripts", "test-grid-files.mjs"), ("docs", "methods", "generation_mix_hourly.md"), ("tests", "test_session1416.py")]


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def node_env():
    return {k: v for k, v in os.environ.items()
            if k not in ("SUPABASE_URL", "SUPABASE_ANON_KEY", "SUPABASE_SERVICE_KEY", "NEXT_PHASE", "NEXT_RUNTIME", "ERW_PAGES_TOGETHER", "ERW_READ_TIMING",
                         "GRID_FILES_OUT", "ERW_SIZES")}


class ThePanels(unittest.TestCase):
    def test_each_block_is_a_named_panel_with_its_file_anchor_and_method(self):
        c = src("site", "components", "grid", "Conditions.tsx")
        self.assertIn("<div data-grid-panel={`grid_yesterday_${grid}`}>", c)
        self.assertIn('<div data-grid-panel="grid_mixtable_all">', c)
        self.assertIn("<Section title={`${ba.label}: yesterday`} id={yesterdayAnchor(ba.code)}>", c)
        self.assertIn('<Section title="Generation mix, as a table" id={CONDITIONS_ANCHOR.mixTable}>', c)
        self.assertEqual(c.count("<PanelFile of={{ panel: "), 2)
        self.assertEqual(c.count("<Link href={METHOD_CONDITIONS}>Method: &quot;Yesterday&quot; and the mix table, keyed</Link>"), 2)
        # the grid from the block's code, the other way of NowView.tsx's CONDITIONS_CODE
        self.assertIn('const GRID_OF: Record<string, string> = { erco: "ercot", ciso: "caiso", pjm: "pjm", miso: "miso", swpp: "spp", nyis: "nyiso", isne: "isone", us48: "us48" };', c)
        a = src("site", "lib", "gridAnchors.ts")
        for line in ('  yesterday: "yesterday",', '  mixTable: "mix-table",',
                     "export const yesterdayAnchor = (code: string): string => `${CONDITIONS_ANCHOR.yesterday}-${code}`;",
                     'export const METHOD_CONDITIONS = "/data/methods/generation_mix_hourly#yesterday-and-the-mix-table-at-390-pixels-and-on-hover-session-1416";'):
            self.assertIn(line, a)

    def test_the_files_take_the_page_s_own_key_functions(self):
        c = src("site", "components", "grid", "Conditions.tsx")
        self.assertIn("by.has(f.key) ? { check: shareKey(r, f.key), raw: (by.get(f.key)! / total) * 100 } : \"\"", c)
        self.assertIn("function genTotal(r: BAResult, gtable: string): { check: string; raw: number } | null {", c)
        self.assertIn('...(gt ? [["Net generation of the day", `UTC day ${r.genDay}`, gt, "MWh"]] : []),', c)
        # a degree day the page cannot compute, or read, in the page's words
        self.assertIn('[`Degree days at ${r.ba.station}`, "the 7 UTC days drawn", "could not be read", ""]', c)
        self.assertIn("`not computed (${x.n} of 24 hours in ${WX})`", c)


class At390(unittest.TestCase):
    def test_the_mix_table_scrolls_in_a_named_frame_with_header_cells(self):
        c = src("site", "components", "grid", "Conditions.tsx")
        self.assertIn('<div className="overflow-x-auto" {...scrollRegion(caption)}>', c)
        self.assertIn('<caption className="sr-only">{caption}</caption>', c)
        self.assertIn('const caption = "Each region\'s share of its UTC day\'s net generation by fuel, in percent (EIA-930)";', c)
        self.assertEqual(c.count('<th scope="col" className="py-1 pr-3 font-normal">'), 2)
        self.assertIn('<th key={f.key} scope="col" className="py-1 pr-3 text-right font-normal">{f.label}</th>', c)
        self.assertIn('<th scope="row" className="py-1 pr-3 text-left font-normal">{r.ba.label}</th>', c)
        self.assertNotIn('<td className="py-1 pr-3">{r.ba.label}</td>', c)
        self.assertNotIn("<th className=", c)
        # no fixed width outside a frame; the two columns stack under lg
        self.assertNotIn("minWidth", c)
        self.assertIn('<div className="grid gap-6 lg:grid-cols-[18rem_1fr]">', c)
        self.assertIn('role="group" aria-label="Fuel colors"', c)


class OnHover(unittest.TestCase):
    def test_the_two_small_charts_are_the_shared_charts_as_they_were(self):
        c = src("site", "components", "grid", "Conditions.tsx")
        # the drawing is unchanged: the same shared components with the same props
        self.assertIn('<LineChart lines={lines} unit="MW" unit2="degF" height={220} ariaLabel={`${r.ba.label} hourly demand, day-ahead forecast and temperature, 7 days`} />', c)
        self.assertIn('parts={pos.map((f) => ({ name: f.label, value: f.mwh, color: `var(--color-fuel-${f.key})` }))}', c)
        self.assertIn('ariaLabel={`${r.ba.label} generation by fuel, ${r.genDay}`}', c)
        self.assertIn("A hover or a tap on the chart gives the hour (UTC) and its", c)
        # the shared charts' cards: the hour and each series' value and unit; the part, its MWh and share
        t = src("site", "components", "TimeChart.tsx")
        self.assertIn('<div className="text-ink">{fmt(hover.t)}</div>', t)
        self.assertIn("onMouseMove={onMove} onMouseLeave={() => setHover(null)}", t)
        s = src("site", "components", "svgchart.tsx")
        self.assertIn("{segs[hover].name}: <span className=\"font-mono\">{num(segs[hover].value)} {unit}</span> ({segs[hover].share.toFixed(1)}%)", s)


class TheNoteAndTheTests(unittest.TestCase):
    def test_the_method_section_and_its_decisions(self):
        n = src("docs", "methods", "generation_mix_hourly.md")
        self.assertIn('### "Yesterday" and the mix table, at 390 pixels and on hover (session 1416)', n)
        self.assertIn("Decisions (chain 107, session 1416):", n)
        for w in ("grid_yesterday_<grid>", "grid_mixtable_all", "`#yesterday-<EIA-930 code>`", "`#mix-table`", "METHOD_CONDITIONS",
                  "erw_grid_yesterday_<grid>.csv", "erw_grid_mixtable_all.csv", "scrollRegion", "**No chart was redrawn.**"):
            self.assertIn(w, n)

    def test_the_render_and_file_tests_name_the_blocks(self):
        r = src("site", "scripts", "test-grid-render.mjs")
        for name in ("grid_yesterday_ercot on /grid?grid=ercot&view=mix", "grid_yesterday_caiso on /grid?grid=caiso&view=mix",
                     "grid_yesterday_isone on /grid?grid=isone&view=mix", "grid_yesterday_us48 on /grid?grid=us48&view=mix",
                     "grid_mixtable_all on /grid?grid=ercot&view=mix", "grid_mixtable_all on /grid?grid=us48&view=mix"):
            self.assertIn(f'{{"name": "{name}"', r)
        f = src("site", "scripts", "test-grid-files.mjs")
        self.assertIn('await check("\\"Yesterday\\" and the mix table: each carries its anchor, links METHOD_CONDITIONS once and offers its file, every figure in it"', f)

    @unittest.skipUnless(NODE and MODULES, "node or site/node_modules is not here")
    def test_the_render_test_holds_the_new_cases(self):
        r = subprocess.run([NODE, "--import", "./scripts/alias-register.mjs", "--import", "./scripts/tsx-register.mjs", os.path.join("scripts", "test-grid-render.mjs")],
                           cwd=SITE, capture_output=True, text=True, timeout=600, env=node_env())
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-2000:])
        for name in ("grid_yesterday_ercot", "grid_yesterday_caiso", "grid_yesterday_isone", "grid_yesterday_us48", "grid_mixtable_all"):
            self.assertIn(f"ok   {name} on ", r.stdout)

    def test_no_em_dash(self):
        for parts in CHANGED:
            self.assertNotIn(EM, src(*parts), "/".join(parts))


if __name__ == "__main__":
    unittest.main()
