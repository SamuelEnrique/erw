"""Session 937: every country's coal, total energy and CO2 emissions from EIA's International Energy Statistics bulk file.

Energy Research Warehouse (ERW). Tests warehouse/connectors/eia_intl_bulk.py's coal and energy-and-CO2 tables on a bulk
file built here in EIA's form (figures made up for the test, not EIA's): thousand short tons and million short tons as
short tons, quadrillion Btu as TBtu, million tonnes of CO2 as tCO2, other products in the same units passed over; the
sector rules and the holds. No network.

    python -m unittest tests.test_session937 -v
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
    ser("INTL.7-1-POL-TST.A", "Coal production, Poland, Annual", [["2024", 100000], ["2023", "NA"]]),
    ser("INTL.7-6-POL-MST.A", "Coal reserves, Poland, Annual", [["2021", 30000]]),
    ser("INTL.7-1-POL-QBTU.A", "Coal production, Poland, Annual", [["2024", 2.0]]),
    ser("INTL.44-2-POL-QBTU.A", "Total energy consumption, Poland, Annual", [["2024", 4.1]]),
    ser("INTL.4008-8-POL-MMTCD.A", "CO2 emissions, Poland, Annual", [["2024", 280]]),
    ser("INTL.26-1-POL-QBTU.A", "Dry natural gas production, Poland, Annual", [["2024", 0.2]]),
]


class CoalEnergy(unittest.TestCase):
    def test_units_and_passes(self):
        c, nc = E.rows(E.read_series(bulk(SERIES)), "u", "r", "v", E.COAL)
        g = c.set_index(["entity", "variable"])
        self.assertEqual((nc, g.loc[("eia_intl:POL:7", "production"), "value"], g.loc[("eia_intl:POL:7", "production"), "unit"]), (2, 1e8, "short_ton"))
        self.assertEqual(g.loc[("eia_intl:POL:7", "reserves"), "value"], 3e10)
        e, ne = E.rows(E.read_series(bulk(SERIES)), "u", "r", "v", E.ENERGY)
        h = e.set_index(["entity", "variable"])
        self.assertEqual(ne, 2)
        self.assertEqual((h.loc[("eia_intl:POL:44", "consumption"), "value"], h.loc[("eia_intl:POL:44", "consumption"), "unit"]), (4100.0, "TBtu"))
        self.assertEqual((h.loc[("eia_intl:POL:4008", "emissions"), "value"], h.loc[("eia_intl:POL:4008", "emissions"), "unit"]), (2.8e8, "tCO2"))


class Registered(unittest.TestCase):
    def test_sectors_and_holds(self):
        for name, sector in (("eia_world_coal_annual", "coal"), ("eia_world_energy_co2_annual", "carbon")):
            self.assertEqual(B.sector_of(name), sector)
            self.assertIn(name, R.STORAGE_HELD)
            with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
                self.assertIn(f"  - {name}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
