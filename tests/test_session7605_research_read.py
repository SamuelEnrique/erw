"""Session 7605 (chain 305, part C, the portable laptop): Automated Analysis (`/research`) read as its reader, a fund
analyst reading the week's findings (docs/reviews/research-read-2026-11-16.md).

1. At 390 px, with a finding's "Method, the table of estimates" opened, the page was 712 px wide: the library's grid
   (`.with-index`, one column on a narrow screen) took the widest card's least width, though the table is in a frame
   that scrolls. Its cards' column (`.index-main`) may now shrink to the screen.
2. Today's chart printed the record's figures under the scanner's own names ("sigma", "stood points", "margin sigmas").
   They are now in plain words (lib/researchrules.ts, FIGURE_WORDS); a key not listed is printed as before.
3. The form's list, "the public tables of the live set", offered tables held whole (energy_deals, datacenter_facilities,
   news_index). A table held whole is no longer offered; one held by grid or by row keeps its public rows and stays.
Energy Research Warehouse (ERW)."""
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
DASHES = (chr(0x2014), chr(0x2013))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheNarrowScreen(unittest.TestCase):
    def test_the_cards_column_may_shrink(self):
        css = src("site", "app", "tokens.css").replace(chr(13), "")
        self.assertIn(".brand-a .with-index > .index-main {\n  min-width: 0;\n}", css)
        # after the wide screen's rule, which gives the column minmax(0, 1fr) above 1024 px
        self.assertLess(css.index("grid-template-columns: 232px minmax(0, 1fr);"), css.index(".brand-a .with-index > .index-main {"))
        self.assertIn('<div className="index-main">', src("site", "components", "research", "Library.tsx"))


class TheRecordsWords(unittest.TestCase):
    def test_every_key_of_the_record_has_words(self):
        s = src("site", "lib", "researchrules.ts")
        for k in ("value", "old_record", "threshold", "margin", "sigma", "margin_sigmas", "strength", "stood_points", "history_points", "history_years"):
            self.assertRegex(s, rf"\n  {k}: \"[^\"]+\",")
        self.assertIn('export const figureWords = (k: string): string => FIGURE_WORDS[k] ?? k.replace(/_/g, " ");', s)

    def test_the_page_uses_them(self):
        p = src("site", "app", "research", "page.tsx")
        self.assertIn('{i ? "; " : ""}{figureWords(k)} <Num check={`digest_chart|${today.date}|${today.table}|${k}`}', p)
        self.assertNotIn('{i ? "; " : ""}{k.replace(/_/g, " ")} <Num check={`digest_chart', p)


class TheHeldGridsPanels(unittest.TestCase):
    """4. site/scripts/check-holds.mjs, run on this session's build, found the small multiples of two cards
    (batteries_lunch_grids, peak_hour_grids) drawing NYISO's and ISO-NE's panels from tables held by grid. A held grid's
    panel is now taken out on the server, so its figures are not in the page; the chart says which grids and why."""

    def test_the_server_takes_a_held_grids_panel_out(self):
        s = src("site", "components", "analysis", "FindingCard.tsx")
        self.assertIn("export function heldMultiples(spec: ChartSpec): ChartSpec {", s)
        self.assertIn("const held = m.panels.filter((p) => licenseHeldGrid(p.grid));", s)
        self.assertIn("panels: m.panels.filter((p) => !licenseHeldGrid(p.grid))", s)
        self.assertEqual(s.count("spec={heldMultiples("), 3)   # the renderer's frame, the form chart, a further chart
        self.assertIn("<CardChart spec={heldMultiples(wk.card.chart)}", src("site", "app", "research", "page.tsx"))

    def test_the_client_chart_asks_no_license_and_draws_the_line(self):
        s = src("site", "components", "analysis", "MultiChart.tsx")
        self.assertNotIn("@/lib/license", s)          # the license file stays out of the client bundle
        self.assertIn("held?: { grid: string; words: string; why: string }[];", s)
        self.assertIn("data-multi-held=", s)
        self.assertIn("license needed (${h.why})", s)


class ThePublicTables(unittest.TestCase):
    def test_a_table_held_whole_is_not_offered(self):
        p = src("site", "app", "research", "page.tsx")
        self.assertIn(".filter((t) => !(licenseNeeded(t) && !licenseByGrid(t) && !licenseByRow(t))).sort();", p)
        self.assertIn('import { licenseByGrid, licenseByRow, licenseNeeded } from "@/lib/license";', p)
        self.assertIn("the public tables of the live set, by name", src("site", "components", "analysis", "AskForm.tsx"))

    def test_no_dash(self):
        for f in (("site", "app", "research", "page.tsx"), ("site", "lib", "researchrules.ts"), ("site", "app", "tokens.css")):
            text = src(*f)
            for ch in DASHES:
                self.assertNotIn(ch, text, f)


if __name__ == "__main__":
    unittest.main()
