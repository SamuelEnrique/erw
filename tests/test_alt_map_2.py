"""Ruling alternative 2 of /map (session 7721, 17 November 2026, branch wip/alt-map-2; not a default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-map-2026-11-17.md, line 2): match planned units
and queue positions by name and county, so a project that is both counts once? On this branch the builder
(warehouse/derived/project_map.py page_rows, match_name) leaves out of the queue layer a position whose name, without words
such as Solar, BESS, LLC, and county match a planned unit's; it is counted once, under the planned unit, and the file
counts the matched rows and MW. Pinned with the builder's own functions on rows made up here and, where the tables are on
the machine (warehouse/output, or the folder ERW_TABLES_DIR names), on them: 163 queue positions match, 31,574.5 MW; the
queue layer 3,737 positions (762,725.3 MW) to 3,574 (731,150.8 MW, -4.1 percent of its MW); the planned layer does not
move. Among them the three near Abilene the rulings line names (Funston, Tiger, Chimney Rock). The impact file, on the
committed file of 16 November: 154 positions, 30,170.5 MW (3.93 percent).

    python -m unittest tests.test_alt_map_2 -v
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


class TheName(unittest.TestCase):
    def test_the_words_left_out(self):
        self.assertEqual(pm.match_name("Funston Solar, LLC"), "FUNSTON")
        self.assertEqual(pm.match_name("Chimney Rock BESS"), "CHIMNEY ROCK")
        self.assertEqual(pm.match_name("Tiger Solar Project Phase II"), "TIGER")
        self.assertEqual(pm.match_name("Solar Energy LLC"), "")


@unittest.skipUnless(all(os.path.exists(os.path.join(TABLES, f"{t}.csv")) for t in NEED), "the map's tables are not on this machine")
class OnTheLocalTables(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows, cls.held, cls.without_state, cls.matched = pm.page_rows(TABLES)

    def layer(self, kind):
        m = self.rows["kind"] == kind
        return int(m.sum()), round(float(self.rows.loc[m, "mw"].sum()), 1)

    def test_the_match(self):
        self.assertEqual(self.matched, {"rows": 163, "mw": 31574.5})
        self.assertEqual(self.layer("queue"), (3574, 731150.8))
        self.assertEqual(self.layer("planned"), (2361, 290264.2))

    def test_the_three_near_abilene_count_once(self):
        q = self.rows[self.rows["kind"] == "queue"]
        p = self.rows[self.rows["kind"] == "planned"]
        for name in ("FUNSTON", "TIGER", "CHIMNEY ROCK"):
            self.assertFalse(any(pm.match_name(n) == name for n in q["name"]), name)
            self.assertTrue(any(pm.match_name(n) == name for n in p["name"]), name)


if __name__ == "__main__":
    unittest.main()
