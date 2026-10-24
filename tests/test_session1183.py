"""Session 1183 (chain 091): every panel in the address.

Energy Research Warehouse (ERW).

Each panel chains 077, 078 and 091 added to the Grid tool has an anchor (an id on the page), one list in
site/lib/gridAnchors.ts, the same on every grid where the panel is the same; each panel's state is in the address (the
tab, the grid, net, t, node, shape, mixp, mix, year, ask, q). site/scripts/test-grid-addresses.mjs holds each panel's
address to gridHref and its state to what the page reads; site/scripts/test-grid-files.mjs holds each drawn panel to
its anchor and no id twice on a page; site/scripts/check-routes.mjs asks each address and finds the anchor. Session
1182's data: links were measured (site/scripts/same-figures.mjs --sizes) and kept.

    python -m unittest tests.test_session1183 -v
"""

import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")
MODULES = all(os.path.isdir(os.path.join(SITE, "node_modules", p)) for p in ("typescript", "react"))
EM = chr(0x2014)

ANCHORS = ["network-figures", "replayed-day", "balance", "gravity-figures", "exchange-grids", "exchange-ties", "exchange-months",
           "last-24-hours", "mix-panel", "scarcity", "caiso-alerts", "ercot-notices", "stored-answers", "stress-ramp", "stress-tight",
           "stress-calm", "stress-grids"]


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read().replace("\r\n", "\n")


def node_env():
    return {k: v for k, v in os.environ.items()
            if k not in ("SUPABASE_URL", "SUPABASE_ANON_KEY", "SUPABASE_SERVICE_KEY", "NEXT_PHASE", "NEXT_RUNTIME", "ERW_PAGES_TOGETHER", "ERW_READ_TIMING",
                         "GRID_FILES_OUT", "ERW_SIZES")}


class TheList(unittest.TestCase):
    def test_one_list_of_anchors_each_with_an_address(self):
        a = src("site", "lib", "gridAnchors.ts")
        for anchor in ANCHORS:
            self.assertIn(f'"{anchor}"', a, anchor)
        self.assertIn("export function anchorOf(key: GridAnchorKey, i: number, grid: string): string {", a)
        self.assertIn("return i ? `${GRID_ANCHOR[key]}-${grid}` : GRID_ANCHOR[key];", a)
        self.assertIn("export const panelAddress = (a: PanelAnchor) => `${a.address}#${GRID_ANCHOR[a.key]}`;", a)

    def test_the_components_draw_them(self):
        uses = {
            ("components", "grid", "NetworkFigures.tsx"): ["id={GRID_ANCHOR.network}", "id={GRID_ANCHOR.balance}", "id={GRID_ANCHOR.gravity}"],
            ("components", "grid", "ReplayDay.tsx"): ["data-replay-day={ask.day} id={GRID_ANCHOR.replay}>"],
            ("components", "grid", "ExchangeView.tsx"): ["id={GRID_ANCHOR.exchangeGrids}", "id={GRID_ANCHOR.exchangeTies}", "id={GRID_ANCHOR.exchangeMonths}"],
            ("components", "grid", "Emissions.tsx"): ["<div id={GRID_ANCHOR.clean24}>"],
            ("components", "grid", "MixView.tsx"): ['<div id={anchorOf("mix", i, grid)}>', '<PanelToggle c={c} month={month} at={anchorOf("mix", i, grid)} />', "#${at}`"],
            ("components", "grid", "AskExamples.tsx"): ["id={GRID_ANCHOR.ask}"],
            ("components", "mix", "views.tsx"): ['id={anchorOf("stressRamp", i, g)}', 'id={anchorOf("stressTight", i, g)}', 'id={anchorOf("stressCalm", i, g)}', "id={GRID_ANCHOR.stressGrids}"],
        }
        for parts, words in uses.items():
            s = src("site", *parts)
            for w in words:
                self.assertIn(w, s, f"{'/'.join(parts)}: {w}")
        self.assertEqual(src("site", "components", "grid", "Emissions.tsx").count("<div id={GRID_ANCHOR.clean24}>"), 2)
        self.assertEqual(src("site", "components", "grid", "ReplayDay.tsx").count("id={GRID_ANCHOR.replay}"), 2)
        # the mix panel's chips no longer send every grid to the first grid's section
        self.assertNotIn("mixp: undefined })}#hourly`", src("site", "components", "grid", "MixView.tsx"))

    def test_the_route_check_lists_each_address_with_its_anchor(self):
        r = src("site", "scripts", "check-routes.mjs")
        self.assertIn("const GRID_ANCHORS = [", r)
        self.assertIn('const ok = drawn.get(page).includes(`id="${anchor}"`);', r)
        for anchor in ANCHORS:
            self.assertRegex(r, r'"/grid\?[^"#]*#' + re.escape(anchor) + '"', anchor)


