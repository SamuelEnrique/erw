"""Session 867: EIA-861's utility data (NERC region, RTOs, activities), as eia861_utility_data.

Energy Research Warehouse (ERW). Tests warehouse/connectors/eia861_utility_data.py on a sheet built here in EIA's layout
(utilities made up for the test): the two columns named SPP told apart by their group heading, the flags kept as EIA
gives them, EIA's aggregates left out, a row with no state, the sector rule and the holds. No network.

    python -m unittest tests.test_session867 -v
"""

import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia861_utility_data as U  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

N = float("nan")
TOP = (["Utility Characteristics", N, N, N, N, N, "Also operating in other NERC Regions"] + [N] * 7
       + ["Operating in these RTOs"] + [N] * 7 + ["Other Activities"] + [N] * 9)
HEAD = (["Data Year", "Utility Number", "Utility Name", "State", "Ownership Type", "NERC Region",
         "TRE", "FRCC", "MRO", "NPCC", "RFC", "SERC", "SPP", "WECC",
         "CAISO", "ERCOT", "PJM", "NYISO", "SPP", "MISO", "ISONE", "Other",
         "Generation", "Transmission", "Buying Transmission", "Distribution", "Buying Distribution",
         "Wholesale Marketing", "Retail Marketing", "Bundled", "Alt Fuel Vehicle", "Alt Fuel Vehicle 2"])


def row(util, state, nerc_spp=N, rto_spp=N, ercot=N):
    r = [2025, util, f"Utility {util}", state, "Cooperative", "SPP"] + [N] * 26
    r[HEAD.index("SPP")] = nerc_spp
    r[len(HEAD) - 1 - HEAD[::-1].index("SPP")] = rto_spp
    r[HEAD.index("ERCOT")] = ercot
    return r


class TheSheet(unittest.TestCase):
    def test_flags_and_rows(self):
        f = pd.DataFrame([TOP, HEAD, row(1, "OK", nerc_spp="N", rto_spp="Y"), row(2, "TX", ercot="Y"), row(88888, "TX"), row(3, N)])
        t = U.sheet_rows(f, 2025, "u", "r").set_index("x_utility_number")
        self.assertEqual(sorted(t.index), ["1", "2", "3"])                    # 88888 left out
        self.assertEqual((t.loc["1", "x_nerc_spp"], t.loc["1", "x_rto_spp"], t.loc["1", "x_rtos"]), ("N", "Y", "SPP"))
        self.assertEqual((t.loc["2", "x_rto_ercot"], t.loc["2", "x_rtos"], t.loc["2", "geo"]), ("Y", "ERCOT", "US-TX"))
        self.assertEqual((t.loc["3", "geo"], t.loc["3", "entity_id"]), ("US", "eia861_utility:3::2025"))

    def test_a_missing_heading_stops(self):
        h = list(HEAD)
        h[HEAD.index("MISO")] = "Midcontinent"
        with self.assertRaises(RuntimeError):
            U.sheet_rows(pd.DataFrame([TOP, h, row(1, "OK")]), 2025, "u", "r")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of("eia861_utility_data"), "power")
        self.assertIn("eia861_utility_data", R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn("  - eia861_utility_data", f.read())


if __name__ == "__main__":
    unittest.main()
