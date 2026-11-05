"""Session 695: EIA-861's distribution reliability by utility (SAIDI, SAIFI, CAIDI), and the units of Decision 51.

Energy Research Warehouse (ERW). Tests warehouse/connectors/eia861_reliability.py on sheets built here in EIA's two
layouts (2015 to 2020, events in the heading; 2021 on, events in a heading row of their own), with figures made up for
the test, not EIA's; the units, the sector rule and the holds. No network.

    python -m unittest tests.test_session695 -v
"""

import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
sys.path.append(os.path.join(ROOT, "warehouse", "validate"))  # last: its build_coverage.py is a shim
import eia861_reliability as E  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402
import erw_validate as V  # noqa: E402

N = float("nan")
OLD_TOP = ["Utility Characteristics", N, N, N, N, "IEEE Standard"] + [N] * 11 + ["Other Standard"] + [N] * 10
OLD_LOW = (["Data Year", "Utility Number", "Utility Name", "State", "Ownership"]
           + ["SAIDI With MED", "SAIFI With MED", "CAIDI With MED", "SAIDI Without MED", "SAIFI Without MED", "CAIDI Without MED",
              "SAIDI With MED Minus LOS", "SAIFI With MED Minus LOS", "CAIDI Minus MED", "Number of Customers",
              "Highest Dist. Voltage", "Outages Recorded Automatically"]
           + ["SAIDI With MED", "SAIFI With MED", "CAIDI With MED", "SAIDI Without MED", "SAIFI Without MED", "CAIDI Without MED",
              "Number of Customers", "Inactive Accounts Included", "Momentary Interruptions", "Highest Dist. Voltage",
              "Outages Recorded Automatically"])
IDX = ["SAIDI (minutes per year)", "SAIFI (times per year)", "CAIDI (minutes per interruption)"]
NEW_TOP = OLD_TOP
NEW_MID = ([N] * 5 + ["All Events (With Major Event Days)", N, N, "Without Major Event Days", N, N,
                      "Loss of Supply Removed (With Major Event Days)", N, N, ".", N, N]
           + ["All Events (With Major Event Days)", N, N, "Without Major Event Days", N, N, ".", N, N, N, N])
NEW_LOW = (["Data Year", "Utility Number", "Utility Name", "State", "Ownership"] + IDX * 3
           + ["Number of Customers", "Highest Dist. Voltage", "Outages Recorded Automatically"]
           + IDX[:2] + ["CAIDI With MED"] + IDX[:2] + ["CAIDI Without MED"]
           + ["Number of Customers", "Inactive Accounts Included", "Momentary Interruptions", "Highest Dist. Voltage", "Outages Recorded Automatically"])
FIGS = [100.0, 1.0, 100.0, 60.0, 0.8, 75.0, 90.0, 0.9, 100.0, 5000, 12.5, "Y", ".", ".", ".", ".", ".", ".", ".", N, N, ".", N]


def row(year, util=97, state="IL"):
    return [year, util, "A Test Coop", state, "Cooperative"] + FIGS


class TheTwoLayouts(unittest.TestCase):
    def check(self, t):
        g = t.set_index("variable")
        self.assertEqual(g.loc["ieee_saidi_with_med", "value"], 100.0)
        self.assertEqual(g.loc["ieee_saidi_with_med", "unit"], "minute/customer")
        self.assertEqual(g.loc["ieee_saifi_without_med", "unit"], "interruption/customer")
        self.assertEqual(g.loc["ieee_caidi_minus_los", "value"], 100.0)
        self.assertEqual(g.loc["ieee_caidi_minus_los", "unit"], "minute/interruption")
        self.assertEqual(g.loc["ieee_customers", "unit"], "count")
        self.assertEqual(len(t), 10)                 # nine IEEE figures and the customers; the other standard is all "."
        self.assertFalse(any(v.startswith("other_") for v in t.variable))
        self.assertEqual((t.entity.iloc[0], t.geo.iloc[0], t.x_ieee_auto_recorded.iloc[0], t.x_ieee_highest_voltage_kv.iloc[0]),
                         ("eia861_reliability:97:IL", "US-IL", "Y", "12.5"))

    def test_2015_to_2020(self):
        self.check(E.sheet_rows(pd.DataFrame([OLD_TOP, OLD_LOW, row(2018)]), 2018, "u", "r"))

    def test_2021_on(self):
        self.check(E.sheet_rows(pd.DataFrame([NEW_TOP, NEW_MID, NEW_LOW, row(2024)]), 2024, "u", "r"))

    def test_a_missing_figure_stops_and_a_key_twice_stops(self):
        low = list(OLD_LOW)
        low[13] = "Something Else"
        with self.assertRaises(RuntimeError):
            E.sheet_rows(pd.DataFrame([OLD_TOP, low, row(2018)]), 2018, "u", "r")
        with self.assertRaises(RuntimeError):
            E.sheet_rows(pd.DataFrame([OLD_TOP, OLD_LOW, row(2018), row(2018)]), 2018, "u", "r")


class Registered(unittest.TestCase):
    def test_units_sector_holds(self):
        for u in ("minute/customer", "interruption/customer", "minute/interruption"):
            self.assertIn(u, V.UNITS)
        self.assertEqual(B.sector_of("eia861_utility_reliability"), "power")
        self.assertIn("eia861_utility_reliability", R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn("  - eia861_utility_reliability", f.read())


if __name__ == "__main__":
    unittest.main()
