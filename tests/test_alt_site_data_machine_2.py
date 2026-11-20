"""Ruling alternative 2 (a) of the data machine's tables (session 7713, 17 November 2026, branch
wip/alt-site-data-machine-2; not a default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-site-data-machine-2026-11-17.md, line 2):
datacenter_mw in the pipeline table reads 0 everywhere: drop the column, or fill it by joining the tracker by plant ID? On
this branch it is dropped (warehouse/derived/generator_pipeline_by_grid.py cells): a cell carries planned_mw and
planned_count only. In the table on Redivis (snapshots 2026-08 and 2026-09, 5,147 rows) that is 1,671 rows that leave
(-32.5 percent of its rows), every one 0.000 MW; no figure a reader sees moves, as no page draws the table. The other
other choice, (b), a fill by plant ID, cannot be built: no tracker table holds an EIA plant or generator ID.

Pinned with the builder's own function on cells made up here (no real row: the table is not on this machine).

    python -m unittest tests.test_alt_site_data_machine_2 -v
"""

import importlib.util
import os
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def load():
    spec = importlib.util.spec_from_file_location("gp_alt2", os.path.join(ROOT, "warehouse", "derived", "generator_pipeline_by_grid.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class TheCells(unittest.TestCase):
    def test_two_variables_a_cell(self):
        m = load()
        plan = pd.DataFrame([("1:A", "ERCO", "TX", "SUN", "P", "2028", 75.0, True), ("2:A", "ERCO", "TX", "SUN", "P", "2028", 25.0, False),
                             ("3:A", "PJM", "VA", "NG", "T", "2027", 300.0, False)], columns=["key", "ba", "state", "fuel", "status", "year", "mw", "tag"])
        rows = pd.DataFrame(m.cells(plan, "2026-09", "https://www.eia.gov/electricity/data/eia860m/"))
        self.assertEqual(len(rows), 4)                                                     # two cells, two rows each (main: three each)
        self.assertEqual(sorted(set(rows["variable"])), ["planned_count", "planned_mw"])
        self.assertEqual(rows[rows["variable"] == "planned_mw"]["value"].tolist(), [100.0, 300.0])

    def test_the_share_of_rows_that_leave(self):
        self.assertEqual(round(1671 / 5147 * 100, 1), 32.5)                                 # the impact file's count on Redivis


if __name__ == "__main__":
    unittest.main()
