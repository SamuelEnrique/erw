"""Session 1415 (chain 107): the Clean tab's emissions blocks.

site/components/grid/Emissions.tsx draws three blocks on the Grid tool's Clean tab. Session 1151 keyed "The last 24
hours" (grid_clean24_<grid>); the two others are now named panels, every figure keyed: "Carbon intensity now, ranked"
(grid_carbonrank_<grid>: the 14 series| keys it had, each with its source on hover) and "Monthly since 2018"
(grid_carbonmonth_<grid>: the 14 series| keys it had, and the two figures of the chart's note, keyed on the committed
site/data/carbon_left_out.json: fmt|n0|filecalc|carbon_left_out_n|... by lib/mixViewCalc.ts leftOutCount, and
fmt|n0|file|carbon_left_out.json|hydro_gap.hours). Each has its file (components/grid/PanelFile.tsx), its anchor
(lib/gridAnchors.ts EMISSIONS_ANCHOR) and its method line (METHOD_EMISSIONS_BLOCKS, a section of docs/methods/emissions.md),
and a held ISO's place in the three blocks reads "license needed" (lib/gridHeld.ts heldCarbonRow; no ISO is held today).
The rows each block draws are chosen as they were, by pure functions moved from the component (lib/gridKeys.ts
carbonRanked, carbonMonthEnds). The node tests hold the blocks as the server draws them (test-grid-render.mjs, eight
cases), their files and anchors (test-grid-files.mjs), a failed read (test-grid-failed-reads.mjs), the held rule
(test-grid-held.mjs) and the new function (test-mix-view-calc.mjs).
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
NEW = [("tests", "test_session1415.py"), ("site", "scripts", "fixtures", "carbon_monthly.json")]
CHANGED = [("site", "components", "grid", "Emissions.tsx"), ("site", "lib", "gridAnchors.ts"), ("site", "lib", "gridHeld.ts"), ("site", "lib", "gridKeys.ts"),
           ("site", "lib", "mixViewCalc.ts"), ("site", "lib", "carbonLeftOut.ts"), ("site", "scripts", "check-filecalc.mjs"),
           ("site", "scripts", "grid-render-standin.mjs"), ("site", "scripts", "test-grid-render.mjs"), ("site", "scripts", "test-grid-files.mjs"),
           ("site", "scripts", "test-grid-failed-reads.mjs"), ("site", "scripts", "test-grid-held.mjs"), ("site", "scripts", "test-mix-view-calc.mjs"),
           ("docs", "methods", "emissions.md"), ("docs", "methods", "generation_mix_hourly.md"), ("tests", "test_session1182.py")]


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def node_env():
    return {k: v for k, v in os.environ.items() if k not in ("SUPABASE_URL", "SUPABASE_ANON_KEY", "SUPABASE_SERVICE_KEY", "NEXT_PHASE", "NEXT_RUNTIME")}


class TheBlocks(unittest.TestCase):
    def test_each_block_is_a_named_panel_with_its_anchor_file_and_method(self):
        e = src("site", "components", "grid", "Emissions.tsx")
        self.assertIn('<div id={EMISSIONS_ANCHOR.rank} data-grid-panel={`grid_carbonrank_${grid ?? "all"}`}>', e)
        self.assertIn('<div id={EMISSIONS_ANCHOR.monthly} data-grid-panel={`grid_carbonmonth_${grid ?? "all"}`}>', e)
        self.assertEqual(e.count("<Link href={METHOD_EMISSIONS_BLOCKS}>Method: the Clean tab&apos;s carbon blocks, keyed</Link>"), 2)
        self.assertEqual(e.count("<PanelFile "), 3)
        self.assertIn("panel: `grid_carbonrank_${grid ?? \"all\"}`", e)
        self.assertIn("panel: `grid_carbonmonth_${grid ?? \"all\"}`", e)
        # the keys the blocks wrote stand, written by the same four lines (tests/test_session473.py counts them)
        self.assertEqual(e.count("check="), 4)
        self.assertIn("<Num check={`series|${T}|${r.entity}|${r.variable}|${r.ts_utc}`} raw={r.value}>{shown(r.value)}</Num>", e)
        self.assertIn("<Num check={`series|${TM}|${first.entity}|${first.variable}|${first.ts_utc}`} raw={first.value}>{shown(first.value)}</Num>", e)
        self.assertIn("<Num check={`series|${TM}|${last.entity}|${last.variable}|${last.ts_utc}`} raw={last.value}>{shown(last.value)}</Num>", e)
        a = src("site", "lib", "gridAnchors.ts")
        for w in ('rank: "carbon-now",', 'monthly: "carbon-monthly",',
                  'export const METHOD_EMISSIONS_BLOCKS = "/data/methods/emissions#on-the-grid-tools-clean-tab-keyed-chain-107-session-1415";'):
            self.assertIn(w, a)

    def test_the_notes_two_figures_are_keyed_on_the_committed_file(self):
        e = src("site", "components", "grid", "Emissions.tsx")
        self.assertIn('check: `fmt|n0|${filecalcKey("carbon_left_out_n", CARBON_LEFT_OUT_NAME, ["intensity_generation"])}`, raw: leftOutCount(CARBON_LEFT_OUT_FILE, "intensity_generation"),', e)
        self.assertIn("hydro: { check: `fmt|n0|file|${CARBON_LEFT_OUT_NAME}|hydro_gap.hours`, raw: CARBON_HYDRO_GAP.hours,", e)
        self.assertIn("<strong>Left out of this chart: <F f={leftOut} /> months the table still holds.</strong>", e)
        self.assertNotIn("{out.length} months", e)
        self.assertNotIn('CARBON_HYDRO_GAP.hours.toLocaleString("en-US")', e)
        lib = src("site", "lib", "mixViewCalc.ts")
        self.assertIn("export const leftOutCount = (f: LeftOutLike, variable: string): number => f.months.filter((m) => m.variable === variable).length;", lib)
        self.assertIn('carbon_left_out_n: { rule: "lib/mixViewCalc.ts leftOutCount",', lib)
        fc = src("site", "scripts", "check-filecalc.mjs")
        self.assertIn("carbon_left_out_n: { file: /^carbon_left_out\\.json$/, args: [/^intensity_(generation|demand)$/] },", fc)
        self.assertIn("v = calc.leftOutCount(json, args[0]);", fc)
        self.assertIn('export const CARBON_LEFT_OUT_NAME = "carbon_left_out.json";', src("site", "lib", "carbonLeftOut.ts"))

    def test_the_rows_are_chosen_as_they_were_and_a_held_iso_is_set_apart(self):
        e = src("site", "components", "grid", "Emissions.tsx")
        self.assertIn("const rank = carbonRanked(rows, ISOS.map((i) => i.entity), isHeld(T));", e)
        self.assertIn("const ends = carbonMonthEnds(rows, ISOS.map((i) => i.entity), (r) => !carbonLeftOut(r.entity, r.variable, r.ts_utc), isHeld(TM));", e)
        self.assertIn("const isHeld = (table: string) => (entity: string) => !!heldCarbonRow(table, entity);", e)
        self.assertIn("{lastDayFigures(rows, open.map((i) => i.entity), newest).map((d) => (", e)
        self.assertIn('<span data-license-held={table} className="text-muted" title={h.why}>{h.words}</span>', e)
        k = src("site", "lib", "gridKeys.ts")
        self.assertIn('const d = g ? of(entity, "intensity_demand").find((r) => r.ts_utc === g.ts_utc) : undefined;', k)
        self.assertIn(".sort((a, b) => a.g.value - b.g.value);", k)
        h = src("site", "lib", "gridHeld.ts")
        self.assertIn('export const CARBON_MONTHLY_TABLE = "carbon_intensity_monthly";', h)
        self.assertIn("return licenseHeldRow(table, entity, now) ? held(table) : null;", h)

    def test_the_note(self):
        n = src("docs", "methods", "emissions.md")
        self.assertIn("## On the Grid tool's Clean tab, keyed (chain 107, session 1415)", n)
        sec = n.split("## On the Grid tool's Clean tab, keyed (chain 107, session 1415)")[1]
        for w in ("grid_carbonrank_<grid>", "grid_carbonmonth_<grid>", "#carbon-now", "#carbon-monthly", "filecalc|carbon_left_out_n", "file|carbon_left_out.json|hydro_gap.hours",
                  "intensity_generation", "intensity_demand", "heldCarbonRow", "METHOD_EMISSIONS_BLOCKS", "same-figures.mjs", "Decisions (chain 107, session 1415):"):
            self.assertIn(w, sec)
        g = src("docs", "methods", "generation_mix_hourly.md")
        self.assertIn("### One function more, for the Clean tab's carbon chart (session 1415)", g)
        self.assertIn("`carbon_left_out_n` on `carbon_left_out.json`", g)

    def test_the_fixture(self):
        import json
        f = json.loads(src("site", "scripts", "fixtures", "carbon_monthly.json"))
        self.assertEqual((f["table"], f["variable"], f["unit"], f["freq"]), ("carbon_intensity_monthly", "intensity_generation", "kgCO2/MWh", "P1M"))
        self.assertEqual(len(f["rows"]), 636)
        self.assertEqual(len({r[0] for r in f["rows"]}), 8)
        for name in ("grid-render-standin.mjs", "test-grid-files.mjs"):
            self.assertIn('const monthlyC = fx("carbon_monthly.json");', src("site", "scripts", name), name)


class TheFiles(unittest.TestCase):
    def test_no_em_dash(self):
        for parts in NEW + CHANGED:
            self.assertNotIn(EM, src(*parts), parts)


@unittest.skipUnless(NODE and MODULES, "node or site/node_modules (typescript, react) is not on this machine")
class TheNodeTests(unittest.TestCase):
    def test_the_files_and_anchors(self):
        r = subprocess.run([NODE, "--import", "./scripts/alias-register.mjs", "--import", "./scripts/tsx-register.mjs", "scripts/test-grid-files.mjs"],
                           cwd=SITE, capture_output=True, text=True, encoding="utf-8", timeout=600, env=node_env())
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-3000:])
        self.assertIn("ok   the Clean tab's carbon blocks: each carries its anchor", r.stdout)


if __name__ == "__main__":
    unittest.main()
