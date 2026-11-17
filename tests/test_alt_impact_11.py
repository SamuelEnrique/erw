"""Ruling alternative 11 of /impact (session 7706, 17 November 2026, branch wip/alt-impact-11; not a default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-impact-2026-11-17.md, line 11): a gas plant's
exempt machinery is JEDI's power generation equipment (58.3 percent of its taxable purchases), or that with the plant
equipment (84.5 percent)? On this branch 84.5 percent in the 12 states that hold the 58.3 (Georgia, Indiana, Kansas,
Massachusetts, Michigan, Missouri, Ohio, Pennsylvania, South Carolina, Vermont, Wisconsin, West Virginia;
site/data/forecast/sales_exemptions.json). Pinned with the page's own model, each state's default gas plant: sales and use
tax -62.9 percent; Georgia USD 21.51 to 7.99 million, Kansas 24.16 to 8.97, Missouri 25.52 to 9.48, Pennsylvania 20.09 to
7.46. The wind half of the line (the towers) is not built: the towers' share of JEDI's purchases is not in the files.

    python -m unittest tests.test_alt_impact_11 -v
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
from alt_impact_cases import JEDI_CSV, M, run_cases  # noqa: E402

STATES = ["ga", "in", "ks", "ma", "mi", "mo", "oh", "pa", "sc", "vt", "wi", "wv"]


@unittest.skipUnless(JEDI_CSV, "nlr_jedi_multipliers.csv is not on this machine")
class GasWithThePlantEquipment(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.f = run_cases([{"id": s, "tech": "natural_gas", "state": s, "given": {}} for s in STATES])

    def test_four_states(self):
        self.assertEqual({s: M(self.f[s]["sums"]["sales"]) for s in ("ga", "ks", "mo", "pa")}, {"ga": 7.99, "ks": 8.97, "mo": 9.48, "pa": 7.46})

    def test_every_state_at_84_5(self):
        self.assertEqual({s: self.f[s]["x"]["exempt"] for s in STATES}, {s: 84.5 for s in STATES})


if __name__ == "__main__":
    unittest.main()
