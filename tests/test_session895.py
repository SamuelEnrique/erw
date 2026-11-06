"""Session 895: EIA-411's peak load, capacity resources and margins by NERC assessment area.

Energy Research Warehouse (ERW). Tests warehouse/connectors/eia411.py on sheets built here in the workbooks' form
(figures made up for the test, not EIA's): each block found by its heading and years, a block's rows stopping at the next
heading, a winter season's years split over two rows, the projected (E) years marked, the measures as variables with
their units, a measure not in the map stopping the run, the sector rule and the holds. No network.

    python -m unittest tests.test_session895 -v
"""

import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia411 as E  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

N = float("nan")


def peak_sheet():
    head = ["Interconnection", "NERC Regional Assesment Area"]
    return pd.DataFrame([
        ["Table 2. Noncoincident peak load", N, N, N, N],
        head + ["Summer", N, N],
        [N, N, "Actual", N, "Projected"],
        [N, N, 2015, 2016, "2017E"],
        ["ERCOT", "TRE", 69000, 71000, 72000],
        ["All Interconnections", "Contiguous U.S. ", 700000, 710000, "NA"],
        head + ["Winter", N, N],
        [N, N, "Actual", N, "Projected"],
        [N, N, "2015/", "2016/", "2017/"],
        [N, N, "2016", "2017", "2018E"],
        ["ERCOT", "TRE", 59000, 61000, 62000],
        ["Notes: something", N, N, N, N],
    ])


def capacity_sheet():
    head = ["Interconnection", "NERC Regional Assesment Area"]
    return pd.DataFrame([
        head + ["Net Internal Demand (MW)[1]", N, N],
        [N, N, "Actual", N, "Projected"],
        [N, N, 2015.0, 2016.0, "2017E"],
        ["ERCOT", "TRE", 68000, 70000, 71000],
        head + ["Capacity Resources (MW)[2]", N, N],
        [N, N, "Actual", N, "Projected"],
        [N, N, 2015.0, 2016.0, "2017E"],
        ["ERCOT", "TRE", 80000, 80000, 90000],
        head + ["Capacity Margin (percent)[3]", N, N],
        [N, N, "Actual", N, "Projected"],
        [N, N, 2015.0, 2016.0, "2017E"],
        ["ERCOT", "TRE", 15.0, 12.5, 26.8],
    ])


class EIA411(unittest.TestCase):
    def test_peak_blocks_and_seasons(self):
        t = pd.DataFrame(E.sheet_rows(peak_sheet(), "summer", "u", "r")).set_index(["entity", "variable", "ts_utc"])
        self.assertEqual(t.loc[("eia411:tre", "summer_peak_load", "2017-06-01T00:00:00Z"), "x_projected"], "projected")
        self.assertEqual(t.loc[("eia411:tre", "summer_peak_load", "2016-06-01T00:00:00Z"), "value"], 71000.0)
        self.assertEqual(t.loc[("eia411:tre", "winter_peak_load", "2015-10-01T00:00:00Z"), "value"], 59000.0)
        self.assertEqual(t.loc[("eia411:contiguous_u_s", "summer_peak_load", "2015-06-01T00:00:00Z"), "node"], "Contiguous U.S. (All Interconnections)")
        self.assertNotIn(("eia411:contiguous_u_s", "summer_peak_load", "2017-06-01T00:00:00Z"), t.index)   # NA has no row
        self.assertEqual(len(t), 8)

    def test_capacity_blocks_and_units(self):
        t = pd.DataFrame(E.sheet_rows(capacity_sheet(), "winter", "u", "r"))
        g = t.set_index(["variable", "ts_utc"])
        self.assertEqual(sorted(t.variable.unique()), ["winter_capacity_margin", "winter_capacity_resources", "winter_net_internal_demand"])
        self.assertEqual(g.loc[("winter_capacity_margin", "2016-10-01T00:00:00Z"), "unit"], "pct")
        self.assertEqual(g.loc[("winter_capacity_resources", "2017-10-01T00:00:00Z"), "value"], 90000.0)

    def test_a_measure_not_in_the_map_stops(self):
        s = capacity_sheet()
        s.iloc[4, 2] = "Something Else"
        with self.assertRaises(RuntimeError):
            E.sheet_rows(s, "summer", "u", "r")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        name = "eia411_capacity_margins_annual"
        self.assertEqual(B.sector_of(name), "power")
        self.assertIn(name, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {name}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
