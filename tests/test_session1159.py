"""Session 1159 (chain 077): the brand pass of the Grid tool (/grid's four tabs, /grid/caiso/alerts), docs/brand.md.

Styles only, through site/app/tokens.css and the shared components; no figure, no check key, no word and no panel moves:
- the tables the chain's panels draw by hand (the energy mix's two, the last 24 hours') take the shared table's rows
  (6 px above and below a cell, the full rule between rows), scoped to [data-grid-panel];
- "license needed" and "not held yet" take one look across the tool (captions grey, upright, a dotted rule under words
  whose reason is in the hover), and in a figure's cell they are set in the sans, as words;
- CAISO's alert state writes its dates and counts in the running text's face, as the other panels' figures (mono is for
  figures in table cells and hover cards, docs/brand.md section 1);
- the scarcity panel's title is the shared ToolSection, as every other panel of the chain;
- the last 24 hours' table (Clean tab) scrolls alone in a frame a keyboard reaches, its note in place, each ISO its row's
  header (so it stays in view as the figures scroll, docs/brand.md section 5);
- the network panels stand 40 px under the drawing's notes, the gap between every other panel of the tool.
"""

import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
EM = chr(0x2014)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def block():
    t = src("site", "app", "tokens.css")
    i = t.index("/* ---- session 1159 (chain 077")
    return t[i:]


class TheTokens(unittest.TestCase):
    def test_the_hand_drawn_tables_take_the_shared_rows(self):
        b = block()
        self.assertIn(".brand-a [data-grid-panel] table :is(thead, tbody) :is(th, td) {\n  padding-top: 6px;\n  padding-bottom: 6px;\n}", b.replace("\r\n", "\n"))
        self.assertIn(".brand-a [data-grid-panel] tbody tr {\n  border-bottom-color: var(--color-rule);\n}", b.replace("\r\n", "\n"))
        self.assertIn(".brand-a [data-grid-panel] tbody td.text-right span.text-xs {\n  font-size: 12px;\n}", b.replace("\r\n", "\n"))

    def test_one_look_for_license_needed_and_not_held(self):
        b = block().replace("\r\n", "\n")
        self.assertIn(".brand-a [data-grid-tool] span[data-missing],\n.brand-a [data-grid-tool] span[data-license-held][title] {\n  font-style: normal;", b)
        self.assertIn(".brand-a [data-grid-tool] span.cursor-help[title] > span[data-license-held] {\n  border-bottom: 0;\n}", b)
        self.assertIn("span.text-muted:not(.text-xs):not([data-check])) {\n  font-family: var(--font-sans);\n}", b)

    def test_no_color_literal_no_new_size_off_the_scale_no_em_dash(self):
        b = block()
        self.assertIsNone(re.search(r"#[0-9A-Fa-f]{3,8}\b", b))
        for px in re.findall(r"font-size:\s*(\d+)px", b):
            self.assertIn(int(px), (12, 14, 16, 20, 24, 36))
        self.assertNotIn(EM, b)
        self.assertNotIn("\\2014", b)

    def test_the_block_is_the_files_last(self):
        """Appended, so no earlier rule of tokens.css moved."""
        t = src("site", "app", "tokens.css")
        self.assertEqual(t.count("/* ---- session 1159 (chain 077"), 1)
        self.assertGreater(t.index("/* ---- session 1159 (chain 077"), t.index("/* session 1072 (chain 073)"))


class TheComponents(unittest.TestCase):
    def test_caiso_alert_figures_in_the_running_texts_face(self):
        c = src("site", "components", "grid", "CaisoAlertState.tsx")
        self.assertIn('<span title={f.tip} className="cursor-help border-b border-dotted border-muted">', c)
        self.assertNotIn("border-muted font-mono", c)
        self.assertEqual(c.count("check="), 1)

    def test_the_scarcity_title_is_the_shared_section(self):
        s = src("site", "components", "grid", "ScarcityPanel.tsx")
        self.assertIn('import { ToolSection } from "@/components/tool/ToolPage";', s)
        self.assertNotIn('from "@/components/Section"', s)
        self.assertIn('<ToolSection title={grid === "us48" ? "The scarcity hours, by grid" : `${label}: the scarcity hours, last 30 days held`} id="scarcity">', s)
        self.assertEqual(s.count("check="), 1)

    def test_the_last_24_hours_table_scrolls_alone_with_its_row_heads(self):
        e = src("site", "components", "grid", "Emissions.tsx")
        self.assertIn('import { scrollRegion } from "@/lib/cells";', e)
        # also covered by site/scripts/test-grid-render.mjs: grid_clean24_ercot on /grid?grid=ercot&view=clean
        self.assertIn('<div className="mt-3" data-grid-panel={`grid_clean24_${grid ?? "all"}`}>', e)
        # also covered by site/scripts/test-grid-render.mjs: grid_clean24_ercot on /grid?grid=ercot&view=clean
        self.assertIn('<div className="overflow-x-auto" {...scrollRegion("Latest, lowest and highest intensity of generation per ISO in the 24 hours drawn")}>', e)
        self.assertIn('<th scope="row" className="py-0.5 pr-2 text-left font-normal">{ISOS.find((i) => i.entity === d.entity)!.label}</th>', e)
        # the note under the table is outside the scrolling frame
        i = e.index('{...scrollRegion("Latest, lowest')
        self.assertLess(e.index("</table>\n              </div>", i), e.index("The hour beside each figure is its hour start, UTC.", i))
        self.assertEqual(e.count("check="), 4)

    def test_the_network_panels_stand_at_the_tools_gap(self):
        n = src("site", "components", "grid", "NetworkFigures.tsx")
        self.assertEqual(n.count('className="mt-10">'), 3)
        self.assertNotIn('className="mt-8"', n)

    def test_no_em_dash_in_the_files_changed(self):
        for parts in (("site", "app", "tokens.css"), ("site", "components", "grid", "CaisoAlertState.tsx"), ("site", "components", "grid", "ScarcityPanel.tsx"),
                      ("site", "components", "grid", "Emissions.tsx"), ("site", "components", "grid", "NetworkFigures.tsx"), ("tests", "test_session1159.py")):
            self.assertNotIn(EM, src(*parts), parts)


if __name__ == "__main__":
    unittest.main()
