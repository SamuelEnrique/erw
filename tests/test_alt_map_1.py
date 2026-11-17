"""Ruling alternative 1 of /map (session 7721, 17 November 2026, branch wip/alt-map-1; not a default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-map-2026-11-17.md, line 1): the Projects tab
draws queue positions and datacenters with names and MW from its own copy of two held tables; hold the map's copy too?
On this branch the builder (warehouse/derived/project_map.py) holds its copy exactly as site/data/license_status.json holds
the tables: energy_projects is held by grid (ISO-NE), so ISO-NE's queue rows are counted and not written (QUEUE_HELD, and
site/lib/resources.ts QUEUE_GRIDS); datacenter_facilities is held whole, so its layer is counted and not written (DC_HELD,
the file's held_layers). No hold is lifted: more is held. Pinned with the builder's own page_rows on rows made up here
and, where the tables are on the machine (warehouse/output, or the folder ERW_TABLES_DIR names), on them: the queue layer
3,737 positions (762,725.3 MW) to 3,315 (739,052.7 MW; ISO-NE's 422 held), the datacenter layer 278 (28,254.0 MW) to 0;
the operating and planned units do not move.

    python -m unittest tests.test_alt_map_1 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import project_map as pm  # noqa: E402

TABLES = os.environ.get("ERW_TABLES_DIR") or os.path.join(ROOT, "warehouse", "output")
NEED = ("energy_projects", "datacenter_facilities", "eia860m_operating_generators", "eia860m_planned_generators")


class TheRule(unittest.TestCase):
    def test_the_lists(self):
        self.assertEqual(set(pm.QUEUE_SHOWN), {"ercot", "spp", "caiso"})
        self.assertEqual(pm.QUEUE_HELD["isone"], ("ISO-NE", "license needed"))
        self.assertEqual(pm.DC_HELD, ("Datacenters", "license needed"))

    def test_the_site_list_agrees(self):
        with open(os.path.join(ROOT, "site", "lib", "resources.ts"), encoding="utf-8") as f:
            s = f.read()
        self.assertIn('{ id: "isone", label: "ISO-NE", shown: false, words: "license needed",', s)


@unittest.skipUnless(all(os.path.exists(os.path.join(TABLES, f"{t}.csv")) for t in NEED), "the map's tables are not on this machine")
class OnTheLocalTables(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows, cls.held, cls.without_state, cls.dc_held = pm.page_rows(TABLES)

    def layer(self, kind):
        m = self.rows["kind"] == kind
        return int(m.sum()), round(float(self.rows.loc[m, "mw"].sum()), 1)

    def test_the_held_layers(self):
        self.assertEqual(self.layer("queue"), (3315, 739052.7))
        self.assertEqual(self.layer("datacenter"), (0, 0.0))
        self.assertEqual(self.dc_held, 278)
        self.assertEqual({h["grid"]: h["rows"] for h in self.held}["isone"], 422)

    def test_the_units_do_not_move(self):
        self.assertEqual(self.layer("operating"), (28712, 1423491.7))
        self.assertEqual(self.layer("planned"), (2361, 290264.2))


if __name__ == "__main__":
    unittest.main()
