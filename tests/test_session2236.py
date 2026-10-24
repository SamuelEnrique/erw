"""Session 2236: Statistics Sweden's table TAB1011, Sweden's electricity supply by type of production.

Energy Research Warehouse (ERW). Tests warehouse/connectors/scb_electricity.py on an answer built here in JSON-stat 2.0's
form (made up for the test, not SCB's): each cell a row on the month's first day, GWh written as MWh, the line's label in
snake case and SCB's code kept, an empty cell not written; dimensions of another kind, a content not in GWh, a month of
another form and a value array of the wrong size stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2236 -v
"""

import copy
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import scb_electricity as S  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}
JS = {"id": ["Prodslag", "ContentsCode", "Tid"], "size": [2, 1, 2],
      "dimension": {"Prodslag": {"category": {"index": {"Vatten": 0, "Karn": 1},
                                              "label": {"Vatten": "hydro power (including pump power), net", "Karn": "nuclear power (condensation), net"}}},
                    "ContentsCode": {"category": {"index": {"EN0108A3": 0}, "label": {"EN0108A3": "GWh "}}},
                    "Tid": {"category": {"index": {"2026M07": 0, "2026M08": 1}, "label": {"2026M07": "2026M07", "2026M08": "2026M08"}}}},
      "value": [5000.5, 5100, 3900, None]}


class Parse(unittest.TestCase):
    def test_rows(self):
        t = S.parse(JS, BASE).set_index(["variable", "ts_utc"])
        self.assertEqual(len(t), 3)
        r = t.loc[("hydro_power", "2026-07-01T00:00:00Z")]
        self.assertEqual((r.value, r.unit, r.x_code, r.geo), (5000500.0, "MWh", "Vatten", "SE"))
        self.assertEqual(t.loc[("nuclear_power", "2026-07-01T00:00:00Z")].value, 3900000.0)
        self.assertNotIn(("nuclear_power", "2026-08-01T00:00:00Z"), t.index)

    def test_stops(self):
        bad = []
        x = copy.deepcopy(JS); x["id"] = ["Region", "ContentsCode", "Tid"]; bad.append(x)
        x = copy.deepcopy(JS); x["dimension"]["ContentsCode"]["category"]["label"]["EN0108A3"] = "TJ"; bad.append(x)
        x = copy.deepcopy(JS); x["dimension"]["Tid"]["category"]["index"] = {"2026-07": 0, "2026M08": 1}; bad.append(x)
        x = copy.deepcopy(JS); x["value"] = [1, 2, 3]; bad.append(x)
        for js in bad:
            with self.assertRaises((RuntimeError, KeyError)):
                S.parse(js, BASE)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(S.NAME), "power")
        self.assertIn(S.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {S.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
