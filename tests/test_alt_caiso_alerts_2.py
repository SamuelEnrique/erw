"""Ruling alternative 2 of /grid/caiso/alerts (session 7714, 17 November 2026, branch wip/alt-caiso-alerts-2; not a default
on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-caiso-alerts-2026-11-17.md, line 2): two cells
rounded twice sit one off in the last digit; store four or more decimals in the builder? On main the builder
(warehouse/derived/flex_alert_scorecard.py) stores four, so 2021-07-29's percent, -0.174972 at full precision, is stored
as -0.175 and drawn -0.18. On this branch it stores six (DECIMALS), and the page draws -0.17 (-5.6 percent of the cell).
2024's year MWh moves the same way by one cent (-16,893.33 to -16,893.32, under 1 percent); no other cell of the 471 the
replication rebuilds moves. Pinned on the builder's constant and on the page's own rounding rule (toLocaleString, at most
two decimals) applied to the figure as stored (site/scripts/alt-caiso-alerts-figures.mjs). The builder itself is not run
here: its inputs are the data machine's.

    python -m unittest tests.test_alt_caiso_alerts_2 -v
"""

import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")


class TheDecimals(unittest.TestCase):
    def test_the_builder_stores_six(self):
        with open(os.path.join(ROOT, "warehouse", "derived", "flex_alert_scorecard.py"), encoding="utf-8") as f:
            code = f.read()
        self.assertIn("\nDECIMALS = 6\n", code)
        self.assertIn("round(float(v), DECIMALS)", code)
        self.assertNotIn("round(float(v), 4)", code)

    def test_the_cell_as_the_page_draws_it(self):
        p = subprocess.run(["node", "scripts/alt-caiso-alerts-figures.mjs"], cwd=SITE, capture_output=True, text=True, timeout=120)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(json.loads(p.stdout), {"2021-07-29 percent": {"main": "-0.18", "branch": "-0.17", "true": "-0.17"}})


if __name__ == "__main__":
    unittest.main()
