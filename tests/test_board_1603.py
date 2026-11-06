"""Session 1603 (chain 165): the board's oil rows: the two series held and not drawn.

Held here, on real rows cut from the old laptop's tables (tests/fixtures/board_1603/): North Dakota's first purchase
price is a monthly row of the crude group, and Mars Blend's is not drawn twice (it is the crude stream row); US
gasoline of all grades is a weekly row beside the US regular row, under the retail group's default filters; the coal
spot placeholders name the World Bank's monthly coal rows. No network, no model. Nothing here sets the environment
at import.
"""
import os
import sys
import unittest

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DERIVED = os.path.join(ROOT, "warehouse", "derived")
FIX = os.path.join(ROOT, "tests", "fixtures", "board_1603")


def builder():
    if DERIVED not in sys.path:
        sys.path.insert(0, DERIVED)
    import board_page  # noqa: E402
    return board_page


class TheOilRows(unittest.TestCase):
    def setUp(self):
        self.bp = builder()
        self.saved, self.absent = self.bp.ip.OUT_DIR, list(self.bp.ABSENT)
        self.bp.ip.OUT_DIR = FIX

    def tearDown(self):
        self.bp.ip.OUT_DIR, self.bp.ABSENT[:] = self.saved, self.absent

    def test_north_dakota_and_not_mars_twice(self):
        b = self.bp.Board()
        self.bp.build_more_oil(b, lambda s: None)
        rows = {r["id"]: r for r in b.rows}
        r = rows["eia-f002038-3-first-purchase-price"]
        t = pd.read_csv(os.path.join(FIX, "eia_crude_first_purchase_prices.csv"), comment="#")
        g = t[t["entity"] == "eia:F002038__3"].sort_values("ts_utc")
        self.assertEqual((r["group"], r["freq"], r["unit"], r["tags"]["kind"]), ("crude", "M", "USD/bbl", "first_purchase_price"))
        self.assertEqual((r["last"]["t"], r["last"]["v"]), (g["ts_utc"].iloc[-1][:10], round(float(g["value"].iloc[-1]), 4)))
        self.assertFalse([i for i in rows if "f003075793" in i])
        self.assertIn("Bakken", r["basis"])

    def test_all_grades_beside_regular(self):
        b = self.bp.Board()
        b.add("retailfuel", "eia:EMM_EPMR_PTE_NUS_DPG|retail", "Gasoline, regular", "USD/gal", "W", {}, tags=dict(product="gasoline", area="region"))
        b.add("retailfuel", "eia:EMM_EPMR_PTE_YBOS_DPG|retail", "Gasoline, regular", "USD/gal", "W", {}, tags=dict(product="gasoline", area="city"))
        self.bp.build_more_oil(b, lambda s: None)
        ids = [r["id"] for r in b.rows if r["group"] == "retailfuel"]
        self.assertEqual(ids, ["eia-emm-epmr-pte-nus-dpg-retail", "eia-emm-epm0-pte-nus-dpg-retail", "eia-emm-epmr-pte-ybos-dpg-retail"])
        r = next(r for r in b.rows if r["id"] == "eia-emm-epm0-pte-nus-dpg-retail")
        t = pd.read_csv(os.path.join(FIX, "eia_retail_fuel_prices.csv"), comment="#")
        g = t[t["entity"] == "eia:EMM_EPM0_PTE_NUS_DPG"].sort_values("ts_utc")
        self.assertEqual((r["status"], r["freq"], r["last"]["v"]), ("ok", "W", round(float(g["value"].iloc[-1]), 4)))
        self.assertEqual(r["tags"], {"product": "gasoline", "area": "region"})

    def test_the_coal_placeholders_name_the_world_rows(self):
        with open(os.path.join(DERIVED, "board_page.py"), encoding="utf-8") as f:
            src = f.read()
        self.assertIn("The World Bank's monthly export prices of Australian and South African coal are under World energy benchmarks, monthly.", src)
        self.assertIn("build_more_oil(b, log)", src)


if __name__ == "__main__":
    unittest.main()