class TheSizes(unittest.TestCase):
    def test_same_figures_measures_a_page(self):
        s = src("site", "scripts", "same-figures.mjs")
        for w in ("export async function sizeOf(node) {", "export function sizeRows(before, after, pct = 15, kb = 100) {", 'if (args.includes("--sizes")) childEnv.ERW_SIZES = "1";',
                  '"sizes.json"', "export function htmlOf(r, files = { n: 0, bytes: 0 }) {"):
            self.assertIn(w, s, w)
        self.assertNotIn("writeFileSync(path.join(work, \"answers", s)


@unittest.skipUnless(NODE and MODULES, "node or site/node_modules (typescript, react) is not on this machine")
class TheNodeTests(unittest.TestCase):
    def run_node(self, script, tsx=True):
        args = [NODE, "--import", "./scripts/alias-register.mjs"] + (["--import", "./scripts/tsx-register.mjs"] if tsx else []) + [script]
        return subprocess.run(args, cwd=SITE, capture_output=True, text=True, encoding="utf-8", timeout=600, env=node_env())

    def test_the_addresses(self):
        r = self.run_node("scripts/test-grid-addresses.mjs", tsx=False)
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-3000:])
        self.assertIn("ok   every panel's address opens its tab and grid, written as gridHref writes it, its state read back", r.stdout)
        self.assertIn("17 panels", r.stdout)

    def test_the_drawn_pages(self):
        r = self.run_node("scripts/test-grid-files.mjs")
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-3000:])
        self.assertNotIn("FAIL", r.stdout)
        self.assertGreaterEqual(len(re.findall(r"each panel carries its anchor", r.stdout)), 18)
        self.assertIn("ok   two grids on one page: the second grid's mix panel and stress tables take the anchor and the grid", r.stdout)


class TheNote(unittest.TestCase):
    def test_the_method_note_says_it(self):
        n = src("docs", "methods", "grid_network.md")
        at = n.index("## Every panel in the address (chain 091, 24 October 2026)")
        part = n[at:n.index("## Not here", at)]
        for anchor in ANCHORS:
            self.assertIn(f"`#{anchor}`", part, anchor)
        for w in ("Decisions (session 1183):", "84,032 bytes", "No page grew by more than 15 percent or 100 KB", "governs no download", "`components/CopyLine.tsx`"):
            self.assertIn(w, part, w)

    def test_no_em_dash(self):
        for parts in (("site", "lib", "gridAnchors.ts"), ("docs", "methods", "grid_network.md"), ("site", "scripts", "check-routes.mjs"),
                      ("site", "scripts", "test-grid-addresses.mjs"), ("site", "scripts", "test-grid-files.mjs"), ("site", "scripts", "same-figures.mjs"),
                      ("site", "scripts", "test-grid-units.mjs"), ("tests", "test_session1183.py")):
            self.assertNotIn(EM, src(*parts), "/".join(parts))


if __name__ == "__main__":
    unittest.main()
