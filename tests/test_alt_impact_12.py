"""Ruling alternative 12 of /impact (session 7706, 17 November 2026, branch wip/alt-impact-12; not a default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-impact-2026-11-17.md, line 12): Washington's
geothermal plant at cost, or by the steam and gas fired column 7.5 (the schedule Washington's gas plants use)? On this
branch by column 7.5 (site/data/forecast/property_rules.json, wa_geothermal_property). Pinned with the page's own model,
Washington geothermal as opened (levy 8.96, the state's average): property over the life USD 80.89 to 34.66 million
(-57.2 percent); first year 2.02 to 1.87 million; taxes, present value 25.20 to 15.48 million (-38.6 percent).

    python -m unittest tests.test_alt_impact_12 -v
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
from alt_impact_cases import JEDI_CSV, M, run_cases  # noqa: E402


@unittest.skipUnless(JEDI_CSV, "nlr_jedi_multipliers.csv is not on this machine")
class WashingtonGeothermalColumn75(unittest.TestCase):
    def test_washington_geothermal(self):
        f = run_cases([{"id": "wa", "tech": "geothermal", "state": "wa", "given": {}}])["wa"]
        self.assertEqual((M(f["sums"]["property"]), M(f["y1"]["property"]), M(f["pv"]["taxes"])), (34.66, 1.87, 15.48))


if __name__ == "__main__":
    unittest.main()
