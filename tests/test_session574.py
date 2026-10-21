"""Sessions 574 and 575: petroleum supply and disposition's twelve more products, read as a second group after session
555's eight; and wood pellets' feedstock cost by fuel type, a fourth route of session 558's connector.
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import eia_petroleum_snd as P  # noqa: E402
import eia_wood_pellets as W  # noqa: E402


class TheGroups(unittest.TestCase):
    def test_two_groups_twenty_products(self):
        self.assertEqual([len(g) for g in P.GROUPS], [8, 12])
        self.assertEqual(len(set(P.PRODUCTS)), 20)
        for p in ("EPPK", "EPL2", "EPOORDO"):
            self.assertIn(p, P.GROUPS[1])


class TheFeedstocks(unittest.TestCase):
    def test_a_feedstock_row(self):
        rec = {"period": "2026-04", "fuelTypeId": "SR", "fuelTypeDescription": "Sawmill Residuals", "cost": "31.4", "cost-units": "USD per ton",
               "quantity": "1", "quantity-units": "tons"}
        r = W.rows("feedstocks-and-cost", [rec], "u", "r").iloc[0]
        self.assertEqual((r["entity"], r["variable"], r["value"], r["unit"], r["node"]),
                         ("eia_wood_pellets:feedstocks:SR", "feedstock_cost", 31.4, "USD/short_ton", "Sawmill Residuals"))

    def test_a_withheld_cost_has_no_row(self):
        rec = {"period": "2026-05", "fuelTypeId": "OR", "fuelTypeDescription": "Other Residuals", "cost": "W", "cost-units": "USD per ton"}
        self.assertEqual(len(W.rows("feedstocks-and-cost", [rec], "u", "r")), 0)


if __name__ == "__main__":
    unittest.main()
