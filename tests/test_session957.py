"""Session 957: EIA's Annual Coal Distribution Report.

Energy Research Warehouse (ERW). Tests warehouse/connectors/eia_coal_distribution.py on workbooks built here in EIA's
form (figures made up for the test, not EIA's): the flow's entity, quarter and geo, the U.S. rows' geo; the page's
latest workbooks found; two workbooks that disagree, a heading not as read and a destination not in the map stopping
the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session957 -v
"""

import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia_coal_distribution as C  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}
FLOWS = [(2024, 3, "Wyoming", "Texas", "Electric Power Sector", "Railroad", 1000),
         (2024, 3, "Kentucky (East)", "Alabama", "Coke Plant", "River", 50),
         (2024, 3, "U.S. (All States)", "U.S. (All States)", "Electric Power Sector", "Railroad", 1050)]


def books(flows=FLOWS, dest=None):
    o = pd.DataFrame(flows, columns=C.O_HEAD)
    d = pd.DataFrame([(y, q, de, og, c, m, v) for y, q, og, de, c, m, v in (dest or flows)], columns=C.D_HEAD)
    return o, d


class Build(unittest.TestCase):
    def test_rows(self):
        t = C.build(*books(), BASE).set_index("entity")
        a = t.loc["eia_coal_flow:wyoming:texas:electric_power_sector:railroad"]
        self.assertEqual((a.ts_utc, a.freq, a.geo, a.unit, a.value), ("2024-07-01T00:00:00Z", "P3M", "US-TX", "short_ton", 1000.0))
        self.assertEqual(t.loc["eia_coal_flow:u_s_all_states:u_s_all_states:electric_power_sector:railroad"].geo, "US")
        self.assertIn("eia_coal_flow:kentucky_east:alabama:coke_plant:river", t.index)

    def test_workbooks(self):
        page = '<a href="xls/o_23state.xlsx"></a><a href="xls/o_24state.xlsx"></a><a href="xls/d_24state.xlsx"></a>'
        self.assertEqual(C.workbooks(page), (C.PAGE + "xls/o_24state.xlsx", C.PAGE + "xls/d_24state.xlsx"))

    def test_stops(self):
        with self.assertRaises(RuntimeError):
            C.build(*books(dest=FLOWS[:2]), BASE)
        o, d = books()
        with self.assertRaises(RuntimeError):
            C.build(o.rename(columns={"Quarter": "Qtr"}), d, BASE)
        with self.assertRaises(RuntimeError):
            C.build(*books([(2024, 1, "Utah", "Ontario", "Coke Plant", "Railroad", 5)]), BASE)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(C.NAME), "coal")
        self.assertIn(C.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {C.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
