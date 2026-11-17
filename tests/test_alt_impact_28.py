"""Ruling alternative 28 of /impact (session 7706, 17 November 2026, branch wip/alt-impact-28; not a default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-impact-2026-11-17.md, line 28): Idaho taxes gross
energy earnings (Code 63-3502B: 3 percent wind and geothermal, 3.5 percent solar), and no Idaho sale price is held; add a
price input? On this branch the reader may type a sale price (site/lib/forecastui.ts field "saleprice", site/lib/forecast.ts
Inputs.saleprice and the rules with earnings_pct in site/data/forecast/property_rules.json). No price is assumed: with none
typed nothing is drawn, as on main. Pinned with the page's own model: Idaho wind as opened, 671,366 MWh a year, pays USD
20,141 a year for each USD 1 per MWh of sale price.

    python -m unittest tests.test_alt_impact_28 -v
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
from alt_impact_cases import JEDI_CSV, run_cases  # noqa: E402


@unittest.skipUnless(JEDI_CSV, "nlr_jedi_multipliers.csv is not on this machine")
class IdahoEarnings(unittest.TestCase):
    def test_idaho(self):
        f = run_cases([{"id": "w1", "tech": "land_based_wind", "state": "id", "given": {"saleprice": 1}},
                       {"id": "w0", "tech": "land_based_wind", "state": "id", "given": {}},
                       {"id": "s1", "tech": "utility_pv", "state": "id", "given": {"saleprice": 1}}])
        self.assertEqual(round(f["w1"]["y1"]["property"]), 20141)
        self.assertIsNone(f["w0"]["y1"]["property"])
        mwh = f["s1"]["x"]["mw"] * 8760 * f["s1"]["x"]["cf"]
        self.assertAlmostEqual(f["s1"]["y1"]["property"], mwh * 0.035, delta=1e-6)


if __name__ == "__main__":
    unittest.main()
