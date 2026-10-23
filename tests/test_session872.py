"""Session 872: ERCOT's CDR unit details, as ercot_cdr_units.

Energy Research Warehouse (ERW). Tests warehouse/connectors/ercot_cdr_units.py on a Unit Details sheet built here in the
report's layout (units made up for the test, not ERCOT's): the key (unit code, else INR, else name, with the fuel), the
status mapped to the data standard's words with ERCOT's code kept, the seasonal capabilities, a heading not in the map,
the sector rule and the holds. No network.

    python -m unittest tests.test_session872 -v
"""

import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import ercot_cdr_units as U  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

N = float("nan")
TOP = ["NOTES"] + [N] * 10 + ["HIGH-RISK SEASON", N, "HIGH-RISK SEASON", N]
MID = [N] * 11 + ["Summer Capabilities, MW", N, "Winter Capabilities, MW", N]
HEAD = ["UNIT NAME", "INTERCONNECTION REQUEST  NUMBER (INR)", "UNIT CODE", "TECHNOLOGY", "FUEL", "CDR STATUS",
        "CDR RESOURCE ATTRIBUTE", "COUNTY", "ZONE", "IN-SERVICE\nDATE", "INSTALLED CAPACITY\n(MW)", 2026, 2027.0, "2026/2027", "2027/2028"]


def row(name, inr, code, fuel, status):
    return [name, inr, code, "ST", fuel, status, "CONV", "ECTOR", "WEST", pd.Timestamp("2020-01-01"), 100, 95, 95.0, 98, 98]


class Units(unittest.TestCase):
    def test_keys_status_capabilities(self):
        f = pd.DataFrame([TOP, MID, HEAD, row("A U1", N, "A_U1", "GAS", "OPER"), row("B NEW", "26INR0001", N, "SOLAR", "PLAN"),
                          row("C OLD", N, N, "COAL", "MOTH-IND"), row("A U1", N, "A_U1", "COAL", "OPER-UNFC")])
        t, caps = U.units(f, "u", "r", "2025-12-19T00:00:00Z", {})
        t = t.set_index("entity_id")
        self.assertEqual(sorted(t.index), ["ercot_cdr_unit:26INR0001:SOLAR", "ercot_cdr_unit:A_U1:COAL", "ercot_cdr_unit:A_U1:GAS", "ercot_cdr_unit:C_OLD:COAL"])
        self.assertEqual((t.loc["ercot_cdr_unit:A_U1:GAS", "status"], t.loc["ercot_cdr_unit:A_U1:COAL", "x_cdr_status"]), ("operating", "OPER-UNFC"))
        self.assertEqual((t.loc["ercot_cdr_unit:26INR0001:SOLAR", "status"], t.loc["ercot_cdr_unit:C_OLD:COAL", "status"]), ("planned", "suspended"))
        self.assertEqual(caps, ["x_summer_2026", "x_summer_2027", "x_winter_2026_2027", "x_winter_2027_2028"])
        self.assertEqual(t.loc["ercot_cdr_unit:A_U1:GAS", "status_date"], "2020-01-01")

    def test_a_heading_not_in_the_map_stops(self):
        h = list(HEAD)
        h[7] = "PARISH"
        with self.assertRaises(RuntimeError):
            U.units(pd.DataFrame([TOP, MID, h, row("A", N, "A", "GAS", "OPER")]), "u", "r", "v", {})


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of("ercot_cdr_units"), "power")
        self.assertIn("ercot_cdr_units", R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn("  - ercot_cdr_units", f.read())


if __name__ == "__main__":
    unittest.main()
