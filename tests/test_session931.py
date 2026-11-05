"""Session 931: the planned generation in a placed ERCOT node's county (a derived table).

Energy Research Warehouse (ERW). Tests warehouse/derived/ercot_node_planned_generation.py on rows built here in the input
tables' form (figures made up for the test): active queue projects only, the kinds from the fuel and technology, EIA-860M's
Texas generators only, zeros for a county with none, the earliest in-service date; a technology group not in the map
stopping the run; the sector rule, the holds and the method note. No network.

    python -m unittest tests.test_session931 -v
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
import ercot_node_planned_generation as P  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

NODES = pd.DataFrame([{"entity_id": "ercot_node:A_1", "name": "A_1", "x_county": "Pecos", "x_zone": "WEST"},
                      {"entity_id": "ercot_node:B_1", "name": "B_1", "x_county": "Oldham", "x_zone": "PANHANDLE"}])
QUEUE = pd.DataFrame([{"status": "active", "county": "Pecos", "capacity_mw": "100", "fuel_technology": "Solar - Photovoltaic Solar", "proposed_in_service_date": "2027-06-01"},
                      {"status": "active", "county": "PECOS ", "capacity_mw": "50", "fuel_technology": "Other - Battery Energy Storage", "proposed_in_service_date": "2026-12-01"},
                      {"status": "active", "county": "Pecos", "capacity_mw": "20", "fuel_technology": "Hydrogen - Other", "proposed_in_service_date": ""},
                      {"status": "completed", "county": "Pecos", "capacity_mw": "999", "fuel_technology": "Wind - Wind Turbine", "proposed_in_service_date": ""}])
EIA = pd.DataFrame([{"state": "TX", "county": "Pecos", "nameplate_mw": "75", "technology_group": "natural_gas"},
                    {"state": "NM", "county": "Pecos", "nameplate_mw": "500", "technology_group": "solar"}])


class Join(unittest.TestCase):
    def test_counts(self):
        t, c = P.build(NODES, QUEUE, EIA, "r")
        a = t.set_index("entity_id").loc["ercot_node:A_1"]
        self.assertEqual((a.x_queue_projects, a.x_queue_mw, a.x_queue_solar_mw, a.x_queue_storage_mw, a.x_queue_other_mw, a.x_queue_wind_mw),
                         (3, 170.0, 100.0, 50.0, 20.0, 0.0))
        self.assertEqual(a.x_queue_next_in_service, "2026-12-01")
        self.assertEqual((a.x_eia_planned_generators, a.x_eia_planned_mw, a.x_eia_natural_gas_mw, a.x_eia_solar_mw), (1, 75.0, 75.0, 0.0))
        b = t.set_index("entity_id").loc["ercot_node:B_1"]
        self.assertEqual((b.x_queue_projects, b.x_queue_mw, b.x_eia_planned_mw, b.x_queue_next_in_service), (0, 0.0, 0.0, ""))
        self.assertEqual(c["counties_without_queue"], 1)

    def test_unknown_group_stops(self):
        with self.assertRaises(RuntimeError):
            P.build(NODES, QUEUE, pd.DataFrame([{"state": "TX", "county": "Pecos", "nameplate_mw": "1", "technology_group": "fusion"}]), "r")


class Registered(unittest.TestCase):
    def test_sector_holds_and_note(self):
        name = "ercot_node_planned_generation"
        self.assertEqual(B.sector_of(name), "power")
        self.assertIn(name, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {name}\n", f.read().replace("\r\n", "\n"))
        self.assertTrue(os.path.exists(os.path.join(ROOT, "docs", "methods", f"{name}.md")))


if __name__ == "__main__":
    unittest.main()
