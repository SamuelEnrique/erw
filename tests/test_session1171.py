"""Session 1171 (chain 078): revisions and preliminary figures, said. The Grid pack's blind spot 9: each tab of the Grid
tool says in its data line, in the same words, that EIA-930's hourly figures are preliminary and revised
(site/lib/gridPreliminary.ts, drawn by site/components/grid/Preliminary.tsx), and check-values tells a revised hour from
a wrong figure (site/scripts/check-revised.mjs, the rule in docs/methods/grid_network.md); its node test
(site/scripts/test-check-revised.mjs) holds a revised row and a wrong row."""
import os
import re
import subprocess
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
WORDS = "EIA-930's hourly figures are preliminary and EIA revises them"
DASH = chr(0x2014)


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


NEW = [("site", "lib", "gridPreliminary.ts"), ("site", "components", "grid", "Preliminary.tsx"), ("site", "scripts", "check-revised.mjs"),
       ("site", "scripts", "test-check-revised.mjs"), ("tests", "test_session1171.py")]


class TheSentence(unittest.TestCase):
    def test_the_words_live_in_one_constant(self):
        lib = src("site", "lib", "gridPreliminary.ts")
        self.assertIn(f'const HEAD = "{WORDS}: a figure here is the value the warehouse held when this page was drawn";', lib)
        # also covered by site/scripts/test-grid-render.mjs: view_gravity on /grid?grid=ercot&view=gravity
        self.assertIn('const TAIL = ", so a later read of the same hour can differ.";', lib)
        self.assertIn("export const EIA930_PRELIMINARY = preliminaryText();", lib)
        self.assertIn('export const DRAWN_ATTR = "data-eia930-drawn";', lib)
        comp = src("site", "components", "grid", "Preliminary.tsx")
        self.assertIn('import { drawnUtc, preliminaryText } from "@/lib/gridPreliminary";', comp)
        self.assertIn("<span data-eia930-drawn={drawn.toISOString()}>{preliminaryText(say ? drawnUtc(drawn) : null)}</span>", comp)

    def test_no_other_site_file_writes_the_words(self):
        hits = []
        for d, _, files in os.walk(SITE):
            if "node_modules" in d or ".next" in d:
                continue
            for f in files:
                if f.endswith((".ts", ".tsx", ".mjs")) and not f.startswith("test-"):   # a node test may pin the words
                    p = os.path.join(d, f)
                    with open(p, encoding="utf-8", errors="replace") as h:
                        if "hourly figures are preliminary" in h.read():
                            hits.append(os.path.relpath(p, SITE).replace(os.sep, "/"))
        self.assertEqual(sorted(hits), ["lib/gridPreliminary.ts"])

    def test_each_of_the_four_tabs_carries_it_once(self):
        net = src("site", "components", "grid", "NetworkView.tsx")   # the Network and Gravity tabs
        self.assertIn('import { Preliminary } from "@/components/grid/Preliminary";', net)
        self.assertEqual(net.count("<Preliminary "), 1)
        self.assertIn("<Preliminary drawn={drawnAt} say />", net)   # the tab already says when the page was drawn
        self.assertIn("const drawn = drawnAt; const clockLag", net)   # one clock for the lag line and the sentence
        # also covered by site/scripts/test-grid-render.mjs: view_gravity on /grid?grid=ercot&view=gravity
        self.assertIn("hours before this page was drawn", net)
        now = src("site", "components", "grid", "NowView.tsx")   # the Mix tab
        self.assertEqual(now.count("<Preliminary "), 1)
        # also covered by site/scripts/test-grid-render.mjs: view_now on /grid?grid=ercot&view=mix
        self.assertIn("Hours are hour starts. <Preliminary drawn={new Date(renderTime())} /></>} />", now)
        page = src("site", "app", "grid", "page.tsx")   # the Clean tab: its data line is new
        clean = page[page.index('{view === "clean" ? ('):page.index('{view === "gravity" ? (')]
        self.assertIn("<SourceLine tables={[...GRID_VIEW_TABLES.clean]} note={<Preliminary drawn={new Date(renderTime())} />} />", clean)
        self.assertEqual(page.count("<Preliminary "), 1)
        self.assertNotIn("Preliminary", src("site", "components", "grid", "ExchangeView.tsx"))   # the Gravity tab says it once


class TheCheck(unittest.TestCase):
    def test_the_method_note_holds_the_rule_and_its_line(self):
        note = src("docs", "methods", "grid_network.md")
        sec = note[note.index("### Revisions, said and checked (session 1171)"):note.index("## Not here")]
        self.assertRegex(sec, re.compile(r"^Revised hours tolerated by check-values: `eia930_all_demand`, `eia930_all_generation`\.$", re.M))
        self.assertIn("Decisions (session 1171):", sec)
        self.assertIn("loaded_at", sec)
        self.assertIn("Every other difference fails as before", sec)
        self.assertIn("Since session 1171 (chain 078)", src("docs", "reviews", "packs", "grid.md"))

    def test_check_values_and_check_methods_read_it(self):
        cv = src("site", "scripts", "check-values.mjs")
        self.assertIn('import * as REV from "./check-revised.mjs";', cv)
        self.assertIn("async function revisedRow(check) {", cv)
        self.assertIn('select: "loaded_at,freq"', cv)
        cm = src("site", "scripts", "check-methods.mjs")
        self.assertIn("line.match(/^(?:ok|late|revised|FAIL)", cm)

    def test_the_node_test_passes(self):
        r = subprocess.run(["node", os.path.join("scripts", "test-check-revised.mjs")], cwd=SITE, capture_output=True, text=True, encoding="utf-8", timeout=300)
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-3000:])
        self.assertRegex(r.stdout, r"\n(\d+) of \1 passed")

    def test_no_dash(self):
        for p in NEW:
            self.assertNotIn(DASH, src(*p), "/".join(p))


if __name__ == "__main__":
    unittest.main()
