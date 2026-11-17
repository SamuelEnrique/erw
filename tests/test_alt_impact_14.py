"""Ruling alternative 14 of /impact (session 7706, 17 November 2026, branch wip/alt-impact-14; not a default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-impact-2026-11-17.md, line 14): Louisiana's gas
severance is computed from a rate whose table is held; is the figure held too? On this branch it is: Louisiana is marked
held in the forecast's copy of the severance rules (site/lib/forecastdata.ts SEVERANCE_HELD), the page's callback returns
NaN for it and the model draws no figure, with the note "license needed" (site/lib/forecast.ts). /severance's own page is
not changed. Pinned with the page's own model, Louisiana's default gas plant with all its fuel from the state: "Severance,
each year" USD 6.41 million becomes blank, over the life 256.40 million becomes blank, and taxes, present value 155.15 to
75.28 million (-51.5 percent).

    python -m unittest tests.test_alt_impact_14 -v
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
from alt_impact_cases import JEDI_CSV, M, run_cases  # noqa: E402


@unittest.skipUnless(JEDI_CSV, "nlr_jedi_multipliers.csv is not on this machine")
class LouisianaSeveranceHeld(unittest.TestCase):
    def test_louisiana_gas(self):
        f = run_cases([{"id": "la", "tech": "natural_gas", "state": "la", "given": {"instate": 100}},
                       {"id": "nm", "tech": "natural_gas", "state": "nm", "given": {"instate": 100}}])
        la = f["la"]
        self.assertEqual((la["y1"]["severance"], la["sums"]["severance"], M(la["pv"]["taxes"])), (None, None, 75.28))
        self.assertEqual(la["severance"]["note"], "license needed: the rate's table is held")
        self.assertIsNotNone(f["nm"]["sums"]["severance"])


if __name__ == "__main__":
    unittest.main()
