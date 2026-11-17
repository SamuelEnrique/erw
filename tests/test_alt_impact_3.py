"""Ruling alternative 3 of /impact (session 7706, 17 November 2026, branch wip/alt-impact-3; not a default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-impact-2026-11-17.md, line 3): no taxable share
of spending is held for geothermal (JEDI's model has no sales tax line); should one plant's set the default? Nevada's two
fiscal notes for Lone Mountain Geothermal give 3.3 percent (the Department of Taxation: USD 5,920,244 of 178,446,043) and
48 percent (the Budget Division). On this branch the default is the Department of Taxation's, 0.033177
(site/data/forecast/jedi_taxable.json). Pinned with the page's own model: Lone Mountain (36 MW, USD 4,956.83 per kW, from
2026) reads sales and use tax USD 0.49 million where main reads "not held", and taxes, present value 0.47 million where
main reads USD 0; every state's geothermal case gains a sales tax figure the same way.

    python -m unittest tests.test_alt_impact_3 -v
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
from alt_impact_cases import JEDI_CSV, M, run_cases  # noqa: E402


@unittest.skipUnless(JEDI_CSV, "nlr_jedi_multipliers.csv is not on this machine")
class GeothermalTaxableShare(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.f = run_cases([{"id": "lm", "tech": "geothermal", "state": "nv", "given": {"mw": 36, "capex": 4956.83, "start": 2026}},
                           {"id": "ut", "tech": "geothermal", "state": "ut", "given": {}}])

    def test_lone_mountain(self):
        lm = self.f["lm"]
        self.assertEqual(lm["x"]["taxable"], 3.3177)
        self.assertEqual((M(lm["sums"]["sales"]), M(lm["pv"]["taxes"])), (0.49, 0.47))
        self.assertTrue(lm["sales"]["held"])

    def test_another_states_case_gains_a_figure(self):
        self.assertIsNotNone(self.f["ut"]["sums"]["sales"])


if __name__ == "__main__":
    unittest.main()
