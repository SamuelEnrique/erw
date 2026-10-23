"""Session 1158 (chain 077): 390 pixels, accessibility, links, on the Grid tool's new panels (sessions 1151 to 1157).

Mechanical fixes, markup and classes only (no figure, no check key moves):
- the energy mix panel's two tables (components/grid/MixFigures.tsx) scroll in a frame a keyboard reaches, named by the
  table's caption (lib/cells.ts scrollRegion, as ToolTable draws it: AccessLint keyboard-accessible/scrollable-region at
  390 px, where the monthly table's 380 px is wider than the column), each fuel's name is the row's header cell, and the
  colour swatch is hidden from a screen reader;
- the network map's drawing (app/network/NetworkMap.tsx) is no longer an image: it holds the regions a keyboard reaches
  and the grids' links (AccessLint aria/presentational-children-focusable); neither drawing takes "group" on its svg
  (aria/aria-allowed-role), the gravity shape's included;
- a hover card of the map and the gravity shape stays inside its frame at 390 px (lib/networkMap.ts cardWidth, in place
  of a fixed max-w-xs), a tap on a line shows its card, and a finger lifting no longer takes it away;
- a stored answer's filter written without a space (where={...}) wraps in the Ask column (AskExamples.tsx, break-words).
"""

import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SITE = os.path.join(ROOT, "site")
EM = chr(0x2014)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheMixTables(unittest.TestCase):
    def test_each_table_scrolls_in_a_named_frame(self):
        m = src("site", "components", "grid", "MixFigures.tsx")
        self.assertIn('import { scrollRegion } from "@/lib/cells";', m)
        self.assertEqual(len(re.findall(r'className="(?:mt-3 )?overflow-x-auto" \{\.\.\.scrollRegion\(', m)), 2)
        self.assertNotIn('<div className="overflow-x-auto">', m)
        self.assertNotIn('<div className="mt-3 overflow-x-auto">', m)

    def test_the_fuel_is_the_rows_header_and_the_swatch_is_hidden(self):
        m = src("site", "components", "grid", "MixFigures.tsx")
        self.assertEqual(m.count('<th scope="row" className="py-1 pr-3 text-left font-normal"><span aria-hidden="true" className="mr-1 inline-block h-2.5 w-2.5"'), 2)
        self.assertNotIn('<td className="py-1 pr-3"><span className="mr-1', m)

    def test_no_figure_moved(self):
        m = src("site", "components", "grid", "MixFigures.tsx")
        # the figures are drawn as before: each through F, a Num with its check key
        self.assertIn("<Num check={f.check} raw={f.raw}>{shown(f.raw)}</Num>", m)
        for f in ("<F f={m.total} />", "<F f={f.mwh} />", '<F f={f.share} unit="%" />', "<F f={f.year} />"):
            self.assertIn(f, m)


class TheDrawings(unittest.TestCase):
    def test_no_image_or_group_role_on_either_drawing(self):
        for name in ("NetworkMap.tsx", "NetworkGravity.tsx"):
            s = src("site", "app", "network", name)
            self.assertIn('className="h-full w-full" preserveAspectRatio="xMidYMid meet"', s, name)
            self.assertIsNone(re.search(r'<svg[^>]*role="(img|group)"[^>]*preserveAspectRatio="xMidYMid meet"', s), name)
            self.assertIn("aria-label=", s, name)

    def test_cards_fit_their_frame_and_answer_a_tap(self):
        for name in ("NetworkMap.tsx", "NetworkGravity.tsx"):
            s = src("site", "app", "network", name)
            self.assertIn("maxWidth: cardWidth(hover.x, hover.right)", s, name)
            self.assertNotIn("max-w-xs", s, name)
            self.assertIn('const leave = (e: PointerEvent<SVGElement>) => { if (e.pointerType !== "touch") setHover(null); };', s, name)
            self.assertNotIn("onPointerLeave={() => setHover(null)}", s, name)
        self.assertIn('onPointerDown={hoverAt(`${f.a}-${f.b}`, "edge")}', src("site", "app", "network", "NetworkMap.tsx"))
        self.assertIn('onPointerDown={hoverAt(p.id, "edge")}', src("site", "app", "network", "NetworkGravity.tsx"))
        self.assertIn("export function cardWidth(x: number, right: boolean): string", src("site", "lib", "networkMap.ts"))

    @unittest.skipUnless(shutil.which("node"), "node is not installed")
    def test_the_node_test(self):
        r = subprocess.run(["node", os.path.join("scripts", "test-grid-390.mjs")], cwd=SITE, capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("5 tests passed", r.stdout)


class TheStoredAnswers(unittest.TestCase):
    def test_a_long_filter_wraps(self):
        a = src("site", "components", "grid", "AskExamples.tsx")
        self.assertIn('className="border-b border-rule py-2 text-sm break-words" data-ask-example={e.id}', a)


class TheFiles(unittest.TestCase):
    def test_no_em_dash(self):
        for parts in (("site", "components", "grid", "MixFigures.tsx"), ("site", "components", "grid", "AskExamples.tsx"),
                      ("site", "app", "network", "NetworkMap.tsx"), ("site", "app", "network", "NetworkGravity.tsx"),
                      ("site", "lib", "networkMap.ts"), ("site", "scripts", "test-grid-390.mjs"), ("tests", "test_session1158.py"),
                      ("archive", "sessions", "SESSION_1158_REPORT.md")):
            if os.path.exists(os.path.join(ROOT, *parts)):
                self.assertNotIn(EM, src(*parts), "/".join(parts))


if __name__ == "__main__":
    unittest.main()
