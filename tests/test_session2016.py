"""Session 2016: EIA's Manufacturing Energy Consumption Survey (MECS).

Energy Research Warehouse (ERW). Tests warehouse/connectors/eia_mecs.py on a sheet built here in EIA's form (figures
made up for the test, not EIA's): an industry's and the total's rows by region, million kWh to MWh, a code ("*", "Q")
counted with no row, a revised mark kept; text where a figure belongs, an industry twice in a region, an industry before
any region and a missing column stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2016 -v
"""

import io
import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia_mecs as M  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}
N = None


def sheet(body, head=("Purchases", "Transfers  inb", "Total onsite generationc", "Sales and transfers offsite", "Net demand for electricityd")):
    rows = [["Released: August 2025", N, N, N, N, N, N, N], [N] * 8, ["Table 11.1  Electricity: components of net demand, 2022", N, N, N, N, N, N, N],
            [N] * 8, [N, N, N, N, N, N, N, N], ["NAICS", " ", N, N, N, N, N, N],
            ["codea", "Subsector and industry"] + list(head) + [N] * (6 - len(head)), [N] * 8]
    b = io.BytesIO()
    pd.DataFrame(rows + body).to_excel(b, index=False, header=False)
    return b.getvalue()


US = [N, N, "Total United States", N, N, N, N, N]
WEST = [N, N, "West Census Region", N, N, N, N, N]


class Parse(unittest.TestCase):
    def test_rows(self):
        counts = {}
        rows = M.parse(sheet([US, ["311", "Food", 100, "*", 7, "Q", 107, "h"], [N, "Total", 200, 1, 9, 2, 208, N],
                              WEST, ["311", "Food", 10, 0, 1, 0, 11, N]]), "Table 11.1", BASE, counts)
        got = {(r["entity"], r["variable"]): r for r in rows}
        self.assertEqual(counts, {"*": 1, "Q": 1})
        p = got[("mecs:us_311", "elec_purchases")]
        self.assertEqual((p["value"], p["unit"], p["geo"], p["x_naics"], p["node"]), (100000.0, "MWh", "US", "311", "Food"))
        self.assertEqual(got[("mecs:us_311", "elec_net_demand")]["x_mark"], "h")
        self.assertNotIn(("mecs:us_311", "elec_transfers_in"), got)
        self.assertEqual(got[("mecs:us_total", "elec_onsite_generation")]["node"], "All manufacturing")
        w = got[("mecs:west_311", "elec_net_demand")]
        self.assertEqual((w["geo"], w["x_region"], w["value"]), ("", "West Census Region", 11000.0))

    def test_stops(self):
        for body in ([US, ["311", "Food", "n/a", 0, 1, 0, 1, N]],
                     [US, ["311", "Food", 1, 0, 1, 0, 1, N], ["311", "Food", 1, 0, 1, 0, 1, N]],
                     [["311", "Food", 1, 0, 1, 0, 1, N]],
                     [US, ["Note: totals", N, N, N, N, N, N, N]]):
            with self.assertRaises(RuntimeError):
                M.parse(sheet(body), "Table 11.1", BASE, {})
        with self.assertRaises(RuntimeError):
            M.parse(sheet([US], head=("Purchases", "Transfers  inb")), "Table 11.1", BASE, {})


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(M.TABLE), "power;gas;oil;coal")
        self.assertIn(M.TABLE, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {M.TABLE}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
