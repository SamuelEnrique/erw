"""Session 1606 (chain 165): the power spreads.

Held here, on real rows cut from the old laptop's tables (tests/fixtures/board_1606/: ERCOT's North, Houston and hub
average and SPP's North hub, day-ahead, 20 to 24 August 2026, and Henry Hub): a hub spread is the first hub's daily mean
less the second's on the same date, within a grid and across two; a pair with no real-time rows held has its real-time
row "not held yet"; the spark spread is drawn at every public hub, the main hub's as before and the others behind the
group's Show filter; every spark and dark row says its heat rate is the board's assumption, and names EIA's fleet
average beside it when the table is on the machine. No network, no model. Nothing here sets the environment at import.
"""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DERIVED = os.path.join(ROOT, "warehouse", "derived")
SITE = os.path.join(ROOT, "site")
FIX = os.path.join(ROOT, "tests", "fixtures", "board_1606")


def builder():
    if DERIVED not in sys.path:
        sys.path.insert(0, DERIVED)
    import board_page  # noqa: E402
    return board_page


class TheSpreads(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        bp = cls.bp = builder()
        saved, absent, intervals = bp.ip.OUT_DIR, list(bp.ABSENT), dict(bp.INTERVALS)
        bp.ip.OUT_DIR = FIX
        try:
            hol = bp.pb.nerc_holidays(range(2025, 2028))
            b = cls.b = bp.Board()
            store = bp.hourly_store(lambda s: None, tables=["ercot_all_hub_prices_history", "iso_hub_prices_history"])
            daily = bp.build_power(b, store, hol, lambda s: None)
            s, _ = bp.table_daily("eia_fuel_spot_prices")
            bp.build_spreads(b, daily, {"eia:henry_hub": s[("eia:henry_hub", "spot_price")]}, {})
        finally:
            bp.ip.OUT_DIR, bp.ABSENT[:] = saved, absent
            bp.INTERVALS.clear(); bp.INTERVALS.update(intervals)
        cls.rows = {r["id"]: r for r in b.rows}

    def test_within_a_grid(self):
        r, n, h = self.rows["ercot-hb-north-ercot-hb-houston-da"], self.rows["ercot-hb-north-da"], self.rows["ercot-hb-houston-da"]
        self.assertEqual((r["group"], r["status"], r["label"], r["tags"]), ("hubspread", "ok", "ERCOT North hub less Houston hub", {"market": "da", "scope": "within"}))
        self.assertEqual(r["last"]["t"], n["last"]["t"])
        self.assertAlmostEqual(r["last"]["v"], n["last"]["v"] - h["last"]["v"], places=3)
        self.assertAlmostEqual(r["moves"]["d"]["v"], n["moves"]["d"]["v"] - h["moves"]["d"]["v"], places=3)
        self.assertIn("the same local operating day", r["formula"])
        self.assertEqual(self.rows["ercot-hb-north-ercot-hb-houston-rt"]["status"], "not_held")

    def test_across_grids(self):
        r, e, s = self.rows["ercot-hb-hubavg-spp-sppnorth-hub-da"], self.rows["ercot-hb-hubavg-da"], self.rows["spp-sppnorth-hub-da"]
        self.assertEqual((r["label"], r["tags"]["scope"]), ("ERCOT Hub average less SPP North hub", "across"))
        self.assertEqual(r["last"]["t"], min(e["last"]["t"], s["last"]["t"]))
        self.assertIn("each on its own local operating day", r["basis"])

    def test_the_spark_spread_at_every_public_hub(self):
        main, north = self.rows["ercot-hb-hubavg-spark"], self.rows["ercot-hb-north-spark"]
        self.assertNotIn("scope", main["tags"])                 # the main hub's row shows under either Show, as before
        self.assertEqual(north["tags"], {"grid": "ERCOT", "scope": "all"})
        self.assertEqual(north["status"], "ok")
        self.assertNotIn("ercot-hb-north-heat", self.rows)       # the implied heat rate stays the main hub's
        for r in (main, north, self.rows["ercot-hb-hubavg-dark"]):
            self.assertIn("is the board's stated assumption", r["basis"])
            self.assertNotIn("EIA's average operating heat rate", r["basis"])   # the table is not in the fixture
        self.assertIn("10.5 MMBtu/MWh", self.rows["ercot-hb-hubavg-dark"]["basis"])

    def test_the_fleet_heat_rate_beside_the_assumption(self):
        ref = {"natural_gas": dict(t="2025-01-01", v=7.5, table="eia_heat_rates_annual")}     # an in-memory reading, not a fixture of EIA's numbers
        words = self.bp.heat_basis("spark", ref)
        self.assertIn("EIA's average operating heat rate of the US natural gas fleet (combined-cycle and peaking plants together) was 7.5 MMBtu/MWh in 2025", words)
        self.assertNotIn("EIA's", self.bp.heat_basis("dark", ref))           # no coal reading given: the assumption alone

    def test_the_groups(self):
        ids = [g["id"] for g in self.bp.GROUPS]
        self.assertEqual(ids[ids.index("spark") + 1], "hubspread")
        spark = next(g for g in self.bp.GROUPS if g["id"] == "spark")
        self.assertEqual([f["key"] for f in spark["filters"]], ["grid", "scope"])
        with open(os.path.join(SITE, "lib", "board.ts"), encoding="utf-8") as f:
            self.assertIn('"battery", "as", "hubspread"]);', f.read())


if __name__ == "__main__":
    unittest.main()
