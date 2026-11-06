"""Session 1602 (chain 165): the board's gas rows: storage, LNG and the hubs not held.

Held here, on real rows cut from the old laptop's tables (tests/fixtures/board_1602/): EIA's weekly working gas in
storage is a row a region, Lower 48 first, its week's move the week's injection or withdrawal and its year's move
against the same week a year before; EIA's LNG exports by terminal are a price row and a volume row a terminal, with
the United States' total and the pipeline trade beside them; daily feedgas is a placeholder naming who would supply
it; seven regional hubs are placeholders. No network, no model. Nothing here sets the environment at import.
"""
import os
import sys
import unittest

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DERIVED = os.path.join(ROOT, "warehouse", "derived")
FIX = os.path.join(ROOT, "tests", "fixtures", "board_1602")


def builder():
    if DERIVED not in sys.path:
        sys.path.insert(0, DERIVED)
    import board_page  # noqa: E402
    return board_page


def raw(name):
    return pd.read_csv(os.path.join(FIX, name + ".csv"), comment="#")


class TheGasFlows(unittest.TestCase):
    def setUp(self):
        self.bp = builder()
        self.saved, self.absent = self.bp.ip.OUT_DIR, list(self.bp.ABSENT)
        self.bp.ip.OUT_DIR = FIX
        self.b = self.bp.Board()
        self.bp.build_gasflows(self.b, lambda s: None)
        self.rows = {r["id"]: r for r in self.b.rows}

    def tearDown(self):
        self.bp.ip.OUT_DIR, self.bp.ABSENT[:] = self.saved, self.absent

    def test_storage_a_row_a_region(self):
        st = [r for r in self.b.rows if r["tags"].get("kind") == "storage"]
        self.assertEqual([r["at"] for r in st], [f"{w}, weekly" for w in self.bp.STORAGE_REGIONS.values()])
        r = self.rows["eia-nw2-epg0-swo-r48-bcf"]
        t = raw("eia_gas_storage_weekly")
        g = t[t["entity"] == "eia:NW2_EPG0_SWO_R48_BCF"].sort_values("ts_utc")
        self.assertEqual((r["group"], r["freq"], r["unit"], r["status"]), ("gasflows", "W", "Bcf", "ok"))
        self.assertEqual((r["last"]["t"], r["last"]["v"]), (g["ts_utc"].iloc[-1][:10], float(g["value"].iloc[-1])))
        # the week's move: the week's injection or withdrawal, against the week before
        self.assertEqual(r["moves"]["w"]["t"], g["ts_utc"].iloc[-2][:10])
        self.assertEqual(r["moves"]["w"]["ch"], round(float(g["value"].iloc[-1] - g["value"].iloc[-2]), 4))
        self.assertIsNone(r["moves"]["d"])
        # the year's move: the same week a year before (within the board's six days' slack)
        last = pd.Timestamp(g["ts_utc"].iloc[-1][:10])
        self.assertLessEqual((last - pd.Timestamp(r["moves"]["y"]["t"])).days - 365, 6)
        self.assertEqual(r["source"], self.bp.STORAGE_SOURCE)

    def test_lng_a_price_and_a_volume_a_terminal(self):
        t = raw("eia_lng_exports_monthly")
        prices = [r for r in self.b.rows if r["tags"].get("kind") == "lng_price"]
        self.assertEqual(len(prices), t[t["variable"] == "export_price"]["entity"].nunique())
        self.assertTrue(all(r["unit"] == "USD/Mcf" and r["freq"] == "M" for r in prices))
        r = self.rows["eia-ngm-epg0-png-yspl-z00-dmcf"]
        g = t[t["entity"] == "eia:NGM_EPG0_PNG_YSPL-Z00_DMCF"].sort_values("ts_utc")
        self.assertEqual((r["label"], r["at"]), ("LNG export price", "Sabine Pass, Louisiana, monthly"))
        self.assertEqual(r["last"]["v"], round(float(g["value"].iloc[-1]), 4))
        vols = [r for r in self.b.rows if r["tags"].get("kind") == "lng_volume" and r["status"] == "ok"]
        self.assertIn("eia-n9133us2", {r["id"] for r in vols})
        self.assertEqual(self.rows["eia-n9133us2"]["label"], "LNG exports, United States")
        # the terminals are in the order of LNG_TERMINALS: Sabine Pass first
        self.assertEqual(prices[0]["id"], "eia-ngm-epg0-png-yspl-z00-dmcf")

    def test_feedgas_is_a_placeholder_naming_the_source(self):
        r = self.rows["lng-feedgas"]
        self.assertEqual((r["status"], r["group"]), ("licensed", "gasflows"))
        self.assertIn("S&P Global Commodity Insights", r["note"])
        self.assertNotIn("last", r)

    def test_every_row_states_its_basis(self):
        for r in self.b.rows:
            if r["status"] == "ok":
                self.assertTrue(r.get("basis"), r["id"])

    def test_the_group_and_the_hubs(self):
        groups = [g["id"] for g in self.bp.GROUPS]
        self.assertEqual(groups[groups.index("gas") + 1], "gasflows")
        g = next(g for g in self.bp.GROUPS if g["id"] == "gasflows")
        self.assertEqual(g["filters"][0]["default"], "storage")
        with open(os.path.join(DERIVED, "board_page.py"), encoding="utf-8") as f:
            src = f.read()
        for hub in ("Houston Ship Channel", "Transco Zone 6 New York", "Eastern Gas South", "Waha"):
            self.assertIn(f'("{hub}", ', src)
        self.assertIn("build_gasflows(b, log)", src)


if __name__ == "__main__":
    unittest.main()
