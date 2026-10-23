"""Session 917: ERCOT's TPIT projects by a resource node's county (a derived table).

Energy Research Warehouse (ERW). Tests warehouse/derived/ercot_node_transmission.py on rows built here in the two input
tables' form (figures made up for the test): a phase counted in its start and end counties, once within one county,
zeros for a county TPIT does not name, the open sums, maximum kV and next date; a status not in the map stopping the run;
the sector rule, the holds and the method note. No network.

    python -m unittest tests.test_session917 -v
"""

import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import ercot_node_transmission as T  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

NODES = pd.DataFrame([{"entity_id": "ercot_node:A_1", "name": "A_1", "x_county": "Pecos", "x_zone": "WEST"},
                      {"entity_id": "ercot_node:B_1", "name": "B_1", "x_county": "Oldham", "x_zone": "PANHANDLE"}])


def phase(eid, status, a, b, kv="345", new="10", up="0", date="2027-06-01", kind="projected", proj="1"):
    return {"event_id": eid, "event_date": date, "status": status, "x_project_number": proj, "x_kv": kv, "x_new_circuit_miles": new,
            "x_upgraded_circuit_miles": up, "x_county_start": a, "x_county_end": b, "x_date_kind": kind}


class Join(unittest.TestCase):
    def test_counts(self):
        tp = pd.DataFrame([phase("p1", "future", "Pecos", "Reeves"), phase("p2", "planned", "PECOS ", "pecos", kv="765", new="5", date="2026-12-01", proj="2"),
                           phase("p3", "completed", "Reeves", "Pecos", date="2024-01-01", kind="actual"), phase("p4", "future", "Ward", "")])
        t, c = T.build(NODES, tp, "r", "ed")
        a = t.set_index("entity_id").loc["ercot_node:A_1"]
        self.assertEqual((a.x_phases_future, a.x_phases_planned, a.x_phases_completed, a.x_phases_cancelled), (1, 1, 1, 0))
        self.assertEqual((a.x_open_projects, a.x_open_new_circuit_miles, a.x_open_max_kv, a.x_open_next_in_service), (2, 15.0, 765, "2026-12-01"))
        b = t.set_index("entity_id").loc["ercot_node:B_1"]
        self.assertEqual((b.x_phases_future, b.x_open_projects, b.x_open_max_kv, b.x_open_next_in_service), (0, 0, "", ""))
        self.assertEqual(c["counties with no phase"], 1)

    def test_unknown_status_stops(self):
        with self.assertRaises(RuntimeError):
            T.build(NODES, pd.DataFrame([phase("p1", "maybe", "Pecos", "")]), "r", "ed")


class Registered(unittest.TestCase):
    def test_sector_holds_and_note(self):
        name = "ercot_node_transmission"
        self.assertEqual(B.sector_of(name), "power")
        self.assertIn(name, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {name}\n", f.read().replace("\r\n", "\n"))
        self.assertTrue(os.path.exists(os.path.join(ROOT, "docs", "methods", f"{name}.md")))


if __name__ == "__main__":
    unittest.main()
