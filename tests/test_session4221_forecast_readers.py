"""Session 4221 (chain 239): the forecast page read as an economic developer, a county assessor and a utility siting analyst.

Energy Research Warehouse (ERW). No network, no build. Each reader's addition is held by a test: the developer's output
rows in A and B, the assessor's MWh and taxable value in the table by year (the model's own year fields, tested in
site/scripts/test-forecast.test.mjs), the siting analyst's taxes in other states. docs/reviews/forecast-faults-2026-11-13.md.
"""

import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PAGE = os.path.join(ROOT, "site", "app", "impact", "Forecast.tsx")


class TheReaders(unittest.TestCase):
    def setUp(self):
        with open(PAGE, encoding="utf-8") as f:
            self.page = f.read()

    def test_the_developer_sees_output_beside_earnings(self):
        self.assertIn('figure: "c:output:total"', self.page)
        self.assertIn('figure: "o:output:total"', self.page)

    def test_the_assessor_sees_mwh_and_taxable_value_where_they_apply(self):
        self.assertIn('...(hasMwh ? ["MWh"] : [])', self.page)
        self.assertIn('...(hasValue ? ["Taxable value"] : [])', self.page)
        self.assertIn('(r.property.rule ?? "").includes("production")', self.page)

    def test_14_each_state_takes_its_own_defaults(self):
        # fault 14: the other states' runs resolve the scenario's values (NaN where not set) in each state
        self.assertIn("const res = run(resolve(P, { ...v, state: ix, proj: NaN }), unpack(jedi, x.tech, st), P, sev);", self.page)
        self.assertNotIn("run({ ...x, state: st }", self.page)

    def test_the_siting_analyst_sees_the_taxes_in_other_states_and_what_they_hold(self):
        self.assertIn('title="Taxes, present value, in other states"', self.page)
        self.assertIn("no property tax rule held: sales and income tax only", self.page)
        self.assertRegex(self.page, r"saysOnCard\s+says=\{\(i\) => `\$\{byTax\[i\]\.name\}", "the hover says which states count a property tax")


class Fault16(unittest.TestCase):
    def test_16_the_own_rate_tip_does_not_say_no_statute_where_one_is_held(self):
        with open(os.path.join(ROOT, "site", "lib", "forecastui.ts"), encoding="utf-8") as f:
            ui = f.read()
        self.assertIn("The state's statute leaves some years or cases open", ui)
        own = ui[ui.index('{ key: "own",'):ui.index('{ key: "ownyears",')]
        self.assertIn("(P.property.states[s]?.rules ?? []).some((r) => r.technologies.includes(t))", own)


class Fault19(unittest.TestCase):
    def test_19_no_chart_on_the_page_carries_a_visible_note(self):
        # explanations only as hover tips (the owner's tool rules): the states chart's sentence under it became a tip
        for name in ("StateChart.tsx", "Forecast.tsx"):
            with open(os.path.join(ROOT, "site", "app", "impact", name), encoding="utf-8") as f:
                src = f.read()
            self.assertNotRegex(src, r"\bnote=", name)
        with open(os.path.join(ROOT, "site", "app", "impact", "StateChart.tsx"), encoding="utf-8") as f:
            self.assertIn("tip={<Tip id=", f.read())


if __name__ == "__main__":
    unittest.main()
