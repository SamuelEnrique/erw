"""Session 1117 (chain 075): all the prices on the board.

Held here: the board's builder (warehouse/derived/board_page.py) draws three public price tables it did not before,
from real rows of each (tests/fixtures/session1117/, copied from the ERW archive's copy of the table):
the World Bank's monthly energy benchmarks (wb_commodity_prices_monthly: crude oil, coal, natural gas, LNG; no metal),
EIA's natural gas prices by sector and state (eia_gas_prices_state_monthly) and EIA's weekly heating oil and propane
prices (eia_heating_fuel_prices_weekly). Each row's latest value is its table's newest, its unit the table's, its area
named from EIA's code; each group's filters are the tags its rows carry; a table not on the machine builds no row and
is noted, as every other table. No network, no model. Nothing here sets the environment at import.
"""
import csv
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DERIVED = os.path.join(ROOT, "warehouse", "derived")
FIX = os.path.join(ROOT, "tests", "fixtures", "session1117")
EM = chr(0x2014)


def builder():
    if DERIVED not in sys.path:
        sys.path.insert(0, DERIVED)
    import board_page  # noqa: E402
    return board_page


def newest(table):
    """{entity: (ts_utc, value, unit)} of the fixture's newest row of each entity."""
    out = {}
    with open(os.path.join(FIX, table + ".csv"), encoding="utf-8") as f:
        for r in csv.DictReader(line for line in f if not line.startswith("#")):
            if r["entity"] not in out or r["ts_utc"] > out[r["entity"]][0]:
                out[r["entity"]] = (r["ts_utc"], float(r["value"]), r["unit"])
    return out


class TheNewRows(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bp = builder()
        cls.saved = cls.bp.ip.OUT_DIR
        cls.bp.ip.OUT_DIR = FIX
        cls.b, cls.log = cls.bp.Board(), []
        try:
            cls.bp.build_world(cls.b, cls.log.append)
            cls.bp.build_gas_prices(cls.b, cls.log.append)
            cls.bp.build_heating(cls.b, cls.log.append)
        finally:
            cls.bp.ip.OUT_DIR = cls.saved

    def rows(self, group):
        return [r for r in self.b.rows if r["group"] == group]

    def test_the_world_banks_nine_energy_benchmarks_and_no_metal(self):
        rows = self.rows("world")
        self.assertEqual([r["code"] for r in rows], [c for c, *_ in self.bp.WB_ENERGY])
        last = newest("wb_commodity_prices_monthly")
        for r in rows:
            t, v, unit = last[f"wb_pink:{r['code']}"]
            self.assertEqual((r["last"]["t"], r["last"]["v"], r["unit"], r["freq"], r["status"]), (t[:10], round(v, 4), unit, "M", "ok"), r["id"])
            self.assertIn(r["tags"]["kind"], ("crude", "coal", "gas"))
        self.assertNotIn("wb-pink-copper", [r["id"] for r in rows])

    def test_gas_by_sector_and_state_named_from_the_code(self):
        rows = self.rows("gasprices")
        self.assertEqual(len(rows), 20)
        last = newest("eia_gas_prices_state_monthly")
        for r in rows:
            entity = "eia_gas_price:" + r["code"].replace(" ", ":")
            t, v, unit = last[entity]
            self.assertEqual((r["last"]["t"], r["last"]["v"], r["unit"]), (t[:10], round(v, 4), unit))
        self.assertEqual(sorted({r["at"] for r in rows}), ["Alabama, monthly", "California, monthly", "Texas, monthly", "United States, monthly"])
        self.assertEqual([r["tags"]["sector"] for r in rows if r["tags"]["area"] == "us"], ["citygate", "residential", "commercial", "industrial", "electric_power"])

    def test_heating_oil_and_propane_by_area(self):
        rows = self.rows("heating")
        self.assertEqual(len(rows), 11)
        last = newest("eia_heating_fuel_prices_weekly")
        for r in rows:
            t, v, unit = last["eia_heating_price:" + r["code"]]
            self.assertEqual((r["last"]["t"], r["last"]["v"], r["unit"], r["freq"]), (t[:10], round(v, 4), unit, "W"))
        self.assertEqual({r["at"].split(",")[0] for r in rows}, {"United States", "East Coast (PADD 1)", "Connecticut"})
        self.assertEqual({r["tags"]["product"] for r in rows}, {"heating_oil", "propane"})

    def test_each_groups_filters_are_its_rows_tags(self):
        groups = {g["id"]: g for g in self.bp.GROUPS}
        order = [g["id"] for g in self.bp.GROUPS]
        self.assertLess(order.index("gas"), order.index("gasprices"))
        self.assertLess(order.index("oilspreads"), order.index("world"))
        self.assertLess(order.index("retailfuel"), order.index("heating"))
        for gid in ("world", "gasprices", "heating"):
            for f in groups[gid]["filters"]:
                values = {o[0] for o in f["options"]} - {"all"}
                self.assertEqual({r["tags"][f["key"]] for r in self.rows(gid)} - values, set(), (gid, f["key"]))
                self.assertIn(f["default"], {o[0] for o in f["options"]})

    def test_a_table_not_on_the_machine_builds_no_row(self):
        bp = self.bp
        saved, absent = bp.ip.OUT_DIR, list(bp.ABSENT)
        bp.ip.OUT_DIR = os.path.join(FIX, "no-such-folder")
        b, log = bp.Board(), []
        try:
            bp.build_world(b, log.append)
            bp.build_gas_prices(b, log.append)
            bp.build_heating(b, log.append)
        finally:
            bp.ip.OUT_DIR = saved
            bp.ABSENT[:] = absent
        self.assertEqual(b.rows, [])
        self.assertEqual(len(log), 3)
        self.assertTrue(all("not on this machine, skipped" in line for line in log))

    def test_no_em_dash(self):
        with open(os.path.join(DERIVED, "board_page.py"), encoding="utf-8") as f:
            self.assertNotIn(EM, f.read())
        for r in self.b.rows:
            self.assertNotIn(EM, r["label"] + r["at"])


if __name__ == "__main__":
    unittest.main()
