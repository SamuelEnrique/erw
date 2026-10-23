"""Session 923: every country's petroleum and natural gas from EIA's International Energy Statistics bulk file.

Energy Research Warehouse (ERW). Tests warehouse/connectors/eia_intl_bulk.py's second table on a bulk file built here in
EIA's form (figures made up for the test, not EIA's): thousand barrels a day as kbbl/d, billion cubic feet as bcf, million
barrels as kbbl, the cubic metre and Btu copies not taken, electricity's series left to the other table and the other
way round, a product not in the map stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session923 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
sys.path.insert(0, os.path.join(ROOT, "tests"))
import eia_intl_bulk as E  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402
from test_session909 import ser, bulk  # noqa: E402

SERIES = [
    ser("INTL.57-1-NOR-TBPD.A", "Crude oil including lease condensate production, Norway, Annual", [["2024", 1800.5], ["2023", "NA"]]),
    ser("INTL.26-1-NOR-BCF.A", "Dry natural gas production, Norway, Annual", [["2024", 4100]]),
    ser("INTL.26-1-NOR-BCM.A", "Dry natural gas production, Norway, Annual", [["2024", 116]]),
    ser("INTL.5-5-NOR-MBBL.A", "Petroleum and other liquids stocks, Norway, Annual", [["2024", 12.5]]),
    ser("INTL.66-13-NOR-TBPD.A", "Bunker residual fuel oil consumption, Norway, Annual", [["2024", 3]]),
    ser("INTL.5-2-NOR-QBTU.A", "Petroleum and other liquids consumption, Norway, Annual", [["2024", 0.4]]),
    ser("INTL.2-12-NOR-BKWH.A", "Electricity net generation, Norway, Annual", [["2024", 150]]),
]


class OilGas(unittest.TestCase):
    def test_units_and_tables(self):
        t, n = E.rows(E.read_series(bulk(SERIES)), "u", "r", "v", E.OIL_GAS)
        self.assertEqual(n, 4)
        g = t.set_index(["entity", "variable"])
        self.assertEqual((g.loc[("eia_intl:NOR:57", "production"), "value"], g.loc[("eia_intl:NOR:57", "production"), "unit"]), (1800.5, "kbbl/d"))
        self.assertEqual(g.loc[("eia_intl:NOR:26", "production"), "unit"], "bcf")
        self.assertEqual((g.loc[("eia_intl:NOR:5", "stocks"), "value"], g.loc[("eia_intl:NOR:5", "stocks"), "unit"]), (12500.0, "kbbl"))
        self.assertEqual(g.loc[("eia_intl:NOR:66", "bunker_consumption"), "node"], "Norway, Residual fuel oil")
        e, ne = E.rows(E.read_series(bulk(SERIES)), "u", "r", "v")
        self.assertEqual((ne, e.entity.tolist()), (1, ["eia_intl:NOR:2"]))

    def test_unknown_product_stops(self):
        bad = ser("INTL.999-1-NOR-TBPD.A", "Something production, Norway, Annual", [["2024", 1]])
        with self.assertRaises(RuntimeError):
            E.rows(E.read_series(bulk(SERIES + [bad])), "u", "r", "v", E.OIL_GAS)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        name = "eia_world_oil_gas_annual"
        self.assertEqual(B.sector_of(name), "oil;gas")
        self.assertIn(name, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {name}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
