"""Ruling alternative 5 of /impact (session 7706, 17 November 2026, branch wip/alt-impact-5; not a default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-impact-2026-11-17.md, line 5): Wisconsin's solar
exemption (Statutes 77.54(56)) reaches the mounting, modules and inverters, 83.6 percent of JEDI's taxable purchases; or the
electrical materials too? On this branch it reaches them: 100 percent, the bound (the electrical share that qualifies is
not held; site/data/forecast/sales_exemptions.json). Pinned with the page's own model: Wisconsin solar as opened reads
sales and use tax USD 0 where main reads 1.48 million (-100 percent at the bound).

    python -m unittest tests.test_alt_impact_5 -v
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
from alt_impact_cases import JEDI_CSV, M, run_cases  # noqa: E402


@unittest.skipUnless(JEDI_CSV, "nlr_jedi_multipliers.csv is not on this machine")
class WisconsinSolarElectrical(unittest.TestCase):
    def test_the_sales_tax_at_the_bound(self):
        f = run_cases([{"id": "wi", "tech": "utility_pv", "state": "wi", "given": {}}])["wi"]
        self.assertEqual((f["x"]["exempt"], M(f["sums"]["sales"])), (100, 0.0))
        self.assertEqual(M(f["pv"]["taxes"]), 14.44)


if __name__ == "__main__":
    unittest.main()
