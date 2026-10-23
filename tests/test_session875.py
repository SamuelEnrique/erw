"""Session 875: EIA's coal receipts at power plants, as eia_coal_receipts_annual.

Energy Research Warehouse (ERW). Tests warehouse/connectors/eia_coal_receipts.py on records built here in the form of
EIA's route coal/shipments/receipts (figures made up for the test, not EIA's): the key with contract type and transport
mode, the units (short_ton, USD/short_ton, Btu/lb, pct), a record twice with two values left out whole, the unit
vocabulary (Decision 52), the sector rule and the holds. No network.

    python -m unittest tests.test_session875 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
sys.path.append(os.path.join(ROOT, "warehouse", "validate"))
import eia_coal_receipts as C  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402
import erw_validate as V  # noqa: E402


def rec(qty="1000", transport="Rail", contract="Contract Purchase"):
    return {"period": "2024", "mineMSHAId": "4800677", "mineName": "M", "mineStateId": "WY", "plantId": "6146", "plantName": "P",
            "plantStateId": "TX", "coalSupplier": "A Supplier, Inc.", "coalRankId": "SUB", "coalRankDescription": "Subbituminous",
            "contractType": contract, "transportationMode": transport, "quantity": qty, "price": "40.1", "heat-content": "8800",
            "sulfur-content": "0.3", "ash-content": "5.1", "quantity-units": "tons", "price-units": "average dollars per ton",
            "heat-content-units": "Btu per pound", "sulfur-content-units": "percent by weight", "ash-content-units": "percent by weight"}


class Receipts(unittest.TestCase):
    def test_rows_and_units(self):
        t = C.rows([rec()], "u", "r").set_index("variable")
        self.assertEqual(t["entity"].iloc[0], "eia_coal_receipt:4800677:6146:A_Supplier_Inc:SUB:Contract_Purchase:Rail")
        self.assertEqual({v: t.loc[v, "unit"] for v in t.index},
                         {"quantity": "short_ton", "price": "USD/short_ton", "heat_content": "Btu/lb", "sulfur_content": "pct", "ash_content": "pct"})
        self.assertEqual(t.loc["quantity", "geo"], "US-TX")

    def test_transport_is_in_the_key_and_two_values_have_none(self):
        C.NO_KEY.clear()
        both = C.rows([rec(transport="Rail"), rec(transport="Truck")], "u", "r")
        self.assertEqual(both["entity"].nunique(), 2)
        s = C.no_key(C.rows([rec("1000"), rec("2000"), rec("1000", transport="Truck")], "u", "r"))
        self.assertEqual(s["entity"].unique().tolist(), ["eia_coal_receipt:4800677:6146:A_Supplier_Inc:SUB:Contract_Purchase:Truck"])
        self.assertEqual(len(C.NO_KEY), 1)


class Registered(unittest.TestCase):
    def test_unit_sector_holds(self):
        self.assertIn("Btu/lb", V.UNITS)
        self.assertEqual(B.sector_of("eia_coal_receipts_annual"), "coal;power")
        self.assertIn("eia_coal_receipts_annual", R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn("  - eia_coal_receipts_annual", f.read())


if __name__ == "__main__":
    unittest.main()
