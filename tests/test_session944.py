"""Session 944: Berkeley Lab's wind plants' 2025 capacity factors.

Energy Research Warehouse (ERW). Tests warehouse/connectors/lbnl_wind_capacity_factors.py on a sheet built here in the
data file's form (figures made up for the test, not LBNL's): the plant code, value, COD and repower kept, a plant
without a value left out; a heading not as read and a plant given twice stopping the run; the sector rule and the
holds. No network.

    python -m unittest tests.test_session944 -v
"""

import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import lbnl_wind_capacity_factors as W  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402


def sheet(data):
    head = [[None] * 15 for _ in range(4)]
    head[1][10], head[1][11], head[1][12] = "2025", "Project", "EIA Plant"
    head[2][10] = "Capacity"
    head[3][10], head[3][11], head[3][12], head[3][13], head[3][14] = "Factor", "COD", "Code", "Repower", "COD Code"
    body = []
    for cf, cod, code, rep in data:
        r = [None] * 15
        r[10], r[11], r[12], r[13] = cf, cod, code, rep
        body.append(r)
    return pd.DataFrame(head + body)


class Rows(unittest.TestCase):
    def test_shape(self):
        out = W.rows(sheet([(0.41, 2012.0, 56789.0, "partial repower"), (0.30, "1998-99", 123, None), (None, 2020, 999, None)]), {"source": "s"})
        t = pd.DataFrame(out).set_index("entity")
        self.assertEqual(len(t), 2)
        a = t.loc["lbnl_wind:56789"]
        self.assertEqual((a.value, a.x_cod, a.x_repower, a.node, a.unit, a.freq), (0.41, "2012", "partial repower", "EIA plant 56789", "ratio", "P1Y"))
        self.assertEqual(t.loc["lbnl_wind:123"].x_cod, "1998-99")

    def test_stops(self):
        bad = sheet([(0.4, 2012, 1, None)])
        bad.iloc[3, 11] = "Year"
        with self.assertRaises(RuntimeError):
            W.rows(bad, {})
        with self.assertRaises(RuntimeError):
            W.rows(sheet([(0.4, 2012, 1, None), (0.3, 2013, 1, None)]), {})


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        name = "lbnl_wind_capacity_factors"
        self.assertEqual(B.sector_of(name), "power")
        self.assertIn(name, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {name}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
