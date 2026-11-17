"""Ruling alternative 4 of /cost-of-power/battery/awards (session 7705, 17 November 2026, branch wip/alt-battery-awards-4;
not a default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-battery-awards-2026-11-17.md, line 4): an A and
B of two settlement points by name? On this branch the real-time section has a box "Two points side by side": two lists
of the storage settlement points and, for each point chosen (?a= and ?b= in the address), its own spread over the days
measured and its place, widest first (site/lib/storagerealtime.ts pointsOf, pointNamed; the page reads the variable
spread_node of ercot_storage_node_basis). No figure that stands moves; two cells are added. Pinned with the page's own
library and component on the public table (site/scripts/alt-battery-awards-figures.mjs), where it is on the machine
(warehouse/output, or the folder ERW_TABLES_DIR names): 293 points, the widest KNAPP_RN at USD 354.96 per MWh, the
narrowest USD 47.60, the median 68.22 (the impact file's figures, week of 28 September 2026); AMAD_ESS_RN USD 54.48,
259th. A name the list does not hold is said so and draws no figure.

    python -m unittest tests.test_alt_battery_awards_4 -v
"""

import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
TABLES = os.environ.get("ERW_TABLES_DIR") or os.path.join(ROOT, "warehouse", "output")
NEED = ("ercot_storage_node_basis", "ercot_storage_rt_monthly", "battery_stack_monthly")


def figures(a, b):
    p = subprocess.run(["node", "--import", "./scripts/tsx-register.mjs", "scripts/alt-battery-awards-figures.mjs", TABLES, a, b], cwd=SITE, capture_output=True, text=True, timeout=300)
    if p.returncode != 0:
        raise AssertionError(p.stderr[-2000:])
    return json.loads(p.stdout)


@unittest.skipUnless(all(os.path.exists(os.path.join(TABLES, f"{t}.csv")) for t in NEED), "the public tables are not on this machine")
class TwoPoints(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.f = figures("KNAPP_RN", "amad_ess_rn")
        cls.none = figures("NOT_A_POINT", "")

    def test_the_points(self):
        f = self.f
        self.assertEqual(f["points"], 293)
        self.assertEqual((f["widest"]["name"], round(f["widest"]["spread"], 2), round(f["narrowest"]["spread"], 2), round(f["median"], 2)), ("KNAPP_RN", 354.96, 47.60, 68.22))

    def test_two_points_side_by_side(self):
        f = self.f
        self.assertEqual((f["a"]["place"], f["b"]["name"], f["b"]["place"]), (1, "AMAD_ESS_RN", 259))
        self.assertEqual(f["drawn"], {"a": "USD 354.96 per MWh", "b": "USD 54.48 per MWh", "options": 588, "notFound": False})

    def test_a_name_not_held_draws_no_figure(self):
        self.assertEqual(self.none["drawn"], {"a": None, "b": None, "options": 588, "notFound": True})


if __name__ == "__main__":
    unittest.main()
