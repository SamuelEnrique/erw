"""Session 2278: Statistics Estonia's table KE21, Estonia's electricity production, imports and exports.

Energy Research Warehouse (ERW). Tests warehouse/connectors/statee_electricity.py on a metadata and an answer built here
in PxWeb's and JSON-stat 2.0's forms (made up for the test, not Statistics Estonia's): the query of every month and the
indicators in GWh only; each cell a row on the month's first day in MWh, the unit dropped from the name, the code kept as
x_code; an empty cell not written; a metadata without the two variables, an indicator not in GWh, a month of another
form and a value array of the wrong size stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2278 -v
"""

import copy
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import statee_electricity as S  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}
META = {"variables": [{"code": S.IND, "values": ["PROD_E", "IMPORTS", "FCONS_C_P_PC"],
                       "valueTexts": ["Total\xa0electricity\xa0production, GWh", "Imports of electricity, GWh",
                                      "Share of sold electricity to enterprises in final consumption, %"]},
                      {"code": S.TIME, "values": ["2026M07", "2026M08"]}]}
JS = {"id": [S.IND, S.TIME], "size": [2, 2],
      "dimension": {S.IND: {"category": {"index": {"PROD_E": 0, "IMPORTS": 1},
                                         "label": {"PROD_E": "Total\xa0electricity\xa0production, GWh", "IMPORTS": "Imports of electricity, GWh"}}},
                    S.TIME: {"category": {"index": {"2026M07": 0, "2026M08": 1}}}},
      "value": [410.5, 395, None, 310]}


class Parse(unittest.TestCase):
    def test_query(self):
        q = S.query(META)
        self.assertEqual(q["query"][0]["selection"]["values"], ["PROD_E", "IMPORTS"])
        self.assertEqual(q["query"][1]["selection"]["values"], ["2026M07", "2026M08"])
        self.assertEqual(q["response"]["format"], "json-stat2")
        with self.assertRaises(RuntimeError):
            S.query({"variables": META["variables"][:1]})

    def test_rows(self):
        t = S.parse(JS, BASE).set_index(["variable", "ts_utc"])
        self.assertEqual(len(t), 3)
        r = t.loc[("total_electricity_production", "2026-07-01T00:00:00Z")]
        self.assertEqual((r.value, r.unit, r.x_code, r.geo, r.node), (410500.0, "MWh", "PROD_E", "EE", "Total electricity production, GWh"))
        self.assertEqual(t.loc[("imports_of_electricity", "2026-08-01T00:00:00Z")].value, 310000.0)
        self.assertNotIn(("imports_of_electricity", "2026-07-01T00:00:00Z"), t.index)

    def test_stops(self):
        bad = []
        x = copy.deepcopy(JS); x["id"] = ["Indicator", S.TIME]; bad.append(x)
        x = copy.deepcopy(JS); x["dimension"][S.IND]["category"]["label"]["IMPORTS"] = "Share of imports, %"; bad.append(x)
        x = copy.deepcopy(JS); x["dimension"][S.TIME]["category"]["index"] = {"2026-07": 0, "2026M08": 1}; bad.append(x)
        x = copy.deepcopy(JS); x["value"] = [1, 2]; bad.append(x)
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
