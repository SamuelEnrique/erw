"""Session 2204 (chain 086, 23 October 2026): the brand pass on the four explorer pages, and the method notes' decisions.
The explorers draw inside the brand's wrapper, whose rules (site/app/tokens.css) set the titles in ink, the labels in
sentence case, the notes at 68 characters, the tables' figures in mono and the axis text at 12 px; the one breach found
by reading was the ERCOT tab's headline tiles at 18 px, now the headline number's size. Each explorer's method note gains
a dated decisions block (docs/methods/ercot_peak_premium.md, demand_growth.md, energy_projects.md). Energy Research
Warehouse (ERW)."""
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
DASH = chr(0x2014)
NOTES = [("docs", "methods", "ercot_peak_premium.md"), ("docs", "methods", "demand_growth.md"), ("docs", "methods", "energy_projects.md")]


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheBrand(unittest.TestCase):
    def test_the_ercot_tabs_tiles_take_the_headline_numbers_size(self):
        e = src("site", "app", "explorer", "ercot-peak-premium", "Explorer.tsx")
        self.assertNotIn("text-lg tabular-nums", e)
        self.assertIn('<div className="font-serif text-3xl tabular-nums">', e)
        css = src("site", "app", "tokens.css")
        self.assertIn(".brand-a .text-3xl:not(h1) {\n  font-size: 24px;", css)

    def test_the_brands_rules_reach_the_explorers(self):
        css = src("site", "app", "tokens.css")
        for rule in (".brand-a h2,", "color: var(--color-ink);       /* a title is ink", ".brand-a .uppercase {\n  text-transform: none;", "max-width: 68ch;", '.brand-a svg[role="img"] text {'):
            self.assertIn(rule, css)
        self.assertIn("<Brand>", src("site", "components", "explore", "Explore.tsx"))
        for f in (("site", "components", "tool", "BarsHover.tsx"), ("site", "components", "tool", "SeriesChart.tsx"), ("site", "components", "tool", "GroupedBars.tsx")):
            self.assertIsNone(re.search(r"#[0-9a-fA-F]{6}\b", src(*f)), "/".join(f))


class TheMethodNotes(unittest.TestCase):
    def test_each_explorers_note_has_a_dated_decisions_block(self):
        for parts in NOTES:
            s = src(*parts)
            self.assertIn("Decisions of the explorer (each dated, and reversible unless said)", s, "/".join(parts))
            block = s[s.index("Decisions of the explorer"):]
            self.assertRegex(block, r"\n1\. 2026-10-21, session 40[345]:")
            self.assertRegex(block, r"\n\d\. 2026-10-23, session 220[0-4]:")
            self.assertIn("site/lib/explore/source.ts", block)

    def test_the_pages_still_link_the_same_notes(self):
        self.assertIn('method={{ href: "/data/methods/ercot_peak_premium"', src("site", "app", "explore", "ercot-peak-premium", "page.tsx"))
        self.assertIn('method={{ href: "/data/methods/demand_growth"', src("site", "app", "explore", "demand-growth", "page.tsx"))
        self.assertIn('export const METHOD = "/data/methods/energy_projects";', src("site", "lib", "explore", "interconnection.ts"))

    def test_no_em_dash_in_the_files(self):
        for parts in NOTES + [("site", "app", "explorer", "ercot-peak-premium", "Explorer.tsx"), ("tests", "test_session2204.py")]:
            self.assertNotIn(DASH, src(*parts), "/".join(parts))


if __name__ == "__main__":
    unittest.main()
