"""Session 2951 (chain 157): generator_pipeline_by_grid, EIA-860M's planned generators by grid each snapshot month and
the moves between two months. The builder is run on two small snapshots written here: every move is the one its
definition names, the cells sum to the snapshot, and the datacenter tag reads a plant's or an owner's name.
No request, no model call."""
import importlib.util
import os
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def load():
    spec = importlib.util.spec_from_file_location("gp_2951", os.path.join(ROOT, "warehouse", "derived", "generator_pipeline_by_grid.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def frame(rows):
    return pd.DataFrame(rows, columns=["key", "ba", "state", "fuel", "status", "year", "mw", "tag"])


BEFORE = frame([("1:A", "ERCO", "TX", "SUN", "U", "2026", 100.0, False),    # comes online
                ("2:A", "ERCO", "TX", "WND", "P", "2027", 50.0, False),     # leaves
                ("3:A", "PJM", "VA", "MWH", "P", "2026", 20.0, False),      # slips to 2027
                ("4:A", "PJM", "VA", "NG", "P", "2028", 300.0, False)])     # moves status P to T
NOW = frame([("3:A", "PJM", "VA", "MWH", "P", "2027", 20.0, False),
             ("4:A", "PJM", "VA", "NG", "T", "2028", 300.0, False),
             ("5:A", "ERCO", "TX", "SUN", "P", "2028", 75.0, True)])        # enters, a datacenter's


class TheMoves(unittest.TestCase):
    def test_each_move(self):
        m = load()
        mv = m.moves(BEFORE, set(), NOW, {"1:A"})
        self.assertEqual({k: sorted(v.index) for k, v in mv.items()},
                         {"entered": ["5:A"], "online": ["1:A"], "left": ["2:A"], "status_moved": ["4:A"], "slipped": ["3:A"]})

    def test_a_generator_operating_before_is_not_entered(self):
        m = load()
        self.assertEqual(list(m.moves(BEFORE, {"5:A"}, NOW, {"1:A"})["entered"].index), [])

    def test_the_cells_and_the_tag(self):
        m = load()
        rows = pd.DataFrame(m.cells(NOW, "2026-09", "https://www.eia.gov/electricity/data/eia860m/"))
        mw = rows[rows["variable"] == "planned_mw"]
        self.assertAlmostEqual(mw["value"].sum(), 395.0)
        dc = rows[(rows["variable"] == "datacenter_mw") & (rows["value"] > 0)]
        self.assertEqual(list(dc["entity"]), ["eia860m_pipeline:ERCO:TX:SUN:P:2028"])
        self.assertTrue(m.DATACENTER.search("Abilene Data Center Solar"))
        self.assertTrue(m.DATACENTER.search("Argonne National Laboratory"))
        self.assertFalse(m.DATACENTER.search("Labette County Wind"))

    def test_the_workbook_month(self):
        m = load()
        self.assertEqual(m.workbook_vintage("20261006T092042.298821Z_00004_august_generator2026.xlsx"), "2026-08")


if __name__ == "__main__":
    unittest.main()
