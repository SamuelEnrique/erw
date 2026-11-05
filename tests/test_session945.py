"""Session 945: the wires utilities in an ERCOT node's county.

Energy Research Warehouse (ERW). Tests warehouse/derived/ercot_node_wires_utilities.py on rows built here in the input
tables' form (made up for the test, not EIA's): a county's utilities listed, its delivery-only companies and those
outside Texas RE named apart; a county in no territory stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session945 -v
"""

import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import ercot_node_wires_utilities as W  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402


def inputs(county="Harris"):
    nodes = pd.DataFrame([{"entity_id": "ercot_node:A_RN", "name": "A_RN", "x_county": county, "x_zone": "HOUSTON"}])
    terr = pd.DataFrame([{"name": n, "x_utility_number": u, "x_state": "TX", "x_county": "Harris", "x_short_form": s, "x_data_year": "2025"}
                         for n, u, s in [("CenterPoint", "1", ""), ("Entergy Texas", "2", ""), ("A Coop", "3", "Y")]])
    deliv = pd.DataFrame([{"ts_utc": "2025-01-01T00:00:00Z", "x_utility_number": "1", "x_state": "TX"}])
    u = [{"x_utility_number": n, "x_state": "TX", "x_year": "2025", **{k: "" for k in W.NERC}} for n in ("1", "2")]
    u[0]["x_nerc_tre"], u[1]["x_nerc_serc"] = "Y", "Y"
    return nodes, terr, deliv, pd.DataFrame(u)


class Build(unittest.TestCase):
    def test_shape(self):
        t, c = W.build(*inputs(), "r")
        a = t.iloc[0]
        self.assertEqual((a.x_utilities_n, a.x_delivery_only, a.x_outside_tre, a.x_short_form_n, a.vintage),
                         (3, "CenterPoint (1)", "Entergy Texas (2)", 1, "EIA-861 2025"))
        self.assertEqual(a.x_utilities, "A Coop (3); CenterPoint (1); Entergy Texas (2)")

    def test_stops(self):
        with self.assertRaises(RuntimeError):
            W.build(*inputs("Bexar"), "r")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        name = "ercot_node_wires_utilities"
        self.assertEqual(B.sector_of(name), "power")
        self.assertIn(name, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {name}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
