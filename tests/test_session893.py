"""Session 893: the package test's expected license flags agree with coverage.csv.

Energy Research Warehouse (ERW). On 22 October 2026 the daily run's package test failed on
carb_auction_allowance_prices: package/tests/test_erw.py still expected "internal", though session 324 had made the table
public (carbon_auctions.py) and the daily run's coverage had taken the flag. This test reads PRICE_BOARD from the package
test's source (without importing it, which needs the package's data) and checks each table's expected license against
warehouse/metadata/coverage.csv, so such a drift fails at landing, not in a daily run. No network.

    python -m unittest tests.test_session893 -v
"""

import ast
import csv
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def price_board():
    with open(os.path.join(ROOT, "package", "tests", "test_erw.py"), encoding="utf-8") as f:
        tree = ast.parse(f.read())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "PRICE_BOARD" for t in node.targets):
            return {k.value: v.elts[2].value for k, v in zip(node.value.keys, node.value.values)}
    raise AssertionError("PRICE_BOARD is not in package/tests/test_erw.py")


class PackageTestFlags(unittest.TestCase):
    def test_expected_license_is_coverage_flag(self):
        with open(os.path.join(ROOT, "warehouse", "metadata", "coverage.csv"), encoding="utf-8") as f:
            cov = {r["table"]: r["license"] for r in csv.DictReader(f)}
        board = price_board()
        self.assertIn("carb_auction_allowance_prices", board)
        for table, expected in board.items():
            if table in cov:
                self.assertEqual(expected, cov[table], table)


if __name__ == "__main__":
    unittest.main()
