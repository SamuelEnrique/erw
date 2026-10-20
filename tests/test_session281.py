"""Session 281: the finish pass of the Economics and Grid pages (/prices, /demand, /curtailment, /storage, /supply, /board).

Energy Research Warehouse (ERW), the daytime chain of 14 October 2026. What is held here, each a fix that needed no
ruling:
- the shared input panel takes a Reset (a plain link to the page's own address and the defaults in words), and the
  five panels whose choices live in the address carry one;
- the storage page's sparkline gives each point's date and value on hover, not only the first and last;
- two links go to today's addresses in one step (the board's ERCOT explorer, the curtailment page's energy mix);
- the board's threshold says its default; /demand prints no range from no earlier year;
- five method notes say what the code does (the owners table's live-set state, the tabs' addresses, demand's third
  view, the cleared-energy tables, curtailment's license hold and its California profile).
Nothing here sets the environment, reads a table or makes a request.
"""

import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class ResetLinks(unittest.TestCase):
    def test_the_panel_takes_a_reset(self):
        tool = src("site", "components", "tool", "ToolPage.tsx")
        self.assertIn("reset?: { href: string; defaults: string }", tool)
        self.assertIn('<a href={reset.href}>Reset to the defaults</a>', tool)

    def test_the_five_panels_carry_one(self):
        for parts, href in ((("site", "app", "prices", "compare", "page.tsx"), "/prices/compare"),
                            (("site", "app", "demand", "page.tsx"), "/demand"),
                            (("site", "app", "curtailment", "page.tsx"), "/curtailment"),
                            (("site", "app", "storage", "buildout", "view.tsx"), "/storage?tab=buildout"),
                            (("site", "app", "storage", "owners", "view.tsx"), "/storage?tab=owners")):
            self.assertIn(f'reset={{{{ href: "{href}", defaults: ', src(*parts), parts)


class SmallFixes(unittest.TestCase):
    def test_each_spark_point_hovers(self):
        spark = src("site", "components", "InlineSpark.tsx")
        self.assertIn("<title>{`${label}: ${p.t.slice(0, 10)} ${p.v.toFixed(2)}`}</title>", spark)

    def test_links_in_one_step(self):
        self.assertIn('<SiteLink href="/prices?tab=ercot">ERCOT since 2015', src("site", "components", "board", "BoardView.tsx"))
        self.assertNotIn('href="/explorer/ercot-peak-premium"', src("site", "components", "board", "BoardView.tsx"))
        self.assertIn('<SiteLink href="/grid?view=mix">the energy mix</SiteLink>', src("site", "app", "curtailment", "page.tsx"))

    def test_the_threshold_and_the_range(self):
        # session 328: the default is said beside the box (both of its rules), no longer in a title
        self.assertIn("\"halfway from the window's mean to its high\"", src("site", "components", "board", "Workbench.tsx"))
        self.assertIn("{file.caiso_break.rows.length > 1 ? <>; in the", src("site", "app", "demand", "page.tsx"))

    def test_the_method_notes(self):
        self.assertIn("loaded under `review_hold`", src("docs", "methods", "storage_owners.md"))
        self.assertIn("`/storage?tab=buildout`", src("docs", "methods", "storage_buildout.md"))
        self.assertIn("a third, consumption", src("docs", "methods", "demand_growth.md"))
        self.assertIn("`spp_dam_cleared_energy`", src("docs", "methods", "supply_and_trade.md"))
        self.assertIn("`licenseHeldGrids()` in `site/lib/license.ts`", src("docs", "methods", "curtailment.md"))
        for name in ("storage_owners.md", "storage_buildout.md", "demand_growth.md", "supply_and_trade.md", "curtailment.md"):
            self.assertEqual(src("docs", "methods", name).count(chr(0x2014)), 0, name)


if __name__ == "__main__":
    unittest.main()
