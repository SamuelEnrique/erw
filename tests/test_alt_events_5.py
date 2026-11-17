"""Ruling alternative 5 of /events (session 7712, 17 November 2026, branch wip/alt-events-5; not a default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-events-2026-11-17.md, line 5): on the Elliott page,
cite FERC's 47,157 MW as SPP's all-time winter peak beside EIA-930's highest hour? On this branch SPP's paragraph cites it
from FERC, NERC and the Regional Entities' inquiry report (the page's own link to it), beside EIA's highest hour of the
window, 47,026 MW on 22 December 2022 (Central time): +131 MW, +0.28 percent. A figure added; nothing that stands moves.
Pinned with the page drawn with its own code on the replication's public rows (site/scripts/alt-events-figures.mjs; EIA's
figure draws as a number with the hold of 21 October stood aside, EVENTS_DRAW_UNHELD=1, and "license needed" under it).

    python -m unittest tests.test_alt_events_5 -v
"""

import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")


class FercsFigure(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        p = subprocess.run(["node", "--import", "./scripts/events-page-register.mjs", "scripts/alt-events-figures.mjs"], cwd=SITE, capture_output=True, text=True, timeout=600,
                           env=dict(os.environ, EVENTS_DRAW_UNHELD="1"))
        if p.returncode != 0:
            raise AssertionError(p.stderr[-2000:])
        cls.f = json.loads(p.stdout)

    def test_the_two_figures(self):
        self.assertEqual((self.f["ferc"], self.f["eiaMax"]), (47157, 47026))
        self.assertEqual((47157 - 47026, round((47157 / 47026 - 1) * 100, 2)), (131, 0.28))

    def test_the_paragraph(self):
        self.assertIn("FERC and NERC's inquiry report gives SPP's all-time winter peak as 47,157 MW", self.f["para"])
        self.assertIn("47,026 MW", self.f["para"])


if __name__ == "__main__":
    unittest.main()
