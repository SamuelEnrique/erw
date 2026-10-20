"""Session 347: the economic impact tool, /impact ("What a project does for a state").

Energy Research Warehouse (ERW). What is held: the page is in review and in the Economics menu under its own line; its
three questions, its decisions block, its downloads and its source line are drawn; every figure it draws carries a
check key of a family scripts/check-values.mjs recomputes; the arithmetic of site/lib/impact.ts, at JEDI's own defaults,
gives JEDI's own figure (checked here in Python against the table where this machine holds it); no em dash.

    python -m unittest tests.test_session347 -v
"""

import os
import re
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
OUT = os.path.join(ROOT, "warehouse", "output", "nlr_jedi_multipliers.csv")


def read(*p):
    with open(os.path.join(*p), encoding="utf-8") as f:
        return f.read()


class ThePage(unittest.TestCase):
    def setUp(self):
        self.page = read(SITE, "app", "impact", "page.tsx")
        self.lib = read(SITE, "lib", "impact.ts")

    def test_in_review_and_in_the_economics_menu(self):
        self.assertRegex(read(SITE, "lib", "release.ts"), r'"/impact": "review"')
        pages = read(SITE, "lib", "pages.ts")
        econ = pages[pages.index('label: "Economics"'):pages.index('label: "Infrastructure Economics"')]
        self.assertIn('href: "/impact", label: "Economic impact"', econ)

    def test_the_three_questions_in_order(self):
        qs = [m.group(1) for m in re.finditer(r'<ToolSection title="([^"]+)"', self.page)]
        self.assertEqual(qs, ["How many jobs?", "What does it pay the state?", "What matters most?"])
        for n in ("1", "2", "3"):
            self.assertIn(f'data-question="{n}"', self.page)

    def test_the_decisions_downloads_and_source(self):
        self.assertIn('data-decisions="347"', self.page)
        self.assertIn("<TableDownloads tables={[TABLE]} />", self.page)
        self.assertIn('data-tax-download="held"', self.page, "the tax table is not settled, so it is not offered")
        self.assertIn("<SourceLine tables={[TABLE, TAX_TABLE]}", self.page)
        self.assertIn("this entire notice appears in all copies of the Data", self.page)

    def test_every_figure_is_a_checked_num(self):
        self.assertIn("check={`${inputsKey(x)}|${s}`}", self.page)
        self.assertIn("check={`series|${TABLE}|${r.entity}|${r.variable}|${iso(r.ts_utc)}`}", self.page)
        cv = read(SITE, "scripts", "check-values.mjs")
        self.assertIn('if (p[0] === "impact")', cv)
        self.assertIn('"/impact"', cv)

    def test_battery_storage_is_named_and_never_filled(self):
        self.assertIn("NOT_MODELED", self.page)
        self.assertIn('battery_storage', self.lib)
        self.assertNotIn('key: "battery_storage", label', self.lib.split("export const TECHS")[1].split("];")[0])

    def test_every_default_is_jedis(self):
        self.assertRegex(self.lib, r'DEFAULTS: Inputs = \{ tech: "land_based_wind", state: "tx", mw: null, capex: 100, local: 100, life: null, abate: false \}')

    def test_no_em_dash(self):
        for f in (os.path.join(SITE, "app", "impact", "page.tsx"), os.path.join(SITE, "app", "impact", "StateChart.tsx"),
                  os.path.join(SITE, "lib", "impact.ts"), os.path.join(ROOT, "docs", "reviews", "packs", "impact.md"),
                  os.path.join(ROOT, "docs", "methods", "economic_impact.md")):
            self.assertEqual(read(f).count(chr(0x2014)), 0, f)


class TheArithmetic(unittest.TestCase):
    """lib/impact.ts's factor, in Python, on the table: at the defaults the page's figure is JEDI's per MW times its MW."""

    def setUp(self):
        if not os.path.exists(OUT):
            self.skipTest("nlr_jedi_multipliers is not on this machine")
        self.d = pd.read_csv(OUT, comment="#", keep_default_na=False, dtype={"x_state": str})

    def v(self, ent, var):
        return float(self.d[(self.d.entity == ent) & (self.d.variable == var)].value.iloc[0])

    def test_the_default_case(self):
        mw = self.v("nlr_jedi:land_based_wind:tx:all:project", "project_mw")
        self.assertEqual(mw, 300.0)
        built = self.v("nlr_jedi:land_based_wind:tx:construction:total", "jobs") * mw
        self.assertAlmostEqual(built, 1026.678, places=3)
        each = self.v("nlr_jedi:land_based_wind:tx:operations:total", "jobs") * mw
        self.assertAlmostEqual(each, 67.1037, places=4)

    def test_texas_is_twelfth_of_fifty_one_for_wind(self):
        c = self.d[(self.d.x_technology == "land_based_wind") & (self.d.x_phase == "construction") & (self.d.x_effect == "total")
                   & (self.d.variable == "jobs") & (self.d.x_state != "")].sort_values("value", ascending=False)
        self.assertEqual(len(c), 51)
        self.assertEqual(list(c.x_state).index("TX") + 1, 12)


if __name__ == "__main__":
    unittest.main()
