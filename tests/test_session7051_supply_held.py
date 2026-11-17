"""Session 7051 (chain 370, the data machine): done-line request 154.

site/data/supply.json, in the public repository, carried NYISO's day-ahead cleared row (its table held for license from
21 October 2026) and ISO-NE's (its table internal) with their figures. A held grid's cleared row is now written with its
status and note only.
"""

import importlib.util
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FIGURES = ("last", "prev", "year", "avg5", "change", "spark", "season")


def builder():
    spec = importlib.util.spec_from_file_location("supply_page_7051", os.path.join(ROOT, "warehouse", "derived", "supply_page.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class TheHeldCleared(unittest.TestCase):
    def test_a_held_grid_and_an_internal_table_are_named(self):
        m = builder()
        held = m.cleared_held({"NYISO": "held, not shown"}, {"isone_dam_cleared_energy": "internal", "nyiso_dam_cleared_energy": "public"})
        self.assertEqual(held["NYISO"], "held, not shown")
        self.assertIn("isone_dam_cleared_energy is held internal", held["ISO-NE"])
        self.assertNotIn("ERCOT", held)

    def test_the_committed_file_holds_no_figure_of_a_held_grid(self):
        with open(os.path.join(ROOT, "site", "data", "supply.json"), encoding="utf-8") as f:
            rows = json.load(f)["rows"]
        for r in rows:
            if r["id"] in ("cleared-nyiso", "cleared-iso-ne"):
                self.assertEqual(r["status"], "licensed", r["id"])
                self.assertEqual([k for k in FIGURES if k in r], [], r["id"])


if __name__ == "__main__":
    unittest.main()
